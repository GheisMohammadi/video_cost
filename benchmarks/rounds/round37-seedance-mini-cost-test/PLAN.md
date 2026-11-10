# Round 37: cost test -- Seedance 2.0 Mini vs. Seedance 2.0 Fast

User directive: generation with Seedance (and other models) is expensive;
test a cheaper tier to see if quality holds up well enough to use it going
forward.

## What was tested

Found `bytedance/seedance-2.0/mini/text-to-video` on fal.ai -- about 36%
cheaper per second than the "fast" tier used in every round so far
(mini: $0.1547/s at 720p vs. fast: $0.2419/s at 720p -- source: fal.ai's
pricing page and the mini model's page). No other cheaper tier
("lite"/"standard") exists for Seedance 2.0 besides fast and mini.

Ran the exact same prompt and payload that produced round 36's accepted
deliverable (4 lines of text, rectangle around "vibe-coded", circle around
"$99", underline under "x.country", 15s, 720p, 16:9) through the mini
endpoint instead of fast, for a direct apples-to-apples comparison.

## What to check

- Does mini hold up on the same text-accuracy and annotation-precision
  checks that fast passed in round 36 (all 4 lines correct, rectangle/circle
  tightly scoped, no reflection, no stray marks)?
- Is the cost savings worth any quality tradeoff found?

## Budget

~$2.32 for one mini attempt at 15s/720p (vs. ~$3.63 for the same at fast
tier). One attempt only -- this is a feasibility check, not a full
production run.
