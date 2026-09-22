"""Pick the frozen job list for round 2 (run locally, needs `pip install sentencepiece`).

Tests what happens when a prompt asks for something this pipeline cannot produce: audio, a
resolution/aspect ratio other than the fixed render settings, or a duration longer than the
fixed clip length. One real prompt per category, matched by regex against the crawled corpus,
each checked to avoid pulling in a second category by accident (except the kitchen-sink case,
which deliberately combines several). All prompts are English and under 130 words, well under
the tokenizer's truncation limit, so token-count effects (already covered in round 1) are not a
factor here.

Categories:
  audio       explicit request for dialogue, music or sound
  resolution  explicit 4K/8K/UHD request
  aspect      explicit vertical/9:16/square request
  camera      camera-brand or lens-spec jargon (a real 27-step round 1 clip using this kind of
              prompt failed blind review; this checks whether that was a one-off or a pattern)
  duration    explicit request for more than 5 seconds
  kitchen_sink   a real prompt combining several of the above at once

Writes round2_jobs.json. Deterministic given the same corpus snapshot; commit before running.
"""
import json
from pathlib import Path

import sentencepiece as spm

PROMPTS = Path(__file__).parent.parent.parent / "prompts" / "prompts.jsonl"
SPIECE = Path(__file__).parent.parent.parent / "prompts" / "spiece.model"
sp = spm.SentencePieceProcessor(model_file=str(SPIECE))
rows = [json.loads(l) for l in PROMPTS.read_text().split("\n") if l.strip()]
by_url = {r["url"]: r for r in rows}

# Picked and hand-verified against the full prompt text for category purity (see round design notes).
PICKS = {
    "audio": "https://awesomevideoprompts.com/en/prompts/2052390610888233466-eternal-sands-pyramids",
    "resolution": "https://awesomevideoprompts.com/en/prompts/2087454978336063743-broken-machine-still-running",
    "aspect": "https://awesomevideoprompts.com/en/prompts/2047352971596595451-dimensional-rift-sorcerer",
    "camera": "https://awesomevideoprompts.com/en/prompts/2050882809502265669-astronaut-space-station",
    "duration": "https://awesomevideoprompts.com/en/prompts/2048983552906465742-floating-doors-surreal",
    "kitchen_sink": "https://awesomevideoprompts.com/en/prompts/2041109818581393888-multiverse-hero",
}

# fal-matched settings, identical to round 1, for direct comparability.
common = {"width": 832, "height": 480, "frames": 81, "fps": 16, "guidance": 3.5, "guidance_2": 4.0, "shift": 5.0}
jobs = []
for i, (cat, url) in enumerate(PICKS.items()):
    r = by_url[url]
    tokens = len(sp.encode(r["prompt"])) + 1
    jobs.append({"job": f"M{i+1}_{cat}", "block": "M_mismatch", "stratum": cat, "prompt_id": r["id"], "prompt": r["prompt"],
                 "source_url": url, "tokens": tokens, "steps": 27, "seed": 5100 + i, "expected_s": 575, **common})

warm = {"job": "W0_warmup", "block": "warmup", "stratum": "warmup", "prompt_id": PICKS["audio"].rsplit("/", 1)[-1].split("-", 1)[0],
        "prompt": by_url[PICKS["audio"]]["prompt"], "tokens": jobs[0]["tokens"], "steps": 4, "seed": 1,
        "expected_s": 100, **common}

out = {"version": 1, "note": "Round 2: capability-mismatch prompts. Frozen before running.",
       "warmup": warm, "jobs": jobs, "expected_total_s": sum(j["expected_s"] for j in jobs)}
(Path(__file__).parent / "round2_jobs.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
for j in jobs:
    print(j["job"], j["tokens"], "tokens, seed", j["seed"], "|", j["source_url"])
print("expected measured seconds:", out["expected_total_s"], "=", round(out["expected_total_s"] / 60, 1), "min")
