"""Recompute the automated gate and distinctness check directly from the delivered mp4 files.

The live in-session gate in batch_session.py compared frame data against thresholds written for
a 0-255 pixel range, but this pipeline's batched calls (prompt passed as a list, used for every
group in this round including the single-item G1) return frames in 0-1 float range instead of
0-255, unlike the single-string-prompt calls used in rounds 1/2. Every threshold check failed as
a false negative as a result; the actual generated video content is correct (confirmed visually:
each clip matches its prompt, and clips within a batch are visibly distinct from each other).

Decoding an already-encoded H.264 file always yields real 0-255 uint8 frames regardless of what
format the pipeline returned internally, which sidesteps the bug entirely rather than guessing at
its exact cause. This produces the authoritative pass/fail values for this round; jobs.jsonl's own
gate/distinctness/delivered fields are superseded by corrected_gate.json, not edited in place, so
the original (buggy) live result stays on record.

Usage: python3 regate_from_files.py SESSION_DIR
Needs ffmpeg on PATH. Writes corrected_gate.json next to the clips.
"""
import itertools
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

session = Path(sys.argv[1])
jobs = [json.loads(l) for l in (session / "jobs.jsonl").read_text().split("\n") if l.strip() and "skipped" not in l]


def decode_frames(path):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), f"{td}/f%04d.png"], check=True)
        files = sorted(Path(td).glob("f*.png"))
        return [np.array(Image.open(f).convert("RGB")) for f in files]


def gate_one(frames, expect_frames, expect_hw):
    n = len(frames)
    idx = np.linspace(0, n - 1, 9).astype(int)
    means = [float(frames[i].mean()) for i in idx]
    diff = float(np.abs(frames[n - 1].astype(np.float32) - frames[0].astype(np.float32)).mean())
    checks = {"frames_ok": n == expect_frames, "shape_ok": tuple(frames[0].shape[:2]) == expect_hw,
              "not_black": min(means) > 5, "not_frozen": diff > 2.0}
    return {"pass": all(checks.values()), "n_frames": n, "first_last_diff": round(diff, 2), **checks}


def distinctness_check(all_frames):
    n = len(all_frames)
    if n < 2:
        return {"pass": True, "min_pairwise_diff": None}
    mid = lambda fr: fr[len(fr) // 2].astype(np.float32)
    diffs = [round(float(np.abs(mid(all_frames[i]) - mid(all_frames[j])).mean()), 2)
             for i, j in itertools.combinations(range(n), 2)]
    return {"pass": min(diffs) > 2.0, "min_pairwise_diff": min(diffs), "all_pairwise_diffs": diffs}


by_group = {}
for j in jobs:
    by_group.setdefault(j["group"], []).append(j)

corrected = {}
for group, members in by_group.items():
    decoded = []
    for m in members:
        clip = session / f"{m['job']}.mp4"
        frames = decode_frames(clip)
        gate = gate_one(frames, m["frames"], (m["height"], m["width"]))
        corrected[m["job"]] = {"gate": gate}
        decoded.append(frames)
        print(m["job"], "gate:", gate["pass"], "first_last_diff", gate["first_last_diff"])
    dist = distinctness_check(decoded)
    print(group, "distinctness:", dist["pass"], "min_pairwise_diff", dist.get("min_pairwise_diff"))
    for m in members:
        corrected[m["job"]]["distinctness"] = dist
        corrected[m["job"]]["delivered"] = corrected[m["job"]]["gate"]["pass"] and dist["pass"] is not False

json.dump(corrected, open(session / "corrected_gate.json", "w"), indent=1)
n_delivered = sum(v["delivered"] for v in corrected.values())
print(f"\n{n_delivered} of {len(corrected)} delivered after correction (was 0 of {len(corrected)} live).")
print("Wrote corrected_gate.json. jobs.jsonl is left as originally recorded.")
