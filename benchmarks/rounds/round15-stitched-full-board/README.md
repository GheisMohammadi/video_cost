[← All rounds](../../../README.md)

# Round 15: turning round 14's isolated wins into one deliverable (Oct 28-29, 2026)

Status: complete. Two approaches tested for combining round 14's correctly-rendered text segments into something closer to a real deliverable: a plain edit (free, no pod) and an image-to-video continuity chain (pod). Neither is a complete, production-ready fix, but each answers a different real question about this project's text-accuracy work.

## Watch both clips

Test 1 — the two-shot edit (free, no pod):

<video src="clips/test1_two_shot_edit.mp4" controls width="420"></video>

Test 2 — the I2V continuation (pod):

<video src="clips/test2_i2v_continuation.mp4" controls width="420"></video>

## 1. Summary

- **Test 1 (free, no pod): a plain edit works, honestly presented as a cut.** Concatenating round 14's A1 and A2 clips produces a 10-second clip with all five script lines correct -- but checking A1's last frame against A2's first frame first confirmed these are two visually distinct generations (different camera angle, pose, shirt pattern), so this is a real jump cut, not a continuous shot. Reported as such.
- **Test 2 (pod): image-to-video continuation preserves existing correct text and adds real continuity, but introduces a new defect.** Starting from A1's actual final frame and continuing generation with lines 3-5 as new quoted text: lines 1-2 stay pixel-correct through the whole continuation (confirming Hunyuan's I2V mode preserves existing text, the same behavior round 10 found for Wan); line 4 ("Get the facts, fit criteria and risks.") renders exactly correct; "ADREFUNDS.COM" renders correctly. But line 3 is wrong/compressed, and unlike round 14's clean isolated A2 result, the new content partially **duplicates itself** -- lines 4 and 5's content each appear to render twice, with different wording each time.
- **Neither approach is strictly better than the other** -- they trade off differently. Test 1 has 100% correct text (it's literally A1 and A2 verbatim) but an obvious cut. Test 2 has real visual continuity (one continuous shot, same person, same framing) but new text accuracy problems the isolated approach didn't have.

## 2. What was run

### Test 1: two-shot edit

Concatenated round 14's `hunyuan_A1_two_lines.mp4` and `hunyuan_A2_deferred_lines.mp4` with `ffmpeg`'s concat demuxer, re-encoded to a single file. No new generation, no pod, zero marginal cost.

**Continuity check performed before any claim was made**: `raw/cut_before.png` (A1's actual last frame) vs. `raw/cut_after.png` (A2's actual first frame) -- different camera angle, different pose, different shirt button pattern. Confirmed this is a hard cut, not a continuous take, before writing up the result.

### Test 2: I2V continuation

| Item | Value |
|---|---|
| Model | `hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-480p_i2v` |
| Starting image | `raw/a1_last_frame.png` -- round 14 A1's actual final frame (lines 1-2 already correct) |
| Prompt | Lines 3-5 as new quoted text, same phrasing as round 14's isolated A2 test, describing the lawyer continuing to write below the existing (preserved) text |
| Settings | 121 frames, 24 fps, 50 steps, seed 10001 -- same convention as rounds 13-14 |
| Load / generate | 251.9 s load, 1975.2 s generate (~33 minutes) on a rented A100 |

## 3. Results

### 3.1 Test 1: correct text, honest cut

`clips/test1_two_shot_edit.mp4` -- watched end to end, all five script lines are legible and correct (reusing round 14's own verified A1 and A2 results). The cut at the 5-second mark is visible and would read as an edited, two-shot video to any viewer -- a legitimate real-world production pattern (most real explainer videos cut between shots), but not a single continuous take.

### 3.2 Test 2: continuity achieved, new duplication defect found

`clips/test2_i2v_continuation.mp4` -- direct frame inspection at frames 1, 60, and 120 (`raw/round15_t2_frame{001,060,120}.png`):

- **Frame 1** (the starting image itself): lines 1-2 exactly as in A1 -- "Thousands of U.S. advertisers are pursuing claims against Google." and "Advertisers are filing refunds for 20-3% of Ad Spend since 2016." (the `20-3%` vs `20-30%` discrepancy is carried over from A1 itself, not introduced here).
- **Frame 60**: lines 1-2 still intact and legible. New text has appeared below: "Federal courts haled Googrch advertising." (wrong -- compresses and garbles line 3, "Federal courts have ruled Google illegally monopolized search advertising") and "Get the facts, fit criteria and risks" (**exactly correct**, matching line 4 verbatim).
- **Frame 120**: lines 1-2 still intact. A third block of text has appeared below the first new block: "Get the facts, fit monopolized snd risks" (a garbled near-repeat of line 4, with a fragment of line 3's "monopolized" merged in) and "DOWNLOAD EXPLAINER File Ad Refunds" / "DOWNLOAD EXLINER ADREFUNDS.COM" (two overlapping, partially garbled near-repeats of line 5 -- "ADREFUNDS.COM" itself is correct in the second one).

**What this confirms**: Hunyuan's image-to-video mode preserves already-correct text through a continuation, the same behavior round 10 documented for Wan's I2V mode -- a second, independent confirmation of that pattern on a different model family.

**What this adds that's new**: unlike round 14's clean, isolated A2 result (each of lines 3-5 appearing once, mostly correct), this continuation shows content **duplicating and varying between repeats** -- line 4's content appears twice with different wording each time, and line 5 similarly. This is a different failure mode than anything documented in rounds 10-14 so far, and it means I2V continuation is not simply "A1 plus A2 stitched for free" -- it has its own, separate accuracy cost.

## 4. What this means

| Question | Answer |
|---|---|
| Can existing correct text survive into a continuation? | Yes -- confirmed again, on a second model family (Hunyuan, after Wan in round 10). |
| Does continuity-based generation match isolated generation's accuracy for the *new* content? | No -- line 3 is wrong and content duplicates, a new problem isolated generation (A2) didn't have. |
| Which approach is the practical recommendation? | Depends on the deliverable. If a visible cut is acceptable (most real explainer/ad content cuts between shots anyway), **Test 1's two-shot edit is the more reliable choice** -- it reuses two results already verified correct. If a single continuous take is required, Test 2 shows it's possible to preserve earlier text while continuing, but the newly-generated portion still needs the same frame-by-frame human QA every other result in this project has needed -- it is not yet reliable enough to skip that check. |
| How does either compare to rounds 10-11's overlay approach? | Rounds 10-11's hand-built compositing still gives the only 100%-controllable, fully-correct result (because the text is drawn, not generated) -- at the cost of the engineering effort documented there. Test 1 and Test 2 are both generation-time approaches with real but partial correctness, consistent with every other generation-time result in this project (rounds 12-14). |

## 5. Still to do

1. Investigate the duplication defect in Test 2 -- does it happen regardless of which lines are continued, or specifically with three stacked text blocks (the starting image's existing 2 lines, plus 2 more new quoted lines, plus the small-print line)? Round 14's A2 isolated three quoted elements (L3, L4, L5) in one generation without this problem; Test 2 adds those on top of 2 already-present lines (5 total blocks of text in the finished frame) -- worth testing whether duplication is a function of total on-screen text blocks, not continuation itself.
2. If a single continuous take is genuinely required for a deliverable, test whether continuing from A2's end (rather than A1's) with only line 5 as new content reduces the duplication problem, by keeping the total new content per generation smaller.
3. Resolve the remaining round 13/14 backlog items: Seedance 2.0 / Kling 3.0 API baseline (still no keys confirmed), and the `20-3%` vs `20-30%` single-digit error, which has now appeared identically in round 14's A1 and carried through unchanged into this round's Test 2 -- worth a dedicated retry to see if it's a seed-specific artifact or a more general small-number rendering weakness.

## 6. Files

- `clips/test1_two_shot_edit.mp4`: Test 1's edited two-shot result (section 3.1).
- `clips/test2_i2v_continuation.mp4`: Test 2's I2V continuation result (section 3.2).
- `raw/cut_before.png`, `raw/cut_after.png`: the frames checked to confirm Test 1 is a real cut, not a continuous take.
- `raw/a1_last_frame.png`: the exact starting image used for Test 2, extracted from round 14's A1 clip.
- `raw/round15_t2_frame{001,060,120}.png`: frames from Test 2 for direct inspection.
- `raw/raw_record_test2.json`: Test 2's generation record (load time, generation time, sha256).
- `i2v_continuation_session.py`: Test 2's pod script.
- `PLAN.md`: this round's plan, frozen before Test 2 ran (Test 1 was run and included before the plan was committed, as a same-session free check).

## 7. Cost

Test 1: free, local, no pod. Test 2: one pod session on a rented A100, ~38 minutes total (load + generation), within this round's approved budget.
