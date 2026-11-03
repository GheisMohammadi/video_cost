"""Round 26: same per-row generation and sync wording as round 23, but with
a fully concrete, pinned-down presenter/scene description repeated verbatim
across every row, instead of round 23's vague adjectives ("stylish
clothing", "styled hair"). The fixed seed only pins the generation noise --
it does not pin how the model interprets a vague adjective, which is the
likely cause of outfit/hair drift across independent per-row generations.

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
    "a young white woman with shoulder-length straight dark brown hair parted in the "
    "middle, wearing a fitted white long-sleeve ribbed top and small gold hoop "
    "earrings, standing in a bright room in front of a white whiteboard mounted on a "
    "light gray wall, fully visible from the waist up"
)

PROMPT = (
    f"vertical 9:16 video, the frame fully filled edge to edge with no letterboxing and no "
    f"padding bars at the top or bottom. wide shot, {PRESENTER}. the whiteboard beside her "
    "is completely blank. at the very "
    "start she looks at the camera for a moment, then turns her head to look at the "
    "whiteboard and keeps her eyes on the board and on the marker tip the entire time she "
    "is writing -- she never looks at the camera while actively writing, since no person "
    "can write accurately on a board without looking at it. she holds a black marker, its "
    "tip touching the whiteboard surface. the marker tip moves slowly and steadily from "
    "left to right across the board, and a single continuous line of black ink trail "
    "appears exactly where the tip has physically touched, one letter forming at a time, "
    "following the tip precisely -- no ink or text ever appears ahead of or away from the "
    "tip's current position, and no part of the text ever fades in on its own; every "
    "letter is drawn by the moving tip. "
    f'The tip traces out the full sentence, "{ROW}" letter by letter, left to right, in '
    "cursive handwriting. her eyes stay on the whiteboard and the marker tip throughout "
    "the writing, not on the camera. only after the row is completely finished does she "
    "turn her head back to look at the camera. the camera holds steady the entire time."
)

ENDPOINT = "alibaba/wan-3.0/text-to-video"
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

    name = f"wan30_round26_row{ROW_INDEX}"
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
