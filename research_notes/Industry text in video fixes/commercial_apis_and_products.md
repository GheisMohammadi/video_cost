# Commercial APIs and products — on-screen text (late 2026)

## Industry pattern

Exact wording is rarely trusted to the video model for long copy. Common production pattern: generate the scene (often with “no text” / blank board), then burn in real text via overlay (ffmpeg, editor, or caption product). fal `auto-caption` / auto-subtitle products transcribe audio into subtitles; they do not place a supplied multi-line script onto a whiteboard.

## Independent short-text benchmarks (not multi-sentence boards)

Public comparisons mostly use 1–2 short lines (title cards, neon signs, “SALE 30%”), not multi-paragraph whiteboard scripts.

| Source | Finding relevant here |
|---|---|
| Voyager “30 models” text-card test (2026) | Veo 3.1 / Fast, Seedance 2.0, MiniMax H3, Hailuo 2.3 held short title+date; Kling 3.0 garbled; Kling 4.0 first Kling tier to spell that card correctly |
| SandBase API bench (2026-10) | Short “SALE 30%” succeeded across models tested; main failure mode was *extra invented* text (esp. Veo Fast) |
| SlopTV on-screen text leaderboard | Seedance 2.0, MiniMax H3, Sora 2 (discontinued), Grok Video among top scorers on short neon-sign style prompts |
| Earlier Seedance 2.0 review (cited in round 13 plan) | ~3.8/10 text; short overlays OK, long strings degrade |

## Implication for this project

A same-prompt API test on the frozen lawyer whiteboard script would be new information: public benches do not measure that length. Expected risk: APIs that win on title cards still fail or partially fail on five-line board copy.

## Cheap reference test (if API access exists)

Same frozen prompt as rounds 10–13; one clip each: Seedance 2.0 (or Fast), Veo 3.1 Fast, Kling 3.0 or 4.0. Cost typically cents–low dollars per clip. No pod required.
