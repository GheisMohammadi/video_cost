"""Compute every round 3 number from the raw session logs (run locally).

Usage: python3 report_batch_session.py SESSION_DIR [--gpu-usd-h 1.6] [--disk-usd-h 0.028]
Only raw jobs.jsonl / session.json / preflight.json are read, so anyone can recompute the
tables independently. One jobs.jsonl record exists per output video; this groups them back by
batch group (G1/G2/G3) to compute each group's real metric: wall time for the whole batch call,
and cost per video-second at that batch size.
"""
import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("session")
ap.add_argument("--gpu-usd-h", type=float)
ap.add_argument("--disk-usd-h", type=float)
a = ap.parse_args()
d = Path(a.session)
sess = json.load(open(d / "session.json"))
rate = (a.gpu_usd_h if a.gpu_usd_h is not None else sess["price_snapshot"]["gpu_usd_h"]) + \
       (a.disk_usd_h if a.disk_usd_h is not None else sess["price_snapshot"]["disk_usd_h"])
rows = [json.loads(l) for l in (d / "jobs.jsonl").read_text().split("\n") if l.strip()]

out = []
P = out.append
P("# Round 3 report: batching under concurrent load\n")
P(f"GPU: {sess['gpu']} | rate used: ${rate:.4f}/h | scope: {sess.get('scope_note', '')}\n")

by_group = {}
for r in rows:
    by_group.setdefault(r.get("group") or r.get("job", "?"), []).append(r)

P("## Groups\n")
P("| Group | Batch size | Status | Wall s (whole batch) | Cost/video | Cost/video-s | vs G1 cost/video-s |")
P("|---|---|---|---|---|---|---|")
base_cvs = None
for g in ("G1", "G2", "G3"):
    members = by_group.get(g, [])
    if not members:
        P(f"| {g} | - | no data | | | | |")
        continue
    if members[0].get("skipped"):
        P(f"| {g} | {members[0].get('batch_size', '?')} | **skipped** ({members[0]['skipped']}) | | | | |")
        continue
    n = len(members)
    ok_n = sum(m.get("delivered") for m in members)
    wall = members[0].get("batch_wall_s")
    cvs = members[0].get("cost_usd_per_video_second")
    cv = members[0].get("cost_usd_per_video")
    ratio = f"{cvs / base_cvs:.2f}x" if (base_cvs and cvs) else ("1.00x (baseline)" if g == "G1" else "-")
    if g == "G1" and cvs:
        base_cvs = cvs
    P(f"| {g} | {members[0].get('batch_size')} | {ok_n}/{n} delivered | {wall} | ${cv} | ${cvs} | {ratio} |")

P("\n## Per-video detail\n")
P("| Job | Group | Batch size | Delivered | Gate pass | Distinctness pass | Peak VRAM GB | GPU util % |")
P("|---|---|---|---|---|---|---|---|")
for r in rows:
    if r.get("skipped"):
        continue
    gate = r.get("gate", {})
    dist = r.get("distinctness", {})
    P(f"| {r.get('job')} | {r.get('group')} | {r.get('batch_size')} | {r.get('delivered')} | "
      f"{gate.get('pass')} | {dist.get('pass')} (min diff {dist.get('min_pairwise_diff')}) | "
      f"{r.get('peak_vram_gb')} | {r.get('gpu_util_mean')} |")

skipped = [g for g in ("G2", "G3") if by_group.get(g) and by_group[g][0].get("skipped")]
if skipped:
    P(f"\nSkipped groups: {skipped}. See jobs.jsonl for the exact reason recorded for each.")

print("\n".join(out))
