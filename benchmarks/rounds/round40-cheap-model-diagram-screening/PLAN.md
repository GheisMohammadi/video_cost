# Round 40: screen genuinely cheap video-gen models against the round-33 diagram task

User directive: Seedance (and the other tools tested so far -- Kling, Veo)
are expensive; find and test cheaper models.

## Models found

Researched fal.ai's pricing page for the cheapest text-to-video models
that could plausibly handle this kind of structured, position-anchored
content (not just generic b-roll):

| Model | Endpoint | Price (per second) | Notes |
|---|---|---|---|
| PixVerse V6 | `fal-ai/pixverse/v6/text-to-video` | $0.045/s at 720p (no audio) | ~5x cheaper than Seedance Fast ($0.24/s) |
| MiniMax H3 Max Turbo | `minimax/h3-max-turbo/text-to-video` | $0.028/s at 768p (current Nov 2026 promo rate) | ~8.6x cheaper than Seedance Fast |
| ~~Grok Imagine Video 1.5~~ | `xai/grok-imagine-video/v1.5/image-to-video` | $0.14/s at 720p | Dropped -- image-to-video only (no text-to-video variant found), and actually pricier than Seedance Mini, so it doesn't serve the "cheap" goal here |

(Seedance 2.0 Mini, already tested in rounds 37-38, sits at $0.1547/s at
720p for reference -- both models here are cheaper than even that.)

## Test

Reused round 33's validated 5-box/hub-point diagram prompt unchanged (the
same explicit, position-anchored layout that Kling and Seedance both
nailed, and Veo failed) as a clean, known-good baseline -- lets this round
answer "can these cheap models handle basic position/connection
instructions at all" without re-deriving a new prompt or re-diagnosing
prompt-wording issues.

One attempt per model, 5s/720p (PixVerse) or 768p (MiniMax, since that's
its stated default tier), 16:9.

## What to check

Same checks as round 33: correct 5-box layout (A top-center, B mid-left,
C mid-right, D bottom-left, E bottom-right), all 4 lines meeting cleanly
at the hub point, legible single-letter labels, progressive line growth
under the tip (no pop-in), fixed camera.

## Budget

PixVerse: ~$0.225 (5s x $0.045/s). MiniMax: ~$0.14 (5s x $0.028/s). Total
~$0.37 for one attempt per model -- intentionally minimal, this is a
feasibility screen, not a production run. Confirm with the user before any
retries or follow-on testing.
