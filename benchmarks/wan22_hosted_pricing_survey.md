# Wan 2.2 A14B across public hosted APIs: does fal's price reflect the market?

Checked 2026-09-23, against each provider's public model/pricing page. This looks at hosted inference APIs that serve the Wan 2.2 model itself (List6 item 2), separate from raw GPU rental comparisons (List6 item 1, not covered here). Every price below is quoted verbatim from its source; nothing is estimated unless marked so.

## Answer, short version

fal's standard-quality price ($0.04/$0.06/$0.08 per second at 480p/580p/720p) is close to the middle of the market for standard-quality Wan 2.2 A14B hosting, not a high outlier. The one direct per-second-billed competitor found, DeepInfra, is about 7% cheaper than fal at 720p. A separate, much cheaper price band exists across several providers for an accelerated/distilled variant of the same model (roughly $0.05-0.0625 at 480p and $0.10-0.125 at 720p, per 5-second video, versus fal's $0.10 turbo tier at 720p) -- but that is a different, faster pipeline, not the standard-quality setting our own benchmark and fal's standard tier use. Our own measured cost is well above all of these, standard or accelerated (see "Where our number sits," below).

## Standard-quality tier (comparable to fal's non-turbo pricing and to our own round 1/2 settings)

| Provider | Price | Resolution | Duration | Basis | Source |
|---|---:|---|---|---|---|
| fal.ai (our benchmark's reference) | $0.04 / $0.06 / $0.08 per second | 480p / 580p / 720p | billed per second, 16 fps | per-second | [fal model page](https://fal.ai/models/fal-ai/wan/v2.2-a14b/text-to-video) |
| DeepInfra | $0.0750 per second | 720p only (fixed) | 5 s fixed | per-second | [DeepInfra model page](https://deepinfra.com/Wan-AI/Wan2.2-T2V-A14B) |
| Together AI (image-to-video, not text-to-video -- not directly comparable) | $0.31 per video | not stated | not stated | flat | [Together AI model page](https://www.together.ai/models/wan-2-2-i2v) |
| Novita AI | not currently offered | -- | -- | -- | their pricing page lists Wan 2.5 and 2.6 T2V tiers but no Wan 2.2 entry as of this check ([Novita pricing](https://novita.ai/pricing)) |
| Replicate | not offered as a standalone standard T2V model | -- | -- | -- | their Wan 2.2 collection lists only the accelerated `wan-2.2-t2v-fast` for text-to-video; the standard-weights A14B they host is image-to-video only, at $0.40/video (480p) and $1.00/video (720p) ([Replicate blog](https://replicate.com/blog/wan-22)) |

DeepInfra is the only found provider billing standard-quality Wan 2.2 A14B text-to-video the same way fal does (per second, no acceleration), which makes it the cleanest direct comparison: **$0.075/s vs fal's $0.08/s at 720p, about 7% lower.** Neither offers a 480p standard tier we could confirm both ways (DeepInfra's model page states its deployment is fixed to 720p only), so the 480p figures we've been using in our own tests are only directly benchmarked against fal, not against a second provider yet.

## Accelerated/distilled tier (context, not a like-for-like match to our tests)

These providers offer a faster, cheaper, quality-reduced Wan 2.2 A14B pipeline, comparable in spirit to fal's separate "turbo" tier rather than to fal's standard tier or to our own round 1/2 settings (which used the full, non-accelerated 27-step configuration).

| Provider | Price (per video) | Resolution | Duration | Source |
|---|---:|---|---|---|
| fal.ai turbo | $0.10 | 720p | not stated | [fal turbo page](https://fal.ai/models/fal-ai/wan/v2.2-a14b/text-to-video/turbo) |
| Replicate (`wan-2.2-t2v-fast`, PrunaAI-optimized) | $0.05 / $0.10 | 480p / 720p | not stated | [Replicate blog](https://replicate.com/blog/wan-22) |
| Segmind (`wan-2.2-t2v-fast`) | $0.0625 / $0.125 | 480p / 720p | not stated | [Segmind pricing](https://www.segmind.com/models/wan-2.2-t2v-fast/pricing) |
| WaveSpeedAI (`t2v-480p-ultra-fast`) | $0.05 | 480p | 5 s (per-second billing, 5 s minimum) | [WaveSpeedAI model page](https://wavespeed.ai/models/wavespeed-ai/wan-2.2/t2v-480p-ultra-fast) |

Fal's turbo price and Replicate's fast-tier 720p price are identical ($0.10/video), and the rest cluster within about 25% of each other. That is a fairly tight, independently-arrived-at price band across unrelated providers for the accelerated variant, which suggests it reflects a real cost floor for that pipeline rather than any one vendor's markup or loss-leader pricing.

## Where our own number sits

Our round 1/2 measured cost, at fal's standard (non-turbo) settings, is:
- Busy-queue only: $0.0527-0.0531 per video-second at 480p (1.32-1.33x fal's $0.04)
- All-in, including setup and idle time: $0.0723-0.0753 per video-second (1.81-1.9x fal's $0.04)

Against the market data above: our all-in number is noticeably above every price found for the standard-quality tier (fal, DeepInfra), and far above the accelerated tier (which we have not attempted to replicate ourselves). This does not mean self-hosting is uncompetitive in general -- our number reflects one A100, one unoptimized configuration, and a single test session, none of which is what production hosting would look like. It does mean that at today's settings, none of the public API prices we could confirm make fal look expensive relative to its market; if anything, DeepInfra prices the same standard configuration slightly below fal.

## Confidence and gaps

- Verified from a live pricing page, with exact figures quoted: fal (standard and turbo), DeepInfra, Replicate (blog-stated pricing for its own hosted models), Segmind, WaveSpeedAI.
- Lower confidence: Together AI's $0.31/video is for image-to-video, not text-to-video, and its duration is not stated on the page -- not a fair comparison, included only for completeness.
- Not found: Novita no longer lists Wan 2.2 in its current pricing (2.5 and 2.6 appear instead) -- itself worth noting, since it suggests the "most mature and deployed open ecosystem" is also the fastest-moving, and Wan 2.2 specifically may already be aging out of some providers' catalogs in favor of newer Wan versions.
- Not checked: Fireworks AI (confirmed to not offer video generation at all), and several smaller aggregators (Muapi, GoEnhance, Sogni) that resell access to Wan 2.2 rather than hosting it directly -- their prices reflect a markup over an underlying provider, not a separate data point.
- None of these providers' exact generation settings (steps, guidance, scheduler) were independently confirmed the way fal's were (`benchmarks/fal_wan22_config.md`); prices are compared on resolution, duration, and billing basis only, which is the most that could be confirmed from public documentation without an account on each platform.

## What "List6 item 1" would still need

This covers hosted APIs only. Comparing our own pipeline's cost across other raw GPU rental providers (Lambda Labs, CoreWeave, Vast.ai) at fully repeatable settings is a separate question, covered by List6 item 1 (round 4): renting the same GPU class elsewhere and running the exact frozen job list.
