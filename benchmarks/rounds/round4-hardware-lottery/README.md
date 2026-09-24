[← All rounds](../../../README.md)

# Round 4: GPU hardware lottery and output reproducibility

Status: complete. Both pods ran simultaneously, all 14 clips (7 per pod) delivered, copied, and checksum-verified; both pods stopped. Design and reasons: [`PLAN.md`](PLAN.md). Exact tables regenerated from the raw logs: [`comparison_report.md`](comparison_report.md).

## Watch the reproducibility case

Same prompt, same seed, same settings, two different physical GPUs, frame 40 of each:

<video src="podA/A1_short.mp4" controls width="380"></video> <video src="podB/A1_short.mp4" controls width="380"></video>

## Summary

Renting "the same GPU spec" twice from RunPod did give two genuinely different physical machines -- confirmed by GPU UUID, not just inferred -- and they were not identical in every respect: pod A carried an unusually high 500 W power limit (every pod used in this project before now, and pod B here, capped at 400 W) and an older driver. Despite that real difference in configuration, the two pods' speed on the identical job list differed by only 1.6% on average (range -0.4% to +3.6%), and both hit the identical software power-cap throttle on every job. The "lottery" exists -- you cannot request a specific unit, and this pair differed in power limit and driver version -- but for raw throughput on this workload, it was a minor effect this time, not the kind of swing that would change a cost estimate meaningfully.

Reproducibility: with the identical seed and settings, the two GPUs did not produce byte-identical output (expected -- floating-point results are not guaranteed to reduce in the same order on different hardware), but the difference was small: a mean pixel difference of 0.82-1.29 across the four comparable prompts, against round 3's established scale where genuinely different content measured above roughly 50. Visual inspection of a sample frame (above) shows no discernible difference. This is a reassuring result for the specific question that motivated checking it: a seed reliably reproduces the same output across different physical GPUs on this pipeline, closely enough that a simple pixel-difference check could plausibly be used to verify a remote worker's output, without requiring an impossible exact match.

## Hardware identity

| | Pod A | Pod B |
|---|---|---|
| GPU | A100-SXM4-80GB | A100-SXM4-80GB |
| GPU UUID | GPU-258ae402-6a0b-4d3e-62ce-83764aff539b | GPU-5a773104-1345-9d3b-e9a1-93f938e261a8 |
| Driver | 570.172.08 | 595.91.07 |
| Power limit | **500 W** | 400 W |
| Host cores / RAM | 192 / 944 GB | 256 / 2003 GB |
| Host load at check-in | 13.07 | 21.12 |
| bf16 matmul (preflight) | 239 TFLOPS | 240 TFLOPS |

Confirmed different physical units by UUID, not inferred from driver version as in earlier rounds (a gap this round's design specifically fixed). The two pods also differ in host RAM and core count, and pod A's 500 W power limit is higher than every other pod used in this project, including pod B.

## Speed comparison (identical job list, both pods)

| Job | Steps | Pod A s | Pod B s | Diff | A SM MHz | B SM MHz |
|---|---|---|---|---|---|---|
| A1_short | 27 | 573.4 | 571.3 | -0.4% | 1363 | 1326 |
| A2_median | 27 | 565.5 | 575.1 | +1.7% | 1366 | 1318 |
| A3_long | 27 | 555.2 | 567.2 | +2.2% | 1370 | 1321 |
| A4_non_english | 27 | 557.3 | 569.1 | +2.1% | 1369 | 1325 |
| B1_median_20steps | 20 | 443.9 | 444.5 | +0.1% | 1356 | 1320 |
| B2_median_15steps | 15 | 338.3 | 350.6 | +3.6% | 1355 | 1318 |

Mean: +1.6% (pod B slower than pod A). Every job on both pods showed the same software power-cap throttle reason. Pod A's SM clock ran consistently 3-4% higher than pod B's (1355-1370 MHz vs 1318-1326 MHz) -- plausibly related to its higher power limit -- but this translated to only a small overall speed advantage, not a proportional one.

Both pods also ran noticeably higher SM clocks than rounds 1 and 3's pods (1300-1313 MHz there, versus 1318-1370 MHz here), despite all of them sharing the identical throttle reason. With this few samples, whether that reflects the specific units, host contention at the time, or something else cannot be separated; it is a pattern worth tracking in a later round, not a conclusion this one supports on its own.

## Reproducibility detail

| Job | Seed | File bytes identical | Decoded frames byte-identical | Mean pixel difference |
|---|---|---|---|---|
| A1_short | 4200 | No | No | 1.29 |
| A2_median | 4201 | No | No | 0.87 |
| A3_long | 4202 | No | No | 1.11 |
| A4_non_english | 4203 | No | No | 0.82 |

All four differences are small and in a tight band (0.82-1.29), consistent with ordinary floating-point non-determinism rather than any of them being a near-miss toward "actually different content."

## Cost

| | Pod A | Pod B |
|---|---|---|
| Pod-on time (estimated) | ~67 min | ~68 min (includes a delayed stop, see below) |
| Cost at $1.618/h | ~$1.80 | ~$1.84 |

**Combined: about $3.64**, under the $5.00 cap. Not yet reconciled against the hosting panel; these are computed from session timing, as in every prior round.

## Operational note: a stop command failed silently and was caught by verification

Pod B's automated stop, issued by the puller once its results were fully copied and verified, failed with a network-level error from RunPod's API (`context deadline exceeded`) -- the request was sent correctly but the response never arrived in time. The puller reported success regardless, because it only checks that the stop command was issued, not that the pod actually stopped. This was caught by a separate, manual connectivity check afterward (matching the practice this project follows before ending every session), which found pod B still running; it was stopped immediately once found. Estimated extra billing from the delay: a few minutes, on the order of $0.05-0.10, included in the cost above. The puller does not yet verify a stop actually succeeded rather than merely being sent -- a real gap, noted here for a future fix rather than fixed silently.

## Files

- `comparison_report.md`: full tables generated by `compare_pods.py podA podB --gpu-usd-h 1.59 --disk-usd-h 0.028`.
- `podA/`, `podB/`: each pod's raw logs (`jobs.jsonl`, `preflight.json`, `session.json`) and all 7 clips (warm-up plus 6 measured jobs).

## Limitations

1. Two pods, one comparison. This establishes that this specific pair differed in configuration but not dramatically in speed; it does not establish a distribution of how much RunPod rentals of this type typically vary.
2. Reproducibility was checked only for this pipeline's specific settings (bf16, CPU offload, this diffusers version), on four prompts, not a broad sweep.
3. As designed, "the lottery" here means two independent requests for the same instance type, whatever RunPod assigned -- it cannot target a specific physical unit, and a different pair of rentals could show a larger or smaller gap.
4. Cost is an estimate, not reconciled against the hosting panel.
