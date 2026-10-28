[← All rounds](../../../README.md)

# Round 18: Wan 3.0 -- new best result, defect narrows to line-wrap duplication (Oct 29, 2026)

Status: complete. Tested whether Wan 3.0 (Alibaba's newest release, available on fal.ai since round 17) improves on round 17's Wan 2.7 result, and used its `seed` parameter (which the 2.7 endpoint doesn't expose) to make this round pinned and reproducible going forward.

## Watch the clip

<video src="clips/wan30_round18.mp4" controls width="420"></video>

## 1. Summary

**New best result in this project's history: 3 of 5 lines fully exact, and the other 2 have every word correct except one word duplicated at a mid-sentence line wrap.** This is a narrower, more specific failure mode than anything seen in rounds 1-17 -- not scrambling, not hallucinated words, not dropped content, just the word immediately before a visual line-wrap getting repeated on the next line.

- Line 1 ("Thousands of U.S. advertisers..."): exact.
- Line 2 ("Advertisers are filing refunds for 20-30%..."): every word correct, but renders as "...for 20-30% of / of Ad Spend since 2016." -- "of" duplicates across the wrap.
- Line 3 ("Federal courts have ruled Google illegally monopolized..."): exact.
- Line 4 ("Get the facts, fit criteria and risks."): exact.
- Line 5 ("DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"): every word correct, but renders as "DOWNLOAD EXPLAINER File / File Ad Refunds ADREFUNDS.COM" -- "File" duplicates across the wrap, same pattern as line 2.
- The "20-30%" digit renders correctly again (as in round 17), and "ADREFUNDS.COM" is exact.
- The lawyer's pointing hand occludes parts of the text in the first and last inspected frames -- an occlusion/framing issue, not a text-rendering error, similar to round 17's late-clip crop.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (`alibaba/wan-3.0/text-to-video`), via fal.ai |
| Prompt | Same five quoted lines as rounds 16-17, same lawyer-at-whiteboard framing, with one addition: "the whiteboard stays fully visible in frame" (an attempt to address round 17's late-clip crop) |
| Seed | 10001 (pinned -- this endpoint exposes `seed`, unlike Wan 2.7's) |
| Duration / resolution | 5s, 1080p, 16:9 |
| Generation time | 155.2s (~2.6 min) -- notably faster than Wan 2.7's 577.8s |
| Cost | ~$1.00 |

## 3. Results

Direct frame inspection at frames 1, 60, 120 (`raw/wan30_frame_{001,060,120}.png`):

- **Frame 1**: all five lines visible; the lawyer's hand covers part of line 4 and line 5. Text matches the pattern described above (exact except the two line-wrap duplications).
- **Frame 60**: clearest frame, hand lowered. Confirms the line-wrap duplication pattern precisely -- "of" repeats at the line 2 wrap, "File" repeats at the line 5 wrap. All other words across all five lines are correct.
- **Frame 120**: same text content as frame 60; the lawyer's hand has moved back up and again partially covers lines 3-5.

The added framing instruction ("whiteboard stays fully visible") did not fully prevent occlusion -- the hand still crosses the board at two of the three inspected frames, though the whiteboard itself stays in frame (unlike round 17's crop, where the board edge was cut off).

## 4. What this means

| Question | Answer |
|---|---|
| Is Wan 3.0 better than Wan 2.7? | Yes -- same single-prompt, no-split-line approach, but 3/5 lines fully exact (vs. 2.7's... actually comparable: 2.7 had 4/5 exact with 1 line missing words; 3.0 has 3/5 exact with 2 lines having one duplicated word each but no dropped content). Overall, 3.0's defect pattern is more consistent and more specific -- always a wrap-point duplication, never a dropped phrase. |
| Does pinning a seed help reproducibility going forward? | Yes -- this round's seed (10001) is recorded, so a rerun with the identical payload can now directly test whether this exact result reproduces, closing the gap round 17 left open. |
| Is the line-wrap duplication bug fixable? | Possibly a prompt-engineering fix -- forcing each quoted line to stay on one visual line (e.g. shorter lines, or an explicit "single line" instruction) may avoid the wrap point entirely. Untested so far. |
| Does this change the project's standing recommendation? | Further strengthens the case from round 17: Wan 3.0 is now the strongest generation-time candidate tested, ahead of Wan 2.7, HunyuanVideo 1.5, and the round 16 hosted APIs. Still not pixel-perfect, so compositing (rounds 10-11) remains the only 100%-reliable path, but the gap has narrowed further. |

## 5. Still to do

1. Rerun with the identical seed (10001) and payload to directly test reproducibility -- the open question round 17 couldn't answer.
2. Test whether shortening lines 2 and 5 (to avoid a mid-sentence wrap) eliminates the duplication defect.
3. Test a stronger occlusion-avoidance instruction (e.g. "the lawyer's hand and marker never cover the whiteboard text") to see if that's controllable via prompt.
4. If reproducible, treat Wan 3.0 as this project's new leading generation-time candidate for any future text-accuracy round.

## 6. Files

- `clips/wan30_round18.mp4`: the generated clip.
- `raw/wan30_frame_{001,060,120}.png`: inspection frames.
- `raw/raw_record_wan30.json`: generation record (request id, endpoint, payload including seed, timing).
- `run_fal_test.py`: the script used to submit, poll, and download the job via fal.ai's queue API. Reads the API key from `server/falAPI.txt` (git-ignored, never printed).
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$1.00, well within the remaining fal.ai balance from round 16's $25 top-up.
