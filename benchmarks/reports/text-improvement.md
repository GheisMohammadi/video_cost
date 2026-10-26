# On-screen text accuracy — progress report (rounds 10–14)

AI video models usually **cannot write long exact text** on a whiteboard. This report tracks what was tried on one frozen customer prompt, what worked, and what is still open.

---

## TL;DR

| Path | Status | When to use |
|---|---|---|
| **Post-production overlay** (rounds 10–11) | Works today — full script correct | Need guaranteed exact wording |
| **HunyuanVideo 1.5 generation** (rounds 13–14) | Works if you split the script into **~2 short quoted lines per clip** | Prefer text baked into the generation; stitch two clips or accept split boards |
| **One packed prompt / Wan / VACE / Qwen edit** | Still fails on this long script | Not reliable for this use case |

**Latest result:** Isolating the previously-failing lines into their own generation made them largely correct.
---

## The test case (same across all rounds)

- **Prompt:** lawyer explaining a multi-line Google advertiser script on a whiteboard  
- **Requirement:** board text must match the script word for word  
- **Seed:** 10001  
- **Round pages:** [10](../rounds/round10-text-accuracy/) · [11](../rounds/round11-sam2-board-tracking/) · [12](../rounds/round12-vace-qwen-text-fix/) · [13](../rounds/round13-new-solutions-search/) · [14](../rounds/round14-hunyuan-glyphprinter-apis/)

After round 11, direction shifted from building custom research fixes to evaluating **published / market** tools on this same prompt.

---

## Timeline at a glance

| Round | Approach | Result in one line |
|---|---|---|
| **10** | Wan 2.2 generate + hand-built text overlay | Generation fails; overlay makes text correct |
| **11** | SAM 2 board tracking for the overlay | Overlay smoother / more general; write-on animation still open |
| **12** | Market editors (VACE, Qwen-Image-Edit) | They edit the board; long text still wrong |
| **13** | HunyuanVideo 1.5 (glyph-aware model) | First exact sentences; later lines in same clip degrade |
| **14** | Hunyuan follow-up: fewer quotes per clip | Isolation recovers failing lines; full board needs two gens |

---

## Round-by-round

### Round 10 — prove the failure, build the overlay

Same prompt on best (27-step) and cheapest (4-step LoRA) Wan configs.

| Clip | Result |
|---|---|
| [config A — plain 27-step](../rounds/round10-text-accuracy/clips/configA_plain27.mp4) | Garbled board text; board visually stable |
| [config B — 4-step LoRA](../rounds/round10-text-accuracy/clips/configB_lora4step.mp4) | Same text failure; board goes semi-transparent later |
| [overlay v1](../rounds/round10-text-accuracy/clips/overlay_prototype.mp4) | Real script pasted on; subject in front (flat board fill) |
| [overlay v2 — clean plate](../rounds/round10-text-accuracy/clips/overlay_prototype_v2_cleanplate.mp4) | Same correct text + real board lighting |
| [I2V from corrected frame](../rounds/round10-text-accuracy/clips/i2v_from_correct_frame.mp4) | Partial only — text drifts in motion |

**Left open:** static text (not written live); edge jitter; board = “not the person” only.

---

### Round 11 — harden the overlay (SAM 2)

Replaced per-frame person masks with SAM 2 video tracking of the board.

| Clip | Result |
|---|---|
| [final composite](../rounds/round11-sam2-board-tracking/clips/final_composite.mp4) | Correct script kept; ~1.5% frame-to-frame mask change; board tracked as its own region |

**Left open:** animated marker write-on; clean-plate color blotch; strongest marker tracker (CoTracker3) noncommercial-only.

---

### Round 12 — market edit tools

| Clip / asset | Result |
|---|---|
| [VACE v1](../rounds/round12-vace-qwen-text-fix/clips/test_a_vace_v1.mp4) | No visible edit (setup mistake: original pixels left in edit region) |
| [VACE retry](../rounds/round12-vace-qwen-text-fix/clips/test_a_vace_retry.mp4) | Board rewritten; long sentences still wrong; `ADREFUNDS.COM` exact |
| [Qwen-Image-Edit](../rounds/round12-vace-qwen-text-fix/clips/test_b_qwen_edit.png) | Text changed; still wrong |

