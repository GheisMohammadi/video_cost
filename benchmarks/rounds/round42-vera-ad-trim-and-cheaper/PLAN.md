# Round 42: fix round 41's opening-frame identity glitch, and cut cost

Round 41 attempt 2 (`round41_minimax_attempt2.mp4`) is the accepted
result, but its very first frame (t=0) is literally the static
`vera-portrait-v01.png` reference photo itself -- different wardrobe
("everyday" overshirt, no glasses) and a different background (indoor
window) than the described whiteboard scene -- held for a fraction of a
second before the model morphs into the actual scene. Looks like a
different character cutting in at the very start.

## Fix 1: remove the glitch frame

Two options, cheapest first:
1. **Post-trim**, no regeneration: cut the first ~0.3-0.5s (the static
   reference-photo hold) from the existing accepted clip with ffmpeg,
   since the actual scene is fully formed by then. Free, no API cost.
2. If post-trim leaves a visible jump/cut: regenerate with a prompt
   instruction that the scene opens already mid-transition (glasses on,
   board visible, shirt already in the bench look) instead of holding on
   the bare reference photo first -- costs one more generation.

Try (1) first since it's free; only pay for (2) if the cut looks bad.

## Fix 2: cheaper generation

Round 41 used 15s at MiniMax's 768P rate (~$0.42/clip). To cut cost
further:
- Drop resolution to **480P** (MiniMax's cheapest tier, ~$0.0175/s
  promo rate through Nov 15 vs. 768P's $0.028/s -- ~38% cheaper per
  second) if 480P still reads clearly enough for on-screen text at this
  aspect ratio.
- Consider trimming duration below 15s if the actual content (4 lines +
  circle + underline) finishes well before the clip ends -- check round
  41's last-frame timing first; no point paying for idle seconds after
  the writing is done.

## What to check

Same acceptance checks as round 41 (text-accurate incl. the URL's
punctuation, circle tight on "$5", underline on the URL line, consistent
identity, no reflection/stray marks) -- plus: no visible identity/scene
jump at the very start, and confirm 480P text is still legible before
accepting it as the new default resolution.

## Budget

Post-trim: $0. If a regeneration or duration/resolution retest is
needed: 1-2 attempts at ~$0.15-0.30 each (480P, shorter duration) -- well
under $1 total, cheaper than round 41's $0.84.
