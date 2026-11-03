[← All rounds](../../../README.md)

# Round 27 plan: image-to-video chaining across all 8 rows, strict onset-sync

## Why

Round 26 (locked-down presenter description) was stopped before completion: still not accepted. Round 24 already tried image-to-video chaining once and it fixed cross-row visual continuity (outfit/board/room genuinely held constant, since every row after the first starts from the literal last frame of the previous row) but broke text fidelity on row 2 -- the model echoed/continued the existing board text ("I vibe-c...") instead of writing the new row's sentence.

This round repeats the I2V chaining approach (requested directly), with two changes aimed at round 24's specific failures:

1. **Text-echo fix**: the image-to-video prompt now explicitly forbids repeating, continuing, or reusing any part of the text already visible on the board from the anchor frame, and states the new row's exact sentence as the only thing to write.
2. **Onset-sync carried forward unchanged** from round 24's `ONSET_RULE` (no ink before tip contact) -- round 24 never got to verify whether this fixed onset-sync on its own, since the round was halted by the text-echo defect on row 2 before further rows were tried.

Presenter description: simplified back down to a single concise descriptor per direction given ("a pretty girl"), not round 26's long pinned-down paragraph -- continuity across rows is now handled structurally by I2V chaining (same literal frame carried forward), so the presenter description no longer needs to do that job through wording.

## Approach

Row 1: text-to-video, `alibaba/wan-3.0/text-to-video`, writes the first row's sentence, onset-sync rule applied.
Rows 2-8: image-to-video, `alibaba/wan-3.0/image-to-video`, `start_image_url` = base64 last frame of the previous row's clip, onset-sync rule applied, explicit no-echo instruction applied.

## Test order

1. Generate row 1, verify onset-sync (no ink before tip contact) and correct text.
2. Generate row 2 chained from row 1, verify (a) outfit/board continuity (expected, structural), (b) correct new text -- not a repeat of row 1's text, (c) onset-sync.
3. If row 2 passes all three checks, continue chaining rows 3-8 the same way.
4. If row 2 repeats round 24's text-echo defect despite the explicit no-echo instruction, stop and report before spending further -- the fix would need to be something other than prompt wording (e.g. cropping/erasing the previous row's text from the anchor frame before feeding it in as `start_image_url`, so there is nothing on the board for the model to echo).

## Budget

~$0.50-0.75/clip x up to 8 clips = ~$4-6, plus any retries.
