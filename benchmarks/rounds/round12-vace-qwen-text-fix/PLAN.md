[← All rounds](../../../README.md)

# Round 12 plan: VACE and Qwen-Image-Edit against the same text-accuracy failure

Status: planned, not yet run.

## Why this round

The boss's direction after round 11: stop building custom fixes by hand (manual compositing, research papers with no usable code) and instead test existing open models with already-published workflows -- things the community has already built and shared on GitHub/Hugging Face. Two candidates were identified:

1. **VACE** (`ali-vilab/VACE`, Apache 2.0) -- an official video-editing add-on for the Wan model family (the same base model this project already uses). Takes a video, a mask of the region to change, and a text prompt, and regenerates just that masked region while leaving the rest of the video untouched. This is the same idea as round 10/11's hand-built clean-plate overlay, but as a real trained model instead of manual pixel compositing.
2. **Qwen-Image-Edit** (`Qwen/Qwen-Image-Edit`, Apache 2.0) -- Alibaba's open image-editing model, specifically strong at rendering and correcting legible text in images. The idea: use it to fix the garbled whiteboard text directly on a frame, then either use that frame as-is or feed it to Wan's image-to-video mode to animate from a starting point that already has correct text (the same approach tested by hand in round 10, section 7, but with a purpose-built text-accurate editor instead of our own manual clean-plate composite).

Both are tested against the exact same customer prompt and frozen job (`round10-text-accuracy/lawyer_job.json`, prompt_id `round10_lawyer_whiteboard`, seed 10001) already used in rounds 10 and 11, so results are directly comparable to the existing baseline (config A: plain 27-step, garbled text) and to round 10/11's overlay result (correct text, hand-built).

## What will be tested

| Test | Input | Tool | What it should fix |
|---|---|---|---|
| A: VACE masked video edit | Round 10's config A clip (`round10-text-accuracy/clips/configA_plain27.mp4`) + a mask of the whiteboard region (reuse round 11's SAM2 board mask, `round11-sam2-board-tracking/raw/board_masks/`) + the real script as the edit prompt | `ali-vilab/VACE` on the Wan2.1-VACE-14B weights (closest scale to this project's Wan2.2-A14B; VACE for Wan2.2 is not released as of this writing -- verify on the pod before assuming) | Replaces the garbled text region directly in the existing video, without manual compositing |
| B: Qwen-Image-Edit text correction | Frame 1 of round 10's config A clip (the first frame showing the garbled board) | `Qwen/Qwen-Image-Edit`, prompted to correct the whiteboard text to the real script | A single corrected image -- tests whether a purpose-built text-accurate editor can fix existing garbled text, not just generate new text from scratch |
| B2 (conditional on B succeeding): I2V from Qwen-Image-Edit's corrected frame | B's output frame | Wan2.2-I2V-A14B (already used in round 10, section 7) | Whether an automatically-corrected starting frame survives into video as well as round 10's manually-corrected one did |

## What would make this a win

- VACE produces a clip with correct text and no visible seam/artifact at the masked region's edge, without any manual pixel work on our side -- a real model doing what rounds 10-11 did by hand.
- Qwen-Image-Edit corrects the whiteboard text in the still frame legibly and correctly, which would mean we have an automated way to generate round 10/11's starting point instead of hand-compositing it.
- Either result still needs to be judged by direct frame inspection against the real script (same method as round 10), not just "looks like text."

## What would not be a win (expected failure modes to watch for)

- VACE's edit introduces its own new text-rendering failure inside the masked region -- it is still a diffusion video model, so there's no guarantee it renders exact characters correctly just because the task is "edit" rather than "generate from scratch." This needs to be checked directly, not assumed.
- Qwen-Image-Edit is built for images; whether its corrected text survives being handed to Wan's image-to-video mode (test B2) is a separate open question, mirroring round 10 section 7's finding that new content and even some existing content can still degrade in motion.

## Resources needed

- A RunPod A100 pod (or equivalent) -- VACE-14B and Qwen-Image-Edit both need real VRAM; exact requirement to be confirmed on the pod before committing to a config.
- Budget: default under $10 unless told otherwise (same cap as round 10).
- `server/runpod14.txt`'s pod is no longer reachable; a new pod notes file is needed before this round can start.

## Steps

1. Get a pod (new `server/runpodN.txt`), verify disk/cache setup per this repo's standard pod checklist (AGENTS.md).
2. Install VACE and Qwen-Image-Edit, confirm which Wan-compatible VACE checkpoint actually exists and fits this pod's VRAM.
3. Run test A (VACE), save the output clip and raw generation record.
4. Run test B (Qwen-Image-Edit), save the output frame and raw record.
5. If B produces a legibly corrected frame, run test B2 (I2V from that frame).
6. Direct frame-by-frame inspection against the real script for every output (same method as round 10) -- no automated accuracy claim without this.
7. Write the round 12 report: results table, sha256-verified clips, honest comparison against round 10/11's hand-built result, and a recommendation on whether either approach should replace the manual pipeline.

## Files (once run)

- `clips/`: VACE output clip, Qwen-Image-Edit corrected frame, and (if run) the B2 I2V clip.
- `raw/`: generation records for each test.
- `README.md`: the full report, written after results are in -- not before.
