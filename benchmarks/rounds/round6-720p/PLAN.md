# Round 6 test design: proper 720p, same rigor as round 1's 480p

Status: scripts written and tested against synthetic data where GPU-independent; not yet run. This is List6 item 6. Frozen before running.

## 1. Question

Fal's most-cited price is its 720p tier ($0.08/s), but every round so far (1, 2, 3) measured 480p. This round closes that gap using the exact same methodology round 1 established for 480p, so the two resolutions are directly comparable rather than needing a second, differently-designed test.

## 2. Test design

Reuses round 1's exact prompts, seeds, and step counts (`benchmarks/prompts/hour_test_jobs.json`, sha256 `b19fd5f5902a13ebba3207dc3e2455e72ac817441600e79efe0ac736323db21d`), changing only width and height to fal's 720p tier (1280x720 instead of 832x480). Frozen as `round6_jobs_720p.json`, sha256 `ee0c1195a331bf56d22b0b404482eb491819516badc69cafe384d6e4029064f5`. Runs through the identical, already-proven `wan22_a14b_session.py` / `pod_guard.sh` / `run_hour_session.sh` used by rounds 1 and 4, with no code changes -- only a different job-list file (`JOBS_FILE=round6_jobs_720p.json`, using the configurability added in round 4). Same warm-up, same six measured jobs (A1-A4 at 27 steps, B1/B2 at 20/15 steps on the median prompt), same blind review process (`make_review_set.py`, reusable since the job shape is identical to round 1's).

Holding the prompts and seeds constant while changing only resolution isolates resolution as the one variable that differs from round 1, the same logic round 3 and round 4 used to reuse round 1's data for controlled comparison.

## 3. What this is expected to show, stated before running

The 720p pilot in round 0 (a single, unrepeated run) measured 1,961 s for one 27-step clip at these settings, versus round 1's 552-568 s for the same settings at 480p -- roughly 3.5x slower. This round will either confirm that ratio with a proper multi-prompt, cross-checked measurement, or show the pilot was not representative. Cost per video-second is expected to land closer to fal's $0.08/s 720p price than 480p's ratio was to $0.04/s, or further from it -- not assumed either way.

## 4. Combined pod session with round 5

This round and round 5 (frame interpolation) run on the same rented pod, back to back, to avoid paying for a second setup and weight download. Procedure:
1. Rent one A100-SXM4-80GB pod.
2. Run this round's job list to completion (preflight, warm-up, six jobs), independent stop guard armed for this phase.
3. Copy and verify results, but do not stop the pod yet (round 5 still needs it).
4. Upload round 1's four existing 480p clips, and hand this round's freshly-generated 720p clips (already on the pod) to round 5 by path.
5. Restart the guard for round 5's phase (a fresh deadline sized for its own budget, the same pattern used mid-round-3 when a deadline needed correcting).
6. Run round 5, copy and verify its results, then stop the pod for real -- confirmed by an actual connectivity check, not just that the stop command was accepted (`pull_session.py` now verifies this itself, a fix made after round 4 found a stop command that reported success while the pod kept running).

## 5. Budget

Derived from round 0's single 720p pilot (1,961 s at 27 steps) and round 1's steps-to-time ratios (20 steps = 74.6% of 27-step time, 15 steps = 58.8%), since no multi-sample 720p timing exists yet -- this is this round's own job to establish, so treat the estimate as rough.

| Item | Time |
|---|---|
| Setup, preflight, download | ~18 min |
| Warm-up | ~3 min |
| A1-A4 at 27 steps (4 x ~1,961 s) | ~131 min |
| B1 at 20 steps (~1,463 s) | ~24 min |
| B2 at 15 steps (~1,153 s) | ~19 min |
| Copy results (larger 720p files) | ~6 min |
| **Total** | **~201 min, about $5.42** at $1.618/h |

## 6. Limitations

1. Resolution and cost estimates for this round rest on a single prior pilot data point (round 0), not a controlled measurement -- this round exists specifically to replace that estimate with real data.
2. No new frame-interpolation or hardware-lottery testing here; those are round 5 and round 4 respectively.
3. Blind review at 720p uses the same single-reviewer process as round 1, with the same limitations (one reviewer, informal, seven clips).
