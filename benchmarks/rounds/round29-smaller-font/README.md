[← All rounds](../../../README.md)

# Round 29: fix line-wrap overflow with a compact-handwriting rule

Status: complete. Round 28 fixed the outfit-consistency defect at the segment
midpoint (digital whiteboard-wipe handoff), but 3 of its 7 clean rows wrapped
across two board lines instead of one, which left row 8 without enough
vertical space and caused it to overwrite earlier text. This round adds an
explicit `SIZE_RULE` instructing small, single-line handwriting and
regenerates the full 8-row chain.

## Watch the clip

<video src="clips/round29_final_captioned.mp4" controls width="260"></video>

## 1. Summary

- **Every row wrote on a single board line.** All 8 rows frame-checked: no
  sentence wrapped to a second line, and the board still had visible spare
  space below row 8, the opposite of round 28's overflow.
- **Outfit/presenter consistency held through the segment-midpoint wipe
  handoff**, same mechanism as round 28 (ink erased via OpenCV inpainting on
  the chain-anchor frame before being fed forward as `start_image_url`).
- **Marker/text sync and no-echo both held**, same as rounds 27-28 -- no ink
  appears before the marker tip is in contact with the board, and no row
  repeats a previous row's text.
- Total duration: 31.93s, matching the target.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (row 1 and the row 5 wipe handoff) and image-to-video (every other row), via fal.ai |
| Seed | 10001 |
| Rows | 8, in two chained segments (1-4, 5-8), wipe handoff at row 5 |
| Resolution / aspect | 720p, 9:16 |
| Generation time | ~130-170s per clip |
| Cost | ~$5-6 (8 rows, no retries needed) |

`run_fal_test.py` usage: `python3 run_fal_test.py <row 1-8> [prev_clip_path] [wipe]`. Same interface as round 28, plus the new `SIZE_RULE` baked into every prompt.

Fixes carried into every prompt:

- **`ONSET_RULE`**: no ink exists beyond what's already on the board at clip start; new ink only begins once the tip is pressed against the board and already moving.
- **`NO_ECHO_RULE`**: forbids repeating or retracing text already on the board.
- **`SIZE_RULE`** (new this round): each letter no taller than roughly a twelfth of the board's height, the full sentence fits on one line without wrapping, and consistent space is left below each line for the rows still to come.

## 3. The line-wrap fix

Round 28's rows 5, 6 and 7 each wrapped their one-sentence row across two
board lines (6 board lines used for 3 sentences), which is what caused row
8's text to collide with existing content and get overwritten. Adding
`SIZE_RULE`'s explicit handwriting-size and single-line instruction fixed
this on the first attempt for all 8 rows in this round -- confirmed by
extracting and visually checking the last frame of every clip. Row 8 (the
last of the second segment) still had clear blank board space below it.

## 4. Post-processing

Same trim + variable-pause + caption-overlay approach as rounds 23/27/28 (`postprocess.py`): rows trimmed to their writing-complete window (frames 0-128 for row 1, 22-128 for middle rows, 22-150 for row 8), stitched with varied freeze-frame pauses (0.20-0.45s) between rows, captions (reused round 22's rendered PNGs, since the script and row split are identical) burned in per original sentence.

## 5. What this means

| Question | Answer |
|---|---|
| Does a compact-handwriting / single-line rule fix round 28's wrap-driven board-overflow? | Yes, verified on all 8 rows -- no wraps, no overwritten text. |
| Does the whiteboard-wipe handoff still hold outfit/presenter consistency with this change? | Yes, same mechanism, same result as round 28. |
| Does sync and no-echo still hold? | Yes, unchanged from rounds 27-28. |
| Open issue remaining | Row-to-row transition glitch/shake (hard cuts between clips) -- not addressed in this round. |

## 6. Files

- `clips/round29_final_captioned.mp4`: final deliverable -- 9:16, 720p, ~32s, captioned.
- `clips/wan30_round29_row{1-4}.mp4`: segment 1 (I2V chained from row 1).
- `clips/wan30_round29_row5.mp4`: segment 2 start -- wipe handoff from round 29's own row 4 last frame.
- `clips/wan30_round29_row{6-8}.mp4`: segment 2 continuation (I2V chained from row 5).
- `run_fal_test.py`: generation script, see usage above.
- `wipe_board.py`: board-ink inpainting helper, reused unchanged from round 28.
- `postprocess.py`: trim/stitch/caption script.
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$5-6 total (8 successful rows, no retries, all 5s/720p generations).
