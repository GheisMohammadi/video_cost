# Benchmark results (2026-09-19)

GPU price: $1.618/h (RunPod panel). The A14B costs below were first computed at $1.70/h and are recomputed here. Pod: RunPod A100-SXM4-80GB. Single runs, no repeats. Compute only: model load, idle time and fal's FILM interpolation are excluded.

| Model | Res | Frames / fps | Steps | Generate | $ / clip | $ / video-s | fal price / video-s |
|---|---|---|---|---|---|---|---|
| Wan2.2 TI2V-5B (PCIe A100) | 1280x704 | 73 / 24 (3.04 s) | 50 | 204 s | | ~$0.028* | not the fal model |
| Wan2.2 TI2V-5B (SXM A100) | 1280x704 | 73 / 24 (3.04 s) | 50 | 187 s | | ~$0.028* | not the fal model |
| Wan2.2 T2V-A14B | 1280x720 | 81 / 16 (5.06 s) | 27 | 1961 s | $0.881 | $0.174 | $0.08 (720p) |
| Wan2.2 T2V-A14B | 832x480 | 81 / 16 (5.06 s) | 27 | 582 s | $0.262 | $0.052 | $0.04 (480p) |

*Derived from the run time and the assumed price, not logged by the script.

A14B runs use fal's standard request defaults (fal_wan22_config.md), CPU offload, the prompt "Kung Fu Friendly Match Victory" (313 tokens, not truncated). Raw records: a14b_runs.jsonl.

Notes:
- 720p GPU utilization 96.6%, 385 W. Compute-bound (estimated about 13 PFLOP per step).
- 480p first step took 48 s (warm-up); steady state about 18 s/step.
- 480p output has garbled burned-in subtitles and outfit changes between frames; 720p looked cleaner in a 5-frame check. No quality scoring done (not required yet).
