# Round 5 test design: cost of fal's default frame-interpolation step

Status: scripts written; the gate logic (including a check specific to this round) tested against synthetic data; the actual interpolation model has not been exercised on a GPU yet. This is List6 item 4. Frozen before running.

## 1. Question

Every cost figure from rounds 1-4 is an explicit lower bound against fal's price, because fal's default request includes a FILM frame-interpolation post-processing pass (`benchmarks/fal_wan22_config.md`: `interpolator_model=film`, `num_interpolated_frames=1`, `adjust_fps_for_interpolation=true`) that this project never implemented. This round measures that missing step directly, using a real PyTorch port of the FILM model (Apache-2.0, [dajes/frame-interpolation-pytorch](https://github.com/dajes/frame-interpolation-pytorch)) -- matching fal's documented default algorithm, not a substitute -- so the "lower bound" caveat can be replaced with an actual number.

## 2. What this does and does not need

This step does not need a fresh Wan generation. It takes already-generated clips as input and measures only the interpolation pass added on top of each clip's already-published generation cost: round 1's existing four 480p clips, and round 6's four 720p clips generated in the same pod session. This makes it a cheap addition to round 6's session rather than a full session of its own, and it directly answers "how much does this add" rather than re-measuring generation cost that is already known.

Interpolation math, matching fal's stated defaults: for N input frames, one interpolated frame is inserted at the midpoint of every consecutive pair, giving 2N-1 total frames; output fps is scaled by the same factor to hold duration constant rather than lengthening the clip. For round 1/6's 81-frame clips: 161 output frames.

## 3. Safeguards, since the model has never been run in this pipeline before

- **Preflight**: CUDA available, model cache not on a network filesystem.
- **Model download**: the FILM model (`film_net_fp16.pt`, 69 MB, from the project's GitHub releases) is fetched once and verified to be a real file (not a truncated or failed download) before use.
- **Smoke test on 6 frames of the first clip only**, before spending time on full clips: checks the input/output tensor format assumption (normalized 0-1 float, matching the model's documented convention) produces a plausible result. If this fails, nothing further runs, and it is reported as a finding, not silently worked around.
- **A gate check specific to this round**: every interpolated (odd-indexed) frame must lie between its two neighboring original frames in average pixel value, and not equal either one. This was tested against two concrete failure modes before use -- a duplicated-neighbor bug and unrelated-noise output -- and correctly caught both, alongside the existing frame-count/black/frozen checks reused from every other round.

## 4. Combined pod session with round 6

Runs on the same pod as round 6, after round 6's clips exist (see round 6's `PLAN.md`, section 4, for the shared procedure). Inputs: round 1's four existing 480p clips (uploaded from this machine) and round 6's four freshly-generated 720p clips (already on the pod, referenced by path, no re-upload needed). Frozen input manifest: `inputs_combined.json`, sha256 `314c47700fd415d89c42766661d8b60221216e683cb938b1f91809d8958230b2`.

## 5. What is measured

Per clip: interpolation wall time, peak VRAM, and the added cost per video-second on top of that clip's already-known generation cost -- giving a combined "generation + interpolation" figure to compare against fal's price directly, at both 480p and 720p (a bonus from running both legs in one session: whether interpolation cost scales with resolution, or is roughly fixed per frame-pair regardless of frame size, is visible from the comparison rather than assumed).

## 6. Budget

Interpolation speed for this specific model and port has not been measured before, so this is a rough estimate, corrected by the smoke test's real per-frame-pair timing before the full run is committed to:

| Item | Estimate |
|---|---|
| Model download (69 MB) | under 1 min |
| Smoke test | under 1 min |
| 4 clips at 480p (80 frame-pairs each) | ~10-15 min, rough |
| 4 clips at 720p (80 frame-pairs each, larger resolution) | ~15-25 min, rough |
| **Total** | **~30-40 min, about $0.80-1.10** |

This is added to round 6's budget as part of the same pod session (see round 6's `PLAN.md`, section 5); combined session total is estimated at about $6.20-6.50.

## 7. Limitations

1. FILM is one interpolation algorithm; fal's actual runtime cost for its own deployment of the same algorithm is not independently knowable, only approximated by running a real, correctly-matched implementation ourselves.
2. Four clips per resolution, one run each -- no repeats to measure interpolation-time variance.
3. No perceptual quality check of the interpolated motion itself (smoothness, artifacts) beyond the automated gate; this round answers a cost question, not a quality one.
