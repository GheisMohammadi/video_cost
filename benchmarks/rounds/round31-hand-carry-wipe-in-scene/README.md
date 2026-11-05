[← All rounds](../../../README.md)

# Round 31: carry the hand/head across row cuts, fold the board-wipe into one continuous shot

Status: complete. Review of round 30's full video found two more defects: a
hand-position jump cut at every row transition, and her face still changing
at the board-wipe handoff. This round fixes both.

## Watch the clip

<video src="clips/round31_final_captioned.mp4" controls width="260"></video>

## 1. Summary

- **Row-transition jump cut fixed.** Every row's clip (except the last) now
  ends with her moving the marker hand down to the start of the next blank
  line, head slowly turning to follow it -- not cutting back to the camera.
  The next row's I2V chain starts from that exact frame, so the hand is
  already in position at the next row's start; no more teleport at the cut.
- **Board-wipe face-change fixed.** Instead of round 28-30's digital
  inpaint-the-board-clean-on-a-still-frame handoff, row 4's own prompt now
  includes picking up a board eraser, wiping the board clean, and moving
  the marker back to the top-left start position, all as one continuous
  in-scene generation. Row 5 then chains normally from that real last
  frame. Verified: the board is fully blank, the eraser is back on its
  tray, and her face/outfit carry through unbroken into row 5.
- **Two rounds of prompt tightening were needed to get the hand-carry
  working cleanly** (see section 3) -- the first version caused the model
  to re-trace/echo already-written text during the hand-move, and a
  tightened version still caused row 3 to overwrite row 2's line instead
  of using the blank line below. Both were fixed with more explicit
  wording, not by abandoning the approach.
- Text accuracy: 8/8 rows exact after the fixes. She turns to camera only
  on the final row (row 8), consistent with round 30.
- Total duration: 31.93s, matching the target.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (row 1) and image-to-video (every other row), via fal.ai |
| Seed | 10001 |
| Rows | 8, single continuous chain (no separate wipe-handoff row -- the wipe is inside row 4's own generation) |
| Resolution / aspect | 720p, 9:16 |
| Generation time | ~120-235s per clip |
| Cost | ~$7-8 (8 final rows + 1 failed row-1 attempt from a pre-top-up/stale-key 403 + 2 retries of row 3 while tightening the prompt) |

`run_fal_test.py` usage: `python3 run_fal_test.py <row 1-8> [prev_clip_path]`. No `wipe_board.py` and no "wipe" argument this round -- the wipe is entirely in-prompt for row 4. Every I2V call still denoises the extracted chain-anchor frame (`denoise_frame.py`, carried over from round 30, fixes a different problem -- chain-hop grain accumulation -- that's independent of this round's fixes).

Fixes carried into every prompt:

- **`ONSET_RULE`**, **`SIZE_RULE`**, **`FACE_RULE`**: unchanged from round 30.
- **`CARRY_HAND_RULE`** (new): every row except the last and except row 4 ends with the marker lifting off the board, moving through the air to the next blank line (explicitly: no ink, no mark, no trace during the move), head slowly turning to follow it.
- **`WIPE_AND_RESET_RULE`** (new, row 4 only): after writing "signed up.", pick up an eraser, wipe the whole board clean, set the eraser down, move the marker to the top-left corner -- one continuous motion, head following the hand throughout.
- **`END_LOOK_RULE`** (row 8 only, same as round 30's `GAZE_RULE_END_LOOK`): look at the camera only after the final sentence finishes.
- **`NO_ECHO_RULE`** (strengthened) and **`STRAY_MARK_RULE`** (new): see section 3.

## 3. The echo/overwrite defects and fixes

**Attempt 1:** the first version of `CARRY_HAND_RULE` just said "move the hand to a blank line below, don't look at the camera." In practice, row 1's hand-carry motion re-traced part of its own text onto the new line ("I vibe...ed"), and row 2 then continued that echo, writing "I vibe-coded in weekend." instead of "in a weekend." Fixed by rewriting `CARRY_HAND_RULE` to explicitly describe the marker lifting off the board surface during the move (no ink, no mark, no trace, no retracing while airborne), and strengthening `NO_ECHO_RULE` to call out the previous line by name.

**Attempt 2:** with that fix in place, rows 1-2 were clean, but row 3 overwrote row 2's existing line ("in a weekend;19", with "Launched" dropped entirely) instead of writing on the blank line below it. A retry from the identical row-2 anchor reproduced the same defect, ruling out a fluke. Root cause: the hand-carry motion leaves a short, faint stray line at the rest position (an artifact of the "ink leaks slightly" residual from attempt 1's partial fix), and the model was treating that stray mark as "text already started here" to continue or merge into. Fixed by adding `STRAY_MARK_RULE`, explicitly telling the model that mark is not text and not something to preserve or write around, and clarifying in `NO_ECHO_RULE` that the target line is two full lines below the topmost finished sentence, separate from anything already there. Retried row 3 with this fix: "Launched; 19" wrote correctly on its own line. Rows 4-8 then chained cleanly with no further echo or overwrite issues.

The thin stray line itself (a few-pixel mark where the hand rests between rows) remained a minor, non-compounding cosmetic artifact through the rest of the chain -- it never again caused text to merge or get dropped.

## 4. Post-processing

Same trim + variable-pause + caption-overlay approach as rounds 23/27-30 (`postprocess.py`): rows trimmed to their writing-complete window (frames 0-128 for row 1, 22-128 for middle rows, 22-150 for row 8) -- stopping before each row's hand-carry-to-next-line motion, since that motion exists only to anchor the next I2V hop and isn't meant to be shown in the final cut. Stitched with the same varied freeze-frame pauses (0.20-0.45s) between rows, captions (reused round 22's rendered PNGs) burned in per original sentence.

## 5. What this means

| Question | Answer |
|---|---|
| Does carrying the hand/head across the cut eliminate the row-boundary jump? | Yes, verified on all 8 rows -- each row opens with the hand already at the next line's start, not teleporting there. |
| Does folding the wipe into row 4's own generation fix the face-change-at-handoff defect? | Yes -- row 4's last frame shows a fully blank board, eraser back on its tray, and consistent face/outfit carried into row 5's opening frame. |
| Was the hand-carry approach reliable on the first attempt? | No -- it took two rounds of prompt tightening (killing in-air ink leakage, then explicitly discounting the resulting stray mark) before it held up across a full 8-row chain. |
| Open issue remaining | None flagged in this round's review; the long-standing row-to-row "glitch/shake" item from rounds 27-30 is specifically what this round's hand-carry fix targets, and was not observed in the final chain. |

## 6. Files

- `clips/round31_final_captioned.mp4`: final deliverable -- 9:16, 720p, ~32s, captioned.
- `clips/wan30_round31_row{1-8}.mp4`: final clean chain.
- `clips/wan30_round31_row3_attempt1.mp4`, `clips/wan30_round31_row3_attempt2.mp4`: the two pre-fix row-3 attempts, kept for reference (echo/overwrite defects described in section 3).
- `run_fal_test.py`: generation script, see usage above.
- `denoise_frame.py`: chain-anchor frame cleanup (denoise + sharpen), carried over unchanged from round 30.
- `postprocess.py`: trim/stitch/caption script.
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$7-8 total (8 final rows + 1 failed row-1 attempt from a transient stale-key 403 right after the fal.ai balance top-up + 2 row-3 retries during prompt tightening, all 5s/720p generations).
