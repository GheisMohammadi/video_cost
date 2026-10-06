# First-party model pricing vs. fal

Checked 2026-10-07. Compares what each model's own maker charges for API access ("first-party") against what fal charges for the same model ("reseller"). Separate question from rounds 1-6, which compare self-hosting on a rented GPU against fal's price; this is first-party API access vs. fal, with no GPU rental involved on either side.

## Summary

Two different comparisons exist and give different answers:

- **Self-hosting on a rented GPU vs. fal's price**: self-hosting costs more than fal, at every resolution measured (rounds 1, 6: 1.33x at 480p, 2.1-2.2x at 720p, Wan 2.2).
- **First-party API price vs. fal's price for the same model**: mixed. Seedance and Wan 2.2 are cheaper first-party. LTX-2.3 is cheaper through fal than first-party. No single rule covers every model; each one is priced independently of the others.

## 1. Which models can be self-hosted at all

| Model | Open weights | Self-hostable | Access options |
|---|---|---|---|
| Wan 2.2 (A14B) | Yes, Apache 2.0, no revenue threshold | Yes (rounds 1-6) | Rent a GPU and run it, or buy API access from Alibaba or fal |
| LTX-2.3 | Yes, under a restricted license (free under $10M org revenue, commercial license required above) plus a gated text encoder dependency (Google's Gemma 3 12B IT, manual approval) | Not yet (round 7, blocked on the gated dependency) | Self-host once access exists, or buy API access from Lightricks or fal |
| Seedance 2.5 / 2.0 Mini | No; ByteDance has not released Seedance weights | No, at any price | API access only, from ByteDance's ModelArk console or fal |
| Veo 3.1 | No | No | API access only, from Google or a reseller |
| MiniMax H3 / Hailuo | No | No | API access only, from MiniMax or a reseller |

Wan 2.2 and LTX-2.3 are the only two with a self-hosting option. Section 2 covers API pricing for all five models.

## 2. First-party price vs. fal's price, model by model

| Model | First-party price | Fal's price (same tier) | Ratio | Confidence |
|---|---|---|---|---|
| Seedance 2.5 (no video input) | $10.70 / million tokens (ByteDance ModelArk) | $21.40 / million tokens | First-party 2.0x cheaper | High: both figures are each provider's own published rate card |
| Wan 2.2 T2V Plus @480p | $0.02/s (Alibaba) | $0.04/s | First-party 2.0x cheaper | Medium: two independent checks agree on the number, but both came from third-party aggregator pages, not a confirmed read of Alibaba's own console |
| Wan 2.2 Kf2v Flash @480p | $0.015/s (Alibaba) | No matching fal tier (Kf2v is a keyframe/image-conditioned variant, not plain text-to-video) | Not comparable | Low: different request type |
| LTX-2.3 Pro @1080p | $0.08/s (Lightricks, docs.ltx.io) | $0.06/s | Fal 1.33x cheaper | High: first-party figure from Lightricks' own docs |
| LTX-2.3 Fast @1080p | $0.06/s (Lightricks) | $0.04/s | Fal 1.5x cheaper | High |
| Seedance 2.0 Mini @720p | ~$0.029/s, promotional rate ending 2026-10-07 | Not checked at this tier | Excluded | Promotional pricing is excluded from profit figures by project rule |
| Veo 3.1 Lite @720p | $0.05/s (Google) | Not checked | No fal figure to compare | First-party only |
| MiniMax H3 @768p | $0.08/s (MiniMax) | Only a promotional fal figure is on file for this model | No non-promotional fal figure to compare | First-party only |

Direction of the price difference is model-specific: confirmed cheaper first-party for Seedance, tentatively cheaper for Wan 2.2, cheaper through fal for LTX-2.3 at both of its tiers.

## 3. Licensing and access friction

| Model | License / access | Effect |
|---|---|---|
| Wan 2.2 | Apache 2.0, no revenue threshold, no gating | No licensing blocker; this is why rounds 1-6 could run on a rented GPU directly |
| LTX-2.3 | LTX-2 license (free under $10M org revenue, commercial license required above) plus a gated text-encoder dependency (Gemma 3 12B IT, manual HF approval) | Two separate blockers. Round 7 is blocked on the gated dependency alone, independent of the revenue threshold |
| Seedance | No weights exist to license; access is contractual only | Reselling output at a markup, if permitted at all, is a terms-of-service question, not a licensing one. Not yet checked: whether ByteDance's API terms permit reselling output purchased through its API |
| Veo 3.1, MiniMax, Hailuo | Same as Seedance: API-only, resale governed by terms of service, not yet checked | Same open question applies |

## 4. Effect on the project's $1M profit formula

The formula (root `README.md`): $1,000,000 spent on capacity, output sold at fal's price, minus the $1,000,000. Applied to self-hosting Wan 2.2, the result is negative (rounds 1, 6). Applied to reselling Alibaba's first-party Wan 2.2 API access instead, using the figure in section 2 (medium confidence, unconfirmed on Alibaba's own console):

$1,000,000 at $0.02/s buys 50,000,000 seconds of output. Sold at fal's $0.04/s: $2,000,000 revenue, **$1,000,000 profit**.

This figure depends on three unconfirmed points:

1. The $0.02/s rate has not been confirmed on Alibaba's own console, only on third-party pages quoting it.
2. Whether Alibaba's terms permit reselling API output at a markup is unchecked.
3. The figure assumes $2,000,000 of buyer demand exists at fal's price -- the same 100%-utilization assumption the formula requires elsewhere, applied here to demand rather than GPU uptime.

## 5. Open items, in order

1. Confirm the Alibaba Wan 2.2 rate against Alibaba's own console, not a third-party page.
2. Find Alibaba's and ByteDance's terms of service and check whether reselling API output at a markup is permitted.
3. If both check out: a small real purchase of API access, to confirm price and output quality, before any larger commitment.

No GPU or pod is needed for any of these three items.
