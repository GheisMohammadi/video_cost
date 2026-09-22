"""Build the blind review set for round 2 from a finished session (run locally).

Usage: python3 make_review_set.py SESSION_DIR REVIEW_DIR
Copies each delivered mismatch-category clip to REVIEW_DIR under a random name, padded to one
identical byte size so file size cannot reveal which category it was. Writes review_prompts.md
(the prompt text for each, since prompt_match needs to be checked against it),
review_scores.csv (one row per clip, fields to fill in), and REVIEW_DIR/_key/review_key.json
(clip name -> job name -> category). Do not open _key/ until every clip is scored.
"""
import csv
import json
import random
import shutil
import struct
import sys
from pathlib import Path

session, out = Path(sys.argv[1]), Path(sys.argv[2])
jobs = {}
for line in (session / "jobs.jsonl").read_text().split("\n"):
    if line.strip():
        r = json.loads(line)
        if r.get("measured") and r.get("delivered") and r.get("job") and (session / f"{r['job']}.mp4").exists():
            jobs[r["job"]] = r

job_list = json.load(open(Path(__file__).parent / "round2_jobs.json"))["jobs"]
prompt_of = {j["job"]: j["prompt"] for j in job_list}
category_of = {j["job"]: j["stratum"] for j in job_list}

names = [j for j in jobs if j != "W0_warmup"]
rng = random.SystemRandom()
rng.shuffle(names)

out.mkdir(parents=True, exist_ok=True)
(out / "_key").mkdir(exist_ok=True)
key, rows, md = {}, [], ["# Prompts for round 2 review\n\nScore prompt_match against what the text asks for. mismatch_handling: how did the clip handle the part of the prompt this pipeline cannot fulfil (ignored cleanly and rendered the rest well / visibly broke or looked rushed / misread the wording as literal content, e.g. an object instead of the intended scene)?\n"]
for i, job in enumerate(names, 1):
    name = f"C{i}"
    shutil.copy(session / f"{job}.mp4", out / f"{name}.mp4")
    key[name] = {"job": job, "category": category_of[job]}
    rows.append({"clip": name, "category_hidden_until_scored": "", "prompt_match": "", "mismatch_handling": "", "artifacts_notes": ""})
    md.append(f"## {name}\n\n{prompt_of[job]}\n")

sizes = {f: f.stat().st_size for f in out.glob("*.mp4")}
target = max(sizes.values()) + 64
for f, sz in sizes.items():
    pad = target - sz
    with open(f, "ab") as fh:
        fh.write(struct.pack(">I", pad) + b"free" + b"\0" * (pad - 8))

(out / "review_prompts.md").write_text("\n".join(md))
with open(out / "review_scores.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["clip", "category_hidden_until_scored", "prompt_match", "mismatch_handling", "artifacts_notes"])
    w.writeheader()
    w.writerows(rows)
json.dump(key, open(out / "_key" / "review_key.json", "w"), indent=1)
print(f"{len(rows)} clips in {out}, all padded to {target} bytes.")
print("prompt_match = pass|partial|fail. mismatch_handling: free text. Do not open _key/ until scoring is finished.")
