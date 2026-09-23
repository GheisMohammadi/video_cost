# Round 3 report: batching under concurrent load

GPU: NVIDIA A100-SXM4-80GB, 580.126.16, 81920 MiB, 400.00 W, 1410 MHz, Enabled | rate used: $1.6180/h | scope: batching = one pipe() call with multiple prompts, not independent worker processes or a queueing server

**Gate and distinctness values below are corrected** (see regate_from_files.py and the round README for why the live in-session values were wrong).

## Groups

| Group | Batch size | Status | Wall s (whole batch) | Cost/video | Cost/video-s | vs G1 cost/video-s |
|---|---|---|---|---|---|---|
| G1 | 1 | 1/1 delivered | 554.6 | $0.2508 | $0.0495 | 1.00x (baseline) |
| G2 | 2 | 2/2 delivered | 1062.0 | $0.2402 | $0.0474 | 0.96x |
| G3 | 4 | 4/4 delivered | 2080.7 | $0.2352 | $0.0465 | 0.94x |

## Per-video detail

| Job | Group | Batch size | Delivered | Gate pass | Distinctness pass | Peak VRAM GB | GPU util % |
|---|---|---|---|---|---|---|---|
| G1_A1_short | G1 | 1 | True | True | True (min diff None) | 32.5 | 92.6 |
| G2_A1_short | G2 | 2 | True | True | True (min diff 67.75) | 36.3 | 95.7 |
| G2_A2_median | G2 | 2 | True | True | True (min diff 67.75) | 36.3 | 95.7 |
| G3_A1_short | G3 | 4 | True | True | True (min diff 51.73) | 43.8 | 97.4 |
| G3_A2_median | G3 | 4 | True | True | True (min diff 51.73) | 43.8 | 97.4 |
| G3_A3_long | G3 | 4 | True | True | True (min diff 51.73) | 43.8 | 97.4 |
| G3_A4_non_english | G3 | 4 | True | True | True (min diff 51.73) | 43.8 | 97.4 |
