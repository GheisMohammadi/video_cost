[← All rounds](../../../README.md)

# Round 21 plan: fix the second-line-starts-early overlap

## Why

Round 20 got genuine marker-to-letter sync for a single line (verified at tight frame spacing: the tip consistently led the ink, not the reverse), but noted one defect: a second visual row began appearing before the first row had finished being written. This round tests whether an explicit sequencing instruction -- do not start the next line until the current line is completely finished -- removes that overlap.

## Test

Same model (`alibaba/wan-3.0/text-to-video`, fal.ai), same seed (10001), same close-up framing and mechanically explicit tip/ink-trail phrasing that worked in round 20. Script extended to the first two lines (not all five, to keep the test focused on the overlap question specifically). Prompt adds an explicit constraint: the second line must not begin until the first line is completely written and the tip has moved down to start the second line.

## Question this answers

Does explicit sequencing language stop the model from writing two lines in parallel, while preserving round 20's tip-to-letter sync and text accuracy?

## Budget

Remaining fal.ai balance (~$20 left after rounds 16-20). Estimated cost for 1-2 test clips at 5s, 1080p: $1-2.

## Verification

Same tight-frame-spacing method as round 20 (every 5-10 frames), checking specifically whether any text from line 2 appears before line 1 is fully formed.
