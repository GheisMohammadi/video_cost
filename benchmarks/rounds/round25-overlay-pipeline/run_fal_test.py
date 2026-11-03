"""Round 25: generate presenter-only footage with Wan 3.0 -- the model is
told explicitly that moving the marker leaves no mark on the board. The
actual handwriting is added afterward by a separate, deterministic
compositing step (see track_tip.py, render_text.py, composite.py), not by
this generation.

Usage: python3 run_fal_test.py <row_index 1-8>
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

ROW_INDEX = int(sys.argv[1]) if len(sys.argv) > 1 else 1

ROWS = [
    "I vibe-coded my app",
    "in a weekend.",
    "Launched; 19",
    "signed up.",
    "So this week I pay",
    "$99 on x.country",
    "to grow my business",
    "on TikTok.",
]
ROW = ROWS[ROW_INDEX - 1]

PRESENTER = (
    "a young white woman, attractive and fashionable, with styled hair and modern "
    "stylish clothing, standing in a bright well-lit room in front of a whiteboard, "
    "fully visible from the waist up"
)

ENDPOINT = "alibaba/wan-3.0/text-to-video"
PROMPT = (
    f"vertical 9:16 video, the frame fully filled edge to edge with no letterboxing "
    f"and no padding bars at the top or bottom. wide shot, {PRESENTER}. the "
    "whiteboard beside her is completely blank and stays completely blank the entire "
    "time -- the marker never touches the board and leaves no ink, no mark, no line, "
    "nothing at all on the board surface; the board must look identical at the end of "
    "the clip as it does at the start. at the very start she looks at the camera for "
    "a moment, then turns her head to look at the whiteboard and keeps her eyes on "
    "the board and on the marker tip the entire time she is writing -- she never "
    "looks at the camera while actively writing, since no person can write "
    "accurately on a board without looking at it. she holds a black marker a few "
    "inches from the whiteboard surface, not touching it. her hand moves the marker "
    "slowly and steadily from left to right in the air just in front of the board, "
    "mimicking the motion of writing a sentence letter by letter, left to right, as "
    "if writing in cursive -- but the marker tip never makes contact with the board "
    "and no ink ever appears. her eyes stay on the whiteboard and the marker tip "
    "throughout the motion, not on the camera. only after the motion is completely "
    "finished does she turn her head back to look at the camera. the camera holds "
    "steady the entire time."
)

SEED = 10001
PAYLOAD = {
    "prompt": PROMPT,
    "duration": 5,
    "resolution": "720p",
    "aspect_ratio": "9:16",
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

    name = f"wan30_round25_row{ROW_INDEX}"
    print(f"--- {name} ({ROW!r}, endpoint={ENDPOINT}) ---", flush=True)
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
        "model": name,
        "row_index": ROW_INDEX,
        "row_text": ROW,
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
