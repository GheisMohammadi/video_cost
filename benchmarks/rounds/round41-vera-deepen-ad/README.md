[← All rounds](../../../README.md)

# Round 41: Vera / Deepen AI ad test ("$5 per person-hour")

Status: complete (internal cost/quality test only -- not a publication,
voice save, or identity lock; see "Not authorized" below). Boss-supplied
ad copy ("Human-in-the-loop review for AI in production. Pay $5 per
person-hour. https://services.deepen.ai"), tested in round 39/40's
cheap-model whiteboard-writing format, anchored on the reference
candidate portrait from the boss-supplied `Vera-Deepen-Character-Kit-v0.2`.

## Watch the clips

<video src="clips/round41_minimax_attempt1.mp4" controls width="260"></video>
<video src="clips/round41_minimax_attempt2.mp4" controls width="260"></video>

(left: attempt 1, URL typo. right: attempt 2, fixed)

## 1. Summary

- **Attempt 2 is a clean, usable result.** All 4 lines text-accurate
  (one minor miss: "Human-in-the-loop" lost its second hyphen, rendering
  "Human-in-the loop"), circle tight around "$5", underline matching the
  URL line with no overshoot, identity consistent with the reference
  portrait throughout (dark bob, round graphite glasses, pale-blue
  stand-collar shirt, watch), progressive writing confirmed mid-clip, and
  she looks at camera only at the end as scripted.
- **Attempt 1 had one real defect:** the URL rendered as
  "services**-**deepen.ai" (hyphen) instead of "services**.**deepen.ai"
  (period) -- notable because this is the actual CTA link, not
  decorative text. Strengthening the prompt's URL instruction (naming
  the character as "a small round dot on the baseline, never a dash")
  fixed it on the very next attempt.
- Both attempts used `minimax/h3-max-turbo/image-to-video`, anchored on
  `vera-portrait-v01.png` per the kit's gating rules (only approved
  identity-anchor candidate; the other two reference stills are scene
  studies only).

## 2. What was run

| Item | Value |
|---|---|
| Model | `minimax/h3-max-turbo/image-to-video` |
| Reference image | `Vera-Deepen-Character-Kit-v0.2/assets/vera-portrait-v01.png` (review candidate, not yet client-approved) |
| Prompt | `prompt_short.txt` -- condensed whiteboard-writing format from rounds 36-39, adapted for this script |
| Resolution / aspect | 768P, 16:9 |
| Duration | 15s each |
| Attempts | 2 (attempt 1: URL hyphen defect; attempt 2: strengthened URL wording, fixed) |
| Cost | ~$0.42 x 2 = ~$0.84 total, under the $5 cap |

`run_fal_test.py` usage: `python3 run_fal_test.py`.

## 3. What this means

| Question | Answer |
|---|---|
| Can this cheap model handle Vera's reference look plus this ad copy in one clip? | Yes, on the second attempt -- all text correct, annotations tight, identity consistent. |
| Is the URL-punctuation defect (hyphen vs. period) a recurring risk? | Possibly -- it's a new variant of the punctuation-drift pattern seen on "x.country" in rounds 34-37. Worth watching on any future script with a dotted domain. |
| Is this cleared for real use? | No. This is a cost/quality test of boss-supplied copy against an unapproved reference character, per the kit's own gating rules -- see "Not authorized" below. |

## 4. Not authorized by this round

Per `Vera-Deepen-Character-Kit-v0.2/START-HERE.md`: no voice work, no
identity lock, and no publication are authorized by this test. The
reference portrait remains a review candidate pending client approval.
"$5 per person-hour" and `services.deepen.ai` are boss-supplied ad copy,
not claims verified in the kit's `CLAIMS-REGISTER.json`.

## 5. Files

- `clips/round41_minimax_attempt1.mp4`, `clips/round41_minimax_attempt2.mp4`: the two generated clips.
- `prompt_short.txt`: prompt used for attempt 2 (current state; attempt 1 lacked the strengthened URL-punctuation wording).
- `run_fal_test.py`: generation script, see usage above.
- `raw/raw_record_round41_minimax_attempt1.json`, `raw/raw_record_round41_minimax_attempt2.json`: generation metadata.
- `raw/attempt1_frame_{early,mid,last}.png`, `raw/attempt2_frame_{mid,last}.png`: sampled frames used for the visual review in section 1.
- `PLAN.md`: this round's plan, frozen before running.
- `Vera-Deepen-Character-Kit-v0.2/`: boss-supplied reference kit (character book, profile, references, claims register).

## 6. Cost

~$0.84 total (2 attempts x ~$0.42), under the boss-approved $5 cap.
