import os, sys, time
import numpy as np
import torch
from PIL import Image

from sam2.build_sam import build_sam2_video_predictor

CKPT = "/tmp/round10_sam2/checkpoints/sam2.1_hiera_small.pt"
CFG = "configs/sam2.1/sam2.1_hiera_s.yaml"
FRAMES_DIR = "/tmp/round10_sam2/frames_jpg"
OUT_DIR = "/tmp/round10_sam2/board_masks"
os.makedirs(OUT_DIR, exist_ok=True)

device = "mps" if torch.backends.mps.is_available() else "cpu"
print("device:", device, flush=True)

predictor = build_sam2_video_predictor(CFG, CKPT, device=device)

t0 = time.time()
state = predictor.init_state(video_path=FRAMES_DIR)
print("init_state done", time.time() - t0, "s", flush=True)

# One point prompt on the board in frame 0 (whiteboard fills most of the
# background in this shot -- same assumption round 10's mediapipe prototype
# made, but here SAM2 tracks the board as its own object across all frames
# instead of re-segmenting the subject independently each frame).
ann_frame_idx = 0
ann_obj_id = 1
points = np.array([[520, 200]], dtype=np.float32)  # board area, right of the subject
labels = np.array([1], dtype=np.int32)

_, out_obj_ids, out_mask_logits = predictor.add_new_points_or_box(
    inference_state=state,
    frame_idx=ann_frame_idx,
    obj_id=ann_obj_id,
    points=points,
    labels=labels,
)

t1 = time.time()
n = 0
for frame_idx, obj_ids, mask_logits in predictor.propagate_in_video(state):
    mask = (mask_logits[0] > 0.0).cpu().numpy().squeeze().astype(np.uint8) * 255
    Image.fromarray(mask).save(f"{OUT_DIR}/mask_{frame_idx+1:03d}.png")
    n += 1
    if frame_idx % 20 == 0:
        print("frame", frame_idx, flush=True)

print("ALL_DONE", n, "frames in", time.time() - t1, "s", flush=True)
