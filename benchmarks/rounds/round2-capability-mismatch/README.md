[← All rounds](../../../README.md)

# Round 2: prompts that ask for what this pipeline cannot produce

Status: 5 of 6 planned clips completed and copied with verified checksums; the pod stopped correctly once nothing further could be produced. Blind review pending. Design and reasons: [`PLAN.md`](PLAN.md). Exact tables regenerated from the raw logs: [`raw/REPORT.md`](raw/REPORT.md).

## What happened to the sixth clip

The kitchen-sink job (`M6_kitchen_sink`, a real prompt combining several mismatch categories at once) did not run. This was not a failure: the session runner's own safety check decided, correctly, that it would not finish inside the fixed measurement window and skipped it rather than risk running past the deadline. The five single-category jobs averaged 593.5 s each, about 2.6% over this round's 575 s per-job estimate; unlike round 1, this round's job list had no cheaper, reduced-step jobs to absorb that kind of variance, so six full-cost jobs came close enough to filling the window that a small, ordinary overrun was enough to push the sixth one out. The pod was stopped normally once the puller confirmed every clip that actually existed had been copied and checksum-verified — nothing was left running, and nothing more could have been retrieved by waiting longer.

A short, cheap follow-up session (about 15-20 minutes, roughly $0.50) would be enough to get the kitchen-sink clip on its own, if wanted.

## Results so far

| Job | Category | Generate s | Cost per clip | Cost per video-second |
|---|---|---|---|---|
| M1 | audio | 594.0 | $0.269 | $0.0531 |
| M2 | resolution | 589.6 | $0.267 | $0.0527 |
| M3 | aspect | 587.2 | $0.266 | $0.0525 |
| M4 | camera/lens jargon | 585.7 | $0.265 | $0.0524 |
| M5 | duration | 590.3 | $0.267 | $0.0528 |

Mean 593.5 s, spread 0.5% (stdev 2.8 s) -- consistent with round 1's finding that generation time barely depends on prompt content. Busy-queue cost: **$0.0527 per video-second**, 1.32x fal's $0.04 at the same 480p/27-step settings -- within 1% of round 1's $0.0531 (1.33x), measured on a different pod instance at a different confirmed rate ($1.59/h here vs $1.618/h there). That agreement is itself a useful result: it's a second, independent data point supporting round 1's cost figure, not just a repeat of the same measurement.

All-in for this session: pod on about 71 minutes, $1.91 total (cap was $3.00). $0.0753 per delivered video-second including setup and idle time.

## Audio check

Every delivered clip, including the one whose prompt explicitly asks for ambient sound and dialogue, was probed for an audio stream. Result: **0 of 6 clips (including the warm-up) have any audio track.** This pipeline's current configuration does not generate audio under any circumstance, regardless of what the prompt requests -- confirmed directly rather than assumed. Given that 31.7% of the real prompt corpus asks for audio (`PLAN.md`, section 2), this is a real gap between what users commonly ask for and what this setup delivers, independent of cost.

## Still to do

1. Blind review of the 5 clips (`review/`, do not open `review/_key/` before scoring): `prompt_match` as in round 1, plus a new `mismatch_handling` field -- was the unsupported part of the prompt ignored cleanly, did it visibly break or look rushed, or was it misread literally (an object rendered instead of the intended scene, echoing round 1's camera-jargon clip)?
2. Decide whether to run the short follow-up session for the kitchen-sink clip.
3. Confirm the pod shows as stopped in the hosting panel.

## Files

- `raw/REPORT.md`: tables generated from the raw logs (`python3 benchmarks/report_session.py benchmarks/rounds/round2-capability-mismatch/raw --gpu-usd-h 1.59 --disk-usd-h 0.028 --copy-s 90`).
- `raw/jobs.jsonl`, `raw/preflight.json`, `raw/session.json`: raw records, including the skip record for the sixth job.
- `raw/audio_check.json`: per-clip audio-stream check.
- `raw/*.mp4`: the six clips that were produced (warm-up plus five measured jobs).
- `review/`: the blind review set and its answer key, once scored.
