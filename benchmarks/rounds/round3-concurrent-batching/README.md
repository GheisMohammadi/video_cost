[← All rounds](../../../README.md)

# Round 3: cost under batched concurrent load

Status: complete. All 7 clips generated, delivered, copied, and checksum-verified; pod stopped normally. Design and reasons: [`PLAN.md`](PLAN.md). Exact tables regenerated from the raw logs: [`raw/REPORT.md`](raw/REPORT.md).

## Watch the batch=4 clips

Four different prompts, generated together in one GPU call:

<video src="raw/G3_A1_short.mp4" controls width="300"></video> <video src="raw/G3_A2_median.mp4" controls width="300"></video>

<video src="raw/G3_A3_long.mp4" controls width="300"></video> <video src="raw/G3_A4_non_english.mp4" controls width="300"></video>

## Summary

Batching gives a real, if modest, cost improvement. Running the same four prompts one at a time (round 1's method) costs $0.0495 per video-second at this pipeline's settings; batching two together drops that to $0.0474 (4% less), and batching four together to $0.0465 (6% less). The gain is real and consistent in direction (more batching, lower cost), but it is not dramatic -- it does not on its own close the gap to fal's $0.04/s, though it moves in that direction. Peak VRAM at batch=4 was 43.8 GB of 80 GB available, well under the limit, suggesting a larger batch size than 4 could likely be tested without running out of memory -- a candidate for a follow-up round.

## What batching means here

This tests one specific form of GPU concurrency: a single call to the model with multiple distinct prompts, so the GPU denoises all of them together. It does not test independent worker processes (infeasible on one GPU at this model's memory footprint) or a real request-queueing server. See `PLAN.md`, section 2, for the full scope statement.

## Results

| Group | Batch size | Wall time (whole batch) | Cost per video | Cost per video-second | vs. batch=1 |
|---|---|---|---|---|---|
| G1 | 1 | 554.6 s | $0.2508 | $0.0495 | 1.00x (baseline) |
| G2 | 2 | 1062.0 s | $0.2402 | $0.0474 | 0.96x |
| G3 | 4 | 2080.7 s | $0.2352 | $0.0465 | 0.94x |

All four prompts and seeds are identical to round 1's A1-A4. G1's own result here ($0.0495/video-s) is close to round 1's separately measured figure for the same prompt on a different pod ($0.0522/video-s using round 1's rate) -- consistent with rounds 1 and 2's earlier finding that this cost is stable across hosts.

Every one of the 7 clips passed the automated gate (correct frame count and resolution, not black, not frozen) and the distinctness check (every output in a batch differs substantially from every other output in the same batch -- minimum pairwise difference 67.75 at batch=2 and 51.73 at batch=4, far above the failure threshold), confirming the batched outputs are genuinely four independent, correctly-associated videos, not a duplication artifact.

## A bug was found and fixed during this round

The automated gate that ran live during the session reported **zero of seven clips delivered** -- every clip failed the "not black" and "not frozen" checks, including the ordinary batch=1 case. Before accepting that at face value, the actual video files were inspected directly (frame extraction, viewed): every clip showed real, correct, prompt-matching content -- an ARRI camera shot for the short prompt, a mosque scene for the Eid prompt, a noodle commercial for the long prompt, a cooking scene for the non-English prompt -- clearly distinct from each other and not remotely black or frozen.

The cause: this round's pipeline calls always pass the prompt as a list (needed to batch multiple prompts together, even for the single-item G1 case), and that code path returns frame data on a 0-1 scale, unlike the 0-255 scale returned by the plain-string calls rounds 1 and 2 used. The gate's thresholds were written for a 0-255 scale, so every check failed by comparing real, correct data against thresholds in the wrong units -- not a problem with the generated video.

Fix and verification, in order:
1. Confirmed the actual clips were fine by decoding real frames from the delivered files and viewing them.
2. Built an offline recheck (`regate_from_files.py`) that decodes each already-delivered mp4 -- which is always genuine 0-255 data regardless of what the pipeline returned internally -- and reapplies the same gate and distinctness logic against that. Result: 7 of 7 delivered, with difference values (24.5-85.9) consistent with round 1's own range (3.3-81.9) for real passing clips. This is the authoritative result used in this report; `jobs.jsonl` still holds the original (wrong) live values, unedited, alongside `corrected_gate.json`.
3. Fixed the actual bug in `batch_session.py` for any future run: both gate functions now detect whether frame data is already on a 0-255 scale or needs scaling up from 0-1, before applying thresholds. Verified against synthetic data covering both scales, including the exact failure case (a real, non-black, non-frozen float-scale video that the original code would have failed) and the cases the check exists to catch (black, frozen, and a simulated duplicated-output bug), all in both scales.

## Cost

Estimated pod-on time: about 88 minutes (session duration 82.96 minutes plus setup/copy overhead), roughly **$2.36** at $1.618/h combined rate -- comfortably under the $3.50 cap. This session's raw logs do not record container uptime before the script started (an omission versus rounds 1/2's telemetry, noted for the next round to restore), so this figure is an estimate; check the hosting panel for the exact amount.

One operational note: partway through the session, the independent stop guard's deadline was extended (from 100 to about 93 minutes remaining at the time, both well inside the approved cap) after the smoke tests' real per-step timing suggested the original deadline -- set from a pre-run guess -- left too little margin before the most valuable result (G3) would finish. The guard was restarted with a new deadline without touching the running generation process; this is recorded in the raw logs' guard log.

## Files

- `raw/REPORT.md`: tables generated from the raw logs (`python3 report_batch_session.py raw --gpu-usd-h 1.59 --disk-usd-h 0.028`, run from this folder).
- `raw/jobs.jsonl`: one record per output video, including the original (uncorrected) live gate values.
- `raw/corrected_gate.json`: the authoritative gate/distinctness/delivered values, recomputed from the actual delivered files.
- `raw/preflight.json`, `raw/session.json`: raw session records.
- `raw/*.mp4`: all 7 delivered clips (G1: 1, G2: 2, G3: 4).
- `regate_from_files.py`: the offline recheck script, in case a future round needs the same recovery.

## Limitations

1. One session, one prompt mixture per batch size -- no repeats, so run-to-run variance in the batching gain itself is not measured.
2. As stated in scope: this measures one specific meaning of concurrent GPU load (batched calls), not independent workers or a real serving queue.
3. Batch=8 or higher was not tested; VRAM headroom at batch=4 (43.8 of 80 GB) suggests it may be worth trying.
4. No blind human quality review this round (see `PLAN.md`, section 6) -- the automated gate and distinctness check, now corrected, cover technical validity and output independence, not comparative perceptual quality.
5. Pod-on cost is an estimate, not reconciled against the hosting panel, because this round's session log omits a container-uptime field that rounds 1/2 recorded.
