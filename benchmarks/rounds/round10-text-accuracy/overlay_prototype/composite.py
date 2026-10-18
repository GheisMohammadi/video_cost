import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import glob, os

FRAMES = sorted(glob.glob("frames/frame_*.png"))
OUT = "composited"
os.makedirs(OUT, exist_ok=True)

base_options = mp_python.BaseOptions(model_asset_path="/tmp/selfie_segmenter.tflite")
options = vision.ImageSegmenterOptions(base_options=base_options, output_category_mask=True)
segmenter = vision.ImageSegmenter.create_from_options(options)

# The real script, exactly as the customer prompt specified -- this is what should appear
# on the board, instead of whatever the model generated.
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

BOARD_FILL = (178, 179, 178)  # sampled from a clean area of the board in frame 1
FONT_PATH = "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"
font = ImageFont.truetype(FONT_PATH, 30)

def render_board(size):
    board = Image.new("RGB", size, BOARD_FILL)
    d = ImageDraw.Draw(board)
    y = 40
    for line in LINES:
        if line:
            d.text((40, y), line, font=font, fill=(20, 20, 60))
        y += 34
    return board

for i, fp in enumerate(FRAMES):
    img = mp.Image.create_from_file(fp)
    result = segmenter.segment(img)
    mask = result.category_mask.numpy_view().squeeze()  # 0 = person, 255 = background/board
    orig = Image.open(fp).convert("RGB")
    board = render_board(orig.size)
    mask_img = Image.fromarray(mask).convert("L")
    # PIL composite(image1, image2, mask): image1 where mask==255, image2 where mask==0.
    # Raw mask is 0=person, 255=board, so image1=board, image2=orig gives: board area -> board
    # (with real text), person area -> original pixels (keeps the subject in front).
    composited = Image.composite(board, orig, mask_img)
    composited.save(f"{OUT}/frame_{i+1:03d}.png")
    if i % 20 == 0:
        print("frame", i, "done", flush=True)

print("ALL_DONE")
