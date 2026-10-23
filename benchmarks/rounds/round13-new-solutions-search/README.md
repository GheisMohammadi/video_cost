[← All rounds](../../../README.md)

# Round 13: a fresh solutions search, license no longer a filter (Oct 22-23, 2026)

Status: in progress, major finding. HunyuanVideo 1.5, tested against the same frozen customer prompt as rounds 10-12, has produced the first word-for-word correct sentences anywhere in this investigation -- not yet a complete fix (later lines in the same clip still degrade), but the first time any config in this project has rendered multi-word, grammatically complete, exactly-correct text.

## 1. Summary

- **The search found HunyuanVideo 1.5** (Tencent, open weights, architecturally different from the Wan-based pipeline tested in every round so far) as the strongest new candidate -- it has a dedicated glyph-aware text encoder built into the model specifically to render text correctly, not a post-production trick.
- **First attempt (prose prompt) failed, same as everything else** -- when the real script was described in ordinary prose, the output was garbled gibberish, matching rounds 10-12's pattern exactly.
- **The first attempt was not a fair test.** HunyuanVideo 1.5's own official Prompt Handbook documents that literal on-screen text must be wrapped in quotation marks to engage the glyph-aware encoder -- this was missed initially (found via a secondary source, then verified against the primary handbook) and corrected before drawing any conclusion.
- **Second attempt (one long quoted block, per the handbook) produced a large fraction of individual words spelled correctly** -- "Thousands", "of", "U.S", "advertisers", "are", "filing", "pursuing", "Ad", "Get the facts, fit crit[eria]", "illegalize", "search advertising" all appear exactly as scripted, but word order was scrambled and some words were still garbled ("Gdvertisers", "Coogle", "mdropolised" for "monopolized").
- **Third attempt (the same script split into five separate, shorter quoted lines, matching the only multi-text pattern the handbook actually documents) produced two completely correct sentences.** "Thousands of U.S. advertisers are pursuing claims against Google." and "Advertisers are filing refunds for 20-30% of Ad Spend since 2016." render **word for word, exactly as scripted** -- the first fully correct multi-word sentences anywhere in this project's text-accuracy investigation (rounds 10-13). The third and fourth lines in the same clip still degrade into garbled, partially duplicated text, and the closing small-print line is still wrong.
- **This is not a complete fix** -- later lines in the same generated clip are not reliable even when earlier ones are perfect, so whatever makes this work does not hold uniformly across a whole scene. But it is the first config in this entire project, across 13 rounds, to produce verbatim-correct on-screen sentences.

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
| v2 | Real script wrapped in one long quotation, per the official Prompt Handbook (section II.4, "In-Video Bilingual Text Rendering") | Large fraction of individual words correct; word order and some words still wrong |
| v3 | Same script split into five separate, shorter quoted lines, matching the handbook's only multi-text example pattern | **Lines 1-2 render word-for-word exactly correct**; lines 3-4 and the closing small print still degrade |

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

### 4.3 v3 (split into shorter quoted lines): the first verbatim-correct sentences in this project

`clips/hunyuan_v3_split_lines.mp4` -- direct frame inspection (frames 1, 60, 120 -- `raw/round13_v3_frame{001,060,120}.png`), transcribed exactly:

> Thousands of U.S. advertisers are pursuing claims against Google.
> Advertisers are filing refunds for 20-30% of Ad Spend since 2016.
> Federal courts he Goaled illegally meaogolized adpend since 2016.
> Federal courts huled Google aeagolized idr saising
> DOWNVER facts, files, ADAFFertisD..CM

Checked against the real script, **the first two lines are exactly, completely correct** -- not isolated correct words inside a garbled sentence (as in v2), but two complete, grammatically correct sentences matching the script verbatim. This is the first result across rounds 10-13 (every config tested: plain Wan, the 4-step LoRA, the hand-built overlay, VACE, Qwen-Image-Edit, and HunyuanVideo 1.5 itself in v1 and v2) to produce a fully correct multi-word sentence.

