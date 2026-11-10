# Round 36: fix reflection/ghost, stray mark after "pay", underline width; add rectangle around "vibe-coded"

User reviewed round 35's three attempts and preferred attempt 1 (the
original 5-line version) over the 4-line version ultimately shipped as
round 35's deliverable. Four issues to address, carried into a new round
built on attempt 1's 5-line text:

1. A second, ghost-like figure of the woman appears on the right side of
   the frame -- a reflection/duplicate visible through or behind the
   glass board.
2. A small stray mark (a parenthesis-like loop) appears right after "pay"
   at the end of line 4 -- not asked for anywhere in the prompt.
3. The underline should cover only "x.country", not spill onto "on"
   (round 34/35's leftover issue, still not fully fixed).
4. New requirement: draw a rectangle around the word "vibe-coded" (in
   line 1), in addition to the existing circle around "$99" and underline
   under "x.country".

User explicitly allowed extending the clip's duration if needed to fit
everything cleanly, since round 35 already found that 5 lines + multiple
annotations is a lot of action for a single clip.

## Fix

- **Duration extended from 10s to 15s** (Seedance 2.0 supports up to 15s)
  to give the extra rectangle annotation room without forcing the same
  content-vs-runtime tradeoff that caused round 35's dropped-line and
  punctuation-glitch failures.
- **Explicit no-reflection/no-ghost rule**: added to both the scene
  description and the critical-requirements list -- "the glass is
  perfectly clear with no reflection of her, no mirrored double, no ghost
  image, and no second figure visible anywhere," reinforced with "there is
  exactly one woman in the frame throughout the entire video."
- **Explicit no-stray-mark-after-text rule**: added to the writing
  sequence itself (step 3), not just the annotation steps -- "the instant
  each line of text is finished, the marker lifts immediately -- no extra
  mark, no stray punctuation, no small tick or loop is added next to or
  after the last word of any line."
- **Underline-width fix carried over** from round 35's wording (explicit
  left/right edge, visible gap from the circle), tried again since it
  wasn't fully resolved there.
- **New rectangle-around-"vibe-coded" step**: added as the first
  annotation (drawn before the circle and underline), as four straight
  strokes drawn one side at a time, with the same progressive-growth and
  no-overshoot rules applied to it as to the other marks.
- Kept the 5-line text from round 35's attempt 1 (not the 4-line merge),
  per the user's preference.

## What to check

- Is there exactly one woman visible in the frame throughout -- no
  reflection/ghost?
- Is there any stray mark after "pay" (or after any other line)?
- Does the rectangle tightly enclose only "vibe-coded"?
- Does the underline cover only "x.country", not "on"?
- All checks carried from round 35: text accuracy (all 5 lines, correct
  "$99"/"x.country" punctuation), progressive stroke growth, no pop-in,
  camera fixed, look-at-camera only at the end.

## Budget

~$3.63 for one 15s/720p Seedance attempt (duration-scaled from round
35's ~$2.42/10s rate). Confirm with the user before any retries.
