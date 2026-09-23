# Round 3 test design: cost under concurrent load (batching)

Status: scripts written and tested against synthetic data; not yet run on a GPU. This is List6 item 3. Frozen before running; job list sha256 in section 4.

## 1. Question

Every cost figure so far (rounds 1 and 2) is for one request handled start to finish before the next begins. Production load looks different: multiple requests arrive close together and the GPU is asked to work on more than one at a time. This round measures whether that changes cost-per-video-second, in either direction, using the same model, settings, and even the same four prompts and seeds already measured individually in round 1.

## 2. Scope: what "concurrent load" means in this test

There are three different things "GPU concurrency" can mean, and only one is tested here:

1. **Batched inference** (tested here): one call to the model with multiple distinct prompts, so the GPU denoises all of them together across the same steps. This is a real, standard way GPUs gain throughput under load, and it is directly supported by this pipeline for distinct text-to-video prompts.
2. **Independent worker processes**, each handling one request with its own loaded model. Not tested: a single request already peaks at roughly 32-38 GB of VRAM under the CPU offload this setup requires, so more than about two full independent copies would not fit in 80 GB, and this setup has no code to run multiple worker processes against one GPU regardless.
3. **A request-queueing/serving layer** that dynamically batches whatever has arrived so far (the way a production inference server would). Not tested: building or adopting such a server is out of scope for this round; this test's "requests" are decided upfront as a fixed batch, not arriving unpredictably over time.

Every result in this round should be read as "what a batched call of size N costs," not as a full production concurrency benchmark.

## 3. Test design

Same model and settings as rounds 1 and 2: Wan 2.2 T2V-A14B, 832x480, 81 frames at 16 fps (5.0625 s), 27 steps, guidance 3.5 / 4.0, shift 5, CPU offload, bf16. A batched call requires every prompt in the batch to share the same resolution, frame count, and step count, which these settings already satisfy.

Three groups, reusing round 1's exact A1-A4 prompts and seeds so the batch=1 case is directly comparable to already-published data, not a new, differently-worded baseline:

| Group | Batch size | Prompts (round 1 names, same seeds) |
|---|---|---|
| G1 | 1 | A1 (short) |
| G2 | 2 | A1 (short), A2 (median) |
| G3 | 4 | A1 (short), A2 (median), A3 (long, truncated), A4 (non-English) |

G1 is included even though round 1 already measured this exact prompt, because round 1 ran on a different pod; measuring it again in the same session as G2 and G3 gives a same-host, same-run baseline to compare against, which is a stronger basis for "did batching change the cost" than comparing across different pods and days. (Rounds 1 and 2's cost agreed within 1% across different pods, which is reassuring context, but this round does not rely on that holding again.)

## 4. Freezing

Job spec: `round3_groups.json`, built directly from round 1's committed `hour_test_jobs.json` (no new prompt selection). sha256, computed before any job ran:

```
f3e153fccb4c557b332212be365c62050b6bef9a424e2d770bc68a9d86fa2a49
```

## 5. Safeguards specific to this round

This is the first time this pipeline has been asked to batch multiple distinct prompts into one call; nothing about its behavior here is assumed to work correctly until checked.

- **Smoke test before every real (27-step) batched job.** Each real group is preceded by a cheap, few-step batched call at the same batch size. If a batch size fails at the smoke-test stage (most likely from running out of GPU memory), the corresponding real job is skipped, and no worse: if batch=2 fails, batch=4 is not attempted either, since it cannot succeed where a smaller batch already failed.
- **Distinctness check.** Every output in a batch must differ meaningfully from every other output in the same batch (a pixel-difference check between them). A batch that produces two suspiciously near-identical outputs from two different prompts fails this check even if every other automated check passes, since that pattern would indicate a batching bug (for example, the same latent reused across batch slots), not N genuinely independent results. This check was tested against a simulated version of that exact bug before use, and correctly failed it.
- **Same automated gate as rounds 1/2** applied to every individual output (frame count, resolution, not black, not frozen).
- **Independent stop guard**, same as rounds 1/2, reconfigured to watch for this round's process name specifically (an earlier draft of the launch script left it watching for round 1/2's process name by default, which would have made its crash-detection silently ineffective for this round; found and fixed before running).

## 6. What is measured

- Wall time for the whole batched call, at each batch size.
- Cost per video and cost per video-second at each batch size, computed from that wall time (not summed from individual estimates), so it reflects what batching actually costs, not what N separate requests would have cost.
- The ratio of batch=2 and batch=4 cost-per-video-second to batch=1's, measured in the same session.
- Peak VRAM and GPU utilization at each batch size, to see how close batch=4 comes to the 80 GB limit.
- Whether the smoke test catches a real failure at batch=4 (out of memory) before real GPU time is spent on it, or whether batch=4 turns out to fit.

No blind human quality review in this round; rounds 1 and 2 already cover perceptual quality, and this round's question is about throughput, cost, and output correctness (the distinctness check), not comparative quality.

## 7. Budget

Wall time at batch sizes above 1 is genuinely unknown in advance -- that is the question this round answers, not an input to it -- so the estimate below spans the two extremes rather than a single guess. Real behavior will be known from the smoke test's measured per-step time before any real job over 27 steps is committed to.

| Item | Time (best case: near-constant total time regardless of batch size) | Time (worst case: cost scales linearly with batch size, no benefit) |
|---|---|---|
| Setup, preflight, download if needed | ~20 min | ~20 min |
| Warm-up | ~3 min | ~3 min |
| Smoke tests (batch=2 and batch=4, a few steps each) | ~6 min | ~12 min |
| G1 (batch=1, 27 steps) | ~10 min | ~10 min |
| G2 (batch=2, 27 steps) | ~11 min | ~20 min |
| G3 (batch=4, 27 steps) | ~13 min | ~39 min |
| **Total** | **~63 min, about $1.70** | **~104 min, about $2.80** |

Hard stop (independent guard): 100 minutes after launch, plus a 15-minute grace period to finish copying results. Session cap: **$3.50**, to cover the worst case with a small margin. If the smoke tests show batch=4 will not fit or will take too long, it is skipped automatically and the session ends well under this cap.

## 8. Limitations

1. One prompt set, one session, one host -- no repeats at each batch size, so run-to-run variance at a given batch size is not measured, only the difference between batch sizes within this one session.
2. Batch=2 and batch=4 mix different prompts of different lengths within one call; a batch's total time reflects that specific mixture, not a pure "N times the same prompt" measurement. This mirrors how mixed real traffic would actually arrive, which is the more useful number for this project, but it means G2 and G3 are not each other's clean scaled-up repeat.
3. As stated in section 2, this measures one specific meaning of "concurrent load" (batched calls), not independent worker processes or a real queueing server. A result here does not directly predict what a production serving system would achieve.
4. No quality review in this round (see section 6).
5. If G3 is skipped, this round establishes a real VRAM ceiling for batching on this hardware and pipeline configuration, but does not find where between batch=2 and batch=4 that ceiling actually sits.
