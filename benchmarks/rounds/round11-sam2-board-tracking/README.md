[← All rounds](../../../README.md)

# Round 11: SAM 2 video tracking for the text-overlay fix (Oct 20, 2026)

Status: in progress. [Round 10](../round10-text-accuracy/) built and tested a post-production fix for on-screen text accuracy: generate the clip, then composite the real script text onto the board afterward, rather than trusting the model to render it. That fix (round 10, section 6) left three open gaps: visible edge jitter (segmentation was re-run independently per frame), no real board-region detection (it relied on "subject vs. everything else," which only works because the board fills nearly the whole background in that specific shot), and a static, non-animated text reveal. This round replaces the segmentation step with SAM 2's video tracking to close the first two gaps, and researches what the third gap (the animated reveal) would need.

## 1. Summary

- **SAM 2 closes the jitter and board-detection gaps.** A single point prompt on the board in frame one, propagated by SAM 2 across all 81 frames of round 10's config A clip, tracks the board as one coherent object instead of re-segmenting independently each frame. Mean frame-to-frame mask change was 1.5% of pixels (max 9.9%, during the fastest hand motion) -- consistent with real hand/marker movement, not segmentation noise. Because SAM 2 tracks the board as its own region rather than inferring it as "not the subject," this generalizes to shots where the board does not fill the whole background, unlike round 10's method.
- **The end-to-end video was rendered, not just the mask.** Plugging SAM 2's mask into round 10's clean-plate compositing pipeline (in place of its mediapipe mask) and rendering the full clip produces the same correct, readable script text as round 10's v2 result.
- **One real defect found and fixed**: pixels SAM 2 classified as "board" in very few frames (not just zero) could still have a median that lands on the original garbled text's color, because there weren't enough clean samples to outvote it. Fixed with OpenCV inpainting (`cv2.inpaint`), reconstructing those low-confidence pixels from surrounding reliable plate pixels instead of trusting an unreliable median.
- **One claim made and retracted in the same session**: a visible color-blotch artifact under the blurred text was initially attributed to this change (SAM 2's tighter mask "starving" the median of samples). Checking it against round 10's own v2 frame showed the identical blotchiness already exists there -- it is a pre-existing limitation of the blur-based clean-plate technique itself, not something this round introduced. Recorded here because the correction process is as much a real result as the technique.
- **The animated-reveal gap is still open.** It needs point-tracking for the marker tip (a different problem from board-region tracking), researched but not built this round. The strongest option, CoTracker3, is CC-BY-NC-licensed and not usable in this project's commercial pipeline as-is; OpenCV's built-in optical-flow trackers have no such restriction and are the recommended next thing to try.

## 2. Why SAM 2, and not just a better mediapipe mask

Round 10's segmentation (mediapipe's `ImageSegmenter`) classifies each frame independently: subject vs. not-subject, with no memory of the previous frame's classification. Two problems followed directly from that: small differences in classification between adjacent frames show up as visible edge jitter, and "not-subject" only equals "board" in a shot where the board is the only other thing in frame.

SAM 2's video mode is built for exactly this: give it one point prompt in one frame, and it tracks that specific object across the whole clip using a memory of what it has already identified, including through occlusion (the marker and hand passing in front of the board). That directly removes the two failure modes mediapipe's design has no mechanism to avoid, as a property of SAM 2's architecture rather than something that needed tuning.

## 3. Method

| Item | Value |
|---|---|
| Input | Round 10's config A clip (`round10-text-accuracy/clips/configA_plain27.mp4`), 81 frames, 832x480 |
| Model | `sam2.1_hiera_small` (official Meta checkpoint) |
| Hardware | Local, Apple Silicon (MPS backend) -- no pod, no GPU rental, no cost |
| Prompt | One point, placed once on blank board space in frame 1 |
| Propagation | SAM 2's `propagate_in_video`, automatic across all 81 frames |
| Runtime | Under 100 seconds for the full clip |

Compositing reused round 10's clean-plate technique (section 6, v2): a per-pixel median across frames classified as "board" reconstructs the board's real lighting and texture, a Gaussian blur over the text region erases the original garbled lettering, the real script is drawn on top, and the subject is composited back in front per frame -- with SAM 2's tracked mask standing in for mediapipe's per-frame mask throughout.

## 4. Results

### 4.1 Tracking quality

Mean frame-to-frame mask change across the clip: **1.5% of pixels** (max 9.9%, at the frame with the fastest hand motion). This is attributable to real motion -- the hand and marker actually moving in front of the board -- not segmentation noise, and the tracked region visibly stays locked to the board's true edge throughout (`raw/overlay_check_001.png`, `raw/overlay_check_040.png`, `raw/overlay_check_081.png`: the tracked region shaded red over the original frame, at the start, middle, and end of the clip).

### 4.2 End-to-end composited video

`clips/final_composite.mp4` -- the full 81-frame render using SAM 2's mask. Same correct, readable script text as round 10's v2 clip, subject composited correctly in front throughout.

### 4.3 A defect found: low-sample-count pixels

