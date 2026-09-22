# Session report

GPU: NVIDIA A100-SXM4-80GB, 580.126.16, 81920 MiB, 400.00 W, 1410 MHz, Enabled | matmul 243 TFLOPS | weights: downloading | host load 15.84 27.64 31.37 7/5046 4532
Rate used: $1.69/h GPU + $0.025/h disk (disk rate assumed) | fal 480p $0.04/video-s (not re-checked)

Jobs: 6 run, 6 delivered and passed the automated gate, 0 failed, 0 skipped []

## Per job

| job | stratum | steps | tokens | truncated | generate s | encode s | busy $ | busy $/video-s | GPU util % | SM clock MHz (mean/min) | throttle | gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1_short | short | 27 | 44 | False | 551.7 | 3.1 | 0.264 | 0.0522 | 92.0 | 1310/1155.0 | 0x4 | pass |
| A2_median | median | 27 | 387 | False | 568.4 | 3.4 | 0.272 | 0.0538 | 89.4 | 1305/1155.0 | 0x4 | pass |
| A3_long | long | 27 | 854 | True | 565.7 | 4.1 | 0.271 | 0.0536 | 89.7 | 1305/1155.0 | 0x4 | pass |
| A4_non_english | non_english | 27 | 393 | False | 558.4 | 2.9 | 0.267 | 0.0528 | 90.7 | 1308/1155.0 | 0x4 | pass |
| B1_median_20steps | median | 20 | 387 | False | 424.1 | 3.1 | 0.204 | 0.0402 | 89.2 | 1304/1155.0 | 0x4 | pass |
| B2_median_15steps | median | 15 | 387 | False | 333.9 | 2.9 | 0.160 | 0.0317 | 85.7 | 1300/1155.0 | 0x4 | pass |

## Fal-matched 480p, 27 steps (n=4; different prompts, one session, one host)

- generate+encode s: mean 564.4, median 565.5, min 554.8, max 571.8, stdev 6.8 (1.2%)
- busy-queue cost: **$0.0531 per delivered video-second** ($0.269 per 5.0625 s clip); fal 480p: $0.04/s ($0.203 per clip); ours / fal = 1.33x
- utilization-adjusted (cost / utilization): 100%: $0.0531 (1.33x fal), 75%: $0.0708 (1.77x fal), 50%: $0.1062 (2.66x fal), 25%: $0.2125 (5.31x fal)
- **all-in this session**: pod on about 81 min (uptime at start 13 + session 66 + copy 2) = $2.32; $0.0762 per delivered video-second over 6 clips (30.4 s). Not a steady-state price.
- setup overhead (load, download, warm-up, idle, copy) about 31 min = $0.88. Amortized over N clips of the same kind:
  N=4: $0.0964/s, N=10: $0.0704/s, N=50: $0.0566/s, N=200: $0.0540/s
- not included: fal's FILM interpolation, delivery/egress, human review time, retries for bad outputs.

## Steps ladder (same prompt and seed)

| steps | generate s | busy $/clip | vs 27 steps |
|---|---|---|---|
| 15 | 333.9 | 0.160 | 0.59x time |
| 20 | 424.1 | 0.204 | 0.75x time |
| 27 | 568.4 | 0.272 | 1.00x time |
