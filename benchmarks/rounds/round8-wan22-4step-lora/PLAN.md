[← All rounds](../../../README.md)

# Round 8 test design: a 4-step distillation LoRA on Wan 2.2

Status: run complete for the cost question this round asked. Results, what happened across two pods, and limitations are in `README.md`. Headline: $0.0097/video-second, 4.1x cheaper than fal, versus round 1's plain-model result of 1.33x more expensive than fal.

## 1. Question

Self-hosted Wan 2.2 costs more than fal's price at both 480p and 720p (rounds 1, 6), and cutting the step count on the plain model already showed a measurable quality cost in round 1's blind review (27 steps ranked best, 20 second, 15 worst). A distillation LoRA is trained specifically to produce a comparable image in far fewer steps without that quality loss. If it holds up, this is a direct route to a lower cost per video-second on hardware already in use, no new model family and no licensing blocker like round 7 hit. Does a 4-step distilled LoRA on Wan 2.2 A14B produce videos fast enough and clean enough, on the same prompts round 1 already has a blind-review baseline for, to beat fal's price where the plain model could not?

## 2. What the LoRA is, confirmed by reading the live repo

- Source: `lightx2v/Wan2.2-Distill-Loras` on Hugging Face, official `lightx2v` org, Apache 2.0, not gated. Confirmed by listing the repo's actual files, not a blog summary.
- The repo ships LoRA files for both Wan 2.2 variants: I2V (image-to-video) and T2V (text-to-video, the one this project uses). The T2V files are `wan2.2_t2v_A14b_high_noise_lora_rank64_lightx2v_4step_1217.safetensors` and the matching `low_noise` file -- one LoRA per expert, matching this project's existing two-expert (`transformer` / `transformer_2`) pipeline structure.
- **The README only documents I2V usage**, via a separate tool (`LightX2V/tools/convert/converter.py`) that merges the LoRA into the base weights offline, or the LightX2V project's own custom runtime -- neither of which is this project's existing pipeline. The T2V files have no written instructions of their own. **Checked separately (section 3)**: diffusers' own `load_lora_weights()` (this project's current pipeline class, `WanPipeline`) does handle these exact files correctly, through a conversion function diffusers' maintainers built specifically for this repo -- confirmed by running it, not assumed from the README's silence.
- The I2V README specifies a 4-step run needs a specific noise schedule, `denoising_step_list: [1000, 750, 500, 250]`, not just "set `num_inference_steps=4`" on the default scheduler. Whether this project's current scheduler (`UniPCMultistepScheduler`) can be given that exact timestep list, or whether a different scheduler is needed, is unconfirmed.
- A related repo, `lightx2v/Wan2.2-Distill-Models`, ships fully pre-merged 4-step checkpoints that would avoid all of the above -- but it is I2V only. No pre-merged T2V option was found.
- Guidance scale: this project's current config uses guidance 3.5 / 4.0 (two experts). Distilled models conventionally run near guidance 1.0 (little or no classifier-free guidance), but no T2V-specific number is confirmed anywhere found -- this is an assumption to test, not a known fact.

## 3. Safeguards

