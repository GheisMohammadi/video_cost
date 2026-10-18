"""Round 10 follow-up: does starting Wan 2.2's image-to-video mode from an already-correct frame
(the round 10 overlay composite) keep the on-screen text accurate as it animates forward, instead of
drifting back into garbled text the way text-to-video generation did (round 10, section 1)?

Usage: python3 i2v_session.py --image start_frame.png --out /root/out_i2v/session
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
from diffusers import AutoencoderKLWan, UniPCMultistepScheduler, WanImageToVideoPipeline
from diffusers.utils import export_to_video, load_image
from huggingface_hub import snapshot_download

MODEL_ID = "Wan-AI/Wan2.2-I2V-A14B-Diffusers"

ap = argparse.ArgumentParser()
ap.add_argument("--image", required=True)
ap.add_argument("--out", default="/root/out_i2v/session")
ap.add_argument("--min-tflops", type=float, default=150)
ap.add_argument("--steps", type=int, default=27)
ap.add_argument("--guidance", type=float, default=3.5)
ap.add_argument("--guidance-2", type=float, default=4.0)
ap.add_argument("--seed", type=int, default=10001)
args = ap.parse_args()
OUT = args.out
os.makedirs(OUT, exist_ok=True)
T0 = time.time()
DONE = os.path.join(os.path.dirname(OUT.rstrip("/")), "SESSION_DONE")

PROMPT = (
    "a white male lawyer continues explaining the text already written on the whiteboard behind him, "
    "using the marker to point and underline words as he speaks, the handwritten text on the board stays "
    "exactly as shown, unchanged and legible, realistic office lighting, static camera"
)


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
if not os.path.isfile(args.image):
    pre["fails"].append(f"start image not found: {args.image}")
try:
    snapshot_download(MODEL_ID, local_files_only=True)
    pre["weights"] = "present"
    pre["download_s"] = 0
except Exception:
    pre["weights"] = "downloading"
    t = time.time()
    if shutil.disk_usage(CACHE).free < 160e9:
        pre["fails"].append("less than 160 GB free for the weights")
    if not pre["fails"]:
        snapshot_download(MODEL_ID, max_workers=16)
    pre["download_s"] = round(time.time() - t, 1)
write("preflight.json", pre)
if pre["fails"]:
    print("PREFLIGHT_FAIL", pre["fails"], flush=True)
    open(DONE, "w").write("preflight failed\n")
    sys.exit(2)
print("PREFLIGHT_OK", json.dumps(pre), flush=True)

# ---------------------------------------------------------------- load
t = time.time()
vae = AutoencoderKLWan.from_pretrained(MODEL_ID, subfolder="vae", torch_dtype=torch.float32)
pipe = WanImageToVideoPipeline.from_pretrained(MODEL_ID, vae=vae, torch_dtype=torch.bfloat16)
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=5.0)
pipe.enable_model_cpu_offload()
load_s = round(time.time() - t, 1)
print("loaded", load_s, flush=True)


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


def quality_gate(path, frames_expected, w_expected, h_expected):
    frames = [f for f in imageio.get_reader(path)]
    n = len(frames)
    idx = np.linspace(0, n - 1, 9).astype(int)
    means = [float(frames[i].mean()) for i in idx]
    diff = float(np.abs(frames[n - 1].astype(np.float32) - frames[0].astype(np.float32)).mean())
    checks = {"frames_ok": n == frames_expected, "shape_ok": tuple(frames[0].shape[:2]) == (h_expected, w_expected),
              "not_black": min(means) > 5, "not_frozen": diff > 2.0}
    return {"pass": all(checks.values()), "n_frames": n, "first_last_diff": round(diff, 2), **checks}


start_image = load_image(args.image)
rec = {"job": "I2V_lawyer_from_correct_frame", "steps": args.steps, "guidance": args.guidance,
       "guidance_2": args.guidance_2, "seed": args.seed, "width": 832, "height": 480, "frames": 81, "fps": 16}
s = Sampler()
s.start()
torch.cuda.reset_peak_memory_stats()
t = time.time()
try:
    frames = pipe(image=start_image, prompt=PROMPT, negative_prompt="", height=480, width=832, num_frames=81,
                  num_inference_steps=args.steps, guidance_scale=args.guidance, guidance_scale_2=args.guidance_2,
                  generator=torch.Generator("cuda").manual_seed(args.seed)).frames[0]
    torch.cuda.synchronize()
    rec["generate_s"] = round(time.time() - t, 1)
    path = os.path.join(OUT, rec["job"] + ".mp4")
    export_to_video(frames, path, fps=16)
    rec["encode_s"] = round(time.time() - t - rec["generate_s"], 1)
    rec["bytes"] = os.path.getsize(path)
    rec["sha256"] = hashlib.sha256(open(path, "rb").read()).hexdigest()
    rec["gate"] = quality_gate(path, 81, 832, 480)
    rec["ok"] = True
    rec["delivered"] = rec["gate"]["pass"]
except Exception as e:
    rec["ok"] = False
    rec["delivered"] = False
    rec["generate_s"] = round(time.time() - t, 1)
    rec["error"] = repr(e)[:500]
    torch.cuda.empty_cache()
s.stop.set()
rec.update(s.summary())
rec["peak_vram_gb"] = round(torch.cuda.max_memory_allocated() / 1e9, 1)
with open(os.path.join(OUT, "jobs.jsonl"), "a") as f:
    f.write(json.dumps(rec) + "\n")
print("JOB", json.dumps({k: rec.get(k) for k in ("job", "ok", "delivered", "generate_s", "error")}), flush=True)

open(DONE, "w").write("ok\n")
print("SESSION_DONE", flush=True)
