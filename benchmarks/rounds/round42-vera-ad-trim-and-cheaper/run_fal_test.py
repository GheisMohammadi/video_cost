"""Round 42: regenerate round 41's ad (fixing the opening-frame glitch at
generation time, not by post-trim) and compare cheap models/resolutions
for cost.

Usage:
  python3 run_fal_test.py minimax_480p
  python3 run_fal_test.py minimax_768p
  python3 run_fal_test.py pixverse_540p
"""
import base64
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
KEY_FILE = os.path.join(ROOT, "server", "falAPI.txt")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIPS_DIR = os.path.join(OUT_DIR, "clips")
RAW_DIR = os.path.join(OUT_DIR, "raw")
ANCHOR_IMAGE = os.path.join(
    OUT_DIR, "..", "round41-vera-deepen-ad",
    "Vera-Deepen-Character-Kit-v0.2", "assets", "vera-portrait-v01.png",
)

TOOL = sys.argv[1] if len(sys.argv) > 1 else None
if TOOL not in ("minimax_480p", "minimax_768p", "pixverse_540p"):
    raise SystemExit("usage: run_fal_test.py <minimax_480p|minimax_768p|pixverse_540p>")

with open(os.path.join(OUT_DIR, "prompt_short.txt")) as f:
    PROMPT = f.read().strip()
with open(os.path.join(OUT_DIR, "prompt_pixverse.txt")) as f:
    PROMPT_PIXVERSE = f.read().strip()

TOOLS = {
    "minimax_480p": {
        "endpoint": "minimax/h3-max-turbo/image-to-video",
        "payload": {"prompt": PROMPT, "duration": 15, "resolution": "480P"},
    },
    "minimax_768p": {
        "endpoint": "minimax/h3-max-turbo/image-to-video",
        "payload": {"prompt": PROMPT, "duration": 15, "resolution": "768P"},
    },
    "pixverse_540p": {
        "endpoint": "fal-ai/pixverse/v6/image-to-video",
        "payload": {"prompt": PROMPT_PIXVERSE, "duration": 14, "resolution": "540p", "aspect_ratio": "9:16"},
    },
}

CONFIG = TOOLS[TOOL]
ENDPOINT = CONFIG["endpoint"]
PAYLOAD = dict(CONFIG["payload"])


def read_key():
    with open(KEY_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                return line
    raise RuntimeError("no key found in " + KEY_FILE)


def image_data_url(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"


def post(url, key, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": f"Key {key}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main():
    os.makedirs(CLIPS_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    key = read_key()

    payload = dict(PAYLOAD)
    payload["image_url"] = image_data_url(ANCHOR_IMAGE)

    name = f"round42_{TOOL}_v5"
    print(f"--- {name} (endpoint={ENDPOINT}) ---", flush=True)
    submit_url = f"https://queue.fal.run/{ENDPOINT}"
    sub = post(submit_url, key, payload)
    request_id = sub["request_id"]
    status_url = sub.get("status_url") or f"https://queue.fal.run/{ENDPOINT}/requests/{request_id}/status"
    result_url = sub.get("response_url") or f"https://queue.fal.run/{ENDPOINT}/requests/{request_id}"
    print(name, "submitted, request_id", request_id, flush=True)

    t0 = time.time()
    while True:
        st = get(status_url, key)
        status = st.get("status")
        print(name, "status", status, "elapsed_s", round(time.time() - t0), flush=True)
        if status == "COMPLETED":
            break
        if status in ("ERROR", "FAILED"):
            raise RuntimeError(f"{name} job failed: {st}")
        time.sleep(8)

    result = get(result_url, key)
    video_url = result["video"]["url"]
    out_path = os.path.join(CLIPS_DIR, f"{name}.mp4")
    urllib.request.urlretrieve(video_url, out_path)
    gen_s = time.time() - t0

    record = {
        "tool": TOOL,
        "endpoint": ENDPOINT,
        "payload": {k: v for k, v in payload.items() if k != "image_url"},
        "anchor_image": os.path.basename(ANCHOR_IMAGE),
        "request_id": request_id,
        "video_url": video_url,
        "generate_s": gen_s,
        "file": os.path.basename(out_path),
    }
    with open(os.path.join(RAW_DIR, f"raw_record_{name}.json"), "w") as f:
        json.dump(record, f, indent=1)
    print(name, "done in", gen_s, "s ->", out_path, flush=True)


if __name__ == "__main__":
    main()
