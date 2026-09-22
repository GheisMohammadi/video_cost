[← Project home](../README.md)

# Benchmark tools

These scripts run one round of testing end to end: pick prompts, run the model on a rented GPU pod, pull the results back, build a blind review set, and turn raw logs into a report. Actual round results live in [`rounds/`](rounds/), one folder per round — this page is about the tools that produce them.

All of these assume you can reach the pod via `../connect.sh` (see the project root [`README.md`](../README.md) and [`AGENTS.md`](../AGENTS.md) for pod access; the key, passphrase and pod address live in `server/`, which is not committed).

## Workflow for a round like round 1

1. **Crawl prompts** (`prompts/crawl_prompts.py`) — pulls real prompts from awesomevideoprompts.com into a local `prompts/prompts.jsonl`. Not committed (see below); run it yourself if you need fresh prompts.
2. **Pick and freeze the job list** (`prompts/make_hour_jobs.py`) — selects a fixed set of prompts by real token count (short / median / long / non-English) plus a steps ladder on one prompt, and writes it to a single JSON file such as `prompts/hour_test_jobs.json`. Commit that file *before* running anything, so the test design can't be adjusted after seeing results.
3. **Run the session on the pod:**
   - `wan22_a14b_session.py` — runs on the pod. Does a preflight check (CUDA works, GPU is fast enough, weights aren't on a slow network volume), a warm-up job, then every job in the frozen list, recording timing, GPU telemetry (utilization, power, clocks, throttling) and an automated quality gate (right size, not black, not frozen) for each one.
   - `pod_guard.sh` — an independent watchdog, started separately from the session script. Stops the pod at a hard deadline, or shortly after the session finishes, or if the session process dies without finishing. It runs as its own process so a stuck or crashed session script cannot leave the pod billing indefinitely.
   - `run_hour_session.sh` — the entry point you actually run on the pod: installs dependencies, arms `pod_guard.sh`, then runs `wan22_a14b_session.py`.
4. **Pull results back** (`pull_session.py`, run on your own machine) — polls the pod over the same `connect.sh` SSH session (there's no other file-transfer channel), copies each finished clip and the raw logs as they appear, verifies every file by checksum, and — once everything is verified — can stop the pod for you (`--stop-when-done`).
5. **Build the blind review set** (`make_review_set.py`) — copies the clips that need a human quality check into randomly-named files of one identical size (so file size can't leak which one is which), plus a scoring sheet. The mapping back to real job names is written to a separate `_key/` file — don't open it until scoring is done.
6. **Generate the report** (`report_session.py`) — recomputes every number (cost per video-second, utilization-adjusted cost, all-in cost, the steps-ladder comparison) directly from the raw logs, so anyone can rerun it and get the same tables. Pass `--review`/`--key` once the blind review is scored to fold those results in too.

## Other files here

- `fal_wan22_config.md` — fal.ai's exact request defaults for Wan 2.2 A14B (resolution, steps, guidance, frame interpolation, price), pulled from their API schema. Rounds that claim to "match fal" should match every field listed here.
- `legacy/` — earlier, superseded scripts (used for round 0, or never used). See [`legacy/README.md`](legacy/README.md).

## What's committed, what isn't

`prompts/prompts.jsonl` (the full crawl, ~16 MB of third-party prompt text), `prompts/crawl.log`, `prompts/baseline_sample.jsonl`, `prompts/saturation_sample.jsonl` and `prompts/spiece.model` (a tokenizer file from the Wan 2.2 model repo) are **not committed** — they're either large scraped/generated data or a third-party file with its own license. They're regenerated locally: run `crawl_prompts.py`, then `make_hour_jobs.py` (which needs `spiece.model` from the [Wan 2.2 repo's tokenizer folder](https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers/tree/main/tokenizer) to count real tokens). The one frozen selection actually used for a round (e.g. `prompts/hour_test_jobs.json`) *is* committed, since that's the input the round's numbers depend on.
