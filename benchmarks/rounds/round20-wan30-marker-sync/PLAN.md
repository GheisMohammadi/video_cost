[← All rounds](../../../README.md)

# Round 20 plan: can a stronger prompt get the marker to actually trace the letters?

## Why

Round 19 found that Wan 3.0's "writing animation" is a line-by-line reveal, not genuine handwriting -- each line appears as a whole pre-formed block near wherever the hand currently is, with no visible sync between the marker tip and individual letters. This round tests whether that's fixable with a much more explicit, mechanically-descriptive prompt (describing the pen tip touching the board and an ink trail following it letter by letter), or whether it's a hard limitation of the model that no prompt phrasing gets around.

## Test

Same model (`alibaba/wan-3.0/text-to-video`, fal.ai), same seed (10001) and script as rounds 18-19, for direct comparability. Prompt rewritten to be far more explicit about the mechanical act of writing: the marker tip touches the whiteboard, an ink trail appears exactly where the tip moves, letter by letter, left to right, no text appearing anywhere the tip has not yet physically touched.

To keep the clip short enough to actually show letter-level tracing in 5 seconds, this test uses only the first script line (the one that rendered exactly correct in every prior round) rather than all five -- if the model can't trace even one short line's letters within 5 seconds, it's unlikely to manage five lines, and a single-line test isolates the marker-sync question from the text-accuracy question already answered in rounds 18-19.

## Budget

Remaining fal.ai balance (~$21 left after rounds 16-19). Estimated cost for 1-2 test clips at 5s, 1080p: $1-2.

## Verification

Tight frame-by-frame inspection (every 5 frames, the method that caught round 19's overstated claim) checking specifically whether the marker tip position matches the leading edge of newly-appeared ink, not just whether the board fills in over time.
