# Round 1 test design: Wan 2.2 A14B at fal's 480p settings on one A100

Status: session run and reviewed. All six jobs delivered, blind review scored and unblinded, billing reconciled against the hosting provider's panel ($2.196 actual vs. a $2.32 estimate). Sections 1-13 are the design as frozen in git before the session ran (job list sha256 `b19fd5f5902a13ebba3207dc3e2455e72ac817441600e79efe0ac736323db21d`). Section 14 records what happened operationally. Full results, the blind review outcome and the billing reconciliation are in [`README.md`](README.md). Figures marked "pilot" come from single, unrepeated runs recorded in `benchmarks/rounds/round0-pilots/`.

## 0. Summary

- **Question:** what does one second of Wan 2.2 A14B video cost on one A100 80GB, for the same request fal.ai sells at 480p, and how much cheaper are fewer diffusion steps?
- **Test:** one session of about 69 minutes, budget capped at $2.50. Four prompts (short, median, long, non-English) at fal's default 27 steps, plus the median prompt again at 20 and 15 steps. Clips are scored with a blind review (no prompt or setting visible while scoring).
- **Scope:** a single one-hour session on one GPU, prioritizing an early end-to-end cost measurement over broad coverage. At 480p one clip takes about 10 minutes, so an hour holds about six clips.
- **What it cannot show:** quality compared with fal or other models, behavior under sustained load, day-to-day variation, or a reliable failure rate. Section 8 lists this in full.
- **How it maps to project requirements:** section 2, including deliberate deviations and why.

## 1. Purpose and context

This project measures whether hosting open-weights video models on rented GPUs can undercut API vendors such as fal.ai, in support of finding where self-hosted generation is profitable. The needed output is a trustworthy **cost per generated video-second**, comparable with the price fal charges for the same request.

This document covers the first end-to-end measurement on one A100 pod: a defensible first number, and a method that reveals its own weaknesses before more budget is spent on it.

## 2. Requirements addressed by this test

Each row is a requirement stated for this project, with how this test does or does not address it.

