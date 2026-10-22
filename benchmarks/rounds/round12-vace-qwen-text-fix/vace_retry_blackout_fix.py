import os, json, time, hashlib, glob
os.environ["HF_HOME"] = "/workspace/hfcache"
os.environ["HF_HUB_CACHE"] = "/workspace/hfcache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/workspace/hfcache"

import torch
from PIL import Image
import numpy as np

OUT = "/workspace/out"
def log(*a):
    print(*a, flush=True)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

PROMPT_SCRIPT = (
    "Thousands of U.S. advertisers are pursuing claims against Google. "
    "Advertisers are filing refunds for 20-30% of Ad Spend since 2016. "
    "Federal courts have ruled Google illegally monopolized search advertising. "
    "Get the facts, fit criteria and risks. Use them for your agency or your clients. "
    "The Google Advertiser Claims, explained. DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"
)
SEED = 10001

from diffusers import WanVACEPipeline, AutoencoderKLWan
from diffusers.utils import export_to_video

t0 = time.time()
model_id = "Wan-AI/Wan2.1-VACE-14B-diffusers"
vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
pipe = WanVACEPipeline.from_pretrained(model_id, vae=vae, torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()
load_s = time.time() - t0
log("VACE loaded in", load_s, "s")

frame_paths = sorted(glob.glob("/workspace/in/frames_jpg/*.jpg"))
mask_paths = sorted(glob.glob("/workspace/in/board_masks/*.png"))
assert len(frame_paths) == len(mask_paths) == 81

# Fix: the first attempt passed the full original (garbled-text) video as
# conditioning alongside the mask, which gives the model a shortcut to just
# copy the existing pixels in the "generate" region instead of regenerating
# them -- the standard VACE inpainting input blacks out the video itself in
# the region to be generated, so there is nothing to copy from.
video_in = []
for fp, mp in zip(frame_paths, mask_paths):
    frame = np.array(Image.open(fp).convert("RGB").resize((832, 480)))
    mask = np.array(Image.open(mp).convert("L").resize((832, 480)))
    frame[mask > 127] = 0
    video_in.append(Image.fromarray(frame))
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
export_to_video(out, f"{OUT}/test_a_vace_retry.mp4", fps=16)
sha = sha256_file(f"{OUT}/test_a_vace_retry.mp4")
log("VACE retry generate_s", gen_s, "sha256", sha)

record = {"test": "A_vace_retry_blacked_out_input", "load_s": load_s, "generate_s": gen_s,
          "sha256": sha, "file": "test_a_vace_retry.mp4", "steps": 30, "seed": SEED}
with open(f"{OUT}/raw_record_retry.json", "w") as f:
    json.dump(record, f, indent=1)
log("ALL_DONE")
with open(f"{OUT}/SESSION_DONE", "w") as f:
    f.write("done\n")
