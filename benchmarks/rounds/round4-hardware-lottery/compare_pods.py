"""Compare two pod rentals of the same advertised GPU spec, run on the identical frozen job list
(run locally, after both pods' raw/ folders have been pulled with pull_session.py).

Usage: python3 compare_pods.py POD_A_RAW POD_B_RAW [--gpu-usd-h 1.6] [--disk-usd-h 0.028]
Needs ffmpeg on PATH (frame decoding) and numpy/Pillow.

Two questions:
1. Hardware lottery: for each prompt run on both pods, how much does generate time, cost,
   GPU clock, throttle reason, and peak VRAM differ? Also reports whether the two pods' GPU UUIDs
   prove they are physically different units, if that field was captured.
2. Reproducibility: for prompts using the same seed and step count on both pods (the ones from
   the A1-A4 set, all at 27 steps), does the identical seed produce the same output on different
   hardware, or does it drift? Checked three ways, weakest to strongest claim: exact file bytes,
   exact decoded-frame bytes, and mean pixel difference if not exact (GPU floating-point results
   are not guaranteed bit-identical across different hardware even with an identical seed, so
   exact match is not assumed going in).
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("pod_a")
ap.add_argument("pod_b")
ap.add_argument("--gpu-usd-h", type=float, default=1.6)
ap.add_argument("--disk-usd-h", type=float, default=0.028)
a = ap.parse_args()
rate = a.gpu_usd_h + a.disk_usd_h


def load(pod):
    d = Path(pod)
    jobs = {json.loads(l)["job"]: json.loads(l) for l in (d / "jobs.jsonl").read_text().split("\n")
            if l.strip() and "skipped" not in l}
    pre = json.loads((d / "preflight.json").read_text())
    return d, jobs, pre


def decode_frames(path):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), f"{td}/f%04d.png"], check=True)
        return [np.array(Image.open(f).convert("RGB")) for f in sorted(Path(td).glob("f*.png"))]


dA, jobsA, preA = load(a.pod_a)
dB, jobsB, preB = load(a.pod_b)

out = []
P = out.append
P("# Round 4: GPU hardware lottery and output reproducibility\n")

P("## Hardware identity\n")
P(f"- Pod A: {preA.get('gpu')} | UUID: {preA.get('gpu_uuid', 'not captured')}")
P(f"- Pod B: {preB.get('gpu')} | UUID: {preB.get('gpu_uuid', 'not captured')}")
if preA.get("gpu_uuid") and preB.get("gpu_uuid"):
    same = preA["gpu_uuid"] == preB["gpu_uuid"]
    P(f"- **{'SAME physical GPU unit (unexpected -- re-check before trusting any speed difference below as a hardware effect)' if same else 'Different physical GPU units, confirmed by UUID'}**")
else:
    P("- GPU UUID not available for at least one pod; physical-unit identity cannot be confirmed, only inferred from driver version and behavior.")
P(f"- Host load at pod check-in: A={preA.get('host', {}).get('loadavg')} | B={preB.get('host', {}).get('loadavg')}")
P(f"- bf16 matmul (preflight): A={preA.get('matmul_bf16_tflops')} TFLOPS | B={preB.get('matmul_bf16_tflops')} TFLOPS\n")

P("## Per-job comparison\n")
P("| Job | Steps | Pod A generate s | Pod B generate s | Diff | A throttle | B throttle | A SM MHz | B SM MHz | A peak VRAM | B peak VRAM |")
P("|---|---|---|---|---|---|---|---|---|---|---|")
shared = sorted(set(jobsA) & set(jobsB) - {"W0_warmup"})
for j in shared:
    ra, rb = jobsA[j], jobsB[j]
    ga, gb = ra.get("generate_s"), rb.get("generate_s")
    diff_pct = f"{100 * (gb - ga) / ga:+.1f}%" if ga else "-"
    P(f"| {j} | {ra.get('steps')} | {ga} | {gb} | {diff_pct} | {ra.get('throttle_reasons_seen')} | {rb.get('throttle_reasons_seen')} | "
      f"{ra.get('sm_clock_mhz_mean')} | {rb.get('sm_clock_mhz_mean')} | {ra.get('peak_vram_gb')} | {rb.get('peak_vram_gb')} |")

if shared:
    diffs = [100 * (jobsB[j]["generate_s"] - jobsA[j]["generate_s"]) / jobsA[j]["generate_s"] for j in shared if jobsA[j].get("generate_s")]
    if diffs:
        P(f"\nMean speed difference, pod B vs pod A, across {len(diffs)} shared jobs: {sum(diffs)/len(diffs):+.1f}%. "
          f"Range: {min(diffs):+.1f}% to {max(diffs):+.1f}%.")

P("\n## Reproducibility (same seed, same 27 steps, both pods)\n")
repro_candidates = [j for j in shared if jobsA[j].get("steps") == 27 and jobsA[j].get("seed") == jobsB[j].get("seed")]
P("| Job | Seed | File bytes identical | Decoded frames byte-identical | Mean pixel difference (0-255 scale) |")
P("|---|---|---|---|---|")
for j in repro_candidates:
    pa, pb = dA / f"{j}.mp4", dB / f"{j}.mp4"
    file_same = hashlib.sha256(pa.read_bytes()).digest() == hashlib.sha256(pb.read_bytes()).digest()
    fa, fb = decode_frames(pa), decode_frames(pb)
    n = min(len(fa), len(fb))
    frame_bytes_same = n == len(fa) == len(fb) and all(np.array_equal(fa[i], fb[i]) for i in range(n))
    mean_diff = round(float(np.mean([np.abs(fa[i].astype(np.float32) - fb[i].astype(np.float32)).mean() for i in range(n)])), 2)
    P(f"| {j} | {jobsA[j]['seed']} | {file_same} | {frame_bytes_same} | {mean_diff} |")

P("\nA nonzero mean pixel difference with matching content (check visually) means the two GPUs produced very similar "
  "but not bit-identical output from the same seed -- expected, since GPU floating-point reduction order is not "
  "guaranteed identical across different hardware. A mean difference in the same range as two genuinely different "
  "videos (see round 3's distinctness check, which flagged real differences above roughly 50) would instead mean "
  "the seed did not actually reproduce the same scene, a stronger and more concerning finding worth flagging clearly.")

print("\n".join(out))
