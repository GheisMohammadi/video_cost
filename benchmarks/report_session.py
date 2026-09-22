"""Compute every cost number from the raw session logs (run locally).

Usage: python3 report_session.py SESSION_DIR [--copy-s 180] [--review review_scores.csv --key _key/review_key.json]
Only raw jobs.jsonl / session.json / preflight.json are read, so anyone can recompute the tables independently.
"""
import argparse
import csv
import json
import statistics as st
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("session")
ap.add_argument("--copy-s", type=float, default=180, help="seconds between session end and pod stop (copying results)")
ap.add_argument("--gpu-usd-h", type=float, help="override the GPU rate stored in session.json")
ap.add_argument("--disk-usd-h", type=float, help="override the disk rate stored in session.json")
ap.add_argument("--review")
ap.add_argument("--key")
a = ap.parse_args()
d = Path(a.session)
sess = json.load(open(d / "session.json"))
pre = json.load(open(d / "preflight.json"))
rows = [json.loads(l) for l in (d / "jobs.jsonl").read_text().split("\n") if l.strip()]
price = dict(sess["price_snapshot"])
if a.gpu_usd_h is not None:
    price["gpu_usd_h"] = a.gpu_usd_h
if a.disk_usd_h is not None:
    price["disk_usd_h"] = a.disk_usd_h
rate = price["gpu_usd_h"] + price["disk_usd_h"]
fal = price["fal_480p_usd_per_s"]
ran = [r for r in rows if r.get("measured") and "skipped" not in r]
skipped = [r["job"] for r in rows if "skipped" in r]
good = [r for r in ran if r.get("delivered")]
busy = lambda r: r["generate_s"] + r.get("encode_s", 0)
usd = lambda s: s * rate / 3600
out = []
P = out.append

P(f"# Session report\n")
P(f"GPU: {pre['gpu']} | matmul {pre.get('matmul_bf16_tflops')} TFLOPS | weights: {pre['weights']} | host load {pre['host']['loadavg']}")
P(f"Rate used: ${price['gpu_usd_h']}/h GPU + ${price['disk_usd_h']}/h disk (disk rate assumed) | fal 480p ${fal}/video-s (not re-checked)\n")
P(f"Jobs: {len(ran)} run, {len(good)} delivered and passed the automated gate, {len(ran)-len(good)} failed, {len(skipped)} skipped {skipped}\n")
P("## Per job\n\n| job | stratum | steps | tokens | truncated | generate s | encode s | busy $ | busy $/video-s | GPU util % | SM clock MHz (mean/min) | throttle | gate |")
P("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in ran:
    ok = r.get("delivered")
    vs = r.get("video_s") or 1
    P(f"| {r['job']} | {r['stratum']} | {r['steps']} | {r.get('tokens_pod')} | {r.get('truncated')} | {r['generate_s']} | {r.get('encode_s','-')} | "
      f"{usd(busy(r)):.3f} | {usd(busy(r))/vs:.4f} | {r.get('gpu_util_mean','-')} | {r.get('sm_clock_mhz_mean','-')}/{r.get('sm_clock_mhz_min','-')} | "
      f"{r.get('throttle_reasons_seen','-')} | {'pass' if ok else 'FAIL ' + str(r.get('error', r.get('gate')))[:60]} |")

A = [r for r in good if r["steps"] == 27]
if A:
    g = [busy(r) for r in A]
    vs = A[0]["video_s"]
    c = usd(sum(g)) / (vs * len(A))
    P(f"\n## Fal-matched 480p, 27 steps (n={len(A)}; different prompts, one session, one host)\n")
    P(f"- generate+encode s: mean {st.mean(g):.1f}, median {st.median(g):.1f}, min {min(g):.1f}, max {max(g):.1f}, stdev {st.pstdev(g):.1f} ({100*st.pstdev(g)/st.mean(g):.1f}%)")
    P(f"- busy-queue cost: **${c:.4f} per delivered video-second** (${c*vs:.3f} per {vs:.4f} s clip); fal 480p: ${fal}/s (${fal*vs:.3f} per clip); ours / fal = {c/fal:.2f}x")
    P("- utilization-adjusted (cost / utilization): " + ", ".join(f"{int(u*100)}%: ${c/u:.4f} ({c/u/fal:.2f}x fal)" for u in (1, .75, .5, .25)))
    # all-in: everything the pod was on for, not only the busy queue
    pod_on = sess["container_uptime_at_start_s"] + sess["session_s"] + a.copy_s
    tot = usd(pod_on)
    delivered_s = sum(r["video_s"] for r in good)
    P(f"- **all-in this session**: pod on about {pod_on/60:.0f} min (uptime at start {sess['container_uptime_at_start_s']/60:.0f} + session {sess['session_s']/60:.0f} + copy {a.copy_s/60:.0f}) = ${tot:.2f}; "
      f"${tot/delivered_s:.4f} per delivered video-second over {len(good)} clips ({delivered_s:.1f} s). Not a steady-state price.")
    overhead = pod_on - sum(busy(r) for r in ran)
    P(f"- setup overhead (load, download, warm-up, idle, copy) about {overhead/60:.0f} min = ${usd(overhead):.2f}. Amortized over N clips of the same kind:")
    P("  " + ", ".join(f"N={n}: ${(usd(overhead) + n*usd(st.mean(g)))/(n*vs):.4f}/s" for n in (4, 10, 50, 200)))
    P("- not included: fal's FILM interpolation, delivery/egress, human review time, retries for bad outputs.")

ladder = sorted([r for r in good if r["stratum"] == "median"], key=lambda r: r["steps"])
if len(ladder) > 1:
    P("\n## Steps ladder (same prompt and seed)\n\n| steps | generate s | busy $/clip | vs 27 steps |")
    P("|---|---|---|---|")
    base = next((busy(r) for r in ladder if r["steps"] == 27), None)
    for r in ladder:
        P(f"| {r['steps']} | {r['generate_s']} | {usd(busy(r)):.3f} | {'-' if not base else f'{busy(r)/base:.2f}x time'} |")

if a.review and a.key:
    key = json.load(open(a.key))
    sc = list(csv.DictReader(open(a.review)))
    P("\n## Blind review (single reviewer, unblinded after scoring)\n")
    acc_s, tot_s, n_acc = 0.0, 0.0, 0
    job = {r["job"]: r for r in good}
    for row in sc:
        j = key[row["clip"]]
        r = job[j]
        in_strata = row["set"].startswith("strata") or j == "A2_median"  # A2 is scored inside the steps set
        if in_strata:
            tot_s += r["video_s"]
            if row["prompt_match"] in ("pass", "partial"):
                acc_s += r["video_s"]; n_acc += 1
        if row["set"].startswith("strata"):
            P(f"- {row['clip']} = {j} ({r['stratum']}): prompt_match {row['prompt_match']}, notes: {row['artifacts_notes']}")
        else:
            P(f"- {row['clip']} = {j} ({r['steps']} steps): rank {row['rank']}, motion {row['motion']}, prompt_match {row['prompt_match']}, notes: {row['artifacts_notes']}")
    if tot_s:
        strata_jobs = [r for r in good if r["block"] == "A_strata"]
        cost = usd(sum(busy(r) for r in strata_jobs))
        P(f"\nAccepted (pass or partial) {n_acc} of {len(strata_jobs)} strata clips. Cost per accepted second: "
          f"{'undefined (none accepted)' if not acc_s else f'${cost/acc_s:.4f}'}. With n={len(strata_jobs)} and one reviewer this is an anecdote, not a rate.")
print("\n".join(out))
