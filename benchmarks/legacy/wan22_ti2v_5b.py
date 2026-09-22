"""Wan2.2 TI2V-5B text-to-video smoke test + timing. Runs on the pod.

Weights cache dir: $WAN_CACHE (default /workspace/hf).
"""
import json
import os
import time

# The pod image may preset HUGGINGFACE_HUB_CACHE, which beats HF_HOME, so set all of them.
CACHE = os.environ.get("WAN_CACHE", "/workspace/hf")
os.environ["HF_HOME"] = CACHE
os.environ["HF_HUB_CACHE"] = os.environ["HUGGINGFACE_HUB_CACHE"] = f"{CACHE}/hub"

import torch
from diffusers import AutoencoderKLWan, WanPipeline
from diffusers.utils import export_to_video
from huggingface_hub import snapshot_download

MODEL_ID = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
OUT_DIR = "/root/out"
FPS = 24
NUM_FRAMES = 73  # 4k+1 frames -> 73 / 24 fps = 3.04 s
WIDTH, HEIGHT = 1280, 704
STEPS = 50
PROMPT = "A red fox trotting through fresh snow in a pine forest at sunrise, cinematic, soft golden light"
NEGATIVE = "blurry, low quality, distorted, watermark, text, static, worst quality"

os.makedirs(OUT_DIR, exist_ok=True)
x = torch.randn(8192, 8192, device="cuda", dtype=torch.bfloat16)
torch.cuda.synchronize(); t0 = time.time()
for _ in range(50):
    y = x @ x
torch.cuda.synchronize()
tflops = 50 * 2 * 8192**3 / (time.time() - t0) / 1e12
print(f"CUDA matmul OK: {tflops:.0f} TFLOPS bf16")
metrics = {"matmul_bf16_tflops": round(tflops), "model": MODEL_ID, "gpu": torch.cuda.get_device_name(0), "torch": torch.__version__}

t = time.time()
snapshot_download(MODEL_ID)
metrics["download_s"] = round(time.time() - t, 1)

t = time.time()
vae = AutoencoderKLWan.from_pretrained(MODEL_ID, subfolder="vae", torch_dtype=torch.float32)
pipe = WanPipeline.from_pretrained(MODEL_ID, vae=vae, torch_dtype=torch.bfloat16).to("cuda")
metrics["load_s"] = round(time.time() - t, 1)

torch.cuda.reset_peak_memory_stats()
t = time.time()
frames = pipe(
    prompt=PROMPT,
    negative_prompt=NEGATIVE,
    height=HEIGHT,
    width=WIDTH,
    num_frames=NUM_FRAMES,
    guidance_scale=5.0,
    num_inference_steps=STEPS,
    generator=torch.Generator("cuda").manual_seed(42),
).frames[0]
torch.cuda.synchronize()
metrics["generate_s"] = round(time.time() - t, 1)
metrics["peak_vram_gb"] = round(torch.cuda.max_memory_allocated() / 1e9, 1)

export_to_video(frames, f"{OUT_DIR}/wan22_ti2v5b.mp4", fps=FPS)
metrics.update(width=WIDTH, height=HEIGHT, frames=NUM_FRAMES, fps=FPS, steps=STEPS, prompt=PROMPT)
with open(f"{OUT_DIR}/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
print("METRICS", json.dumps(metrics))
