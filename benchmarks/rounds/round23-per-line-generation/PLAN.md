[← All rounds](../../../README.md)

# Round 23 plan: generate each row separately, control pacing in post

## Why

Round 22 tried to get a 4-row paragraph (2 rows per segment, 2 segments) to write itself correctly within single 15s Wan 3.0 generations. Across three prompt variants it never fully succeeded, and a closer audit (every-frame spacing, all transitions, both segments -- not just the one transition flagged earlier) found the problem is broader than first reported:

- Segment A: row1-to-row2 transition is clean. Row2-to-row3 overlaps (row3's first letters appear before row2's last word is written).
- Segment B: row1-to-row2 does **not** overlap in time, but row2 ("$99 on x.country") does not animate at all -- it fades in as a translucent whole-row ghost over ~1s (frames ~155-180) and then solidifies, rather than being traced letter by letter. This is a different, arguably worse defect than overlap: it's round 19's original "fake writing" failure mode reappearing in just one row of one generation.

Two things follow from this:

1. **The problem isn't one fixable transition** -- it's that a single generation asked to write 4 rows in sequence produces inconsistent per-row behavior: sometimes clean, sometimes overlapping, sometimes not animated at all. Three different prompt-wording attempts in round 22 each changed *which* failure mode showed up, not whether one did.
2. **The "~1 second gap" reported as the fix in round 22 was never a real, controllable value.** It was one artifact of one specific generation. There's no prompt parameter that reliably sets inter-row pacing, so asking for "dynamic, natural, varies per line" timing via prompt wording is very unlikely to work any better than asking for a fixed value did -- the model isn't taking direction on pacing at all, it's just producing whatever it produces.

Round 20 and round 21 are the only prior results in this project with **fully verified, clean, letter-level sync** -- and both only ever asked a single generation to write *one* line. That's the one configuration that has actually worked reliably across this project's history.

## Proposed approach for round 23

Stop asking one generation to sequence multiple rows. Generate each board row (or each short script line) as its own separate, short Wan 3.0 clip -- one line of text per generation, framing matched to round 22 (wide shot, visible presenter, 9:16, 720p), same eyes-on-board fix from round 22 carried forward. Then:

1. Stitch the per-row clips together in post (ffmpeg), where we have full, deterministic control over the cut points.
2. Add the pause *between* rows ourselves in post, instead of hoping the model produces one -- e.g. hold the last frame of each clip (or a short static board shot) for a variable amount of time per transition (we can make this genuinely non-uniform: 0.3-0.4s for a short row, 0.6-0.8s for a longer one, or just hand-tune per cut) rather than depending on emergent, uncontrollable model timing.
3. This also gives a natural place to handle the continuity question flagged as still-open in round 22 (outfit/board/background shifting at the segment cut) -- more, shorter cuts make outfit continuity harder to fully solve with independent generations regardless, so this round treats it as the same accepted tradeoff as round 22 unless told otherwise, and focuses on the sync fix specifically.

## Tradeoffs being accepted

- More generations (4 short clips instead of 2 longer ones) -- more cost, and each one has its own continuity risk (same open issue as round 22, not newly introduced).
- More visible cuts in the final video (one per row instead of one per segment). Whether that reads as acceptable "quick cut" editing or as choppy depends on how tight the per-row clips are and how the post-production pause is handled -- this is itself something to evaluate once a test clip exists, not assumed to be fine.
- This approach is a bigger pivot than another prompt-wording tweak, so it is being proposed for confirmation before spending, rather than run automatically.

## Budget

Each 15s/720p generation in round 22 cost ~$1.50. Round 23's per-row clips can likely be shorter than 15s (a single short row doesn't need 15s), which may reduce per-clip cost, but needs a test to confirm Wan 3.0's minimum duration and pricing at shorter lengths. Estimate: 4 rows x 2 segments worth of script = 4 short test clips to start (~$3-6 depending on duration), more if duration/pricing differs from 15s rate.

## Verification

Same tight-frame-spacing method used throughout rounds 19-22: inspect every few frames across each clip, not just 3 spaced-out samples, specifically checking (a) the row writes progressively rather than fading in as a block, and (b) no text exists before the tip reaches it. Apply this check to every row this time, not just the one that was flagged as a problem last round -- round 22's narrower bug reports came from checking too few frames in too few places.
