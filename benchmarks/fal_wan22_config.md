# fal.ai Wan 2.2 A14B: request spec to match

Source: fal raw OpenAPI schema (`https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=fal-ai/wan/v2.2-a14b/text-to-video`) and the model pages, checked 2026-09-19. Prices come from the model page and can change.

## Endpoints and prices

| Endpoint | Price | Notes |
|---|---|---|
| `fal-ai/wan/v2.2-a14b/text-to-video` (standard) | $0.08 / $0.06 / $0.04 per video second at 720p / 580p / 480p | Video seconds are counted at 16 fps. Default 81 frames is about 5.06 s, so about $0.40 at 720p. |
| `fal-ai/wan/v2.2-a14b/text-to-video/turbo` | $0.10 / $0.075 / $0.05 **per video** at 720p / 580p / 480p | Flat per video. Schema has no steps, frames or guidance parameters, so it is a fixed pipeline (likely distilled). About $0.02 per second if 5 s. Not matched yet. |
| `fal-ai/wan/v2.2-5b/text-to-video` | not checked | 5B variant, different model. |

## Standard request defaults (what we match)

| Parameter | Default | Range or values |
|---|---|---|
| resolution | 720p | 480p, 580p, 720p |
| aspect_ratio | 16:9 | 16:9, 9:16, 1:1 |
| num_frames | 81 | 17 to 161 |
| frames_per_second | 16 | 4 to 60 |
| num_inference_steps | 27 | 2 to 40 |
| guidance_scale (high-noise expert) | 3.5 | 1 to 10 |
| guidance_scale_2 (low-noise expert) | 4 | 1 to 10 |
| shift | 5 | 1 to 10 |
| acceleration | regular | none, regular |
| interpolator_model | film | none, film, rife |
| num_interpolated_frames | 1 | 0 to 4 |
| adjust_fps_for_interpolation | true | |
| enable_prompt_expansion | false | |
| enable_safety_checker / output checker | false | |
| video_quality | high | low, medium, high, maximum |
| video_write_mode | balanced | fast, balanced, small |
| negative_prompt | "" | |

## Open questions

- What `acceleration: regular` does server-side is not documented.
- The default output includes FILM frame interpolation and H.264 encoding, so a matched deploy must include those steps in its cost.
- Max duration on fal is 161 frames at 16 fps (about 10 s), which conflicts with the "5 s max" figure for Wan 2.2. Native Wan 2.2 A14B was trained for 81 frames.
