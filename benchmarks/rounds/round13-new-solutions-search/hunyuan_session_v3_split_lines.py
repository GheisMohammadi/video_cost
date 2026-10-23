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

# v2 (one ~400-char quoted block) got a large fraction of individual words
# right but scrambled their order. The Prompt Handbook's own text-rendering
# examples never exceed ~17 characters, and its only multi-text example uses
# several separate short quoted phrases, not one long quote. v3 tests that
# documented pattern: the same script, split into five separate, shorter
# quoted lines, each introduced individually, instead of one long quote.
PROMPT = (
    'a whiteboard with four lines of handwritten text and a smaller line below them. '
    'The first line reads "Thousands of U.S. advertisers are pursuing claims against Google." '
    'The second line reads "Advertisers are filing refunds for 20-30% of Ad Spend since 2016." '
    'The third line reads "Federal courts have ruled Google illegally monopolized search advertising." '
    'The fourth line reads "Get the facts, fit criteria and risks." '
    'Below in smaller text it reads "DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM" '
    'a white, male lawyer stands beside the whiteboard holding a marker, pointing at the board and explaining it to the camera'
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
export_to_video(video, f"{OUT}/hunyuan_lawyer_v3_split_lines.mp4", fps=24)
sha = sha256_file(f"{OUT}/hunyuan_lawyer_v3_split_lines.mp4")
log("generate_s", gen_s, "sha256", sha)

record = {
    "model": "hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-480p_t2v",
    "prompt_id": "round10_lawyer_whiteboard_split_lines",
    "note": "v3: same script as v2, split into five shorter separate quoted lines instead of one long quote",
    "seed": SEED,
    "height": 480, "width": 832, "num_frames": 121, "fps": 24,
    "num_inference_steps": 50,
    "load_s": load_s, "generate_s": gen_s,
    "sha256": sha, "file": "hunyuan_lawyer_v3_split_lines.mp4",
}
with open(f"{OUT}/raw_record_v3.json", "w") as f:
    json.dump(record, f, indent=1)

log("ALL_DONE")
with open(f"{OUT}/SESSION_DONE", "w") as f:
    f.write("done\n")
