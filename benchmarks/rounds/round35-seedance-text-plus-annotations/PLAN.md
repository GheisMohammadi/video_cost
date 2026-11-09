# Round 35: text-writing + annotation marks, single Seedance clip

New test combining the whiteboard-writing task (rounds 1-31) with the
line-drawing task (rounds 32-34): the same presenter persona from rounds
32-34 (young Asian woman, black T-shirt, blue jeans, neon-yellow marker,
transparent glass board, matte black background, studio lighting) writes
a short script and then annotates two parts of it:

- Writes: "I vibe-coded my app in a weekend. Launched 19. So this week I
  pay $99 on x.country" (split into 5 short lines, same compact-handwriting
  approach that fixed line-wrap overflow in round 29).
- Draws a circle around "$99".
- Draws an underline under "x.country".

## Approach

Single 10s Seedance 2.0 generation, tried as-is first (confirmed with the
user: cheapest/fastest to test given the amount of action -- 5 lines of
text plus 2 annotation marks -- is a lot to fit in 10s; iterate from here
if it comes out rushed or garbled, rather than pre-emptively chaining
multiple clips like the whiteboard rounds did).

Only Seedance 2.0 (`bytedance/seedance-2.0/fast/text-to-video`) is used,
per the boss's round-34 direction to focus there.

## Prompt design, carrying forward every lesson learned so far

- **Compact handwriting, one line each** (round 29's fix for line-wrap
  overflow): each of the 5 lines stays on a single horizontal line, never
  wrapping.
- **Progressive stroke growth, never pre-formed** (onset-sync rule, all
  rounds since round 20): applies to every letter, the circle, and the
  underline alike.
- **No-echo** (round 27 on): never retrace or repeat a previous line's
  text.
- **Explicit, position-anchored annotation targets** (round 33's fix for
  round 32's vague box/connection descriptions): the circle encloses only
  "$99", not "on x.country"; the underline matches only "x.country"'s
  width, not extending under "$99" or into empty space.
- **No-overshoot / no-decoration rule** (round 34's fix for Seedance's
  stray correction strokes and arrow-pop-in look): applied to every
  stroke, not just the annotation marks -- the marker lifts immediately
  the instant each stroke reaches its endpoint, no extra marks left
  behind.
- **Face/appearance consistency rule** (round 30's fix for I2V chain-hop
  drift): kept even though this is a single ungained generation, since it
  costs nothing to include and guards against any single-clip drift.

## What to check

- Do all 5 lines render with correct text, no line-wrap, no overflow?
- Does the circle tightly enclose only "$99" (not spilling onto "on
  x.country" or missing part of "$99")?
- Does the underline match only "x.country"'s width?
- Do all strokes (letters, circle, underline) grow progressively under the
  tip, with no pop-in and no stray correction marks at their endpoints?
- Does she look at the board throughout and only at the camera at the very
  end?

## Budget

~$2.42 for one Seedance attempt (10s, 720p). Confirm with the user before
any retries.
