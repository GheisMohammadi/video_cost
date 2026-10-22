import os, sys, json, time, hashlib

OUT = "/workspace/out"
os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")

def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    LOG.write(msg + "\n"); LOG.flush()

os.environ["HF_HOME"] = "/workspace/hfcache"
os.environ["HF_HUB_CACHE"] = "/workspace/hfcache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/workspace/hfcache"

import torch
from PIL import Image
import numpy as np
import glob

PROMPT_SCRIPT = (
    "Thousands of U.S. advertisers are pursuing claims against Google. "
    "Advertisers are filing refunds for 20-30% of Ad Spend since 2016. "
    "Federal courts have ruled Google illegally monopolized search advertising. "
    "Get the facts, fit criteria and risks. Use them for your agency or your clients. "
    "The Google Advertiser Claims, explained. DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"
)

SEED = 10001
record = {"tests": []}

def save_record():
    with open(f"{OUT}/raw_record.json", "w") as f:
        json.dump(record, f, indent=1)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

# ---------------- Test A: VACE masked video edit ----------------
log("=== TEST A: VACE ===")
t0 = time.time()
from diffusers import WanVACEPipeline, AutoencoderKLWan
from diffusers.utils import export_to_video

model_id = "Wan-AI/Wan2.1-VACE-14B-diffusers"
vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
pipe = WanVACEPipeline.from_pretrained(model_id, vae=vae, torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()
load_s = time.time() - t0
log("VACE loaded in", load_s, "s")

frame_paths = sorted(glob.glob("/workspace/in/frames_jpg/*.jpg"))
mask_paths = sorted(glob.glob("/workspace/in/board_masks/*.png"))
assert len(frame_paths) == len(mask_paths) == 81, (len(frame_paths), len(mask_paths))
video_in = [Image.open(p).convert("RGB").resize((832, 480)) for p in frame_paths]
mask_in = [Image.open(p).convert("L").resize((832, 480)) for p in mask_paths]

t0 = time.time()
gen = torch.Generator(device="cuda").manual_seed(SEED)
vace_prompt = (
    "a whiteboard with the exact handwritten text: " + PROMPT_SCRIPT +
    " -- realistic marker handwriting, clean legible letters, same lighting as the rest of the scene"
)
out = pipe(
    prompt=vace_prompt,
    video=video_in,
    mask=mask_in,
    height=480, width=832, num_frames=81,
    num_inference_steps=30,
    guidance_scale=5.0,
    generator=gen,
).frames[0]
gen_s = time.time() - t0
export_to_video(out, f"{OUT}/test_a_vace.mp4", fps=16)
sha = sha256_file(f"{OUT}/test_a_vace.mp4")
log("VACE generate_s", gen_s, "sha256", sha)
record["tests"].append({"test": "A_vace", "load_s": load_s, "generate_s": gen_s,
                         "sha256": sha, "file": "test_a_vace.mp4", "steps": 30, "seed": SEED})
save_record()

del pipe
torch.cuda.empty_cache()

# ---------------- Test B: Qwen-Image-Edit text correction ----------------
log("=== TEST B: Qwen-Image-Edit ===")
t0 = time.time()
from diffusers import QwenImageEditPipeline

qpipe = QwenImageEditPipeline.from_pretrained("Qwen/Qwen-Image-Edit", torch_dtype=torch.bfloat16)
qpipe.enable_model_cpu_offload()
load_s_b = time.time() - t0
log("Qwen-Image-Edit loaded in", load_s_b, "s")

frame1 = Image.open(frame_paths[0]).convert("RGB")
edit_prompt = (
    "Replace the handwritten text on the whiteboard with this exact text, clearly legible, "
    "same handwriting style and marker colors as the original, keep everything else unchanged: "
    + PROMPT_SCRIPT
)

t0 = time.time()
gen_b = torch.Generator(device="cuda").manual_seed(SEED)
result = qpipe(
    image=frame1,
    prompt=edit_prompt,
    num_inference_steps=30,
    generator=gen_b,
).images[0]
gen_s_b = time.time() - t0
result.save(f"{OUT}/test_b_qwen_edit.png")
sha_b = sha256_file(f"{OUT}/test_b_qwen_edit.png")
log("Qwen-Image-Edit generate_s", gen_s_b, "sha256", sha_b)
record["tests"].append({"test": "B_qwen_image_edit", "load_s": load_s_b, "generate_s": gen_s_b,
                         "sha256": sha_b, "file": "test_b_qwen_edit.png", "steps": 30, "seed": SEED})
save_record()

del qpipe
torch.cuda.empty_cache()

log("ALL_DONE")
with open(f"{OUT}/SESSION_DONE", "w") as f:
    f.write("done\n")
