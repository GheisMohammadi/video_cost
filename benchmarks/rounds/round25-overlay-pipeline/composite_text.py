"""Composite a deterministically-rendered sentence onto cleaned (ink-free)
presenter frames, revealed left-to-right over a known writing time window.

Since the frames are already ink-free (clean_plate.py), any remaining
dark/skin pixel in a given frame is legitimately the real hand/marker --
text is only painted where that's NOT true, so the real hand always stays
visually in front without needing per-frame hand tracking.

Usage:
  python3 composite_text.py <cleaned_frames_dir> <out_dir> "<text>" \
      <start_frame_idx> <end_frame_idx> <text_x> <text_y> <font_size> <font_path>
"""
import glob
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

cleaned_dir = sys.argv[1]
out_dir = sys.argv[2]
text = sys.argv[3]
start_frame = int(sys.argv[4])
end_frame = int(sys.argv[5])
text_x = int(sys.argv[6])
text_y = int(sys.argv[7])
font_size = int(sys.argv[8])
font_path = sys.argv[9]
os.makedirs(out_dir, exist_ok=True)

paths = sorted(glob.glob(os.path.join(cleaned_dir, "*.png")))
sample = cv2.imread(paths[0])
H, W = sample.shape[:2]

font = ImageFont.truetype(font_path, font_size)
tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(tmp)
bbox = d.textbbox((text_x, text_y), text, font=font)
text_w = bbox[2] - bbox[0]
text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d2 = ImageDraw.Draw(text_layer)
d2.text((text_x, text_y), text, font=font, fill=(20, 20, 20, 255))
text_np = np.array(text_layer)  # RGBA


def skin_mask(bgr):
    b, g, r = cv2.split(bgr.astype(np.int16))
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    mask = (r > 95) & (g > 40) & (b > 20) & (r > g) & (r > b) & ((mx - mn) > 15)
    return mask


for i, p in enumerate(paths, start=1):
    img = cv2.imread(p)
    frac = max(0.0, min(1.0, (i - start_frame) / max(1, (end_frame - start_frame))))
    reveal_right_edge = bbox[0] + text_w * frac

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dark = gray < 150
    skin = skin_mask(img)
    foreground = dark | skin

    alpha = text_np[:, :, 3].astype(np.float32) / 255.0
    xs = np.arange(W)[None, :]
    reveal_col_mask = (xs < reveal_right_edge).astype(np.float32)
    alpha = alpha * reveal_col_mask
    alpha[foreground] = 0.0  # never paint over the real hand/marker

    out = img.astype(np.float32)
    text_bgr = text_np[:, :, [2, 1, 0]].astype(np.float32)
    for c in range(3):
        out[:, :, c] = out[:, :, c] * (1 - alpha) + text_bgr[:, :, c] * alpha
    cv2.imwrite(os.path.join(out_dir, os.path.basename(p)), out.astype(np.uint8))

print(f"composited {len(paths)} frames -> {out_dir}")
