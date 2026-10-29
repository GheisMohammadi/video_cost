[← All rounds](../../../README.md)

# Round 22: new script, visible woman presenter, portrait 9:16, 30s via stitched segments (Oct 29, 2026)

Status: complete, one open issue flagged for review. Boss directive: new script about vibe-coding/TikTok ad spend, progressive whiteboard writing (not pre-written), presenter changed to a woman, mid-screen caption overlay added in post, output always 9:16/720p/30s (15s fallback).

**Correction 1 (eye gaze)**: the first version of this round had the presenter looking at the camera while actively writing, which is not something a person can physically do while writing accurately. The prompt originally included "she glances at the camera occasionally but keeps writing" -- removed and replaced with an explicit instruction that she looks at the camera only before writing starts and after both lines are complete, and keeps her eyes on the board/marker tip the entire time she is writing. Both segments were regenerated with the corrected prompt; text accuracy and marker sync held after the fix.

**Correction 2 (simultaneous-line writing)**: after correction 1, closer tight-frame inspection found a second, more serious physical-plausibility problem: within a single sentence that wrapped onto two visual rows, the model was filling both rows concurrently -- the second row's letters appeared while the first row still had missing words, something no person writing by hand can do. The original prompt only constrained ordering *between* the two full sentences, not between a sentence's own wrapped rows, and the model was choosing its own (bad) wrap point. Fixed by pre-splitting each sentence into explicit short rows (so the model never decides where to wrap) and chaining them with the same "next row doesn't start until this one is fully finished" language verified in round 21, generalized from 2 rows to 4. This made 3 of 4 row transitions fully clean. The remaining transition (row 2 to row 3) still shows a brief (~1s) overlap where the next row's first letter appears slightly before the previous row's last word is finished. An additional attempt to fix this with an explicit "lift the marker off the board and pause" instruction did not eliminate the overlap and introduced an unwanted side effect (stray bullet-point dashes/dots before each row). Given diminishing returns after several $1.50 test generations, this was accepted as the final version rather than pursued further -- see section 4.2.

## Watch the clip

<video src="clips/round22_final_captioned.mp4" controls width="260"></video>

## 1. Summary

