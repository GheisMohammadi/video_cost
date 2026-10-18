[← All rounds](../../../README.md)

# Round 10 test design: on-screen text accuracy

Status: run complete. Results, both clips, and limitations are in `README.md`. Headline: both the highest-quality and the fastest/cheapest config fail completely at reproducing the script's exact text; the fast config additionally shows a visual breakdown (a semi-transparent, reflective whiteboard) the slow config does not.

## 1. Question

Given the exact customer prompt that already failed once (a lawyer explaining a multi-line script on a whiteboard, word-for-word), does this project's pipeline reproduce that failure, and does a different generation config (plain 27-step model vs the 4-step distillation LoRA from rounds 8-9) change the outcome. Secondary: is this a problem a different generation setting can fix, or -- as research into the field suggests (see the project's own notes from this round's planning conversation) -- is on-screen text accuracy an unsolved limitation industry-wide, meaning the real fix is a post-production overlay step rather than a generation-time one.

## 2. What was run

| Item | Value |
|---|---|
| Prompt | The customer's exact text, unedited: a white male lawyer explaining a multi-paragraph script (Google advertiser claims) on a whiteboard with a marker |
| Configs tested | (A) plain Wan 2.2 T2V-A14B, 27 steps, standard guidance (round 1's settings) -- the highest-quality config this project has measured. (B) the 4-step distillation LoRA, guidance 1.0 (round 8-9's settings) -- the fastest/cheapest config this project has measured |
| Resolution | 832x480, 81 frames at 16 fps (5.0625 s) -- same as every prior round; resolution is not the variable under test here |
| Seed | 10001, fixed, same for both configs so any difference is attributable to the config, not the random draw |
| Hardware | One RunPod A100-SXM4-80GB pod, both configs run sequentially in the same session to avoid a second pod |

## 3. What this round does not attempt

1. A fix. This round reproduces and documents the failure with evidence; section 1's secondary question (generation-time fix vs post-production overlay) gets answered by what the clips actually show, not assumed in advance.
2. A blind review. One prompt, two configs, direct inspection of the output against the exact script -- this is a reproduction test, not a statistically supported quality claim.
3. 720p, quantization, or any other variable rounds 1-9 covered. Those are orthogonal to the text-accuracy question this round asks.

## 4. Budget

Under $10, team-confirmed, no further budget approval needed for this round. In practice: one short pod session, two 81-frame clips (one per config) plus a warm-up, well under an hour of GPU time.
