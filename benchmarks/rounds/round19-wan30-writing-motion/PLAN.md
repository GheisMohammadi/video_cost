[← All rounds](../../../README.md)

# Round 19 plan: does Wan 3.0's accuracy survive forced writing motion?

## Why

Round 18 found Wan 3.0 renders 3 of 5 whiteboard lines exactly correct (the other 2 off by one duplicated word at a line wrap) -- the best text result in this project's history. But direct inspection found the whiteboard text is **static and fully pre-written from frame 1**, with no progressive handwriting animation -- only the lawyer's body and hand move. This may be why accuracy is so high: holding a fixed rendered board steady is a much easier task than animating someone writing it stroke-by-stroke, which is what every other round's prompt has nominally asked for and what a real deliverable most likely needs. Round 17 (Wan 2.7) showed the same static-board pattern on direct comparison of its three inspection frames.

## Test

Same five-line whiteboard script, same model and endpoint as round 18 (`alibaba/wan-3.0/text-to-video`), same seed (10001) for direct comparability -- but with the prompt changed to explicitly force progressive writing: describing the board as blank at the start, and the lawyer actively writing each line with the marker during the clip, rather than presenting an already-complete board.

## Question this answers

Does Wan 3.0's near-perfect text accuracy hold up once the model is required to actually animate the writing motion, or does accuracy degrade once real writing animation is introduced (the same failure pattern seen in every Wan 2.2 / HunyuanVideo round where text was shown being written)?

## Budget

Remaining fal.ai balance (~$22 left after rounds 16-18). Estimated cost for 1-2 test clips at 5s, 1080p: $1-2.

## Verification

Direct frame-by-frame inspection against the real script text, plus a frame-to-frame pixel-diff check on the whiteboard region specifically (the same method used in round 18 to confirm the text was static) to confirm whether writing motion is actually present this time.
