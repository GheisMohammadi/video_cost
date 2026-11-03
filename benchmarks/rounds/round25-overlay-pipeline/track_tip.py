"""Prototype: track the marker tip's pixel position frame by frame.

Reads already-extracted frames and, within a board-region crop, finds a
dark blob that also differs from a per-pixel background median (so static
dark fixtures like the easel's mounting bracket don't get picked up as the
tip -- only things that move, and are dark, qualify). Feasibility test
only -- no video generation involved, no cost.

Usage: python3 track_tip.py <frames_dir> <out_csv> [x0 y0 x1 y1]
"""
import csv
import glob
import os
import sys

import cv2
import numpy as np

frames_dir = sys.argv[1]
out_csv = sys.argv[2]
region = tuple(int(v) for v in sys.argv[3:7]) if len(sys.argv) >= 7 else None

paths = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
imgs = [cv2.imread(p) for p in paths]
h, w = imgs[0].shape[:2]
x0, y0, x1, y1 = region if region else (0, 0, w, h)

crops = [img[y0:y1, x0:x1] for img in imgs]
grays = [cv2.cvtColor(c, cv2.COLOR_BGR2GRAY) for c in crops]
stack = np.stack(grays, axis=0)
bg = np.median(stack, axis=0).astype(np.uint8)

rows = []
for p, gray in zip(paths, grays):
    diff = cv2.absdiff(gray, bg)
    motion_mask = diff > 18
    dark_mask = gray < 70
    mask = (motion_mask & dark_mask).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    found = None
    candidates = [c for c in contours if 15 < cv2.contourArea(c) < 5000]
    if candidates:
        c = max(candidates, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"]) + x0
            cy = int(M["m01"] / M["m00"]) + y0
            found = (cx, cy, int(cv2.contourArea(c)))
    rows.append((os.path.basename(p), found[0] if found else "", found[1] if found else "", found[2] if found else ""))

with open(out_csv, "w", newline="") as f:
    w_ = csv.writer(f)
    w_.writerow(["frame", "x", "y", "area"])
    w_.writerows(rows)

print(f"wrote {len(rows)} rows to {out_csv}")
