# HunyuanVideo 1.5 — continuation options after round 13

## Verified facts from docs / community nodes

- Quoted strings engage Glyph-ByT5; unquoted prose does not (Prompt Handbook § In-Video Bilingual Text Rendering). Official demos are short signage (“hunyuan”, “Hunyuan Video 1.5”), not multi-sentence boards.
- ComfyUI `HyVideo15GlyphByT5`: extracts `"..."` / `“...”`; community note: short high-contrast text works far better than long sentences; 480p limits typography crispness.
- `byt5_max_length` defaults to **256** in Comfy loaders — total quoted payload across many lines can stress or truncate the glyph path.
- I2V rewrite rules (Tencent): keep quoted text intact; do not spell letter-by-letter in the prompt.

## Round 13 result pattern to exploit

| Attempt | Pattern | Outcome |
|---|---|---|
| v1 prose | no quotes | fail |
| v2 one long quote | ~full script in one quote | words often right, order wrong |
| v3 five short quotes | handbook multi-text style | lines 1–2 exact; 3–4+ degrade |

Open tests that stay within “use published model correctly,” not new research:

1. **Two-line clip only** — generate only the two sentences that already succeeded; measure repeatability (same seed + new seeds).
2. **Deferred lines** — separate generation with only lines 3–4 (+ small print); see if isolation restores accuracy.
3. **Stitch / dual-board** — if (1) and (2) both succeed, composite or cut so the full script appears without asking one generation for five quotes.
4. **Reorder** — put previously failing lines first; check whether degradation is position/capacity vs content.
5. **Fewer quotes + smaller print separate** — four body lines in one clip vs small-print URL in another.

## License (already checked in round 13)

Tencent Hunyuan Community License Agreement (not Apache 2.0). Geographic / acceptable-use review before commercial deploy; testing OK under current project direction.
