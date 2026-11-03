"""Erase any model-drawn ink within a designated text region, regardless of
whether the generation prompt was obeyed. Within the region, a dark pixel
is kept only if it's part of a connected blob touching skin-tone pixels
(the hand/marker); anything else dark (stray ink) is replaced with a clean
background plate taken from frame 0 (before the hand ever enters frame).

Stray ink and the real hand/marker are often spatially touching (the model
draws where it thinks the tip is), so geometry alone can't separate them.
But they differ temporally: ink, once drawn, stays dark in every later
frame; the hand is transient and moves away. A late reference frame (after
she's turned back to camera, hand clear of the board) tells us which dark
pixels are persistent ink -- erase exactly those, in every frame, leaving
real-time hand/marker darkness untouched.

Usage: python3 clean_plate.py <frames_dir> <out_dir> <late_ref_frame> x0 y0 x1 y1
  late_ref_frame: filename (within frames_dir) of a frame where the board
  is static and the hand is clear of it, e.g. the clip's last frame.
"""
import glob
import os
import sys

import cv2
import numpy as np

frames_dir = sys.argv[1]
out_dir = sys.argv[2]
late_ref_name = sys.argv[3]
x0, y0, x1, y1 = (int(v) for v in sys.argv[4:8])
os.makedirs(out_dir, exist_ok=True)

paths = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
plate = cv2.imread(paths[0])
late_ref = cv2.imread(os.path.join(frames_dir, late_ref_name))

plate_region = plate[y0:y1, x0:x1]
late_region = late_ref[y0:y1, x0:x1]
late_gray = cv2.cvtColor(late_region, cv2.COLOR_BGR2GRAY)
ink_mask = (late_gray < 150).astype(np.uint8) * 255
# Only dilate components that are small (ink strokes are thin), so large
# bright-ish shadow regions in the reference frame don't get inflated too.
n, labels, stats, _ = cv2.connectedComponentsWithStats(ink_mask)
small_only = np.zeros_like(ink_mask)
for lbl in range(1, n):
    if stats[lbl, cv2.CC_STAT_AREA] < 2000:
        small_only[labels == lbl] = 255
ink_mask = cv2.dilate(small_only, np.ones((3, 3), np.uint8))

for p in paths:
    img = cv2.imread(p)
    region = img[y0:y1, x0:x1]
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    dark_here = (gray < 150).astype(np.uint8) * 255
    erase = cv2.bitwise_and(dark_here, ink_mask)
    erase3 = cv2.cvtColor(erase, cv2.COLOR_GRAY2BGR) > 0
    cleaned_region = np.where(erase3, plate_region, region)
    out = img.copy()
    out[y0:y1, x0:x1] = cleaned_region
    cv2.imwrite(os.path.join(out_dir, os.path.basename(p)), out)

print(f"cleaned {len(paths)} frames -> {out_dir}")
