[← All rounds](../../../README.md)

# Round 28: digital whiteboard-wipe handoff for outfit consistency

Status: superseded by round 29 for the line-wrap-overflow fix; the
whiteboard-wipe mechanism itself carries forward unchanged. Round 27 fixed
chain-length text garbling by restarting the I2V chain with a fresh
text-to-video generation at row 5, but that let the model reinvent the
presenter's outfit. This round replaces that restart with a digital
whiteboard-wipe: the chain-anchor frame's board region is cleaned via OpenCV
inpainting (ink erased, everything outside the board rectangle untouched)
before being fed forward as the next row's `start_image_url`, with a prompt
describing her wiping the board clean in-scene.

## Watch the preview

<video src="clips/round28_preview_rows1to7.mp4" controls width="260"></video>

(Rows 1-7 only -- row 8 failed in this round, see below. Not captioned; a sync/continuity preview, not a finished deliverable.)

## 1. Summary

- **Outfit/presenter consistency fixed.** All pixels outside the board
  rectangle in the wipe-handoff anchor frame are byte-identical to the
  source frame, so the model has no room to reinvent the woman's appearance
  the way round 27's fresh restart did. Verified: same outfit, hair, board,
  and room across the wipe handoff at row 5.
- **Board-ink inpainting (`wipe_board.py`) works cleanly.** An earlier
  flat-fill/stretched-patch approach left visible ghosting and stretch
  artifacts; switching to `cv2.inpaint` (`INPAINT_TELEA`) blended naturally
  with the board's existing smudges and fully erased the ink.
- **Side-finding on round 27's garbling defect**: row 5, at the same hop
  depth that garbled text twice in round 27, did NOT garble here -- evidence
  that round 27's garbling was driven by accumulated-text complexity (dense,
  re-encoded handwriting) rather than pure hop-count.
- **New defect found: board-space overflow (row 8).** Text was now wrapping
  across 2 board lines per sentence (vs. round 27's 1 line), using up space
  faster. Row 8's correct text ("on TikTok.") was written mid-clip, then
  later overwritten onto the same line as the prior sentence when the board
  ran out of vertical room -- a different failure mode from round 27's
  garbling. Fixed in round 29 via an explicit compact-handwriting /
  single-line rule.

## 2. What was run

| Item | Value |
|---|---|
| Model | Wan 3.0 text-to-video (row 1) and image-to-video (every other row), via fal.ai |
| Seed | 10001 |
| Rows | 8 attempted, 7 succeeded (1-7 clean, 8 failed on board overflow) |
| Resolution / aspect | 720p, 9:16 |
| Generation time | ~125-130s per clip |

`run_fal_test.py` usage: `python3 run_fal_test.py <row 1-8> [prev_clip_path] [wipe]`. Passing `wipe` as the 3rd argument triggers the board-ink inpainting handoff instead of normal I2V chaining.

Fixes carried into every prompt (same as round 27): `ONSET_RULE` (no ink before marker contact) and `NO_ECHO_RULE` (no repeating prior rows' text).

## 3. The wipe mechanism

```
img = cv2.imread(in_path)
region = img[y0:y1, x0:x1].copy()
gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
ink_mask = (gray < 180).astype(np.uint8) * 255
ink_mask = cv2.dilate(ink_mask, np.ones((5, 5), np.uint8))
cleaned_region = cv2.inpaint(region, ink_mask, 7, cv2.INPAINT_TELEA)
img[y0:y1, x0:x1] = cleaned_region
```

Board rectangle used: `(390, 90, 720, 1150)` in this project's 720x1280 framing. The prompt for the handoff row narratively describes her wiping the board clean (raises her hand, wipes left to right, confirms it's clean) so the blank board is justified in-scene rather than appearing as an unexplained jump cut.

## 4. The row-8 board-overflow defect

Frame-by-frame audit (checking an intermediate frame, not just the final one) found "business." correctly written mid-clip, then overwritten by "on TikTok." directly on the same board line in the final frame -- the board ran out of vertical space for a 4th wrapped line within that segment. Diagnosed cause: each sentence this round was wrapping across 2 lines instead of round 27's 1 line (unclear why -- possibly font-size/spacing variance between generations), using board space roughly twice as fast.

## 5. What this means

| Question | Answer |
|---|---|
| Does the whiteboard-wipe handoff fix round 27's outfit-consistency defect? | Yes, verified pixel-consistent appearance across rows 1-7. |
| Is round 27's garbling driven by hop-count or by accumulated-text complexity? | Evidence favors complexity -- the same hop depth did not garble once the board was wiped clean first. |
| Does the wipe handoff introduce any new problem? | Yes -- board-space overflow when text wraps across multiple lines per sentence (row 8). Fixed in round 29. |

## 6. Files

- `clips/round28_preview_rows1to7.mp4`: preview of the clean portion (rows 1-7, rows 1-4 reused unchanged from round 27), uncaptioned.
- `clips/wan30_round28_row{5-7}.mp4`: wipe-handoff row 5 and chained rows 6-7, clean.
- `clips/wan30_round28_row8.mp4`: failed attempt, board-overflow defect.
- `run_fal_test.py`: generation script, see usage above.
- `wipe_board.py`: board-ink inpainting helper.
- `preview_rows1to7.py`: preview stitch script (no captions).
- `PLAN.md`: this round's plan, frozen before running.

## 7. Cost

~$4-5 (7 successful rows + 1 failed row-8 generation, all 5s/720p).
