"""Round 38: apply the whiteboard rounds' line-by-line I2V chaining to
the text+annotation task (round 35-36), testing whether finer-grained
chaining fixes Seedance Mini's quality problems from round 37.

7 chained steps: 4 text lines, then 3 annotations (rectangle around
"vibe-coded", circle around "$99", underline under "x.country").

Usage:
  python3 run_fal_test.py 1
      # step 1, text-to-video, new presenter + blank board
  python3 run_fal_test.py 2 clips/round38_step1.mp4
      # step 2, chained from step 1
  ...
  python3 run_fal_test.py 7 clips/round38_step6.mp4
      # step 7 (final), chained from step 6
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

STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 1
PREV_CLIP = sys.argv[2] if len(sys.argv) > 2 else None
NUM_STEPS = 7
IS_LAST_STEP = STEP == NUM_STEPS

PRESENTER = (
    "a young Asian woman writing and annotating text on a transparent glass writing board "
    "against a matte black background. She wears a plain black T-shirt and blue jeans and "
    "holds a bright neon-yellow marker in her right hand. The camera is fixed, medium-wide "
    "shot, straight-on perspective, professional studio lighting."
)

NO_REFLECTION_RULE = (
    "The glass is perfectly clear with no reflection of her, no mirrored double, no ghost "
    "image, and no second figure visible anywhere in or behind the glass -- only one woman "
    "is ever visible in the frame, at the center, and the area behind and beside the glass "
    "is plain matte black with nothing else in it."
)

FACE_RULE = (
    "Her face, age, and features do not change from the start of the clip to the end -- "
    "the exact same person throughout."
)

ONSET_RULE = (
    "Ink only appears exactly underneath the moving marker tip, one stroke at a time, "
    "never ahead of the tip, never appearing all at once or partially formed before the "
    "tip draws it."
)

NO_ECHO_RULE = (
    "She never retraces, repeats, or redraws any word or mark already on the board -- "
    "only the new stroke described for this clip is added."
)

SIZE_RULE = (
    "Her handwriting is small and compact, staying on a single horizontal line without "
    "wrapping to a second line."
)

STRAY_MARK_RULE = (
    "There may already be a short faint mark at the marker tip's current position. That "
    "mark is not text and is not something to preserve, continue, or write around -- "
    "whatever is drawn in this clip begins fresh at that position, entirely independent "
    "of that mark."
)

NO_OVERSHOOT_RULE = (
    "The instant the marker tip reaches a stroke's natural endpoint, the marker lifts "
    "immediately -- no extra tick mark, no small correction stroke, no double-back, no "
    "wiggle, no decorative mark of any kind is left behind."
)

NO_ARROWHEAD_RULE = (
    "Every mark is a plain stroke with no arrowhead, no decorative flourish, and no extra "
    "ink beyond its stated shape."
)

PUNCTUATION_RULE = (
    '"$99" is written as a dollar sign followed directly by the two digits "9" and "9" '
    'with no period, space, or extra digit between them. "x.country" is written with a '
    'period between "x" and "country", never a hyphen or dash, and with a lowercase "x".'
)

END_LOOK_RULE = (
    "After this final stroke is completely finished, she lifts the marker, lowers her "
    "hand, and looks toward the camera -- this is the last action of the video. The "
    "finished board -- four lines of text, a rectangle around \"vibe-coded\", a circle "
    "around \"$99\", and an underline below \"x.country\" -- remains visible and completely "
    "unchanged."
)


def carry_hand_rule(target_desc):
    return (
        "After this clip's stroke is completely finished, she does not look at the "
        "camera. Keeping her eyes on the board, she lifts the marker tip slightly off "
        "the glass so it leaves no ink, and moves her hand steadily through the air to "
        f"{target_desc}, her head slowly turning to follow her hand the whole way -- one "
        "continuous, slow motion, not a cut. By the final frame of this clip, her hand "
        "and the marker tip are at rest at that new position, ready for the next stroke, "
        "not still at the position where this clip's stroke ended."
    )


STEPS = {
    1: {
        "kind": "text",
        "text": "I vibe-coded my app",
        "position": "top-left of the board",
        "carry_to": "a blank position directly below this line, at its left edge, ready to begin the next line of text",
    },
    2: {
        "kind": "text",
        "text": "in a weekend. Launched 19.",
        "position": "directly below the first line of text already on the board",
        "carry_to": "a blank position directly below this line, at its left edge, ready to begin the next line of text",
    },
    3: {
        "kind": "text",
        "text": "So this week I pay",
        "position": "directly below the two lines of text already on the board",
        "carry_to": "a blank position directly below this line, at its left edge, ready to begin the next line of text",
    },
    4: {
        "kind": "text",
        "text": "$99 on x.country",
        "position": "directly below the three lines of text already on the board",
        "carry_to": 'the word "vibe-coded" in the first (topmost) line of text, positioning the tip just to the left of and slightly above that word, ready to begin drawing a rectangle around it',
    },
    5: {
        "kind": "rectangle",
        "target": "vibe-coded",
        "carry_to": 'the text "$99" further down the board, positioning the tip just to the left of and slightly above it, ready to begin drawing a circle around it',
    },
    6: {
        "kind": "circle",
        "target": "$99",
        "carry_to": 'a position just below and to the left of the word "x.country" on the same line, ready to begin drawing a straight horizontal line under it',
    },
    7: {
        "kind": "underline",
        "target": "x.country",
        "carry_to": None,
    },
}

STEP_CFG = STEPS[STEP]
END_RULE = END_LOOK_RULE if IS_LAST_STEP else carry_hand_rule(STEP_CFG["carry_to"])

if STEP_CFG["kind"] == "text":
    if STEP == 1:
        PROMPT = (
            f"A realistic, continuous 5-second video of {PRESENTER} The board is completely "
            f"blank at the start. {NO_REFLECTION_RULE} {ONSET_RULE} {SIZE_RULE} "
            f"She looks at the board, raises her hand, and writes exactly this text at the "
            f'{STEP_CFG["position"]}: "{STEP_CFG["text"]}" -- reproduced exactly, character for '
            f"character, with no extra punctuation of any kind added anywhere. {PUNCTUATION_RULE} "
            f"{END_RULE} The camera holds steady the entire time."
        )
        ENDPOINT = "bytedance/seedance-2.0/fast/text-to-video"
    else:
        PROMPT = (
            f"Continuing from this exact frame -- same woman, same outfit, same glass board, "
            f"same room, same camera framing, nothing changes about the scene itself. {FACE_RULE} "
            f"{NO_REFLECTION_RULE} {STRAY_MARK_RULE} {NO_ECHO_RULE} {ONSET_RULE} {SIZE_RULE} "
            f"She writes exactly this new text {STEP_CFG['position']}, in the same handwriting "
            f'style and size as the text already there: "{STEP_CFG["text"]}" -- reproduced '
            f"exactly, character for character, with no extra punctuation of any kind added "
            f"anywhere. This sentence continues across several separate videos, each one "
            f"adding only its own short piece -- this clip's piece is only the words "
            f'"{STEP_CFG["text"]}" and nothing else. Even though the full sentence is not yet '
            f"complete, she does not try to finish it or add any further words, numbers, "
            f"dollar amounts, or symbols in this clip -- the moment she finishes writing the "
            f'last letter of "{STEP_CFG["text"]}", her hand stops writing entirely for the rest '
            f"of this clip; it does not begin a new line, and it does not add anything else "
            f"to the board. {PUNCTUATION_RULE} "
            f"{END_RULE} The camera holds steady the entire time."
        )
        ENDPOINT = "bytedance/seedance-2.0/fast/image-to-video"
else:
    shape_desc = {
        "rectangle": (
            f'draws a closed yellow rectangle around the text "{STEP_CFG["target"]}" only -- '
            f"tightly enclosing just that text, not touching any neighboring word. The "
            f"rectangle is drawn as four straight strokes, one side at a time, each growing "
            f"progressively under the moving tip -- it does not appear all at once."
        ),
        "circle": (
            f'draws a closed yellow oval/circle around the text "{STEP_CFG["target"]}" only -- '
            f"tightly enclosing just that text, not touching any neighboring word. The circle "
            f"is drawn as one continuous curved stroke, growing progressively under the moving "
            f"tip -- it does not appear all at once."
        ),
        "underline": (
            f'draws one straight horizontal yellow line directly underneath the text '
            f'"{STEP_CFG["target"]}" only. The underline starts exactly below the left edge of '
            f'the first character of "{STEP_CFG["target"]}" and ends exactly below the right '
            f'edge of its last character -- its length matches only that word, not any '
            f"neighboring word, and not any empty space. This line grows progressively under "
            f"the moving tip, from its left end to its right end."
        ),
    }[STEP_CFG["kind"]]

    PROMPT = (
        f"Continuing from this exact frame -- same woman, same outfit, same glass board, "
        f"same room, same camera framing, nothing changes about the scene itself. {FACE_RULE} "
        f"{NO_REFLECTION_RULE} {STRAY_MARK_RULE} {ONSET_RULE} "
        f"She {shape_desc} {NO_OVERSHOOT_RULE} {NO_ARROWHEAD_RULE} {END_RULE} "
        f"The camera holds steady the entire time."
    )
    ENDPOINT = "bytedance/seedance-2.0/mini/image-to-video"

SEED = 20001
PAYLOAD = {
    "prompt": PROMPT,
    "duration": "5",
    "aspect_ratio": "16:9",
    "resolution": "720p",
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
    raw_frame = os.path.join(RAW_DIR, f"_chain_start_frame_step{STEP}_raw.png")
    os.system(f'ffmpeg -y -v error -sseof -1 -i "{clip_path}" -frames:v 1 -update 1 "{raw_frame}"')

    denoised_frame = os.path.join(RAW_DIR, f"_chain_start_frame_step{STEP}_denoised.png")
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
    if STEP > 1:
        if not PREV_CLIP:
            raise RuntimeError("step > 1 requires the previous clip path as 2nd arg")
        payload["image_url"] = extract_last_frame_b64(PREV_CLIP)

    name = f"round38_step{STEP}"
    print(f"--- {name} (kind={STEP_CFG['kind']}, endpoint={ENDPOINT}, last_step={IS_LAST_STEP}) ---", flush=True)
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
        "step": STEP,
        "kind": STEP_CFG["kind"],
        "endpoint": ENDPOINT,
        "chained_from": PREV_CLIP,
        "is_last_step": IS_LAST_STEP,
        "payload": {k: v for k, v in payload.items() if k != "image_url"},
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
