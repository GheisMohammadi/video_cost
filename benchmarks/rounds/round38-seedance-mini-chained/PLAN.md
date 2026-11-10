# Round 38: apply the whiteboard rounds' line-by-line chaining to the text+annotation task, on Seedance Mini

User insight: rounds 36/37's single-clip attempts at "4 lines of text + 3
annotations" kept jumbling content (dropped lines, merged lines, duplicated
floating text, wrong-order writing) because too much action was crammed
into one generation. The whiteboard rounds (27-31) solved exactly this
problem for plain text by generating one short clip per line, chained via
I2V from the previous clip's last frame, with the hand carried to the next
position so there's no jump cut. This round applies that same structure
here: one clip per text line, then one clip per annotation (rectangle,
circle, underline), each chained from the previous clip's last frame.

User also asked to test whether this finer-grained chaining fixes round
37's quality problems on Seedance Mini (the cheaper tier), rather than
reverting to the more expensive "fast" tier.

## Structure (7 chained clips)

1. Text-to-video: write line 1, "I vibe-coded my app". Carry hand to line
   2's start at the end (same `CARRY_HAND_RULE` mechanism as round 31).
2. I2V, chained from clip 1: write line 2, "in a weekend. Launched 19."
   Carry hand to line 3's start.
3. I2V, chained from clip 2: write line 3, "So this week I pay". Carry
   hand to line 4's start.
4. I2V, chained from clip 3: write line 4, "$99 on x.country". Instead of
   carrying to a new text line, carry the hand up to the position needed
   to start drawing the rectangle around "vibe-coded" in line 1.
5. I2V, chained from clip 4: draw a rectangle around "vibe-coded" only.
   Carry hand down to the position needed to start drawing the circle
   around "$99".
6. I2V, chained from clip 5: draw a circle around "$99" only. Carry hand
   to the position needed to start the underline under "x.country".
7. I2V, chained from clip 6: draw the underline under "x.country" only.
   This is the final clip -- she looks at the camera at the end instead of
   carrying to another position.

Each clip is 5s at 720p/16:9, matching the whiteboard rounds' per-row
length. `denoise_frame.py` (carried over unchanged from round 30) cleans
each chain-anchor frame before it's re-encoded into the next generation,
guarding against I2V chain-hop grain accumulation the same way it did in
the whiteboard rounds.

## Carried-forward rules (from rounds 27-36)

- `ONSET_RULE`: ink only appears under the moving tip, never ahead of it.
- `NO_ECHO_RULE`: never retrace or repeat a previous line's text.
- `SIZE_RULE`: compact handwriting, stays on one line, never wraps.
- `FACE_RULE`: face/age/features don't change within or across clips.
- `STRAY_MARK_RULE`: a short mark already at the tip's rest position is
  not text and isn't preserved or written around.
- `NO_OVERSHOOT_RULE`: the marker lifts the instant a stroke reaches its
  endpoint -- no extra tick, no correction stroke, no decorative mark.
- `NO_REFLECTION_RULE`: exactly one woman visible throughout, no
  ghost/mirrored double (round 36's fix).
- `CARRY_HAND_RULE` / a new `CARRY_TO_ANNOTATION_RULE`: hand moves to the
  next position with the head following, no jump cut, no stray ink during
  the move (round 31's fix, extended here to also cover the
  text-to-annotation handoff, which round 31 never needed).
- `END_LOOK_RULE`: only the final clip (step 7) ends with looking at the
  camera.

## What to check

- Does every line/annotation render correctly on its own clip (much
  smaller ask per generation than cramming everything into one)?
- Does the hand carry cleanly between every step, including the
  text-to-rectangle handoff (new, not previously tested)?
- Does Seedance Mini -- which jumbled content badly in round 37's
  single-clip test -- hold up once each clip only has one simple action to
  do?
- Does chain-hop grain/face drift reappear across 7 hops (round 30's
  original problem), now that `denoise_frame.py` is back in the pipeline?

## Budget

7 clips x 5s x $0.1547/s (mini, 720p) = ~$5.41 total for one clean pass,
assuming no retries. Given each clip is a much smaller/simpler ask than
round 37's single clip, fewer retries are expected than in rounds 35/36's
single-clip attempts -- confirm with the user before any retries anyway.
