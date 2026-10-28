[← All rounds](../../../README.md)

# Round 17: Wan 2.7 -- best text-rendering result in this project's history (Oct 29, 2026)

Status: complete. One anecdotal lead (a hands-on tester calling out Wan 2.7's text rendering) checked directly against this project's frozen five-line whiteboard script, after round 16 found both tested hosted APIs (Kling 2.5 Turbo Pro, Seedance 1.0 Pro) worse than self-hosted HunyuanVideo 1.5.

## Watch the clip

<video src="clips/wan27_round17.mp4" controls width="420"></video>

## 1. Summary

**Wan 2.7 renders 4 of the 5 script lines exactly correct, word-for-word, in a single generation with no prompt-splitting workaround.** This is the strongest text-accuracy result in 17 rounds of this project -- better than round 13-14's HunyuanVideo 1.5 best case (2 lines exact, needed a multi-generation split-line approach) and far better than round 16's hosted APIs (0 lines legible).

- Lines 1-4 (the main whiteboard script): pixel-perfect match to the source text, including "20-30%" rendered exactly right -- HunyuanVideo 1.5 consistently rendered this as the wrong "20-3%" across rounds 14 and 15; Wan 2.7 does not make that error.
- Line 5 (small print): "DOWNLOAD EXPLAINER" and "ADREFUNDS.COM" both render correctly; the middle words "File Ad Refunds" are dropped from the line, so it's not a perfect 5-for-5, but is still clearly legible and mostly correct.
- Text is **stable across the whole clip** -- no scrambling, no duplication, no drift between frames, unlike every self-hosted model tested so far (Wan 2.2, HunyuanVideo 1.5).
- One unrelated framing issue: by the last frame the lawyer's body has moved to crop part of lines 1-3 off-camera. The text itself is unaffected; this is a composition/camera problem, not a text-rendering problem.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 2.7 text-to-video (`fal-ai/wan/v2.7/text-to-video`), via fal.ai |
| Prompt | All five quoted lines in one generation, same lawyer-at-whiteboard framing as round 16 |
| Duration / resolution | 5s, 1080p, 16:9 |
| Generation time | 577.8s (~9.6 min) |
| Cost | ~$0.75 |

Same prompt as round 16 (for direct comparison):

```
a whiteboard with four lines of handwritten text and a smaller line below them.
The first line reads "Thousands of U.S. advertisers are pursuing claims against Google."
The second line reads "Advertisers are filing refunds for 20-30% of Ad Spend since 2016."
The third line reads "Federal courts have ruled Google illegally monopolized search advertising."
The fourth line reads "Get the facts, fit criteria and risks."
Below in smaller text it reads "DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"
a white, male lawyer stands beside the whiteboard holding a marker, pointing at the board and explaining it to the camera
```

One API quirk hit and fixed: fal's Wan 2.7 endpoint requires `duration` as an integer (`5`), not a string (`"5"`) -- the string form fails with HTTP 422. Round 16's Kling/Seedance endpoints accepted the string form without complaint, so this wasn't caught until Wan 2.7's first submission failed.

## 3. Results

Direct frame inspection at frames 1, 60, 120 (`raw/wan27_frame_{001,060,120}.png`):

- **Frame 1**: all five lines visible and legible. Lines 1-4 exact. Line 5 reads "DOWNLOAD EXPLAINER" / "ADREFUNDS.COM" -- correct words, middle phrase dropped.
- **Frame 60**: identical text, still exact on lines 1-4, same line 5 as frame 1. No drift.
- **Frame 120**: same text content, still correct, but the lawyer has moved and his body now crops off the right portion of lines 1-3 (the words are still there, just partially behind him in the frame).

## 4. What this means

| Question | Answer |
|---|---|
| Is Wan 2.7 better at text than Hunyuan or the hosted APIs tested so far? | Yes, clearly -- 4/5 lines exact vs. Hunyuan's 2/5 best case (round 13 v3) and the hosted APIs' 0/5 (round 16). |
| Does it need the split-line workaround Hunyuan required? | No -- this result came from a single prompt with all five lines together, which is what caused Hunyuan to degrade in round 13 v3 and round 14 A3. |
| Does the `20-3%` digit error (seen consistently in Hunyuan, rounds 14-15) appear here? | No -- `20-30%` renders exactly correct. |
| Is this a complete fix? | Not quite -- line 5's middle words are dropped, and the framing lets the subject crop into the text by the end of the clip. But this is the first result in the project where the large majority of a real script renders correctly from one simple prompt. |
| Does this change the project's standing recommendation? | Yes, worth re-opening the generation-time question. Previously the only 100%-reliable path was compositing (rounds 10-11). Wan 2.7 doesn't reach 100%, but at 80%+ word-for-word accuracy from one prompt, it's now the strongest generation-time candidate this project has tested -- worth a second run (different seed/prompt) to see if this result is repeatable, and worth testing whether a tighter framing instruction fixes the late-clip crop. |

## 5. Still to do

1. Repeat the test with a different seed to check whether this result is repeatable or a lucky draw -- Wan 2.7 doesn't expose a documented seed parameter on this fal endpoint, so repeatability can currently only be checked by resubmitting the same prompt.
2. Retry with an explicit framing instruction (e.g. "keep the full whiteboard in frame at all times") to fix the late-clip crop.
3. Try to recover line 5's dropped middle words -- test whether shortening line 5 or giving it its own sentence (the split-line approach that helped Hunyuan) fixes it, or whether it's a length-based drop specific to the smallest-text line.
4. If this holds up under a repeat, consider Wan 2.7 the new baseline candidate for any future round testing on-screen text, ahead of HunyuanVideo 1.5.

## 6. Files

- `clips/wan27_round17.mp4`: the generated clip.
- `raw/wan27_frame_{001,060,120}.png`: inspection frames.
- `raw/raw_record_wan27.json`: generation record (request id, endpoint, payload, timing).
- `run_fal_test.py`: the script used to submit, poll, and download the job via fal.ai's queue API. Reads the API key from `server/falAPI.txt` (git-ignored, never printed).
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$0.75, well within the remaining fal.ai balance from round 16's $25 top-up.
