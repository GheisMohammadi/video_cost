[← All rounds](../../../README.md)

# Round 42: regenerate round 41's ad, compare cheap models, cut cost

Status: complete. Seven passes were needed to land on the accepted fix:
(1) post-trimmed round 41's existing clip for free; (2) regenerated
from scratch via image-to-video and confirmed the opening-frame glitch
can't be prompted away; (3) tried MiniMax text-to-video (no
reference-image anchor) to avoid the glitch by construction -- it did,
but introduced a worse defect (text appeared fully formed before the
marker tip reached it) and was rejected; (4) reverted to image-to-video
+ trim (v1, accepted at the time) but review caught a sequencing
defect: she circled "$5" and drew the underline while line 4 (the URL)
was still only partly written; (5) v3, with an explicit "finish all
four lines before any annotation begins" instruction plus 1 extra
second of duration (15s vs 14s) -- fixed that, but review caught a
*different*, worse defect within line 3 itself: she skipped ahead to
line 4 while "per person-hour" was still missing from line 3, and the
missing text then appeared on line 3 after the tip had already moved
on; (6) v4, with an explicit word-by-word, no-skip-ahead rule for every
line -- fixed that, but review caught the circle/underline ordering
regressing *again*: she circled "$5" while the URL was still only
partly written ("https://servic..."); (7) **v5**, with the
circle/underline instruction rewritten to require the marker to have
fully lifted off line 4 at least once before touching "$5" again --
confirmed by frame sampling: at 9-10.5s the full URL is complete and no
circle exists yet, and the final frame shows correct circle, underline
and, this time, both URL punctuation marks as periods.

## Watch the clip

<video src="clips/round42_minimax_480p_v5_final.mp4" controls width="260"></video>

(MiniMax H3 Max Turbo, image-to-video, 480P, 15s, opening glitch frame
trimmed, correct per-line and per-annotation order -- accepted result)

**One open defect in this exact take (unresolved, pre-existing):** line
1 drops one of its three hyphens ("Human-in-the loop" instead of
"Human-in-the-loop"). This has appeared in every attempt in this ad so
far regardless of wording. The URL-punctuation drift that affected v3
and v4 did not reproduce in this take (both marks rendered as correct
periods), though given how intermittently it has appeared across
attempts with identical wording (documented since round 34), it should
still be treated as a risk on any future regeneration, not as fully
resolved.

## 1. Summary

- **Accepted fix (v5): image-to-video, anchored on the reference
  portrait, 15s duration, with the opening glitch frame trimmed in post,
  an explicit word-by-word no-skip-ahead rule for every line, and the
  circle/underline instruction rewritten to require the marker to have
  fully lifted off line 4 at least once before touching "$5" again.**
  Confirmed by frame sampling: at 9-10.5s the full URL
  ("https://services.deepen.ai", both punctuation marks correct) is
  already complete and no circle or underline exists yet; the final
  frame shows both annotations present and correctly placed.
- **Text-to-video was tried and rejected.** Dropping the reference-image
  anchor does remove the opening-frame glitch by construction, but
  introduces a worse problem: at the 2s mark, the entire first line is
  already fully written while the marker tip is still down near her
  chest. Not acceptable for an ad whose whole premise is watching her
  write it.
- **One open defect in the accepted take (unresolved, pre-existing):**
  line 1 drops one of its three hyphens ("Human-in-the loop" instead of
  "Human-in-the-loop"). This has reproduced in every attempt in this ad
  regardless of wording changes made for other defects.
- The URL-punctuation drift that affected v3 and v4 (a dash where a
  period should be) did not reproduce in v5 -- but given how
  intermittently it has appeared across attempts with identical wording
  (documented since round 34), treat it as a residual risk on any future
  regeneration, not as definitively fixed.

## 2. What was tried and ruled out

