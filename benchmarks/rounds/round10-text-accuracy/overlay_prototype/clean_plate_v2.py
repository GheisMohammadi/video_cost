from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import glob

plate = Image.open("clean_plate.png").convert("RGB")

# The clean plate correctly recovers the board's real lighting/texture (median-across-frames removes
# the moving person), but the garbled AI-generated text is static in every frame, so the median
# reconstructs it perfectly too. A strong blur over just the text region erases the sharp letter edges
# (what makes text readable as text) while keeping the smooth lighting gradient underneath -- unlike the
# v1 prototype's flat fill, this still looks like the same lit whiteboard, just blank.
TEXT_REGION = (0, 0, 832, 480)  # left, top, right, bottom -- the whole frame; the person-mask protects the subject during compositing regardless
blurred_patch = plate.crop(TEXT_REGION).filter(ImageFilter.GaussianBlur(radius=18))
plate_cleaned = plate.copy()
plate_cleaned.paste(blurred_patch, TEXT_REGION)
plate_cleaned.save("clean_plate_blurred.png")

LINES = [
    "U.S. advertisers are pursuing",
    "claims against Google.",
    "",
    "Refunds for 20-30% of Ad Spend",
    "since 2016.",
    "",
    "Federal courts ruled Google",
    "illegally monopolized search",
    "advertising.",
    "",
    "The Google Advertiser Claims,",
    "explained.",
    "",
    "DOWNLOAD EXPLAINER",
    "File Ad Refunds -- ADREFUNDS.COM",
]
FONT_PATH = "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"
font = ImageFont.truetype(FONT_PATH, 30)
board_with_text = plate_cleaned.copy()
d = ImageDraw.Draw(board_with_text)
y = 40
for line in LINES:
    if line:
        d.text((40, y), line, font=font, fill=(20, 20, 60))
    y += 34
board_with_text.save("clean_plate_blurred_with_text.png")

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import os

base_options = mp_python.BaseOptions(model_asset_path="/tmp/selfie_segmenter.tflite")
options = vision.ImageSegmenterOptions(base_options=base_options, output_category_mask=True)
segmenter = vision.ImageSegmenter.create_from_options(options)

OUT = "composited_v2"
os.makedirs(OUT, exist_ok=True)
FRAMES = sorted(glob.glob("frames/frame_*.png"))
for i, fp in enumerate(FRAMES):
    img = mp.Image.create_from_file(fp)
    result = segmenter.segment(img)
    mask = result.category_mask.numpy_view().squeeze()
    mask_img = Image.fromarray(mask).convert("L")
    orig = Image.open(fp).convert("RGB")
    composited = Image.composite(board_with_text, orig, mask_img)
    composited.save(f"{OUT}/frame_{i+1:03d}.png")
    if i % 20 == 0:
        print("frame", i, flush=True)
print("ALL_DONE")
