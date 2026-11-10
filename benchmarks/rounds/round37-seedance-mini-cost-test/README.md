[← All rounds](../../../README.md)

# Round 37: cost test -- Seedance 2.0 Mini vs. Seedance 2.0 Fast

Status: complete (single-attempt feasibility check). User directive:
generation with Seedance (and other models) is expensive; test a cheaper
tier to see if quality holds up well enough to use it going forward.

## Watch the clip

<video src="clips/round37_seedance_mini.mp4" controls width="260"></video>

## 1. Summary

- Found `bytedance/seedance-2.0/mini/text-to-video` on fal.ai -- about 36%
  cheaper per second than the "fast" tier used in every round so far
  (mini: $0.1547/s at 720p vs. fast: $0.2419/s at 720p). No other cheaper
  tier ("lite"/"standard") exists for Seedance 2.0 besides fast and mini.
- Ran the exact same prompt/payload that produced round 36's accepted
  deliverable (4 lines of text, rectangle around "vibe-coded", circle
  around "$99", underline under "x.country", 15s, 720p, 16:9) through the
  mini endpoint instead of fast, for a direct apples-to-apples comparison.
- **Result: noticeably worse quality on this one attempt.** Lines written
  out of order (line 3 started before line 2 finished), a duplicate,
  floating "$99" with its own circle appearing separately from the real
  text line, the actual line read "$999 on x.country" (an extra digit
  typo), an odd stray period before "19" in "Launched 19.", and an extra
  stray stroke under the rectangle.
- One attempt isn't conclusive given the attempt-to-attempt variance seen
  on the fast tier too (rounds 35/36 needed 2-3 tries each), but it was
  enough of a quality drop to motivate round 38's test of whether
  finer-grained line-by-line chaining (the structure that worked for plain
  text in rounds 27-31) could make the cheaper tier reliable.

## 2. What was run

| Item | Value |
|---|---|
| Model | `bytedance/seedance-2.0/mini/text-to-video` |
| Resolution / aspect | 720p, 16:9 |
| Duration | 15s |
| Attempts | 1 (feasibility check, not a full production run) |
| Generation time | ~230s |
| Cost | ~$2.32 (vs. ~$3.63 for the same clip on the fast tier) |

`run_fal_test.py` usage: `python3 run_fal_test.py` (no arguments).

## 3. What this means

| Question | Answer |
|---|---|
| Is Seedance Mini cheaper than Fast? | Yes, ~36% cheaper per second at 720p. |
| Does Mini hold up on the same single-clip text+annotation task that Fast passed in round 36? | No, not on this attempt -- out-of-order writing, a duplicated/floating annotation, a text typo, and a stray mark all appeared. |
| Is this conclusive proof Mini can't do this task? | No -- only one attempt was run, and both tiers have shown real variance before. Round 38 tests whether restructuring the task (one clip per line/annotation, chained, matching the whiteboard rounds' approach) changes the picture. |
| Open issue | Whether finer-grained chaining makes Mini reliable enough to use for cost savings -- addressed in round 38. |

## 4. Files

- `clips/round37_seedance_mini.mp4`: the generated clip.
- `prompt.txt`: identical to round 36's final prompt (copied unchanged for a direct comparison).
- `run_fal_test.py`: generation script, see usage above.
- `raw/raw_record_round37_seedance_mini.json`: generation metadata.
- `raw/frame_{early,mid,last}.png`: sampled frames used for the visual review in section 1.
- `PLAN.md`: this round's plan, frozen before running.

## 5. Cost

~$2.32 total, one attempt.
