[← All rounds](../../../README.md)

# Round 39: continue the text+annotation task on cheap models

Status: complete (single-attempt screen). Continuation of round 38, which
left the text+annotation task (write 4 lines, then annotate with a
rectangle, circle, and underline) blocked on a fal.ai balance exhaustion.
Round 40 screened two genuinely cheap models (PixVerse V6, MiniMax H3 Max
Turbo) against an unrelated diagram task; this round runs those same
models against the actual task in progress, in one 15s clip each (not
round 38's 7-step chain).

## Watch the clips

<video src="clips/round39_pixverse.mp4" controls width="260"></video>
<video src="clips/round39_minimax.mp4" controls width="260"></video>

(left to right: PixVerse V6, MiniMax H3 Max Turbo)

## 1. Summary

- **MiniMax H3 Max Turbo produced the best result in this project's
  history for this task.** All 4 lines rendered exactly correct ("I
  vibe-coded my app" / "in a weekend. Launched 19." / "So this week I
  pay" / "$99 on X.country" -- only a capital-X drift from the prompt's
  lowercase "x"). The rectangle sits tight around "vibe-coded", the
  circle sits tight around "$99", and -- for the first time across
  rounds 34-38 -- the underline sits under "x.country" alone with no
  overshoot onto "on". No reflection, ghost, or stray marks. A mid-clip
  frame (7s mark) confirms the text was written progressively in real
  time, not merely correct by luck at the end.
- **PixVerse V6 got the annotations right but dropped content.** Rectangle
  and circle both tight and correctly placed, matching round 36's
  quality. But "Launched 19." was dropped from line 2 (rendered as just
  "in weekend,"), "x.country" lost its period ("x country"), and the
  underline overshot onto "on x country" -- the same category of defect
  seen on Seedance across rounds 34-37.
- Both results are from a single attempt each; per project convention,
  not conclusive on their own, but MiniMax's result is strong enough to
  be worth standardizing on for this task going forward, pending a
  confirmation retry.

## 2. What was run

| Item | Value |
|---|---|
| Models | `fal-ai/pixverse/v6/text-to-video`, `minimax/h3-max-turbo/text-to-video` |
| Prompt | Condensed version of round 36's final working prompt (`prompt_short.txt`, 1820 bytes) |
| Resolution / aspect | 720p (PixVerse), 768p (MiniMax), both 16:9 |
| Duration | 15s each |
| Cost | PixVerse ~$0.675 (15s x $0.045/s), MiniMax ~$0.42 (15s x $0.028/s promo rate) -- ~$1.10 total |

`run_fal_test.py` usage: `python3 run_fal_test.py <pixverse|minimax>`.

## 3. What this means

| Question | Answer |
|---|---|
| Can cheap models (5-9x cheaper than Seedance Fast) handle this task in one clip? | MiniMax: yes, on this one attempt, and better than any Seedance attempt tried so far. PixVerse: partially -- annotations correct, text incomplete. |
| Does the underline-overshoot defect (rounds 34-37) persist on these models? | Fixed on MiniMax this attempt. Still present on PixVerse. |
| Is this conclusive? | No -- one attempt per model. Worth a confirmation retry on MiniMax before adopting it as the standard tool for this task. |

## 4. Files

- `clips/round39_pixverse.mp4`, `clips/round39_minimax.mp4`: the two generated clips.
- `prompt_short.txt`: condensed version of round 36's prompt, under both models' character limits.
- `run_fal_test.py`: generation script, see usage above.
- `raw/raw_record_round39_{pixverse,minimax}.json`: generation metadata.
- `raw/pixverse_frame_{early,mid,last}.png`, `raw/minimax_frame_{mid,last}.png`: sampled frames used for the visual review in section 1.
- `PLAN.md`: this round's plan, frozen before running.

## 5. Cost

~$1.10 total (PixVerse ~$0.675, MiniMax ~$0.42), one attempt each.
