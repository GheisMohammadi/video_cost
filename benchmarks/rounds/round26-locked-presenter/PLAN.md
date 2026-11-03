[← All rounds](../../../README.md)

# Round 26 plan: pin down presenter/scene details to fix cross-row consistency

## Why

Round 25's compositing pipeline (deterministic text render over "blank board" presenter footage) was rejected outright as unacceptable quality. Round 24's image-to-video chaining fixed cross-row clothing/background continuity but broke text fidelity (wrong words appeared). Round 23 remains the best-looking result so far but left one open question (its own section 6, item 1): independent per-row generations don't preserve outfit/background across cuts.

Round 23's `PRESENTER` string is vague: "a young white woman, attractive and fashionable, with styled hair and modern stylish clothing." Every row is an independent generation, so Wan 3.0 re-interprets "stylish clothing" and "styled hair" freshly each time -- the fixed seed (10001) pins the noise, not the model's reading of a vague adjective. That is the most likely cause of the clothing/hair drift the user flagged, separate from (and simpler to fix than) the marker-sync issue.

## Approach

Keep round 23's generation mechanism unchanged (per-row text-to-video, tip-touches-board prompt, same sync wording -- it is this project's best-verified sync result, rounds 20-23). Only change: replace the vague `PRESENTER` string with one fully concrete description, repeated verbatim across all 8 row prompts:

- Exact hair: color, length, style (e.g. "shoulder-length straight dark brown hair")
- Exact top: garment type, color, fit (e.g. "a fitted white long-sleeve ribbed top")
- Exact room/board/wall details held constant (e.g. "a white whiteboard mounted on a light gray wall, in a bright room with a window to her right")

No new technique, no new risk beyond round 23's -- this is a prompt-wording change only, cheap to test.

## Test order

1. Generate rows 1 and 2 only with the locked description, same seed (10001).
2. Compare outfit/hair/background across those two independently-generated clips side by side (the actual failure mode -- not sync, which round 23 already verified).
3. If consistency visibly improves, generate the remaining 6 rows and rebuild the stitched/captioned final video, reusing round 23's `postprocess.py` trim/pause logic.
4. If it does not improve, report back before spending further -- vague wording may not be the dominant cause, and the next step would need to be a different continuity mechanism (e.g. img2img style-reference conditioning if available on this endpoint) rather than more prompt tuning.

## Budget

~$0.50-0.75/clip x 2 test clips = ~$1-1.50 for the consistency test. Full 8-row run if the test passes: ~$6, matching round 23's actual cost.
