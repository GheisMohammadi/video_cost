# Round 4 test design: GPU hardware lottery and output reproducibility

Status: scripts written and tested against synthetic data; not yet run on a GPU. This is List6 items 1 and 2, combined as originally planned (item 2 rides free on item 1's runs). Frozen before running.

## 1. Question

Rounds 1-3 all used a RunPod A100-SXM4-80GB, requested the same way each time, but never verified whether "the same GPU spec" means consistent real-world performance across different rentals, or whether performance depends on which specific instance is assigned. This round rents two fresh pods of the identical advertised spec and runs the identical frozen job list on both, to answer that directly. Riding on the same data: with the identical seed, does the identical prompt produce the same output on two different physical GPUs, or does it drift -- relevant to verifying a remote worker's output on a distributed GPU network, not just a curiosity.

## 2. What is already known, for free, before spending anything

Rounds 1 and 3 happen to already include one directly comparable data point: the same prompt and seed (`A1_short`, seed 4200, 27 steps) was run on two different pod rentals (round 1's pod and round 3's pod). Neither run was designed as a controlled comparison -- different sessions, days, and (for round 3) a different in-memory code path -- so this is suggestive context, not this round's result:

| | Round 1 pod | Round 3 pod |
|---|---|---|
| Generate time | 551.7 s | 554.6 s (0.5% higher) |
| GPU utilization | 92.0% | 92.6% |
| SM clock mean | 1310 MHz (of 1410 max) | 1313 MHz |
| Throttle reason | 0x4 (software power cap) | 0x4 (software power cap) |
| Driver version | 580.126.16 | 580.126.16 |

The two rentals landed within 0.5% of each other's speed and showed the identical throttle reason. That could mean either of two different things, and this round is designed to tell them apart: (a) this specific software power cap is applied fleet-wide to this instance type, so "the lottery" mostly doesn't apply to raw speed, or (b) it is a coincidence and two more samples would show more spread. Neither prior session recorded a GPU UUID (a unique per-physical-unit identifier), so it is not even confirmed whether rounds 1 and 3 used two different physical GPUs or the same one twice -- fixed for this round (section 5).

## 3. Test design

Reuses round 1's exact, unmodified, already-committed job list (`benchmarks/prompts/hour_test_jobs.json`, sha256 `b19fd5f5902a13ebba3207dc3e2455e72ac817441600e79efe0ac736323db21d`) and its exact, already-proven session runner, guard, and orchestrator (`wan22_a14b_session.py`, `pod_guard.sh`, `run_hour_session.sh`), unchanged except for one small, additive fix (section 5). No new prompt selection and no new generation code -- the only new work this round is running that same, already-verified procedure on two pods instead of one, and comparing the results.

Procedure:
1. Rent a fresh A100-SXM4-80GB pod ("pod A"), run the full existing job list on it (warm-up, then A1-A4 at 27 steps, then B1/B2 at 20/15 steps on the median prompt), copy and verify results, stop the pod.
2. Rent a second fresh A100-SXM4-80GB pod ("pod B"), same procedure.
3. Run `compare_pods.py` locally on the two results, which reports:
   - Whether the two pods' GPU UUIDs prove they are physically different units.
   - Generate time, GPU clock, throttle reason, and peak VRAM for each of the 6 shared jobs, pod A vs pod B, and the mean speed difference across them.
   - For the four prompts sharing a seed and step count across both pods (A1-A4, all at 27 steps): whether the two pods' output files are byte-identical, whether the decoded frames are byte-identical, and if not, the mean pixel difference -- checked against the scale round 3 established for what "genuinely different content" looks like (roughly 50 and above), so a small drift and an actual mismatch are not confused with each other.

Pods are rented sequentially (one full session, then the next), matching every prior round's practice, not simultaneously. This means the two sessions do not happen at the exact same time, which is a real limitation (see section 7): a fair comparison of "the same instance type" still leaves open whether the day or hour of rental affects fleet-wide contention, something this design cannot separate from a true per-unit hardware difference.

## 4. Reproducibility: what result would mean what

Stated before running, so the interpretation is not adjusted after seeing the answer:
- **Exact match** (byte-identical decoded frames): the strongest possible result, meaning this pipeline's output is fully deterministic given a seed, independent of which physical GPU ran it.
- **Small nonzero difference, content matches on inspection**: the expected, unremarkable outcome -- GPU floating-point operations are not guaranteed to reduce in the same order on different hardware, so tiny numerical drift compounding over 27 diffusion steps is normal and does not mean the seed failed to do its job.
- **Large difference, in the range round 3 found between genuinely different videos**: would mean the seed does not actually pin down the output across hardware, a real finding with direct relevance to verifying work on a distributed GPU network, and would need to be flagged clearly rather than averaged away.

## 5. One small, additive fix before this round

`wan22_a14b_session.py`'s preflight now also captures each GPU's UUID (`nvidia-smi --query-gpu=uuid`), a single read-only query added alongside the existing GPU-name query. This does not touch any generation, gating, or timing logic. Without it, this round could not actually confirm whether two rentals are different physical units, only infer it indirectly -- the gap that made section 2's existing data inconclusive on that specific question.

## 6. Budget

| Item | Per pod | Both pods |
|---|---|---|
| Setup, preflight, download | ~15 min | ~30 min |
| Warm-up + 6 measured jobs (same as round 1) | ~53 min | ~106 min |
| Copy results | ~3 min | ~6 min |
| **Total** | **~71 min, about $1.92** | **~142 min, about $3.84** |

Session cap: **$5.00** total across both pods, matching List6's original combined estimate for items 1-2 ($3-5). Each pod uses the same guard and go/no-go rules already proven in round 1 (preflight abort on a bad GPU, pause if the first job runs far over estimate).

## 7. Limitations

1. **Sequential, not simultaneous rentals.** The two pods are not compared at the same moment in time, so fleet-wide contention effects (time of day, day of week) are not separated from genuine per-unit hardware variance. A true controlled experiment would rent both at once; this round does not, matching every prior round's one-pod-at-a-time practice and keeping cost predictable.
2. **Two samples.** This establishes whether two rentals differ, not a distribution of how much rentals typically differ. A finding here (for example, both throttled identically) is suggestive of a fleet-wide pattern, not proof of one.
3. **Reproducibility is checked only within this pipeline's specific settings** (bf16, CPU offload, this diffusers version) -- it does not generalize to other precision or optimization settings.
4. **RunPod cannot be asked for a specific physical unit.** "The lottery" here means two independent requests for the same instance type, whatever RunPod's scheduler assigns -- consistent with how this project has always rented pods, and with what a real user of this GPU tier would experience.
