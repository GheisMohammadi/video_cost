"""Round 23 post-processing: trim each of the 8 per-row clips down to its
active writing portion, stitch them with a short freeze-frame pause between
rows (pause length deliberately varied per transition, not a fixed value --
round 22's "fixed ~1s gap" was an uncontrolled artifact of the generation,
not something we actually set; here the pause is something we choose), then
burn in the mid-screen caption overlay.
"""
import json
import os
import subprocess

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIPS_DIR = os.path.join(OUT_DIR, "clips")
RAW_DIR = os.path.join(OUT_DIR, "raw")

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

# Trim window per row (frames @ 30fps out of each 150-frame / 5s clip),
# found by inspecting raw/calib_row{N}_*.png: writing is complete by frame
# ~120-128 in every row tested; start trim skips the opening
# look-at-camera/blink beat (~0.7s). Row 1 keeps its original start (the
# video's opening camera beat) and row 8 keeps its original end (the
# video's closing camera beat).
TRIM = {
    1: (0, 128),
    2: (22, 128),
    3: (22, 128),
    4: (22, 128),
    5: (22, 128),
    6: (22, 128),
    7: (22, 128),
    8: (22, 150),
}

# Deliberately varied pause (seconds) between each pair of consecutive rows
# (7 gaps for 8 rows) -- not a single fixed value.
PAUSES = [0.20, 0.35, 0.25, 0.40, 0.30, 0.45, 0.20]

FPS = 30


def run(cmd):
    subprocess.run(cmd, check=True)


def trim_clip(row, start_f, end_f, out_path):
    start_t = start_f / FPS
    dur_t = (end_f - start_f) / FPS
    run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{start_t:.4f}", "-i", os.path.join(CLIPS_DIR, f"wan30_round23_row{row}.mp4"),
        "-t", f"{dur_t:.4f}",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        out_path,
    ])


def freeze_pause(source_clip, duration_s, out_path):
    run([
        "ffmpeg", "-y", "-v", "error",
        "-sseof", "-0.07", "-i", source_clip,
        "-vframes", "1", os.path.join(RAW_DIR, "_pause_frame.png"),
    ])
    run([
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-t", f"{duration_s:.4f}",
        "-i", os.path.join(RAW_DIR, "_pause_frame.png"),
        "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264", "-crf", "18",
        out_path,
    ])


def main():
    os.makedirs(CLIPS_DIR, exist_ok=True)
    trimmed = []
    for row in range(1, 9):
        start_f, end_f = TRIM[row]
        out_path = os.path.join(CLIPS_DIR, f"trim_row{row}.mp4")
        trim_clip(row, start_f, end_f, out_path)
        trimmed.append(out_path)
        print(f"trimmed row{row}: frames {start_f}-{end_f} ({(end_f-start_f)/FPS:.2f}s) -> {out_path}")

    concat_list = []
    for i, clip in enumerate(trimmed):
        concat_list.append(clip)
        if i < len(trimmed) - 1:
            pause_path = os.path.join(CLIPS_DIR, f"pause_{i+1}.mp4")
            freeze_pause(clip, PAUSES[i], pause_path)
            concat_list.append(pause_path)
            print(f"pause after row{i+1}: {PAUSES[i]}s -> {pause_path}")

    list_file = os.path.join(RAW_DIR, "concat_list_rows.txt")
    with open(list_file, "w") as f:
        for c in concat_list:
            f.write(f"file '{c}'\n")

    stitched = os.path.join(CLIPS_DIR, "round23_stitched.mp4")
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", list_file,
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        stitched,
    ])
    print("stitched ->", stitched)

    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", stitched],
        capture_output=True, text=True,
    ).stdout.strip()
    print("total stitched duration:", dur, "s")


if __name__ == "__main__":
    main()
