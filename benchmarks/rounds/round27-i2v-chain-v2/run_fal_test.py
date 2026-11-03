"""Round 27: image-to-video chaining across all 8 rows (row N+1 starts from
row N's literal last frame, so outfit/board/room cannot reinvent themselves
between rows), with a strict onset-sync rule (carried over from round 24)
and an explicit no-echo instruction fixing round 24's row-2 defect, where
the model repeated/continued the previous row's text instead of writing the
new row's sentence.

Usage:
  python3 run_fal_test.py 1                    # text-to-video, row 1
  python3 run_fal_test.py 2 clips/wan30_round27_row1.mp4   # image-to-video, row 2 chained from row1's last frame
  python3 run_fal_test.py 3 clips/wan30_round27_row2.mp4   # etc.
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

ROW_INDEX = int(sys.argv[1]) if len(sys.argv) > 1 else 1
PREV_CLIP = sys.argv[2] if len(sys.argv) > 2 else None
# "fresh" forces a text-to-video generation (blank board) even for ROW_INDEX > 1,
# used to start a new chain segment once the board/chain-degradation limit is hit.
FRESH_SEGMENT = PREV_CLIP == "fresh"
if FRESH_SEGMENT:
    PREV_CLIP = None

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

PRESENTER = "a pretty young woman, standing in a bright well-lit room in front of a whiteboard, fully visible from the waist up"

# No ink before tip contact -- carried over unchanged from round 24.
ONSET_RULE = (
    "At the start of this clip, the visible board surface has no new ink on it beyond "
    "what is already shown -- no stray marks, no partial letters, nothing floating or "
    "disconnected from the marker tip. The very first new mark of ink only begins at the "
    "exact moment the tip is already pressed against the board and already moving -- "
    "never before, never while the tip is still in the air or still being raised."
)

# Fix for round 24's row-2 defect: the model echoed/continued the previous
# row's text instead of writing the new sentence. Explicitly forbid that.
NO_ECHO_RULE = (
    "Do not repeat, continue, retrace, or reuse any part of the text already written on "
    f'the board. The only new text written in this clip is the sentence "{ROW}" -- write '
    "exactly that and nothing else."
)

if ROW_INDEX == 1 or FRESH_SEGMENT:
    ENDPOINT = "alibaba/wan-3.0/text-to-video"
    PROMPT = (
        f"vertical 9:16 video, the frame fully filled edge to edge with no letterboxing and "
        f"no padding bars at the top or bottom. wide shot, {PRESENTER}. the whiteboard "
        f"beside her is completely blank. {ONSET_RULE} at the very start she looks at the "
        "camera for a moment, then turns her head to look at the whiteboard and keeps her "
        "eyes on the board and on the marker tip the entire time she is writing -- she "
        "never looks at the camera while actively writing, since no person can write "
        "accurately on a board without looking at it. she holds a black marker, its tip "
        "touching the whiteboard surface. the marker tip moves slowly and steadily from "
        "left to right across the board, and a single continuous line of black ink trail "
        "appears exactly where the tip has physically touched, one letter forming at a "
        "time, following the tip precisely -- no ink or text ever appears ahead of or away "
        "from the tip's current position, and no part of the text ever fades in on its "
        "own; every letter is drawn by the moving tip. "
        f'The tip traces out the full sentence, "{ROW}" letter by letter, left to right, '
        "in cursive handwriting. her eyes stay on the whiteboard and the marker tip "
        "throughout the writing, not on the camera. only after the row is completely "
        "finished does she turn her head back to look at the camera. the camera holds "
        "steady the entire time."
    )
else:
    ENDPOINT = "alibaba/wan-3.0/image-to-video"
    PROMPT = (
        "continuing from this exact frame -- same woman, same outfit, same whiteboard, "
        "same room, same camera framing, nothing changes about the scene itself. she is "
        "still holding the black marker. she now moves the marker tip to a blank area of "
        f"the board below her previous writing and begins a new row of text. {NO_ECHO_RULE} "
        f"{ONSET_RULE} the marker tip moves slowly and steadily from left to right across "
        "the board, and a single continuous line of black ink trail appears exactly where "
        "the tip has physically touched, one letter forming at a time, following the tip "
        "precisely -- no ink or text ever appears ahead of or away from the tip's current "
        "position, and no part of the text ever fades in on its own; every letter is drawn "
        "by the moving tip. "
        f'The tip traces out the full sentence, "{ROW}" letter by letter, left to right, in '
        "cursive handwriting, in the same handwriting style as the text already on the "
        "board. her eyes stay on the whiteboard and the marker tip throughout the writing. "
        "only after the row is completely finished does she turn her head back to look at "
        "the camera. the camera holds steady the entire time."
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


def extract_last_frame_b64(clip_path):
    frame_path = os.path.join(RAW_DIR, f"_chain_start_frame_row{ROW_INDEX}.png")
    os.system(f'ffmpeg -y -v error -sseof -0.1 -i "{clip_path}" -frames:v 1 "{frame_path}"')
    with open(frame_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"


def main():
    os.makedirs(CLIPS_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    key = read_key()

    payload = dict(PAYLOAD)
    if ROW_INDEX > 1 and not FRESH_SEGMENT:
        if not PREV_CLIP:
            raise RuntimeError("row > 1 requires the previous clip path as 2nd arg")
        payload["start_image_url"] = extract_last_frame_b64(PREV_CLIP)

    name = f"wan30_round27_row{ROW_INDEX}"
    print(f"--- {name} ({ROW!r}, endpoint={ENDPOINT}) ---", flush=True)
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
        "model": name,
        "row_index": ROW_INDEX,
        "row_text": ROW,
        "endpoint": ENDPOINT,
        "chained_from": PREV_CLIP,
        "payload": {k: v for k, v in payload.items() if k != "start_image_url"},
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
