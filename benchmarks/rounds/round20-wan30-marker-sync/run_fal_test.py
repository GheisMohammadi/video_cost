"""Round 20: can a more explicit prompt get the marker to trace letters in real time?

Single short line, same model/seed as rounds 18-19, prompt rewritten to
be mechanically explicit about the pen tip and ink trail instead of
describing the end result ("he writes a line that reads...").
"""
import json
import os
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
KEY_FILE = os.path.join(ROOT, "server", "falAPI.txt")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIPS_DIR = os.path.join(OUT_DIR, "clips")
RAW_DIR = os.path.join(OUT_DIR, "raw")

L1 = "Thousands of U.S. advertisers are pursuing claims against Google."

PROMPT = (
    "extreme close-up on a whiteboard, completely blank. a hand holds a black marker, "
    "its tip touching the whiteboard surface. the marker tip moves slowly and steadily from "
    "left to right across the board, and a single continuous line of black ink trail appears "
    "exactly where the tip has physically touched, one letter forming at a time, following the "
    "tip precisely -- no ink or text ever appears ahead of or away from the tip's current position. "
    f'By the time the tip reaches the end of the line, it has traced out the full sentence "{L1}" '
    "letter by letter, left to right, in cursive handwriting. the camera holds steady on the "
    "whiteboard the entire time."
)

ENDPOINT = "alibaba/wan-3.0/text-to-video"
SEED = 10001
PAYLOAD = {
    "prompt": PROMPT,
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

    print("--- wan30_marker_sync ---", flush=True)
    submit_url = f"https://queue.fal.run/{ENDPOINT}"
    sub = post(submit_url, key, PAYLOAD)
    request_id = sub["request_id"]
    status_url = sub.get("status_url") or f"https://queue.fal.run/{ENDPOINT}/requests/{request_id}/status"
    result_url = sub.get("response_url") or f"https://queue.fal.run/{ENDPOINT}/requests/{request_id}"
    print("wan30_marker_sync submitted, request_id", request_id, flush=True)

    t0 = time.time()
    while True:
        st = get(status_url, key)
        status = st.get("status")
        print("wan30_marker_sync status", status, "elapsed_s", round(time.time() - t0), flush=True)
        if status == "COMPLETED":
            break
        if status in ("ERROR", "FAILED"):
            raise RuntimeError(f"wan30_marker_sync job failed: {st}")
        time.sleep(10)

    result = get(result_url, key)
    video_url = result["video"]["url"]
    out_path = os.path.join(CLIPS_DIR, "wan30_marker_sync_round20.mp4")
    urllib.request.urlretrieve(video_url, out_path)
    gen_s = time.time() - t0

    record = {
        "model": "wan30_marker_sync",
        "endpoint": ENDPOINT,
        "payload": PAYLOAD,
        "request_id": request_id,
        "video_url": video_url,
        "generate_s": gen_s,
        "file": os.path.basename(out_path),
    }
    with open(os.path.join(RAW_DIR, "raw_record_wan30_marker_sync.json"), "w") as f:
        json.dump(record, f, indent=1)
    print("wan30_marker_sync done in", gen_s, "s ->", out_path, flush=True)


if __name__ == "__main__":
    main()
