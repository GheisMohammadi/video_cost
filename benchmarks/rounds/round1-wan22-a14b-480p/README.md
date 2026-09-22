[← All rounds](../../../README.md)

# Round 1: Wan 2.2 A14B at fal's 480p settings on one A100 (Sep 22, 2026)

Status: run complete, all clips copied and checksum-verified, pod stopped, blind review scored. Plan and reasons: [`PLAN.md`](PLAN.md), committed to git before the session ran. Exact tables regenerated from the raw logs: [`raw/REPORT.md`](raw/REPORT.md).

## Watch two of the clips

Fal-matched setting, 27 steps (median prompt):

<video src="clips/A2_median.mp4" controls width="420"></video>

Same prompt and seed, only 15 steps (cheapest, ranked worst by blind review — see section 6):

<video src="clips/B2_median_15steps.mp4" controls width="420"></video>

All 7 clips are in [`clips/`](clips/). GitHub plays them inline when you open the file, even if the preview above doesn't render in your view.

## 1. Summary

- On one A100-SXM 80GB at $1.69/h (+ about $0.025/h disk), generating a 5.06 s, 832x480 clip with fal's default 27 steps costs **about $0.27 and takes about 9.4 minutes**. That is **$0.053 per video-second**, 1.33 times fal's price of $0.04 for the same tier.
- Counting the whole session (download, setup, warm-up, idle), the cost was **$0.072 per video-second, 1.8 times fal** (real RunPod billing: $2.159 GPU + $0.037 storage = $2.196; close to the $2.32 estimate in the first draft of this report). This is not a steady-state price.
- Speed hardly changed with the prompt (short, median, long-and-truncated, non-English: 552 to 568 s, spread 1.2%). The cost depends on the hardware and the settings, not on the prompt.
- Fewer steps cut the cost: 20 steps is 25% cheaper ($0.040/s, about fal's price) and 15 steps is 41% cheaper ($0.032/s, below fal's price). **A blind quality review ranked the clips in the same order as step count** (27 best, then 20, then 15) -- see section 6.
- Six of six clips were delivered and passed the automated checks. There were no failures, but six runs cannot establish a failure rate.
- Prompt-match, on a blind read of the video alone (no prompt or settings visible while scoring): 2 of 4 clips judged pass or partial (the short prompt was scored a clear fail; the median prompt's rating was not filled in, see section 6).

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 2.2 T2V-A14B (diffusers), bf16, CPU offload |
| Request (fal defaults) | 832x480, 81 frames at 16 fps (5.0625 s), guidance 3.5 / 4.0, shift 5, no negative prompt. Frame interpolation not included |
| Hardware | RunPod A100-SXM4-80GB, driver 580.126.16, CUDA 13.0, 128 cores, US-MD-1. PyTorch 2.8.0+cu128 |
| Prices used | $1.69/h GPU and $0.09/GB disk (read as per month, about $0.025/h for 200 GB), taken from the hosting provider's panel. The disk unit is assumed |
| Prompts | Four real prompts from awesomevideoprompts.com, chosen by real token count: short (44 tokens), median (387), long (854, truncated at 512), non-English (393) |
| Jobs | Warm-up (4 steps, excluded), then A1-A4 at 27 steps, then the median prompt again at 20 and 15 steps with the same seed |

## 3. Results

| Job | Steps | Tokens | Generate s | Encode s | GPU busy | Cost per clip | Cost per video-second |
|---|---|---|---|---|---|---|---|
| A1 short | 27 | 44 | 551.7 | 3.1 | 92.0% | $0.264 | $0.0522 |
| A2 median | 27 | 387 | 568.4 | 3.4 | 89.4% | $0.272 | $0.0538 |
| A3 long (truncated) | 27 | 854 | 565.7 | 4.1 | 89.7% | $0.271 | $0.0536 |
| A4 non-English | 27 | 393 | 558.4 | 2.9 | 90.7% | $0.267 | $0.0528 |
| B1 median | 20 | 387 | 424.1 | 3.1 | 89.2% | $0.204 | $0.0402 |
| B2 median | 15 | 387 | 333.9 | 2.9 | 85.7% | $0.160 | $0.0317 |

Fal-matched runs (A1-A4, n = 4): mean 564.4 s, median 565.5 s, range 554.8 to 571.8 s, standard deviation 6.8 s (1.2%).
Peak VRAM 32.5 GB on every job. Every clip passed the automated gate (81 frames, correct size, not black, not frozen).

## 4. Cost, three ways

| View | Cost per video-second | Versus fal's $0.04 |
|---|---|---|
| Busy-queue cost at 100% utilization (A1-A4) | $0.0531 | 1.33x |
| Same, if the GPU is busy 75% of the time | $0.0708 | 1.77x |
| Same, at 50% | $0.1062 | 2.66x |
| Same, at 25% | $0.2125 | 5.31x |
| All-in for this session (pod on about 81 min, $2.32, 6 clips) | $0.0762 | 1.9x |
| Setup overhead spread over N clips of the same kind: N=10 / 50 / 200 | $0.0704 / $0.0566 / $0.0540 | 1.8x / 1.4x / 1.35x |

Fal's price for the same clip is $0.2025 (5.0625 s at $0.04). Ours at 27 steps is $0.269 busy-only.

What it takes to match fal at 27 steps: about 25% lower cost per second, either a GPU hour 25% cheaper (about $1.29/h including disk) or about 1.33 times faster generation. Fal's price also includes frame interpolation that we did not run, so the real gap is somewhat larger than shown.

## 5. Steps ladder (same prompt and seed)

| Steps | Generate s | Time versus 27 steps | Cost per video-second |
|---|---|---|---|
| 27 | 568.4 | 1.00x | $0.0538 |
| 20 | 424.1 | 0.75x | $0.0402 |
| 15 | 333.9 | 0.59x | $0.0317 |

Time falls roughly in proportion to steps. The quality effect is unknown until the blind review is scored.

## 6. Blind review results (single reviewer)

The reviewer scored 6 clips with random names, no prompt or step count visible, then the key was opened.

**Prompt match** (does the 5.06 s clip match its prompt's content? duration mismatches were explicitly excluded from scoring, since prompts were written for other tools that allow longer clips):

| Clip | Job | Stratum | prompt_match | Notes |
|---|---|---|---|---|
| S1 | A4 non-English | non_english | partial | "a bit weird" |
| S2 | A3 long (truncated) | long | pass | "clean" |
| S3 | A1 short | short | **fail** | "that's a camera not film" |
| B3 | A2 median, 27 steps | median | not scored | field left blank |

2 of 4 strata prompts (A1-A4) were judged pass or partial. A1 (short prompt) failed review even though it ran at the same 27-step setting as the others, so the automated gate passing is not the same as the content being right. A2's rating is missing, so it counts as not-accepted in that tally; it is not the same as a confirmed fail.

**Steps ladder** (same prompt and seed, unlabeled, ranked 1 = best):

| Clip | Steps | Rank | Motion (relative) |
|---|---|---|---|
| B3 = A2 | 27 | **1 (best)** | more |
| B1 | 20 | 2 | same |
| B2 | 15 | **3 (worst)** | same |

The ranking is monotonic with step count: more steps ranked better, in that order, every time. With one reviewer and one prompt this is a single data point, not a statistically supported result, but it points the same direction the step count would predict, so the cost saving from fewer steps likely comes with a real, human-visible quality cost. `prompt_match` was left blank for all three ladder clips, so the review does not say whether cutting steps also breaks prompt adherence, only relative preference and perceived motion.

**Caution on the tally above:** "2 of 4" mixes a real fail (S3) with a missing rating (A2). Do not read it as a 50% pass rate; read the two rows separately.

## 7. Real cost vs. computed estimate

| | GPU | Storage | Total | $/video-second (6 clips, 30.375 s) | vs fal $0.04 |
|---|---|---|---|---|---|
| Computed estimate (pod-on time x rate) | -- | -- | $2.32 | $0.0762 | 1.9x |
| **Actual RunPod billing** | $2.159 | $0.037 | **$2.196** | **$0.0723** | **1.81x** |

The two agree within 5%, so the timing-based cost model in this benchmark is reasonably trustworthy. The real numbers also let us check the assumed disk rate: $0.037 over an implied 76.7 minutes of pod life is about $0.029/h, close to the $0.025/h assumed in the report above (about 15% higher). Section 4's "busy-queue" ratio (1.33x, using only generation time, not full pod time) is unaffected by this reconciliation.

## 8. Agreement with the earlier pilot

The earlier single 480p run (second pod, $1.618/h) took 582 s. This session's mean is 564 s, 3% faster, with a different PyTorch version and host. The two are consistent, and the pilot's first step was slow because it had no warm-up.

## 9. What happened during the session

- Weights download took 709.7 s (11.8 min), longer than the 8 min planned. Model load 79.8 s, warm-up 145.4 s (includes one-time loading).
- The pre-flight check passed (bf16 matmul 243 TFLOPS, weights cache on local disk). The audit before the run found that `/workspace` on this pod is a network volume, so the weights were kept on the local 200 GB disk.
- The GPU ran under a software power cap on every job (throttle code 0x4): mean clock about 1,305 MHz of a 1,410 MHz maximum. The shared host was busy (load average 46 to 67 at job starts).
- The first launch command failed harmlessly (a missing output folder), and it was relaunched. Nothing ran unguarded.
- The independent stop guard (hard stop at 03:07) was not needed. The pull script copied everything with checksums and stopped the pod at about 03:05. `runpodctl` printed a config-file warning but reported the pod stopped, and a connection test afterwards confirms it is stopped.
- Total pod time about 81 minutes, computed cost about $2.32, under the $2.50 cap. This is computed from rates and timings, **not yet reconciled with the RunPod billing page**.
- Two review-set flaws were found and fixed after the run and before scoring (a clip shown twice, and file sizes that revealed the step count). See PLAN.md, section 13, rows 22 and 23.
- Not copied from the pod: its text logs (`session.log`, `guard.log`, `pip.log`). The per-job records and telemetry, which the numbers come from, were copied.

## 10. Limits of these numbers

1. One session, one host, four comparable runs. No day-to-day or host-to-host variation and no confidence intervals.
2. Cost-only comparison with fal. We did not run fal, so we know nothing about their hardware, speed or quality.
3. Fal's default frame interpolation and delivery costs are not included.
4. The rates are as read from the hosting provider's panel. The disk unit is assumed.
5. The software (PyTorch 2.8) and the power-capped, shared host differ from the pilot, and cannot be separated from the GPU effect in one session.
6. Quality is unreviewed. The blind review is one informal reviewer and cannot support a quality claim against fal.
7. A100 only. Nothing here transfers to other GPUs, including the "high-end GPU" bet.

## 11. Still to do

1. Done: blind scoring, unblinding, and billing reconciliation (sections 6-7).
2. Confirm in the RunPod panel that the pod shows as stopped.
3. Decide on the next session (PLAN.md, section 12): 720p and 580p, a second day or host, interpolation. If steps are lowered in production, get at least a second reviewer's opinion on the 15/20/27-step tradeoff before relying on it.
4. Optional: re-score the median prompt's `prompt_match` (left blank) to complete the strata tally.

## 12. Files

- `REPORT.md`: tables generated from the raw logs (`python3 benchmarks/report_session.py benchmarks/rounds/round1-wan22-a14b-480p/raw --gpu-usd-h 1.69 --disk-usd-h 0.025 --copy-s 90`).
- `jobs.jsonl`, `preflight.json`, `session.json`: raw records.
- `*.mp4`: the seven clips (warm-up plus six jobs). Each was verified by md5 when copied, and `jobs.jsonl` holds each file's sha256 as recorded on the pod.
- `review/review_scores.csv`, `review/review_prompts.md`, `review/_key/review_key.json`: the completed blind review and its answer key. The padded, renamed video copies used for scoring are not kept; the clips in `clips/` are the same content.
