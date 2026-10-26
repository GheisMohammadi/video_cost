# Industry text in video fixes

Research for Round 14 planning (Oct 26, 2026). Full notes under `research_notes/Industry text in video fixes/`.

## What industry does

1. **Short on-screen text (title cards, neon, “SALE 30%”):** several hosted models now often succeed (Seedance 2.0, Veo 3.1, Hailuo/MiniMax H3; Kling improved in 4.0). Public benches almost never use multi-sentence whiteboard scripts.
2. **Long exact copy:** production default is still **do not ask the model to paint the letters** — generate the scene, then overlay real text (editors / ffmpeg). fal auto-caption is speech→subtitles, not a supplied board script.
3. **Generation-time glyph models:** HunyuanVideo 1.5 (video + ByT5 glyph path) and GlyphPrinter (image, CVPR 2026, **code+weights now public**) are the concrete published options closest to this project’s problem.

## What changed since round 13’s open list

| Item | Status now |
|---|---|
| Hunyuan: fewer quotes / isolate failing lines | Still the highest-leverage untested follow-up |
| GlyphPrinter image vs video / release | **Resolved:** image-only T2I; inference + weights released Mar 2026 |
| Seedance / Kling same-prompt baseline | Still untested here; short-text benches look stronger than round 13’s long-script bar |
| Overlay animated reveal | Still open; industry-aligned but deprioritized vs market generation tools |

## Recommended Round 14 shape

**Primary (pod):** (A) Hunyuan two-line / deferred-line / reorder tests on the frozen script; (B) GlyphPrinter correct still → I2V on the same script.

**Secondary (no/low pod):** same frozen prompt on Seedance 2.0 and one of Veo 3.1 Fast / Kling 4.0 if API access exists.

**Ops:** independent stop guard + stop pod after pull; do not leave the session billing.

Win criteria: more than two verbatim sentences on one board, or a GlyphPrinter→I2V path that keeps the full script correct through motion; API clips as closed-model reference either way.
