"""Wan2.2 T2V-A14B baseline matched to fal's standard request defaults. Runs on the pod.

fal defaults (see fal_wan22_config.md): 1280x720, 81 frames @16 fps, 27 steps,
guidance 3.5 / 4.0 (high-noise / low-noise expert), shift 5. Not yet matched: FILM frame
interpolation (fal default x1) and fal's H.264 encode settings. Cost of those is a later phase.

Usage: python3 wan22_a14b_baseline.py PROMPTS.jsonl [--runs N] [--steps 27]
Weights cache: $WAN_CACHE (default /workspace/hf). Each run is appended to /root/out/a14b_runs.jsonl.
"""
import argparse
import json
import os
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
NEGATIVE = ""  # fal default is an empty negative prompt
GPU_PRICE_PER_HOUR = 1.618

ap = argparse.ArgumentParser()
ap.add_argument("prompts")
ap.add_argument("--runs", type=int, default=1)
ap.add_argument("--steps", type=int, default=27)
ap.add_argument("--frames", type=int, default=81)
ap.add_argument("--width", type=int, default=1280)
ap.add_argument("--height", type=int, default=720)
ap.add_argument("--fps", type=int, default=16)
args = ap.parse_args()
os.makedirs(OUT, exist_ok=True)


class GpuSampler(threading.Thread):
    """Samples nvidia-smi once a second: utilization, power, memory."""

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
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=5.0)  # fal shift=5
pipe.enable_model_cpu_offload()  # two 14B experts + text encoder do not all fit in 80 GB with activations
load_s = round(time.time() - t, 1)
print("loaded", load_s, "s", flush=True)

prompts = [json.loads(l) for l in open(args.prompts).read().split("\n") if l.strip()]
tok_limit = 512
for run in range(args.runs):
    for p in prompts:
        seed = 42 + run
        n_tokens = len(pipe.tokenizer(p["prompt"]).input_ids)
        rec = {"model": MODEL_ID, "gpu": torch.cuda.get_device_name(0), "prompt_id": p["id"], "words": p["words"],
               "prompt_tokens": n_tokens, "truncated": n_tokens > tok_limit, "run": run, "seed": seed,
               "steps": args.steps, "frames": args.frames, "width": args.width, "height": args.height,
               "fps": args.fps, "guidance": 3.5, "guidance_2": 4.0, "shift": 5.0, "load_s": load_s}
        torch.cuda.reset_peak_memory_stats()
        sampler = GpuSampler(); sampler.start()
        t = time.time()
        try:
            frames = pipe(prompt=p["prompt"], negative_prompt=NEGATIVE, height=args.height, width=args.width,
                          num_frames=args.frames, num_inference_steps=args.steps, guidance_scale=3.5,
                          guidance_scale_2=4.0, generator=torch.Generator("cuda").manual_seed(seed)).frames[0]
            torch.cuda.synchronize()
            rec["generate_s"] = round(time.time() - t, 1)
            export_to_video(frames, f"{OUT}/a14b_{p['id']}_r{run}.mp4", fps=args.fps)
            rec["encode_s"] = round(time.time() - t - rec["generate_s"], 1)
            rec["ok"] = True
            rec["video_s"] = round(args.frames / args.fps, 2)
            rec["cost_usd"] = round(rec["generate_s"] * GPU_PRICE_PER_HOUR / 3600, 4)
            rec["usd_per_video_s"] = round(rec["cost_usd"] / rec["video_s"], 4)
        except Exception as e:  # record OOMs and other failures, keep going
            rec["ok"] = False
            rec["error"] = repr(e)[:300]
            rec["fail_after_s"] = round(time.time() - t, 1)
            torch.cuda.empty_cache()
        sampler.stop.set()
        s = sampler.samples
        if s:
            rec["gpu_util_mean"] = round(sum(x[0] for x in s) / len(s), 1)
            rec["power_w_mean"] = round(sum(x[1] for x in s) / len(s), 1)
        rec["peak_vram_gb"] = round(torch.cuda.max_memory_allocated() / 1e9, 1)
        with open(f"{OUT}/a14b_runs.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        print("RUN", json.dumps(rec), flush=True)
print("DONE")
