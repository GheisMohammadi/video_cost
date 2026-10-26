# Open tools and overlays — test readiness (late 2026)

## GlyphPrinter (was blocked in round 13 — now ready)

- **What:** CVPR 2026 Highlight; R-GDPO for glyph-accurate **image** text rendering. Base: FLUX.1-dev + released stage1/stage2 weights.
- **Release:** Inference code + weights 2026-03-13; training + GlyphCorrector 2026-03-15. GitHub `FudanCVL/GlyphPrinter`, HF `FudanCVL/GlyphPrinter`.
- **Video?** No — T2I / visual text in images. Relevant path: correct still → I2V (same strategy as round 10 §7, with a stronger text image model than hand composite or Qwen-Image-Edit).
- **License:** Confirm in repo before production (FLUX.1-dev has its own terms; GlyphPrinter packaging separately).

## Other open text image tools

- AnyText / AnyText2, Glyph-ByT5 / Glyph-SDXL — image scene-text; usable as still generators, then I2V.
- HunyuanVideo 1.5 — only open **video** model in this project’s tests with a dedicated glyph path that produced verbatim sentences.

## Overlay / post path (production default)

- Round 10–11 clean-plate + SAM 2: already works for exact script; gaps = animated write-on, blotch, marker track license.
- fal auto-caption: speech → subtitles, not whiteboard script placement.
- Market skill pattern: prompt “no text”, then ffmpeg `--overlay-text` for exact strings.

## Ranking for a market-solutions round

1. Hunyuan prompt/capacity follow-ups (highest chance to extend round 13’s partial win).
2. GlyphPrinter still → Wan/Hunyuan I2V (published weights; image-only clarified).
3. Hosted API same-prompt baseline (Seedance / Veo / Kling) if keys exist.
4. Overlay polish (animated reveal) — reliable but was deprioritized vs market generation tools.
