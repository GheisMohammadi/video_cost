import os, json, time, hashlib
os.environ["HF_HOME"] = "/workspace/hfcache"
os.environ["HF_HUB_CACHE"] = "/workspace/hfcache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/workspace/hfcache"

import torch
from PIL import Image
from diffusers import HunyuanVideo15ImageToVideoPipeline
from diffusers.utils import export_to_video

OUT = "/workspace/out"
os.makedirs(OUT, exist_ok=True)

def log(*a):
    print(*a, flush=True)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

L3 = "Federal courts have ruled Google illegally monopolized search advertising."
L4 = "Get the facts, fit criteria and risks."
L5 = "DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"
SEED = 10001

# Round 14's A1 already has lines 1-2 correct on the board (its own final
# frame, used here as the starting image). This continuation asks the model
# to keep writing below the existing text -- same quoted-lines-3-5 content
# and phrasing as round 14's isolated A2 test -- to check whether I2V
# continuity (a) preserves A1's already-correct text and (b) lets the new
# lines render as well as A2's isolated result, instead of degrading the
# way round 14's packed five-quote A3 did.
PROMPT = (
    "the lawyer continues writing on the whiteboard below the existing text, which stays exactly as "
    "shown, unchanged and legible. Two more lines of handwritten text appear below it, with a smaller "
    "line below them. "
    f'The first new line reads "{L3}" '
    f'The second new line reads "{L4}" '
    f'Below in smaller text it reads "{L5}" '
    "the lawyer keeps pointing at the board and explaining it to the camera"
)

start_image = Image.open("/workspace/in/a1_last_frame.png").convert("RGB")
log("start image size", start_image.size)

t0 = time.time()
dtype = torch.bfloat16
pipe = HunyuanVideo15ImageToVideoPipeline.from_pretrained(
    "hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-480p_i2v", torch_dtype=dtype
)
pipe.enable_model_cpu_offload()
pipe.vae.enable_tiling()
load_s = time.time() - t0
log("HunyuanVideo-1.5 I2V loaded in", load_s, "s")

generator = torch.Generator(device="cuda").manual_seed(SEED)

t0 = time.time()
video = pipe(
    image=start_image,
    prompt=PROMPT,
    generator=generator,
    num_frames=121,
    num_inference_steps=50,
).frames[0]
gen_s = time.time() - t0
export_to_video(video, f"{OUT}/i2v_continuation.mp4", fps=24)
sha = sha256_file(f"{OUT}/i2v_continuation.mp4")
log("generate_s", gen_s, "sha256", sha)

record = {
    "model": "hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-480p_i2v",
    "test": "round15_test2_i2v_continuation",
    "note": "I2V continuation from round 14 A1's final frame, adding lines 3-5 as new quoted text",
    "start_image": "round14 A1_two_lines.mp4 final frame (lines 1-2 already correct)",
    "seed": SEED,
    "num_frames": 121, "fps": 24,
    "num_inference_steps": 50,
    "load_s": load_s, "generate_s": gen_s,
    "sha256": sha, "file": "i2v_continuation.mp4",
}
with open(f"{OUT}/raw_record_test2.json", "w") as f:
    json.dump(record, f, indent=1)

log("ALL_DONE")
with open(f"{OUT}/SESSION_DONE", "w") as f:
    f.write("done\n")
