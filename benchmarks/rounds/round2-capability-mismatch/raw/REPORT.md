# Session report

GPU: NVIDIA A100-SXM4-80GB, 580.159.04, 81920 MiB, 400.00 W, 1410 MHz, Enabled | matmul 243 TFLOPS | weights: downloading | host load 42.14 40.38 37.95 44/7766 2483
Rate used: $1.59/h GPU + $0.028/h disk (disk rate assumed) | fal 480p $0.04/video-s (not re-checked)

Jobs: 5 run, 5 delivered and passed the automated gate, 0 failed, 1 skipped ['M6_kitchen_sink']

## Per job

| job | stratum | steps | tokens | truncated | generate s | encode s | busy $ | busy $/video-s | GPU util % | SM clock MHz (mean/min) | throttle | gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M1_audio | audio | 27 | 117 | False | 594.0 | 4.0 | 0.269 | 0.0531 | 86.5 | 1289/1155.0 | 0x4 | pass |
| M2_resolution | resolution | 27 | 145 | False | 589.6 | 4.1 | 0.267 | 0.0527 | 86.9 | 1287/1155.0 | 0x4 | pass |
| M3_aspect | aspect | 27 | 125 | False | 587.2 | 4.1 | 0.266 | 0.0525 | 87.8 | 1290/1155.0 | 0x4 | pass |
| M4_camera | camera | 27 | 115 | False | 585.7 | 4.1 | 0.265 | 0.0524 | 87.6 | 1289/1155.0 | 0x4 | pass |
| M5_duration | duration | 27 | 118 | False | 590.3 | 4.3 | 0.267 | 0.0528 | 87.2 | 1287/1155.0 | 0x4 | pass |

## Fal-matched 480p, 27 steps (n=5; different prompts, one session, one host)

- generate+encode s: mean 593.5, median 593.7, min 589.8, max 598.0, stdev 2.8 (0.5%)
- busy-queue cost: **$0.0527 per delivered video-second** ($0.267 per 5.0625 s clip); fal 480p: $0.04/s ($0.203 per clip); ours / fal = 1.32x
- utilization-adjusted (cost / utilization): 100%: $0.0527 (1.32x fal), 75%: $0.0703 (1.76x fal), 50%: $0.1054 (2.63x fal), 25%: $0.2108 (5.27x fal)
- **all-in this session**: pod on about 71 min (uptime at start 8 + session 61 + copy 2) = $1.91; $0.0753 per delivered video-second over 5 clips (25.3 s). Not a steady-state price.
- setup overhead (load, download, warm-up, idle, copy) about 21 min = $0.57. Amortized over N clips of the same kind:
  N=4: $0.0809/s, N=10: $0.0640/s, N=50: $0.0549/s, N=200: $0.0533/s
- not included: fal's FILM interpolation, delivery/egress, human review time, retries for bad outputs.
