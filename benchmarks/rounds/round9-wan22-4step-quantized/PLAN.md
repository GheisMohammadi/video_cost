[← All rounds](../../../README.md)

# Round 9 test design: quantization on top of round 8's 4-step LoRA

Status: the loading combination is confirmed working (quantized transformer plus LoRA attaches cleanly, both experts), but no generation result exists yet. First attempt: `torchao`'s latest release failed to import against this pipeline's torch version; a compatible version (0.17.0) was found, then diffusers 0.41.0's `TorchAoConfig` required an `AOBaseConfig` instance rather than the string argument that worked locally against an older diffusers version -- both fixed before any pod cost. Loading itself then measured 650s (versus round 8's ~100s for plain bf16), because the C++ acceleration kernels this torchao version needs are not available for this pipeline's torch version -- quantization runs through a slower fallback path. Since the session script originally reloaded the model once per process launch, two separate launches (a loading check, then a smoke test) spent the 650s load cost twice, leaving the guard's 40-minute hard deadline too little room for the smoke test's generation step to finish -- the guard stopped the pod on schedule, correctly, mid-generation. Fixed: `quant_session.py` now loads once per process and runs the warm-up sanity check and the real job list in the same run, regardless of which mode is requested.

## 1. Question

Does quantizing the model (int8 weight-only) on top of round 8's already-working 4-step LoRA reduce cost per video-second further, on an A100 -- and does it change output quality? Secondary question: does LightX2V's newer T2V LoRA release (dated 250928) differ meaningfully from the one round 8 used (dated 1217), given the source repo itself ships a comparison video between the two versions?

## 2. What was researched before writing this plan

- **NVFP4 (4-bit) is ruled out for this project's hardware.** LightX2V ships a pre-quantized NVFP4 T2V checkpoint (`lightx2v/LightWan2.2-A14B`), but NVFP4 has no native tensor-core support on Ampere (A100) or Hopper (H100) -- only Blackwell. Loading an NVFP4 checkpoint on an A100 forces dequantization back to bf16 before inference, which gives no speed or memory benefit and adds dequantization overhead. Confirmed from hardware vendor documentation, not the model card. Not tested this round.
- **INT8 weight-only quantization is a real option on A100.** Diffusers' own `torchao` integration documents this path explicitly, including A100 benchmarks (CogVideoX-5B: ~19.7 GB bf16 down to ~10.3 GB int8 weight-only). This reduces memory, and may reduce time depending on whether this workload is memory-bandwidth-bound -- not confirmed for Wan 2.2's architecture specifically, this round's job to measure.
- **A newer LightX2V T2V 4-step LoRA release exists**, in `lightx2v/Wan2.2-Lightning` (`Wan2.2-T2V-A14B-4steps-lora-250928/`), separate from `lightx2v/Wan2.2-Distill-Loras` (the "1217"-dated files round 8 used). The repo includes its own comparison video (`v1.1-vs-250928.mp4`) between versions, meaning the source project itself treats these as different enough to document -- not yet confirmed which, if either, is better for this project's prompts.
- **LightX2V's own quantized T2V checkpoints exist only as NVFP4** (ruled out above) **or int8** (`lightx2v/Wan2.2-Distill-Models` is I2V only, but other repos list int8 T2V files per LightX2V's documentation) -- confirmed to exist, not yet confirmed loadable through this project's existing `diffusers` pipeline the way round 8's LoRA was. This is section 3's first checkpoint.

## 3. Safeguards

- **Loading checkpoint before any pod time, same pattern as round 8**: confirm quantized weights (either a LightX2V-published int8 T2V checkpoint, or `torchao` applied to the already-working round 8 pipeline) actually load through this project's `WanPipeline`, and that a LoRA already applied to a quantized model (or a quantized model with a LoRA applied on top) behaves as expected -- order of operations between quantization and LoRA loading is a new integration question round 8 did not need to answer. Do this locally where possible (inspecting checkpoint structure, as round 8 did for the LoRA's tensor keys) before spending pod time.
- **Smoke test on one short prompt** before the full set, same as round 8 -- checks for degenerate output, not just the automated gate, given round 8 found the gate misses a real guidance-related defect that only direct frame inspection caught.
- **`PROC_PATTERN` set correctly from the start** (`[l]ora_session` or this round's actual process name) -- round 8 found this defaulted wrong and silently disabled the guard's crash-detection for an entire run.
- **Clear `SESSION_DONE` before reusing a pod for a follow-up job** -- round 8's second pod stopped mid-way through a follow-up run because a stale marker from the prior job was never cleared.
- Independent stop guard (`pod_guard.sh`), same as every round.

## 4. Session design

- Resolution: 480p, matching rounds 1 and 8, so results sit next to both.
- Prompts and seeds: round 1's frozen four (short, median, long, non-English), same as round 8.
- Primary comparison: round 8's exact config (4-step LoRA, guidance 1.0, bf16) versus the same config with int8 weight-only quantization applied.
- Secondary, time/budget permitting: the "250928" LoRA release versus the "1217" release round 8 used, at the same (non-quantized) settings, to isolate which change (quantization vs. LoRA version) causes which effect rather than changing both at once.

## 5. Budget

**$10.00 cap**, same figure as round 8, not yet re-confirmed for this round. Sized the same way round 8 was: most of the risk is in the loading checkpoint (section 3), not generation time, since four 4-step clips at round 8's measured pace cost under $0.20 total.

| Item | Estimate |
|---|---|
| Setup, quantized-checkpoint or torchao integration, loading checkpoint | uncertain, time-boxed rather than estimated -- this round's own job to establish, same caveat round 8's plan carried for its own integration risk |
| Smoke test | under 10 min once the checkpoint passes |
| Four clips, quantized config | round 8's 4-step clips averaged 107.2 s busy each; quantization's effect on that number is what this round measures, not assumed |
| Four clips, "250928" LoRA at bf16 (if budget allows) | similar order of magnitude to round 8's clips |

## 6. Limitations (known before running)

1. Whether int8 quantization helps at all on this workload is unconfirmed -- Wan 2.2's A14B dual-expert DiT may be compute-bound rather than memory-bandwidth-bound at this batch size, in which case weight-only quantization would save memory without saving time.
2. No blind quality review planned this round either, matching round 8 -- cost and loading-feasibility questions come first, same as round 8's own stated scope.
3. 480p only, same as round 8.
4. If both the quantization test and the LoRA-version test are run, four clips each means eight total, doubling round 8's four-clip scope -- budget (section 5) may not cover both; the quantization test is the priority if a choice is needed.
5. One session's worth of data per configuration -- no repeats, no confidence intervals, same limitation as every prior round.