- **Loading checkpoint -- done, confirmed without a GPU.** Both T2V LoRA files were downloaded and run through diffusers' own conversion function (`_convert_non_diffusers_wan_lora_to_diffusers`, in `diffusers.loaders.lora_conversion_utils`, diffusers 0.36.0). This function is not a guess: its source comments cite this exact repo (`lightx2v/Wan2.2-Distill-Loras`) by name, meaning diffusers' own maintainers built and tested it specifically against this LoRA. Running it end to end on both files converted all 800 tensors each, no errors, no leftover unconverted keys, into key names (`transformer.blocks.0.attn1.to_q.lora_A.weight`, shape `[5120, 64]` at rank 64) confirmed to match the real model's own parameter names (pulled separately from `Wan-AI/Wan2.2-T2V-A14B-Diffusers`'s config, on the `meta` device, no weight download needed). This resolves the integration risk this round was built around -- `pipe.load_lora_weights()` should accept these files as-is.
- **Loading API, confirmed by reading `WanLoraLoaderMixin`'s actual source** (not the community example found earlier, which used a `components=` kwarg that does not exist on this method): the low-noise file needs `load_lora_weights(path, adapter_name=..., load_into_transformer_2=True)`; the high-noise file omits that flag and attaches to the default `transformer`.
- **Scheduler, also confirmed by reading the source**: `WanPipeline.__call__` always calls `self.scheduler.set_timesteps(num_inference_steps, device=device)` -- there is no pipeline-level argument to pass the LoRA's documented exact schedule (`[1000, 750, 500, 250]`) through. `lora_session.py` (section 4) patches `pipe.scheduler.set_timesteps` directly to force that schedule when `--force-schedule` is passed, and the smoke test compares that against the default schedule a plain `num_inference_steps=4` would compute.
- **Smoke test at the documented step schedule** (`[1000, 750, 500, 250]` or the closest equivalent this project's scheduler supports) on one short prompt before spending time on the full set -- checks that four steps actually produce a non-degenerate video (not noise, not a static frame) before committing to more clips.
- **Guidance scale is swept, not assumed**: the smoke test checks at least guidance 1.0 against the current default (3.5/4.0) before picking which one the full run uses.
- Independent stop guard (`pod_guard.sh`), same as every round.

## 4. Session design

- Resolution: **480p**, matching round 1 exactly, so this round's clips sit directly next to round 1's existing blind-review ladder (27, 20, 15 steps) for the same four prompts and seeds -- a four-point quality comparison (27 / 20 / 15 / 4-distilled) on identical content, not a new review from scratch.
- Prompts and seeds: round 1's frozen four (short, median, long, non-English) -- same job list file reused, only the step count and LoRA change.
- Per clip: generate time, cost, the existing automated gate, plus a blind-review slot alongside round 1's three existing ladder clips once this round's clips exist.

## 5. Budget

**Rough, and secondary to section 3's checkpoints** -- if the integration step itself fails or needs the heavier offline-merge fallback, most of the budget goes to establishing that, not to generation time.

| Item | Estimate |
|---|---|
| Setup, LoRA download (two files, rank 64 -- small relative to the 27B base weights) | under 10 min |
| Checkpoint: does the LoRA load cleanly | time-boxed, not scaled to generation cost |
| Smoke test, one short clip, step-schedule and guidance sweep | under 10 min if the checkpoint passes |
| Four clips at the confirmed working config | round 1's 27-step clips averaged 564.4 s each; at 4 of 27 steps, a naive linear estimate is ~84 s each, but round 1's own step-ladder data showed fixed per-job overhead makes fewer steps take *more* than a linear share of the time (15 steps was 58.8% of 27-step time, not 15/27 = 55.6%) -- so treat 84 s as a floor, not an estimate, and correct it from the smoke test's real timing |
| **Total** | **$10.00 cap**, sized generously since the integration risk (section 3) turned out to resolve cleanly and the remaining cost is mostly setup/weight-download time, not generation |

## 6. Limitations (known before running)

1. The core premise -- that this LoRA loads cleanly on this project's pipeline -- is confirmed (section 3). Whether the resulting video is actually usable quality is not; that is what the rest of this round measures.
2. Guidance scale and exact noise schedule for T2V are both assumptions carried over from the I2V documentation, not confirmed for T2V.
3. One reviewer, same as every prior blind review in this project -- a single data point on quality, not a statistically supported result.
4. 480p only this round; round 6 showed cost scales worse than linearly with resolution for the plain model, and whether a distilled LoRA's speed advantage holds the same way at 720p is untested here.
5. If the offline-merge fallback (section 3) is needed, this round's scope and budget would need revisiting before continuing -- not assumed to fit inside the figure in section 5.
