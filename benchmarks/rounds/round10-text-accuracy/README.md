[← All rounds](../../../README.md)

# Round 10: on-screen text accuracy (Oct 18-19, 2026)

Status: complete. A real customer prompt, flagged in advance as a known failure case, run unedited against both this project's highest-quality config and its fastest/cheapest config. Both fail at the actual task; one fails in a materially worse way.

## Watch both clips

Plain 27-step model (this project's highest-quality config):

<video src="clips/configA_plain27.mp4" controls width="420"></video>

4-step distillation LoRA (this project's fastest/cheapest config):

<video src="clips/configB_lora4step.mp4" controls width="420"></video>

## 1. Summary

- **Neither config renders the script's actual words.** The prompt asks for a specific multi-line script, word for word, on a whiteboard. Both configs produce whiteboard text that is visually plausible at a glance -- correct layout, correct colors (the Google-blue/red/yellow matches the brand, by coincidence or association rather than instruction), correct general shape of "a marked-up business whiteboard" -- but the actual characters are not the script. Words are invented, garbled, or partial ("Arrsodss, Aavetss Remva" instead of "Advertiser Claims"; "gochorres Adverttissrer" instead of "advertisers"). This reproduces the failure a customer prompt already flagged.
- **The fast config fails in a worse, different way, not just a less-accurate one.** By the later frames, the 4-step config's whiteboard becomes semi-transparent and starts showing a ghostly reflected duplicate of the lawyer's own face and an unrequested second object (a paper or clipboard), on top of the already-garbled text. The plain config's board stays a stable, opaque, readable-looking (if wrong) surface throughout. This is a new finding, not something the customer's report described -- the fast config does not just write worse text, it visually breaks down more as the clip continues.
- **The marker does not reliably track to where it is "writing.**" In several frames, the marker tip sits away from the text that appears to be forming, or new text appears in a column the marker was not at the moment before. This matches the customer's second complaint (marks not matching text position).
- **This is not a config problem rounds 1-9's settings can fix.** The plain, highest-quality, most expensive config this project has measured still fails completely at exact text. Research done before this round (see the conversation that scoped it) found this is an industry-wide, currently-unsolved limitation of video diffusion models, not something specific to this project's pipeline or its speed optimizations.

## 2. What was run

| Item | Value |
|---|---|
| Prompt | The customer's exact prompt, unedited: a white male lawyer explaining a multi-paragraph script (Google advertiser claims) on a whiteboard with a marker |
| Config A | Wan 2.2 T2V-A14B, 27 steps, standard guidance (round 1's settings) |
| Config B | Wan 2.2 T2V-A14B plus round 8's 4-step distillation LoRA, guidance 1.0 (round 8-9's settings) |
| Resolution | 832x480, 81 frames at 16 fps (5.0625 s) -- same as every prior round |
| Seed | 10001, fixed across both configs |
| Tokens | 119 (the prompt's real UMT5 token count on the pod, well under the 512-token truncation limit -- the whole script was passed to the model intact, not cut off) |

## 3. Results

| Config | Generate s | Gate | Text accuracy (direct inspection) | Visual stability |
|---|---|---|---|---|
| A: plain, 27 steps | 552.7 | pass | Garbled, invented words throughout; layout and color scheme plausible, actual script not reproduced | Stable; whiteboard stays opaque and consistent across all five inspected frames |
| B: 4-step LoRA, guidance 1.0 | 113.0 | pass | Garbled, invented words throughout, same as config A | Degrades over the clip: by the later frames the board becomes semi-transparent, showing a reflected duplicate of the subject's face and an unrequested extra object |

Both clips passed the automated gate (81 frames, correct shape, not black, not frozen) -- the gate has no way to check text content or detect the transparency/reflection defect, consistent with round 8's earlier finding that the gate misses real, visible problems that direct frame inspection catches.

## 4. What this means for the team's question

The team's ask was: find ways to check and improve text/label accuracy, informed by open models and fal's off-the-shelf approach. Research done before this round found a consistent industry answer: no current video model reliably renders exact on-screen text, and the standard fix used everywhere (whiteboard-explainer tools, fal's own auto-caption product) is a post-production overlay -- generate the visual separately from the text, then composite the real text on afterward, rather than asking the model to render it.

This round's result supports that conclusion directly: even this project's best, slowest, most expensive config fails completely at the literal task. The fast config fails in a visually worse way on top of that. Neither points to a generation-side fix being realistic with this pipeline.

What the described QA process (a human checking every frame for hands, teeth, text, logos, continuity, lip-sync, pronunciation) is already positioned to catch exactly this kind of failure -- the open question is whether any part of that review can be assisted or triaged automatically (for example, flagging frames with likely-wrong text via OCR comparison against the script, before a human watches the full clip), separate from fixing the text at generation time.

## 5. Limitations

1. One prompt, one seed, two configs -- a reproduction of a known failure, not a systematic study of text accuracy across many prompts.
2. No OCR or automated text-comparison was run against the two clips; the "garbled, invented words" assessment is from direct visual inspection of five frames per clip, not a full-clip read or a character-level accuracy score.
3. The marker-tracking observation is qualitative, from the same frame inspection, not a measured position-accuracy figure.
4. 480p only. Whether resolution affects text legibility (as opposed to text *correctness*, which is a different problem) is untested here.
5. Neither config's whiteboard-transparency defect (config B) nor general garbling (both configs) was tested across repeats -- one clip per config, same limitation as every prior round.

## 6. Still to do

1. Research and prototype the post-production overlay approach the field standardizes on: detect the whiteboard region, composite real text onto it, rather than relying on generation.
2. Investigate automated pre-screening for the described manual QA process -- OCR-based text-match scoring, face/hand artifact detection -- as a triage layer before human review, not a replacement for it.
3. Test whether other models (open or fal-hosted) handle this same exact prompt any differently, now that a reproducible baseline exists to compare against.

## 7. Files

- `jobs.jsonl`: all three records (one shared warm-up, plus one real job per config), reconstructed from the session's own output.
- `clips/`: `configA_plain27.mp4`, `configB_lora4step.mp4`, each verified by sha256 against its jobs.jsonl record.
- `lawyer_job.json`: the frozen job list containing the customer's exact prompt, committed before this round ran.
