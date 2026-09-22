"""Build the blind review set from a finished session (run locally).

Usage: python3 make_review_set.py SESSION_DIR REVIEW_DIR
Creates REVIEW_DIR/ with randomly named clips, review_prompts.md, review_scores.csv, and REVIEW_DIR/_key/review_key.json.
DO NOT open _key/ until every clip is scored. Set B holds the same prompt and seed at 3 step counts; the reviewer sees no step count.
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
spec = json.load(open(Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).parent / "prompts" / "hour_test_jobs.json"))
prompt_of = {j["job"]: j["prompt"] for j in spec["jobs"]}
strata = [k for k in jobs if k.startswith("A") and not k.startswith("A2")]  # A2 is shown only in the steps set, never twice
steps_set = [k for k in jobs if k.startswith("B") or k == next((x for x in jobs if x.startswith("A2")), None)]
rng = random.SystemRandom()
rng.shuffle(strata)
rng.shuffle(steps_set)
out.mkdir(parents=True, exist_ok=True)
(out / "_key").mkdir(exist_ok=True)
key, rows, md = {}, [], ["# Prompts for review (score prompt_match against these)\n"]
for i, job in enumerate(strata, 1):
    name = f"S{i}"
    shutil.copy(session / f"{job}.mp4", out / f"{name}.mp4")
    key[name] = job
    rows.append({"clip": name, "set": "strata", "prompt_match": "", "artifacts_notes": "", "motion": "", "rank": ""})
    md.append(f"## {name}\n\n{prompt_of[job]}\n")
for i, job in enumerate(steps_set, 1):
    name = f"B{i}"
    shutil.copy(session / f"{job}.mp4", out / f"{name}.mp4")
    key[name] = job
    rows.append({"clip": name, "set": "steps (same prompt and seed)", "prompt_match": "", "artifacts_notes": "", "motion": "", "rank": ""})
if steps_set:
    md.append(f"## B1, B2, B3 (same prompt)\n\n{prompt_of.get(next((j for j in steps_set if j in prompt_of), steps_set[0]), '')}\n")
# pad every copy to the same byte size with a trailing MP4 "free" box (players ignore it)
sizes = {f: f.stat().st_size for f in out.glob("*.mp4")}
target = max(sizes.values()) + 64
for f, sz in sizes.items():
    pad = target - sz
    with open(f, "ab") as fh:
        fh.write(struct.pack(">I", pad) + b"free" + b"\0" * (pad - 8))
(out / "review_prompts.md").write_text("\n".join(md))
with open(out / "review_scores.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["clip", "set", "prompt_match", "artifacts_notes", "motion", "rank"])
    w.writeheader()
    w.writerows(rows)
json.dump(key, open(out / "_key" / "review_key.json", "w"), indent=1)
print(f"{len(rows)} clips in {out}, all padded to {target} bytes. prompt_match = pass|partial|fail; motion = more|same|less (relative, within set B); rank 1 = best (set B).")
print("Do not open _key/ until scoring is finished.")
