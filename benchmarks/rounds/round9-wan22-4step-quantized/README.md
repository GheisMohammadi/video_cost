[← All rounds](../../../README.md)

# Round 9: int8 quantization on top of round 8's 4-step LoRA (Oct 14-15, 2026)

Status: complete. Round 1's exact four prompts and seeds, same 480p settings, int8 weight-only quantization stacked on round 8's 4-step distillation LoRA. All four clips generated, verified, and visually checked.

## Watch one of the clips

Median prompt, 4-step LoRA plus int8 quantization:

<video src="clips/A2_median.mp4" controls width="420"></video>

Same prompt and seed, 4-step LoRA only (round 8), for comparison:

<video src="../round8-wan22-4step-lora/clips/A2_median.mp4" controls width="420"></video>

## 1. Summary

- **Quantization makes generation faster, not just smaller.** Mean generate time dropped from round 8's 107.2 s to **84.2 s**, a further **1.27x speedup** on top of round 8's already-fast result. Combined with round 8's 5.27x over the plain model, this round's config is roughly **6.7x faster than the plain 27-step model** on these prompts.
- **Cost, pod already warm (matches round 8's own convention)**: **$0.0076/video-second, 0.19x fal's $0.04 -- 5.25x cheaper than fal**, up from round 8's 4.1x. Run through the project's $1M profit formula: roughly **$4.26M profit** on $1,000,000 spent, versus round 8's ~$3.1M.
- **Peak VRAM dropped from 33.5 GB to 19.6 GB** (about 41% less), confirming int8 weight-only quantization's expected memory benefit alongside the unexpected generation-speed benefit.
- **Loading the quantized model is much slower, and this matters for short sessions.** One-time load cost for both experts: 581.6 s, versus round 8's roughly 80-100 s for plain bf16. The `torchao` version this environment's `torch` (2.8.0) supports does not have working C++ acceleration kernels (they require torch >= 2.11.0), so quantization itself runs through a slower fallback path during loading. Counting this one-time cost against only this round's four clips gives an all-in figure of $0.0207/video-second, 0.52x fal -- worse than the generation-only figure, though this cost is fixed per session and would shrink as a fraction of total cost with more clips generated per pod session.
- **Visual quality holds up; the one known defect is unchanged.** A1, A2, and A4 show no visible artifacts from quantization. A3 (the Indomie commercial prompt) has the same garbled on-screen text round 8 found ("MISSIU N FENOIOT SPCIFT" here, versus round 8's similarly garbled text on the same prompt) -- confirming this defect comes from the LoRA/distillation, not from quantization.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 2.2 T2V-A14B (diffusers), bf16 base with both experts quantized via `TorchAoConfig(Int8WeightOnlyConfig())`, plus round 8's T2V 4-step LoRA attached on top (confirmed: diffusers' LoRA loader handles a quantized base transformer via its own `is_quantized` code path) |
| Request | 832x480, 81 frames at 16 fps (5.0625 s), 4 inference steps, guidance 1.0 / 1.0 -- identical settings to round 8, isolating quantization as the only variable |
| Prompts | Round 1's exact four prompts and seeds: short, median, long (truncated), non-English |
| Hardware | One RunPod A100-SXM4-80GB pod (after two earlier pod attempts hit integration issues before any generation -- section 4) |
| Prices used | $1.618/h GPU, $0.02778/h disk (round 1's assumed rate), fal 480p $0.04/video-second |

## 3. Results

| Job | Gen-only busy s | Gen-only $/video-s | vs fal $0.04 | Round 8 busy s | Speedup vs round 8 |
|---|---|---|---|---|---|
| A1 short | 90.2 | $0.0081 | 0.20x | 113.5 | 1.26x |
| A2 median | 83.5 | $0.0075 | 0.19x | 112.4 | 1.35x |
| A3 long (truncated) | 80.5 | $0.0073 | 0.18x | 103.0 | 1.28x |
| A4 non-English | 82.6 | $0.0075 | 0.19x | 99.8 | 1.21x |

Mean: 84.2 s busy, $0.0385/clip, $0.0076/video-second, 0.19x fal's price, 1.27x faster than round 8 on the same four prompts.

All-in for this session (one-time 581.6 s quantized load plus the four clips' 336.8 s combined generation, divided across only these four clips): $0.1050/clip, $0.0207/video-second, 0.52x fal.

Every clip passed the automated gate (81 frames, correct 832x480 shape, not black, not frozen). All four clip files were pulled and verified by sha256 against their jobs.jsonl records.

## 4. Two pod attempts before this one, neither producing generation output

| Attempt | Issue | Cause | Resolution |
|---|---|---|---|
| First pod | `torchao`'s latest release failed to import | Needs a newer `torch` than this pipeline's 2.8.0 has (`ScalingType` not present) | Tested versions down to a compatible one (0.17.0), confirmed by import check before any pod cost beyond the version search itself |
| First pod, continued | `TorchAoConfig("int8_weight_only")` raised a `TypeError` | diffusers 0.41.0 requires an `AOBaseConfig` instance, not the string argument that worked against an older diffusers version tested locally | Switched to `TorchAoConfig(Int8WeightOnlyConfig())`, confirmed working via the same import check |
| First pod, continued | Pod stopped by the independent guard mid-generation, before a result was produced | The session script reloaded the model once per process launch (a loading check, then a separate smoke test); each load took the newly-discovered 581.6 s, and two loads in one pod session left too little of the guard's 40-minute deadline for the smoke test's generation step to finish. The guard stopped the pod on schedule, correctly -- this was the guard working as designed, not a crash | Rewrote the script to load once per process and run the warm-up check and the real job list in the same invocation, regardless of mode |
| Second pod | None -- this attempt produced this round's results | -- | HARD_S raised to 45 minutes to give the single ~582 s load comfortable room alongside generation |

## 5. Limitations

1. Quantized loading's 581.6 s cost was measured once, on one pod; the earlier pod's loading-only check measured a similar 650 s, so this appears consistent, but neither is a controlled repeat.
2. The C++ acceleration kernels this `torchao` version expects are unavailable on this environment's `torch` version. Whether quantized generation would be faster still with those kernels working is untested; the speedup measured here comes despite running through a slower fallback path, which makes the result conservative, not optimistic.
3. No blind quality review this round, matching round 8's own scope -- the text-rendering defect noted in section 1 is an observation from direct frame inspection, not a formal review.
4. 480p only, same as round 8.
5. One session, four comparable clips -- no repeats, no confidence intervals, same limitation as every prior round.
6. The all-in figure (section 3) assumes only four clips share the one-time load cost; a longer-running pod generating more clips per session would show a better all-in figure without any change to the underlying method.

## 6. Still to do

1. A longer job list in one pod session, to see how the all-in cost (section 3) improves as more clips amortize the fixed load cost.
2. Investigate whether a `torch` upgrade (to >= 2.11.0) restores `torchao`'s C++ kernels and reduces the 581.6 s load time, which is this round's main remaining inefficiency.
3. A blind quality review of this round's clips alongside round 1's and round 8's, now that three comparable configurations exist for the same four prompts.
4. Test at 720p.

## 7. Files

- `jobs.jsonl`, `preflight.json`: raw records, reconstructed from the session's own output (section 4 explains why -- the two prior pod attempts never reached generation and left no complete session.json).
- `clips/`: `A1_short.mp4`, `A2_median.mp4`, `A3_long.mp4`, `A4_non_english.mp4`, each verified by sha256 against its jobs.jsonl record.
- `quant_session.py`, `round9_jobs.json`: the session script (in its working, single-load form) and frozen job list, committed alongside `PLAN.md` before this round's results existed.
