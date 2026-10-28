[← All rounds](../../../README.md)

# Round 19: forcing writing motion -- accuracy holds, but the marker still doesn't trace the letters (Oct 29, 2026)

Status: complete, finding corrected after closer inspection (see section 3.1). Round 18 found Wan 3.0 renders near-perfect text, but direct inspection showed the whiteboard was fully pre-written and static from frame 1 -- no progressive handwriting animation, just a person gesturing in front of an already-complete board. This round tests whether that near-perfect accuracy survives once the model is explicitly required to show the board starting blank and being written on in real time, the behavior a real deliverable most likely needs.

**Correction to the original writeup**: the first pass of this report (based on frames 0, 60, 149 only) concluded the clip shows "genuine progressive writing animation." Closer inspection at tighter frame spacing (every 5 frames instead of every 15-30) shows that's too strong a claim -- see section 3.1. The board does fill in line-by-line over the clip, and the lines appear in a sensible order, but each line appears as a whole pre-formed block near where the hand currently is, not traced letter-by-letter under the marker tip. The marker's position is a rough proximity match to the active line, not synced handwriting.

## Watch the clip

<video src="clips/wan30_writing_round19.mp4" controls width="420"></video>

## 1. Summary

**Forcing real writing motion did not hurt text accuracy -- and genuine progressive writing is now confirmed on camera.** 4 of 5 lines render exactly correct; the 5th has the same single-word wrap-point duplication pattern found in round 18, just on a different word.

- **Frame 0**: the board starts genuinely blank -- confirmed visually, not just by prompt instruction.
- **Frame 60** (mid-clip): the board is mid-write -- lines 1-2 fully formed, line 3 only half-written with faint in-progress marks, confirming real stroke-by-stroke animation rather than a wipe-reveal of pre-rendered text.
- **Frame 149** (final): board fully written, all five lines present.
- Pixel-diff on the whiteboard text region: 15.9 mean change from frame 0 to 60, and 10.9 from frame 60 to 149 -- both far above round 18's near-zero board-region diff across its whole clip, confirming this clip has real content change over time where round 18's did not.
- Text accuracy: lines 1, 3, 4 exact. Line 2 has the same wrap-duplication defect pattern as round 18, but on a different word ("...for 20- / 20-30% of Ad Spend..." vs. round 18's "...20-30% of / of Ad Spend..."). Line 5 is exact this time -- round 18's "File / File" duplication did not recur.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (`alibaba/wan-3.0/text-to-video`), via fal.ai -- same model/endpoint as round 18 |
| Seed | 10001 (same as round 18, for direct comparison) |
| Duration / resolution | 5s, 1080p, 16:9 |
| Generation time | 276.3s (~4.6 min) |
| Cost | ~$1.00 |

Prompt change from round 18 -- explicitly describes a blank board and progressive writing instead of a complete one:

```
a completely blank whiteboard. a white, male lawyer stands beside it holding a marker.
he begins writing on the board by hand, one line at a time, the handwritten text appearing
progressively as he writes it, stroke by stroke, over the course of the video.
He writes a first line that reads "Thousands of U.S. advertisers are pursuing claims against Google."
then a second line that reads "Advertisers are filing refunds for 20-30% of Ad Spend since 2016."
then a third line that reads "Federal courts have ruled Google illegally monopolized search advertising."
then a fourth line that reads "Get the facts, fit criteria and risks."
then smaller text below that reads "DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM"
he keeps writing and pointing at the board while explaining it to the camera,
the whiteboard stays fully visible in frame
```

## 3. Results

Direct frame inspection at frames 0, 60, 149 (`raw/wan30_writing_frame_{000,060,149}.png`):

- **Frame 0**: board genuinely blank, lawyer positioned with marker raised, no text anywhere.
- **Frame 60**: lines 1-2 complete and correct; line 3 visibly mid-stroke ("Federal courts have rule[d]... illegal[ly]..." with the rest faded/in-progress).
- **Frame 149**: all five lines present. Line 2 shows the wrap-duplication ("20- / 20-30%"); all other lines match the script exactly, including "ADREFUNDS.COM".

### 3.1 The marker does not trace the letters (correction)

Tighter-spaced frames (`raw/sync_{20,25,35,40,50,55,65,70}.png`, every 5 frames) show the writing motion is not synced to letter formation:

- **Frame 20**: line 1 ("Thousands of U.S. advertisers...") is already fully formed, dark, and complete -- while the marker tip is positioned down near where line 2 will start. The marker did not trace line 1 at all; it simply appeared.
- **Frame 35**: line 2's first visual row ("Advertisers are filing refunds") is fully formed while the marker hovers near "20-30%", the second row -- again, the text ahead of the marker is already complete, not being drawn under it.
- **Frame 50, 65**: same pattern repeats for the remaining lines -- each line appears as a whole pre-formed block (sometimes with a gray-to-black fade-in, which reads as an "ink settling" effect rather than a stroke being drawn) roughly in the area the hand is currently near, not literally under the moving marker tip.

**Correct characterization**: the board fills in **line-by-line over time**, in a sensible top-to-bottom order roughly tracking the hand's position -- this is a real improvement over round 18's single-frame reveal, and the pixel-diff evidence in the summary above (15.9 / 10.9 mean change) is still valid evidence of genuine content change over time. But it is not genuine handwriting animation -- there is no letter-by-letter tracing, and the marker is not mechanically synced to what appears. This is closer to "lines fade in during a writing-themed shot" than "the lawyer is actually writing."

## 4. What this means

| Question | Answer |
|---|---|
| Was round 18's near-perfect result an artifact of skipping the writing animation? | Partially answered -- forcing a line-by-line reveal instead of a single static frame produced comparable text accuracy (4/5 exact vs. round 18's 3/5 exact plus 2 near-exact), so accuracy is not dependent on round 18's single-frame shortcut. But this round does not show genuine handwriting, so the deeper question (does accuracy hold under *real* letter-by-letter writing) is still open. |
| Is the wrap-point duplication defect specific to the "File Ad Refunds" line? | No -- it appeared on line 2 this time instead of line 5, so it's not tied to one specific line's content; it looks like a general line-wrap artifact that can hit whichever line happens to wrap at that point in a given generation. |
| Does this change the practical recommendation? | Modestly -- Wan 3.0 with this prompt produces a line-by-line reveal with good text accuracy, which is visually better than round 18's single static frame, but it is not the "lawyer actually writing" shot a real deliverable likely wants. If true letter-tracing handwriting is a hard requirement, this prompt does not deliver it. |
| Does this close the text-accuracy question? | No on two counts: the wrap-duplication defect is unresolved, and the marker-sync gap identified in section 3.1 means this is best described as a working text-accuracy result with an unconvincing writing animation, not a complete fix. |