| Attempt | Result |
|---|---|
| Image-to-video, stronger "no glitch frame" prompt wording | Glitch frame persisted on both MiniMax resolutions and PixVerse -- confirms fixed conditioning behavior, not a wording gap. |
| PixVerse 540P (image-to-video) | Wrong wardrobe for the entire clip, "for Ai" capitalization error, no circle on "$5", URL regressed to dashes. Most expensive option tried. Dropped. |
| MiniMax text-to-video, no image anchor | No opening glitch, but text appears before the marker tip reaches it. **Rejected.** |
| Image-to-video + trim, 14s, no ordering instruction (v1) | Opening glitch fixed, content accurate, but circle/underline started *before* the URL line finished writing. |
| Image-to-video + trim, 14s, explicit write-then-annotate order (v2) | Circle/underline ordering fixed, but the clip ran out of time before the underline -- it's missing entirely. |
| Image-to-video + trim, 15s, write-then-annotate order + reinforced URL wording (v3) | Circle/underline ordering correct, underline present -- but caught a *different*, worse defect: she skipped ahead to line 4 while line 3 ("per person-hour") was still incomplete, and the missing words then appeared on line 3 after the tip had already left it. |
| Image-to-video + trim, 15s, word-by-word no-skip-ahead rule for every line (v4) | Each line genuinely completed in order -- but the circle/underline ordering regressed: she circled "$5" while the URL was still only partly written ("https://servic..."). |
| **Image-to-video + trim, 15s, per-line rule + circle/underline gated on the marker lifting off line 4 at least once (v5, accepted)** | **Per-line order correct, circle/underline strictly after all text, both URL punctuation marks correct in this take.** |

## 3. What was run

| Model | Mode | Resolution | Duration | Generation cost | Result |
|---|---|---|---|---|---|
| **`minimax/h3-max-turbo/image-to-video` (v5)** | **image-to-video (anchor), trimmed, per-line + ordering fixed** | **480P** | **15.1s, ~14.7s after trim** | **~$0.26** | **Accepted -- correct per-line and annotation order, correct URL punctuation** |
| `minimax/h3-max-turbo/image-to-video` (v4) | image-to-video (anchor), trimmed, per-line fixed | 480P | 15.1s, ~14.7s after trim | ~$0.26 | Correct per-line order, but circle/underline started before the URL finished |
| `minimax/h3-max-turbo/image-to-video` (v3) | image-to-video (anchor), trimmed, ordering-fixed | 480P | 15.1s, ~14.7s after trim | ~$0.26 | Correct circle/underline order, but line 3 written out of sequence (skip-ahead + retroactive fill) |
| `minimax/h3-max-turbo/image-to-video` (v2) | image-to-video (anchor), trimmed, ordering-fixed | 480P | 14.4s, ~14.0s after trim | ~$0.25 | Correct circle/underline order, but underline missing (ran out of time) |
| `minimax/h3-max-turbo/image-to-video` (v1) | image-to-video (anchor), trimmed | 480P | 14.4s, ~14.0s after trim | ~$0.25 | Accurate content, but circle/underline started before text finished |
| `minimax/h3-max-turbo/image-to-video` | image-to-video (anchor), trimmed | 768P | 14.4s, ~14.0s after trim | ~$0.40 | Same as 480P v1, sharper -- not re-run with the later fixes |
| `fal-ai/pixverse/v6/image-to-video` | image-to-video (anchor) | 540P | 14.0s | ~$0.49 | Wrong wardrobe, URL/circle defects -- not usable |
| `minimax/h3-max-turbo/text-to-video` | text-to-video (no anchor) | 480P | 14.4s | ~$0.25 | No opening glitch, but text pre-formed ahead of the marker tip -- rejected |

Total spend this round: ~$2.43 across all eight attempts (one PixVerse
attempt also hit a 422 for an over-length prompt before being resubmitted
with a condensed one -- that attempt was rejected at submission time, so
it was never queued or billed).

`run_fal_test.py` usage: `python3 run_fal_test.py <minimax_480p|minimax_768p|pixverse_540p>` (image-to-video, now at 15s with the per-line + ordering fix baked into `prompt_short.txt`).
`run_fal_test_t2v.py` usage: `python3 run_fal_test_t2v.py <480p|768p>` (text-to-video, tried and rejected).
Opening-frame trim applied with `ffmpeg -ss 0.4 -c:v libx264 -crf 18 -preset veryfast` (no cost, no re-generation).

## 4. What this means

