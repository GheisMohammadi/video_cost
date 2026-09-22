#!/usr/bin/env python3
"""Copy session artifacts from the pod to this machine through the interactive RunPod proxy (no scp).

Usage: python3 benchmarks/pull_session.py DEST_DIR [--loop] [--interval 120] [--max-polls 60] [--stop-when-done]

Each poll copies jobs.jsonl / preflight.json / session.json and any finished clip not copied yet, and verifies md5.
A clip is copied only after its record is in jobs.jsonl (the runner writes the record after the file is complete).
--stop-when-done: after SESSION_DONE and a fully verified copy, run `runpodctl stop pod` on the pod. If anything failed
verification the pod is NOT stopped by this script (the independent guard still stops it later).
"""
import argparse
import base64
import hashlib
import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

CONNECT = str(Path(__file__).resolve().parent.parent / "connect.sh")
REMOTE = "/root/out/session"


def ssh(cmds, tail_wait=8, timeout=150):
    script = "stty -echo\n" + cmds + "\nexit\n"
    cmd = f"(sleep 8; printf %s {shlex.quote(script)}; sleep {tail_wait}) | perl -e 'alarm {timeout}; exec @ARGV' {CONNECT}"
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.replace("\r", "")


def tagged(out):
    """Return {tag: value} from lines like TAG:value (ignores the echoed command lines)."""
    res = {}
    for line in out.split("\n"):
        m = re.search(r"(?:^|[^A-Za-z0-9_])((?:LS|DONE|JL|F_[a-z]+|B_[A-Za-z0-9_]+|M_[A-Za-z0-9_]+)):(\S*)\s*$", line)
        if m and not m.group(2).startswith("$("):
            res[m.group(1)] = m.group(2)
    return res


def poll(dest, stop_when_done):
    out = tagged(ssh(
        f'cd {REMOTE}; echo "LS:$(ls *.mp4 2>/dev/null | tr \'\\n\' \',\')"; '
        f'echo "DONE:$([ -f /root/out/SESSION_DONE ] && echo yes || echo no)"; '
        f'echo "JL:$(base64 -w0 jobs.jsonl 2>/dev/null)"; '
        f'for f in preflight session; do echo "F_$f:$(base64 -w0 $f.json 2>/dev/null)"; done'))
    if "DONE" not in out:
        print("poll failed (no answer)", flush=True)
        return False, False
    dest.mkdir(parents=True, exist_ok=True)
    jl = base64.b64decode(out.get("JL", "")).decode() if out.get("JL") else ""
    if jl:
        (dest / "jobs.jsonl").write_text(jl)
    for name in ("preflight", "session"):
        v = out.get(f"F_{name}")
        if v:
            (dest / f"{name}.json").write_bytes(base64.b64decode(v))
    finished = {json.loads(l)["job"] for l in jl.split("\n") if l.strip() and "skipped" not in l}
    want = [j for j in finished if (out.get("LS") or "").find(j + ".mp4") >= 0]
    bad = 0
    for job in sorted(want):
        f = dest / f"{job}.mp4"
        if f.exists():
            continue
        r = tagged(ssh(f'cd {REMOTE}; echo "B_{job}:$(base64 -w0 {job}.mp4)"; echo "M_{job}:$(md5sum {job}.mp4 | cut -c1-32)"', tail_wait=10, timeout=200))
        data = base64.b64decode(r.get(f"B_{job}", "")) if r.get(f"B_{job}") else b""
        if data and hashlib.md5(data).hexdigest() == r.get(f"M_{job}"):
            f.write_bytes(data)
            print(f"copied {job}.mp4 ({len(data)} bytes, md5 ok)", flush=True)
        else:
            bad += 1
            print(f"copy of {job}.mp4 FAILED verification", flush=True)
    done = out.get("DONE") == "yes"
    all_copied = done and bad == 0 and all((dest / f"{j}.mp4").exists() for j in want) and (dest / "session.json").exists()
    print(f"poll: finished={len(finished)} copied={len(list(dest.glob('*.mp4')))} done={done} verified={all_copied}", flush=True)
    if all_copied and stop_when_done:
        print("STOP:", ssh('echo "STOP:$(runpodctl stop pod $RUNPOD_POD_ID 2>&1 | head -2 | tr \'\\n\' \' \')"', tail_wait=6, timeout=60).split("STOP:")[-1].strip()[:200], flush=True)
    return done, all_copied


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dest")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=int, default=120)
    ap.add_argument("--max-polls", type=int, default=60)
    ap.add_argument("--stop-when-done", action="store_true")
    a = ap.parse_args()
    dest = Path(a.dest)
    for i in range(a.max_polls if a.loop else 1):
        done, ok = poll(dest, a.stop_when_done)
        if ok:
            print("ALL_COPIED", flush=True)
            return
        if done and not ok:
            print("session finished but copy not verified; retrying", flush=True)
        if a.loop:
            time.sleep(a.interval)
    print("max polls reached", flush=True)


if __name__ == "__main__":
    main()
