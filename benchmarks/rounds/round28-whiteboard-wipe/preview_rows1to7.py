"""Quick preview stitch of rows 1-7 (the clean portion of round 28) for
review before deciding how to fix row 8's board-overflow defect. Rows 1-4
are reused unchanged from round 27 (not regenerated this round); rows 5-7
are round 28's whiteboard-wipe-handoff clips. No captions -- this is a
sync/continuity preview, not a finished deliverable.
"""
import os
import subprocess

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIPS_DIR = os.path.join(OUT_DIR, "clips")
RAW_DIR = os.path.join(OUT_DIR, "raw")
R27_CLIPS = os.path.join(os.path.dirname(OUT_DIR), "round27-i2v-chain-v2", "clips")

FPS = 30
TRIM = {
    1: (0, 128),
    2: (22, 128),
    3: (22, 128),
    4: (22, 128),
    5: (22, 128),
    6: (22, 128),
    7: (22, 128),
}
PAUSES = [0.20, 0.35, 0.25, 0.40, 0.30, 0.45]

SOURCES = {
    1: os.path.join(R27_CLIPS, "wan30_round27_row1.mp4"),
    2: os.path.join(R27_CLIPS, "wan30_round27_row2.mp4"),
    3: os.path.join(R27_CLIPS, "wan30_round27_row3.mp4"),
    4: os.path.join(R27_CLIPS, "wan30_round27_row4.mp4"),
    5: os.path.join(CLIPS_DIR, "wan30_round28_row5.mp4"),
    6: os.path.join(CLIPS_DIR, "wan30_round28_row6.mp4"),
    7: os.path.join(CLIPS_DIR, "wan30_round28_row7.mp4"),
}


def run(cmd):
    subprocess.run(cmd, check=True)


def trim_clip(row, start_f, end_f, out_path):
    start_t = start_f / FPS
    dur_t = (end_f - start_f) / FPS
    run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{start_t:.4f}", "-i", SOURCES[row],
        "-t", f"{dur_t:.4f}",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        out_path,
    ])


def freeze_pause(source_clip, duration_s, out_path):
    run([
        "ffmpeg", "-y", "-v", "error",
        "-sseof", "-0.07", "-i", source_clip,
        "-vframes", "1", os.path.join(RAW_DIR, "_preview_pause_frame.png"),
    ])
    run([
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-t", f"{duration_s:.4f}",
        "-i", os.path.join(RAW_DIR, "_preview_pause_frame.png"),
        "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264", "-crf", "18",
        out_path,
    ])


def main():
    trimmed = []
    for row in range(1, 8):
        start_f, end_f = TRIM[row]
        out_path = os.path.join(CLIPS_DIR, f"preview_trim_row{row}.mp4")
        trim_clip(row, start_f, end_f, out_path)
        trimmed.append(out_path)
        print(f"trimmed row{row}")

    concat_list = []
    for i, clip in enumerate(trimmed):
        concat_list.append(clip)
        if i < len(trimmed) - 1:
            pause_path = os.path.join(CLIPS_DIR, f"preview_pause_{i+1}.mp4")
            freeze_pause(clip, PAUSES[i], pause_path)
            concat_list.append(pause_path)

    list_file = os.path.join(RAW_DIR, "preview_concat_list.txt")
    with open(list_file, "w") as f:
        for c in concat_list:
            f.write(f"file '{c}'\n")

    out = os.path.join(CLIPS_DIR, "round28_preview_rows1to7.mp4")
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", list_file,
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        out,
    ])
    print("preview ->", out)


if __name__ == "__main__":
    main()
