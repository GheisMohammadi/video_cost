[← All rounds](../../../README.md)

# Round 17 plan: Wan 2.7 text-rendering check (fal.ai)

## Why

Round 16 found both hosted APIs tested so far (Kling 2.5 Turbo Pro, Seedance 1.0 Pro) render on-screen text worse than self-hosted HunyuanVideo 1.5. A follow-up search for which model is actually strong at text turned up one anecdotal but specific lead: Wan 2.7 (Alibaba's newest Wan generation, successor to the Wan 2.2 used as this project's baseline in rounds 1-9) was singled out by one hands-on tester as having a known strength in text rendering. Thin evidence (one anecdote), but cheap to check directly against our own frozen script, and directly relevant since this project's whole self-hosted pipeline is already built on the Wan family.

## Model

**Wan 2.7 text-to-video**, via fal.ai (`fal-ai/wan/v2.7/text-to-video`). $0.10/s at 720p, $0.15/s at 1080p.

## Test

Same five-line whiteboard script and same prompt format used in round 16 (all five quoted lines in one generation, lawyer-at-whiteboard framing), for direct comparability against Kling and Seedance's round 16 results, and against Hunyuan's round 13-14 results.

If the single-prompt attempt is clearly wrong, retry with the split-line approach (the fix that worked for Hunyuan in round 13 v3) before concluding Wan 2.7 also fails.

## Budget

Remaining fal.ai balance from round 16's $25 top-up (~$24 left). Estimated cost for 1-2 test clips at 5s, 1080p: $0.75-1.50.

## Verification

Direct frame-by-frame inspection of the actual returned video against the real script text, same as every other round.
