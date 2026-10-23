[← All rounds](../../../README.md)

# Round 13: a fresh solutions search, license no longer a filter (Oct 22-23, 2026)

Status: first result in. HunyuanVideo 1.5, tested against the same frozen customer prompt as rounds 10-12, is the first tool in this entire investigation to render a large fraction of individual words correctly -- still not a working fix, but a real, qualitative step beyond every prior result (pure gibberish in rounds 10-12).

## 1. Summary

- **The search found HunyuanVideo 1.5** (Tencent, open weights, architecturally different from the Wan-based pipeline tested in every round so far) as the strongest new candidate -- it has a dedicated glyph-aware text encoder built into the model specifically to render text correctly, not a post-production trick.
- **First attempt (prose prompt) failed, same as everything else** -- when the real script was described in ordinary prose, the output was garbled gibberish, matching rounds 10-12's pattern exactly.
- **The first attempt was not a fair test.** HunyuanVideo 1.5's own official Prompt Handbook documents that literal on-screen text must be wrapped in quotation marks to engage the glyph-aware encoder -- this was missed initially (found via a secondary source, then verified against the primary handbook) and corrected before drawing any conclusion.
- **Second attempt (quoted text, per the handbook) produced the best text-accuracy result found in this whole project.** A large fraction of individual words are spelled correctly -- "Thousands", "of", "U.S", "advertisers", "are", "filing", "pursuing", "Ad", "Get the facts, fit crit[eria]", "illegalize", "search advertising" all appear exactly as scripted. This is categorically different from rounds 10-12's results, which never produced more than isolated correct words or short strings.
- **It is still not correct.** Word order is scrambled relative to the real script, several words are still garbled or wrong ("Gdvertisers", "Coogle", "mdropolised" for "monopolized"), and the closing URL is wrong ("ADRVAVEBA.COM" instead of "ADREFUNDS.COM"). This is a real improvement in vocabulary accuracy, not a solved problem.

## 2. What was searched

A fresh, license-unconstrained search (per direction: a restrictive license can be bought or negotiated, not a reason to skip a tool), covering:

1. **HunyuanVideo 1.5** -- tested this round, see below.
2. **GlyphPrinter** (CVPR 2026, Fudan/NTU) -- the strongest reported accuracy numbers found in any search this project has done (0.9320 sentence accuracy, English), but no confirmed code/weight release or confirmation it applies to video rather than only images. Not tested this round; still needs that question answered.
3. **Hosted commercial APIs** (Seedance 2.0, Kling 3.0) -- the only semi-independent data found was a review scoring Seedance 2.0 at 3.8/10 for text rendering specifically, with long strings reported to degrade. Not tested this round -- held for a follow-up once API access is confirmed.

See `PLAN.md` for the full search writeup and reasoning behind this prioritization.

## 3. What was run

Both tests used the identical frozen job prompt_id already used in rounds 10-12 (`round10_lawyer_whiteboard`), seed 10001, 832x480, with HunyuanVideo 1.5's own default frame count/fps (121 frames, 24fps -- different from the 81-frame/16fps convention used elsewhere in this project, since this is a different model with its own defaults).

| Test | Prompt format | Result |
|---|---|---|
| v1 | Real script described in prose (no quotes) | Gibberish, same pattern as rounds 10-12 |
| v2 | Real script wrapped in quotation marks, per the official Prompt Handbook (section II.4, "In-Video Bilingual Text Rendering") | Large fraction of individual words correct; word order and some words still wrong |

Model: `hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-480p_t2v`, 50 inference steps, bf16, CPU offload, VAE tiling. Both ran on a rented A100; generation took ~34 minutes per test (2032s and 2040s), plus a one-time ~250s model load.

## 4. Results

### 4.1 v1 (prose prompt): fails, same as every prior round

`clips/hunyuan_v1_prose_prompt.mp4` -- garbled, invented text throughout, no colors, a small logo-like sticker instead of the real Google branding. Direct frame inspection (frames 1, 60, 120 -- `raw/round13_frame{001,060,120}.png`) found no recognizable fragment of the real script. This matches every other result in this project to date.

### 4.2 v2 (quoted prompt): the best text-accuracy result in this project so far

`clips/hunyuan_v2_quoted_prompt.mp4` -- direct frame inspection (frames 1, 60, 120 -- `raw/round13_v2_frame{001,060,120}.png`), transcribed as closely as the handwriting allows:

