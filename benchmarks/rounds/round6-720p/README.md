[← All rounds](../../../README.md)

# Round 6: Wan 2.2 A14B at fal's 720p settings on one A100 (Sep 30 - Oct 1, 2026)

Status: partial. The A-strata block (4 clips, same prompts/seeds as round 1) is complete, checksum-verified, and the pod stopped. The step-count ladder (B1 at 20 steps, B2 at 15 steps) was not completed -- see section 5. Plan and reasons: [`PLAN.md`](PLAN.md), committed to git before the session ran.

## Watch two of the clips

Fal-matched setting, 27 steps (median prompt), at 720p:

<video src="clips/A2_median.mp4" controls width="420"></video>

Same prompt and seed at 480p, from round 1, for comparison:

<video src="../round1-wan22-a14b-480p/clips/A2_median.mp4" controls width="420"></video>

All 5 clips collected here (warm-up plus the 4 A-strata jobs) are in [`clips/`](clips/).

## 1. Summary

- At 720p on one A100-SXM 80GB, generating a 5.06 s, 1280x720 clip with fal's default 27 steps costs **about $0.88 and takes about 32 minutes**, busy-only. That is **about $0.174 per video-second, 2.1-2.2x fal's $0.08 price for the same tier** -- a materially worse ratio than round 1 found at 480p (1.33x).
- 720p generation took **3.4-3.5x as long as the same prompt at 480p** (round 1), while the pixel count only grew 2.3x. Cost does not scale linearly with resolution on this pipeline; it gets proportionally worse per pixel as resolution rises.
- Speed was again insensitive to prompt content: the four A-strata clips ran 1,860.6 to 1,954.5 s generate time (spread 2.2%, similar to round 1's 1.2% at 480p).
- All 4 clips were delivered and passed the automated gate (81 frames, correct 1280x720 shape, not black, not frozen).
- No blind quality review has been done on these clips yet (round 1's single-reviewer process was planned but not reached before the session's budget/time ran out).
- The step-count ladder (B1, B2) and frame interpolation (round 5) are **not** in this round -- see section 5.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 2.2 T2V-A14B (diffusers), bf16, CPU offload |
| Request (fal defaults at 720p) | 1280x720, 81 frames at 16 fps (5.0625 s), guidance 3.5 / 4.0, shift 5, no negative prompt. Frame interpolation not included |
| Hardware | RunPod A100-SXM4-80GB. A1 ran on one physical GPU (500 W power limit, GPU-1778c0be...); A2-A4 ran on a second physical GPU on a different pod (400 W power limit, GPU-155a8c86...), after the first pod's container became unreachable mid-session (section 5) |
| Prices used | $1.618/h GPU, $0.02778/h disk (same assumed rate as round 1), fal 720p $0.08/video-second (from `fal_wan22_config.md`) |
| Prompts | Round 1's exact four prompts and seeds, reused for direct comparison: short (44 tokens), median (387), long (854, truncated at 512), non-English (393) |
| Jobs run | Warm-up (4 steps, excluded, run twice -- once per pod), then A1-A4 at 27 steps. B1/B2 (20/15 steps) were not run |

## 3. Results

| Job | Steps | Tokens | Generate s | Encode s | Busy $ | $/video-s | vs fal $0.08 | GPU util | Power mean W | SM clock mean MHz |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 short | 27 | 44 | 1860.6 | 3.7 | $0.852 | $0.1684 | 2.10x | 96.9% | 479.3 | 1383 |
| A2 median | 27 | 387 | 1924.7 | 2.6 | $0.881 | $0.1740 | 2.18x | 97.9% | 391.2 | 1316 |
| A3 long (truncated) | 27 | 854 | 1940.6 | 4.2 | $0.889 | $0.1756 | 2.20x | 97.1% | 387.3 | 1312 |
| A4 non-English | 27 | 393 | 1954.5 | 3.0 | $0.895 | $0.1768 | 2.21x | 96.4% | 386.0 | 1311 |

A-strata (n = 4): mean 1,920.1 s, median 1,932.7 s, range 1,860.6-1,954.5 s, standard deviation 41.5 s (2.2%).
Peak VRAM 37.5 GB on every job (vs 32.5 GB at 480p -- higher resolution needs more activation memory even with the same model). Every clip passed the automated gate (81 frames, correct 1280x720 shape, not black, not frozen).

A1 ran faster and drew more power than A2-A4 despite being the same job type, because it ran on a different physical GPU with a 500 W power limit (vs the usual 400 W) -- the same hardware-lottery effect round 4 measured directly, visible again here as a side effect rather than the thing being tested.

## 4. 480p vs 720p, same prompts and seeds

| Job | 480p generate s (round 1) | 720p generate s (this round) | Ratio |
|---|---|---|---|
| A1 short | 551.7 | 1860.6 | 3.37x |
| A2 median | 568.4 | 1924.7 | 3.39x |
| A3 long | 565.7 | 1940.6 | 3.43x |
| A4 non-English | 558.4 | 1954.5 | 3.50x |

Pixel count at 720p is 1280x720 / 832x480 = 2.31x that of 480p. Generation time grew 3.37-3.50x -- noticeably more than proportional to pixel count. Fal's own price follows the same pattern in the other direction: $0.08 at 720p is 2x its $0.04 480p price, not 2.3x, so fal's pricing scales *better* than our measured generation time does. That is the direct cause of the worse cost ratio in section 1 (2.1-2.2x fal at 720p, vs 1.33x at 480p): our cost grows faster than fal's price does as resolution rises.

## 5. What happened during the session (the incomplete part)

This round needed two pod attempts and surfaced two real bugs, neither of which affects the numbers in sections 3-4 (both affected jobs were re-run cleanly and verified):

1. **First pod (`runpod7`)**: warm-up and A1 completed normally and were verified (1,860.6 s, matching this round's pilot estimate of 1,961 s within a few percent). The pod's container then became unreachable before A2 finished. Its text logs (`guard.log`, `session.log`) were not pulled before the container was gone, so the exact cause could not be confirmed; the timing is consistent with the independent stop-guard's idle-crash detection firing after the generation process stopped responding. A log-pulling gap this exposed was fixed in `pull_session.py` (every poll now also copies `guard.log`, `session.log`, `pip.log`, not just at the end) so a repeat would leave evidence.
2. **Second pod (`runpod8`)**: verified (GPU, CUDA, disk, a timed matmul) before use. A2 completed and was copied. The resume attempt for A3-B2 was then killed by `wan22_a14b_session.py`'s own internal watchdog, which defaults to a 58-minute total measurement window -- a default sized for round 1's one-hour, six-short-job session, never overridden for this round's five-job, ~2.5-hour 720p resume. It fired 2 steps before A3 finished. The stale completion marker it left was cleared and the remaining jobs were relaunched directly with an explicit, correctly-sized window. A3 and A4 then completed and were copied and verified.
3. The pod's independent stop-guard had already been armed (before bug 2) with a hard deadline sized for the originally-planned five-job resume. Since restarting that guard would have meant stopping and replacing the one independent safety process meant to prevent runaway billing -- the opposite of what it exists for -- the deadline was left as armed rather than extended. B1 was mid-generation (step ~14-20 of 20) when that deadline fired; the guard stopped the pod cleanly, confirmed by a direct connectivity check afterward (`container not found`). B2 never started.

Net effect: the A-strata block (this round's primary comparison with round 1) is complete and clean. The step-count ladder is not, and needs a separate pod session, sized correctly for just those two jobs (about 44 minutes of generation: B1 ~24 min, B2 ~19 min, plus one warm-up).

## 6. Limits of these numbers

1. A1 and A2-A4 ran on two different physical GPUs (different power limits), not a single consistent host -- round 4 shows this kind of difference is real but small for speed, and section 3 shows the same pattern here.
2. No blind quality review yet. Round 1's content-match and step-ladder review cannot be extended to 720p until B1/B2 exist and a reviewer scores all three alongside A1-A4.
3. Cost-only comparison with fal; we did not run fal, so we know nothing about their hardware, speed, or quality at 720p.
4. Fal's default frame interpolation and delivery costs are not included (round 5 measures interpolation separately, also not yet complete).
5. The $1.618/h GPU rate and $0.02778/h disk rate are the planning-time assumed rates (same as round 1), not yet reconciled against actual RunPod billing for either pod used in this round.
6. Four comparable runs on the completed side, no repeats, no confidence intervals -- same limitation as every prior round.

## 7. Still to do

1. A separate pod session for B1 (20 steps) and B2 (15 steps) at 720p, sized correctly this time (explicit `--window-min` covering just those two jobs, well inside the guard's hard deadline).
2. Blind review of all 7 clips (A1-A4, B1, B2, plus round 1's 480p equivalents) once B1/B2 exist.
3. Reconcile the computed cost above against actual RunPod billing for both pods (see round 1, section 7, for the method).
4. Round 5 (frame interpolation) still needs its own pod time; it was planned to piggyback on this round's session but that session ran out of time first.

## 8. Files

- `jobs.jsonl`, `preflight.json`: raw records (one combined file across both pod attempts; two `W0_warmup` rows reflect the two separate pod sessions).
- `pod_logs/`: `guard.log`, `session.log` pulled from the second pod (best-effort; the first pod's logs were lost with its container, see section 5).
- `*.mp4` in `clips/`: warm-up plus the 4 A-strata jobs. Each was verified by md5 when copied, and `jobs.jsonl` holds each file's sha256 as recorded on the pod.
- `raw/`: the same files as pulled, kept separately from the curated `clips/` copies.
