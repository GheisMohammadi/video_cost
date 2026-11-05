"""Clean up a chain-anchor frame before it's fed forward as the next row's
start_image_url. Each I2V hop re-encodes its input frame, and light-gray
sensor-like grain compounds hop to hop -- visible as early as row 3-4 in
round 30 and severe by row 5. This isn't ink (the whiteboard-wipe's
dark-pixel inpaint mask doesn't touch it), so it survives the wipe
unchanged and keeps compounding.

Fix: run non-local-means denoising over the whole frame, then a mild
unsharp-mask pass to recover edge crispness lost to denoising, before the
frame is ever re-encoded into the next generation.

Usage: python3 denoise_frame.py <in.png> <out.png>
"""
import sys

import cv2

in_path, out_path = sys.argv[1], sys.argv[2]

img = cv2.imread(in_path)
denoised = cv2.fastNlMeansDenoisingColored(img, None, h=7, hColor=7, templateWindowSize=7, searchWindowSize=21)

blurred = cv2.GaussianBlur(denoised, (0, 0), sigmaX=1.5)
sharpened = cv2.addWeighted(denoised, 1.5, blurred, -0.5, 0)

cv2.imwrite(out_path, sharpened)
print(f"denoised {in_path} -> {out_path}")
