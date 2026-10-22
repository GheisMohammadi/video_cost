[← All rounds](../../../README.md)

# Round 12: VACE and Qwen-Image-Edit against the same text-accuracy failure (Oct 22, 2026)

Status: **interrupted, incomplete**. Both tools were tested against the exact same frozen customer prompt used in rounds 10-11. Both failed on the first attempt. A likely root cause was diagnosed and a fix was in progress for VACE when the pod was stopped mid-run by this round's own monitoring mistake, not a model or budget problem. The fix is unverified.

## 1. Summary

- **VACE, first attempt: no visible edit at all.** The output video is visually indistinguishable from the original unedited clip -- same garbled text, same layout, frame for frame. The model did not appear to act on the edit prompt or the mask.
- **Likely cause, diagnosed after the fact**: the original video (with its already-garbled text) was passed to VACE as conditioning for every frame, including inside the region marked for editing. That gives the model a direct shortcut -- copy the pixels that are already there -- instead of actually regenerating that region from the prompt. The fix: black out the video's content inside the edit region before passing it in, so there is nothing to copy from. This is a known pattern for inpainting-style conditioning, not something specific to this project's setup -- it was missed on the first attempt because the pipeline's documentation describes the mask's role clearly but does not say the video itself must also be edited to match.
- **Qwen-Image-Edit, first attempt: made an edit, but the wrong one.** The tool did change the whiteboard's handwriting (visibly different from the original), confirming it responds to edit instructions on existing text -- but the new text is still garbled gibberish, not the real script. So it replaced one wrong text with a different wrong text.
- **The VACE fix (blacked-out edit region) was re-run but never finished.** It was 16+ of 30 steps in (roughly half) when the pod was stopped. This was not a budget or model problem -- it was caused by a mistake in this round's own cost-control setup (see section 4). The result is unverified; it needs a rerun to know whether the fix actually works.

## 2. What was run

Both tests used the identical frozen job already used in rounds 10-11: prompt_id `round10_lawyer_whiteboard`, seed 10001, the exact customer script, 832x480, 81 frames.

| Test | Tool | Input | What it should fix |
|---|---|---|---|
| A (v1) | `Wan-AI/Wan2.1-VACE-14B-diffusers` | Round 10's config A clip + round 11's SAM2 board mask (white=board=edit, black=subject=keep) + the real script as the edit prompt | Replace the garbled board text directly in the video, no manual compositing |
| A (retry, incomplete) | Same, with the video's board region blacked out before conditioning | Remove the "copy the existing pixels" shortcut that likely caused test A (v1) to make no visible change |
| B | `Qwen/Qwen-Image-Edit` | Frame 1 of round 10's config A clip, prompted to correct the whiteboard text to the real script | A single corrected starting frame, as an alternative to manual compositing |

## 3. Results

### 3.1 Test A (v1): VACE made no visible change

`clips/test_a_vace_v1.mp4` -- compared frame-by-frame against the original input clip, the text, layout, and even the lawyer's exact pose per frame are the same. No evidence the model acted on the mask or the prompt.

