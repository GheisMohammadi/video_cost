[← All rounds](../../../README.md)

# Round 14: Hunyuan quote-isolation follow-ups (Oct 26, 2026)

Status: **complete for tests A1–A3**. GlyphPrinter→I2V (B) and hosted-API baselines (C) deferred — see section 6. Pod `runpod20` stopped after verified pull.

## Watch the clips

A1 — only the two lines that were exact in round 13 v3:

<video src="clips/hunyuan_A1_two_lines.mp4" controls width="420"></video>

A2 — only the lines that degraded in round 13 v3 (isolated):

<video src="clips/hunyuan_A2_deferred_lines.mp4" controls width="420"></video>

A3 — same five quotes as round 13 v3, failing lines first:

<video src="clips/hunyuan_A3_reorder.mp4" controls width="420"></video>

## 1. Summary

- **Isolation fixes the lines round 13 lost.** When lines 3–4 + small print are the only quoted text in the prompt (A2), they render largely correct — the same content that garbled when packed with five quotes in round 13 v3. Quote count / glyph-path capacity, not “hard” sentences, was the main failure mode.
- **A1 confirms the two previously-correct lines stay correct (near-verbatim) alone.** Line 1 matches the script. Line 2 is exact except `20-3%` instead of `20-30%` (one missing digit). Minor late-clip occlusion/cropping where the arm crosses the board.
- **A3 (reorder, five quotes) still degrades** — paraphrases, duplicates, wrong URL — same class of failure as round 13 v3. Putting previously-failing lines first does not unlock a full five-line board in one generation.
- **Practical generation pattern:** split the customer script across **two Hunyuan generations** (≈2 quoted lines each), then combine in edit — stronger than one five-quote shot. Still weaker than rounds 10–11 overlay for guaranteed full-script accuracy, but the first clear generation-time path to the whole board.

## 2. What was run

| Item | Value |
|---|---|
| Model | `hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-480p_t2v` |
| Pod | `server/runpod20.txt` (A100-SXM4-80GB), one session, one model load |
| Seed | 10001 |
| Settings | 832×480, 121 frames, 24 fps, 50 steps (same as round 13) |
| Load | 52.7 s (weights already local after fetch) |
| Guard | `HARD_S=9000`, `PROC_PATTERN=[r]ound14_hunyuan_session` |

| Job | Prompt structure | Generate s | sha256 |
|---|---|---|---|
| A1 | Quoted L1 + L2 only | 2024.4 | `97a12805…e21cc6` |
| A2 | Quoted L3 + L4 + L5 only | 2029.3 | `10960a7d…b5f6c093` |
| A3 | Five quotes, order L3,L4,L1,L2,L5 | 2030.3 | `68d0dacc…9f56f6d` |

## 3. Frame inspection vs script

Target script lines:

1. Thousands of U.S. advertisers are pursuing claims against Google.
2. Advertisers are filing refunds for 20-30% of Ad Spend since 2016.
3. Federal courts have ruled Google illegally monopolized search advertising.
4. Get the facts, fit criteria and risks.
5. DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM

### A1 (`raw/A1_frame{001,060,120}.png`)

| Line | Assessment |
|---|---|
| L1 | Exact in early/mid frames |
| L2 | Exact except `20-3%` vs `20-30%` |
| Notes | Late frames: arm can crop the end of L1; text remains readable |

### A2 (`raw/A2_frame{001,060,120}.png`)

| Line | Assessment |
|---|---|
| L3 | Correct content (often wrapped onto two visual lines) |
| L4 | Exact |
| L5 | Near-exact (`ADREFUNDS.COM` correct; casing/spacing on “File”/“FILE” varies) |
| Notes | Marker/hand can smudge a word mid-clip; overall far better than round 13 v3’s lines 3–5 |

### A3 (`raw/A3_frame{001,060,120}.png`)

Full five-quote board still fails QA: shortened/paraphrased sentences, duplicated “Thousands…” content, wrong/garbled URL (`ADVERFFUNDS.COM` and similar). Reordering does not solve multi-quote overload.

## 4. What this means

| Question | Answer |
|---|---|
| Can Hunyuan render the “hard” lines? | Yes, when they are not competing with many other quoted regions (A2). |
| Can one generation hold the full board? | Not reliably (A3 = round 13 v3 pattern). |
| Production implication | Prefer **two short-quote Hunyuan clips** (or overlay from rounds 10–11) over one packed prompt. |

## 5. Cost / ops

Single A100 session: load + three generations ≈ 52 s + 3×~2030 s ≈ **1.7 hours** busy GPU time, then stop. Pod stop confirmed after pull (`runpodctl stop`; connectivity probe no longer returned alive). Independent guard was armed (`hard=9000s`); session finished before the hard deadline.

## 6. Deferred (planned, not run this session)

| ID | Why deferred |
|---|---|
| B GlyphPrinter → I2V | A1–A2 already answered the round’s main Hunyuan question; GlyphPrinter needs FLUX weights + upstream condition setup — separate session if still wanted |
| C Seedance / Veo / Kling | No API keys provided for this round |

## 7. Files

- `PLAN.md` — frozen before the run
- `clips/hunyuan_A{1,2,3}_*.mp4` — sha256-verified pulls
- `raw/raw_record_A*.json`, `raw/session.json`, `raw/jobs.jsonl`, `raw/session.log`
- `raw/A{1,2,3}_frame{001,060,120}.png` — inspection frames
- `round14_hunyuan_session.py`, `run_round14.sh` — pod runner
