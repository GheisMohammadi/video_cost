[← All rounds](../../../README.md)

# Round 14 plan: Hunyuan follow-ups, GlyphPrinter→I2V, optional API baselines

Status: A1–A3 run complete (see README.md). B and C deferred. Frozen before any pod job.

## Why this round

Round 13 produced the first verbatim-correct on-screen sentences in this project (HunyuanVideo 1.5, two of five quoted lines exact; later lines in the same clip degraded). Open items from that round, plus a market research pass for Round 14:

1. Isolate whether later-line degradation is quote-count / capacity vs line content (fewer quotes per clip; deferred lines; reorder).
2. GlyphPrinter (CVPR 2026) now has public inference code and weights — image-only T2I on FLUX.1-dev. Test as correct still → I2V, the published-tool version of round 10 §7 / round 12 Qwen path.
3. Optional: same frozen prompt on hosted APIs (Seedance 2.0, Veo 3.1 Fast, and/or Kling) if keys are available — public text benches use short title cards, not this script.

Direction unchanged from rounds 12–13: evaluate published / market solutions, not invent new research architectures. Overlay animated-reveal polish stays out of scope unless generation paths fail to advance.

## Frozen test case

Identical customer script and seed family as rounds 10–13 (`round10_lawyer_whiteboard`, seed 10001 where the sampler allows it). Direct frame inspection against the real script; no automated accuracy claim without that.

## What will be tested

| ID | Tool | Prompt / input | Question |
|---|---|---|---|
| A1 | HunyuanVideo 1.5 T2V | Only quoted lines 1–2 (the ones exact in round 13 v3) | Do those two stay exact when they are the only quotes? |
| A2 | HunyuanVideo 1.5 T2V | Only quoted lines 3–4 + small-print URL | Does isolation restore accuracy on the lines that failed in v3? |
| A3 | HunyuanVideo 1.5 T2V | Same five quotes as round 13 v3, but failing lines first | Is degradation positional / capacity vs content? |
| B1 | GlyphPrinter | Still image of the whiteboard with the full script | Can a published glyph T2I model render the full script correctly? |
| B2 | Wan or Hunyuan I2V | B1 still as first frame (only if B1 text is correct) | Does correct text survive motion better than round 10/12 I2V paths? |
| C | Hosted API(s) | Same frozen prose/quoted prompt as appropriate per vendor | Closed-model reference on this long script (skip if no API access) |

A1–A3 share one model load on one pod where possible (round 13 paid a fresh download per attempt).

## What would make this a win

- A2 (or A1+A2 stitch pattern) yields verbatim lines that round 13 v3 lost — evidence the full board is reachable by limiting quotes per generation.
- B1 renders the full script correctly on a still; B2 keeps it through motion — a market image-text path usable for text-heavy clips.
- Any C clip that beats Hunyuan on this script — reason to route text-heavy jobs to that vendor.

## Expected failure modes

- A2 still garbles lines 3–4 even in isolation (content difficulty, not quote count).
- A3 still degrades “later” content after reorder (capacity / competition among glyph regions).
- GlyphPrinter strong on short glyphs, weak on multi-sentence boards (same length pattern as every prior round).
- I2V from a correct still drifts text (round 10 §7).
- APIs succeed on short cards in public benches but fail this long script.

## Resources

- Pod: `server/runpod20.txt` (fresh for this round).
- Budget: approved for this round’s A+B pod work (Hunyuan ~35 min/gen after load; plan one load + three gens, then GlyphPrinter if disk/VRAM allow).
- API keys: only if provided; otherwise C is skipped and noted in the report.
- Stop: independent `pod_guard.sh` + stop pod after verified pull (`--stop-when-done` or `runpodctl stop` from inside). Do not leave the pod billing after tests.

## Steps

1. Preflight on runpod20: disk, fstype of cache dir, GPU matmul, deps.
2. Upload and run Hunyuan A1–A3 in one session; arm guard with `PROC_PATTERN` matching the actual script name; `HARD_S` sized for ~3×35 min + load + margin.
3. Inspect frames vs script; decide whether to run B on the same pod (weights disk) or stop and report A-only.
4. If B: install GlyphPrinter, generate still, optional I2V.
5. C only with confirmed API access.
6. Pull clips + raw records with checksums; stop pod; write `README.md`.

## Files (once run)

- `clips/`: A1–A3 mp4s; B still/png and B2 mp4 if run; C clips if run.
- `raw/`: generation records, extracted frames.
- `README.md`: results after the run — not before.
