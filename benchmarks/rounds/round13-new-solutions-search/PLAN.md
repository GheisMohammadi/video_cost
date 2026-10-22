[← All rounds](../../../README.md)

# Round 13 plan: a fresh search for text-accuracy solutions, license no longer a filter

Status: planned, not yet run.

## Why this round

After round 12 (VACE, Qwen-Image-Edit -- both failed on the actual customer prompt, same as every tool tested since round 10), direction from the boss: search again, this time without ruling anything out over licensing -- a restrictive license can be bought out or negotiated with the team behind it, so it should not stop a tool from being considered. This round is a fresh literature/tool search under that relaxed constraint, followed by testing whatever looks most promising.

## What was found

Ranked by how directly it targets this project's actual problem (long, exact, multi-sentence text in a generated video) and how ready it is to test:

### 1. HunyuanVideo 1.5 -- highest priority, ready to test now

An open-weight text-to-video model from Tencent (released Nov 20, 2025), architecturally different from everything tested so far in this project (Wan-based: rounds 1-12 are all Wan 2.2/2.1). Its distinguishing feature for this problem: **glyph-aware text encoding**, built into the model via a Glyph-ByT5 text encoder specifically to help it understand and render text correctly, in both English and Chinese. This is a generation-time fix, not a post-production inpainting trick like round 10-12's work -- it's a different bet: that a model built from the ground up with text rendering in mind does better than one (Wan) that was not.

- Weights are public, with native ComfyUI support and a dedicated `HunyuanVideo Glyph by T5` node already available in the community.
- License is unclear from this search: one source lists Apache 2.0, another lists a custom "Tencent Hunyuan Community License Agreement" (generally commercial-use-permitting but with regional restrictions). Needs checking directly in the repo's `LICENSE` file before any production use, but per this round's direction, that is a negotiation/cost question, not a reason to skip testing it.
- No independent test of its text accuracy against Wan or any other model was found -- every claim found is either a vendor demo or absent entirely. This project would be producing new information by testing it directly, not confirming something already known.

### 2. Hosted commercial APIs (Seedance 2.0, Kling 3.0) -- cheap, fast, worth a direct comparison point

No infrastructure needed -- these are paid APIs, callable directly, no pod required. Worth a small, direct test now that license/cost is not a blocker (these are commercial from the start; the question is just whether to pay for API calls, not whether the license permits use).

- The only semi-independent accuracy data found: a review scoring Seedance 2.0 at 3.8/10 for text rendering specifically, noting "short overlays and simple title cards can work... but longer strings degrade quickly" and that characters can warp/flicker once the camera or subject moves. This is a third-party review, not a controlled test, and not run against this project's actual prompt.
- No text-accuracy data found for Kling 3.0 at all.
- Value of testing: a real, controlled data point (same prompt, same seed where possible) for "do the best-funded closed models actually do better," instead of relying on reviews. Low cost, fast to run, no pod setup.

### 3. GlyphPrinter -- promising numbers, unclear applicability, needs more digging before spending anything on it

A CVPR 2026 paper (Fudan University / NTU, arXiv 2603.15616, March 2026) reporting strong results: 0.9851 normalized edit distance and 0.9320 sentence accuracy on English text rendering, beating AnyText2, Glyph-ByT5-v2, X-Omni, and Qwen-Image in its own benchmark. The best raw accuracy numbers found in any search this project has done.

- **Not yet confirmed to apply to video** -- the method (Region-Grouped Direct Preference Optimization, a fine-tuning technique) and its comparisons are against image-generation baselines (AnyText2, Qwen-Image), not video models. It may be an image-only technique, which would make it relevant to round 10/11's "generate a correct starting frame" approach (I2V from a correct frame) rather than a direct video fix.
- **No code or weight release confirmed** -- searches for a GitHub repo or Hugging Face page under the project's name or the authors' names found nothing. The project page URL (`henghuiding.com/GlyphPrinter`) was referenced in the paper's metadata but not independently verified reachable or populated with a release.
- Before spending any time or pod budget on this one, it needs: confirming the project page actually has released code/weights, and confirming whether it's an image or video method. Not ready to test yet, unlike the other two.

## What will be tested this round

1. **HunyuanVideo 1.5** against the identical frozen customer prompt used in rounds 10-12 (prompt_id `round10_lawyer_whiteboard`, seed 10001 where the model's sampler allows it) -- a genuinely new base model, not a post-production trick.
2. **Seedance 2.0 and/or Kling 3.0** via their paid APIs, same prompt, as a direct closed-model reference point.
3. GlyphPrinter is **not** tested this round -- it needs the applicability/release questions above answered first. If it turns out to be image-only, it folds into round 10/11's starting-frame approach as a possible upgrade over the hand-built clean-plate compositing, not a new round of its own.

## What would make this a win

- HunyuanVideo 1.5 renders the real script, or even visibly more of it correctly than Wan does, in a way that's reproducible -- would be the first generation-time improvement found in this whole investigation (rounds 10-12 only found post-production and editing approaches, none of which fully worked either).
- A closed API renders it correctly -- would tell the team this is solvable today by using a different vendor for text-heavy clips, even if self-hosting remains cheaper for everything else (this project's original cost-focus finding, rounds 1-9).

## What would not be a win (expected failure modes to watch for)

- HunyuanVideo 1.5's glyph-aware encoding was demonstrated publicly only on short signage (a neon sign in one demo), not long multi-sentence scripts like this project's actual customer prompt -- it may do better on short text and still fail on long text, the same pattern already seen in round 12's VACE retry (`ADREFUNDS.COM` rendered correctly, the surrounding sentence did not).
- Seedance 2.0's own review already predicts long-string degradation -- a repeat of every other result in this project would not be surprising, but running it on this exact prompt turns a review's claim into this project's own verified data point either way.

## Resources needed

- A RunPod A100 pod (or equivalent) for HunyuanVideo 1.5 -- 8.3B parameters, should fit comfortably given round 12's VACE-14B ran fine on the same hardware.
- API keys/billing access for Seedance 2.0 and/or Kling 3.0, if testing those -- need to check which the project already has access to or whether new accounts/payment are needed.
- Budget: default under $10 for the pod portion unless told otherwise; API call costs are typically a few cents to low dollars per video and should be confirmed per-vendor before running.

## Steps

1. Get a pod for HunyuanVideo 1.5 (or confirm an existing one can be reused).
2. Verify the model's actual license file in its repo before running (not relying on the conflicting secondary sources found in this search).
3. Run the identical frozen lawyer/whiteboard prompt through HunyuanVideo 1.5, direct frame-by-frame inspection against the real script (same method as every prior round -- no automated accuracy claim without it).
4. Check API access for Seedance 2.0 / Kling 3.0; if available, run the same prompt through whichever is accessible.
5. Write the round 13 report: results table, sha256-verified clips, honest comparison against rounds 10-12's results, and resolve the GlyphPrinter applicability question (even if the answer is "not tested this round, here's why") before closing out.

## Files (once run)

- `clips/`: HunyuanVideo 1.5's output, and any API-sourced clips.
- `raw/`: generation records for each test.
- `README.md`: the full report, written after results are in -- not before.
