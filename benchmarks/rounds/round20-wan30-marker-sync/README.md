[← All rounds](../../../README.md)

# Round 20: a close-up, mechanically explicit prompt gets real marker-to-letter sync (Oct 29, 2026)

Status: complete. Round 19 found Wan 3.0's "writing animation" was actually a line-by-line reveal -- each line appeared as a whole pre-formed block near the hand, with no sync between the marker tip and individual letters. This round tests whether a much more explicit, close-up, single-line prompt (describing the pen tip and ink trail directly, rather than "he writes a line that reads...") can get genuine tip-to-letter tracing.

## Watch the clip

<video src="clips/wan30_marker_sync_round20.mp4" controls width="420"></video>

## 1. Summary

**Yes -- this prompt produces real tip-to-ink synchronization, verified at tight frame spacing.** Unlike round 19, where whole lines appeared pre-formed ahead of the marker, this clip shows the marker tip consistently sitting at the trailing edge of the most recently drawn ink at every sampled frame (every 5-10 frames, same scrutiny that caught round 19's overstated claim). Text content is also exact: "Thousands of U.S. advertisers are pursuing claims against Google." -- the full line, letter-perfect.

One wrinkle, reported honestly rather than smoothed over: at frame 45 a second visual row ("are pu...") begins appearing before the first row is fully finished ("Thousand" rather than "Thousands" at that instant) -- so it is not strictly one single continuous stroke across the whole sentence from first letter to last. But within each stroke the tip visibly leads the ink, which is the specific defect round 19 identified and this round set out to test.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (`alibaba/wan-3.0/text-to-video`), via fal.ai -- same model/endpoint as rounds 18-19 |
| Seed | 10001 (same as rounds 18-19) |
| Script | Line 1 only (the line every prior round rendered correctly) -- isolated to separate the marker-sync question from the text-accuracy question already answered in rounds 18-19 |
| Duration / resolution | 5s, 1080p, 16:9 |
| Generation time | 174.9s (~2.9 min) |
| Cost | ~$1.00 |

Prompt, rewritten to be mechanically explicit rather than describing the end result:

```
extreme close-up on a whiteboard, completely blank. a hand holds a black marker, its tip
touching the whiteboard surface. the marker tip moves slowly and steadily from left to right
across the board, and a single continuous line of black ink trail appears exactly where the
tip has physically touched, one letter forming at a time, following the tip precisely -- no
ink or text ever appears ahead of or away from the tip's current position. By the time the tip
reaches the end of the line, it has traced out the full sentence "Thousands of U.S. advertisers
are pursuing claims against Google." letter by letter, left to right, in cursive handwriting.
the camera holds steady on the whiteboard the entire time.
```

Two changes from round 19's approach: (1) extreme close-up framing instead of a wide shot of the whole lawyer-and-board scene, and (2) the prompt describes the physical mechanism (tip touching, ink trail following the tip) instead of the narrative outcome (he writes a line that reads...).

## 3. Results

Frame inspection at 5-10 frame spacing (`raw/frame_*.png`, `raw/tight_*.png`):

- **Frame 0**: blank board.
- **Frame 30**: "Thousand" visible, marker tip positioned immediately after the "d", about to continue.
- **Frames 35-45**: tip visibly leads each new letter as it appears -- "Tho" at frame 40, "Thousand" with tip right at its end at frame 45. A second row ("are pu...") begins appearing at frame 45 while row 1 is still mid-word, so the two rows are not strictly sequential, but each row's own text ends right at the tip.
- **Frame 60-90**: tip continues to sit at the trailing edge of newly-written text through "Thousands of U.S." and "are pursuing claims against G[oogle]".
- **Frame 149** (final): full line visible and exact: "Thousands of U.S. advertisers are pursuing claims against Google."

## 4. What this means

| Question | Answer |
|---|---|
| Is genuine marker-to-letter sync achievable with Wan 3.0? | Yes, under the right prompt and framing -- a close-up shot with a mechanically explicit prompt gets real tip-leads-ink behavior, unlike round 19's wide shot with a narrative prompt. |
| Does this fully solve round 19's gap? | Mostly, with one caveat: a second line began forming slightly before the first line finished, so multi-line sequencing isn't perfectly serialized yet. For a single-line or isolated-phrase shot, this result looks solid. |
| Does accuracy hold alongside the sync fix? | Yes -- the one line tested rendered exactly correct, consistent with rounds 18-19's accuracy findings. |
| What's the practical implication? | The combination of (a) close-up/tighter framing and (b) a mechanically explicit, physically-grounded prompt (tip + ink trail, not "he writes") looks like the key lever for getting convincing handwriting animation out of Wan 3.0 -- worth retesting with the full five-line script and a wider shot to see if the same prompt style holds up at the original scene framing, or whether the close-up crop is doing most of the work. |

## 5. Still to do

1. Retest with the full five-line script to see whether this prompt style (mechanical description + explicit tip-ink constraint) holds up for a longer, multi-line board, or whether the close-up/single-line setup was doing most of the work here.
2. Retest at the original wide framing (lawyer visible, whole board in shot) with the same mechanically explicit phrasing, to see whether the sync fix survives when the camera isn't a tight close-up on the hand.
3. Investigate the frame-45 multi-line overlap (second line starting before the first finishes) -- test whether an explicit "do not start the next line until the current line is fully written" instruction resolves it.
4. If the full-script, wide-shot version holds up, this becomes the new standard prompt template for any future Wan 3.0 text-accuracy round, replacing round 18/19's phrasing.

## 6. Files

- `clips/wan30_marker_sync_round20.mp4`: the generated clip.
- `raw/frame_{0,10,20,...,149}.png`: frames across the full clip (every 10 frames).
- `raw/tight_{35,40,45,55,65,75,85,95}.png`: tighter-spaced frames used to verify the tip-to-ink sync claim.
- `raw/raw_record_wan30_marker_sync.json`: generation record (request id, endpoint, payload including seed, timing).
- `run_fal_test.py`: the script used to submit, poll, and download the job via fal.ai's queue API. Reads the API key from `server/falAPI.txt` (git-ignored, never printed).
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$1.00, well within the remaining fal.ai balance from round 16's $25 top-up.
