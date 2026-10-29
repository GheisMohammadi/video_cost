"""Round 22, segment A only: new script, wide shot with a visible woman presenter,
portrait 9:16, 720p. Re-tests marker-to-letter sync at wide framing (round 20/21
verified sync only at extreme close-up with no presenter visible).

Run segment A alone first; do not run segment B until A is inspected.
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

SEGMENT = sys.argv[1] if len(sys.argv) > 1 else "A"

# Each sentence is pre-split into short rows that fit on one board row at this
# framing, so the model is never left to decide its own wrap point -- it was
# wrapping sentences into two rows and filling both rows at once (letters
# appearing in row 2 before row 1 had every word), which is what a real person
# writing by hand cannot do. Giving explicit short rows avoids that entirely.
ROWS = {
    "A": ["I vibe-coded my app", "in a weekend.", "Launched; 19", "signed up."],
    "B": ["So this week I pay", "$99 on x.country", "to grow my business", "on TikTok."],
}
LINES = ROWS[SEGMENT]

PRESENTER = (
    "a young white woman, attractive and fashionable, with styled hair and modern "
    "stylish clothing, standing in a bright well-lit room in front of a whiteboard, "
    "fully visible from the waist up"
)

# Chain the rows with the same sequencing language verified in round 21 (one
# line fully done before the next begins), generalized from 2 rows to N.
row_steps = []
for i, row in enumerate(LINES):
    if i == 0:
        row_steps.append(
            f'First, the tip traces out the full first row, "{row}" letter by letter, '
            "left to right."
        )
    else:
        row_steps.append(
            "Only after that entire row is completely finished does she move the marker "
            f'down to start the next row -- no part of it appears while the row above is '
            f'still being written. Then the tip traces out the next row, "{row}" letter '
            "by letter, left to right, the same way."
        )
ROW_SEQUENCE = " ".join(row_steps)

PROMPT = (
    f"wide shot, {PRESENTER}. the whiteboard beside her is completely blank. at the very "
    "start she looks at the camera for a moment, then turns her head to look at the "
    "whiteboard and keeps her eyes on the board and on the marker tip the entire time she "
    "is writing -- she never looks at the camera while actively writing, since no person "
    "can write accurately on a board without looking at it. she holds "
    "a black marker, its tip touching the whiteboard surface. the marker tip moves slowly "
    "and steadily from left to right across the board, and a single continuous line of "
    "black ink trail appears exactly where the tip has physically touched, one letter "
    "forming at a time, following the tip precisely -- no ink or text ever appears ahead "
    "of or away from the tip's current position. "
    f"{ROW_SEQUENCE} "
    "no two rows are ever written at the same time -- each row is entirely finished before "
    "the next one starts. in cursive handwriting. her eyes stay on the whiteboard and the "
    "marker tip throughout the writing, not on the camera. only after all four rows are "
    "completely finished does she turn her head back to look at the camera. the camera "
    "holds steady the entire time."
)

ENDPOINT = "alibaba/wan-3.0/text-to-video"
SEED = 10001
PAYLOAD = {
    "prompt": PROMPT,
    "duration": 15,
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

    name = f"wan30_round22_seg{SEGMENT}"
    print(f"--- {name} ---", flush=True)
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
        "model": name,
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
