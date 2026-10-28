[← All rounds](../../../README.md)

# Round 21: explicit sequencing instruction fixes the line overlap (Oct 29, 2026)

Status: complete. Round 20 got genuine marker-to-letter sync for a single line but noted a second line began forming before the first was finished. This round tests whether an explicit "do not start line 2 until line 1 is completely finished" instruction fixes that overlap, using the same close-up framing and mechanically explicit prompt style that worked in round 20.

## Watch the clip

<video src="clips/wan30_sequential_round21.mp4" controls width="420"></video>

## 1. Summary

**Fixed.** Checked at tight (4-frame) spacing around the transition point specifically: line 1 is fully complete and the hand is already repositioning below it with no line 2 text present (frame 80), and line 2 only begins appearing after that (frame 88). No overlap between the two lines this time, unlike round 20.

- Both lines render **exactly correct**: "Thousands of U.S. advertisers are pursuing claims against Google." and "Advertisers are filing refunds for 20-30% of Ad Spend since 2016."
- The marker-to-letter sync from round 20 is preserved -- the tip continues to lead the ink rather than text appearing ahead of it.
- "20-30%" renders correctly (no digit error, consistent with every Wan 3.0 round so far).

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (`alibaba/wan-3.0/text-to-video`), via fal.ai -- same model/endpoint/seed as rounds 18-20 |
| Seed | 10001 |
| Script | Lines 1-2 (extended from round 20's single line, to directly test the overlap question) |
| Duration / resolution | 5s, 1080p, 16:9 |
| Generation time | 141.9s (~2.4 min) |
| Cost | ~$1.00 |

Prompt, building on round 20's mechanically explicit style with an added sequencing constraint:

```
extreme close-up on a whiteboard, completely blank. a hand holds a black marker, its tip
touching the whiteboard surface. the marker tip moves slowly and steadily from left to right
across the board, and a single continuous line of black ink trail appears exactly where the
tip has physically touched, one letter forming at a time, following the tip precisely -- no
ink or text ever appears ahead of or away from the tip's current position.
First, the tip traces out the full first line, "Thousands of U.S. advertisers are pursuing
claims against Google." letter by letter, left to right. Only after that entire first line is
completely finished does the hand move the marker down to start a new line below it -- no part
of the second line appears while the first line is still being written.
Then the tip traces out the second line, "Advertisers are filing refunds for 20-30% of Ad
Spend since 2016." letter by letter, left to right, the same way. the two lines never overlap
in time -- the first is fully done before the second begins. in cursive handwriting. the
camera holds steady on the whiteboard the entire time.
```

## 3. Results

Frame inspection, both broad (every 10 frames) and tight (every 4 frames around the transition point, `raw/tight_{72,76,80,84,88,92,96}.png`):

- **Frame 60**: line 1 near-complete ("...pursuing claims against Googl[e]"), no line 2 present.
- **Frame 72-80**: line 1 fully complete, hand already moved down to position below it -- still no line 2 text at frame 80.
- **Frame 88**: line 2 begins -- a single letter "A" visible, tip positioned right there.
- **Frame 90-96**: line 2 builds normally ("Adv", then "Advertis" / "20-2..."), tip leading the ink, line 1 untouched above.
- **Frame 149** (final): both lines complete and exact.

## 4. What this means

| Question | Answer |
|---|---|
| Does an explicit sequencing instruction stop the two-line overlap seen in round 20? | Yes -- verified at tight frame spacing specifically around the transition point, the same rigor that caught round 19's and round 20's issues. |
| Does the fix cost any accuracy or sync quality? | No -- both lines render exactly correct, and the tip-to-ink sync from round 20 holds up across the line break. |
| Does this generalize to more than two lines? | Not yet tested -- this round used two lines specifically to isolate the overlap question. The next test should extend to the full five-line script to confirm the sequencing instruction holds for a longer board. |
| What's the practical implication? | The combination of close-up framing, mechanically explicit tip/ink-trail phrasing (round 20), and an explicit no-overlap sequencing instruction (this round) now produces a genuinely convincing two-line handwriting animation with correct text -- the strongest and most honest "lawyer actually writing" result in this project's 21-round history. |

## 5. Still to do

1. Extend to the full five-line script with this same prompt pattern (close-up, mechanical phrasing, explicit sequencing) to see whether it holds for the complete board, not just two lines.
2. Retest at the original wide framing (lawyer visible in shot, not just the hand close-up) with the same prompt style, since a full deliverable likely needs the presenter visible, not just a hand-and-board close-up.
3. If both hold up, adopt this round's prompt pattern as the standard template going forward, replacing rounds 18-19's phrasing.

## 6. Files

- `clips/wan30_sequential_round21.mp4`: the generated clip.
- `raw/frame_{0,10,...,149}.png`: frames across the full clip (every 10 frames).
- `raw/tight_{72,76,80,84,88,92,96}.png`: tight-spaced frames around the line 1 to line 2 transition, used to verify no overlap.
- `raw/raw_record_wan30_sequential.json`: generation record (request id, endpoint, payload including seed, timing).
- `run_fal_test.py`: the script used to submit, poll, and download the job via fal.ai's queue API. Reads the API key from `server/falAPI.txt` (git-ignored, never printed).
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$1.00, well within the remaining fal.ai balance from round 16's $25 top-up.