## 5. Still to do

1. Test whether shortening lines 2 and 5 (to avoid a mid-sentence line wrap) eliminates the duplication defect under the writing-motion prompt, same open item as round 18.
2. Run a second writing-motion test with a different seed to confirm this result (4/5 exact, line-by-line reveal) is repeatable rather than a single lucky draw.
3. Investigate whether any prompt phrasing gets genuine marker-to-letter tracing rather than a line-by-line reveal -- current evidence (section 3.1) suggests this may be a hard limitation of the model rather than a prompt-engineering gap, so this should be treated as an open research question, not assumed fixable.
4. For any deliverable that requires visibly correct handwriting motion (not just a line-by-line reveal), flag this as an unresolved gap rather than treating round 18/19's results as sufficient.

## 6. Files

- `clips/wan30_writing_round19.mp4`: the generated clip.
- `raw/frame_{0,15,30,45,60,75,90,105,120,135,149}.png`: frames sampled across the full clip, used to confirm the board fills in over time via pixel-diff.
- `raw/sync_{20,25,35,40,50,55,65,70}.png`: tighter-spaced frames used to check whether the marker traces the letters (section 3.1) -- it does not.
- `raw/wan30_writing_frame_{000,060,149}.png`: the three frames used for direct text inspection (copies of frame_0, frame_60, frame_149).
- `raw/raw_record_wan30_writing.json`: generation record (request id, endpoint, payload including seed, timing).
- `run_fal_test.py`: the script used to submit, poll, and download the job via fal.ai's queue API. Reads the API key from `server/falAPI.txt` (git-ignored, never printed).
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$1.00, well within the remaining fal.ai balance from round 16's $25 top-up.
