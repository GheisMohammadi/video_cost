"""Round 5 session (runs on the pod): how much does fal's default frame-interpolation
post-processing step actually cost, on top of the generation cost already measured?

Rounds 1-3's cost figures are all an explicit lower bound versus fal's price, because fal's
default request includes a FILM interpolation pass after generation (see
benchmarks/fal_wan22_config.md: interpolator_model=film, num_interpolated_frames=1,
adjust_fps_for_interpolation=true) that this project never implemented. This measures that
missing step directly, using a real PyTorch port of the FILM model (Apache-2.0, matches fal's
documented default algorithm, not a substitute), rather than continuing to note the gap without
a number.

This does NOT need a fresh Wan generation: it takes already-generated clips as input (round 1's
existing 480p A1-A4 clips, and round 6's 720p A1-A4 clips once those exist) and measures only the
interpolation step's own cost, added on top of each clip's already-published generation cost.

Interpolation math, matching fal's stated defaults: for N input frames, one interpolated frame is
inserted at the midpoint (dt=0.5) of every consecutive pair, giving 2N-1 total frames. Output fps
is scaled by the same factor ((2N-1)/N) to hold the clip's duration constant (fal's
"adjust_fps_for_interpolation"), rather than making the clip longer.

Procedure:
  1. Preflight: CUDA available, weights/model cache not on a network filesystem (reusing the same
     checks as every other round's session runner).
  2. Download the FILM model (film_net_fp16.pt, Apache-2.0) if not already cached.
  3. Smoke test: interpolate a 6-frame slice of the first input clip only. This is the first time
     this pipeline has run this model at all; this checks the input/output tensor format assumption
     (normalized 0-1 float, NCHW, matching the model's documented convention) produces a sane,
     non-garbage frame before spending time on full clips. If it fails or the check below fails,
     nothing further runs and this is reported as a finding, not silently worked around.
  4. Full run: interpolate every input clip in full, recording wall time and peak VRAM per clip.

Every output passes the automated gate used throughout this project (right frame count for 2N-1,
not black, not frozen) plus a check specific to this round: an interpolated (odd-indexed) frame
must lie between its two neighbors in pixel value, not equal to either and not wildly different
from both, since a broken interpolation would produce either a flat copy of one neighbor or noise
unrelated to both, and either failure mode must not be silently counted as a valid output.

Usage: python3 interpolate_session.py INPUTS.json [--out /root/out/session] [--gpu-usd-h 1.6] [--disk-usd-h 0.028]
INPUTS.json: {"clips": [{"name": "...", "path": "/root/inputs/x.mp4", "fps": 16, "frames": 81}, ...]}
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

MODEL_URL = "https://github.com/dajes/frame-interpolation-pytorch/releases/download/v1.0.2/film_net_fp16.pt"
MODEL_PATH = "/root/film_net_fp16.pt"

ap = argparse.ArgumentParser()
ap.add_argument("inputs")
ap.add_argument("--out", default="/root/out/session")
ap.add_argument("--gpu-usd-h", type=float, default=1.6)
ap.add_argument("--disk-usd-h", type=float, default=0.028)
args = ap.parse_args()
OUT = args.out
os.makedirs(OUT, exist_ok=True)
T0 = time.time()
DONE = os.path.join(os.path.dirname(OUT.rstrip("/")), "SESSION_DONE")


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def log(*a):
    print(*a, flush=True)


def write(name, obj):
    json.dump(obj, open(os.path.join(OUT, name), "w"), indent=1)


import torch
from PIL import Image

pre = {
    "utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
    "gpu": sh("nvidia-smi --query-gpu=name,driver_version,uuid,memory.total,power.limit --format=csv,noheader"),
    "torch": torch.__version__,
    "fails": [],
}
if not torch.cuda.is_available():
    pre["fails"].append("torch.cuda.is_available() is False")
model_dir = os.path.dirname(MODEL_PATH)
fstype = sh(f"df --output=fstype {model_dir or '/root'} | tail -1")
if "fuse" in fstype or "nfs" in fstype:
    pre["fails"].append(f"model cache directory is on a network filesystem ({fstype})")
write("preflight.json", pre)
if pre["fails"]:
    log("PREFLIGHT_FAIL", pre["fails"])
    open(DONE, "w").write("preflight failed\n")
    sys.exit(2)
log("PREFLIGHT_OK", json.dumps(pre))

if not os.path.exists(MODEL_PATH):
    t = time.time()
    r = subprocess.run(["curl", "-sL", "-o", MODEL_PATH, MODEL_URL])
    if r.returncode != 0 or os.path.getsize(MODEL_PATH) < 1e6:
        log("MODEL_DOWNLOAD_FAILED")
        open(DONE, "w").write("model download failed\n")
        sys.exit(3)
    log("model downloaded", round(time.time() - t, 1), "s,", round(os.path.getsize(MODEL_PATH) / 1e6, 1), "MB")

device = "cuda"
model = torch.jit.load(MODEL_PATH, map_location=device)
model.eval()


def load_frame_tensor(path):
    img = np.array(Image.open(path).convert("RGB")).astype(np.float32) / 255.0
    return torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(device)


def tensor_to_frame(t):
    arr = t.squeeze(0).permute(1, 2, 0).clamp(0, 1).mul(255).byte().cpu().numpy()
    return arr


def decode_clip(path, tmpdir):
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), f"{tmpdir}/f%04d.png"], check=True)
    return sorted(Path(tmpdir).glob("f*.png"))


def interpolate_clip(path, n_frames_expected, fps_in, out_path, limit_frames=None):
    with tempfile.TemporaryDirectory() as td:
        frame_paths = decode_clip(path, td)
        if limit_frames:
            frame_paths = frame_paths[:limit_frames]
        n = len(frame_paths)
        with tempfile.TemporaryDirectory() as outdir:
            written = []
            with torch.no_grad():
                for i in range(n - 1):
                    a, b = load_frame_tensor(frame_paths[i]), load_frame_tensor(frame_paths[i + 1])
                    Image.fromarray(tensor_to_frame(a)).save(f"{outdir}/{2*i:05d}.png")
                    written.append(f"{outdir}/{2*i:05d}.png")
                    mid = model(a, b, torch.tensor([0.5], device=device))
                    if isinstance(mid, (list, tuple)):
                        mid = mid[0]
                    Image.fromarray(tensor_to_frame(mid)).save(f"{outdir}/{2*i+1:05d}.png")
                    written.append(f"{outdir}/{2*i+1:05d}.png")
                last = load_frame_tensor(frame_paths[n - 1])
                Image.fromarray(tensor_to_frame(last)).save(f"{outdir}/{2*(n-1):05d}.png")
                written.append(f"{outdir}/{2*(n-1):05d}.png")
            out_frames_n = len(written)
            fps_out = fps_in * out_frames_n / n_frames_expected if n_frames_expected else fps_in * out_frames_n / n
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps_out), "-i", f"{outdir}/%05d.png",
                            "-pix_fmt", "yuv420p", str(out_path)], check=True)
            return out_frames_n, fps_out, [np.array(Image.open(p).convert("RGB")) for p in written]


def gate(frames, expect_n):
    n = len(frames)
    idx = np.linspace(0, n - 1, 9).astype(int)
    means = [float(frames[i].mean()) for i in idx]
    diff = float(np.abs(frames[-1].astype(np.float32) - frames[0].astype(np.float32)).mean())
    # interpolation-specific check: an interpolated (odd-index) frame should sit strictly between
    # its two original (even-index) neighbors in pixel value, not equal to either.
    interp_ok = True
    for i in range(1, n - 1, 2):
        lo, hi = frames[i - 1].astype(np.float32), frames[i + 1].astype(np.float32)
        mid = frames[i].astype(np.float32)
        lo_m, hi_m, mid_m = lo.mean(), hi.mean(), mid.mean()
        between = min(lo_m, hi_m) - 2 <= mid_m <= max(lo_m, hi_m) + 2
        not_dup = abs(mid_m - lo_m) > 0.05 and abs(mid_m - hi_m) > 0.05
        if not (between and not_dup):
            interp_ok = False
            break
    checks = {"frames_ok": n == expect_n, "not_black": min(means) > 5, "not_frozen": diff > 2.0, "interpolated_frames_plausible": interp_ok}
    return {"pass": all(checks.values()), "n_frames": n, **checks}


clips = json.load(open(args.inputs))["clips"]

# ---- smoke test: first 6 frames of the first clip only ----
c0 = clips[0]
t = time.time()
try:
    n_out, fps_out, frames = interpolate_clip(c0["path"], 6, c0["fps"], "/root/out/smoke.mp4", limit_frames=6)
    smoke_gate = gate(frames, 2 * 6 - 1)
    smoke = {"ok": True, "wall_s": round(time.time() - t, 1), "n_out": n_out, "fps_out": round(fps_out, 2), "gate": smoke_gate}
except Exception as e:
    smoke = {"ok": False, "error": repr(e)[:400], "wall_s": round(time.time() - t, 1)}
write("smoke.json", smoke)
log("SMOKE", json.dumps(smoke))
if not smoke.get("ok") or not smoke.get("gate", {}).get("pass"):
    log("SMOKE_FAILED, stopping before spending time on full clips")
    open(DONE, "w").write("smoke test failed\n")
    sys.exit(4)

# ---- full clips ----
records = []
for c in clips:
    torch.cuda.reset_peak_memory_stats()
    t = time.time()
    out_path = os.path.join(OUT, f"{c['name']}_interpolated.mp4")
    try:
        n_out, fps_out, frames = interpolate_clip(c["path"], c["frames"], c["fps"], out_path)
        wall_s = round(time.time() - t, 1)
        g = gate(frames, 2 * c["frames"] - 1)
        ok = True
    except Exception as e:
        wall_s = round(time.time() - t, 1)
        g, ok = {"pass": False, "error": repr(e)[:400]}, False
    cost = wall_s * (args.gpu_usd_h + args.disk_usd_h) / 3600
    rec = {"name": c["name"], "input_frames": c["frames"], "input_fps": c["fps"],
           "output_frames": n_out if ok else None, "output_fps": round(fps_out, 2) if ok else None,
           "interpolation_wall_s": wall_s, "interpolation_cost_usd": round(cost, 4),
           "peak_vram_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2), "ok": ok,
           "delivered": ok and g.get("pass"), "gate": g}
    records.append(rec)
    with open(os.path.join(OUT, "jobs.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    log("CLIP", json.dumps({k: rec[k] for k in ("name", "ok", "delivered", "interpolation_wall_s", "interpolation_cost_usd")}))

write("session.json", {"model": "FILM (dajes/frame-interpolation-pytorch, film_net_fp16.pt)",
                       "gpu": pre["gpu"], "session_s": round(time.time() - T0, 1),
                       "price_snapshot": {"gpu_usd_h": args.gpu_usd_h, "disk_usd_h": args.disk_usd_h}})
open(DONE, "w").write("ok\n")
log("SESSION_DONE")
