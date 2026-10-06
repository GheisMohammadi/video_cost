# First-party model pricing vs. fal: when going direct actually helps

Checked 2026-10-07. This compares what each video model's own maker charges for API access ("first-party") against what fal charges for the same model ("reseller"). It is a different question from rounds 1-6, which compared *self-hosting on a rented GPU* against fal -- this document is about *buying API access* instead, either straight from the maker or through fal.

## The one-paragraph answer

There are two different kinds of "cheaper," and they should not be mixed up:

1. **Self-hosting an open-weights model on a rented GPU, vs. fal's price.** Rounds 1 and 6 measured this directly: our own cost is *higher* than fal's price, for every model and resolution tried so far (1.33x at 480p, 2.1-2.2x at 720p, Wan 2.2). Renting more GPUs does not fix this on its own.
2. **Buying API access straight from the model's maker, vs. buying the same access through fal.** This is a completely different comparison -- no GPU rental involved, just two prices for the same underlying compute. Here the answer is genuinely mixed: for some models going direct is much cheaper than fal; for at least one, fal is cheaper than going direct. Section 2 below has the numbers.

Only the second kind of comparison is new in this document.

## 1. Which models even allow which kind of "cheaper"

Not every model can be self-hosted. This changes what "going direct" even means for each one.

| Model | Open weights? | Can we self-host it? | What "direct" means for this model |
|---|---|---|---|
| Wan 2.2 (A14B) | Yes, Apache 2.0, no revenue threshold | Yes -- this is what rounds 1-6 ran ourselves | Either rent a GPU and run it (rounds 1-6), or buy API access straight from Alibaba instead of through fal |
| LTX-2.3 | Yes, but under a restricted license (free under $10M org revenue; commercial license required above that) and needs a separately gated text encoder (Google's Gemma 3 12B IT, manual approval) | Not yet -- this is what blocked round 7 | Either self-host (once gated access exists), or buy API access straight from Lightricks instead of through fal |
| Seedance 2.5 / 2.0 Mini | No -- ByteDance has never released Seedance weights | No, not an option at any price | The *only* lever is which door you buy API access through: ByteDance's own ModelArk console, or fal |
| Veo 3.1 | No | No | Same as Seedance -- API only, via Google or a reseller |
| MiniMax H3 / Hailuo | No | No | Same as Seedance -- API only, via MiniMax or a reseller |

Wan 2.2 and LTX-2.3 are the only two models here where self-hosting is even on the table, and for both, our own measurements (or round 7's blocked attempt) are the relevant comparison -- not this document. Everything in section 2 below is about buying API access, for every model listed.

## 2. First-party price vs. fal's price, model by model

Confidence matters a lot here, so each row says where the number came from and how sure we are.

| Model | First-party price | fal's price (same tier) | Direct vs. fal | Confidence |
|---|---|---|---|---|
| Seedance 2.5 (no video input) | $10.70 / million tokens (ByteDance ModelArk) | $21.40 / million tokens | **Direct is 2.0x cheaper** | High -- both are the providers' own published rate cards |
| Wan 2.2 T2V Plus @480p | $0.02/s (Alibaba, per two independent checks) | $0.04/s | **Direct would be 2.0x cheaper** | Medium -- two separate checks agree on the number, but neither came from actually opening an Alibaba console; third-party aggregator pages quoted it both times |
| Wan 2.2 Kf2v Flash @480p | $0.015/s (Alibaba) | no matching fal tier (Kf2v is a keyframe/image-conditioned variant, not fal's plain text-to-video) | not a fair comparison | Low -- different feature, not the same request type |
| LTX-2.3 Pro @1080p | $0.08/s (Lightricks' own docs.ltx.io) | $0.06/s | **Direct is 1.33x *more* expensive -- fal is cheaper** | High -- first-party source found directly |
| LTX-2.3 Fast @1080p | $0.06/s (Lightricks) | $0.04/s | **Direct is 1.5x *more* expensive -- fal is cheaper** | High |
| Seedance 2.0 Mini @720p | ~$0.029/s, promo, ends 2026-10-07 | not separately checked at this tier | not usable for a profit estimate | Excluded -- this is a time-limited promotional price, and the team's own rule is to ignore promotional pricing when sizing a profit number |
| Veo 3.1 Lite @720p | $0.05/s (Google) | not checked | -- | First-party only; no fal comparison done yet |
| MiniMax H3 @768p | $0.08/s (MiniMax) | not checked at a non-promotional rate | -- | The only fal number on file for this model is itself a promotional rate, so no fair comparison exists yet |

**The pattern that matters:** going direct is not automatically cheaper. Seedance and (tentatively) Wan 2.2 say yes. LTX-2.3 says no -- fal is cheaper than Lightricks' own listed price, for both of its tiers. A reseller can end up cheaper than the maker itself, for example by getting volume pricing the maker's retail page doesn't offer, or by pricing a tier as a loss-leader to attract users. There's no shortcut here; each model has to be checked on its own.

## 3. Licensing and access, side by side

| Model | License / access friction | What this means in practice |
|---|---|---|
| Wan 2.2 | Apache 2.0, no revenue threshold, no gating | The least friction of anything here -- this is why rounds 1-6 could rent a GPU and run it the same day |
| LTX-2.3 | LTX-2 license: free under $10M org revenue, commercial license required above it. Separately, its required text encoder (Gemma 3 12B IT) is gated on Hugging Face and needs manual approval | Two separate blockers, not one -- even if the revenue threshold is a non-issue, the gated text encoder alone stopped round 7 cold |
| Seedance | No weights exist to license -- access is purely contractual, through whichever API door is used | Reselling at a markup, if it's even allowed, is a terms-of-service question, not a licensing one. **Not yet checked**: whether ByteDance's API terms permit buying their API and reselling the output at a markup. This is the single biggest open question before anyone acts on section 2's Seedance number |
| Veo 3.1, MiniMax, Hailuo | Same situation as Seedance -- API-only, terms-of-service governs resale, not checked yet | Same caveat applies |

## 4. What this means for the team's $1M profit question

The boss's framing (see root `README.md`'s rounds table and the team channel) is: spend $1M, sell the output at fal's price, what's left over. Applied to *self-hosting* Wan 2.2, that number is negative (rounds 1 and 6 already showed this). Applied to *reselling Alibaba's own Wan 2.2 API access* instead -- using the one number in section 2 with the best (though still unconfirmed) support -- it looks very different:

$1,000,000 spent at $0.02/s direct buys 50,000,000 seconds of output. Sold at fal's $0.04/s, that's $2,000,000 in revenue. **Profit: $1,000,000** -- the first positive number this project has produced, under the same formula that made self-hosting look like a loss.

This number should not be treated as a decision yet. Three things stand between it and being real:

1. The $0.02/s figure has never been confirmed on Alibaba's own console -- only on third-party pages that claim to quote it.
2. Whether Alibaba's terms allow buying API access and reselling the output at a markup is unknown and unchecked.
3. The formula assumes $2,000,000 worth of buyers actually exist at fal's price -- the same "100% utilization" assumption the boss's own framing already requires, now applied to demand instead of GPU uptime.

## 5. What would need checking next, in order

1. Confirm the Alibaba Wan 2.2 rate directly -- open a DashScope/Alibaba Cloud console and read the real number, not another aggregator page.
2. Find Alibaba's and ByteDance's terms of service and check whether reselling API output at a markup is permitted.
3. If both check out, size a small real test: buy a small amount of API access directly, confirm the price and the output quality, before committing anything close to $1,000,000.

None of this needs a GPU or a pod -- it's account access and reading terms of service, which is why it's listed separately from every other round in `rounds/`.