| Question | Answer |
|---|---|
| Can the opening-frame glitch be fixed by prompting while still anchoring on the reference image? | No -- confirmed with a much stronger instruction on the same model; it's conditioning-image behavior, not a wording gap. |
| Can it be avoided by dropping the image anchor (text-to-video)? | It removes the opening glitch, but introduces a worse defect: text appears fully written before the marker tip reaches it. Rejected. |
| Can within-line ordering (no skip-ahead, no retroactive fill) be enforced? | Yes, with an explicit word-by-word, no-skip-ahead rule for every line -- confirmed on v4 and v5. |
| Can circle/underline-after-all-text ordering be reliably enforced? | Mostly -- it held on v2 and v3, regressed on v4, and held again on v5 once gated explicitly on "the marker has lifted off line 4 at least once." Treat as probabilistic, not guaranteed, on any single generation -- verify by frame sampling before accepting a take. |
| Is the URL-punctuation drift (period vs. dash) fixed? | Not reliably -- correct in this exact take, but it's an intermittent defect going back to round 34 that has flipped between correct and wrong across attempts with identical wording. Re-check it on any future regeneration. |
| Is a cheaper resolution worth it? | Yes -- MiniMax 480P matches 768P's accuracy at ~65% of its cost. |
| Is PixVerse a viable cheaper alternative for this specific script? | No -- worse accuracy and it was the most expensive option tried. MiniMax remains the better model for this task. |

## 5. Files

- `clips/round42_minimax_480p_v5_final.mp4`: **accepted result** (image-to-video, 15s, trimmed, correct per-line and annotation order, correct URL punctuation).
- `clips/round42_minimax_480p_v4_final.mp4`, `clips/round42_minimax_480p_v3_final.mp4`, `clips/round42_minimax_480p_v2_final.mp4`, `clips/round42_minimax_480p_final.mp4`: earlier attempts kept for reference (v4: circle/underline started early; v3: line 3 written out of sequence; v2: underline missing; v1: wrong annotation order).
- `clips/round42_minimax_768p_final.mp4`: 768P version of v1's fix (not re-run with the later fixes) -- viable alternative if sharper detail is needed and the fixes are reapplied.
- `clips/round42_minimax_480p.mp4`, `clips/round42_minimax_480p_v2.mp4`, `clips/round42_minimax_480p_v3.mp4`, `clips/round42_minimax_480p_v4.mp4`, `clips/round42_minimax_480p_v5.mp4`, `clips/round42_minimax_768p.mp4`, `clips/round42_pixverse_540p.mp4`: untrimmed image-to-video outputs, kept for reference.
- `clips/round42_minimax_t2v_480p.mp4`: text-to-video attempt, kept for reference -- **rejected**, text appears ahead of the marker tip.
- `prompt_short.txt`: image-to-video prompt, current state is v5 (per-line rule + circle/underline gated on line 4 completion + reinforced URL wording, 15s).
- `prompt_t2v.txt`: text-to-video prompt (identity described in words, no image anchor) -- the rejected attempt.
- `prompt_pixverse.txt`: condensed version of the pre-v3 prompt, under PixVerse's 2048-byte cap.
- `run_fal_test.py`: image-to-video generation script, see usage above.
- `run_fal_test_t2v.py`: text-to-video generation script (rejected path).
- `raw/raw_record_round42_*.json`: generation metadata for every attempt.
- `raw/i2v_check_{3,5}.png`: frames confirming genuine marker-tip sync on v1.
- `raw/v2_seq_*.png`, `raw/v3_seq_*.png`, `raw/v4_fine_*.png`, `raw/v4_circle_*.png`, `raw/v5_check_*.png`: frame-by-frame sequencing checks for v2-v5.
- `raw/t2v_check_{0.5,2,4,6}.png`: frames confirming the text-before-tip defect on the rejected text-to-video attempt.
- `raw/v2_final_last.png`, `raw/v3_final_last.png`, `raw/v4_final_last.png`, `raw/v5_final_last.png`, `raw/t2v_480p_{t0,mid,last}.png`, `raw/round42_{minimax_480p,minimax_768p,pixverse_540p}_{t0,mid,last}.png`, `raw/round42_{minimax_480p,minimax_768p}_final_t0.png`: sampled frames used for the visual review above.
- `PLAN.md`: this round's plan, frozen before running.

## 6. Cost

~$2.43 total across all eight attempts (MiniMax 480P v1 ~$0.25, v2 ~$0.25, v3 ~$0.26, v4 ~$0.26, v5 ~$0.26 -- the accepted result, MiniMax 768P ~$0.40, PixVerse 540P ~$0.49, MiniMax text-to-video ~$0.25 -- rejected).