- **Marker sync holds at wide framing.** Rounds 20-21 only verified genuine tip-leads-ink sync in extreme close-up with no presenter visible. This round re-tested the same prompt pattern (mechanically explicit tip/ink phrasing + explicit no-overlap sequencing) at a wide shot with the woman fully in frame, and sync held -- text appears progressively under the marker tip, not pre-written.
- **Text accuracy: 4/4 lines exactly correct** across both segments: "I vibe-coded my app in a weekend." / "Launched; 19 signed up." / "So this week I pay $99 on x.country" / "to grow my business on TikTok." -- including the dollar amount and the custom domain, which is new territory (no prior round tested numerals-plus-symbol accuracy like "$99" or a domain-style string).
- **9:16, 720p, 30s all hit.** Wan 3.0 accepted `aspect_ratio: "9:16"` and `resolution: "720p"` without error. 30s was achieved by generating two independent 15s segments (Wan 3.0's per-generation cap, confirmed since round 17/18) and concatenating.
- **Caption overlay works**, rendered as pre-timed PNG overlays composited with ffmpeg (not `drawtext` -- this machine's ffmpeg build lacks libfreetype, so captions are rasterized with PIL and alpha-composited instead).
- **Open issue: continuity break at the segment cut (0:15).** Segment A and Segment B were independent generations sharing only the seed and character-description text. The result: same face, but the outfit changes (button shirt + jeans to a beige dress), the whiteboard itself changes (wall-mounted panel to a free-standing board), the wall color/background shifts, and the hairstyle changes slightly. This was flagged as a known risk in the plan before generating, and it is now confirmed, not a surprise. It reads as a hard cut between two different takes/locations rather than one continuous shot.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (`alibaba/wan-3.0/text-to-video`), via fal.ai |
| Seed | 10001 (same for both segments, best-effort continuity only) |
| Aspect ratio | 9:16 (new -- all rounds 1-21 used 16:9) |
| Resolution | 720p (new -- rounds 18-21 used 1080p) |
| Duration | 2x 15s segments, concatenated to 30s |
| Generation time | Segment A: 353s (~5.9 min). Segment B: 364s (~6.1 min) |
| Cost | ~$1.50/segment at 720p -> ~$3 total for both generations |

Prompt pattern, corrected version (Segment A shown; Segment B identical structure with the second half of the script):

```
wide shot, a young white woman, attractive and fashionable, with styled hair and modern
stylish clothing, standing in a bright well-lit room in front of a whiteboard, fully
visible from the waist up. the whiteboard beside her is completely blank. at the very
start she looks at the camera for a moment, then turns her head to look at the whiteboard
and keeps her eyes on the board and on the marker tip the entire time she is writing --
she never looks at the camera while actively writing, since no person can write accurately
on a board without looking at it. she holds a black marker, its tip touching the
whiteboard surface. the marker tip moves slowly and steadily from left to right across
the board, and a single continuous line of black ink trail appears exactly where the tip
has physically touched, one letter forming at a time, following the tip precisely -- no
ink or text ever appears ahead of or away from the tip's current position.
First, the tip traces out the full first line, "I vibe-coded my app in a weekend." letter
by letter, left to right. Only after that entire first line is completely finished does
she move the marker down to start a new line below it -- no part of the second line
appears while the first line is still being written.
Then the tip traces out the second line, "Launched; 19 signed up." letter by letter, left
to right, the same way. the two lines never overlap in time -- the first is fully done
before the second begins. in cursive handwriting. her eyes stay on the whiteboard and the
marker tip throughout the writing, not on the camera. only after both lines are completely
finished does she turn her head back to look at the camera. the camera holds steady the
entire time.
```

## 3. Results

Frame inspection at 1-second spacing across both 15s segments, plus final-frame checks:

- Segment A, frame 0: blank board, woman visible waist-up, correct wardrobe/framing.
- Segment A, frame 5 (~t=5s): line 1 partially written ("I vibe-code / in a weeke..."), tip at the leading edge of the ink.
- Segment A, frame 10 (~t=10s): line 1 complete and correct, line 2 just starting.
- Segment A, final frame (~t=15s): both lines complete and exactly correct.
- Segment B, frame 0: same face/seed, different outfit and board setup (see continuity issue above).
- Segment B, final frame (~t=15s, clip-relative): both lines complete and exactly correct, including "$99" and "x.country".

## 4. Post-processing pipeline

1. Concatenate Segment A + Segment B with `ffmpeg -f concat` (same codec/resolution/fps, lossless copy).
2. Render 4 caption cards (one per script line) as transparent PNGs with PIL (`raw/captions/cap{0-3}.png`), centered horizontally, vertically mid-screen, semi-transparent rounded background box, white bold text, auto word-wrapped.
3. Composite the 4 PNGs onto the stitched video with timed `overlay=...:enable='between(t,start,end)'` filters (~7-8s per line), re-encoded with libx264.
4. Output: `clips/round22_final_captioned.mp4` -- 720x1280, 30.0s, 30fps.

## 4.1 Eye-gaze correction

Frame inspection confirms the fix held across both segments:

- Frame 0: she looks directly at the camera (the intended opening beat).
- Mid-writing frames (both segments): she is consistently shown in profile, eyes on the board and the marker tip, never toward the camera while text is forming.
- Final frame (both segments): she turns back to face the camera only once both lines are fully written.

Text accuracy and marker sync were unaffected by the fix -- all 4 lines still render exactly correct.

## 4.2 Sequential-row-writing correction

The script was pre-split into 4 short rows per segment instead of 2 sentences left for the model to wrap on its own:

- Segment A: "I vibe-coded my app" / "in a weekend." / "Launched; 19" / "signed up."
- Segment B: "So this week I pay" / "$99 on x.country" / "to grow my business" / "on TikTok."

Frame inspection of the final version (every 1s, plus tight spacing around each row transition):

- Row 1 to row 2: clean -- row 2 has no content until row 1's last word is on the board.
- Row 2 to row 3: a brief overlap remains -- row 3's first 1-2 letters appear roughly 1 second before row 2's final word is finished, visible across frames ~250-270.
- Row 3 to row 4: clean.
- All 4 rows render exactly correct in both segments, including "$99" and "x.country".

This is a large improvement over the original defect (two entire sentences appearing to grow at once, for the whole second half of the clip), narrowed down to one brief, partial overlap at a single transition. Not fully eliminated after three different prompt strategies (implicit sentence-level-only rule, explicit pre-split rows, and an explicit marker-lift pause) -- accepted as the final result per direction to stop iterating given cost (~$10-11 spent on 7 test generations investigating this single issue).

## 5. What this means

| Question | Answer |
|---|---|
| Does the round 20/21 sync-fix prompt pattern work at wide framing with a visible presenter? | Yes -- verified at 1s frame spacing across both segments, text builds progressively under the tip, matching the close-up result's quality. |
| Does Wan 3.0 support portrait 9:16 and 720p? | Yes -- both accepted without error. |
| Can 30s be reached? | Yes, by stitching two 15s generations -- Wan 3.0's hard per-call cap is 15s. |
| Does stitching preserve visual continuity? | No -- confirmed outfit/board/background/hairstyle all shift at the cut, despite using the same seed. This is a real limitation of independent generations, not something the seed alone fixes. |
| Does the caption overlay work? | Yes, via a PNG-overlay pipeline since this ffmpeg build lacks drawtext/libfreetype. |

## 6. Still to do / open for direction

1. **Continuity at the cut**: decide whether the current hard cut (new outfit/location) is acceptable as a stylistic "two takes" edit, or whether it needs fixing. A true fix would need an image-to-video continuation approach (feed Segment A's last frame into Segment B's generation as a starting image) rather than independent text-to-video calls with a shared seed -- this hasn't been tested and would need its own round.
2. **Residual row-transition overlap**: one of the three row boundaries per segment still shows a brief (~1s) overlap where the next row starts just before the previous one finishes. Accepted as the final version for this round (see section 4.2) rather than pursued further, given cost. Worth retrying with fresh ideas in a future round if this remains unacceptable -- e.g. even shorter per-row text, or splitting each row into its own separate generation (proven clean in round 20/21, at the cost of more cuts and more spend).
3. Extend to more than 2 segments if the boss wants finer caption timing granularity or more script content.
4. If both the cut and the residual overlap are acceptable as-is, this prompt pattern (wide shot + mechanically explicit sync phrasing + pre-split rows + eyes-on-board + 9:16/720p) becomes the new standard template for future rounds.

## 7. Files

- `clips/round22_final_captioned.mp4`: final deliverable -- 9:16, 720p, 30s, captioned.
- `clips/round22_stitched_30s.mp4`: pre-caption stitched clip (for reference/debugging).
- `clips/wan30_round22_segA.mp4`, `clips/wan30_round22_segB.mp4`: the two raw 15s generations.
- `raw/captions/cap{0-3}.png`: rendered caption overlay images.
- `raw/raw_record_wan30_round22_seg{A,B}.json`: generation records (request id, endpoint, payload including seed, timing).
- `run_fal_test.py`: submits/polls/downloads a segment via fal.ai's queue API. Usage: `python3 run_fal_test.py A` or `B`. Reads the API key from `server/falAPI.txt` (git-ignored, never printed).
- `postprocess.sh`: stitches the two segments and applies the caption overlay.
- `PLAN.md`: this round's plan, frozen before running.

## 8. Cost

~$3 for the final pair of Wan 3.0 generations (720p, 15s each). Post-processing (ffmpeg/PIL) is free/local. The round as a whole, including iterating on the eye-gaze and row-sequencing fixes (7 test generations total), cost roughly $10-11.
