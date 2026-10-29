#!/bin/bash
# Round 22 post-generation pass: stitch segments A+B into ~30s, then burn
# mid-screen captions on top. Captions are a separate overlay from the
# whiteboard-writing text -- they repeat the spoken script line by line,
# centered vertically in the frame, TikTok caption style.
set -euo pipefail
cd "$(dirname "$0")"

SEG_A=clips/wan30_round22_segA.mp4
SEG_B=clips/wan30_round22_segB.mp4
STITCHED=clips/round22_stitched_30s.mp4
FINAL=clips/round22_final_captioned.mp4

# 1. Concatenate the two segments (same codec/resolution/fps, safe to concat directly).
cat > raw/concat_list.txt <<EOF
file '$(pwd)/$SEG_A'
file '$(pwd)/$SEG_B'
EOF
ffmpeg -y -v error -f concat -safe 0 -i raw/concat_list.txt -c copy "$STITCHED"

# 2. Burn mid-screen captions, one per script line, as pre-rendered transparent
# PNG overlays (this ffmpeg build has no drawtext/libfreetype), timed to roughly
# when each line is spoken/written (4 lines over ~30s -> ~7.5s each).
ffmpeg -y -v error -i "$STITCHED" \
  -i raw/captions/cap0.png -i raw/captions/cap1.png \
  -i raw/captions/cap2.png -i raw/captions/cap3.png \
  -filter_complex "
  [0:v][1:v] overlay=0:0:enable='between(t,0,7)' [v1];
  [v1][2:v] overlay=0:0:enable='between(t,7,15)' [v2];
  [v2][3:v] overlay=0:0:enable='between(t,15,22)' [v3];
  [v3][4:v] overlay=0:0:enable='between(t,22,30)' [v4]
  " -map "[v4]" -map 0:a? -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy "$FINAL"

echo "stitched -> $STITCHED"
echo "final captioned -> $FINAL"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration,r_frame_rate -of default=noprint_wrappers=1 "$FINAL"
