from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import glob

FRAMES = sorted(glob.glob("frames_jpg/*.jpg"))
MASKS = sorted(glob.glob("board_masks/*.png"))
assert len(FRAMES) == len(MASKS) == 81

# Per-pixel median across frames, counting only pixels SAM2 tracked as "board"
# in that frame -- same clean-plate technique as round 10's v2, but using
# SAM2's tracked board mask instead of mediapipe's per-frame subject mask.
frames_arr = np.stack([np.array(Image.open(f).convert("RGB"), dtype=np.float32) for f in FRAMES])
masks_arr = np.stack([np.array(Image.open(m)) > 0 for m in MASKS])

mask4 = masks_arr[..., None]
frames_masked = np.where(mask4, frames_arr, np.nan)
with np.errstate(invalid="ignore"):
    clean_plate = np.nanmedian(frames_masked, axis=0)
sample_count = masks_arr.sum(axis=0)
# A pixel with very few board-classified samples can still have its median
# land directly on one of the original garbled-text pixels (not just zero
# samples -- "not enough samples to outvote the text" is the real failure
# mode, which is why the first attempt, which only treated the zero-sample
# case as unreliable, still showed color blotches). Treat anything under a
# reliability floor the same way: unreliable, to be reconstructed by
# inpainting instead of trusted as a real median.
MIN_RELIABLE_SAMPLES = 10
nan_px = sample_count < MIN_RELIABLE_SAMPLES
plate_u8 = np.nan_to_num(clean_plate, nan=0).clip(0, 255).astype(np.uint8)

# Unreliable pixels -- previously filled from an unmasked all-frame average,
# which pulled in the original garbled text's colors directly. cv2.inpaint
# instead reconstructs those pixels from surrounding *already-clean* plate
# pixels only, so no garbled-text color can leak in.
if nan_px.any():
    import cv2
    inpaint_mask = (nan_px.astype(np.uint8)) * 255
    inpaint_mask = cv2.dilate(inpaint_mask, np.ones((3, 3), np.uint8), iterations=1)
    bgr = cv2.cvtColor(plate_u8, cv2.COLOR_RGB2BGR)
    bgr = cv2.inpaint(bgr, inpaint_mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)
    plate_u8 = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

plate = Image.fromarray(plate_u8)
plate.save("clean_plate_sam2.png")

TEXT_REGION = (0, 0, 832, 480)
blurred_patch = plate.crop(TEXT_REGION).filter(ImageFilter.GaussianBlur(radius=18))
plate_cleaned = plate.copy()
plate_cleaned.paste(blurred_patch, TEXT_REGION)

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
board_with_text.save("clean_plate_sam2_with_text.png")

import os
OUT = "composited_sam2"
os.makedirs(OUT, exist_ok=True)
for i, (fp, mp) in enumerate(zip(FRAMES, MASKS)):
    orig = Image.open(fp).convert("RGB")
    mask_img = Image.open(mp).convert("L")
    composited = Image.composite(board_with_text, orig, mask_img)
    composited.save(f"{OUT}/frame_{i+1:03d}.png")
    if i % 20 == 0:
        print("frame", i, flush=True)
print("ALL_DONE")
