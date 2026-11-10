"""Round 40: screen genuinely cheap video-gen models (PixVerse V6,
MiniMax H3 Max Turbo) against round 33's validated 5-box diagram prompt.

Usage:
  python3 run_fal_test.py pixverse
  python3 run_fal_test.py minimax
"""
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

TOOL = sys.argv[1] if len(sys.argv) > 1 else None
if TOOL not in ("pixverse", "minimax"):
    raise SystemExit("usage: run_fal_test.py <pixverse|minimax>")

with open(os.path.join(OUT_DIR, "prompt_short.txt")) as f:
    PROMPT = f.read().strip()  # both PixVerse (2048 byte) and MiniMax caps require the condensed prompt

TOOLS = {
    "pixverse": {
        "endpoint": "fal-ai/pixverse/v6/text-to-video",
        "payload": {"prompt": PROMPT, "duration": 5, "aspect_ratio": "16:9", "resolution": "720p"},
    },
    "minimax": {
        "endpoint": "minimax/h3-max-turbo/text-to-video",
        "payload": {"prompt": PROMPT, "duration": 5, "aspect_ratio": "16:9", "resolution": "768P"},
    },
}

CONFIG = TOOLS[TOOL]
ENDPOINT = CONFIG["endpoint"]
PAYLOAD = CONFIG["payload"]


def read_key():
    with open(KEY_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                return line
    raise RuntimeError("no key found in " + KEY_FILE)


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

    name = f"round40_{TOOL}"
    print(f"--- {name} (endpoint={ENDPOINT}) ---", flush=True)
    submit_url = f"https://queue.fal.run/{ENDPOINT}"
    sub = post(submit_url, key, PAYLOAD)
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
        "payload": PAYLOAD,
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
