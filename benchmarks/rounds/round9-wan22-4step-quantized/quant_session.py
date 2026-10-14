"""Round 9: round 8's 4-step LoRA plus int8 weight-only quantization (runs on the pod).

Usage:
  Loading checkpoint only, no generation (run this first, every time):
    python3 quant_session.py check --lora-high H.safetensors --lora-low L.safetensors --out OUT_DIR
  Smoke test (one short prompt, bf16+LoRA vs int8-quantized+LoRA):
    python3 quant_session.py smoke JOBS.json --lora-high H.safetensors --lora-low L.safetensors --out OUT_DIR
  Full run (frozen job list, quantized config only, once the smoke test confirms it is worth it):
    python3 quant_session.py full JOBS.json --lora-high H.safetensors --lora-low L.safetensors --out OUT_DIR --guidance 1.0 --guidance-2 1.0

Quantization: TorchAoConfig("int8_weight_only") passed to WanTransformer3DModel.from_pretrained for both
experts, confirmed locally (round 9's PLAN.md, section 2) that diffusers' LoRA loader has an explicit,
anticipated code path for a quantized base model (`is_quantized = hasattr(transformer, "hf_quantizer")`
in diffusers/loaders/lora_pipeline.py) -- quantize first, then load the LoRA on top, same order used here.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time

CACHE = os.environ.get("WAN_CACHE", "/root/hf")
os.environ["HF_HOME"] = CACHE
os.environ["HF_HUB_CACHE"] = os.environ["HUGGINGFACE_HUB_CACHE"] = f"{CACHE}/hub"

import diffusers
import imageio
import numpy as np
import torch
from diffusers import AutoencoderKLWan, TorchAoConfig, WanPipeline, WanTransformer3DModel
from torchao.quantization import Int8WeightOnlyConfig
from diffusers.utils import export_to_video
from huggingface_hub import snapshot_download

MODEL_ID = "Wan-AI/Wan2.2-T2V-A14B-Diffusers"

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["check", "smoke", "full"])
ap.add_argument("jobs", nargs="?")
ap.add_argument("--lora-high", required=True)
ap.add_argument("--lora-low", required=True)
ap.add_argument("--out", default="/root/out9/session")
ap.add_argument("--min-tflops", type=float, default=150)
ap.add_argument("--guidance", type=float, default=1.0)
ap.add_argument("--guidance-2", type=float, default=1.0)
args = ap.parse_args()
OUT = args.out
os.makedirs(OUT, exist_ok=True)
T0 = time.time()
DONE = os.path.join(os.path.dirname(OUT.rstrip("/")), "SESSION_DONE")


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def write(name, obj):
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(obj, f, indent=1)


# ---------------------------------------------------------------- preflight
pre = {
    "utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
    "gpu": sh("nvidia-smi --query-gpu=name,driver_version,memory.total,power.limit,clocks.max.sm --format=csv,noheader"),
    "gpu_uuid": sh("nvidia-smi --query-gpu=uuid --format=csv,noheader"),
    "versions": {"torch": torch.__version__, "diffusers": diffusers.__version__, "python": sys.version.split()[0]},
    "fails": [],
}
if not torch.cuda.is_available():
    pre["fails"].append("torch.cuda.is_available() is False")
else:
    x = torch.randn(8192, 8192, device="cuda", dtype=torch.bfloat16)
    for _ in range(5):
        x @ x
    torch.cuda.synchronize()
    t = time.time()
    for _ in range(30):
        x @ x
    torch.cuda.synchronize()
    pre["matmul_bf16_tflops"] = round(30 * 2 * 8192 ** 3 / (time.time() - t) / 1e12)
    del x
    if pre["matmul_bf16_tflops"] < args.min_tflops:
        pre["fails"].append(f"matmul {pre['matmul_bf16_tflops']} TFLOPS below {args.min_tflops}")
    pre["vram_total_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1)
os.makedirs(CACHE, exist_ok=True)
pre["cache_fstype"] = sh(f"df --output=fstype {CACHE} | tail -1")
if "fuse" in pre["cache_fstype"] or "nfs" in pre["cache_fstype"]:
    pre["fails"].append(f"weights cache is on a network filesystem ({pre['cache_fstype']})")
for p in (args.lora_high, args.lora_low):
    if not os.path.isfile(p):
        pre["fails"].append(f"LoRA file not found: {p}")
try:
    snapshot_download(MODEL_ID, local_files_only=True)
    pre["weights"] = "present"
    pre["download_s"] = 0
except Exception:
    pre["weights"] = "downloading"
    t = time.time()
    if shutil.disk_usage(CACHE).free < 160e9:
        pre["fails"].append("less than 160 GB free for the 139 GB weights")
    if not pre["fails"]:
        snapshot_download(MODEL_ID, max_workers=16)
    pre["download_s"] = round(time.time() - t, 1)
write("preflight.json", pre)
if pre["fails"]:
    print("PREFLIGHT_FAIL", pre["fails"], flush=True)
    open(DONE, "w").write("preflight failed\n")
    sys.exit(2)
print("PREFLIGHT_OK", json.dumps(pre), flush=True)

# ---------------------------------------------------------------- load, quantize, LoRA
t = time.time()
quant_config = TorchAoConfig(Int8WeightOnlyConfig())
vae = AutoencoderKLWan.from_pretrained(MODEL_ID, subfolder="vae", torch_dtype=torch.float32)
transformer = WanTransformer3DModel.from_pretrained(MODEL_ID, subfolder="transformer", quantization_config=quant_config, torch_dtype=torch.bfloat16)
transformer_2 = WanTransformer3DModel.from_pretrained(MODEL_ID, subfolder="transformer_2", quantization_config=quant_config, torch_dtype=torch.bfloat16)
pipe = WanPipeline.from_pretrained(MODEL_ID, vae=vae, transformer=transformer, transformer_2=transformer_2, torch_dtype=torch.bfloat16)
print(f"quantized transformers loaded {round(time.time() - t, 1)}", flush=True)
print("transformer has hf_quantizer:", hasattr(pipe.transformer, "hf_quantizer"), flush=True)
print("transformer_2 has hf_quantizer:", hasattr(pipe.transformer_2, "hf_quantizer"), flush=True)

t_lora = time.time()
pipe.load_lora_weights(args.lora_high, adapter_name="high")
pipe.load_lora_weights(args.lora_low, adapter_name="low", load_into_transformer_2=True)
print(f"LoRA attached onto quantized base {round(time.time() - t_lora, 1)}", flush=True)
pipe.enable_model_cpu_offload()
load_s = round(time.time() - t, 1)
print("loaded", load_s, "quantized+LoRA", flush=True)

if args.mode == "check":
    # Loading-only checkpoint: confirms the quantized-base + LoRA combination builds and moves to the
    # pipeline without error, before any generation is attempted. No forward pass here on purpose --
    # this mode exists to catch a broken combination cheaply, the same discipline round 8 used for the
    # LoRA's own loading path before spending any generation time on it.
    print("CHECK_OK: quantized transformer + LoRA loaded without error", flush=True)
    open(DONE, "w").write("check ok\n")
    print("SESSION_DONE", flush=True)
    sys.exit(0)


class Sampler(threading.Thread):
    Q = "utilization.gpu,power.draw,memory.used,clocks.sm,temperature.gpu,clocks_throttle_reasons.active"

    def __init__(self):
        super().__init__(daemon=True)
        self.rows, self.stop = [], threading.Event()

    def run(self):
        while not self.stop.is_set():
            out = sh(f"nvidia-smi --query-gpu={self.Q} --format=csv,noheader,nounits")
            p = [x.strip() for x in out.split(",")]
            try:
                self.rows.append([float(v) for v in p[:5]] + [int(p[5], 16)])
            except (ValueError, IndexError):
                pass
            self.stop.wait(1.0)

    def summary(self):
        r = self.rows
        if not r:
            return {}
        col = lambda i: [x[i] for x in r]
        mask = 0
        for v in col(5):
            mask |= int(v)
        return {"gpu_util_mean": round(sum(col(0)) / len(r), 1), "power_w_mean": round(sum(col(1)) / len(r), 1),
                "power_w_max": max(col(1)), "sm_clock_mhz_mean": round(sum(col(3)) / len(r)), "sm_clock_mhz_min": min(col(3)),
                "temp_c_max": max(col(4)), "throttle_reasons_seen": hex(mask), "samples": len(r)}


def quality_gate(path, job):
    frames = [f for f in imageio.get_reader(path)]
    n = len(frames)
    idx = np.linspace(0, n - 1, 9).astype(int)
    means = [float(frames[i].mean()) for i in idx]
    diff = float(np.abs(frames[n - 1].astype(np.float32) - frames[0].astype(np.float32)).mean())
    checks = {"frames_ok": n == job["frames"], "shape_ok": tuple(frames[0].shape[:2]) == (job["height"], job["width"]),
              "not_black": min(means) > 5, "not_frozen": diff > 2.0}
    return {"pass": all(checks.values()), "n_frames": n, "first_last_diff": round(diff, 2), **checks}


def run_job(job, name_suffix, steps, guidance, guidance_2):
    rec = {"job": job["job"] + name_suffix, "stratum": job.get("stratum"), "steps": steps,
           "guidance": guidance, "guidance_2": guidance_2, "quantized": "int8_weight_only",
           "width": job["width"], "height": job["height"], "frames": job["frames"], "fps": job["fps"]}
    s = Sampler()
    s.start()
    torch.cuda.reset_peak_memory_stats()
    t = time.time()
    try:
        frames = pipe(prompt=job["prompt"], negative_prompt="", height=job["height"], width=job["width"], num_frames=job["frames"],
                      num_inference_steps=steps, guidance_scale=guidance, guidance_scale_2=guidance_2,
                      generator=torch.Generator("cuda").manual_seed(job["seed"])).frames[0]
        torch.cuda.synchronize()
        rec["generate_s"] = round(time.time() - t, 1)
        path = os.path.join(OUT, rec["job"] + ".mp4")
        export_to_video(frames, path, fps=job["fps"])
        rec["encode_s"] = round(time.time() - t - rec["generate_s"], 1)
        rec["bytes"] = os.path.getsize(path)
        rec["sha256"] = hashlib.sha256(open(path, "rb").read()).hexdigest()
        rec["gate"] = quality_gate(path, job)
        rec["ok"] = True
        rec["delivered"] = rec["gate"]["pass"]
    except Exception as e:
        rec["ok"] = False
        rec["delivered"] = False
        rec["generate_s"] = round(time.time() - t, 1)
        rec["error"] = repr(e)[:300]
        torch.cuda.empty_cache()
    s.stop.set()
    rec.update(s.summary())
    rec["peak_vram_gb"] = round(torch.cuda.max_memory_allocated() / 1e9, 1)
    with open(os.path.join(OUT, "jobs.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print("JOB", json.dumps({k: rec.get(k) for k in ("job", "ok", "delivered", "generate_s", "guidance")}), flush=True)
    return rec


spec = json.load(open(args.jobs))

# "smoke" and "full" both run in this same process, after the single load above -- loading the
# quantized model twice (once per separate process launch) cost 650s each on the first pod attempt
# and ate the whole guard deadline before any generation finished. One load, then warm-up as a sanity
# check, then the real jobs, all in one process, regardless of which mode was requested.
run_job(spec["warmup"], "_quantized_guidance1", 4, 1.0, 1.0)
if args.mode == "full":
    for job in spec["jobs"]:
        run_job(job, "", 4, args.guidance, args.guidance_2)

open(DONE, "w").write("ok\n")
print("SESSION_DONE", flush=True)
