"""Round 14 HunyuanVideo 1.5 tests A1–A3: fewer quotes, deferred lines, reorder.

One model load, three generations. Writes clips + raw_record_*.json under OUT.
Creates SESSION_DONE when finished (or on fatal error after logging).
"""
import os, json, time, hashlib, traceback

os.environ["HF_HOME"] = "/workspace/hfcache"
os.environ["HF_HUB_CACHE"] = "/workspace/hfcache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/workspace/hfcache"

import torch
from diffusers import HunyuanVideo15Pipeline
from diffusers.utils import export_to_video

OUT = "/workspace/out"
os.makedirs(OUT, exist_ok=True)
SEED = 10001
MODEL = "hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-480p_t2v"

# Same sentences as round 13 v3; A tests vary which are quoted in-prompt.
L1 = "Thousands of U.S. advertisers are pursuing claims against Google."
L2 = "Advertisers are filing refunds for 20-30% of Ad Spend since 2016."
L3 = "Federal courts have ruled Google illegally monopolized search advertising."
L4 = "Get the facts, fit criteria and risks."
L5 = "DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"

JOBS = [
    {
        "id": "A1_two_lines",
        "file": "hunyuan_A1_two_lines.mp4",
        "prompt_id": "round14_lawyer_A1_two_lines",
        "note": "Only the two lines that were verbatim-correct in round 13 v3",
        "prompt": (
            "a whiteboard with two lines of handwritten text. "
            f'The first line reads "{L1}" '
            f'The second line reads "{L2}" '
            "a white, male lawyer stands beside the whiteboard holding a marker, "
            "pointing at the board and explaining it to the camera"
        ),
    },
    {
        "id": "A2_deferred_lines",
        "file": "hunyuan_A2_deferred_lines.mp4",
        "prompt_id": "round14_lawyer_A2_deferred",
        "note": "Only lines 3–4 + small print (the lines that degraded in round 13 v3)",
        "prompt": (
            "a whiteboard with two lines of handwritten text and a smaller line below them. "
            f'The first line reads "{L3}" '
            f'The second line reads "{L4}" '
            f'Below in smaller text it reads "{L5}" '
            "a white, male lawyer stands beside the whiteboard holding a marker, "
            "pointing at the board and explaining it to the camera"
        ),
    },
    {
        "id": "A3_reorder",
        "file": "hunyuan_A3_reorder.mp4",
        "prompt_id": "round14_lawyer_A3_reorder",
        "note": "Same five quotes as round 13 v3 but previously-failing lines first",
        "prompt": (
            "a whiteboard with four lines of handwritten text and a smaller line below them. "
            f'The first line reads "{L3}" '
            f'The second line reads "{L4}" '
            f'The third line reads "{L1}" '
            f'The fourth line reads "{L2}" '
            f'Below in smaller text it reads "{L5}" '
            "a white, male lawyer stands beside the whiteboard holding a marker, "
            "pointing at the board and explaining it to the camera"
        ),
    },
]


def log(*a):
    print(*a, flush=True)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mark_done(msg="done"):
    with open(f"{OUT}/SESSION_DONE", "w") as f:
        f.write(msg + "\n")


def main():
    log("round14_hunyuan_session start")
    t0 = time.time()
    dtype = torch.bfloat16
    pipe = HunyuanVideo15Pipeline.from_pretrained(MODEL, torch_dtype=dtype)
    pipe.enable_model_cpu_offload()
    pipe.vae.enable_tiling()
    load_s = time.time() - t0
    log("HunyuanVideo-1.5 loaded in", load_s, "s")

    records = []
    for job in JOBS:
        log("---", job["id"], "---")
        generator = torch.Generator(device="cuda").manual_seed(SEED)
        t0 = time.time()
        video = pipe(
            prompt=job["prompt"],
            generator=generator,
            height=480,
            width=832,
            num_frames=121,
            num_inference_steps=50,
        ).frames[0]
        gen_s = time.time() - t0
        path = f"{OUT}/{job['file']}"
        export_to_video(video, path, fps=24)
        sha = sha256_file(path)
        log("generate_s", gen_s, "sha256", sha, "file", job["file"])
        rec = {
            "model": MODEL,
            "job": job["id"],
            "prompt_id": job["prompt_id"],
            "note": job["note"],
            "seed": SEED,
            "height": 480,
            "width": 832,
            "num_frames": 121,
            "fps": 24,
            "num_inference_steps": 50,
            "load_s": load_s,
            "generate_s": gen_s,
            "sha256": sha,
            "file": job["file"],
        }
        records.append(rec)
        with open(f"{OUT}/raw_record_{job['id']}.json", "w") as f:
            json.dump(rec, f, indent=1)
        # Incremental jobs.jsonl for pull tooling / crash recovery
        with open(f"{OUT}/jobs.jsonl", "a") as f:
            f.write(json.dumps({"job": job["id"], "file": job["file"], "sha256": sha, "generate_s": gen_s}) + "\n")

    with open(f"{OUT}/session.json", "w") as f:
        json.dump({"load_s": load_s, "jobs": records}, f, indent=1)
    log("ALL_DONE")
    mark_done("done")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        mark_done("error")
        raise