**Takeaway:** edit tools can touch the board; they do not solve long exact copy.

---

### Round 13 — HunyuanVideo 1.5 (first exact sentences)

Glyph-aware model. On-screen text must be in **quotation marks** (model handbook).

| Clip | Prompt | Result |
|---|---|---|
| [v1 — prose](../rounds/round13-new-solutions-search/clips/hunyuan_v1_prose_prompt.mp4) | No quotes | Gibberish |
| [v2 — one long quote](../rounds/round13-new-solutions-search/clips/hunyuan_v2_quoted_prompt.mp4) | Whole script in one quote | Words often right; order scrambled |
| [v3 — short quoted lines](../rounds/round13-new-solutions-search/clips/hunyuan_v3_split_lines.mp4) | Five separate short quotes | **Lines 1–2 exact**; lines 3–5 degrade |

**Open into round 14:** is later-line failure “hard sentences,” or too many quotes in one generation?

---

### Round 14 — Hunyuan isolation (latest)

Same model and script. Three tests:

| Clip | What was asked | Result |
|---|---|---|
| [A1 — two lines only](../rounds/round14-hunyuan-glyphprinter-apis/clips/hunyuan_A1_two_lines.mp4) | Only lines 1–2 (the ones exact in round 13) | Near-exact (L2: `20-3%` vs script `20-30%`) |
| [A2 — deferred lines only](../rounds/round14-hunyuan-glyphprinter-apis/clips/hunyuan_A2_deferred_lines.mp4) | Only lines 3–5 (the ones that failed in round 13) | **Largely correct** when alone |
| [A3 — five quotes, reordered](../rounds/round14-hunyuan-glyphprinter-apis/clips/hunyuan_A3_reorder.mp4) | All five quotes, failing lines first | Still degrades (same class as round 13 v3) |

**What round 14 proves**

1. Round 13’s later-line failures were mainly **too many quotes per generation**, not impossible sentences.  
2. The full customer script is reachable with **two short-quote Hunyuan clips** (A1 + A2).  
3. A single five-quote generation is still not reliable (A3).

**Deferred this round:** GlyphPrinter→I2V and hosted APIs (Seedance / Veo / Kling) — no API keys; GlyphPrinter left for a later session.

---

## What works today vs what is still open

### Works

1. **Overlay path** — exact full script ([round 10 v2](../rounds/round10-text-accuracy/clips/overlay_prototype_v2_cleanplate.mp4), [round 11](../rounds/round11-sam2-board-tracking/clips/final_composite.mp4)).  
2. **Hunyuan split-generation path** — ~2 quoted lines per clip ([A1](../rounds/round14-hunyuan-glyphprinter-apis/clips/hunyuan_A1_two_lines.mp4) + [A2](../rounds/round14-hunyuan-glyphprinter-apis/clips/hunyuan_A2_deferred_lines.mp4)).  
3. **Prompt rule for Hunyuan** — put on-screen text in quotes; keep each quote short.

### Still open

1. **One-shot full board** in a single generation.  
2. **Animated write-on** (marker-timed reveal) on the overlay path.  
3. **Clean-plate blotch** on overlay reconstruction.  
4. **Hunyuan license** review before commercial deploy (Tencent community license).  
5. **Hosted API baselines** and **GlyphPrinter→I2V** not yet run on this prompt.

---

## Suggested watch order (5 minutes)

1. Failure: [Wan config A](../rounds/round10-text-accuracy/clips/configA_plain27.mp4)  
2. Overlay fix: [clean plate](../rounds/round10-text-accuracy/clips/overlay_prototype_v2_cleanplate.mp4)  
3. First exact sentences: [Hunyuan v3](../rounds/round13-new-solutions-search/clips/hunyuan_v3_split_lines.mp4)  
4. Round 14 isolation win: [A1](../rounds/round14-hunyuan-glyphprinter-apis/clips/hunyuan_A1_two_lines.mp4) → [A2](../rounds/round14-hunyuan-glyphprinter-apis/clips/hunyuan_A2_deferred_lines.mp4)  
5. Still broken if packed: [A3](../rounds/round14-hunyuan-glyphprinter-apis/clips/hunyuan_A3_reorder.mp4)
