# Round 33: fix round 32's line-geometry and text defects with an explicit, position-anchored diagram layout

Review of round 32's three clips found: in all three, the text rendered on
the board was wrong/garbled, and in all three, the lines did not connect
the items they were supposed to connect (Kling: line positions off, lines
appearing out of nowhere; Seedance: wrong points connected; Veo: wrong
points connected).

## Diagnosis

Round 32's prompt described the pre-existing diagram only vaguely
("several small, neatly arranged technical labels and boxes... representing
a simple software architecture diagram") and the connection instructions
referred to boxes only by relative description ("two existing boxes", "one
upper box to two lower boxes") without saying which specific boxes, where
they are, or which edge the line should touch. With no fixed layout to
anchor to, each model invented its own box positions and picked its own
(often wrong) connection points. This mirrors a lesson already learned in
the whiteboard-text rounds: vague or long-form content gets garbled; short,
explicit, position-anchored content renders more reliably.

## Fix

- **Explicit fixed layout**: exactly 5 boxes, each with a single bold
  letter label (A-E), each given an explicit position (top-center,
  mid-left, mid-right, bottom-left, bottom-right) and explicit relative
  relationship to the others (B and C directly across from each other, D
  directly below B, E directly below C).
- **Single empty "hub point"** defined exactly midway between B and C, so
  all 4 lines (1 vertical + 1 horizontal + 2 diagonal) have an unambiguous
  shared meeting point instead of a vague "near the top" or "another
  position".
- **Explicit start/end points named by box + edge** for every line (e.g.
  "from A's bottom edge straight down to the hub point"), not by ordinal
  description ("two existing boxes").
- **Single-letter labels only** (A-E), not multi-word text, since short
  content is what survived the whiteboard-text rounds' accuracy checks.
- Same 3 tools as round 32 (Kling 3.0 Pro, Seedance 2.0, Veo 3.1), same
  aspect ratio/resolution choices, same character-limit workaround for
  Kling (`prompt_kling.txt`, condensed to fit under 2500 chars while
  keeping every position/connection detail).

## What to check per clip

- Do the five boxes render in the described fixed layout (A top-center, B
  mid-left, C mid-right, D below B, E below C)?
- Does the vertical line run from A to the hub point (not some other
  point)?
- Does the horizontal line run from B to C through the hub point?
- Do the two diagonals run from the hub point to D and to E specifically
  (not to the wrong boxes)?
- Are the five labels legible single letters, not garbled multi-word text?
- Same physical-plausibility checks as round 32 (progressive line growth
  under the tip, no pre-formed/floating lines, fixed camera, look-at-camera
  only at the end).

## Budget

Same ~$5.15 as round 32 (Kling ~$1.12, Seedance ~$2.42, Veo ~$1.60 for 8s),
one attempt per tool. Confirm with the user before any retries.