Checking per-pixel board-sample counts across the 81 masks found 56,456 of 399,360 pixels (14%) were never classified as board in any frame, and tens of thousands more had fewer than 10 samples. A median computed from very few samples can land directly on an actual garbled-text pixel rather than averaging it out -- this is a real failure mode, not a hypothetical one, and the first version of this round's render visibly showed it as faint color blotches.

**Fix**: any pixel with fewer than 10 board-classified samples across the clip is treated as unreliable and reconstructed with OpenCV's Telea inpainting algorithm (`cv2.inpaint`) from surrounding *already-clean* plate pixels, instead of being trusted as a real median or filled from an unmasked all-frame average (the first fix attempted, which still pulled in the original garbled colors and did not visibly change the result).

### 4.4 A claim retracted

After the inpainting fix, the rendered video still showed the same color blotches, unchanged. The working theory -- that SAM 2's mask was tighter than mediapipe's and this was a new, SAM2-specific tradeoff -- was checked directly against round 10's own v2 output by extracting its frame one. **The identical blotchiness is already present in round 10's v2 clip.** This is a real, pre-existing limitation of the blur-based clean-plate technique: where the garbled text's color is present in effectively every sample (not just a few), a moving-occluder-based median cannot remove it, and a Gaussian blur softens sharp edges without fully erasing a strong color cast underneath. Already listed as a known gap in round 10, section 6 -- not a new one introduced by this round's change.

This is recorded as a result in its own right: the first explanation offered for an observed difference was plausible but wrong, and checking it against the actual prior output (not just re-reasoning about the pipeline) is what caught it.

## 5. What this doesn't yet address

1. **Animated text reveal.** The most visible remaining issue from round 10, section 6 is unaffected by this round's change -- SAM 2 tracks the board region, not the marker tip, which is a different tracking target. See section 6 below for what was researched on this.
2. **The blur-blotch artifact** (section 4.4) is unaffected -- it is a property of the blur-based reconstruction, not the tracking method, and remains open regardless of which segmentation approach supplies the mask.

## 6. Marker-tip tracking: researched, not built

The animated reveal needs a tracked point for the marker tip (so pre-rendered text can be progressively revealed along the path the marker actually follows, instead of appearing as a full static block from frame one). Three tools were researched for this:

- **CoTracker3**: a transformer-based dense point tracker, explicitly built to survive occlusion -- directly relevant, since the marker tip repeatedly passes behind the writing hand. **License: CC-BY-NC** -- noncommercial only, not usable in this project's pipeline, which supports a commercial video-generation service.
- **SAM 2**: this round's tool, built for region/object tracking, not single-point trajectories -- not the right tool for this specific sub-problem.
- **OpenCV's built-in point trackers** (Lucas-Kanade optical flow + `goodFeaturesToTrack`): already a dependency in this pipeline, no license restriction, less robust under occlusion than CoTracker3, but the marker tip is visible and moves smoothly for most of the clip, so worth testing before taking on a noncommercial dependency.

No tracking code for this was written this round; it is the immediate next step (section 7).

## 7. Still to do

1. Marker-tip tracking for the animated text reveal -- try OpenCV optical flow first (no license concern); fall back to CoTracker3 only if occlusion robustness proves necessary, accepting its noncommercial-license restriction, or look for a permissively-licensed alternative.
2. Build the actual animated reveal: once a marker-tip trajectory exists, progressively reveal the pre-rendered text along that path instead of showing the full block from frame one.
3. Address the blur-blotch artifact (section 4.4) -- an alternative to a flat Gaussian blur (for example, a stronger local blur radius scaled to local color variance, or inpainting the text region instead of blurring it) might remove it without needing a new tracking method.
4. Re-run this round's full pipeline on round 10's config B clip (the 4-step LoRA config) and on a different prompt/shot, to check whether the board-region tracking and the low-sample-count fix generalize beyond this one clip.

## 8. Files

- `scripts/sam2_board_track.py`: the SAM 2 video-tracking script (local, MPS, no pod). Produces `raw/board_masks/`.
- `scripts/clean_plate_v3_sam2.py`: the end-to-end compositing script -- SAM 2 mask, per-pixel median clean plate, reliability-threshold inpainting for low-sample pixels (section 4.3), text overlay, per-frame subject compositing. Produces `clips/final_composite.mp4`.
- `raw/board_masks/`: the 81 tracked board masks SAM 2 produced, one per frame.
- `raw/overlay_check_{001,040,081}.png`: visual verification frames -- the tracked region shaded red over the original frame, at the start, middle, and end of the clip (section 4.1).
- `clips/final_composite.mp4`: this round's final rendered result (section 4.2).

Dependencies: `torch`, `torchvision`, `opencv-python-headless`, `Pillow`, and `sam2` (installed from `github.com/facebookresearch/sam2`, requires Python >= 3.10 -- this machine's system Python is 3.9, so a separate venv on Homebrew's `python3.12` was used). The `sam2.1_hiera_small` checkpoint (~184 MB) is downloaded from Meta's public checkpoint URL and is not committed to this repo.
