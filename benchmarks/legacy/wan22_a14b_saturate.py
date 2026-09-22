"""Saturation run: feed back-to-back Wan2.2 T2V-A14B requests until a hard time limit.

Requests use fal's standard defaults (see fal_wan22_config.md) and realistic prompts used as-is.
Hard stop: no new request starts if it is unlikely to finish before --max-minutes, and a watchdog
kills the process at --max-minutes + --grace-s even mid-generation. Killing the process does NOT
stop billing; pass --stop-pod to also run `runpodctl stop pod` (off by default: if the disk is not
a persistent volume, stopping the pod deletes the downloaded weights).

Usage: python3 wan22_a14b_saturate.py PROMPTS.jsonl --max-minutes 60
Output: /root/out/sat_runs.jsonl (one record per request), /root/out/sat_summary.json
"""
import argparse
import json
import os
import random
import statistics as st
import subprocess
import threading
import time

CACHE = os.environ.get("WAN_CACHE", "/workspace/hf")
os.environ["HF_HOME"] = CACHE
os.environ["HF_HUB_CACHE"] = os.environ["HUGGINGFACE_HUB_CACHE"] = f"{CACHE}/hub"

import torch
from diffusers import AutoencoderKLWan, UniPCMultistepScheduler, WanPipeline
from diffusers.utils import export_to_video

MODEL_ID = "Wan-AI/Wan2.2-T2V-A14B-Diffusers"
OUT = "/root/out"
GPU_PRICE_PER_HOUR = 1.618
TOKEN_LIMIT = 512

ap = argparse.ArgumentParser()
ap.add_argument("prompts")
ap.add_argument("--max-minutes", type=float, default=60)
ap.add_argument("--grace-s", type=float, default=120)
ap.add_argument("--steps", type=int, default=27)
ap.add_argument("--frames", type=int, default=81)
ap.add_argument("--width", type=int, default=1280)
ap.add_argument("--height", type=int, default=720)
ap.add_argument("--fps", type=int, default=16)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--stop-pod", action="store_true")
args = ap.parse_args()
os.makedirs(f"{OUT}/sat", exist_ok=True)
session_start = time.time()
deadline = session_start + args.max_minutes * 60


def finish(code):
    if args.stop_pod:
        subprocess.run(["runpodctl", "stop", "pod", os.environ["RUNPOD_POD_ID"]])
    os._exit(code)


def watchdog():
    while time.time() < deadline + args.grace_s:
        time.sleep(5)
    print("HARD_STOP watchdog fired", flush=True)
    finish(3)


threading.Thread(target=watchdog, daemon=True).start()


class GpuSampler(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.samples, self.stop = [], threading.Event()

    def run(self):
        while not self.stop.is_set():
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,power.draw,memory.used", "--format=csv,noheader,nounits"],
                capture_output=True, text=True).stdout.strip()
            try:
                self.samples.append([float(x) for x in out.split(",")])
            except ValueError:
                pass
            self.stop.wait(1.0)


t = time.time()
vae = AutoencoderKLWan.from_pretrained(MODEL_ID, subfolder="vae", torch_dtype=torch.float32)
pipe = WanPipeline.from_pretrained(MODEL_ID, vae=vae, torch_dtype=torch.bfloat16)
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=5.0)
pipe.enable_model_cpu_offload()
load_s = round(time.time() - t, 1)
print("loaded", load_s, "s", flush=True)

prompts = [json.loads(l) for l in open(args.prompts).read().split("\n") if l.strip()]
random.Random(args.seed).shuffle(prompts)
records, i = [], 0
while True:
    recent = [r["generate_s"] for r in records if r["ok"]][-5:]
    need = 1.2 * (sum(recent) / len(recent)) if recent else 0
    if time.time() + need > deadline:
        print("session time limit reached, stopping", flush=True)
        break
    p = prompts[i % len(prompts)]
    seed = args.seed * 1000 + i
    n_tokens = len(pipe.tokenizer(p["prompt"]).input_ids)
    rec = {"idx": i, "t_start_s": round(time.time() - session_start, 1), "prompt_id": p["id"], "words": p["words"],
           "prompt_tokens": n_tokens, "truncated": n_tokens > TOKEN_LIMIT, "seed": seed, "steps": args.steps,
           "frames": args.frames, "width": args.width, "height": args.height, "fps": args.fps}
    torch.cuda.reset_peak_memory_stats()
    sampler = GpuSampler(); sampler.start()
    t = time.time()
    try:
        frames = pipe(prompt=p["prompt"], negative_prompt="", height=args.height, width=args.width,
                      num_frames=args.frames, num_inference_steps=args.steps, guidance_scale=3.5,
                      guidance_scale_2=4.0, generator=torch.Generator("cuda").manual_seed(seed)).frames[0]
        torch.cuda.synchronize()
        rec["generate_s"] = round(time.time() - t, 1)
        export_to_video(frames, f"{OUT}/sat/{i:04d}_{p['id']}.mp4", fps=args.fps)
        rec["encode_s"] = round(time.time() - t - rec["generate_s"], 1)
        rec["ok"] = True
        rec["video_s"] = round(args.frames / args.fps, 2)
    except Exception as e:
        rec["ok"] = False
        rec["generate_s"] = round(time.time() - t, 1)
        rec["error"] = repr(e)[:300]
        torch.cuda.empty_cache()
    sampler.stop.set()
    s = sampler.samples
    if s:
        rec["gpu_util_mean"] = round(sum(x[0] for x in s) / len(s), 1)
        rec["power_w_mean"] = round(sum(x[1] for x in s) / len(s), 1)
    rec["peak_vram_gb"] = round(torch.cuda.max_memory_allocated() / 1e9, 1)
    records.append(rec)
    with open(f"{OUT}/sat_runs.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print("RUN", json.dumps(rec), flush=True)
    i += 1

wall = time.time() - session_start
ok = [r for r in records if r["ok"]]
gen = [r["generate_s"] for r in ok]
video_s = sum(r["video_s"] for r in ok)
busy_s = sum(r["generate_s"] + r.get("encode_s", 0) for r in records)
summary = {
    "requests": len(records), "ok": len(ok), "failed": len(records) - len(ok),
    "failure_rate": round((len(records) - len(ok)) / max(len(records), 1), 3),
    "truncated_prompts": sum(r["truncated"] for r in records),
    "generate_s_mean": round(st.mean(gen), 1) if gen else None,
    "generate_s_p50": round(st.median(gen), 1) if gen else None,
    "generate_s_p95": round(sorted(gen)[int(0.95 * (len(gen) - 1))], 1) if gen else None,
    "generate_s_stdev": round(st.pstdev(gen), 1) if gen else None,
    "video_seconds": round(video_s, 1), "session_wall_s": round(wall, 1), "load_s": load_s,
    "busy_s": round(busy_s, 1), "gpu_price_per_hour": GPU_PRICE_PER_HOUR,
    "usd_per_video_s_busy": round(busy_s * GPU_PRICE_PER_HOUR / 3600 / video_s, 4) if video_s else None,
    "usd_per_video_s_session": round(wall * GPU_PRICE_PER_HOUR / 3600 / video_s, 4) if video_s else None,
}
json.dump(summary, open(f"{OUT}/sat_summary.json", "w"), indent=2)
print("SUMMARY", json.dumps(summary), flush=True)
finish(0)
