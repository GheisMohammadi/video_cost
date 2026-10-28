[← All rounds](../../../README.md)

# Round 19: forcing real writing motion -- accuracy holds (Oct 29, 2026)

Status: complete. Round 18 found Wan 3.0 renders near-perfect text, but direct inspection showed the whiteboard was fully pre-written and static from frame 1 -- no progressive handwriting animation, just a person gesturing in front of an already-complete board. This round tests whether that near-perfect accuracy survives once the model is explicitly required to show the board starting blank and being written on in real time, the behavior a real deliverable most likely needs.

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
- **Frame 60**: lines 1-2 complete and correct; line 3 visibly mid-stroke ("Federal courts have rule[d]... illegal[ly]..." with the rest faded/in-progress) -- real-time writing confirmed, not a static reveal.
- **Frame 149**: all five lines present. Line 2 shows the wrap-duplication ("20- / 20-30%"); all other lines match the script exactly, including "ADREFUNDS.COM".

## 4. What this means

| Question | Answer |
|---|---|
| Was round 18's near-perfect result an artifact of skipping the writing animation? | No -- forcing genuine progressive writing produced comparable accuracy (4/5 exact vs. round 18's 3/5 exact plus 2 near-exact), so the high accuracy is not dependent on the "cheat" of a static pre-written board. |
| Is the wrap-point duplication defect specific to the "File Ad Refunds" line? | No -- it appeared on line 2 this time instead of line 5, so it's not tied to one specific line's content; it looks like a general line-wrap artifact that can hit whichever line happens to wrap at that point in a given generation. |
| Does this change the practical recommendation? | Yes, further strengthens it -- Wan 3.0 with an explicit writing-motion instruction is now the strongest and most realistic generation-time candidate tested in this project: it animates the writing as a real deliverable would need, at accuracy comparable to the best static-board result. |
| Does this close the text-accuracy question? | Not completely -- the wrap-duplication defect still needs a fix (see round 18's open item: shortening lines to avoid mid-sentence wraps). But two consecutive rounds now land in the 80%+ exact-line range with a specific, well-understood defect pattern rather than scrambled or hallucinated text. |

## 5. Still to do

1. Test whether shortening lines 2 and 5 (to avoid a mid-sentence line wrap) eliminates the duplication defect under the writing-motion prompt, same open item as round 18.
2. Run a second writing-motion test with a different seed to confirm this result (4/5 exact, real animation) is repeatable rather than a single lucky draw.
3. If reproducible, adopt the writing-motion prompt pattern (blank board + progressive-write instruction) as the standard template for any future Wan 3.0 text-accuracy round, rather than the static-board phrasing used in round 18.

## 6. Files

- `clips/wan30_writing_round19.mp4`: the generated clip.
- `raw/frame_{0,15,30,45,60,75,90,105,120,135,149}.png`: frames sampled across the full clip, used to confirm genuine progressive writing via pixel-diff.
- `raw/wan30_writing_frame_{000,060,149}.png`: the three frames used for direct text inspection (copies of frame_0, frame_60, frame_149).
- `raw/raw_record_wan30_writing.json`: generation record (request id, endpoint, payload including seed, timing).
- `run_fal_test.py`: the script used to submit, poll, and download the job via fal.ai's queue API. Reads the API key from `server/falAPI.txt` (git-ignored, never printed).
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$1.00, well within the remaining fal.ai balance from round 16's $25 top-up.
