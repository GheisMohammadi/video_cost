[← All rounds](../../../README.md)

# Round 30: fix the per-row camera-look bug and mid-chain face/appearance drift

Status: complete. Review of round 29's full stitched video found two defects:
the presenter turns to look at the camera after every row (not just the
last), and her face looks subtly different/older by the middle of the
video. This round fixes both.

## Watch the clip

<video src="clips/round30_final_captioned.mp4" controls width="260"></video>

## 1. Summary

- **Camera-look fixed.** Round 29's per-row prompt (inherited from rounds
  27-28) ended every row with "only after the row is completely finished
  does she turn her head back to look at the camera" -- since this line was
  in every row's prompt, not just the last, it happened after every line in
  the stitched video. This round's prompts keep her eyes on the board and
  marker for the whole clip on rows 1-7, and only row 8's prompt includes
  the turn-to-camera beat.
- **Face/appearance drift root-caused and fixed.** The first attempt at
  this round's row 5 (the whiteboard-wipe handoff row, same mechanism as
  round 28-29) still showed heavy degradation: visible light-gray grain
  built up across rows 1-4 and got worse through the wipe, her shirt
  pattern changed (plain to polka-dot), and her face looked older -- the
  exact symptom reported. A retry from the same row 4 anchor came back
  nearly identical, ruling out a one-off fluke. Diagnosed cause: I2V
  chaining re-encodes its input frame every hop, and sensor-like grain
  compounds hop to hop; it isn't dark enough to be caught by the
  whiteboard-wipe's ink-detection mask, so it passes through unchanged and
  keeps building. Fixed by adding a denoising + mild unsharp-mask pass
  (`denoise_frame.py`, `cv2.fastNlMeansDenoisingColored` plus a sharpen
  step to recover edge crispness) applied to **every** chain-anchor frame
  before it's re-encoded into the next generation, not just at the wipe
  point. Rows 2-5 were regenerated with this fix; the board stayed visibly
  clean and her face/outfit stayed consistent all the way through row 8.
- Text accuracy, onset-sync, no-echo, and single-line handwriting all held,
  unchanged from round 29.
- Total duration: 31.93s, matching the target.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (row 1) and image-to-video (every other row), via fal.ai |
| Seed | 10001 |
| Rows | 8, in two chained segments (1-4, 5-8), wipe handoff at row 5 |
| Resolution / aspect | 720p, 9:16 |
| Generation time | ~105-215s per clip |
| Cost | ~$8-9 (8 final rows + 1 pre-fix row 5 attempt + 1 retry, all superseded by the denoised regeneration of rows 2-5) |

`run_fal_test.py` usage: same interface as round 29, `python3 run_fal_test.py <row 1-8> [prev_clip_path] [wipe]`. Every I2V call now denoises the extracted chain-anchor frame (`denoise_frame.py`) before any wipe step and before encoding it as `start_image_url`.

Fixes carried into every prompt:

- **`ONSET_RULE`**, **`NO_ECHO_RULE`**, **`SIZE_RULE`**: unchanged from round 29.
- **`FACE_RULE`** (new): states her face, age, and features do not change within the clip.
- **`GAZE_RULE`** (new, replaces the old universal end-of-clip camera-look line): `GAZE_RULE_HOLD` for rows 1-7 (eyes on the board/marker for the entire clip, never look at the camera), `GAZE_RULE_END_LOOK` for row 8 only (look at the camera after the sentence is finished, since it's the final line of the video).

## 3. The face-drift defect and fix

First row-5 attempt (wipe handoff from this round's own row 4): board heavily speckled with light-gray grain, shirt pattern changed to polka-dot, face visibly older -- the same symptom the review flagged. Retried once from the identical row 4 anchor: came back nearly the same (same grain pattern, same polka-dot shirt, same older-looking face), ruling out a fluke the same way round 27's garbling retry did.

Root cause: the grain isn't ink, so the whiteboard-wipe's dark-pixel inpaint mask (`gray < 180`) doesn't touch it, and it was already visible as early as rows 3-4 in the chain before the wipe ever ran. `denoise_frame.py` runs `cv2.fastNlMeansDenoisingColored` over the whole frame (not just the board region) then a mild unsharp-mask pass, applied to every row's extracted chain-anchor frame, wipe or not. Rows 2-5 were regenerated with this in the pipeline; row 5's board came back visibly clean on the first denoised attempt, with the original plain light-blue shirt and consistent face.

## 4. Post-processing

Same trim + variable-pause + caption-overlay approach as rounds 23/27/28/29 (`postprocess.py`): rows trimmed to their writing-complete window (frames 0-128 for row 1, 22-128 for middle rows, 22-150 for row 8), stitched with varied freeze-frame pauses (0.20-0.45s) between rows, captions (reused round 22's rendered PNGs) burned in per original sentence.

## 5. What this means

| Question | Answer |
|---|---|
| Does restricting the turn-to-camera prompt line to only the last row fix the per-row camera-look bug? | Yes, verified on all 8 rows -- she only looks at the camera once, at the very end. |
| Is the face/appearance drift caused by the whiteboard-wipe mechanism itself? | No -- it's generic I2V chain-hop grain accumulation, present even without the wipe and not touched by the wipe's ink-only inpaint mask. |
| Does denoising every chain-anchor frame fix it? | Yes, verified by regenerating rows 2-5 with the fix and comparing against the two pre-fix row-5 failures. |
| Open issue remaining | Row-to-row transition glitch/shake (hard cuts between clips) -- still not addressed. |

## 6. Files

- `clips/round30_final_captioned.mp4`: final deliverable -- 9:16, 720p, ~32s, captioned.
- `clips/wan30_round30_row{1-8}.mp4`: final clean chain (rows 2-5 are the denoised regenerations).
- `clips/wan30_round30_row5_noisy1.mp4`: first (pre-fix) row 5 attempt, kept for reference -- heavy grain, outfit/face drift.
- `clips/wan30_round30_row{2-4}_pre_denoise.mp4`: pre-fix versions of rows 2-4, kept for reference.
- `run_fal_test.py`: generation script, see usage above.
- `denoise_frame.py`: chain-anchor frame cleanup (denoise + sharpen), new this round.
- `wipe_board.py`: board-ink inpainting helper, reused unchanged from round 28-29.
- `postprocess.py`: trim/stitch/caption script.
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$8-9 total (8 final rows + 1 failed pre-fix attempt + 1 retry, all 5s/720p generations).
