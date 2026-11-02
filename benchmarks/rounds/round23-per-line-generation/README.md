[← All rounds](../../../README.md)

# Round 23: one generation per board row, pacing controlled in post (Oct 30 - Nov 2, 2026)

Status: complete. Round 22's 4-rows-per-generation approach produced inconsistent per-row sync (clean on some rows, overlapping on others, and one row that faded in as a whole block instead of animating). This round generates each board row as its own separate Wan 3.0 clip, stitches them, and controls the pause between rows ourselves instead of hoping the model produces one -- addressing both the leftover sync defect and the complaint that round 22's reported "~1s gap" was a fixed, unnatural value rather than something genuinely dynamic.

## Watch the clip

<video src="clips/round23_final_captioned.mp4" controls width="260"></video>

## 1. Summary

- **Every row's sync verified individually.** All 8 rows (4 per original sentence-pair, matching round 22's script) were frame-audited at tight spacing. Every row writes progressively under the marker tip -- no overlap with a neighboring row (because each is its own generation, there's no neighbor to overlap with) and no fade-in-as-a-block behavior (round 22's row 6 equivalent, "$99 on x.country", was the clearest past failure -- this round's version of that row animates correctly).
- **Pacing between rows is deliberately non-uniform.** Round 22's "~1 second gap" was never a real, controllable value -- it was one artifact of one specific generation. This round trims each row clip to its actual writing-completion point (which already varies naturally, 3.53-4.27s depending on the row) and inserts a hand-picked, varied freeze-frame pause between rows (0.20-0.45s, different for each of the 7 transitions) -- something we now actually control rather than hope for.
- **New defect found and fixed mid-round**: rows 2 and 3's first generations rendered with unexplained letterboxing (white bars top/bottom, model choosing a smaller framing within the 9:16 canvas) while every other row filled the frame edge-to-edge. Caught by direct visual comparison across all 8 final frames, not assumed. Fixed by regenerating both rows with an explicit "fills the frame edge to edge, no letterboxing" instruction; both regenerations came back full-frame.
- Total duration: 31.93s (target was 30s, 15s fallback) -- close enough to the target that it wasn't worth trimming further at the cost of pacing quality.
- Text accuracy: all 8 rows exactly correct, including "$99" and "x.country". One cosmetic artifact: row 3 ("Launched; 19") has a stray trailing period not in the original script -- noted, not fixed, since it doesn't affect legibility and chasing it would mean another regeneration.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (`alibaba/wan-3.0/text-to-video`), via fal.ai |
| Seed | 10001 for every row (same seed round 18-22 used; does not guarantee visual continuity across independent generations, same caveat as round 22) |
| Rows | 8 separate 5s generations, one per board row (list below) |
| Resolution / aspect | 720p, 9:16 (two rows regenerated with an explicit "no letterboxing" instruction) |
| Generation time | ~150-260s per clip |
| Cost | ~$0.50-0.75/clip at 5s/720p x 10 generations (8 + 2 retries for the letterboxing fix) = roughly $6-7 |

Rows (unchanged from round 22's script, split the same way):

1. "I vibe-coded my app"
2. "in a weekend."
3. "Launched; 19"
4. "signed up."
5. "So this week I pay"
6. "$99 on x.country"
7. "to grow my business"
8. "on TikTok."

Prompt per row (single-row version of round 22's eyes-on-board fix, no multi-row sequencing language needed since each clip only ever has one row):

```
vertical 9:16 video, the frame fully filled edge to edge with no letterboxing and no
padding bars at the top or bottom. wide shot, a young white woman, attractive and
fashionable, with styled hair and modern stylish clothing, standing in a bright
well-lit room in front of a whiteboard, fully visible from the waist up. the
whiteboard beside her is completely blank. at the very start she looks at the camera
for a moment, then turns her head to look at the whiteboard and keeps her eyes on the
board and on the marker tip the entire time she is writing -- she never looks at the
camera while actively writing, since no person can write accurately on a board
without looking at it. she holds a black marker, its tip touching the whiteboard
surface. the marker tip moves slowly and steadily from left to right across the
board, and a single continuous line of black ink trail appears exactly where the tip
has physically touched, one letter forming at a time, following the tip precisely --
no ink or text ever appears ahead of or away from the tip's current position, and no
part of the text ever fades in on its own; every letter is drawn by the moving tip.
The tip traces out the full sentence, "<ROW TEXT>" letter by letter, left to right, in
cursive handwriting. her eyes stay on the whiteboard and the marker tip throughout the
writing, not on the camera. only after the row is completely finished does she turn
her head back to look at the camera. the camera holds steady the entire time.
```

(The "vertical 9:16 video, fully filled... no letterboxing" opening sentence was added partway through this round, after rows 2 and 3's first attempts came back letterboxed -- see section 4.)

## 3. Post-processing: trim + variable-pause stitch

Each row's 5s clip was trimmed to its active-writing window (found by frame inspection, not assumed): the opening ~0.7s camera-glance/blink beat is cut from every row except the first (which keeps its opening beat as the video's intro), and the closing turn-to-camera beat is cut from every row except the last (which keeps its closing beat as the video's outro). This leaves each middle row as a clean 3.53s "eyes on board, writing" clip.

Between every pair of rows, a short freeze-frame hold (the last frame of the preceding row, held static) is inserted -- durations deliberately varied per transition: 0.20, 0.35, 0.25, 0.40, 0.30, 0.45, 0.20 seconds, rather than one repeated value. This is the actual fix for the "fixed-feeling gap" complaint: round 22 had no real control over inter-row pacing at all, so asking the model for "dynamic, natural" timing via prompt wording would not have worked -- pacing has to be set in post, where it now is.

Mid-screen captions (one per original sentence, reusing round 22's rendered PNG overlays) are timed to the new, recalculated row/pause boundaries.

## 4. The letterboxing defect (found and fixed mid-round)

After generating all 8 rows, a full comparison of every row's final frame found rows 2 and 3 rendered with white padding bars top and bottom -- a smaller, letterboxed framing within the 9:16 canvas -- while rows 1 and 4-8 filled the frame completely. This was not visible from a single row's own frames in isolation; it only showed up when comparing all 8 side by side, which is why it wasn't caught by row-by-row verification alone.

Both rows were regenerated with an explicit "frame fully filled edge to edge, no letterboxing" instruction added to the prompt. Both regenerations came back full-frame, matching the other 6 rows. The original letterboxed clips are kept as `clips/wan30_round23_row{2,3}_letterboxed.mp4` for reference.

## 5. What this means

| Question | Answer |
|---|---|
| Does generating one row per clip fix the sync defects from round 22? | Yes -- every row verified individually at tight frame spacing, both the overlap failure mode and the fade-in-as-a-block failure mode are gone. |
| Is the inter-row pacing actually dynamic now? | Yes, in the sense that matters: it's deliberately varied and fully under our control (0.20-0.45s per transition), rather than an unexplained, uncontrollable artifact of a single generation as round 22's was. |
| Does this approach have new risks round 22 didn't? | Yes -- framing can vary per-generation (the letterboxing defect), which only shows up when comparing clips side by side, and there are now 8 continuity boundaries instead of 1, each carrying round 22's already-flagged risk that independent generations don't preserve outfit/background. |
| Is the continuity-at-the-cut issue from round 22 resolved? | No, and it's not expected to be -- this round made more cuts (8, not 2), which is the same accepted tradeoff flagged in the round 23 plan, not a new problem. |

## 6. Still to do / open for direction

1. **Continuity across 8 cuts**: unchanged from round 22's open question, now with more cut points. Still needs a decision on whether this reads as acceptable or needs an image-to-video continuation approach.
2. The stray period after "Launched; 19" (row 3) and the earlier-noted capitalization inconsistency ("Signed up." vs "signed up.") are minor and left as-is -- flagging in case they matter for a client-facing deliverable.
3. If the per-row approach is accepted as the new standard, it should be documented as the working template (framing instruction included) instead of round 22's multi-row approach, which is now superseded by evidence that it doesn't reliably sync.

## 7. Files

- `clips/round23_final_captioned.mp4`: final deliverable -- 9:16, 720p, ~32s, captioned.
- `clips/round23_stitched.mp4`: pre-caption stitched clip.
- `clips/wan30_round23_row{1-8}.mp4`: the 8 raw row generations (rows 2 and 3 are the regenerated, full-frame versions).
- `clips/wan30_round23_row{2,3}_letterboxed.mp4`: the original letterboxed generations, kept for reference.
- `clips/trim_row{1-8}.mp4`, `clips/pause_{1-7}.mp4`: intermediate trimmed/pause segments.
- `raw/raw_record_wan30_round23_row{N}.json`: generation records per row.
- `run_fal_test.py`: generates one row. Usage: `python3 run_fal_test.py <row_index 1-8>`. Reads the API key from `server/falAPI.txt` (git-ignored, never printed).
- `postprocess.py`: trims each row to its writing-complete window and stitches with variable pauses.
- `PLAN.md`: this round's plan, frozen before running.

## 8. Cost

~$6-7 total (8 rows + 2 letterboxing-fix retries, all 5s/720p generations), plus two failed submissions that errored out on a transient network issue before any generation started (no cost). Free local post-processing (ffmpeg/PIL).
