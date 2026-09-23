[← All rounds](../../../README.md)

# Round 2: prompts that ask for what this pipeline cannot produce

Status: 5 of 6 planned clips completed, copied with verified checksums, and blind-reviewed. A follow-up session for the sixth clip is prepared and frozen (`round2_topup_jobs.json`), not yet run. Design and reasons: [`PLAN.md`](PLAN.md). Exact tables regenerated from the raw logs: [`raw/REPORT.md`](raw/REPORT.md).

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

## Blind review results (single reviewer)

The reviewer scored 5 clips with random names, no prompt or category visible, then the key was opened.

| Clip | Category | prompt_match | mismatch_handling | Notes |
|---|---|---|---|---|
| C1 | camera/lens jargon | pass | "kind of done" | "looks good" |
| C2 | resolution (8K wording) | partial | "struggled and looks broken" | "walks in sky" |
| C3 | audio | partial | "no one actually talks" | "not much motion" |
| C4 | aspect | pass | "looks something better have been done" | "looks good" |
| C5 | duration (15 s requested) | partial | "struggled" | "looks impossible" |

2 of 5 passed outright, 3 were partial, none failed outright. No clip was scored as "misread literally" this time (the failure mode round 1's camera-jargon clip showed) -- this round's camera-jargon clip (C1) instead passed. The two prompts are different: round 1's was 30 words and largely just camera-technical wording with little scene description ("ARRI Alexa Cinematic Film Still"); this round's is 65 words with a full scene described and the camera jargon as one modifier among several. With one data point in each direction, this suggests the failure mode may depend on how much of the prompt is actual scene content versus jargon, not on the presence of jargon alone -- worth testing more directly in a later round, not yet established.

The two categories that most directly ask for more than a 5-second, standard clip -- resolution ("8K") and duration ("15-second") -- were the two marked "struggled" rather than just ignored cleanly. The audio clip was marked partial for a different reason: the prompt implies spoken dialogue, and the reviewer noted no one actually speaks, consistent with this pipeline producing no audio and no attempt at visible lip-sync either.

## Still to do

1. Run the short follow-up session for the kitchen-sink clip (`round2_topup_jobs.json`, prepared and frozen; same warm-up and settings as the main session, one job only).
2. Confirm the pod shows as stopped in the hosting panel.

## Files

- `raw/REPORT.md`: tables generated from the raw logs (`python3 benchmarks/report_session.py benchmarks/rounds/round2-capability-mismatch/raw --gpu-usd-h 1.59 --disk-usd-h 0.028 --copy-s 90`).
- `raw/jobs.jsonl`, `raw/preflight.json`, `raw/session.json`: raw records, including the skip record for the sixth job.
- `raw/audio_check.json`: per-clip audio-stream check.
- `raw/*.mp4`: the six clips that were produced (warm-up plus five measured jobs).
- `review/review_scores.csv`, `review/review_prompts.md`, `review/_key/review_key.json`: the completed blind review and its answer key. The padded, renamed video copies used for scoring are not kept; the clips in `raw/` are the same content.
- `round2_topup_jobs.json`: frozen job list for the sixth clip's follow-up session (the unmodified `M6_kitchen_sink` entry from `round2_jobs.json`, plus the same warm-up job).
