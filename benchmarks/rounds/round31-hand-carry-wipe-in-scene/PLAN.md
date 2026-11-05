# Round 31: carry the hand/head across row cuts, fold the board-wipe into one continuous shot

Review of round 30's full video found two more defects:

1. **Jump cut at every row transition.** Each row's clip ends right after
   the marker finishes the last letter, at the end of the sentence just
   written. The next row's I2V chain starts from that same frame, so the
   next generation has to teleport the hand from "end of row N" to "start
   of row N+1" within its own opening beat -- a visible hand-position jump
   at every cut.
2. **Face still changes at the board-wipe handoff.** Round 30 fixed the
   grain-driven drift across ordinary chain hops, but the wipe handoff
   itself (digitally inpainting the board clean on a still frame, then
   prompting a fresh I2V continuation from that doctored frame) is still a
   real discontinuity -- the model has no continuous motion to anchor the
   same face to, only a static before/after image pair.

## Fix

- **Hand/head carry-over.** Every row's prompt (except the last) now ends
  with her moving the marker tip down to the start of the next blank line
  *within that same clip*, with her head slowly turning to follow the
  hand's movement rather than cutting back to the camera. The next row's
  I2V chain then starts from a frame where the hand is already in position
  -- no teleport, no jump cut. Row 1 (text-to-video) and rows 2-3, 5-7 all
  get this treatment; only row 8 (the last) skips it, since there's no
  "next row" to move to.
- **Board-wipe folded into row 4's own generation.** Instead of digitally
  erasing the board on a still frame and starting a fresh I2V prompt from
  the doctored image (round 28-30's approach), row 4's prompt now
  continues in one shot: after writing "signed up.", she picks up a board
  eraser/cleaner, wipes the board clean left to right, then moves the
  marker back to the top-left start position (same spot row 1 started).
  Row 5 then chains normally from that real last frame -- no inpainting,
  no `wipe_board.py`, no separate "wipe" prompt branch. This replaces a
  static-frame discontinuity with continuous motion the model can anchor
  the same face to.
- Keep round 30's `denoise_frame.py` grain-cleanup pass on every
  chain-anchor frame (fixes a different problem -- compounding sensor
  grain -- and is still needed regardless of the wipe mechanism change).
- Keep `ONSET_RULE`, `NO_ECHO_RULE`, `SIZE_RULE`, `FACE_RULE` unchanged
  from round 30.

## Test order

Same 8-row chain. Check every row's last frame for: hand already
positioned at the next row's start (not mid-air, not still at the previous
line), head oriented toward where it's looking (board, not camera, except
row 8), and face/outfit continuity against the previous row.

## Budget

~8 rows x ~$0.6-0.8 = ~$5-6, same as prior rounds. No separate wipe-retry
budget needed since the wipe is now part of row 4's normal generation.