VACE's own documentation (checked before running) states the mask is what tells the model which regions to generate vs. keep (black = keep, white = generate), and the test's mask convention matched that spec exactly (reusing round 11's SAM2 board mask, board=white=generate). The mask being correct does not mean the pipeline was used correctly end to end -- passing the full, unedited original video as the `video` conditioning input, even within the "generate" region, appears to have let the model simply reproduce what was already there rather than treating that region as something to regenerate. This was not caught before running; it surfaced only from watching the actual output.

### 3.2 Test B: Qwen-Image-Edit changed the text, incorrectly

`clips/test_b_qwen_edit.png` -- the handwriting is visibly different from the input frame (different letterforms, different specific marks), confirming the model responded to the edit instruction rather than passing the image through unchanged. But the resulting text does not match the real script -- it is a different, equally invented set of characters ("aoli Fathocobr af Crcondl reuinrs," and similar gibberish in place of "Thousands of U.S. advertisers are pursuing claims..."). The underlying problem -- a model that cannot render exact arbitrary text -- shows up here too, even in a tool marketed specifically for accurate text rendering and editing.

### 3.3 Test A (retry): interrupted, unverified

A second attempt blacked out the board region in the input video before passing it to VACE, to remove the suspected "copy the existing pixels" shortcut. This ran to roughly step 16 of 30 (about half of generation) before the pod was stopped by this round's own monitoring setup (section 4). No output file exists to inspect. The fix is a reasonable, specific hypothesis grounded in how the first attempt behaved, but it is unverified until re-run to completion.

## 4. What went wrong operationally

This project's own monitoring tool (`pod_guard.sh`) uses a background watchdog to stop the pod independently of the main job, as a safety net against jobs that hang or crash while still billing. Its idle-detection works by checking, every few seconds, whether a process matching a given name pattern is running; if that pattern goes missing for too long without a "done" marker present, it assumes the job died and stops the pod.

The watchdog was started once, at the beginning of the session, watching for the process name of the first script (`round12_session.py`). That script completed both test A and test B normally and exited, which is expected and fine. The retry for test A was then started as a **separate script with a different filename** (`round12_retry_a.py`) -- but the watchdog was never told to watch for the new name. Once the first script exited, the watchdog stopped seeing any matching process at all, and after its configured idle window, it concluded the job had died and stopped the pod -- while the retry was still genuinely running, about halfway through a real generation.

This is a known failure mode this project's own documentation (`AGENTS.md`) explicitly warns about -- the watchdog's process check only works if its pattern actually matches whatever is currently running -- and it was not followed when the retry script was launched under a new name mid-session. No data was at risk (the watchdog did its job correctly given what it was told to watch for), but roughly half of a ~12-minute generation was wasted, along with the time to diagnose and write the fix.

## 5. What this means so far

- Neither tool fixed the text-accuracy problem on a first, naive attempt -- consistent with every other result in this project so far (rounds 10 and 11): no tool tested yet reliably renders or corrects exact text in video.
- VACE's failure mode (no change at all) looks like a setup mistake on this round's part, not necessarily a limitation of the model itself -- the diagnosis is specific and testable, just not yet confirmed.
- Qwen-Image-Edit's failure mode (wrong text, but a real edit) is different and more informative: it shows the model can follow "change what's written here" instructions, but still cannot render the *correct* arbitrary characters -- the same fundamental limitation documented in round 10, just reached through a different, more specialized tool.

## 6. Still to do

1. Re-run the VACE retry (blacked-out edit region, `vace_retry_blackout_fix.py`, already written) to completion on a fresh pod, with the watchdog's process pattern matching the actual script being run this time.
2. If the retry still fails to produce correct text, that would be a real (not setup-caused) finding about VACE's limits on long-form text -- worth documenting as such.
3. Qwen-Image-Edit's result doesn't need a mechanical retry (it ran to completion) -- but trying a different prompt phrasing, or a shorter target text, would help separate "this tool can't do long text" from "this specific prompt phrasing didn't work."
4. Compare whichever approach succeeds against round 10/11's hand-built overlay result on correctness, effort, and (for VACE) generation cost.

## 7. Files

- `clips/test_a_vace_v1.mp4`: VACE's first attempt -- no visible edit (section 3.1).
- `clips/test_b_qwen_edit.png`: Qwen-Image-Edit's result -- edited, but wrong text (section 3.2).
- `raw/raw_record.json`: generation records for both first-attempt tests (load time, generation time, sha256).
- `raw/round12_vace_frame{001,040,080}.png`: frames extracted from the VACE v1 clip for direct inspection.
- `round12_session.py`: the script that produced both first-attempt results.
- `vace_retry_blackout_fix.py`: the corrected VACE script (blacks out the edit region in the input video before conditioning) -- written and partially run, not yet verified to completion (section 3.3).

## 8. Cost

Pod ran from GPU verification through the interrupted retry, roughly 40 minutes on a rented A100 -- within this round's approved budget.
