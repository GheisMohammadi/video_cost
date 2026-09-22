# Round 2 test design: prompts that ask for what this pipeline cannot produce

Status: frozen before running. Job list sha256 recorded in section 4. Shares its cost methodology, metric definitions, and safeguards with round 1 (`benchmarks/rounds/round1-wan22-a14b-480p/PLAN.md`); this document covers only what is different.

## 1. Question

Round 1 measured cost for a prompt this pipeline can fully satisfy. Real prompts routinely ask for more than that: audio, a different resolution or aspect ratio than the fixed render settings, or a longer duration than the fixed clip length. This round asks: how common is that in practice, and what actually happens to the output when it does? One round 1 clip, generated at full settings from a prompt built around camera-equipment terminology, passed every automated check yet still failed blind review outright — this round checks whether that was a one-off or a pattern.

## 2. Evidence from the real prompt corpus

Measured directly from the crawled prompt set (5,859 usable prompts, the same corpus used in round 1):

| Category | Share of prompts requesting it |
|---|---|
| Audio, dialogue, or music | 31.7% |
| Explicit 4K/8K/UHD resolution | 18.1% |
| Vertical, 9:16, or square aspect ratio | 9.5% |
| A stated duration over 5 seconds | 22.0% |
| Camera-brand jargon (for example a specific camera model) | 1.9% |
| Lens-spec jargon (for example a focal length in mm) | 9.0% |

Audio alone is requested by roughly a third of real prompts, none of which this pipeline configuration can produce; the point of this round is to check what happens to the rest of the clip when that request is present, not to re-litigate that audio is absent (round 1 pilots reported no audio track from this pipeline previously).

## 3. Test design

One real, unedited prompt per category, at the same settings as round 1 (832x480, 81 frames at 16 fps, 27 steps, guidance 3.5 / 4.0, shift 5, empty negative prompt) so results are directly comparable. Each was checked against its full text to confirm it does not also trigger a different category by accident, except the sixth case, which is deliberately a real prompt combining several categories at once (a naturally occurring pattern in the corpus, not a constructed example).

| Job | Category | What the prompt asks for that this pipeline cannot produce |
|---|---|---|
| M1 | audio | ambient sound / dialogue in a desert-ruins scene |
| M2 | resolution | explicit 8K wording |
| M3 | aspect | (visually implied vertical composition via a portal/rift scene, selected for a request outside the fixed 16:9 frame) |
| M4 | camera | camera-brand and lens-spec jargon ("shot on ARRI Amira ... 24mm lens, f/2.8") |
| M5 | duration | an explicit 15-second request |
| M6 | kitchen sink | resolution, aspect, camera jargon, and lens spec together in one real prompt |

All six prompts are English and under 180 tokens, well under the model's 512-token limit, so truncation (already covered in round 1) is not a factor here. Every prompt's source URL and the picking script are in `select_jobs.py`; the frozen list is `round2_jobs.json`.

A warm-up job runs first, as in round 1, and is excluded from queue cost.

## 4. Freezing

Job list file: `round2_jobs.json`. sha256, computed before any job ran:

```
e3b848adfe8f619f38f161944f6878a938b38f4f25f9deb057423a22bc2dec66
```

## 5. What is measured beyond round 1's metrics

- **Automated audio check:** every delivered clip is probed for an audio stream (`check_audio.py`). Expected result, given this pipeline's configuration, is that none have one; the value of running it is confirming that directly rather than assuming it, for every category, not only the one that explicitly asked for audio.
- **Blind review, extended:** the same blind, randomly-named, size-padded review process as round 1, scoring `prompt_match` (pass / partial / fail) as before, plus a new field, `mismatch_handling`, free text on how the unsatisfiable part of the prompt was handled: ignored cleanly with the rest of the scene rendered well, visibly broken or rushed, or misread literally (for example rendering an object named in passing rather than the intended scene — the failure mode round 1's camera-jargon clip appeared to show).
- No steps ladder in this round; round 1 already covers that question, and every job here uses the standard 27 steps to isolate the category-of-mismatch variable.

## 6. Procedure and safeguards

Identical to round 1 section 6: preflight checks before any model load, the independent stop guard armed first, a go/no-go check if the first job runs far over its expected time, and a verified, checksummed copy of every result before the pod is stopped.

## 7. Budget

| Item | Time | Cost (estimate, $1.59/h GPU + $0.028/h disk) |
|---|---|---|
| Pod boot, upload, preflight | about 5 min | $0.13 |
| Weights download (if not already present) | about 12 min | $0.32 |
| Model load and warm-up | about 3 min | $0.08 |
| Six measured jobs at 27 steps each | about 58 min | $1.55 |
| Copy results | about 3 min | $0.08 |
| **Total** | **about 81 min** | **about $2.16 ($2.55 if weights must be downloaded from empty)** |

Session cap: $3.00, confirmed before running.

## 8. Limitations

Same general limitations as round 1 (single session, single host, no confidence intervals, one informal reviewer familiar with the project). Specific to this round: one prompt per category is not enough to say a category's failure mode is general rather than specific to that particular prompt's wording; the audio check only confirms presence or absence of an audio stream, not whether the visual content still matches everything else the prompt asked for; and the aspect-ratio and resolution categories are tested by prompt wording only; the render settings themselves are fixed regardless of what the prompt requests, so this measures whether the wording confuses the model's composition, not whether the pipeline can be made to actually output a different resolution or aspect ratio.
