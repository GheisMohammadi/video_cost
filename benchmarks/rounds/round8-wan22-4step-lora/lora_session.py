"""Round 8: Wan2.2 T2V-A14B with the lightx2v 4-step distillation LoRA (runs on the pod).

Usage:
  Smoke test (one short prompt, three configs, before spending time on the full set):
    python3 lora_session.py smoke JOBS.json --lora-high H.safetensors --lora-low L.safetensors --out OUT_DIR
  Full run (frozen job list, one fixed config chosen from the smoke test):
    python3 lora_session.py full JOBS.json --lora-high H.safetensors --lora-low L.safetensors --out OUT_DIR \
        --guidance 1.0 --guidance-2 1.0 --force-schedule

Loading API confirmed against the installed diffusers source (not a blog example): the low-noise LoRA
needs `load_into_transformer_2=True`, not a `components=` kwarg -- that kwarg does not exist on
WanLoraLoaderMixin.load_lora_weights. --force-schedule patches the scheduler to use the LoRA's documented
exact timesteps ([1000, 750, 500, 250]) instead of whatever a plain num_inference_steps=4 would compute.
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
from diffusers import AutoencoderKLWan, WanPipeline
from diffusers.utils import export_to_video
from huggingface_hub import snapshot_download

MODEL_ID = "Wan-AI/Wan2.2-T2V-A14B-Diffusers"
FORCED_TIMESTEPS = [1000.0, 750.0, 500.0, 250.0]  # from lightx2v/Wan2.2-Distill-Loras' README (I2V-documented, applied here to the T2V files)

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["smoke", "full"])
ap.add_argument("jobs")
ap.add_argument("--lora-high", required=True)
ap.add_argument("--lora-low", required=True)
ap.add_argument("--out", default="/root/out8/session")
ap.add_argument("--min-tflops", type=float, default=150)
ap.add_argument("--guidance", type=float, default=1.0)
ap.add_argument("--guidance-2", type=float, default=1.0)
ap.add_argument("--force-schedule", action="store_true")
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


# ---------------------------------------------------------------- preflight (same checks as every round)
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

# ---------------------------------------------------------------- load + LoRA
t = time.time()
vae = AutoencoderKLWan.from_pretrained(MODEL_ID, subfolder="vae", torch_dtype=torch.float32)
pipe = WanPipeline.from_pretrained(MODEL_ID, vae=vae, torch_dtype=torch.bfloat16)
# Deliberately NOT overriding the scheduler to UniPC here (unlike wan22_a14b_session.py): the LoRA
# was distilled against a flow-matching schedule, so this keeps WanPipeline's own default
# FlowMatchEulerDiscreteScheduler, which is what --force-schedule patches below.
pipe.load_lora_weights(args.lora_high, adapter_name="high")
pipe.load_lora_weights(args.lora_low, adapter_name="low", load_into_transformer_2=True)
pipe.enable_model_cpu_offload()
load_s = round(time.time() - t, 1)
print("loaded", load_s, "with LoRA", flush=True)

if args.force_schedule:
    _orig_set_timesteps = pipe.scheduler.set_timesteps

    def _forced_set_timesteps(num_inference_steps=None, device=None, **kw):
        return _orig_set_timesteps(timesteps=FORCED_TIMESTEPS, device=device)

    pipe.scheduler.set_timesteps = _forced_set_timesteps
    print("scheduler patched to forced timesteps", FORCED_TIMESTEPS, flush=True)


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
           "guidance": guidance, "guidance_2": guidance_2, "forced_schedule": args.force_schedule,
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
    print("JOB", json.dumps({k: rec.get(k) for k in ("job", "ok", "delivered", "generate_s", "guidance", "forced_schedule")}), flush=True)
    return rec


spec = json.load(open(args.jobs))

if args.mode == "smoke":
    # Three configs on the warmup (short) prompt only: default 4-step schedule at the usual guidance,
    # default 4-step schedule at guidance 1.0 (the conventional distilled-model setting), and the
    # LoRA's documented exact schedule at guidance 1.0. Comparing these picks the full run's config.
    job = spec["warmup"]
    args.force_schedule = False
    run_job(job, "_a_default_sched_default_guidance", 4, 3.5, 4.0)
    run_job(job, "_b_default_sched_guidance1", 4, 1.0, 1.0)
    _orig_set_timesteps = pipe.scheduler.set_timesteps

    def _forced(num_inference_steps=None, device=None, **kw):
        return _orig_set_timesteps(timesteps=FORCED_TIMESTEPS, device=device)

    pipe.scheduler.set_timesteps = _forced
    args.force_schedule = True
    run_job(job, "_c_forced_sched_guidance1", 4, 1.0, 1.0)
else:
    for job in spec["jobs"]:
        run_job(job, "", 4, args.guidance, args.guidance_2)

open(DONE, "w").write("ok\n")
print("SESSION_DONE", flush=True)
