[← All rounds](../../../README.md)

# Round 25 plan: compositing pipeline instead of model-drawn text

## Why

Round 24 confirmed that neither of round 23's two defects is fixable through prompt wording alone:

1. **Onset-sync** (ink appears before the marker tip is in writing position): still present in round 24's row 1 despite a strengthened onset instruction.
2. **Cross-row consistency**: fixed by image-to-video chaining, but chaining introduced a worse defect -- the model started writing the wrong text (repeating the previous row's sentence instead of the new one).

Research into how professional AI whiteboard-explainer tools (Golpo AI, InVideo AI, Animaker, VideoScribe/Doodly) actually produce this effect found they don't ask a single video-generation model to draw text in one shot. They composite: a presenter/hand asset plays over a deterministic, separately-driven text animation (a predefined stroke/path revealed progressively), so the text and the hand motion are mathematically locked together instead of inferred by a diffusion model. This is a structural reason Wan 3.0 keeps failing the same two ways regardless of prompt wording -- generating pixel-accurate, stroke-correct handwriting in sync with a hand isn't a task video diffusion models are built to do reliably.

## Proposed approach

Stop asking Wan 3.0 to draw text at all. Split the job:

1. **Presenter footage (Wan 3.0, as before)**: she turns to the board, mimes a left-to-right writing motion with the marker near the board surface, and turns back -- but the prompt explicitly tells the model the board stays blank / the marker leaves no mark. This keeps using Wan 3.0 for what it's already good at (realistic human motion, plausible gaze behavior, consistent clothing within one clip) and removes the one thing it keeps failing at.
2. **Marker-tip tracking**: track the black marker tip's pixel position frame by frame in the raw clip (color-threshold / template matching), giving an x-position trajectory over the writing motion.
3. **Deterministic text reveal**: render the row's sentence in a cursive/handwriting font as a static image, and reveal it left-to-right as a mask synced to the tracked tip's x-position (reveal progress = (tip_x - start_x) / (end_x - start_x)), not to a fixed time duration. Composite the revealed text onto the board region of each frame.
4. **Stitch + caption**: reuse round 22/23's trim/pause/caption-overlay pipeline on top of the composited clips.

This guarantees, by construction rather than by hope: the text is always the exact scripted sentence (we render it ourselves), and ink only ever appears under/behind the tracked tip position (no onset-sync defect possible, since we are the ones deciding when reveal starts).

## What this does and doesn't fix

- **Text fidelity**: fixed by construction -- we render the exact string, never depend on the model to spell or sequence it correctly.
- **Onset-sync**: fixed by construction -- reveal is driven by tracked tip position, not by the model's own (unreliable) sense of when it "should" start drawing.
- **Cross-row consistency**: still an open question for this round. Each row's presenter footage is still an independent Wan 3.0 generation (image-to-video chaining is available again if needed, now that it only needs to carry outfit/scene continuity, not text content).
- **New risk**: tracking accuracy. If the marker tip isn't reliably detectable (motion blur, hand occlusion, lighting), the reveal will desync from the hand regardless of how clean the compositing math is. This is tested first, for free, before generating anything new.

## Test order (cheapest-first, reusing existing footage)

1. **Tracking prototype, $0**: run marker-tip detection against round 24's already-generated row 1 frames (`../round24-i2v-continuity/raw/row1_frames/`) to check whether simple color-threshold tracking gives a usable, stable trajectory. No new generation needed for this step.
2. **One real test clip**: if tracking is viable, generate one new Wan 3.0 clip with the "blank board, no mark left" prompt for row 1, and run the full tracking + reveal + composite pipeline on it. Audit frame-by-frame.
3. Only if that looks right, generate the remaining 7 rows and build the full stitched/captioned deliverable.

## Budget

Step 1 is free. Step 2 is ~1 generation (~$1-1.50). Step 3, if reached, is ~7 more generations (~$7-10).
