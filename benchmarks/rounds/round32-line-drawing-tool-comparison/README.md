[← All rounds](../../../README.md)

# Round 32: line-drawing (not text) comparison across 3 top video-gen tools

Status: complete. Boss directive: shift the test subject from handwriting
text to drawing straight diagram lines, and compare 3 of the current
best-regarded video-gen tools rather than sticking to Wan 3.0 alone. Same
boss-provided prompt (verbatim, see `prompt.txt`) run through all three via
fal.ai, describing a woman drawing a simple software-architecture diagram
(vertical line, horizontal line, two branching diagonals) on a transparent
glass board.

## Watch the clips

<video src="clips/round32_kling.mp4" controls width="260"></video>
<video src="clips/round32_seedance.mp4" controls width="260"></video>
<video src="clips/round32_veo.mp4" controls width="260"></video>

(left to right: Kling 3.0 Pro, Seedance 2.0, Veo 3.1)

## 1. Summary

| Tool | Resolution | Duration | Cost | Line-sync / geometry | Notes |
|---|---|---|---|---|---|
| Kling 3.0 Pro | 1080p | 10s (full) | ~$1.12 | Best -- clean straight vertical/horizontal lines, labeled boxes match the "simple architecture diagram" brief closely | Board text renders mirrored/garbled, likely an artifact of the transparent-glass framing being rendered as shot through the glass from the far side. Ends with her looking straight at camera, diagram untouched, matching the script. |
| Seedance 2.0 (fast) | 720p | 10s (full) | ~$2.42 | Weakest -- final diagram has 4 crossing diagonal lines instead of the scripted single vertical + horizontal + 2-way branch | Good hand/marker grip realism and composition, but geometry drifted furthest from the instructions. Most expensive of the three for this clip. |
| Veo 3.1 | 1080p | 8s only (no 10s option) | ~$1.60 | Good -- vertical, horizontal, and branching diagonals to two boxes track the brief better than Seedance | Most visually polished lighting/studio look of the three. Board text is fake-but-convincing gibberish (a known AI text-rendering artifact). Cannot do the full 10s the brief asked for in one generation. |

Sora 2 was excluded -- its fal.ai API is being discontinued (shutting down
Sep 2026). Runway/Pika/Luma were not tested this round.

## 2. What was run

| Item | Value |
|---|---|
| Models | `fal-ai/kling-video/v3/pro/text-to-video`, `bytedance/seedance-2.0/fast/text-to-video`, `fal-ai/veo3.1` -- all via fal.ai |
| Prompt | Boss-provided, verbatim (`prompt.txt`); Kling required a shortened version (`prompt_kling.txt`) since its API caps prompts at 2500 characters and the full prompt is 2517 |
| Aspect ratio | 16:9 (prompt specifies a medium-wide straight-on studio shot, not the 9:16 vertical format used in the whiteboard-text rounds) |
| Generation time | ~140-390s per clip |
| Cost | ~$5.15 total for one attempt per tool, no retries needed |

`run_fal_test.py` usage: `python3 run_fal_test.py <kling|seedance|veo>`.

## 3. Issues hit

- **Kling's 2500-character prompt limit**: the boss-provided prompt is 2517
  characters, 17 over Kling's cap, and the first submission failed with a
  `422 string_too_long` error. Fixed by writing a slightly condensed
  version of the same prompt (`prompt_kling.txt`) that preserves every
  requirement, used only for the Kling call.
- **A stale 403 from fal.ai right after the account's balance top-up**
  (carried over from round 31) was not an issue this round -- the account
  was already confirmed working before round 32 started.

## 4. What this means

| Question | Answer |
|---|---|
| Which tool best followed the line-drawing/sync instructions? | Kling 3.0 Pro, on geometry -- cleanest straight lines and closest match to the scripted diagram shape. |
| Which tool looked most visually polished/realistic? | Veo 3.1 -- best lighting and studio realism, though it can't generate the full 10s in one call. |
| Which tool underperformed? | Seedance 2.0 -- most expensive of the three here, and its final diagram geometry (4 crossing diagonals) drifted furthest from the brief. |
| Open issue | Board text legibility: Kling renders it mirrored/garbled, Veo renders convincing-looking but fake gibberish. Neither produces genuinely readable diagram labels -- not evaluated further this round since the focus was line/stroke sync, not text. |

## 5. Files

- `clips/round32_kling.mp4`, `clips/round32_seedance.mp4`, `clips/round32_veo.mp4`: the three generated clips.
- `prompt.txt`: boss-provided prompt, used verbatim for Seedance and Veo.
- `prompt_kling.txt`: condensed version used only for Kling (character-limit workaround).
- `run_fal_test.py`: generation script, see usage above.
- `raw/raw_record_round32_{kling,seedance,veo}.json`: per-tool generation metadata (endpoint, payload, request id, cost-relevant timing).
- `raw/*_frame_{early,mid,last}.png`: sampled frames used for the visual review in section 1.
- `PLAN.md`: this round's plan, frozen before running.

## 6. Cost

~$5.15 total (Kling ~$1.12, Seedance ~$2.42, Veo ~$1.60), one attempt per tool, no retries.
