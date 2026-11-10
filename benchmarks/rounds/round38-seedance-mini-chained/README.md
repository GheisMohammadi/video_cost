[← All rounds](../../../README.md)

# Round 38: apply line-by-line chaining to the text+annotation task, test Seedance Mini

Status: blocked (fal.ai balance exhausted mid-round). User insight: rounds
36/37's single-clip attempts at "4 lines of text + 3 annotations" kept
jumbling content because too much action was crammed into one generation.
The whiteboard rounds (27-31) solved this for plain text by chaining one
short clip per line via I2V, with the hand carried to the next position.
This round applies that same structure here, testing whether it also
fixes Seedance Mini's quality problems from round 37.

## 1. Summary

- **Structure**: 7 chained clips -- 4 text lines, then 3 annotations
  (rectangle around "vibe-coded", circle around "$99", underline under
  "x.country"), each chained via I2V from the previous clip's last frame,
  5s/720p/16:9 per clip.
- **Step 1 (text, Mini): clean on the first try.** Correct text, hand
  carried cleanly below the line, no reflection/ghost.
- **Step 2 (text, Mini): failed 3 times in a row**, all with the same
  pattern -- "Launched" misspelled as "Launcked", and the clip writing
  ahead into later steps' content (e.g. appending "$99 x.contry" onto this
  step's line). This was a repeated, systematic failure, not variance.
  Switched the 4 text steps to the "fast" tier per the user's direction
  (keeping the 3 annotation steps on Mini, since they hadn't been tested
  yet and are structurally simpler).
- **Step 2 (text, Fast): succeeded on the 3rd submission attempt** (2
  earlier submissions were rejected by a transient content-moderation
  false positive on the input frame -- `"may contain likenesses of real
  people"` -- not a real content issue, cleared on retry). Text came out
  correct, though a stray unintended underline-like mark appeared beneath
  "Launched 19" -- a minor defect, not pursued further.
- **Step 3 (text, Fast): failed twice**, both times writing ahead --
  "So this week I pay" came out as "So this week I pay $99 x-country",
  pulling step 4's content into step 3's line and dropping the period in
  "x.country" again. This is the same write-ahead failure mode seen on
  Mini, now also appearing on Fast -- looks like a genuine model
  completion bias (recognizing the sentence and wanting to finish it)
  rather than a tier-specific defect. Strengthened the stop-rule wording
  significantly (explicitly framing the sentence as continuing "across
  several separate videos" and stating her hand "stops writing entirely"
  after the stated text) before the blocker below hit.
- **Blocked**: the fal.ai account's balance ran out again mid-retry of the
  strengthened step 3 prompt. Round paused here, unresolved, pending a
  top-up.

## 2. What was run so far

| Item | Value |
|---|---|
| Models | `bytedance/seedance-2.0/mini/{text,image}-to-video` (step 1, originally steps 2-7); `bytedance/seedance-2.0/fast/{text,image}-to-video` (steps 2-4, after the switch) |
| Resolution / aspect | 720p, 16:9 |
| Duration | 5s per clip (7 clips planned) |
| Attempts so far | step 1: 1; step 2: 4 (3 on Mini, 1 on Fast); step 3: 2 (both on Fast) |
| Cost so far | ~$3.08 (1 Mini text clip + 1 Mini image clip attempt + 4 Fast image clip attempts, 5s/720p each, excluding the 2 submissions rejected before generation started) |

## 3. Technical notes for continuing this round

- **Seedance's image-to-video field name is `image_url`, not
  `start_image_url`** (the Wan convention used in the whiteboard rounds)
  -- `run_fal_test.py` was fixed to use the correct field name after the
  first chain attempt failed with a `422 missing image_url` error.
- **Seedance Mini's output needs `ffmpeg -sseof -1 ... -frames:v 1
  -update 1`** to extract the last frame reliably -- the `-sseof -0.1`
  approach used for Wan/Seedance Fast in prior rounds produced an empty
  PNG on Mini's output container. `run_fal_test.py` uses the more robust
  `-1`/`-update 1` form throughout now, which works for both tiers.
- **Transient content-moderation 403s/422s on chain-anchor frames**
  happened twice in this round (once attributed, once likely) -- a
  `content_policy_violation` / `"may contain likenesses of real people"`
  false positive on the synthetic presenter's own face. Both ccleared on
  a bare retry with the identical image. Treat this as expected noise,
  not a real problem to fix.
- **The write-ahead failure is the open, unresolved problem.** It
  happened on both Mini and Fast, on two different lines ("Launched 19."
  pulling in later content; "So this week I pay" pulling in "$99
  x-country"), always completing toward the next piece of the known
  sentence. The strengthened stop-rule wording (framing the sentence as
  spanning multiple separate videos, stating her hand stops writing
  entirely after the target text) was queued for a retry when the
  balance ran out -- worth checking first once generation resumes.

## 4. What this means so far

| Question | Answer |
|---|---|
| Does line-by-line chaining fix the structural problems from rounds 35-36 (reflection, hand-carry jump cuts)? | Yes, confirmed on the clips that completed -- no reflection, clean hand-carry between steps. |
| Does chaining fix Seedance Mini's text-accuracy problems from round 37? | No -- Mini still produced misspellings and write-ahead content even with just one short line per clip (3/3 failures on step 2). |
| Is the write-ahead failure tier-specific? | No -- it reproduced on Fast too (step 3, 2/2 failures), suggesting a model completion bias tied to recognizing the sentence, not a Mini-specific weakness. |
| Open issue | Round incomplete -- blocked on fal.ai balance mid-retry of a strengthened stop-rule prompt for step 3. |

## 5. Files

- `clips/round38_step1.mp4`: step 1, final (Mini, text-to-video).
- `clips/round38_step2.mp4`: step 2, final (Fast, succeeded on the 3rd submission).
- `clips/round38_step2_attempt1.mp4`, `clips/round38_step2_attempt2.mp4`, `clips/round38_step2_attempt3_mini.mp4`: step 2's three failed Mini attempts, kept for reference.
- `clips/round38_step3_attempt1.mp4`, `clips/round38_step3_attempt2.mp4`: step 3's two failed Fast attempts (both write-ahead), kept for reference. Step 3 not yet resolved.
- `run_fal_test.py`: generation script -- 7-step chain definition, tier switched per step, see usage in the file's docstring.
- `denoise_frame.py`: chain-anchor frame cleanup, carried over unchanged from round 30.
- `raw/raw_record_round38_*.json`: generation metadata for every attempt.
- `raw/check_step*.png`: sampled last-frames used for the visual review above.
- `PLAN.md`: this round's plan, frozen before running.

## 6. Cost so far

~$3.08 (partial -- round incomplete, 4 of 7 steps not yet attempted or not yet resolved).
