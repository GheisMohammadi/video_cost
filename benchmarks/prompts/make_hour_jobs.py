"""Pick the fixed job list for the one-hour session (run locally, needs `pip install sentencepiece`).

Strata (real umt5 token counts, English = under 2% non-ASCII characters, no reference-image prompts):
  short     20-60 tokens
  median    340-410 tokens
  long      over 800 tokens (Wan truncates at 512)
  non-en    over 30% non-ASCII characters, 300-500 tokens (isolates language from truncation)
Then two steps-ladder jobs on the median prompt with the same seed (20 and 15 steps) for blind review.
Writes hour_test_jobs.json. Deterministic (fixed seed), commit it before running.
"""
import json
import random
from pathlib import Path

import sentencepiece as spm

HERE = Path(__file__).parent
sp = spm.SentencePieceProcessor(model_file=str(HERE / "spiece.model"))
rows = [json.loads(l) for l in (HERE / "prompts.jsonl").read_text().split("\n") if l.strip()]
usable = [r for r in rows if not r["needs_reference"]]
for r in usable:
    r["tokens"] = len(sp.encode(r["prompt"])) + 1
    r["nonascii"] = sum(ord(c) > 127 for c in r["prompt"]) / max(len(r["prompt"]), 1)

rng = random.Random(20260921)
pools = {
    "short": [r for r in usable if r["nonascii"] < 0.02 and 20 <= r["tokens"] <= 60],
    "median": [r for r in usable if r["nonascii"] < 0.02 and 340 <= r["tokens"] <= 410],
    "long": [r for r in usable if r["nonascii"] < 0.02 and r["tokens"] > 800],
    "non_english": [r for r in usable if r["nonascii"] > 0.30 and 300 <= r["tokens"] <= 500],
}
pick = {k: rng.choice(v) for k, v in pools.items()}
# fal-matched settings for 480p; expected seconds are rough estimates used only to size the measurement window
common = {"width": 832, "height": 480, "frames": 81, "fps": 16, "guidance": 3.5, "guidance_2": 4.0, "shift": 5.0}
jobs = []
for i, (k, r) in enumerate(pick.items()):
    jobs.append({"job": f"A{i+1}_{k}", "block": "A_strata", "stratum": k, "prompt_id": r["id"], "prompt": r["prompt"],
                 "tokens": r["tokens"], "steps": 27, "seed": 4200 + i, "expected_s": 560, **common})
med = pick["median"]; med_seed = 4200 + 1
for j, (steps, exp) in enumerate([(20, 420), (15, 320)]):
    jobs.append({"job": f"B{j+1}_median_{steps}steps", "block": "B_steps", "stratum": "median", "prompt_id": med["id"],
                 "prompt": med["prompt"], "tokens": med["tokens"], "steps": steps, "seed": med_seed, "expected_s": exp, **common})
warm = {"job": "W0_warmup", "block": "warmup", "stratum": "short", "prompt_id": pick["short"]["id"],
        "prompt": pick["short"]["prompt"], "tokens": pick["short"]["tokens"], "steps": 4, "seed": 1, "expected_s": 100, **common}
out = {"version": 1, "note": "Frozen before the session. Warm-up is excluded from queue cost but counted in all-in cost.",
       "warmup": warm, "jobs": jobs, "expected_total_s": sum(j["expected_s"] for j in jobs)}
(HERE / "hour_test_jobs.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
for j in jobs:
    print(j["job"], j["prompt_id"], "tokens", j["tokens"], "steps", j["steps"], "seed", j["seed"])
print("expected measured seconds:", out["expected_total_s"], "=", round(out["expected_total_s"] / 60, 1), "min")
print("pool sizes:", {k: len(v) for k, v in pools.items()})
