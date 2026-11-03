[← All rounds](../../../README.md)

# Round 24 plan: image-to-video chaining for continuity, tighter onset-sync audit

## Why

Two problems were reported against round 23's result, both confirmed against the actual clips before writing this plan:

1. **Premature ink before she starts writing.** Checking row 1's raw clip (the row believed clean) at 5-frame spacing from frame 0, a short disconnected ink mark appears on the board around frame 40 (1.33s) -- before her hand is in a writing position, and not connected to the marker tip's current location. Round 23's verification jumped from frame 0 to frame 60 in most rows and missed this onset window entirely. The per-row split fixed cross-row overlap, but a finer version of the same "tip doesn't actually lead the ink" problem is still present at the start of individual rows.
2. **Clothing, board and room are inconsistent across rows.** Confirmed and already flagged as an open, unresolved limitation since round 22: each row/segment is an independent text-to-video generation sharing only a seed, which does not preserve visual state. This has been accepted as a known tradeoff through rounds 22-23; it now needs an actual fix rather than continuing to be noted and deferred.

Both point at the same root cause: every row so far has been generated as an independent text-to-video call with no anchor to a real starting state, giving the model room to both improvise a spurious early mark and reinvent her outfit/board/room from scratch each time.

## Proposed approach

**Image-to-video (I2V) chaining.** Confirmed available: `alibaba/wan-3.0/image-to-video` on fal.ai, taking `start_image_url` (accepts a base64 data URI directly, no image hosting needed) plus the same `prompt`/`resolution`/`aspect_ratio`/`duration`/`seed` controls as the text-to-video endpoint used so far.

1. Row 1 generated as before (text-to-video), but with a stricter onset instruction (see below) to address defect 1 at the source.
2. Row 1's actual final frame extracted and used as `start_image_url` for row 2's generation -- an image-to-video call, not an independent text-to-video call. The prompt describes her continuing to write the next row, starting from that exact pixel state (same outfit, same board, same room, marker already in hand), rather than re-describing the scene from scratch.
3. Row 3 chains from row 2's final frame, and so on through row 8 -- each row is a continuation of the previous frame, not a fresh generation.
4. Onset-sync instruction strengthened for every row: explicitly state the starting frame already shows a confirmed blank (or already-written, for continuation rows) board with no stray marks, and that the very first new ink only appears once the tip is already touching the board in the image -- not before.

## What this is expected to fix, and what it doesn't guarantee

- **Continuity (defect 2)**: expected to fix directly -- starting each generation from the literal previous frame means the outfit/board/room physically cannot reinvent themselves between rows, unlike independent text-to-video calls.
- **Onset sync (defect 1)**: expected to help (a confirmed-blank starting image is a stronger anchor than a text description of "completely blank"), but this is a prompt-adherence problem the model has shown repeatedly (rounds 19-23) that it doesn't reliably obey from wording alone. This round tests it, but doesn't assume success -- every row will be frame-audited from frame 0, not from frame 60 as round 23's checks mostly were.

## Test order (cheapest-first)

1. Generate row 1 (text-to-video, strengthened onset prompt). Audit from frame 0.
2. Generate row 2 as an image-to-video continuation of row 1's last frame. Audit (a) visual continuity against row 1's final frame, (b) onset sync from frame 0.
3. Only if both check out, continue chaining rows 3-8. If continuity or onset sync still fails at row 2, stop and report before spending on the rest of the chain.

## Budget

~$1-1.50 per 5s/720p generation observed in round 23. Testing rows 1-2 first: ~$2-3. Full 8-row chain if the test succeeds: ~$8-12 additional.

## Verification

Every row audited from frame 0 (not starting at frame 60 as round 23 mostly did) specifically for any ink appearing before the tip is in contact. Continuity checked by direct visual comparison between each row's start frame and the previous row's end frame (should be identical or near-identical, not just "similar woman, similar room").