| # | Requirement | Status | How this test handles it, and why |
|---|---|---|---|
| 1 | Verify published measurements of running open-weights models: hardware cost, batch throughput, interactive latency, optimal iterations, additional pipelines, to establish the actual cost to run. | **Partly** | **Hardware cost:** covered (measured seconds x hourly rate, with disk shown separately). **Optimal iterations:** covered by the 27 / 20 / 15 step ladder. **Interactive latency:** per-clip generation time is recorded, but no latency target is tested (later dropped as a requirement). **Batch throughput:** not covered (single request at a time). **Additional pipelines:** not covered; fal's default frame interpolation is not implemented, so this cost is understated versus fal's request. **Published measurements:** this test does not verify any specific published Wan 2.2 timing claim, since none had been collected yet. |
| 2 | Match fal.ai's API configuration: the same deploy and generation settings as the API request, to establish actual pricing to charge. | **Covered, with one gap** | Every generation parameter is set to fal's published default for `fal-ai/wan/v2.2-a14b/text-to-video` (source and date in section 4; `benchmarks/fal_wan22_config.md`). Gap: fal's server-side details (hardware, what its `acceleration: regular` flag does, interpolation) are not visible from outside. Only cost is compared. |
| 3 | Cross-model quality scoring is not required yet. | **Covered** | No VBench and no cross-model scoring. The only quality step is a small blind review within this test's own clips (steps ladder), added because "optimal iterations" is meaningless without checking that fewer steps does not visibly break the video. |
| 4 | Use realistic prompts from real video-prompt sources rather than toy examples. | **Covered** | Prompts come from a crawl of a public prompt-sharing site (6,314 unique, 5,859 usable without reference images). They are used as written. Four are chosen by real token count so the test hits the cases that matter (section 5.2). |
| 5 | Start with a basic GPU, a limited daily time budget, and end-to-end measurements before optimizing. | **Covered** | One A100 pod, one session of about an hour, hard stop on every session. No optimization beyond the steps ladder. |
| 6 | Each account/pod used for testing is tracked individually for cost. | **Covered** | This test's cost is reconciled against its own hosting-provider billing page. |
| 7 | Assume 100% utilization; feed continuous requests to saturate the GPU. | **Partly / Deviates** | Jobs run back to back with no idle gaps, so the headline number is the cost at full utilization. It is **not** an open-ended run: a fixed list of six jobs, because one 480p clip takes about 10 minutes and this test was limited to an hour. GPU utilization is measured and reported, not assumed. The same cost is also shown at 75 / 50 / 25% utilization so a reader can see how quickly the advantage disappears. |
| 8 | Track published vs. measured values on a shared reference sheet. | **Partly** | The report script produces measured values with their definitions, ready to enter into any such sheet. Entry itself, and adding published values, is outside this test. |
| 9 | 5 seconds as a base clip length; promote per-model maximum durations later (5 s for Wan 2.2). | **Covered** | 81 frames at 16 fps is 5.0625 s, which is fal's default. As far as known this is also the length the model was trained for, but that was not verified here. Fal's API accepts up to 161 frames (about 10 s), so the 5-second figure describes a typical/native length, not an API limit. Longer durations are a later phase. |
| 10 | Track failure rates and generation-speed variability. | **Partly** | Every failure, skip and outlier is logged and reported, and speed spread is computed. With four runs at the same settings, no meaningful failure rate can be stated. Fixed-shape diffusion is compute-bound, so speed varies little between prompts (pilot: GPU 88-97% busy). The variability that matters — host and time of day — needs more than one session (later phase). |
| 11 | Hosting is expected to be most profitable at high utilization with a high-end GPU and a complex generation pipeline. | **Not covered (by design)** | This test's scope is a basic GPU. It says nothing about higher-end GPU classes and must not be scaled linearly to them. |
| 12 | A 15-second interactive latency target is not required for now; being less price-competitive on latency than the fastest API tiers is acceptable. | **Not applicable here** | That requirement concerned a different model family. Fal also sells a separate Wan 2.2 A14B "turbo" endpoint at a flat price per video at 720p, not matched by this test (its pipeline is not published), and that is a difference reviewers should know about. |
| 13 | Find the GPU/server configuration with the best balance: not too slow, and cost per generation no higher than competitors. | **Partly** | This test gives cost per clip and per second next to fal's 480p price. The A100 is one candidate; no other GPU or provider is tested here. |

## 3. Constraints and configuration log

| Constraint or decision | Type | Reason |
|---|---|---|
| Use the crawled prompts exactly as written. | Project decision | Realism (requirement 4). Long prompts are truncated by the model's text encoder, and that is recorded, not fixed. |
| Model under test: Wan 2.2 T2V-A14B at fal's standard settings, not the smaller 5B model used in earlier pilots. | Project decision | The 5B model is a different model from the one fal's standard endpoint serves. |
| Cost uses the hosting provider's billing-page rate rather than an earlier quoted rate, once the two diverged. | Configuration correction | The billing page is the authoritative source. |
| Hard stop on every session; stop the pod once a session is idle. | Project decision | Idle pod time was previously the largest cost driver in this project. |
| Limit this test to one hour. | Project decision | Budget. |
| Single reviewer for the blind review. | Project decision | No second reviewer available for this test. |
| No API-purchased comparison clips from fal in this test. | Project decision | No budget allocated for that yet, so no paired quality comparison against fal is possible here. |
| Other model families (H3/FastH3, LTX) not included in this test. | Project decision | Availability and access not established for this test. |
| Test at 480p, not 720p. | Design choice, see section 5.1 | |

## 4. Inputs and evidence this test starts from

