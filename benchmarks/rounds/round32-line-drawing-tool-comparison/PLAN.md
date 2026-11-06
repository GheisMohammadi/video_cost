# Round 32: line-drawing (not text) comparison across 3 top video-gen tools

Boss directive: instead of handwriting text, test drawing straight lines /
simple diagram strokes on a board, and compare 3 of the best tools
currently available rather than sticking to Wan 3.0 alone.

## Prompt (boss-provided, used verbatim, unchanged across all 3 tools)

A realistic, continuous 10-second video of a young Asian woman presenting a
technical diagram on a transparent glass writing board against a matte
black background. Full prompt text stored in `prompt.txt` in this folder.

## Tools selected (via fal.ai, same infra/billing as prior rounds)

Picked from current (Nov 2026) independent rankings of top video-gen
models, not just fal's own promotional picks:

| Tool | fal.ai endpoint | Max duration | Price |
|---|---|---|---|
| Kling 3.0 Pro | `fal-ai/kling-video/v3/pro/text-to-video` | supports 10s | ~$0.112/s (audio off) -> ~$1.12 for 10s |
| Seedance 2.0 (fast) | `bytedance/seedance-2.0/fast/text-to-video` | supports up to 15s, native 10s | ~$0.242/s (720p) -> ~$2.42 for 10s |
| Veo 3.1 | `fal-ai/veo3.1` | capped at 8s (no 10s option) | $0.20/s (720p/1080p, no audio) -> ~$1.60 for 8s |

Sora 2's fal API is being discontinued (shutting down Sep 2026) -- excluded.
Runway/Pika/Luma not tested this round; can add in a follow-up if these 3
don't clearly answer the line-sync question.

Veo 3.1 cannot do a full 10s in one generation (8s cap) -- run it at its
max (8s) and note the duration mismatch in the report rather than trying
to force or stitch it to 10s this round.

## What to check per clip

Same physical-plausibility checks as the whiteboard-text rounds, adapted
for line-drawing:
- Does the yellow line grow progressively under the marker tip, or does it
  appear pre-formed/ahead of the marker?
- Do previously drawn lines stay geometrically fixed (no drift, no
  redraw, no disappearing segments)?
- Hand/wrist/arm anatomy plausibility during the straight-line and
  diagonal strokes.
- Camera stays fixed (no cuts/zooms), per the prompt's explicit requirement.
- Does she only look at camera at the very end, as scripted?

## Budget

~$1.12 (Kling) + ~$2.42 (Seedance) + ~$1.60 (Veo 8s) = ~$5.15 for one
attempt per tool. Retries only if a result is unusable, confirmed with the
user before spending more.
