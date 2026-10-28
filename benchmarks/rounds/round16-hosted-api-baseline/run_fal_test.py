"""Round 16: hosted API baseline (Kling 2.5 Turbo Pro, Seedance 1.0 Pro) via fal.ai.

Reads the fal API key from server/falAPI.txt (never printed), submits one
text-to-video job per model with the round 13-15 whiteboard script, polls
until done, and downloads the result into clips/.
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

L1 = "Thousands of U.S. advertisers are pursuing claims against Google."
L2 = "Advertisers are filing refunds for 20-30% of Ad Spend since 2016."
L3 = "Federal courts have ruled Google illegally monopolized search advertising."
L4 = "Get the facts, fit criteria and risks."
L5 = "DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"

PROMPT_ALL = (
    "a whiteboard with four lines of handwritten text and a smaller line below them. "
    f'The first line reads "{L1}" '
    f'The second line reads "{L2}" '
    f'The third line reads "{L3}" '
    f'The fourth line reads "{L4}" '
    f'Below in smaller text it reads "{L5}" '
    "a white, male lawyer stands beside the whiteboard holding a marker, "
    "pointing at the board and explaining it to the camera"
)

MODELS = {
    "kling": {
        "endpoint": "fal-ai/kling-video/v2.5-turbo/pro/text-to-video",
        "payload": {"prompt": PROMPT_ALL, "duration": "5"},
    },
    "seedance": {
        "endpoint": "fal-ai/bytedance/seedance/v1/pro/text-to-video",
        "payload": {"prompt": PROMPT_ALL, "duration": "5", "resolution": "1080p"},
    },
}


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
        headers={
            "Authorization": f"Key {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": f"Key {key}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def run_model(name, cfg, key):
    print(f"--- {name} ---", flush=True)
    submit_url = f"https://queue.fal.run/{cfg['endpoint']}"
    sub = post(submit_url, key, cfg["payload"])
    request_id = sub["request_id"]
    status_url = sub.get("status_url") or f"https://queue.fal.run/{cfg['endpoint']}/requests/{request_id}/status"
    result_url = sub.get("response_url") or f"https://queue.fal.run/{cfg['endpoint']}/requests/{request_id}"
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
    out_path = os.path.join(CLIPS_DIR, f"{name}_round16.mp4")
    urllib.request.urlretrieve(video_url, out_path)
    gen_s = time.time() - t0

    record = {
        "model": name,
        "endpoint": cfg["endpoint"],
        "payload": cfg["payload"],
        "request_id": request_id,
        "video_url": video_url,
        "generate_s": gen_s,
        "file": os.path.basename(out_path),
    }
    with open(os.path.join(RAW_DIR, f"raw_record_{name}.json"), "w") as f:
        json.dump(record, f, indent=1)
    print(name, "done in", gen_s, "s ->", out_path, flush=True)
    return record


def main():
    os.makedirs(CLIPS_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    key = read_key()
    targets = sys.argv[1:] or list(MODELS.keys())
    for name in targets:
        run_model(name, MODELS[name], key)


if __name__ == "__main__":
    main()