| Input | Value | Source and date |
|---|---|---|
| GPU and rate | RunPod A100-SXM4-80GB, $1.69/h for the pod used in this session. An earlier pod on the same project used $1.618/h; the pilot costs in this document use that earlier rate. | Hosting provider panel |
| Disk rate | $0.09/GB, read as per month, so 200 GB is about $0.025/h. **The unit is assumed** and the raw session file still holds an earlier placeholder default until the report script overrides it. | Hosting provider panel; unit to be confirmed |
| fal price | Wan 2.2 A14B standard: $0.04 / $0.06 / $0.08 per video-second at 480p / 580p / 720p, counted at 16 fps | fal model page, read close to this test's date; no promotion was noted on the page at that time |
| fal defaults | 81 frames, 16 fps, 27 steps, guidance 3.5 / 4.0, shift 5, FILM interpolation x1, empty negative prompt | fal's published API schema (`benchmarks/fal_wan22_config.md`) |
| Pilot: Wan 2.2 5B, 1280x704, 3.04 s, 50 steps | 187 s on one A100 pod, 204 s on another A100 pod of a different form factor | `benchmarks/rounds/round0-pilots/raw/SUMMARY.md` |
| Pilot: A14B 720p, 81 frames, 27 steps | 1,961 s; $0.881 per clip; $0.174 per video-second; GPU 96.6% busy; peak VRAM 37.5 GB | same; single run |
| Pilot: A14B 480p, 81 frames, 27 steps | 582 s; $0.261 per clip; $0.0517 per video-second; GPU 88.0% busy; peak VRAM 32.5 GB; first step 48 s versus about 18 s later | same; single run |
| Prompt set | 6,314 unique crawled prompts, 5,859 without reference images; about 74% originally written for a different (non-Wan) model | `benchmarks/prompts/prompts.jsonl` (not committed; regenerate with `crawl_prompts.py`) |
| Token statistics (real umt5 tokenizer) | usable prompts: median 374 tokens, p90 1,068; **36.5% exceed the 512-token limit**; non-English prompts (922 of them): median 709 tokens, 63.8% over 512 | computed from the prompt set with the tokenizer bundled in the Wan 2.2 model repository |
| Cost comparison reference: LTX-2.5 on a different GPU class | Reported queue-only cost of $0.00146 per video-second, versus $0.0137 for the whole experiment once failed setup attempts and overhead are included (about 9x) | a separate benchmark bundle in this project's broader body of work |

Pilot figures were single runs, not designed as measurements. They were used only to size this test.

## 5. Test design and the reasons for each choice

### 5.1 Model and settings

Wan 2.2 T2V-A14B, 832x480, 81 frames at 16 fps (5.0625 s), 27 steps, guidance 3.5 / 4.0, shift 5, empty negative prompt, bf16 with CPU offload, no interpolation.

Reasons:
- Same request as fal's standard endpoint (requirement 2).
- **480p, not 720p:** one 720p clip takes about 33 minutes (pilot), so an hour would hold about one clip, too few for a within-session comparison. At 480p a clip takes about 10 minutes and fal has a priced 480p tier ($0.04/s). The single 720p pilot stays a pilot, not part of this test.
- **CPU offload:** two 14B experts plus the text encoder do not all fit in 80 GB with activations. The pilot ran this way with peak VRAM of 32-38 GB; the resulting weight-swapping cost is part of the real cost of this setup, not an artifact to remove.

### 5.2 Prompt strata (frozen)

Prompts are chosen by **real token count**, using a fixed random seed.

| Job | Stratum | Real tokens | Steps | Seed | Source prompt |
|---|---|---|---|---|---|
| W0 (warm-up) | short | 44 | 4 | 1 | same as A1 |
| A1 | short (30 words) | 44 | 27 | 4200 | https://awesomevideoprompts.com/en/prompts/2041132845834579975-arri-alexa-cinematic |
| A2 | median (254 words) | 387 | 27 | 4201 | https://awesomevideoprompts.com/en/prompts/2059451654106222828-eid-ul-adha-village-mosque-dawn |
| A3 | long (436 words, truncated) | 861 | 27 | 4202 | https://awesomevideoprompts.com/en/prompts/2094688480744083924-pov-your-instant-noodles-just-entered-ac |
| A4 | non-English (mostly Chinese) | 393 | 27 | 4203 | https://awesomevideoprompts.com/en/prompts/2058202318026240180-90s-anime-cooking-elf |
| B1 | same as A2 | 387 | 20 | 4201 | same as A2 |
| B2 | same as A2 | 387 | 15 | 4201 | same as A2 |

