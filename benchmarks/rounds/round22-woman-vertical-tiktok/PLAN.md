[← All rounds](../../../README.md)

# Round 22 plan: new script, visible woman presenter, portrait 9:16, 30s via stitched segments

## Why

Boss directive (verbatim): new script, whiteboard writing must appear progressively (not pre-written), presenter changes to a white, attractive, fashionable woman, add a post-generation caption overlay in mid-screen, and the output must always be 9:16, 720p, 30 seconds (15s if 30s is not achievable).

This is a different set of constraints than rounds 18-21, which used 16:9 close-up framing on just a hand/board (no presenter visible) to get genuine marker-to-letter sync. Showing the presenter requires going back to a wider shot, which has not been tested with the round 20/21 sync-fix prompt pattern. 30s also exceeds Wan 3.0's per-generation cap (confirmed at 15 in round 17/18), so it requires stitching two clips.

## New script

Boss's text split into two halves for two 15s segments:

- Segment A: "I vibe-coded my app in a weekend." / "Launched; 19 signed up."
- Segment B: "So this week I pay $99 on x.country" / "to grow my business on TikTok."

## Decisions (confirmed)

1. **Framing**: wide shot, woman fully visible writing on the board. Re-test marker sync from scratch at this framing using the round 20/21 prompt style (mechanically explicit tip/ink phrasing + explicit no-overlap sequencing). Sync quality is not guaranteed to match the close-up result -- this round measures that.
2. **Duration**: two independent 15s generations (same seed, same character description for best-effort continuity), concatenated with ffmpeg to approximate 30s. Known risk: the woman's appearance/board state may not match exactly across the cut since these are independent generations, not an image-to-video continuation.
3. **Aspect ratio**: test whether `alibaba/wan-3.0/text-to-video` accepts `"aspect_ratio": "9:16"` -- unverified, all prior rounds used 16:9. If rejected, fall back to 16:9 and crop/pad to 9:16 in post.
4. **Resolution**: 720p (cheaper than the 1080p used in rounds 18-21, and boss specified 720p explicitly).
5. **Caption overlay**: separate post-generation ffmpeg pass (drawtext or burned subtitles) placing the spoken-line text in the mid-screen area, distinct from the whiteboard-writing text itself. No generation cost.

## Test order (cheapest-first)

1. Generate Segment A alone first (1 clip) to verify: aspect ratio accepted, woman visible and matches "attractive, fashionable" description reasonably, marker sync holds at wide framing. Do not generate Segment B until A is verified.
2. If A looks right, generate Segment B with the same seed/character description.
3. Stitch A+B with ffmpeg, confirm total duration ~30s, 720p, 9:16.
4. Add caption overlay pass on the stitched result.

## Verification

Same tight-frame-spacing method as rounds 19-21 (every 4-10 frames around any writing transition) to check whether the marker genuinely leads the ink at this wider framing, not just text-content accuracy.

## Budget

Remaining fal.ai balance from round 16's $25 top-up, minus ~$3-4 spent in rounds 17-21. Estimate: 720p is cheaper per second than the 1080p used before; budget ~$3-5 for this round's tests (1-2 generations + possible retries).
