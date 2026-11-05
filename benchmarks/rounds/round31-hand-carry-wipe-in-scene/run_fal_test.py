"""Round 31: same chain/onset/no-echo/size/face rules as round 30, with two
changes:

1. Every row's clip except the last ends with her moving the marker tip
   down to the start of the next blank line, head slowly turning to follow
   the hand -- not cutting back to the camera. The next row's I2V chain
   starts from that frame, so the hand is already in position: no jump cut
   at the row boundary.
2. The board-wipe is now part of row 4's own generation (pick up an
   eraser, wipe the board, move the marker back to the row-1 start
   position), instead of a separate digital-inpaint handoff. Row 5 is then
   a normal I2V chain continuation from row 4's real last frame -- no
   `wipe_board.py`, no "wipe" argument, no separate prompt branch for it.

Usage:
  python3 run_fal_test.py 1
      # row 1, text-to-video, new presenter + blank board
  python3 run_fal_test.py 2 clips/wan30_round31_row1.mp4
      # row 2, chained from row 1 (hand already at row 2's start in that frame)
  python3 run_fal_test.py 5 clips/wan30_round31_row4.mp4
      # row 5, chained from row 4 (board already wiped, hand at row 1's position)
"""
import base64
import json
import os
import subprocess
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
IS_LAST_ROW = ROW_INDEX == len(ROWS)
IS_WIPE_ROW = ROW_INDEX == 4

PRESENTER = "a pretty young woman, standing in a bright well-lit room in front of a whiteboard, fully visible from the waist up"

ONSET_RULE = (
    "At the start of this clip, the visible board surface has no new ink on it beyond "
    "what is already shown -- no stray marks, no partial letters, nothing floating or "
    "disconnected from the marker tip. The very first new mark of ink only begins at the "
    "exact moment the tip is already pressed against the board and already moving -- "
    "never before, never while the tip is still in the air or still being raised."
)

NO_ECHO_RULE = (
    "Do not repeat, continue, retrace, or reuse any part of the text already written on "
    f'the board, including any text from the previous line above. The only new text written '
    f'in this clip is the sentence "{ROW}" -- write exactly that and nothing else. The line '
    "where she is about to write is two full lines below the topmost finished sentence on "
    "the board, clearly separate from it -- not on the same line as, not merged with, and "
    "not overlapping any text that is already there."
)

STRAY_MARK_RULE = (
    "There may already be a short faint mark or line at the marker tip's current position. "
    "That mark is not text, is not part of any sentence, and is not something to preserve, "
    "continue, or write around -- it is simply where her hand happens to be resting. The new "
    "sentence begins fresh at that exact position, written as entirely new ink, completely "
    "independent of that mark."
)

SIZE_RULE = (
    "Her handwriting is small and compact -- each letter no taller than roughly a "
    "twelfth of the board's height. The entire sentence fits on a single horizontal "
    "line without wrapping to a second line and without needing to shrink mid-sentence "
    "to fit; she leaves consistent blank space below each line for the rows still to "
    "come."
)

FACE_RULE = (
    "Her face, age, and features do not change from the start of the clip to the end -- "
    "the exact same person throughout, no drift in her appearance."
)

CARRY_HAND_RULE = (
    "After the sentence is completely finished, she does not look at the camera. Instead, "
    "keeping her eyes on the board, she lifts the marker tip slightly off the board surface "
    "so it is no longer touching it, and moves her hand and the marker through the air, "
    "steadily down to a blank area of the board just below what she just wrote. While the "
    "tip is lifted and traveling through the air, it leaves no ink, no mark, no line, no "
    "trace, no retracing, and no repeating of any letter or word already on the board -- the "
    "board's existing text stays exactly as it is, completely unchanged, and absolutely no "
    "new ink of any kind appears anywhere on the board during this motion. Once her hand "
    "arrives at the blank line below, she lowers the tip to rest lightly against the board "
    "at the left edge of that blank line, touching but not pressing or dragging, so still no "
    "ink appears even at that final resting position. Her head slowly turns to follow her "
    "hand as it moves through the air, the same way a person's gaze naturally tracks their "
    "own hand -- it is not a sudden cut, it is one continuous, slow head turn following the "
    "hand's path. By the final frame of the clip, her hand and the marker tip are at rest, "
    "untouched by ink, at the left edge of that new blank line, not still at the end of the "
    "sentence she just wrote, and the blank line itself remains completely empty."
)

END_LOOK_RULE = (
    "Only after the sentence is completely finished does she turn her head to look at the "
    "camera, since this is the final line of the video."
)

