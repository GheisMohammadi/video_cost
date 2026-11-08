[← All rounds](../../../README.md)

# Round 33: fix round 32's line-geometry and text defects with an explicit, position-anchored diagram layout

Status: complete. Review of round 32's three clips found wrong/garbled
board text and incorrect line connections in all three tools. This round
replaces the vague box/connection description with an explicit, fully
position-anchored 5-box layout and single-letter labels.

## Watch the clips

<video src="clips/round33_kling.mp4" controls width="260"></video>
<video src="clips/round33_seedance.mp4" controls width="260"></video>
<video src="clips/round33_veo.mp4" controls width="260"></video>

(left to right: Kling 3.0 Pro, Seedance 2.0, Veo 3.1)

## 1. Summary

- **Diagnosis of round 32's defects**: the prompt described the diagram
  only vaguely ("several small, neatly arranged technical labels and
  boxes... representing a simple software architecture diagram") and
  referred to connections by relative description only ("two existing
  boxes", "one upper box to two lower boxes") -- no fixed positions, no
  named boxes, no explicit start/end points. Each model invented its own
  layout and picked its own (often wrong) connection points.
- **Fix**: exactly 5 boxes, each with a single bold letter (A-E), each
  given an explicit position (A top-center, B mid-left, C mid-right, D
  bottom-left/below B, E bottom-right/below C), plus a single named "hub
  point" exactly midway between B and C where all 4 lines (1 vertical + 1
  horizontal + 2 diagonal) meet. Every line's start/end was named by box +
  edge, not by ordinal description.
- **Result: Kling 3.0 Pro and Seedance 2.0 both nailed the layout and
  connections exactly as specified** -- all 5 boxes in the correct
  positions, all 4 lines meeting cleanly at the hub point, labels
  rendering as clean single letters (fixing round 32's garbled-text
  defect too).
- **Veo 3.1 regressed this round** -- placed A/B/C all in a single top row
  instead of the described top-center/mid-left/mid-right layout, and the
  diagonal/vertical connections don't follow the hub-point design. Worst
  of the three this time, a reversal from round 32 where it was the most
  visually polished.
- Confirms the lesson already learned in the whiteboard-text rounds:
  short, explicit, position-anchored content renders far more reliably
  than vague or long-form descriptions.

## 2. What was run

| Item | Value |
|---|---|
| Models | Same as round 32: `fal-ai/kling-video/v3/pro/text-to-video`, `bytedance/seedance-2.0/fast/text-to-video`, `fal-ai/veo3.1` |
| Prompt | New, explicit 5-box/hub-point layout (`prompt.txt`); Kling again required a condensed version (`prompt_kling.txt`) to fit its 2500-character cap |
| Aspect ratio | 16:9, same as round 32 |
| Generation time | ~148-359s per clip |
| Cost | ~$5.15, same as round 32, one attempt per tool, no retries |

`run_fal_test.py` usage: `python3 run_fal_test.py <kling|seedance|veo>`.

## 3. What this means

| Question | Answer |
|---|---|
| Does an explicit, position-anchored layout fix round 32's wrong-connection defect? | Yes, for Kling and Seedance -- both matched the specified layout and connections exactly. Not for Veo this round. |
| Does it fix round 32's garbled-text defect? | Yes, for Kling and Seedance -- single-letter labels rendered cleanly. Veo's labels were also legible single letters despite its layout/connection errors. |
| Is Veo's regression a layout-instruction-following problem specifically, or something else? | Open question -- worth a follow-up with an even more rigidly spelled-out layout before concluding Veo can't do this reliably. |
| Open issue | None raised yet for Kling/Seedance on this diagram; Veo's layout-following needs another look if it's to stay in the comparison set. |

## 4. Files

- `clips/round33_kling.mp4`, `clips/round33_seedance.mp4`, `clips/round33_veo.mp4`: the three generated clips.
- `prompt.txt`: explicit 5-box/hub-point layout prompt, used verbatim for Seedance and Veo.
- `prompt_kling.txt`: condensed version used only for Kling (character-limit workaround), same layout/connection details.
- `run_fal_test.py`: generation script, see usage above.
- `raw/raw_record_round33_{kling,seedance,veo}.json`: per-tool generation metadata.
- `raw/*_frame_{early,last}.png`: sampled frames used for the visual review in section 1.
- `PLAN.md`: this round's plan, frozen before running.

## 5. Cost

~$5.15 total (Kling ~$1.12, Seedance ~$2.42, Veo ~$1.60), one attempt per tool, no retries.
