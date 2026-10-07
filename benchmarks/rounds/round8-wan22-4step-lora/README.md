[← All rounds](../../../README.md)

# Round 8: Wan 2.2 A14B with a 4-step distillation LoRA (Oct 7-8, 2026)

Status: complete for the cost question this round asked. Round 1's exact four prompts and seeds, same 480p settings, 4-step distilled LoRA versus the plain 27-step model. No blind quality review this round (section 5); one visual defect is documented in section 1.

## Watch one of the clips

Median prompt, 4 steps with the distillation LoRA:

<video src="clips/A2_median.mp4" controls width="420"></video>

Same prompt and seed, 27 steps, no LoRA, from round 1:

<video src="../round1-wan22-a14b-480p/clips/A2_median.mp4" controls width="420"></video>

## 1. Summary

- **First result in this project where self-hosting costs less than fal.** Mean cost **$0.0097/video-second**, **0.24x fal's $0.04** -- **4.1x cheaper than fal**. Round 1's plain model, same prompts and settings, cost 1.33x *more* than fal.
- Generation time: mean 564.4 s (round 1, 27 steps) to 107.2 s (this round, 4 steps) on the same four prompts -- a **5.27x speedup**. Fixed per-job overhead (model forward setup, VAE decode) does not shrink with fewer steps, so the speedup is smaller than the 6.75x step-count ratio alone.
- **Guidance scale determines output quality with this LoRA; the automated gate does not catch the difference.** Default guidance (3.5/4.0, used by every prior round) produces a rippling, glass-crack-like distortion across the frame. Guidance 1.0 (the standard classifier-free-guidance-free setting for a distilled model) produces clean, coherent output and is faster, since low guidance skips an extra forward pass per step. Both configurations pass the automated gate (frame count, shape, not black, not frozen); only direct inspection of extracted frames shows the distortion.
- **One quality defect**: on-screen text in one clip (A3, the Indomie commercial prompt) renders as garbled, illegible characters instead of readable words. Text rendering is a known weak point for video diffusion generally; one clip does not establish whether 4-step distillation makes it worse.
- The LoRA's documentation recommends an exact 4-step noise schedule. This project's pipeline uses `UniPCMultistepScheduler`, which does not accept an explicit timestep list; only the plain `num_inference_steps=4` schedule was tested. See section 4.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 2.2 T2V-A14B (diffusers), bf16, CPU offload, plus `lightx2v/Wan2.2-Distill-Loras`' T2V 4-step LoRA (rank 64, one file per expert) |
| Loading | `pipe.load_lora_weights(high_noise_path, adapter_name="high")` for the `transformer` component; `pipe.load_lora_weights(low_noise_path, adapter_name="low", load_into_transformer_2=True)` for `transformer_2` -- confirmed against the installed diffusers source (round 8's `PLAN.md`, section 3) |
| Request | 832x480, 81 frames at 16 fps (5.0625 s), 4 inference steps, guidance 1.0 / 1.0, default (`UniPCMultistepScheduler`) 4-step schedule |
| Prompts | Round 1's exact four prompts and seeds: short, median, long (truncated), non-English |
| Hardware | Two RunPod A100-SXM4-80GB pods (section 4) |
| Prices used | $1.618/h GPU, $0.02778/h disk (round 1's assumed rate), fal 480p $0.04/video-second |

## 3. Results

| Job | LoRA busy s | LoRA $ | LoRA $/video-s | vs fal $0.04 | Plain 27-step busy s (round 1) | Speedup | Cost cut |
|---|---|---|---|---|---|---|---|
| A1 short | 113.5 | $0.0519 | $0.0102 | 0.26x | 554.8 | 4.89x | 79.5% |
| A2 median | 112.4 | $0.0514 | $0.0102 | 0.25x | 571.8 | 5.09x | 80.3% |
| A3 long (truncated) | 103.0 | $0.0471 | $0.0093 | 0.23x | 569.8 | 5.53x | 81.9% |
| A4 non-English | 99.8 | $0.0456 | $0.0090 | 0.23x | 561.3 | 5.62x | 82.2% |

Mean: 107.2 s busy, $0.0490/clip, $0.0097/video-second, 0.24x fal's price, 5.27x faster than round 1's plain model on the same four prompts.

Every clip passed the automated gate (81 frames, correct 832x480 shape, not black, not frozen). A1's clip file does not exist locally (section 4); its timing and gate record are included above. It was not available for the visual inspection that found A3's text defect (section 1).

## 4. Two pods, three issues

This round ran across two pods. None of the three issues below changed the numbers in section 3; each affected run is either excluded or marked.

| Issue | Cause | Effect on results |
|---|---|---|
| First launch failed immediately | `peft` was not in the dependency list this round's script installed; `load_lora_weights()` requires it | None -- fixed before any generation, base weights already cached |
| First pod became unreachable before A2 started, after the smoke test and A1_short completed | Not established. The independent stop-guard's hard deadline is ruled out by timing (the pod stopped responding roughly 5-6 minutes before that deadline). A separate, confirmed bug: the guard was armed with its default `PROC_PATTERN` (`wan22_a14b_session`), which never matches this round's actual process (`lora_session.py`), so its crash-detection path was inactive for the entire run -- but neither of the guard's other two stop conditions (hard deadline, done-marker grace period) fits the observed timing either, so this bug does not explain the pod's disappearance | A1_short's clip file is unrecoverable; its jobs.jsonl record (section 3) was captured before the pod stopped responding |
| Second pod stopped mid-way through a follow-up job (regenerating A1's missing clip) | The `SESSION_DONE` marker from the completed A2-A4 run was not cleared before the follow-up job was launched on the same pod. The independent guard counted its grace period from that marker's timestamp and stopped the pod once it elapsed, which is its designed behavior given a leftover marker | A1 was not regenerated; its data from the first pod is used as-is (section 3) |

A2-A4 are complete and verified. A1's measurements are real; its clip file is not available.

## 5. Limitations

1. The LoRA's documented exact 4-step noise schedule (`[1000, 750, 500, 250]`) was not tested -- only the default schedule `UniPCMultistepScheduler` computes for `num_inference_steps=4`. Forcing the exact schedule fails (`UniPCMultistepScheduler.set_timesteps()` does not accept a `timesteps` argument). Whether the documented schedule performs differently is untested.
2. One clip (A3) has a text-rendering defect; no systematic check across more clips or more prompts with on-screen text was done.
3. No blind quality review this round. A1's clip being unavailable limits a future review to A2-A4 against round 1's ladder, not all four.
4. 480p only. Round 6 found cost scales worse than linearly with resolution for the plain model; whether a distilled LoRA's speed advantage holds at 720p is untested.
5. One session, four comparable clips (three with surviving files) -- no repeats, no confidence intervals, same limitation as every prior round.
6. The $1.618/h and $0.02778/h rates are the project's standing assumed rates, not reconciled against actual RunPod billing for either pod this round used.

## 6. Still to do

1. A blind quality review of A2-A4 against round 1's 27-step clips for the same prompts, to check whether the speed and cost advantage found here comes with a quality cost the way round 1's own steps-ladder did (27 vs 20 vs 15 steps, no LoRA).
2. Fix the scheduler limitation (section 5, item 1) and test the LoRA's documented exact schedule against the default one used here.
3. Test at 720p.
4. Re-run with `PROC_PATTERN` set correctly from the start (section 4) to establish whether the first pod's disappearance was guard-related or not.

## 7. Files

- `jobs.jsonl`: all seven records (two smoke-test configs that succeeded, one that failed, and all four A-strata jobs), reconstructed from the session's own output, since this round's smoke-test flow did not use `pull_session.py`.
- `preflight.json`: the second pod's preflight record; the first pod's GPU identity is noted inline since its own preflight.json was not pulled back.
- `clips/`: `A2_median.mp4`, `A3_long.mp4`, `A4_non_english.mp4` (the 4-step LoRA results, each verified by sha256 against its jobs.jsonl record), plus `smoke_a_default_guidance.mp4` and `smoke_b_guidance1.mp4` (the two smoke-test clips on the warm-up prompt that demonstrate section 1's guidance-scale finding).
- `lora_session.py`, `round8_jobs.json`: the session script and frozen job list, committed alongside `PLAN.md` before this round ran.
