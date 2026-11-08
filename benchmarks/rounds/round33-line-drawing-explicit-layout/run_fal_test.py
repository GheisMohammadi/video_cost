"""Round 33: same 3-tool line-drawing comparison as round 32 (Kling 3.0
Pro, Seedance 2.0, Veo 3.1), with an explicit, position-anchored 5-box
diagram layout replacing round 32's vague box/connection descriptions.

Usage:
  python3 run_fal_test.py kling
  python3 run_fal_test.py seedance
  python3 run_fal_test.py veo
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
if TOOL not in ("kling", "seedance", "veo"):
    raise SystemExit("usage: run_fal_test.py <kling|seedance|veo>")

with open(os.path.join(OUT_DIR, "prompt.txt")) as f:
    PROMPT = f.read().strip()
with open(os.path.join(OUT_DIR, "prompt_kling.txt")) as f:
    PROMPT_KLING = f.read().strip()  # Kling's API caps prompts at 2500 chars; full prompt.txt is 2517

TOOLS = {
    "kling": {
        "endpoint": "fal-ai/kling-video/v3/pro/text-to-video",
        "payload": {"prompt": PROMPT_KLING, "duration": "10", "aspect_ratio": "16:9"},
    },
    "seedance": {
        "endpoint": "bytedance/seedance-2.0/fast/text-to-video",
        "payload": {"prompt": PROMPT, "duration": "10", "aspect_ratio": "16:9", "resolution": "720p"},
    },
    "veo": {
        "endpoint": "fal-ai/veo3.1",
        "payload": {"prompt": PROMPT, "resolution": "1080p", "audio": False},
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

    name = f"round33_{TOOL}"
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
        time.sleep(10)

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
