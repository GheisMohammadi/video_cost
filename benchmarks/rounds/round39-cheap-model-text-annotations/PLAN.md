# Round 39: continue the text+annotation task (rounds 35-38) on cheap models

Continuation of round 38 (which was blocked mid-chain on a fal.ai balance
exhaustion) and the user's cost-reduction directive -- test the actual
in-progress task (write 4 lines of text, then annotate with a rectangle
around "vibe-coded", a circle around "$99", and an underline under
"x.country") on the cheap models identified in round 40 (PixVerse V6,
MiniMax H3 Max Turbo), not a different task.

## Approach

Single-clip attempt first (round 36's proven structure: everything in one
15s generation), rather than immediately re-doing round 38's 7-step
chain, since:
- Round 38 showed the write-ahead failure reproduces on both Seedance
  tiers regardless of chaining, so chaining doesn't obviously fix the
  hardest remaining problem.
- A single-clip attempt is far cheaper to iterate on while screening
  whether these cheap models can handle this content at all.
- If a single clip proves unreliable on these models too, fall back to
  chaining as round 38 did for Seedance.

Condensed round 36's final prompt (`prompt_short.txt`, 1820 bytes) to fit
under PixVerse's 2048-byte cap, reused unchanged for MiniMax.

## What to check

Same as round 36's acceptance checks: all 4 lines text-accurate, no
reflection/ghost, no stray marks after any line, rectangle tightly around
"vibe-coded", circle tightly around "$99", underline close to "x.country"
only, progressive stroke growth (no pop-in), look-at-camera only at the
end.

## Budget

PixVerse: ~15s x $0.045/s = ~$0.675. MiniMax: ~15s x $0.028/s = ~$0.42.
~$1.10 total for one attempt per model -- confirm with the user before
retries, consistent with the project's standard practice.
