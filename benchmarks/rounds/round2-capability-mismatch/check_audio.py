"""Check whether each delivered clip has an audio stream (run locally, needs ffprobe).

This pipeline's configuration does not generate audio regardless of what a prompt asks for, so
every result here is expected to be "no". The point is to confirm that directly rather than
assume it, and to record it against the share of prompts that actually request audio.

Usage: python3 check_audio.py SESSION_DIR
Writes audio_check.json next to the clips.
"""
import json
import subprocess
import sys
from pathlib import Path

session = Path(sys.argv[1])
jobs = [json.loads(l) for l in (session / "jobs.jsonl").read_text().split("\n") if l.strip() and "skipped" not in l]
job_list = json.load(open(Path(__file__).parent / "round2_jobs.json"))["jobs"]
category_of = {j["job"]: j["stratum"] for j in job_list}

results = []
for j in jobs:
    clip = session / f"{j['job']}.mp4"
    if not clip.exists():
        continue
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                          "stream=codec_type", "-of", "csv=p=0", str(clip)], capture_output=True, text=True)
    results.append({"job": j["job"], "category": category_of.get(j["job"], "warmup"), "has_audio": bool(out.stdout.strip())})

json.dump(results, open(session / "audio_check.json", "w"), indent=1)
for r in results:
    print(r["job"], "(" + r["category"] + "):", "has audio" if r["has_audio"] else "no audio")
n_audio = sum(r["has_audio"] for r in results)
print(f"\n{n_audio} of {len(results)} clips have an audio stream.")