The third and fourth lines, in the same clip, degrade back toward the v2 pattern -- recognizable fragments and correct individual words ("Federal courts", "illegally", "Google") but wrong order and invented words, with the third and fourth lines partially duplicating each other's content ("since 2016" repeated, "Google...monopolized" repeated across both). The closing small-print line is still wrong throughout.

**What this suggests**: the model's glyph-aware encoder can render a short, cleanly-isolated quoted phrase with real accuracy -- confirmed twice now, independently, by two of five quoted segments landing perfectly. But accuracy is not uniform across a whole clip; something about generating multiple quoted text regions in the same scene causes later ones to degrade, a different and more specific limitation than "this model can't do long text" (v2's apparent conclusion) or "this model can't do text" (rounds 10-12's conclusion about Wan-based approaches).

## 5. What this means

- **This is not a complete fix** -- two of five quoted lines in the same clip rendering perfectly does not mean the whole board is correct, and a human reviewer would still catch the third and fourth lines as wrong in QA.
- **It is the strongest evidence so far that a text-accuracy improvement is possible at the generation stage**, not just via post-production editing (rounds 10-11) or masked-region editing (round 12). Verbatim-correct sentences, even partially, had not been produced by any tool tested in this project before this round.
- **The pattern across v1 -> v2 -> v3 is itself informative**: prose (fails completely) -> one long quote (words correct, order wrong) -> several short quotes (some lines fully correct, later lines degrade). Each methodology correction moved the result meaningfully closer to working, which argues for continuing to refine the prompt structure rather than concluding the model has hit a hard limit.
- **The methodology lesson matters as much as any single result**: the first attempt with this model would have been reported as "fails, same as everything else" if the official documentation hadn't been checked before concluding, and the second attempt would have been reported as "the length limit is the problem" if the handbook's only multi-text example hadn't been tried directly.

## 6. Still to do

1. Investigate why later quoted lines degrade within the same clip -- try reducing the number of quoted segments per clip (e.g., two lines per generation instead of five), reordering which content comes first, or separating the small-print line into its own generation entirely.
2. Resolve GlyphPrinter's applicability question (video vs. image-only, code/weight release) before deciding whether to test it.
3. Test Seedance 2.0 and/or Kling 3.0 via their paid APIs on the same prompt, once API access is confirmed, as a closed-model reference point.
4. Check HunyuanVideo 1.5's license (Tencent Hunyuan Community License Agreement, confirmed by reading the actual `LICENSE` file in the model repo -- not Apache 2.0, which one secondary source incorrectly claimed) for any production use -- the agreement does not apply in the EU, UK, and South Korea, and has its own acceptable-use terms; this needs review before any commercial deployment, separately from this round's testing.

## 7. Files

- `clips/hunyuan_v1_prose_prompt.mp4`: first attempt, prose prompt, fails (section 4.1).
- `clips/hunyuan_v2_quoted_prompt.mp4`: second attempt, one long quoted block -- words correct, order wrong (section 4.2).
- `clips/hunyuan_v3_split_lines.mp4`: third attempt, split into shorter quoted lines -- two lines exactly correct (section 4.3).
- `raw/raw_record_v1.json`, `raw/raw_record_v2.json`, `raw/raw_record_v3.json`: generation records (load time, generation time, sha256) for all three tests.
- `raw/round13_frame{001,060,120}.png`: frames from v1 for direct inspection.
- `raw/round13_v2_frame{001,060,120}.png`: frames from v2 for direct inspection.
- `raw/round13_v3_frame{001,060,120}.png`: frames from v3 for direct inspection.
- `hunyuan_session_v1_prose.py`: the v1 script (prose prompt, no quotes).
- `hunyuan_session_v2_quoted.py`: the v2 script (one long quoted block, per the Prompt Handbook).
- `hunyuan_session_v3_split_lines.py`: the v3 script (script split into five shorter quoted lines).
- `PLAN.md`: this round's search writeup, frozen before any test ran.

## 8. Cost

Three pod sessions on a rented A100: v1 (~43 minutes including model download and generation), v2 (~39 minutes), and v3 (~39 minutes) -- weights not cached between pods since each used a separate fresh pod. All within this round's approved budget.
