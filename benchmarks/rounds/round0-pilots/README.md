[← All rounds](../../../README.md)

# Round 0: pilot smoke tests (Sep 19-20, 2026)

Status: informal. These predate the "round" methodology (no preflight, no frozen job list, no independent stop guard, no blind review). They exist to confirm the pod and pipeline work, and to size Round 1's budget. **Do not use these numbers for cost comparisons** — use [Round 1](../round1-wan22-a14b-480p/) instead.

## Clips

<video src="clips/wan22_ti2v5b_sxm.mp4" controls width="420"></video>

Wan2.2 TI2V-5B, 1280x704, 3.04 s, 50 steps, on the A100-SXM pod.

| Clip | What it is |
|---|---|
| [`wan22_ti2v5b_pcie.mp4`](clips/wan22_ti2v5b_pcie.mp4) | Same 5B model and settings, on the earlier A100 PCIe pod |
| [`wan22_ti2v5b_sxm.mp4`](clips/wan22_ti2v5b_sxm.mp4) | 5B model on the A100-SXM pod (shown above) |
| [`wan22_a14b_480p_sxm.mp4`](clips/wan22_a14b_480p_sxm.mp4) | First A14B run at 480p, fal defaults, single sample |
| [`wan22_a14b_720p_sxm.mp4`](clips/wan22_a14b_720p_sxm.mp4) | First A14B run at 720p, fal defaults, single sample |

## Numbers (single runs, one sample each — see `raw/SUMMARY.md`)

| Model | Res | Steps | Generate | $/video-s (est., $1.618-1.70/h GPU) |
|---|---|---|---|---|
| Wan2.2 TI2V-5B (PCIe) | 1280x704 | 50 | 204 s | ~$0.029 |
| Wan2.2 TI2V-5B (SXM) | 1280x704 | 50 | 187 s | ~$0.029 |
| Wan2.2 A14B | 1280x720 | 27 | 1,961 s | $0.174-0.183 |
| Wan2.2 A14B | 832x480 | 27 | 582 s | $0.052-0.054 |

The 480p A14B figure here is close to Round 1's measured $0.053/s at the same settings, which is a useful cross-check even though this run had no warm-up (its first diffusion step alone took 48s) and no repeats.

## Raw data

`raw/SUMMARY.md`, `raw/metrics_wan22_ti2v5b.json`, `raw/metrics_wan22_ti2v5b_a100sxm.json`, `raw/a14b_runs.jsonl`.