Reasons:
- **Short:** a large share of the prompt set is short (680 usable prompts under 30 words).
- **Long:** 36.5% of prompts exceed the encoder's token limit, so truncation is the normal case, not a corner case.
- **Non-English at a length under the limit:** isolates the language effect from truncation.
- **B1 and B2 reuse A2's prompt and seed:** any difference between them is due to the step count alone.
- Total expected measured time: 2,980 s (49.7 min). The job list file is frozen by its sha256 (`b19fd5f5902a13ebba3207dc3e2455e72ac817441600e79efe0ac736323db21d`) and must not change after the first result is seen.

### 5.3 Warm-up

A 4-step job runs first and is excluded from queue cost (but counted in all-in cost). In the pilot, the first step of a 480p run took 48 s versus about 18 s later; the warm-up absorbs that. It also exercises the whole code path (export, quality gate, telemetry), so a defect surfaces within minutes rather than after the full measured window.

### 5.4 Sample size and statistics

Four fixed-shape runs at 27 steps in one session. This is intentionally small:
- Fixed-shape diffusion is compute-bound, so speed hardly depends on the prompt (pilot: GPU 88-97% busy). Speed differences between the four prompts are still informative; a tight spread confirms the expectation.
- No confidence intervals are claimed. Results are labelled single-session, single-host.

### 5.5 Blind steps ladder

The median prompt is rendered at 27, 20 and 15 steps with the same seed. The three clips are scored with random names and no step count visible, then the answer key is opened. Fields: `prompt_match` (pass / partial / fail), free-text notes on artifacts, and motion recorded as "more / same / less", never "better". The other three strata clips (short, long, non-English) are scored only on `prompt_match`. The median 27-step clip is shown once, inside the steps set, and its `prompt_match` also counts for the median stratum, so no clip is shown twice. All review copies are padded to one identical byte size so file size cannot reveal the step count.

Reason: requirement 1's "optimal iterations" is meaningless unless fewer steps is checked for a visible quality effect. This gives a cost saving and a quality impression together. A single reviewer familiar with the project's goals is a weak instrument; the result is informal by design.

### 5.6 What is compared with fal, and how

Cost only: this test's cost per delivered video-second at 480p against fal's $0.04. No claim about equal quality. The ratio is a **lower bound** on the true gap, since fal's default interpolation and delivery are not in this test's number.

## 6. Procedure, go / no-go rules and safeguards

1. Confirm the pod is reachable before starting.
2. Upload the session files with checksums verified, then start `run_hour_session.sh`, which **arms the independent stop guard first**.
3. **Preflight (automatic):** CUDA available, bf16 matmul at least 150 TFLOPS after warm-up, at least 75 GB VRAM, at least 15 GB free disk, and the weights cache not on a network filesystem. **If any check fails, nothing else runs and the pod is stopped.** A faulty GPU can otherwise produce hours of billing with no usable compute.
4. Watch the log as jobs run. **If the first 27-step job exceeds 840 s (1.5x expected), pause and report** instead of spending the whole measurement window on a slower-than-expected host.
5. When the session-complete marker appears, copy results off the pod and verify every file's checksum. Stop the pod once the copy is verified.
6. Build the blind review set. Score it without opening the answer key.
7. Run the report script to compute every number from the raw logs. Reconcile the pod's cost against the hosting provider's billing page (billing data can lag by about an hour).

**Independent guard (`pod_guard.sh`):** stops the pod at a hard deadline (75 min after it starts), 15 min after the session finishes (time to copy results), or 20 min after the session process disappears without finishing. It runs independently of the benchmark code, so a stuck or crashed session cannot leave the pod billing indefinitely. It was tested locally against a stand-in for the pod-stop command, covering four cases: hard deadline, done-plus-grace, crash, and no false stop while the session is still running.

**Verification status before the run:** the session runner (`wan22_a14b_session.py`) had been syntax-checked but not exercised against a live model or GPU before this session. The guard had not yet stopped a real pod in this exact form, although the underlying stop command had worked in an earlier, unrelated session.

## 7. Metrics and definitions

