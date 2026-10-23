import os, json, time, hashlib
os.environ["HF_HOME"] = "/workspace/hfcache"
os.environ["HF_HUB_CACHE"] = "/workspace/hfcache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/workspace/hfcache"

import torch
from diffusers import HunyuanVideo15Pipeline
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

# Per the official HunyuanVideo 1.5 Prompt Handbook (section II.4, "In-Video
# Bilingual Text Rendering"), literal on-screen text must be wrapped in
# quotation marks to engage the model's glyph-aware text encoder -- the
# first attempt (round13_hunyuan_session.py) described the script in prose
# without quotes, which does not use the documented text-rendering path.
PROMPT = (
    'a white, male lawyer uses a marker to write on a whiteboard, the whiteboard shows the exact text '
    '"Thousands of U.S. advertisers are pursuing claims against Google. Advertisers are filing refunds '
    'for 20-30% of Ad Spend since 2016. Federal courts have ruled Google illegally monopolized search '
    'advertising. Get the facts, fit criteria and risks. Use them for your agency or your clients. '
    'The Google Advertiser Claims, explained. DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM", '
    'the lawyer points at the board and explains it to the camera'
)
SEED = 10001

t0 = time.time()
dtype = torch.bfloat16
pipe = HunyuanVideo15Pipeline.from_pretrained(
    "hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-480p_t2v", torch_dtype=dtype
)
pipe.enable_model_cpu_offload()
pipe.vae.enable_tiling()
load_s = time.time() - t0
log("HunyuanVideo-1.5 loaded in", load_s, "s")

generator = torch.Generator(device="cuda").manual_seed(SEED)

t0 = time.time()
video = pipe(
    prompt=PROMPT,
    generator=generator,
    height=480,
    width=832,
    num_frames=121,
    num_inference_steps=50,
).frames[0]
gen_s = time.time() - t0
export_to_video(video, f"{OUT}/hunyuan_lawyer_v2_quoted.mp4", fps=24)
sha = sha256_file(f"{OUT}/hunyuan_lawyer_v2_quoted.mp4")
log("generate_s", gen_s, "sha256", sha)

record = {
    "model": "hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-480p_t2v",
    "prompt_id": "round10_lawyer_whiteboard_quoted",
    "note": "v2: literal text wrapped in quotation marks per official Prompt Handbook section II.4",
    "seed": SEED,
    "height": 480, "width": 832, "num_frames": 121, "fps": 24,
    "num_inference_steps": 50,
    "load_s": load_s, "generate_s": gen_s,
    "sha256": sha, "file": "hunyuan_lawyer_v2_quoted.mp4",
}
with open(f"{OUT}/raw_record_v2.json", "w") as f:
    json.dump(record, f, indent=1)

log("ALL_DONE")
with open(f"{OUT}/SESSION_DONE", "w") as f:
    f.write("done\n")
