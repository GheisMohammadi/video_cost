"""Round 27 post-processing: trim each of the 8 per-row clips down to its
active writing portion, stitch them with a short freeze-frame pause between
rows (varied per transition, same approach as round 23), then burn in the
mid-screen caption overlay (reusing round 22's rendered caption PNGs, since
the script and row split are identical).
"""
import os
import subprocess

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIPS_DIR = os.path.join(OUT_DIR, "clips")
RAW_DIR = os.path.join(OUT_DIR, "raw")
CAPTIONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(OUT_DIR)),
    "rounds", "round22-woman-vertical-tiktok", "raw", "captions",
)

FPS = 30

# Same calibration round 23 used (identical row text, identical 5s/720p
# generation target) -- writing completes by frame ~128 in every row, start
# trim skips the opening look-at-camera/blink beat (~0.7s). Row 1 keeps its
# original start (video's opening beat), row 8 keeps its original end
# (video's closing beat). Row 5 (fresh segment start) also keeps its
# opening beat trimmed like every other middle row -- it is not the video's
# intro.
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

PAUSES = [0.20, 0.35, 0.25, 0.40, 0.30, 0.45, 0.20]

# Caption timing: one caption per original sentence (2 rows each), shown
# while those two rows are on screen. Row/pause durations after trim:
ROW_DUR = {r: (end - start) / FPS for r, (start, end) in TRIM.items()}


def run(cmd):
    subprocess.run(cmd, check=True)


def trim_clip(row, start_f, end_f, out_path):
    start_t = start_f / FPS
    dur_t = (end_f - start_f) / FPS
    run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{start_t:.4f}", "-i", os.path.join(CLIPS_DIR, f"wan30_round27_row{row}.mp4"),
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

    stitched = os.path.join(CLIPS_DIR, "round27_stitched.mp4")
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", list_file,
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        stitched,
    ])
    print("stitched ->", stitched)

    # Caption overlay timing: segment boundaries in the stitched timeline.
    # Segment i covers rows (2i+1, 2i+2) plus the pause after the first of
    # the pair and the pause after the second (except after row 8).
    t = 0.0
    segments = []  # (caption_index, start_t, end_t)
    for seg in range(4):
        row_a, row_b = 2 * seg + 1, 2 * seg + 2
        start_t = t
        t += ROW_DUR[row_a]
        t += PAUSES[row_a - 1]
        t += ROW_DUR[row_b]
        end_t = t
        if row_b < 8:
            t += PAUSES[row_b - 1]
        segments.append((seg, start_t, end_t))
        print(f"caption {seg}: {start_t:.2f}s - {end_t:.2f}s")

    filter_parts = []
    inputs = ["-i", stitched]
    for seg_idx, _, _ in segments:
        inputs += ["-i", os.path.join(CAPTIONS_DIR, f"cap{seg_idx}.png")]

    chain = "[0:v]"
    for i, (seg_idx, start_t, end_t) in enumerate(segments):
        out_label = f"v{i+1}"
        filter_parts.append(
            f"{chain}[{i+1}:v]overlay=0:0:enable='between(t,{start_t:.3f},{end_t:.3f})'[{out_label}]"
        )
        chain = f"[{out_label}]"

    filter_complex = ";".join(filter_parts)
    final_out = os.path.join(CLIPS_DIR, "round27_final_captioned.mp4")
    run([
        "ffmpeg", "-y", "-v", "error",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", chain, "-map", "0:a?",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        final_out,
    ])
    print("captioned ->", final_out)

    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", final_out],
        capture_output=True, text=True,
    ).stdout.strip()
    print("total final duration:", dur, "s")


if __name__ == "__main__":
    main()
