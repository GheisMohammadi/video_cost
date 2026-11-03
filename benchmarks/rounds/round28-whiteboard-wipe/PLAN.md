[← All rounds](../../../README.md)

# Round 28 plan: whiteboard-wipe handoff + crossfade transitions

## Why

Round 27 fixed marker/text sync and ink timing (verified frame-by-frame across all 8 rows) via I2V chaining, but left two problems:

1. **Outfit/presenter changes at the midpoint.** The chain had to restart with a fresh text-to-video generation at row 5 because continuing the I2V chain past ~4 hops caused text to garble (confirmed twice). The fresh restart fixed garbling but let the model reinvent the woman's appearance.
2. **Visible glitch/shake at row-to-row cuts.** Even within a chained segment, each cut (freeze-frame pause -> next generated clip) shows a small jump -- the next clip's first frame doesn't pixel-match the freeze frame exactly, since "continuing from this exact frame" is a re-render, not a guaranteed pixel-identical continuation.

## Approach

### 1. Whiteboard-wipe handoff (fixes outfit consistency)

Instead of restarting the chain with a new text-to-video generation at the midpoint, digitally erase the ink from the row 4 anchor frame's board region (`wipe_board.py`, OpenCV inpainting over a brightness-threshold ink mask) before feeding it to row 5 as the I2V `start_image_url`. Every pixel outside the board rectangle -- her face, hair, outfit, the room -- is untouched, so there is no possibility of the model reinventing her appearance; it is pixel-identical to row 4's last frame except for a blank board.

The row 5 prompt is changed from "continuing from this exact frame... begins a new row of text" to "continuing from this exact frame... she wipes the whiteboard clean with her hand/an eraser, then begins a new sentence" -- narratively motivating why the board is now blank, instead of just presenting a blank board with no in-universe explanation.

This also tests the round 27 open question about *why* row 5 garbled: if the degradation was driven by the model having to read back increasingly complex/blurry accumulated handwriting through repeated re-encoding, wiping the board before that hop removes exactly that input complexity, and may fix the garbling as a side effect, not just the appearance-consistency problem. If row 5 (post-wipe) still garbles, that tells us the degradation is hop-count-driven regardless of board content, and the project will need a different mitigation for long chains.

### 2. Crossfade transitions (fixes glitch/shake)

Round 23/27's stitching used a hard cut straight into a freeze-frame pause, then a hard cut into the next clip. Replacing both cut points with a short crossfade (ffmpeg `xfade`, ~0.15-0.2s) instead of a hard concat should visually absorb the small pixel/pose mismatch between a generated clip's last frame and the next clip's first frame, rather than presenting it as a sudden pop.

## Test order

1. Reuse round 27's rows 1-4 as-is (already verified clean) -- no need to regenerate.
2. Generate row 5 chained from the wiped row 4 frame, verify: (a) same woman/outfit as rows 1-4, (b) blank board at the start, (c) correct new text, (d) no premature ink.
3. If row 5 passes, continue chaining rows 6-8 from it (each new anchor also wiped before being fed forward is not needed now, since there's no segment restart mid-chain for those if they stay within the safe ~4-hop window -- re-evaluate per round 27's observed garbling pattern if row 5 passes its own test but a later row fails).
4. Rebuild the stitched/captioned final video using crossfade transitions instead of hard cuts at every row boundary, and compare the transition smoothness against round 27's version.

## Budget

~$0.50-0.75/clip x up to 4 clips (rows 5-8, reusing rows 1-4) = ~$2-3, plus any retries. Free local post-processing.