WIPE_AND_RESET_RULE = (
    "After the sentence is completely finished, she does not look at the camera. Keeping "
    "her eyes on the board, she reaches down, picks up a board eraser/cleaner cloth from "
    "the tray below the whiteboard, and wipes the entire board clean with a few steady "
    "strokes left to right and top to bottom, fully erasing every line of text that was on "
    "it. She then sets the eraser back down, picks the marker back up, and moves the marker "
    "tip to the top-left corner of the now-blank board, positioning it there ready to begin "
    "writing a new line from the top. Her head follows her hand throughout this entire "
    "sequence -- erasing, then moving to the top-left -- the same way a person's gaze "
    "naturally tracks their own hand; it is one continuous, slow motion, not a cut. By the "
    "final frame of the clip, the board is completely blank, and her hand and the marker tip "
    "are at rest at the top-left corner of the board, not still holding the eraser and not "
    "already writing anything new."
)

if ROW_INDEX == 1:
    ENDPOINT = "alibaba/wan-3.0/text-to-video"
    END_RULE = CARRY_HAND_RULE
    PROMPT = (
        f"vertical 9:16 video, the frame fully filled edge to edge with no letterboxing and "
        f"no padding bars at the top or bottom. wide shot, {PRESENTER}. the whiteboard "
        "beside her is completely blank. {onset} at the very start she looks at the "
        "camera for a moment, then turns her head to look at the whiteboard and keeps her "
        "eyes on the board and on the marker tip for the rest of the clip -- she never "
        "looks at the camera again after this opening moment, since no person can write "
        "accurately on a board without looking at it. she holds a black marker, its tip "
        "touching the whiteboard surface. {size} the marker tip moves slowly and steadily "
        "from left to right across the board, and a single continuous line of black ink "
        "trail appears exactly where the tip has physically touched, one letter forming "
        "at a time, following the tip precisely -- no ink or text ever appears ahead of "
        "or away from the tip's current position, and no part of the text ever fades in "
        "on its own; every letter is drawn by the moving tip. "
        f'The tip traces out the full sentence, "{ROW}" letter by letter, left to right, '
        "in small cursive handwriting, staying on a single line. {end_rule} the camera "
        "holds steady the entire time."
    ).format(onset=ONSET_RULE, size=SIZE_RULE, end_rule=END_RULE)
else:
    ENDPOINT = "alibaba/wan-3.0/image-to-video"
    if IS_LAST_ROW:
        END_RULE = END_LOOK_RULE
    elif IS_WIPE_ROW:
        END_RULE = WIPE_AND_RESET_RULE
    else:
        END_RULE = CARRY_HAND_RULE

    PROMPT = (
        "continuing from this exact frame -- same woman, same outfit, same whiteboard, "
        "same room, same camera framing, nothing changes about the scene itself. {face} "
        "she is already holding the black marker, its tip already positioned at the left "
        "edge of a blank line on the board, ready to write. without any pause or "
        "repositioning, she immediately begins writing a new row of text starting exactly "
        "where the tip already is. {stray} {no_echo} {onset} {size} the marker tip moves slowly "
        "and steadily from left to right across the board, and a single continuous line of "
        "black ink trail appears exactly where the tip has physically touched, one letter "
        "forming at a time, following the tip precisely -- no ink or text ever appears "
        "ahead of or away from the tip's current position, and no part of the text ever "
        "fades in on its own; every letter is drawn by the moving tip. "
        f'The tip traces out the full sentence, "{ROW}" letter by letter, left to right, in '
        "small cursive handwriting, staying on a single line, in the same handwriting "
        "style and size as any text already on the board. her eyes stay on the whiteboard "
        "and the marker tip throughout the writing. {end_rule} the camera holds steady the "
        "entire time."
    ).format(face=FACE_RULE, stray=STRAY_MARK_RULE, no_echo=NO_ECHO_RULE, onset=ONSET_RULE, size=SIZE_RULE, end_rule=END_RULE)

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
    raw_frame = os.path.join(RAW_DIR, f"_chain_start_frame_row{ROW_INDEX}_raw.png")
    os.system(f'ffmpeg -y -v error -sseof -0.1 -i "{clip_path}" -frames:v 1 "{raw_frame}"')

    denoised_frame = os.path.join(RAW_DIR, f"_chain_start_frame_row{ROW_INDEX}_denoised.png")
    subprocess.run(
        [sys.executable, os.path.join(OUT_DIR, "denoise_frame.py"), raw_frame, denoised_frame],
        check=True,
    )

    with open(denoised_frame, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"


def main():
    os.makedirs(CLIPS_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    key = read_key()

    payload = dict(PAYLOAD)
    if ROW_INDEX > 1:
        if not PREV_CLIP:
            raise RuntimeError("row > 1 requires the previous clip path as 2nd arg")
        payload["start_image_url"] = extract_last_frame_b64(PREV_CLIP)

    name = f"wan30_round31_row{ROW_INDEX}"
    print(f"--- {name} ({ROW!r}, endpoint={ENDPOINT}, last_row={IS_LAST_ROW}, wipe_row={IS_WIPE_ROW}) ---", flush=True)
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
        "is_last_row": IS_LAST_ROW,
        "is_wipe_row": IS_WIPE_ROW,
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
