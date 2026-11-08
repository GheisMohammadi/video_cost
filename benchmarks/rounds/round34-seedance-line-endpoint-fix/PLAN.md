# Round 34: fix Seedance's D/E endpoint and arrow-pop-in defects

Boss directive: round 33's Seedance result was good enough to keep testing
on its own (Kling and Seedance both matched the layout well, but boss is
focusing only on Seedance going forward). Review of round 33's Seedance
clip found three remaining defects, all localized to the two diagonal
lines (hub point -> D, hub point -> E):

1. The diagonal lines connect to the wrong point on Box D / Box E (not
   landing precisely where intended).
2. After each diagonal line reaches its endpoint, a small extra stroke is
   drawn there -- a correction/overshoot mark not asked for.
3. The line endings look like arrows that "appear suddenly" -- i.e. an
   arrowhead-like shape pops in at the endpoint instead of the line
   growing there progressively like the vertical/horizontal lines did.

## Fix

Same explicit 5-box/hub-point layout as round 33, with the diagonal-line
instructions (steps 4-5) and the critical-requirements section tightened:

- **Exact endpoint named, not just the box**: "precisely at the midpoint
  of its top edge", explicitly ruling out a corner, inside the box, or
  beside it -- not just "ending exactly at the top edge of Box D" as
  round 33 said.
- **Explicit no-arrowhead rule**: lines are described as plain strokes
  with "no arrowhead, no arrow styling, no triangular tip, no dot, no
  circle... at either end."
- **Explicit no-overshoot/no-correction rule**: "the instant the marker
  tip reaches a line's stated endpoint, the marker lifts immediately...
  no extra tick mark, no small correction stroke, no short secondary
  segment, no double-back, no wiggle."
- **Explicit equal-pace growth for the diagonals**: added a line calling
  out specifically that the two diagonal lines must grow at the same
  gradual, visible pace as the vertical/horizontal lines, "not pop into
  existence, not flash on screen" -- directly targeting the "appear
  suddenly" symptom.

Only Seedance 2.0 is tested this round (`bytedance/seedance-2.0/fast/text-to-video`),
per the boss's direction to stop comparing tools and focus there since its
results were good enough. No Kling-specific trimmed prompt needed this
round.

## What to check

- Do both diagonal lines land at the exact midpoint of D's and E's top
  edges (not a corner, not inside, not beside)?
- Do the diagonals grow progressively under the tip, same visible pace as
  the vertical/horizontal lines (no sudden pop-in)?
- Is there any extra mark/stroke left at either diagonal's endpoint after
  it's drawn?
- Same checks carried from round 33: correct 5-box layout, hub point, no
  garbled text, camera fixed, look-at-camera only at the end.

## Budget

~$2.42 for one Seedance attempt (10s, 720p). Confirm with the user before
any retries.