> Thousands of U.S advertisers are agaimt Gdvertisers are filing refudz.
> Thousandes are pursuing Coogle. Advertisers ar 2-3% 2ounds Ad Spord siacer of
> Federts caue ave rouied Gogally moertiszs, Get the facts, fit criterting.
> Federts he Gogalle illegalize mdropolised search advertising criteria, and Uss
> ADRVAVEBA.COM
> (separately, larger, circled: "Googie")

Real script: "Thousands of U.S. advertisers are pursuing claims against Google. Advertisers are filing refunds for 20-30% of Ad Spend since 2016. Federal courts have ruled Google illegally monopolized search advertising. Get the facts, fit criteria and risks. Use them for your agency or your clients. The Google Advertiser Claims, explained. DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"

Checked word by word against the real script, a large number of words are spelled **exactly correctly**, including multi-word runs: "Thousands of U.S advertisers are", "filing", "pursuing", "Advertisers", "Ad", "Get the facts, fit crit[eria]", "illegalize", "search advertising", "criteria, and". Several more are close misspellings of the right word ("agaimt"/against, "refudz"/refunds, "Coogle"/Google, "mdropolised"/monopolized, "Googie"/Google). The closing URL is wrong ("ADRVAVEBA.COM" vs "ADREFUNDS.COM").

What is still wrong: **word order**. The model has correctly spelled a large fraction of the vocabulary but has not reproduced the sentence structure -- phrases appear shuffled and partially duplicated relative to the script's actual order ("are agaimt Gdvertisers are filing" has "Advertisers" effectively duplicated and out of place). This reads as a model that has learned to render individual words/short phrases as glyphs accurately, but does not yet preserve long-sequence word order reliably -- a different and more specific failure mode than rounds 10-12's results, which showed no real-word recovery at all.

## 5. What this means

- **This is not a working fix** -- the board is still not readable as the real script, and a human reviewer would still catch this as wrong text in QA.
- **It is the first evidence in this whole project that a text-accuracy improvement is possible at the generation stage**, not just via post-production editing (rounds 10-11) or masked-region editing (round 12). A model built with glyph-aware text encoding gets measurably, substantially closer to correct vocabulary than every Wan-based test run so far.
- **The methodology lesson matters as much as the result**: the first attempt with this same model would have been reported as "fails, same as everything else" if the official documentation hadn't been checked before concluding. The gap between "this tool doesn't work" and "this tool wasn't used as documented" was real and specific here, not a formality.
- Next question worth testing: does the word-order problem improve with a different prompt structure (e.g., describing the text as appearing line by line, or breaking the quoted block into smaller quoted phrases), or is it a hard limit of this model's sequence length handling, the same way round 12 found a hard limit on long sentences versus short strings?

## 6. Still to do

1. Test whether restructuring the quoted text (shorter quoted phrases, explicit line breaks) improves word-order accuracy, now that vocabulary accuracy is no longer the dominant failure mode for this model.
2. Resolve GlyphPrinter's applicability question (video vs. image-only, code/weight release) before deciding whether to test it.
3. Test Seedance 2.0 and/or Kling 3.0 via their paid APIs on the same prompt, once API access is confirmed, as a closed-model reference point.
4. Check HunyuanVideo 1.5's license (Tencent Hunyuan Community License Agreement, confirmed by reading the actual `LICENSE` file in the model repo -- not Apache 2.0, which one secondary source incorrectly claimed) for any production use -- the agreement does not apply in the EU, UK, and South Korea, and has its own acceptable-use terms; this needs review before any commercial deployment, separately from this round's testing.

## 7. Files

- `clips/hunyuan_v1_prose_prompt.mp4`: first attempt, prose prompt, fails (section 4.1).
- `clips/hunyuan_v2_quoted_prompt.mp4`: second attempt, quoted prompt per the official handbook -- the best result in this project so far (section 4.2).
- `raw/raw_record_v1.json`, `raw/raw_record_v2.json`: generation records (load time, generation time, sha256) for both tests.
- `raw/round13_frame{001,060,120}.png`: frames from v1 for direct inspection.
- `raw/round13_v2_frame{001,060,120}.png`: frames from v2 for direct inspection.
- `hunyuan_session_v1_prose.py`: the v1 script (prose prompt, no quotes).
- `hunyuan_session_v2_quoted.py`: the v2 script (quoted literal text, per the Prompt Handbook).
- `PLAN.md`: this round's search writeup, frozen before any test ran.

## 8. Cost

Two pod sessions on a rented A100: v1 (~43 minutes including model download and generation) and v2 (~39 minutes, weights not cached between pods since each used a separate fresh pod). Both within this round's approved budget.
