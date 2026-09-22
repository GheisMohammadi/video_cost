"""One-hour Wan2.2 T2V-A14B session (runs on the pod): preflight, warm-up, frozen job list, telemetry, quality gate.

Usage: python3 wan22_a14b_session.py hour_test_jobs.json [--window-min 58] [--out /root/out/session]

Rules enforced here:
- Preflight aborts before any model load if CUDA, compute speed, VRAM or disk look wrong.
- The warm-up job is excluded from queue cost. Every failure and skip is written to jobs.jsonl.
- A job is skipped (and recorded) if it is unlikely to finish inside the measurement window.
- The independent pod stop lives in pod_guard.sh, not here. This file only kills itself.
Not covered: fal's FILM frame interpolation (its cost is NOT in these numbers).
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

CACHE = os.environ.get("WAN_CACHE", "/root/hf")  # local container disk; /workspace may be a slow network (FUSE) volume
os.environ["HF_HOME"] = CACHE
os.environ["HF_HUB_CACHE"] = os.environ["HUGGINGFACE_HUB_CACHE"] = f"{CACHE}/hub"

import diffusers
import imageio
import numpy as np
import torch
from diffusers import AutoencoderKLWan, UniPCMultistepScheduler, WanPipeline
from diffusers.utils import export_to_video
from huggingface_hub import snapshot_download

MODEL_ID = "Wan-AI/Wan2.2-T2V-A14B-Diffusers"
TOKEN_LIMIT = 512

ap = argparse.ArgumentParser()
ap.add_argument("jobs")
ap.add_argument("--out", default="/root/out/session")
ap.add_argument("--window-min", type=float, default=58)
ap.add_argument("--min-tflops", type=float, default=150)
ap.add_argument("--gpu-usd-h", type=float, default=1.69)  # RunPod panel rate for the third pod, 2026-09-22
ap.add_argument("--disk-usd-h", type=float, default=0.025)  # 200 GB x $0.09/GB-month / 720 h (engineer-supplied rate, assumed monthly)
ap.add_argument("--fal-480p-usd-s", type=float, default=0.04)  # fal Wan 2.2 A14B standard, page of 2026-09-19
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
    "container_uptime_s": int(sh("ps -o etimes= -p 1") or 0),
    "gpu": sh("nvidia-smi --query-gpu=name,driver_version,memory.total,power.limit,clocks.max.sm,persistence_mode --format=csv,noheader"),
    "versions": {"torch": torch.__version__, "diffusers": diffusers.__version__, "python": sys.version.split()[0]},
    "host": {"loadavg": sh("cat /proc/loadavg"), "nproc": sh("nproc"), "mem": sh("free -g | awk '/Mem/{print $2\"G total \"$7\"G avail\"}'")},
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
    if pre["vram_total_gb"] < 75:
        pre["fails"].append("less than 75 GB VRAM")
os.makedirs(CACHE, exist_ok=True)
pre["cache_fstype"] = sh(f"df --output=fstype {CACHE} | tail -1")
if "fuse" in pre["cache_fstype"] or "nfs" in pre["cache_fstype"]:
    pre["fails"].append(f"weights cache is on a network filesystem ({pre['cache_fstype']})")
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
pre["disk_free_gb"] = round(shutil.disk_usage(CACHE).free / 1e9, 1)
if pre["disk_free_gb"] < 15:
    pre["fails"].append("less than 15 GB free disk")
write("preflight.json", pre)
if pre["fails"]:
    print("PREFLIGHT_FAIL", pre["fails"], flush=True)
    open(DONE, "w").write("preflight failed\n")
    sys.exit(2)
t_pre_s = round(time.time() - T0, 1)
print("PREFLIGHT_OK", json.dumps(pre), flush=True)

# ---------------------------------------------------------------- load
t = time.time()
vae = AutoencoderKLWan.from_pretrained(MODEL_ID, subfolder="vae", torch_dtype=torch.float32)
pipe = WanPipeline.from_pretrained(MODEL_ID, vae=vae, torch_dtype=torch.bfloat16)
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=5.0)  # fal shift=5
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


def quality_gate(path, job):
    frames = [f for f in imageio.get_reader(path)]
    n = len(frames)
    idx = np.linspace(0, n - 1, 9).astype(int)
    means = [float(frames[i].mean()) for i in idx]
    diff = float(np.abs(frames[n - 1].astype(np.float32) - frames[0].astype(np.float32)).mean())
    checks = {"frames_ok": n == job["frames"], "shape_ok": tuple(frames[0].shape[:2]) == (job["height"], job["width"]),
              "not_black": min(means) > 5, "not_frozen": diff > 2.0}
    return {"pass": all(checks.values()), "n_frames": n, "first_last_diff": round(diff, 2), **checks}


def run_job(job, measured):
    rec = {k: job[k] for k in ("job", "block", "stratum", "prompt_id", "tokens", "steps", "seed", "width", "height", "frames", "fps")}
    rec["measured"] = measured
    rec["tokens_pod"] = len(pipe.tokenizer(job["prompt"]).input_ids)
    rec["truncated"] = rec["tokens_pod"] > TOKEN_LIMIT
    rec["loadavg_start"] = sh("cut -d' ' -f1-3 /proc/loadavg")
    rec["t_start_s"] = round(time.time() - T0, 1)
    s = Sampler()
    s.start()
    torch.cuda.reset_peak_memory_stats()
    t = time.time()
    try:
        frames = pipe(prompt=job["prompt"], negative_prompt="", height=job["height"], width=job["width"], num_frames=job["frames"],
                      num_inference_steps=job["steps"], guidance_scale=job["guidance"], guidance_scale_2=job["guidance_2"],
                      generator=torch.Generator("cuda").manual_seed(job["seed"])).frames[0]
        torch.cuda.synchronize()
        rec["generate_s"] = round(time.time() - t, 1)
        path = os.path.join(OUT, job["job"] + ".mp4")
        export_to_video(frames, path, fps=job["fps"])
        rec["encode_s"] = round(time.time() - t - rec["generate_s"], 1)
        rec["video_s"] = round(job["frames"] / job["fps"], 4)
        rec["bytes"] = os.path.getsize(path)
        rec["sha256"] = hashlib.sha256(open(path, "rb").read()).hexdigest()
        rec["gate"] = quality_gate(path, job)
        rec["ok"] = True
        rec["delivered"] = rec["gate"]["pass"]
    except Exception as e:  # keep going; failures are data
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
    print("JOB", json.dumps({k: rec.get(k) for k in ("job", "ok", "delivered", "generate_s", "encode_s", "gpu_util_mean", "throttle_reasons_seen")}), flush=True)
    return rec


spec = json.load(open(args.jobs))
warm = run_job(spec["warmup"], measured=False)
window_start = time.time()
window_end = window_start + args.window_min * 60


def watchdog():  # last resort: this process only. The pod is stopped by pod_guard.sh.
    while time.time() < window_end + 240:
        time.sleep(5)
    open(DONE, "w").write("watchdog\n")
    print("WATCHDOG_EXIT", flush=True)
    os._exit(3)


threading.Thread(target=watchdog, daemon=True).start()
recs, skipped = [], []
for job in spec["jobs"]:
    if time.time() + job["expected_s"] * 1.15 > window_end:
        skipped.append(job["job"])
        with open(os.path.join(OUT, "jobs.jsonl"), "a") as f:
            f.write(json.dumps({"job": job["job"], "skipped": "would not finish inside window", "measured": True}) + "\n")
        continue
    recs.append(run_job(job, measured=True))

write("session.json", {
    "spec_version": spec.get("version"), "model": MODEL_ID, "gpu": pre["gpu"], "load_s": load_s, "warmup_s": warm.get("generate_s"),
    "preflight_and_download_s": t_pre_s,
    "window_s": round(time.time() - window_start, 1), "session_s": round(time.time() - T0, 1),
    "container_uptime_at_start_s": pre["container_uptime_s"], "download_s": pre["download_s"],
    "jobs_run": len(recs), "jobs_failed": sum(not r["ok"] for r in recs), "jobs_skipped": skipped,
    "price_snapshot": {"gpu_usd_h": args.gpu_usd_h, "disk_usd_h": args.disk_usd_h, "fal_480p_usd_per_s": args.fal_480p_usd_s,
                       "note": "disk rate assumed; fal price from model page 2026-09-19 and promo status unchecked today"},
    "not_included": ["FILM frame interpolation (fal default)", "delivery/egress", "human review time"],
})
open(DONE, "w").write("ok\n")
print("SESSION_DONE", flush=True)
