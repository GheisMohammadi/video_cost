[← All rounds](../../../README.md)

# Round 35: text-writing + annotation marks, single Seedance clip

Status: complete. New test combining the whiteboard-writing task (rounds
1-31) with the line-drawing task (rounds 32-34): the same presenter
persona from rounds 32-34 writes a short script and then annotates two
parts of it -- a circle around "$99" and an underline under "x.country" --
all in one continuous Seedance 2.0 generation.

## Watch the clip

<video src="clips/round35_seedance.mp4" controls width="260"></video>

(third attempt, the final deliverable -- see section 3 for the first two)

## 1. Summary

- **Script**: "I vibe-coded my app in a weekend. Launched 19. So this week
  I pay $99 on x.country", written as 4 short lines, then annotated with a
  circle around "$99" and an underline under "x.country".
- **Final result (3rd attempt)**: all 4 lines render correctly, "$99" and
  "x.country" both render with correct punctuation, the circle tightly
  encloses "$99" only, and the underline sits under "x.country" with a
  small overrun onto "on" -- close but not pixel-perfect.
- Took 3 attempts to get here (see section 3) -- the first two each
  surfaced a different defect (punctuation glitches vs. a dropped line),
  both traced to fitting 5 lines of text plus 2 precise annotation marks
  into a single 10-second generation.
- Progressive stroke sync (text, circle, and underline all growing under
  the moving tip, not popping in) held across all three attempts --
  carried forward cleanly from round 34's fixes.

## 2. What was run

| Item | Value |
|---|---|
| Model | `bytedance/seedance-2.0/fast/text-to-video` only (per the boss's round-34 direction to focus on Seedance) |
| Resolution / aspect | 720p, 16:9 |
| Duration | 10s |
| Attempts | 3 (see section 3) |
| Generation time | ~232-414s per clip |
| Cost | ~$7.26 (3 attempts x ~$2.42) |

`run_fal_test.py` usage: `python3 run_fal_test.py` (no arguments).

## 3. Three attempts

1. **Attempt 1** (5 lines, original prompt): all 5 lines present and
   legible, circle correctly tight around "$99", but punctuation drifted
   -- a stray ")" after "pay", "$.99" instead of "$99", "x-country"
   instead of "x.country" -- and the underline covered the whole "$99 on
   x-country" span instead of just "x.country".
2. **Attempt 2** (same 5 lines, tightened punctuation + underline-width
   wording): punctuation fixed ("$99" and "x.country" both correct), but
   a whole line -- "Launched 19." -- was dropped entirely, and the
   underline still overshot onto "on x-country". Diagnosis: 5 lines of
   text plus 2 precise annotation marks is too much action to reliably
   fit into one 10-second generation; the model trades off accuracy
   somewhere to fit the runtime.
3. **Attempt 3** (reduced to 4 lines by merging "in a weekend." and
   "Launched 19." onto one line, same tightened punctuation/underline
   wording): the fix. All 4 lines present and correct, "$99" and
   "x.country" punctuation both correct, circle tight, underline close
   under "x.country" with only a small overrun onto "on" remaining.
   Accepted as the round's deliverable.

## 4. What this means

| Question | Answer |
|---|---|
| Can a single Seedance clip handle both whiteboard-style writing and precise annotation marks? | Yes, once the text content is trimmed to fit the 10s budget -- 4 lines plus 2 annotations worked; 5 lines plus 2 annotations did not reliably. |
| Does naming exact punctuation in the prompt fix text-accuracy glitches? | Yes -- attempt 2 onward had correct "$99" and "x.country" rendering after the prompt explicitly spelled out the exact characters expected. |
| Is the underline-width overshoot (round 34's leftover issue, also seen here) now fixed? | Mostly, not fully -- it's much closer (a small overrun onto "on" vs. covering the whole remaining line in earlier attempts) but not pixel-exact. Open issue for a future round if it matters. |
| Open issue | Underline still slightly overruns past "x.country" onto "on". Not pursued further this round. |

## 5. Files

- `clips/round35_seedance.mp4`: final deliverable (3rd attempt, 4-line version).
- `clips/round35_seedance_attempt1.mp4`: 1st attempt (5 lines, punctuation glitches), kept for reference.
- `clips/round35_seedance_attempt2.mp4`: 2nd attempt (5 lines, dropped a line), kept for reference.
- `prompt.txt`: final prompt (4 lines), with the punctuation and underline-width fixes from attempts 2-3.
- `run_fal_test.py`: generation script, see usage above.
- `raw/raw_record_round35_seedance*.json`: generation metadata for all 3 attempts.
- `raw/frame_*.png`: sampled frames used for the visual review across all 3 attempts.
- `PLAN.md`: this round's plan, frozen before running.

## 6. Cost

~$7.26 total (3 attempts x ~$2.42, 10s/720p each).
