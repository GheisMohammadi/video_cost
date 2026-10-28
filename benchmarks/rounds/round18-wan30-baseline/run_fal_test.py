"""Round 18: Wan 3.0 text-rendering check via fal.ai.

Reads the fal API key from server/falAPI.txt (never printed), submits one
text-to-video job with the round 13-17 whiteboard script, polls until
done, and downloads the result into clips/.
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
    "pointing at the board and explaining it to the camera, the whiteboard stays fully visible in frame"
)

ENDPOINT = "alibaba/wan-3.0/text-to-video"
SEED = 10001
PAYLOAD = {
    "prompt": PROMPT_ALL,
    "duration": 5,
    "resolution": "1080p",
    "aspect_ratio": "16:9",
    "seed": SEED,
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

    print("--- wan30 ---", flush=True)
    submit_url = f"https://queue.fal.run/{ENDPOINT}"
    sub = post(submit_url, key, PAYLOAD)
    request_id = sub["request_id"]
    status_url = sub.get("status_url") or f"https://queue.fal.run/{ENDPOINT}/requests/{request_id}/status"
    result_url = sub.get("response_url") or f"https://queue.fal.run/{ENDPOINT}/requests/{request_id}"
    print("wan30 submitted, request_id", request_id, flush=True)

    t0 = time.time()
    while True:
        st = get(status_url, key)
        status = st.get("status")
        print("wan30 status", status, "elapsed_s", round(time.time() - t0), flush=True)
        if status == "COMPLETED":
            break
        if status in ("ERROR", "FAILED"):
            raise RuntimeError(f"wan30 job failed: {st}")
        time.sleep(10)

    result = get(result_url, key)
    video_url = result["video"]["url"]
    out_path = os.path.join(CLIPS_DIR, "wan30_round18.mp4")
    urllib.request.urlretrieve(video_url, out_path)
    gen_s = time.time() - t0

    record = {
        "model": "wan30",
        "endpoint": ENDPOINT,
        "payload": PAYLOAD,
        "request_id": request_id,
        "video_url": video_url,
        "generate_s": gen_s,
        "file": os.path.basename(out_path),
    }
    with open(os.path.join(RAW_DIR, "raw_record_wan30.json"), "w") as f:
        json.dump(record, f, indent=1)
    print("wan30 done in", gen_s, "s ->", out_path, flush=True)


if __name__ == "__main__":
    main()
