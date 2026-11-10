# Round 41: Vera / Deepen AI ad test ("$5 per person-hour")

Boss-supplied ad copy to test, in the same whiteboard-writing-plus-
annotation format used in rounds 35-39:

> Human-in-the-loop review for AI in production.
> Pay $5 per person-hour.
> https://services.deepen.ai

Reference kit supplied by boss: `Vera-Deepen-Character-Kit-v0.2/`, a
proposed AI-character ("Vera") built for Deepen AI marketing. Its
`START-HERE.md` sets hard gates before any paid production:

- The character/identity is **unapproved** -- the clean-face portrait
  (`assets/vera-portrait-v01.png`) is only a review candidate.
- Approval is required on: the specific film, which reference look to
  use, voice, and a whole-order cost cap, before paid generation.
- One audience + one CTA per film (see `AUDIENCE-ROUTES.json`).
- Real product/claim statements need client-cleared evidence; the kit's
  `CLAIMS-REGISTER.json` does not include "$5 per person-hour" or
  `services.deepen.ai` -- those come directly from boss's message, not
  from the kit's verified-claims list, so they're used here as supplied
  ad copy for a cost/quality test, not as an independently verified claim.
- Must not touch or reuse a separate, unrelated saved identity/voice
  called "Claire" -- nothing in this round does.

## Approvals obtained (per boss, this round)

- Cost cap: **under $5 total**.
- Look and audience: boss said to choose the best match for what this
  round is testing.

## Choices made

- **Look:** `assets/vera-portrait-v01.png` -- the kit's only
  identity-anchor candidate (the other two stills are explicitly scene
  studies, "do not promote into an identity master").
- **Audience route:** `buyer` (Data buyer / ML lead) from
  `AUDIENCE-ROUTES.json` -- closest fit to the ad copy's pitch ("human
  review for AI in production" is a service pitched at teams running AI
  in production, i.e. ML leads/data buyers, not calibration engineers or
  data suppliers). CTA URL is overridden to the one boss gave
  (`https://services.deepen.ai`) rather than the route's default
  `refinery` URL, since this round is testing boss's specific copy.

## Approach

Same structure as round 39's single-clip MiniMax attempt (best
cost/quality result so far): one clip, Vera writing the three lines on
a whiteboard/glass board, following her character book's wardrobe
("Bench" look: pale-blue stand-collar shirt, charcoal trousers, thin
graphite glasses) and camera-behavior notes (calm, points once, returns
attention to camera only at the end). Image-to-video anchored on
`vera-portrait-v01.png` so the identity in the clip matches the
reference candidate that's pending approval, on
`minimax/h3-max-turbo/text-to-video` or `/image-to-video` depending on
which variant accepts a reference image.

Lines to render, top to bottom:
1. "Human-in-the-loop review"
2. "for AI in production."
3. "Pay $5 per person-hour."
4. "https://services.deepen.ai"

Annotation: circle around "$5" (the price, the single most important
number), underline under the URL -- mirrors round 39's successful
rectangle/circle/underline pattern.

## What to check

Same acceptance checks as round 39: all 4 lines text-accurate
(including the URL, which is long and easy for models to garble/drop
characters from), no reflection/ghost, no stray marks, circle tight
around "$5", underline matching only the URL's width, no overshoot,
progressive writing (no pop-in), look-at-camera only at the end, and
that Vera's described identity markers (dark bob, graphite glasses,
petrol/pale-blue wardrobe) come through recognizably from the anchor
image.

## Budget

MiniMax at $0.028/s promo rate, 15s clip = ~$0.42 for one attempt,
leaving headroom under the $5 cap for 1-2 retries if the first attempt
garbles the URL or price (the hardest part of this script).

## Not authorized by this round

No voice, no identity lock, no publication. This is an internal
cost/quality test only, per the kit's own gating language and consistent
with this project's standing practice of testing before committing.
