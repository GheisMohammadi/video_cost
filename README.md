# Video generation cost benchmarks

We're measuring what it actually costs to run open-weights video models on rented GPUs (RunPod, and later other hosts and bare metal), compared with API vendors like fal.ai — to find where self-hosting is profitable for Harmony's video operators. Each test is a **round**, in its own folder under [`benchmarks/rounds/`](benchmarks/rounds/), with its own plan, raw data, video clips and report. Click a round below to see its detail page and videos.

## Rounds

| Round | Date | What was tested | Headline result |
|---|---|---|---|
| [Round 1](benchmarks/rounds/round1-wan22-a14b-480p/) | Sep 21-22, 2026 | Wan 2.2 A14B, 480p, fal's exact default settings, one-hour session, 6 prompts (varied length/language), 27/20/15-step ladder, blind human review | **$0.0531/video-s** busy-only (1.33x fal's $0.04), **$0.0723/video-s** all-in reconciled against real billing (1.81x fal). Fewer steps is cheaper but the blind review ranked quality in the same order as step count. |
| [Round 0](benchmarks/rounds/round0-pilots/) | Sep 19-20, 2026 | Informal single-run pilots: Wan 2.2 5B and first A14B smoke tests | First cost signals, used to size Round 1. Not for citing — no repeats, no review, no independent stop guard. |

## How a round is built

Each round folder holds:
- `README.md` — the round's report: what was tested, the numbers, and embedded video clips.
- `PLAN.md` (from Round 1 onward) — written and audited *before* the run, with reasons for every choice and traceability to the project's stated requirements. Frozen in git before results exist.
- `clips/` — the generated videos.
- `raw/` — the raw logs and generated tables everything else is computed from.
- `review/` — blind human review scores and the answer key, where one was done.

The tools that run a round (pod session script, independent stop guard, prompt crawler, review-set builder, report generator) live in `benchmarks/` and are reused across rounds — see [`benchmarks/README.md`](benchmarks/README.md) for what each one does and the order they run in.

## Starting a new round

1. Copy the shape of `benchmarks/rounds/round1-wan22-a14b-480p/`: a `PLAN.md` written and committed *before* running anything, covering what's being tested, why, the cost budget, and traceability to any open request from the team.
2. Name the folder `roundN-<short-slug>`, incrementing N.
3. Use the existing scripts in `benchmarks/` (see [`benchmarks/README.md`](benchmarks/README.md)) where the test fits their shape; extend or replace them where it doesn't, and note that in the round's `PLAN.md`.
4. Add a row to the table above once the round has a result.

## Pod access

Running a new round needs a rented GPU pod (currently RunPod). `./connect.sh` opens an SSH session to whichever pod is current; the pod's address, SSH key and passphrase live in `server/`, which is **not committed** (`.gitignore` covers `server/` and `connect.sh`) since they're per-person credentials. If you're setting this up for the first time, you'll need your own pod and your own `server/` folder — see [`AGENTS.md`](AGENTS.md) for the exact layout it expects and for pod-specific gotchas (disk layout, cache paths, how to stop a pod). You don't need any of this to read a round's report or watch its clips — those are plain files in `benchmarks/rounds/`.

## Repo layout

```
README.md                    this page
AGENTS.md                    conventions and pod-specific gotchas for whoever (or whatever) drives the pod
connect.sh                   SSH into the current RunPod pod
server/                      pod credentials — gitignored, not committed, you provide your own
benchmarks/
  README.md                  what each tool below does and the order they run in
  fal_wan22_config.md        fal.ai's exact request spec, used to match their deploys
  wan22_a14b_session.py      runs on the pod: preflight checks, warm-up, the frozen job list, telemetry, quality gate
  pod_guard.sh               independent watchdog that stops the pod on a deadline, even if the session hangs
  run_hour_session.sh        entry point that arms the guard and starts the session on the pod
  pull_session.py            copies results back over SSH, verifies checksums, can stop the pod when done
  report_session.py          turns a round's raw logs into its results tables
  make_review_set.py         builds a blind (relabeled, size-matched) set of clips for human quality review
  prompts/                   crawler + selection scripts for real prompts (see benchmarks/README.md for what's committed)
  legacy/                    earlier scripts, superseded or never used — kept for reference
  rounds/
    round0-pilots/           informal single-run pilots (not for citing)
    round1-wan22-a14b-480p/  PLAN.md, README.md (report), clips/, raw/, review/
    roundN-.../              same shape, one folder per round
```
