[← All rounds](../../../README.md)

# Round 7 test design: Wan 2.2's cheaper/faster rival, LTX-2.3

Status: scripts not yet written; model and fal pricing researched (section 1-2) and spot-checked against the live Hugging Face repo (not just blog summaries); nothing run yet. Self-hosted Wan 2.2 already costs more than fal's own Wan 2.2 price at both 480p and 720p (rounds 1, 6), so more A100 capacity running Wan 2.2 does not by itself produce a profit under the project's cost-vs-fal framing (root `README.md`). LTX-2.3 is evaluated here as a concrete alternative; it is the model TaoMate runs. Frozen before running.

## 1. Question

Is LTX-2.3 cheaper to self-host, per video-second, than Wan 2.2 was -- and specifically, cheaper relative to *its own* fal price than Wan 2.2 was relative to fal's Wan 2.2 price (1.33x at 480p, 2.1-2.2x at 720p)? If LTX-2.3 self-hosted comes in under fal's LTX-2.3 price, that is the first model in this project where the cost-vs-fal profit formula (root `README.md`) comes out positive.

## 2. What LTX-2.3 is, and how it differs from everything tested so far

- **Architecture**: 22B total, an asymmetric dual-stream diffusion transformer -- a 14B video stream (3D RoPE) and a 5B audio stream (1D RoPE) joined by cross-modal attention -- plus a required **Gemma 3 12B IT** text encoder (a separate, **gated** Hugging Face repo, manual approval). Confirmed live: `Lightricks/LTX-2.3` is the real, official repo (org `Lightricks`, tagged `diffusers`), but it ships as flat named checkpoint files (`ltx-2.3-22b-dev.safetensors`, `-distilled.safetensors`, `-distilled-lora-*`, plus spatial/temporal upscalers), not a standard pipeline folder. Real inference goes through a dedicated `LTX2Pipeline` diffusers class (from the `Lightricks/LTX-2` line) or the `ltx_pipelines` package in the `Lightricks/LTX-2` GitHub repo (`uv sync`, Python >=3.12, CUDA >12.7, PyTorch ~2.7) -- not a generic one-line `from_pretrained`.
- **It generates audio by default.** This is not an optional post-process like Wan's interpolation gap (round 5) -- the audio stream is part of the architecture fal bills for. Matching fal's default means our run must also produce audio, which is new compute this project hasn't measured before.
- **License**: LTX-2 license, free for organizations under $10,000,000 annual revenue; a commercial license is required above that threshold (confirmed by reading the actual `LICENSE` file in the repo, not a blog summary). This is a business fact to confirm against Harmony/ONE's actual revenue before acting on any result here commercially; irrelevant to this round's cost measurement itself.
- **Resolution tiers differ from Wan.** Fal's LTX-2.3 pricing has no 480p/720p tier at all; the floor is 1080p. Two fal variants: `fast` ($0.04/$0.08/$0.16 per video-second at 1080p/1440p/2160p) and `pro` ($0.06/$0.12/$0.24). This round matches **Pro at 1080p ($0.06/video-second)**, following this project's established convention of matching fal's standard/non-turbo endpoint rather than its cheaper fast tier (rounds 1-6 did this for Wan 2.2's turbo endpoint too).
- **Duration options**: fal lists 6/8/10 s (default reported as 6 s, not independently confirmed against the live API schema the way the file layout above was). This round uses **6 s** to match fal's default, unlike round 1-6's 5.06 s (Wan's 81-frame default) -- durations are not comparable 1:1 across models, only each model's self-hosted cost against its own fal price is.
- **VRAM**: official minimum is 32 GB+ for full bf16; our A100-80GB should fit it without the CPU-offload scheme Wan 2.2 needed (two 14B experts), but this is unconfirmed until a real load is attempted -- plan accordingly (section 3).

## 3. Safeguards (several new, since nothing about this pipeline has been run before)

- **Gemma 3 12B IT access must be requested and approved before any pod time starts.** Gated HF approvals can take hours; burning paid GPU time waiting on it would be a pure loss. This is a prerequisite, not a pod-time task.
- **Pipeline-loading pilot before any full run.** The first thing to measure, on a cheap/short pod slice, is simply: does `LTX2Pipeline` (or the `ltx_pipelines` package) load `Lightricks/LTX-2.3` plus the gated text encoder, and does a single short generation complete and decode to a valid file. This project's blog research for this model has already shown conflicting claims (diffusers "coming soon" vs working code samples) -- that conflict gets resolved by trying it, not by trusting either source further.
- **VRAM/offload check as part of preflight**, same as every round: if 32 GB+ does not fit cleanly on the shared A100, decide on offload before, not during, a paid job.
- **Independent stop guard** (`pod_guard.sh`), same as every round -- but with a wider error margin than usual on the hard deadline, since per-clip generation time for this model is completely unmeasured; size it only after the pilot clip's real timing is known, the same correction made mid-round-3 and again in round 6.
- **Staged spend, not a single committed job list.** Given the combination of a new codebase, a gated dependency, and an unverified VRAM/offload path, this round spends in two steps: (1) a small pilot slice to get one verified clip and a real per-clip time, (2) only then decide, from real numbers, how much of the remaining budget buys more prompts at Pro/1080p versus also sampling the Fast tier for a cost/quality contrast -- rather than freezing a full job list now against unknowns the way rounds 1-6 could, because those reused an already-proven pipeline.

## 4. Budget

**$8.00 total.** Unlike every prior round, this is not sized against a pre-measured pilot (there is no round-0-style LTX pilot yet) -- it is sized to absorb the real risk that step one (just getting a valid clip out of a brand-new codebase) costs more in debugging time than the generation itself. Rough allocation, to be corrected after the pilot clip's real timing is known:

| Item | Estimate |
|---|---|
| Setup, repo clone, dependency install, weight download (22B + 12B text encoder, larger than Wan's 27B across two checkpoints) | ~20-30 min, genuinely uncertain |
| Pilot: one clip, Pro tier, 1080p, 6 s, with audio | unmeasured -- this round's own job to establish |
| Remaining budget | spent per section 3's staged-spend rule, after the pilot |

## 5. Hardware

RunPod A100-SXM4-80GB, same as every prior round. Hardware stays constant on this model's first measurement rather than also varying GPU tier, so any cost difference found is attributable to the model, not a confounded hardware change.

## 6. Limitations (known before running)

1. Not comparable 1:1 with Wan 2.2's clips: different resolution floor (1080p vs 480p/720p), different duration (6 s vs 5.06 s), and audio is generated here and wasn't there. Only each model's ratio to its own fal price is comparable across rounds.
2. One pilot, then a small number of pro-tier clips -- not the four-prompt-strata rigor rounds 1 and 6 used, because budget here is split between genuine pipeline risk and measurement.
3. No blind quality review planned for this round; it answers a cost question first.
4. Fal's exact default config (duration, fps, step count if any is exposed, audio sample rate) is pieced together from search results and will be corrected against whatever this project's own pod-side pilot run and/or a direct fal schema check show once reached.
5. The $10M-revenue license threshold's relevance to Harmony/ONE is a business fact outside this round's scope, not resolved here.
