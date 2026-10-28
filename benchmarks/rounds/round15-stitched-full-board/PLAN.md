[← All rounds](../../../README.md)

# Round 15 plan: turn round 14's isolated wins into one deliverable board

Status: planned, not yet run.

## Why this round

Round 14 confirmed the cause of round 13 v3's partial failure: quote *count* in a single generation, not sentence difficulty. Isolated, lines 3-5 (A2) render correctly; packed together with lines 1-2 (A3, five quotes), they degrade. The practical pattern round 14 landed on: **two short-quote Hunyuan generations, combined, beat one packed prompt.** This round turns that into an actual demo of the full script on one board, and checks whether a smarter combination (continuity via image-to-video, not just an edit) can do better than a plain two-shot cut.

Checked before writing this plan, not carried over from round 14's unconfirmed guesses:
- A1's last frame and A2's first frame were compared directly (`round14.../raw/A1_frame120.png` vs `A2_frame001.png`): different camera angle, different pose, different shirt button pattern. These are two unrelated generations, not two halves of one continuous take. A naive concatenation is a hard cut, not a seamless shot -- real, but worth being upfront about in the final report rather than overstating it as "one continuous board."
- GlyphPrinter (deferred from round 13) was checked this session: code and weights are released (`github.com/FudanCVL/GlyphPrinter`), but it is image-only (built on FLUX.1-dev), no video support, no stated license. It would need its own separate image-to-video step afterward, the same two-stage pipeline round 10 already did by hand and round 12 tried with Qwen-Image-Edit -- and Hunyuan's direct text-to-video approach (rounds 13-14) is already producing exact sentences without that extra complexity. Deprioritized further; not planned for this round.

## What will be tested

### Test 1: two-shot edit (free, local, no pod -- do this first)

Trim and concatenate round 14's A1 and A2 clips (the two generations with correct text) into one edited sequence, as a real video editor would cut between two shots. No new generation, no pod cost. This demonstrates the practical "two generations, combined in post" production pattern end to end, honestly presented as a two-shot edit (a jump cut), not a single continuous take.

### Test 2: I2V continuity chain (pod required -- the main new test this round)

The more interesting, untested idea: instead of an edit-level cut, chain the two generations with Hunyuan's own image-to-video mode, the way round 10 section 7 tested for Wan. Use A1's final frame (lines 1-2 already correct on the board) as the starting image for a second generation, continuing with lines 3-5's content as new quoted text.

This tests two things at once:
1. **Does Hunyuan's I2V mode preserve already-correct text**, the way round 10 found Wan's I2V mode does? If yes, lines 1-2 should stay legible and correct through the second generation.
2. **Does continuing from a real (not packed-prompt) starting point let the new quoted lines render as well as A2's isolated result**, rather than degrading the way A3's packed five-quote attempt did? This is the real test of whether continuity-based generation can produce one actual continuous-feeling shot with the full correct script, closing the gap A3 left open.

If this works, it would be a genuinely new result: not just "isolate quotes, edit together" (Test 1, already known to work) but "chain quoted generations via I2V, closer to one real continuous shot."

## What would make this a win

- Test 2 produces a single clip where both the early (preserved) and newly-generated text are correct, with a visually continuous-enough transition (same person, same framing) that it reads as one shot rather than an obvious cut -- the first time this project has produced something close to a deliverable, correct, single-take board.

## What would not be a win (expected failure modes to watch for)

- I2V continuation might preserve the early text (as round 10 found for Wan) but still degrade the newly-added lines, the same as A3 -- in which case Test 1's honest two-shot edit remains the better practical recommendation.
- The continuation might also fail to preserve camera/person continuity as well as hoped, given I2V models can still drift over long continuations (round 10 saw "minor softening by later frames" even for preserved text).

## Resources needed

- A RunPod A100 pod for Test 2 (I2V generation) -- same scale as rounds 13-14's T2V tests.
- No pod needed for Test 1 -- local video editing only, can run immediately.
- Budget: default under $10 unless told otherwise, consistent with prior rounds.

## Steps

1. Run Test 1 now, locally, no pod -- produces an immediate, free deliverable demonstrating the two-shot pattern.
2. Get a pod for Test 2.
3. Extract A1's final frame as the I2V starting image; write the continuation prompt with lines 3-5 as quoted text, matching A2's isolated phrasing as closely as possible.
4. Run the I2V continuation, direct frame-by-frame inspection against the script (same method as every prior round).
5. Compare Test 2's result against Test 1's edit and against round 14's A1/A2/A3 on: text correctness, visual continuity, and whether this is actually better than "two generations, edited together" or just a more expensive way to get the same thing.
6. Write the round 15 report with an honest verdict on which approach (edit vs. I2V chain vs. rounds 10-11's overlay) is the actual production recommendation.

## Files (once run)

- `clips/`: Test 1's edited two-shot clip, Test 2's I2V continuation clip.
- `raw/`: generation records, inspection frames, the I2V starting image.
- `README.md`: the full report, written after results are in -- not before.