| Metric | Definition |
|---|---|
| Delivered seconds | frames / fps = 81 / 16 = 5.0625 s per clip, never rounded to 5 |
| Busy-queue cost | (GPU + disk $/h) x (generate + encode seconds) / delivered seconds |
| Utilization-adjusted cost | busy-queue cost / utilization, at 100 / 75 / 50 / 25% |
| All-in cost | pod-on time x rate / delivered seconds. Pod-on time = container uptime when the run starts + session duration + copy time. Also shown amortized over N = 4, 10, 50, 200 clips |
| Steps ladder | time and cost at 27 / 20 / 15 steps, with the blind ranking |
| Telemetry per job | GPU utilization, power, SM clock (mean, min), temperature, throttle reasons, host load, peak VRAM |
| Automated gate | file decodes; frame count and size correct; not black; not frozen |

A "delivered" clip is one that passes the automated gate. Failed and skipped jobs stay in the tables and their time stays in the cost.

## 8. Budget for this session

| Item | Time | Cost (estimate) |
|---|---|---|
| Pod boot until connected | about 3 min | $0.08 |
| Install; download 139 GB if weights are missing | about 2 + 8 min | $0.27 |
| Model load and warm-up | about 3 min | $0.08 |
| Measured jobs | about 50 min | $1.35 |
| Copy results | about 3 min | $0.08 |
| **Total** | **about 69 min (about 59 if weights are already present)** | **about $1.9 (about $1.6)** |

Ceiling: guard hard stop at 75 min after start plus boot time, so at most about $2.2. Session cap $2.50.

## 9. Limitations and threats to validity

1. **Single session, single host, four comparable runs.** No day-to-day or host-to-host variation, no confidence intervals.
2. **Cost-only comparison with fal.** No fal clips run for this test, so no statement about equal quality. Fal's hardware and pipeline are unknown from outside.
3. **Interpolation excluded.** Fal's default output includes FILM interpolation. This test's cost is therefore understated relative to fal's request.
4. **Blind review is weak:** one reviewer, informal, seven clips shown, no inter-rater agreement. The reviewer is familiar with the project's goals.
5. **Disk price assumed.** If disk cost turns out to be already included in the GPU rate, this test's cost is about 1.7% lower.
6. **Prompts were written for other models.** About 74% were written for a different, non-Wan model, and many ask for audio, 4K or longer clips than Wan can produce. This test measures cost, not how faithfully Wan follows the prompt's every request.
7. **Fal's promotion status** for this endpoint was not stated on the page read for this test; prices may change.
8. **A100 only.** Nothing here transfers to other GPUs. The "high-end GPU" hypothesis (requirement 11) is untested.
9. **The session runner was unverified on real hardware before this run** (section 6).
10. **Time-limited, fixed job list, not open-ended saturation.** Requirement 7's "continuous requests" is approximated here by a fixed back-to-back list.
11. **Software stack differs from the pilots** (a newer PyTorch/CUDA build than the pilots used), and the shared host was busy (load average about 22-32 on 128 cores when checked). Both are recorded in the telemetry, and neither can be separated from GPU effects within one session.

## 10. Files and how to verify

