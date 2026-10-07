[← All rounds](../../../README.md)

# Round 8: Wan 2.2 A14B with a 4-step distillation LoRA (Oct 7-8, 2026)

Status: complete for the question this round asked (cost). Round 1's exact four prompts and seeds, same 480p settings, comparing a 4-step distilled LoRA against the plain 27-step model. No blind quality review this round (see section 6); one real visual defect found and reported in section 3.

## Watch one of the clips

Median prompt, 4 steps with the distillation LoRA:

<video src="clips/A2_median.mp4" controls width="420"></video>

Same prompt and seed, 27 steps, no LoRA, from round 1:

<video src="../round1-wan22-a14b-480p/clips/A2_median.mp4" controls width="420"></video>

## 1. Summary

- **The LoRA works, and it is the first result in this project where self-hosting beats fal's price.** Mean cost **$0.0097/video-second**, about **0.24x fal's $0.04** -- roughly **4.1x cheaper than fal**, versus round 1's plain-model result of 1.33x *more expensive* than fal at the same settings.
- Generation time dropped from a mean of 564.4 s (round 1, 27 steps) to 107.2 s (this round, 4 steps) on the same four prompts -- a **5.27x speedup**, more than the 6.75x step-count ratio alone would predict, which is expected since fixed per-job overhead (model forward setup, VAE decode) does not shrink with fewer steps.
- **Guidance scale matters more than step count here.** The default guidance (3.5/4.0, what every prior round used) produces visibly broken output with this LoRA -- a rippling, glass-crack-like distortion across the frame. Guidance 1.0 (the conventional classifier-free-guidance-free setting for a distilled model) produces clean, coherent output and is also faster, since low guidance skips an extra forward pass per step. This was confirmed by direct visual inspection of extracted frames, not just the automated gate, which passed both configurations.
- **One real quality defect found**: on-screen text in one clip (A3, the Indomie commercial prompt) renders as garbled, illegible characters instead of readable words. Text rendering is a known weak point for video diffusion generally; whether this is worse under 4-step distillation specifically is not established by one clip.
- One documented scheduler limitation: the LoRA's own documentation recommends an exact 4-step noise schedule, but this project's pipeline uses `UniPCMultistepScheduler`, which does not accept an explicit timestep list -- only the plain `num_inference_steps=4` schedule was tested, not the documented exact one. See section 5.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 2.2 T2V-A14B (diffusers), bf16, CPU offload, plus `lightx2v/Wan2.2-Distill-Loras`' T2V 4-step LoRA (rank 64, one file per expert) |
| Loading | `pipe.load_lora_weights(high_noise_path, adapter_name="high")` for the `transformer` component; `pipe.load_lora_weights(low_noise_path, adapter_name="low", load_into_transformer_2=True)` for `transformer_2` -- confirmed against the installed diffusers source, not a community example (see round 8's `PLAN.md`, section 3) |
| Request | 832x480, 81 frames at 16 fps (5.0625 s), 4 inference steps, guidance 1.0 / 1.0, default (`UniPCMultistepScheduler`) 4-step schedule |
| Prompts | Round 1's exact four prompts and seeds, reused for direct comparison: short, median, long (truncated), non-English |
| Hardware | Two RunPod A100-SXM4-80GB pods (see section 4) |
| Prices used | $1.618/h GPU, $0.02778/h disk (same assumed rate as round 1), fal 480p $0.04/video-second |

## 3. Results

| Job | LoRA busy s | LoRA $ | LoRA $/video-s | vs fal $0.04 | Plain 27-step busy s (round 1) | Speedup | Cost cut |
|---|---|---|---|---|---|---|---|
| A1 short | 113.5 | $0.0519 | $0.0102 | 0.26x | 554.8 | 4.89x | 79.5% |
| A2 median | 112.4 | $0.0514 | $0.0102 | 0.25x | 571.8 | 5.09x | 80.3% |
| A3 long (truncated) | 103.0 | $0.0471 | $0.0093 | 0.23x | 569.8 | 5.53x | 81.9% |
| A4 non-English | 99.8 | $0.0456 | $0.0090 | 0.23x | 561.3 | 5.62x | 82.2% |

Mean: 107.2 s busy, $0.0490/clip, $0.0097/video-second, 0.24x fal's price (4.1x cheaper), 5.27x faster than round 1's plain model on the same four prompts.

Every clip passed the automated gate (81 frames, correct 832x480 shape, not black, not frozen). A1's clip file itself was lost when its pod died before being pulled back (section 4); its timing and gate record survive and are included above, but it was not available for the visual check in section 1 that caught A3's text defect.

## 4. What happened during the session

This round needed two pods and surfaced three real issues, none of which affect the numbers in section 3 (the affected runs were cleanly isolated or redone):

1. **Missing dependency, caught before any generation**: the first launch failed immediately with `PEFT backend is required for load_lora_weights()` -- `peft` was not in the dependency list this round's script installed. Fixed by adding it; no cost impact, the base model weights were already downloaded and cached.
2. **First pod died mid-run, cause unconfirmed.** After the smoke test and A1_short completed cleanly, the pod became unreachable (`container not found`) before A2 started. Timing rules out the independent stop-guard's hard deadline (the pod died roughly 5-6 minutes before it would have fired). A real bug was found while investigating: the guard was armed with its default `PROC_PATTERN` (`wan22_a14b_session`), which never matches this round's actual process name (`lora_session.py`) -- meaning the guard's crash-detection path was silently inactive for this entire run. That bug is fixed for the second pod (section 5), though it does not explain this specific death, since the only two stop paths that do not depend on `PROC_PATTERN` (the hard deadline, and the done-marker grace period) both don't fit the timing either. A1_short's clip file was lost with this pod; its jobs.jsonl record survives (section 3).
3. **Second pod, a mistake this time, not a mystery**: after A2-A4 completed, the `SESSION_DONE` marker from that run was never cleared before a follow-up job (regenerating A1's lost clip) was launched on the same pod. The independent guard counted its grace period from the *original* run's completion and correctly stopped the pod mid-regeneration -- the guard worked exactly as designed; the process mistake was reusing a pod without clearing its prior completion marker. A1 was not regenerated a second time; its data from the first pod is used as-is (section 3's note).

Net effect: A2-A4 are complete, verified, and clean. A1's numbers are real but its clip file does not exist locally.

## 5. Limitations

1. The LoRA's documented exact 4-step noise schedule (`[1000, 750, 500, 250]`) was never actually tested -- only the default schedule `UniPCMultistepScheduler` computes for `num_inference_steps=4`. An attempt to force the exact schedule failed (`UniPCMultistepScheduler.set_timesteps()` does not accept a `timesteps` argument, unlike the scheduler class this was tested against locally before any pod was used -- see round 8's `PLAN.md`, section 3, which separately confirmed the LoRA's *loading* path, not its *scheduling* path). Whether the documented schedule would do meaningfully better is untested.
2. One clip (A3) showed a clear text-rendering defect; no systematic check across more clips or more prompts with on-screen text was done.
3. No blind quality review this round -- it answers a cost question first, matching this round's own plan. A1's clip being unavailable means a future review can only compare A2-A4 directly against round 1's ladder, not all four.
4. 480p only. Round 6 showed cost scales worse than linearly with resolution for the plain model; whether a distilled LoRA's speed advantage holds at 720p is untested.
5. One session, four comparable clips (three with surviving files) -- no repeats, no confidence intervals, same limitation as every prior round.
6. The $1.618/h and $0.02778/h rates are the project's standing assumed rates, not reconciled against actual RunPod billing for either pod this round used.

## 6. Still to do

1. A blind quality review of A2-A4 against round 1's 27-step clips for the same prompts, to check whether the speed and cost advantage found here comes with a quality cost the way round 1's own steps-ladder did (27 vs 20 vs 15 steps, no LoRA).
2. Fix the scheduler limitation (section 5, item 1) and test the LoRA's documented exact schedule against the default one actually used here.
3. Test at 720p.
4. Re-run with `PROC_PATTERN` set correctly from the start (section 4, item 2) to find out whether the first pod's death was the guard after all, or something else.

## 7. Files

- `jobs.jsonl`: all seven records (two smoke-test configs that succeeded, one that failed, and all four A-strata jobs), reconstructed from the session's own output after the pods that generated them stopped -- not pulled by `pull_session.py`, since this round's ad hoc smoke-test flow did not use it.
- `preflight.json`: the second pod's preflight record; the first pod's GPU identity is noted inline since its own preflight.json was never pulled back.
- `clips/`: `A2_median.mp4`, `A3_long.mp4`, `A4_non_english.mp4` (the real 4-step LoRA results, each verified by sha256 against its jobs.jsonl record), plus `smoke_a_default_guidance.mp4` and `smoke_b_guidance1.mp4` (the two smoke-test clips on the warm-up prompt that showed the guidance-scale finding in section 1).
- `lora_session.py`, `round8_jobs.json`: the session script and frozen job list, committed alongside `PLAN.md` before this round ran.
