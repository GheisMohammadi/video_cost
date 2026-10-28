[← All rounds](../../../README.md)

# Round 16: hosted API baseline -- Kling and Seedance, both worse than self-hosted (Oct 29, 2026)

Status: complete. Tested whether hosted commercial APIs do better than the self-hosted models (Wan 2.2, HunyuanVideo 1.5) used in rounds 1-15, on the identical five-line whiteboard script and prompt format that got round 13 v3 / round 14 its first verbatim-correct sentences.

## Watch both clips

Kling 2.5 Turbo Pro:

<video src="clips/kling_round16.mp4" controls width="420"></video>

Seedance 1.0 Pro:

<video src="clips/seedance_round16.mp4" controls width="420"></video>

## 1. Summary

**Both hosted models performed worse than HunyuanVideo 1.5 (round 13-14), and worse than Wan 2.2's best self-hosted results.** Neither rendered any recognizable fragment of the actual script text.

- **Kling 2.5 Turbo Pro**: the whiteboard shows dense, static cursive-style scrawl that is not real English at any point in the clip -- scrambled letter clusters, no match to any of the five script lines.
- **Seedance 1.0 Pro**: the whiteboard shows four short bulleted pseudo-words ("A unitres", "Swent icmo.n", "Twetanet.", "Taumlanss") -- shorter and more legible as individual letters than Kling's output, but still not real words and not a match to any part of the actual script.

## 2. What was run

| Item | Kling 2.5 Turbo Pro | Seedance 1.0 Pro |
|---|---|---|
| Provider | fal.ai | fal.ai |
| Endpoint | `fal-ai/kling-video/v2.5-turbo/pro/text-to-video` | `fal-ai/bytedance/seedance/v1/pro/text-to-video` |
| Duration | 5s | 5s |
| Resolution | default | 1080p |
| Generation time | ~204s | ~71s |
| Cost | ~$0.35 | ~$0.62 |

Prompt (identical for both, same format as round 14's A3 -- all five quoted lines in one generation, lawyer-at-whiteboard framing):

```
a whiteboard with four lines of handwritten text and a smaller line below them.
The first line reads "Thousands of U.S. advertisers are pursuing claims against Google."
The second line reads "Advertisers are filing refunds for 20-30% of Ad Spend since 2016."
The third line reads "Federal courts have ruled Google illegally monopolized search advertising."
The fourth line reads "Get the facts, fit criteria and risks."
Below in smaller text it reads "DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"
a white, male lawyer stands beside the whiteboard holding a marker, pointing at the board and explaining it to the camera
```

Neither model's documentation was found to specify a different recommended format for on-screen text, so the Hunyuan-proven quoted-line format was used as-is for a first pass (see section 5 for the planned split-line retry, not yet run).

## 3. Results

Direct frame inspection at frames 1, 60, 120 (`raw/kling_frame_*.png`, `raw/seedance_frame_*.png`):

- **Kling**: identical static text across all three frames (the model appears to render the board once and hold it, unlike Hunyuan/Wan's progressive-writing animation). Every line is unreadable scrawl -- no English words, no match to script content.
- **Seedance**: also static across the clip. Four short bullet points, each 1-2 pseudo-words. More letter-like than Kling's output but still gibberish -- none of the five real lines appear, not even a fragment or a correct word.

## 4. What this means

| Question | Answer |
|---|---|
| Do hosted commercial APIs render on-screen text better than self-hosted models? | No -- on this test, both hosted models did noticeably worse than HunyuanVideo 1.5, which got two full sentences verbatim correct using the same prompt discipline. |
| Is this a prompt-format problem (like Hunyuan's initial failure in round 13)? | Possibly -- neither model's own docs were checked as thoroughly as Hunyuan's Prompt Handbook was in round 13; a retry with each model's own recommended text-rendering prompt convention, and/or the split-line approach that fixed Hunyuan, hasn't been tried yet. See "Still to do." |
| Does this change the project's standing recommendation? | No -- compositing (rounds 10-11, hand-drawn/overlaid text) remains the only approach with 100%-correct text. Generation-time text rendering, hosted or self-hosted, has not yet produced a fully reliable result in 16 rounds. |

## 5. Still to do

1. Retry both models with the split-line prompt format (2-3 shorter generations instead of one five-line prompt), the same fix that worked for Hunyuan in round 13 v3, before concluding either model fails outright on text rendering.
2. Check each model's own prompting documentation (if any) for a recommended on-screen-text convention, the way Hunyuan's Prompt Handbook was found and used in round 13.
3. If a second pass still fails, deprioritize hosted APIs for text-accuracy work and treat compositing (rounds 10-11) as the standing recommendation for any deliverable that requires correct on-screen text.

## 6. Files

- `clips/kling_round16.mp4`, `clips/seedance_round16.mp4`: the two generated clips.
- `raw/kling_frame_{001,060,120}.png`, `raw/seedance_frame_{001,060,120}.png`: inspection frames.
- `raw/raw_record_kling.json`, `raw/raw_record_seedance.json`: generation records (request id, endpoint, timing).
- `run_fal_test.py`: the script used to submit, poll, and download both jobs via fal.ai's queue API. Reads the API key from `server/falAPI.txt` (git-ignored, never printed).
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$0.97 total (Kling ~$0.35 + Seedance ~$0.62), well within the $25 credited to fal.ai for this round.