| File | Purpose |
|---|---|
| `benchmarks/prompts/prompts.jsonl` | crawled prompt set (one JSON record each, with a `needs_reference` flag); not committed, regenerate with `crawl_prompts.py` |
| `benchmarks/prompts/make_hour_jobs.py`, `prompts/hour_test_jobs.json` | picks and freezes the job list (needs `sentencepiece` and the model's tokenizer file) |
| `benchmarks/wan22_a14b_session.py` | runs on the pod: preflight, warm-up, jobs, telemetry, quality gate |
| `benchmarks/pod_guard.sh`, `run_hour_session.sh` | independent stop guard; pod orchestrator |
| `benchmarks/make_review_set.py` | builds the blind review set and its answer key |
| `benchmarks/report_session.py` | computes every table in the report from the raw logs |
| `benchmarks/fal_wan22_config.md` | fal's request spec and prices |
| `benchmarks/rounds/round0-pilots/` | pilot clips, raw records and a summary |

To re-derive the tables: `python3 benchmarks/report_session.py <session_dir>` reads only the raw `jobs.jsonl`, `session.json` and `preflight.json` files. The report and review-set scripts were verified against synthetic data before this session; the pod runner was not exercised on real hardware before this session.

## 11. Open questions for review

1. Is 480p the right tier to lead with, given fal's most-cited price point is 720p?
2. Is four runs at 27 steps enough to say anything about speed, or should the ladder be dropped in favor of more repeats?
3. Should frame interpolation be implemented before this number is used for a decision?
4. Is the amortization table (N = 4 to 200) representative of a distributed-hosting setup, where startup costs may differ?
5. Is a single informal reviewer acceptable for the steps ladder, or should the ladder be reported only as a timing result?
6. Do the go/no-go thresholds (150 TFLOPS, 840 s on the first job) fit what is known about this class of pod?
7. What should happen next given requirement 7's open-ended saturation goal, now that the cost of a real hour is known?

## 12. Later phases (not part of this session)

A second session on another day and, if possible, another host; 720p and 580p; image-to-video; a frame-count ladder (17 and 161); fp8 variants; frame interpolation; batch and concurrency tests; another model family using its own public benchmark bundle; other model families if their weights become accessible; fal comparison clips once budget exists for them; a second reviewer; entry of measured and published values into a shared reference sheet.

## 13. Adjustments made before this session ran

The starting draft of this design covered about 22.7 GPU-hours across many models and configurations. It was reviewed against the one-hour budget constraint (section 3) and reduced to this single session. Changes made in that review, with reasons:

| # | Issue found | Change made |
|---|---|---|
| 1 | Scope of 22.7 GPU-hours did not fit a one-hour budget. | Reduced to one session, about 69 min, about $1.9. |
| 2 | Quality pairs against fal needed API access that was not available for this test. | Dropped; blind review of this test's own steps ladder only, with no parity claim against fal. |
| 3 | Draft called for two reviewers and inter-rater agreement statistics. | Reduced to one reviewer; agreement is not claimed. |
| 4 | Other model-family tiers depended on access not established for this test. | Removed from this test; listed under later phases. |
| 5 | Truncation was first estimated from word counts (22.5%). With the real tokenizer it is 36.5% (64% for non-English). | Prompts are chosen by real token counts instead. |
| 6 | Draft called for at least 5 runs on 2 different days. | Reduced to four runs in one session, labelled as such. |
| 7 | The independent stop guard was specified but did not yet exist. | Built and tested against a stand-in pod-stop command; a bug where a process-matching pattern could match its own invoking command line was found and fixed. |
| 8 | The earlier draft's runner had no preflight, no frozen job list, no clock/throttle telemetry, no quality gate, and no time estimate for the first job. | Replaced by the current session runner. |
| 9 | All-in cost, as first specified, ignored pod time before the script starts. | Now uses container uptime plus session plus copy time. |
| 10 | Cost per accepted second from four clips would read like a stable rate. | Reported as raw counts with an explicit "not a rate" label. |
| 11 | Disk price was an unstated assumption. | Stated explicitly throughout and flagged for confirmation. |
| 12 | The interpolation gap was not stated. | Stated as excluded, with the resulting ratio labelled a lower bound. |
| 13 | An earlier share-of-prompts figure (76%) covered all crawled rows, not just the usable subset. | Corrected to 74% for the usable subset actually used. |
| 14 | No warm-up handling, despite a 48 s first step observed in the pilot. | Warm-up job added, excluded from queue cost. |
| 15 | Model weights might not survive a pod stop. | Preflight now handles both cases and reports download time either way. |
| 16 | The guard could stop the pod before results were fully copied. | 15-minute grace period added after the session finishes. |
| 17 | The job list could be edited after seeing results. | Frozen by its file hash, recorded in section 5.2. |
| 18 | Validation on the pod actually used for this session found that its `/workspace` mount is a network filesystem of unknown quota, unlike pods used for earlier pilots. Loading 139 GB through it would be slow and could exceed the quota, and the disk-free check would have passed incorrectly because that mount reports a very large nominal size. | Weights are cached on the local container disk instead. Preflight now refuses any cache location on a network filesystem and requires 160 GB free before downloading. |
| 19 | The pod image enables a fast-download feature flag without shipping the package it depends on, which would have crashed the download. | The session script installs the required package and verifies the import before starting; a failure ends the session immediately. |
| 20 | The software stack on this pod differs from the pilots (newer PyTorch/CUDA build and a newer library version). Speed differences may not be attributable to the GPU alone. | Versions are recorded per session, and the difference is listed as a limitation. |
| 21 | The hourly rate for the pod used in this session was not known when this design was first written. | The confirmed rate ($1.69/h GPU, $0.09/GB disk) is used, and the report script accepts rate overrides so results can be recomputed if a rate is later corrected. Pilot costs in section 4 keep the earlier rate, so they are not directly comparable to this session's results. |
| 22 | Found before scoring the blind review: the first draft of the review set showed the 27-step median clip twice (as a strata clip and as one of the steps-ladder clips), which would have revealed which steps clip was the baseline. | The median clip is now shown only in the steps-ladder set; the review-set builder and report script were changed and verified against synthetic data. |
| 23 | Found after the run: file sizes of the steps-ladder clips grew with step count (463,802 / 487,768 / 494,887 bytes), which could reveal which clip used how many steps. | Review copies are now padded to one identical byte size, and clip names are reshuffled per review set. |

## 14. What actually happened in this session

This section reports operational facts only; interpretation of the results is in `README.md`.

| Item | Planned | Actual |
|---|---|---|
| Pod | A100-SXM4-80GB | A100-SXM4-80GB, driver 580.126.16, CUDA 13.0, 128 cores; a newer PyTorch build than the pilots used |
| Rate | $1.618/h assumed | $1.69/h GPU and $0.09/GB disk, confirmed from the hosting panel after the run had started. The raw session file stored the earlier placeholder rate, so the report was recomputed with the confirmed rate. The disk unit (per month) is assumed. |
| Preflight | pass or abort | Passed: bf16 matmul 243 TFLOPS, cache on local disk, 85.1 GB VRAM |
| Weights download | about 8 min | 709.7 s (11.8 min) |
| Model load / warm-up | about 3 min | 79.8 s / 145.4 s (warm-up includes one-time model loading, GPU 57.5% busy) |
| Jobs | 6 jobs, about 49.7 min | 6 run, 0 failed, 0 skipped. Measured window 3,038 s (50.6 min) |
| First launch attempt | | Failed because an expected output directory did not exist yet; nothing ran unguarded. Relaunched about 1.5 minutes later. |
| Guard | hard stop 70 min after launch | Armed. Not needed: results were fully copied and verified, and the pod was stopped manually once that was confirmed, before the hard deadline. |
| Pod stop | | The stop command printed an unrelated configuration warning but reported the pod stopped; confirmed separately by a failed connection attempt afterward. |
| Pod-on time and cost | about 69 min, about $1.9 | about 81 min computed, about $2.32 computed (under the $2.50 cap); reconciled in section 7 of `README.md` against actual billing of $2.196 |
| Host and GPU conditions | | Host load average 46-67 at job starts (a busy shared host). Every job ran under a software power cap, mean SM clock about 1,305 MHz of a 1,410 MHz maximum. |
| Prompt tokens | A3 = 861 (counted locally before the run) | A3 = 854 as counted on the pod (both above the 512-token limit, so both indicate truncation). Other prompts' counts matched exactly. |

Deviations from the budget in section 8: weights download and pre-launch setup time ran longer than estimated, raising the cost from about $1.9 to about $2.3 computed (about $2.2 actual). The go/no-go threshold in section 6 (first 27-step job above 840 s) was not triggered: the first job took 551.7 s.

The review-set fixes from section 13, rows 22-23, were applied before scoring began.

Blind scoring, unblinding and billing reconciliation are complete; see `README.md`, sections 6-7. Quality note: the blind ranking of the steps ladder (27 > 20 > 15) was monotonic with step count on this one prompt, so the cost saving from fewer steps likely trades off real quality; more prompts and a second reviewer are needed before relying on that tradeoff.
