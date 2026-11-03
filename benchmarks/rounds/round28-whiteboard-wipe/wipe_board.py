"""Digitally erase ink from the board region of a chain-anchor frame, so the
next I2V generation can be told "she wipes the board clean" while the image
we actually feed it already shows a blank board -- and, critically, every
pixel outside the board rectangle (the woman, her outfit, her hair, the
room) is left byte-identical, so there is no possibility of the model
reinventing her appearance the way a fresh text-to-video restart does.

The board region has no hand/marker in it at a chain-boundary frame (she is
facing the camera, marker down at her side), so any dark pixel inside the
rectangle is ink, not hand/marker -- a plain brightness threshold is enough,
no temporal/motion logic needed (unlike round 25's clean_plate.py, which had
to solve for ink touching a moving hand mid-stroke).

Usage: python3 wipe_board.py <in_frame.png> <out_frame.png> x0 y0 x1 y1
"""
import sys

import cv2
import numpy as np

in_path, out_path = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7])

img = cv2.imread(in_path)
region = img[y0:y1, x0:x1].copy()
gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

# Inpaint over the ink mask using the surrounding board texture (shadows,
# smudges, reflections) instead of a flat fill -- blends far better than
# copying/stretching a clean patch.
ink_mask = (gray < 180).astype(np.uint8) * 255
ink_mask = cv2.dilate(ink_mask, np.ones((5, 5), np.uint8))

cleaned_region = cv2.inpaint(region, ink_mask, 7, cv2.INPAINT_TELEA)
img[y0:y1, x0:x1] = cleaned_region
cv2.imwrite(out_path, img)
print(f"wiped board region ({x0},{y0})-({x1},{y1}) -> {out_path}")
