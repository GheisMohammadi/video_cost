# Round 30: keep eyes on the board between rows, reduce face drift

Round 29 fixed the line-wrap overflow and verified clean sync/consistency on
all 8 rows, but review of the full stitched video found two defects:

1. **She looks at the camera after every row, not just the last.** Every
   per-row prompt in round 29 (inherited unchanged from rounds 27-28) ends
   with "only after the row is completely finished does she turn her head
   back to look at the camera." Since this line is in every row's prompt,
   not just the final row's, it happens after each line in the stitched
   video. It should only happen once, at the very end of row 8.
2. **Her face looks subtly older/different by the middle of the video.**
   Despite the whiteboard-wipe handoff keeping every pixel outside the board
   rectangle byte-identical at the row-5 handoff, the model still drifts her
   appearance somewhat across the I2V chain. The handoff frame is pixel-
   locked, but generation itself is not perfectly appearance-stable hop to
   hop.

## Fix

- Per-row prompt branches: rows 1-7 keep her eyes on the whiteboard and the
  marker tip for the entire clip, never turning to the camera; only row 8's
  prompt includes the "turn to camera at the end" instruction.
- Add an explicit face/appearance-stability instruction to every I2V prompt
  (same exact face, same exact age, no change to her features) to reduce
  drift, on top of the existing "same woman, same outfit" framing already
  used.
- Keep everything else unchanged from round 29: I2V chaining, `ONSET_RULE`,
  `NO_ECHO_RULE`, `SIZE_RULE`, whiteboard-wipe handoff at row 5.

## Test order

Same 8-row chain as round 29: rows 1-4 chained from a text-to-video row 1,
row 5 wipe-handoff, rows 6-8 chained from row 5. Check each row's last frame
for (a) she is still looking at the board, not the camera, until row 8, and
(b) face consistency against the previous row's last frame.

## Budget

~8 rows x ~$0.6-0.8 = ~$5-6, same as rounds 27-29.
