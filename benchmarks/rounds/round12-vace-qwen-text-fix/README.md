[← All rounds](../../../README.md)

# Round 12: VACE and Qwen-Image-Edit against the same text-accuracy failure (Oct 22, 2026)

Status: **complete**. Both tools were tested against the exact same frozen customer prompt used in rounds 10-11. Both fail at the actual task. VACE's first attempt made no visible edit at all; a diagnosed fix (re-run on a second pod after the first attempt's retry was interrupted by a monitoring mistake, see section 4) confirmed the diagnosis was correct -- the fixed version genuinely edits the board now -- but the resulting text is still wrong, except for one short, distinct string that came out exactly correct. Qwen-Image-Edit edited the text on its first and only attempt, also incorrectly.

## 1. Summary

- **VACE, first attempt: no visible edit at all.** The output video is visually indistinguishable from the original unedited clip -- same garbled text, same layout, frame for frame. The model did not appear to act on the edit prompt or the mask.
- **Likely cause, diagnosed after the fact**: the original video (with its already-garbled text) was passed to VACE as conditioning for every frame, including inside the region marked for editing. That gives the model a direct shortcut -- copy the pixels that are already there -- instead of actually regenerating that region from the prompt. The fix: black out the video's content inside the edit region before passing it in, so there is nothing to copy from. This is a known pattern for inpainting-style conditioning, not something specific to this project's setup -- it was missed on the first attempt because the pipeline's documentation describes the mask's role clearly but does not say the video itself must also be edited to match.
- **Qwen-Image-Edit, first attempt: made an edit, but the wrong one.** The tool did change the whiteboard's handwriting (visibly different from the original), confirming it responds to edit instructions on existing text -- but the new text is still garbled gibberish, not the real script. So it replaced one wrong text with a different wrong text.
- **The VACE fix was re-run to completion on a second pod and confirmed: the diagnosis was right, but the underlying text problem remains.** With the edit region blacked out before conditioning, VACE now genuinely regenerates that region -- new, different handwriting, consistent across all 81 frames, no flicker or reversion to the original. But the text is still not the real script. One detail stands out: the short, distinct string "ADREFUNDS.COM" came out **exactly correct**, while the long sentence around it did not -- consistent with the pattern documented elsewhere in this project that short, simple text fragments sometimes render correctly while long sentences do not.

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

### 3.3 Test A (retry): fix confirmed, underlying problem remains

The first retry attempt (blacking out the board region in the input video before passing it to VACE, to remove the suspected "copy the existing pixels" shortcut) was interrupted mid-run by a monitoring mistake (section 4) and had to be re-run from scratch on a second pod.

`clips/test_a_vace_retry.mp4` -- the completed, sha256-verified result. The diagnosis in section 3.1 was correct: with the original video blacked out in the edit region, VACE now genuinely acts on the mask and prompt. The board shows new, different handwriting from the original garbled text, consistent and stable across all 81 frames (checked at frames 1, 40, and 80 -- `raw/round12_retry_frame{001,040,080}.png`), with no flicker or reversion to the original text.

The text itself is still not the real script -- "THOLDITES OF HERNETIRS UF, ARVERTIESS, OP FIE, GLLMDS" where the script reads "Thousands of U.S. advertisers are pursuing claims against Google," and similar garbling throughout. One specific detail is worth recording: the short, distinct string "ADREFUNDS.COM" (from the end of the script) renders **exactly correctly**, standing out clearly against the garbled sentence around it. This matches a pattern already seen elsewhere in this project -- short, simple, distinct text sometimes comes out right while long, multi-word sentences do not -- and is a real, specific data point about where this class of model's text limits sit, not just a restatement of "it fails."

## 4. What went wrong operationally (first attempt at the retry)

This project's own monitoring tool (`pod_guard.sh`) uses a background watchdog to stop the pod independently of the main job, as a safety net against jobs that hang or crash while still billing. Its idle-detection works by checking, every few seconds, whether a process matching a given name pattern is running; if that pattern goes missing for too long without a "done" marker present, it assumes the job died and stops the pod.

