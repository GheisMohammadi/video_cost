# Round 29: fix line-wrap overflow via smaller/compact handwriting

Round 28 fixed outfit consistency (whiteboard-wipe handoff) and verified clean
sync on rows 1-7, but each of rows 5, 6, 7 wrapped across two board lines
instead of one (6 board lines used for 3 sentences), which is what caused
row 8 to run out of vertical space and overwrite earlier text.

## Fix

Add an explicit `SIZE_RULE` to every prompt: the handwriting must be small
and compact enough that each full sentence fits on a single board line,
leaving room for all remaining rows below it. Keep everything else from
round 28 unchanged: I2V chaining, `ONSET_RULE`, `NO_ECHO_RULE`, the
whiteboard-wipe handoff at the segment midpoint (row 5).

## Test order

1. Row 1 (text-to-video) -- confirm single-line-per-sentence handwriting
   before spending budget on the full chain.
2. Rows 2-4 (I2V chained), same as round 27/28.
3. Row 5: wipe handoff from round 27's row 4 last frame (reuse, not
   regenerated), same as round 28.
4. Rows 6-8 (I2V chained from row 5).

If row 1 still wraps, stop and try a different fix (e.g. explicitly stating
board-line count/spacing) before spending budget on the rest of the chain.

## Budget

~8 rows x ~$0.6-0.8 = ~$5-6, same order of magnitude as rounds 27/28.
