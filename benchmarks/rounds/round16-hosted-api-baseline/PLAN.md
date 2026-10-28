[← All rounds](../../../README.md)

# Round 16 plan: hosted API baseline (Kling, Seedance)

## Why

Rounds 12-15 tested only open-weight, self-hosted models (Wan 2.2, HunyuanVideo 1.5). All of them render on-screen text with partial accuracy at best — scrambled word order, duplicated content, or garbled characters, even in the best case found so far (round 13 v3 / round 14 A1-A2). This round checks whether hosted commercial APIs, which may use a different text-rendering pipeline internally, do meaningfully better on the same script.

## Models

- **Kling 2.5 Turbo Pro** (text-to-video), via fal.ai. $0.35 for a 5s clip, +$0.07/s after.
- **Seedance 1.0 Pro** (text-to-video), via fal.ai. ~$0.62 for a 5s 1080p clip.

## Script and prompt format

Reusing the same five sentences used in rounds 13-15 (the real customer whiteboard script), and the prompt format round 13 v3 found necessary for Hunyuan (quoted lines, explicitly introduced one at a time) as the starting point — adapted to whatever prompt convention each hosted model's docs recommend for on-screen text, if different.

```
L1 = "Thousands of U.S. advertisers are pursuing claims against Google."
L2 = "Advertisers are filing refunds for 20-30% of Ad Spend since 2016."
L3 = "Federal courts have ruled Google illegally monopolized search advertising."
L4 = "Get the facts, fit criteria and risks."
L5 = "DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"
```

## Tests

1. Kling 2.5 Turbo Pro, 5s clip, all 5 lines in one prompt (same whiteboard/lawyer framing as prior rounds).
2. Seedance 1.0 Pro, 5s clip, same prompt as test 1.
3. If either model's test 1 result is clearly wrong/scrambled, retry with the split-line approach (lines broken into 2 shorter calls, like round 14's A1/A2) before concluding the model fails outright — same methodology discipline as round 13's Hunyuan work.

## Budget

$25 credited to fal.ai. Estimated cost for tests 1-3: $2-5. Leaves headroom for reruns.

## Verification

Same as every other round: direct frame-by-frame inspection of the actual returned video against the real script text, no OCR/automated claim trusted without it.
