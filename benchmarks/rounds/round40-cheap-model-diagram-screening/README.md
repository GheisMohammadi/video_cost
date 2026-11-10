[← All rounds](../../../README.md)

# Round 40: screen genuinely cheap video-gen models against the round-33 diagram task

Status: complete (single-attempt feasibility screen). User directive:
Seedance (and the other tools tested so far -- Kling, Veo) are expensive;
find and test cheaper models. This round is a quick, cheap screen using
the round-33 diagram task, run before round 39 continues the actual
in-progress text+annotation task on these same models.

## Watch the clips

<video src="clips/round40_pixverse.mp4" controls width="260"></video>
<video src="clips/round40_minimax.mp4" controls width="260"></video>

(left to right: PixVerse V6, MiniMax H3 Max Turbo)

## 1. Summary

- Researched fal.ai's pricing page for the cheapest text-to-video models
  that could plausibly handle structured, position-anchored content:
  **PixVerse V6** ($0.045/s at 720p, ~5x cheaper than Seedance Fast's
  $0.24/s) and **MiniMax H3 Max Turbo** ($0.028/s at 768p during the
  current Nov 2026 promo rate, ~8.6x cheaper than Seedance Fast).
- **Grok Imagine Video 1.5 was dropped** -- turned out to be
  image-to-video only (no text-to-video variant found), and at $0.14/s
  for 720p it's actually pricier than Seedance Mini, so it doesn't serve
  the cost goal at all.
- Reused round 33's validated 5-box/hub-point diagram prompt unchanged as
  a clean, known-good baseline -- the same explicit, position-anchored
  layout that Kling and Seedance both nailed in round 33, and Veo failed.
- **Both cheap models passed on the first attempt.** PixVerse and MiniMax
  both rendered the exact correct 5-box layout (A top-center, B mid-left,
  C mid-right, D bottom-left, E bottom-right) with all 4 lines meeting
  cleanly at the shared hub point -- matching round 33's best results
  (Kling, Seedance) at roughly 1/5 to 1/9 the per-second cost. Progressive
  line growth under the moving tip was confirmed on PixVerse via a
  mid-drawing frame.
- Both models required a further-condensed prompt to fit their character
  limits: PixVerse caps prompts at 2048 UTF-8 bytes (stricter than Kling's
  2500) and MiniMax was tested with the same condensed version for
  consistency.

## 2. What was run

| Item | Value |
|---|---|
| Models | `fal-ai/pixverse/v6/text-to-video`, `minimax/h3-max-turbo/text-to-video` |
| Prompt | Condensed version of round 33's diagram prompt (`prompt_short.txt`, 1987 bytes, under both models' limits) |
| Resolution / aspect | 720p (PixVerse), 768p (MiniMax), both 16:9 |
| Duration | 5s each |
| Generation time | ~61-68s per clip |
| Cost | ~$0.37 total (PixVerse ~$0.225, MiniMax ~$0.14) |

`run_fal_test.py` usage: `python3 run_fal_test.py <pixverse|minimax>`.

## 3. What this means

| Question | Answer |
|---|---|
| Can genuinely cheap models (5-9x cheaper than Seedance Fast) handle explicit, position-anchored diagram instructions? | Yes, on this one attempt each -- both matched round 33's best results exactly. |
| Is this conclusive proof these models are reliable? | No -- only one attempt per model; round 33 itself needed prompt iteration (round 32 to round 33) before any tool got this right consistently. Worth more attempts before fully trusting either model. |
| Open issue | This round tested the diagram task, not the text+annotation task that round 38 was actually in the middle of -- round 39 picks that back up on these same cheap models. |

## 4. Files

- `clips/round40_pixverse.mp4`, `clips/round40_minimax.mp4`: the two generated clips.
- `prompt_short.txt`: condensed version of round 33's diagram prompt, under both models' character limits.
- `run_fal_test.py`: generation script, see usage above.
- `raw/raw_record_round40_{pixverse,minimax}.json`: generation metadata.
- `raw/{pixverse,minimax}_frame_{early,last}.png`: sampled frames used for the visual review in section 1.
- `PLAN.md`: this round's plan, frozen before running.

## 5. Cost

~$0.37 total (PixVerse ~$0.225, MiniMax ~$0.14), one attempt each.