The watchdog was started once, at the beginning of the session, watching for the process name of the first script (`round12_session.py`). That script completed both test A and test B normally and exited, which is expected and fine. The retry for test A was then started as a **separate script with a different filename** (`round12_retry_a.py`) -- but the watchdog was never told to watch for the new name. Once the first script exited, the watchdog stopped seeing any matching process at all, and after its configured idle window, it concluded the job had died and stopped the pod -- while the retry was still genuinely running, about halfway through a real generation.

This is a known failure mode this project's own documentation (`AGENTS.md`) explicitly warns about -- the watchdog's process check only works if its pattern actually matches whatever is currently running -- and it was not followed when the retry script was launched under a new name mid-session. No data was at risk (the watchdog did its job correctly given what it was told to watch for), but roughly half of a ~12-minute generation was wasted, along with the time to diagnose and write the fix. The retry was re-run successfully on a second pod with the watchdog's pattern corrected to match the actual script.

## 5. What this means

- **Neither tool fixes the text-accuracy problem**, consistent with every other result in this project so far (rounds 10 and 11): no tool tested yet reliably renders or corrects exact, long-form text in video, including two tools specifically marketed for masked video editing and accurate text rendering.
- VACE's first-attempt failure (no change at all) was a setup mistake on this round's part, not a model limitation -- confirmed by the corrected retry, which shows the model can and does act on the mask and prompt once the conditioning shortcut is removed. That correction matters for anyone reusing this pipeline: the input video must have its edit region blanked out, not just a separate mask passed alongside the untouched original.
- Qwen-Image-Edit's and VACE's failure modes converge on the same underlying limitation already documented in round 10: these models can follow "change what's written here" instructions and will visibly act on them, but cannot render arbitrary, correct, long-form characters. The one correctly-rendered short string (`ADREFUNDS.COM`, test A retry) suggests the limitation scales with text length/complexity rather than being an all-or-nothing failure -- worth testing more directly (see below).

## 6. Still to do

1. Test whether short, simple text (a single word, a URL, a percentage) reliably renders correctly with VACE and Qwen-Image-Edit, versus the long sentences tested here -- the one correct string in test A retry (`ADREFUNDS.COM`) suggests this is worth a direct, controlled test rather than an incidental observation.
2. Compare VACE's corrected approach against round 10/11's hand-built overlay result on effort and generation cost (VACE: ~13 minutes generation + one-time model download on an A100, for an automated edit; round 10/11: free, local, but required building and debugging the compositing pipeline by hand).
3. Try different Qwen-Image-Edit prompt phrasing, or a shorter target text, to help separate "this tool can't do long text" from "this specific prompt phrasing didn't work."

## 7. Files

- `clips/test_a_vace_v1.mp4`: VACE's first attempt -- no visible edit (section 3.1).
- `clips/test_a_vace_retry.mp4`: VACE's corrected retry -- genuinely edits the board, text still wrong except for one short correct string (section 3.3).
- `clips/test_b_qwen_edit.png`: Qwen-Image-Edit's result -- edited, but wrong text (section 3.2).
- `raw/raw_record.json`, `raw/raw_record_retry.json`: generation records (load time, generation time, sha256) for the first-attempt tests and the completed retry.
- `raw/round12_vace_frame{001,040,080}.png`, `raw/round12_retry_frame{001,040,080}.png`: frames extracted from the v1 and retry clips for direct inspection.
- `round12_session.py`: the script that produced both first-attempt results (test A v1, test B).
- `vace_retry_blackout_fix.py`: the corrected VACE script (blacks out the edit region in the input video before conditioning) -- re-run to completion on a second pod, result in section 3.3.

## 8. Cost

Two pod sessions: the first ran from GPU verification through the interrupted retry (~40 minutes, A100, stopped by the monitoring mistake in section 4); the second ran the corrected retry to completion (~25 minutes, A100, including a cached-weights reload). Both within this round's approved budget.
