[← All rounds](../../../README.md)

# Round 18 plan: Wan 3.0 text-rendering check (fal.ai)

## Why

Round 17 found Wan 2.7 renders 4 of 5 whiteboard lines exactly correct from a single prompt -- the best result in this project's history, but with two open questions: is it reproducible (Wan 2.7's fal endpoint doesn't expose a seed parameter, so it couldn't be checked), and does the newer Wan 3.0 (released after 2.7, also on fal.ai) do even better, given Alibaba's pattern of incremental text-fidelity improvements across Wan releases.

## Model

**Wan 3.0 text-to-video**, via fal.ai (`alibaba/wan-3.0/text-to-video`). ~$0.10/s at 720p, ~$0.20/s at 1080p. Unlike the 2.7 endpoint, this one exposes a `seed` parameter, which lets this round also serve as round 17's reproducibility check once a result is pinned and resubmitted.

## Test

Same five-line whiteboard script and same prompt format used in rounds 16-17 (all five quoted lines in one generation, lawyer-at-whiteboard framing), for direct comparability.

## Budget

Remaining fal.ai balance (~$23 left after rounds 16-17). Estimated cost for 1-2 test clips at 5s, 1080p: $1-2.

## Verification

Direct frame-by-frame inspection of the actual returned video against the real script text, same as every other round.
