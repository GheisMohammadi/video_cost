[← All rounds](../../../README.md)

# Round 34: fix Seedance's D/E endpoint, overshoot, and arrow-pop-in defects

Status: complete. Boss directive: round 33's Seedance result was good
enough to keep testing on its own, so this round drops Kling/Veo and
focuses only on Seedance 2.0. Review of round 33's Seedance clip found
three defects on the two diagonal lines (hub point -> D, hub point -> E):
they connected to the wrong point on the box, left a small extra
correction stroke at the endpoint, and looked like arrows "appearing
suddenly" (popping in rather than growing progressively).

## Watch the clip

<video src="clips/round34_seedance.mp4" controls width="260"></video>

## 1. Summary

- **All three flagged defects fixed.** The diagonal lines now land exactly
  at the midpoint of D's and E's top edges, no stray correction stroke
  remains at either endpoint, and both diagonals grow progressively under
  the marker tip at the same pace as the other lines -- no pop-in,
  verified by checking a mid-drawing frame mid-stroke.
- **New, minor defect found**: the B -> C "horizontal" line no longer
  renders as a flat horizontal line -- it comes out as two diagonal
  segments from B and C converging at the hub point, the same slope as
  the D/E diagonals, so the horizontal and diagonal lines are visually
  indistinguishable in shape. Reviewed with the user and accepted as-is
  (the three originally flagged defects matter more than this cosmetic
  one); not pursued further this round.
- Labels, layout, and hub-point structure all held from round 33 -- five
  boxes in the correct positions, clean single-letter labels, no garbled
  text.

## 2. What was run

| Item | Value |
|---|---|
| Model | `bytedance/seedance-2.0/fast/text-to-video` only (Kling and Veo dropped this round per boss direction) |
| Resolution / aspect | 720p, 16:9 |
| Duration | 10s |
| Generation time | ~241s |
| Cost | ~$2.42, one attempt, no retries needed |

`run_fal_test.py` usage: `python3 run_fal_test.py` (no arguments -- Seedance only).

## 3. Fix

Same explicit 5-box/hub-point layout as round 33, with the diagonal-line
steps and critical-requirements section tightened:

- **Exact endpoint named, not just the box**: "precisely at the midpoint
  of its top edge", explicitly ruling out a corner, inside the box, or
  beside it.
- **Explicit no-arrowhead rule**: lines described as plain strokes with
  "no arrowhead, no arrow styling, no triangular tip, no dot, no circle...
  at either end."
- **Explicit no-overshoot/no-correction rule**: "the instant the marker
  tip reaches a line's stated endpoint, the marker lifts immediately...
  no extra tick mark, no small correction stroke, no short secondary
  segment, no double-back, no wiggle."
- **Explicit equal-pace growth for the diagonals**: called out specifically
  that the two diagonal lines must grow at the same gradual, visible pace
  as the vertical/horizontal lines, directly targeting the "appear
  suddenly" symptom.

## 4. What this means

| Question | Answer |
|---|---|
| Does naming the exact endpoint (box edge midpoint, not just "the edge") fix the wrong-connection-point defect? | Yes, verified on both D and E. |
| Does an explicit no-overshoot rule stop the stray correction stroke? | Yes, no extra marks found at either diagonal's endpoint. |
| Does an explicit equal-pace-growth rule stop the arrow-pop-in look? | Yes, verified mid-drawing -- the diagonal grows continuously under the tip, same as the vertical/horizontal lines. |
| Open issue | The B->C line renders as two diagonals meeting at the hub instead of a flat horizontal line -- accepted as a minor cosmetic defect this round, not fixed. |

## 5. Files

- `clips/round34_seedance.mp4`: the generated clip.
- `prompt.txt`: round 33's layout prompt with the diagonal-endpoint/no-overshoot/no-arrowhead/equal-pace fixes added.
- `run_fal_test.py`: generation script (Seedance only), see usage above.
- `raw/raw_record_round34_seedance.json`: generation metadata.
- `raw/frame_{early,mid,last}.png`: sampled frames used for the visual review in section 1.
- `PLAN.md`: this round's plan, frozen before running.

## 6. Cost

~$2.42 total, one attempt, no retries.
