[← All rounds](../../../README.md)

# Round 27: image-to-video chaining, strict onset-sync, no-echo rule

Status: complete, superseded by round 28 for the outfit-consistency fix. Round 24 tried image-to-video (I2V) chaining once and it fixed cross-row visual continuity but introduced a text-echo defect (the model repeated the previous row's text instead of writing the new one). This round repeats I2V chaining with an explicit no-echo instruction and verifies marker/text sync frame-by-frame across all 8 rows.

## Watch the clip

<video src="clips/round27_final_captioned.mp4" controls width="260"></video>

## 1. Summary

- **Marker/text sync verified clean across all 8 rows.** Every row frame-audited at tight spacing: no ink ever appears before the marker tip is in contact with the board (checked at the exact onset, frame-by-frame around the 0.8-1.0s mark of each clip), and no row repeats or echoes the previous row's text.
- **Two chain segments, not one.** Chaining past ~4 hops caused row 5 to garble text twice in a row ("So this I pay." then "Sighed I pay." instead of "So this week I pay") -- confirmed as a repeatable failure, not a fluke, by retrying once. The chain was split into two 4-row segments: rows 1-4 chained from a single text-to-video start, rows 5-8 chained from a second, independent text-to-video start.
- **Outfit/presenter changes at the segment boundary.** Starting segment 2 with a fresh text-to-video generation let the model reinvent the woman's appearance (white top -> light blue shirt). This is the open problem round 28 addresses.
- Total duration: 31.93s, matching round 23's target.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (row 1 of each segment) and image-to-video (every other row), via fal.ai |
| Seed | 10001 |
| Rows | 8, in two chained segments (1-4, 5-8) |
| Resolution / aspect | 720p, 9:16 |
| Generation time | ~100-285s per clip (retries included) |
| Cost | ~$5-6 (8 rows + 2 retries on row 5) |

`run_fal_test.py` usage: `python3 run_fal_test.py <row 1-8> [prev_clip_path | "fresh"]`. Row 1 and any row passed `"fresh"` in place of a previous-clip path start a new text-to-video segment (blank board, new presenter generation); every other row chains image-to-video from the literal last frame of the previous clip.

Fixes carried into every prompt:

- **`ONSET_RULE`**: no ink exists on the board beyond what's already there at clip start; the first new ink only begins the instant the tip is pressed against the board and moving.
- **`NO_ECHO_RULE`** (new this round): explicitly forbids repeating, continuing, or retracing any text already on the board, and states the new row's exact sentence as the only thing to write -- this is what fixed round 24's row-2 echo defect.

## 3. The row-5 garbling defect

Row 5, chained from row 4 (the 5th hop in that segment), came back with "So this I pay." -- missing the word "week". Retried once from the same row 4 anchor: came back worse, "Sighed I pay." -- a different, more garbled result. Two failures from the same anchor, not improving on retry, rules out a one-off fluke.

Resolution: instead of continuing to push the same chain past 4 hops, row 5 was regenerated as a **fresh** text-to-video clip (new presenter generation, blank board), and rows 6-8 were chained from it as a second, independent 4-row segment. Both segments individually verified clean (no further garbling in rows 6, 7, 8).

This fix traded the garbling defect for an appearance-consistency defect (the fresh generation picked a different outfit). Round 28 addresses that trade-off directly.

## 4. Post-processing

Same trim + variable-pause + caption-overlay approach as round 23 (`postprocess.py`): each row trimmed to its writing-complete window (frames 0-128 for row 1, 22-128 for middle rows, 22-150 for row 8), stitched with varied freeze-frame pauses (0.20-0.45s) between rows, captions (reused round 22's rendered PNGs, since the script and row split are identical) burned in per original sentence.

## 5. What this means

| Question | Answer |
|---|---|
| Does I2V chaining with a no-echo rule fix round 24's text-echo defect? | Yes, verified on all 7 chained rows (every row after a text-to-video start). |
| Does onset-sync hold across a chained sequence, not just a single clip? | Yes, verified frame-by-frame on all 8 rows. |
| Can one I2V chain safely carry all 8 rows? | No -- chaining degrades past ~4 hops, causing text garbling, confirmed by a repeatable failure at hop 5. |
| Does splitting into two segments fix garbling? | Yes, but at the cost of an outfit/appearance change at the segment boundary (open problem, see round 28). |

## 6. Files

- `clips/round27_final_captioned.mp4`: final deliverable -- 9:16, 720p, ~32s, captioned.
- `clips/wan30_round27_row{1-4}.mp4`: segment 1 (I2V chained from row 1).
- `clips/wan30_round27_row5_worderror.mp4`, `clips/wan30_round27_row5_garbled2.mp4`: the two failed row-5 attempts, kept for reference.
- `clips/wan30_round27_row{5-8}.mp4`: segment 2 (row 5 regenerated fresh, 6-8 I2V chained from it).
- `run_fal_test.py`: generation script, see usage above.
- `postprocess.py`: trim/stitch/caption script.
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$5-6 total (8 successful rows + 2 retries on row 5, all 5s/720p generations).
