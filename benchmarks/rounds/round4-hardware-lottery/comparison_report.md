# Round 4: GPU hardware lottery and output reproducibility

## Hardware identity

- Pod A: NVIDIA A100-SXM4-80GB, 570.172.08, 81920 MiB, 500.00 W, 1410 MHz, Enabled | UUID: GPU-258ae402-6a0b-4d3e-62ce-83764aff539b
- Pod B: NVIDIA A100-SXM4-80GB, 595.91.07, 81920 MiB, 400.00 W, 1410 MHz, Enabled | UUID: GPU-5a773104-1345-9d3b-e9a1-93f938e261a8
- **Different physical GPU units, confirmed by UUID**
- Host load at pod check-in: A=13.07 13.93 14.47 15/4200 822 | B=21.12 11.66 10.18 34/8645 2553
- bf16 matmul (preflight): A=239 TFLOPS | B=240 TFLOPS

## Per-job comparison

| Job | Steps | Pod A generate s | Pod B generate s | Diff | A throttle | B throttle | A SM MHz | B SM MHz | A peak VRAM | B peak VRAM |
|---|---|---|---|---|---|---|---|---|---|---|
| A1_short | 27 | 573.4 | 571.3 | -0.4% | 0x4 | 0x4 | 1363 | 1326 | 32.5 | 32.5 |
| A2_median | 27 | 565.5 | 575.1 | +1.7% | 0x4 | 0x4 | 1366 | 1318 | 32.5 | 32.5 |
| A3_long | 27 | 555.2 | 567.2 | +2.2% | 0x4 | 0x4 | 1370 | 1321 | 32.5 | 32.5 |
| A4_non_english | 27 | 557.3 | 569.1 | +2.1% | 0x4 | 0x4 | 1369 | 1325 | 32.5 | 32.5 |
| B1_median_20steps | 20 | 443.9 | 444.5 | +0.1% | 0x4 | 0x4 | 1356 | 1320 | 32.5 | 32.5 |
| B2_median_15steps | 15 | 338.3 | 350.6 | +3.6% | 0x4 | 0x4 | 1355 | 1318 | 32.5 | 32.5 |

Mean speed difference, pod B vs pod A, across 6 shared jobs: +1.6%. Range: -0.4% to +3.6%.

## Reproducibility (same seed, same 27 steps, both pods)

| Job | Seed | File bytes identical | Decoded frames byte-identical | Mean pixel difference (0-255 scale) |
|---|---|---|---|---|
| A1_short | 4200 | False | False | 1.29 |
| A2_median | 4201 | False | False | 0.87 |
| A3_long | 4202 | False | False | 1.11 |
| A4_non_english | 4203 | False | False | 0.82 |

A nonzero mean pixel difference with matching content (check visually) means the two GPUs produced very similar but not bit-identical output from the same seed -- expected, since GPU floating-point reduction order is not guaranteed identical across different hardware. A mean difference in the same range as two genuinely different videos (see round 3's distinctness check, which flagged real differences above roughly 50) would instead mean the seed did not actually reproduce the same scene, a stronger and more concerning finding worth flagging clearly.
