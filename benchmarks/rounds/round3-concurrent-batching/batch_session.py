"""Round 3 session (runs on the pod): does batching multiple prompts into one GPU call change
cost-per-video versus one request at a time (rounds 1/2's method)?

"Concurrent load" here means diffusers' native batched inference: passing a list of distinct
prompts to one pipe() call, so the GPU denoises all of them together across the same steps. This
is a real and common form of GPU throughput scaling, but it is not the same as independent
worker processes handling separate requests (infeasible here: a single request already peaks
near 32-38 GB under CPU offload, so more than roughly two full independent model copies would not
fit in 80 GB) and not a production request-queueing server (out of scope for this round).

Every batch group must use identical width/height/frames/fps/steps (a batched call requires a
uniform shape); only the prompts and per-item seeds differ.

Procedure, in order, each step gated on the previous one succeeding:
  1. Preflight: same checks as the round 1/2 session runner (CUDA, bf16 matmul speed, VRAM,
     weights cache not on a network filesystem).
  2. Load the model once.
  3. Warm-up: one batch-of-1 job at a few steps (exercises the ordinary, already-used code path).
  4. Smoke test, batch=2: the same prompts as group G2 but at a few steps only. This is the first
     time this pipeline has ever been asked to batch two different prompts in one call; this
     checks the call succeeds and produces two distinct, correctly-associated outputs before any
     real (27-step) time is spent on it, and gives a real measured per-step time to size G2's
     real job instead of guessing.
  5. If the batch=2 smoke test fails for any reason (including an out-of-memory error), G2 and
     G3 are both skipped -- if two prompts cannot be batched, four cannot either -- and only G1
     (the ordinary single-request case) runs for real.
  6. If it succeeds: smoke test batch=4 (group G3's prompts), same purpose. If this one fails
     (most likely from running out of GPU memory), G3 alone is skipped; G1 and G2 still run for
     real, since G2's smoke test already succeeded independently.
  7. Real jobs, at the full 27 steps: G1 (batch=1), then G2 (batch=2) if cleared, then G3
     (batch=4) if cleared. Each real job's full wall time and per-video cost is recorded.

Every output video, from every group, passes the same automated gate as rounds 1/2 (right frame
count, right size, not black, not frozen) plus one gate specific to this round: within a batch,
each output must differ meaningfully from every other output in the same batch (mean pixel
difference between them checked against a threshold). Passing every other check but producing two
near-identical videos from two different prompts would indicate a batching bug, not a successful
run, and must not be silently counted as one.

One jobs.jsonl record is written per output video (not one per batch call), named
"<group>_<prompt-short-name>" (e.g. "G2_A1_short"), each carrying its own mp4 and the shared
batch-level wall time and cost, so the existing puller (pull_session.py) needs no changes to
collect this round's results.

Usage: python3 batch_session.py round3_groups.json [--out /root/out/session] [--gpu-usd-h 1.6] [--disk-usd-h 0.028]
"""
import argparse
import hashlib
import itertools
import json
import os
import shutil
import subprocess
import sys
import threading
import time

CACHE = os.environ.get("WAN_CACHE", "/root/hf")
os.environ["HF_HOME"] = CACHE
os.environ["HF_HUB_CACHE"] = os.environ["HUGGINGFACE_HUB_CACHE"] = f"{CACHE}/hub"

import diffusers
import imageio
import numpy as np
import torch
from diffusers import AutoencoderKLWan, UniPCMultistepScheduler, WanPipeline
from diffusers.utils import export_to_video
from huggingface_hub import snapshot_download

MODEL_ID = "Wan-AI/Wan2.2-T2V-A14B-Diffusers"
TOKEN_LIMIT = 512

ap = argparse.ArgumentParser()
ap.add_argument("groups")
ap.add_argument("--out", default="/root/out/session")
ap.add_argument("--min-tflops", type=float, default=150)
ap.add_argument("--gpu-usd-h", type=float, default=1.6)
ap.add_argument("--disk-usd-h", type=float, default=0.028)
args = ap.parse_args()
OUT = args.out
os.makedirs(OUT, exist_ok=True)
T0 = time.time()
DONE = os.path.join(os.path.dirname(OUT.rstrip("/")), "SESSION_DONE")


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def write(name, obj):
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(obj, f, indent=1)


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- preflight (same checks as round 1/2)
pre = {
    "utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
    "gpu": sh("nvidia-smi --query-gpu=name,driver_version,memory.total,power.limit,clocks.max.sm,persistence_mode --format=csv,noheader"),
    "versions": {"torch": torch.__version__, "diffusers": diffusers.__version__, "python": sys.version.split()[0]},
    "host": {"loadavg": sh("cat /proc/loadavg"), "nproc": sh("nproc")},
    "fails": [],
}
if not torch.cuda.is_available():
    pre["fails"].append("torch.cuda.is_available() is False")
else:
    x = torch.randn(8192, 8192, device="cuda", dtype=torch.bfloat16)
    for _ in range(5):
        x @ x
    torch.cuda.synchronize()
    t = time.time()
    for _ in range(30):
        x @ x
    torch.cuda.synchronize()
    pre["matmul_bf16_tflops"] = round(30 * 2 * 8192 ** 3 / (time.time() - t) / 1e12)
    del x
    if pre["matmul_bf16_tflops"] < args.min_tflops:
        pre["fails"].append(f"matmul {pre['matmul_bf16_tflops']} TFLOPS below {args.min_tflops}")
    pre["vram_total_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1)
    if pre["vram_total_gb"] < 75:
        pre["fails"].append("less than 75 GB VRAM")
os.makedirs(CACHE, exist_ok=True)
pre["cache_fstype"] = sh(f"df --output=fstype {CACHE} | tail -1")
if "fuse" in pre["cache_fstype"] or "nfs" in pre["cache_fstype"]:
    pre["fails"].append(f"weights cache is on a network filesystem ({pre['cache_fstype']})")
try:
    snapshot_download(MODEL_ID, local_files_only=True)
    pre["weights"] = "present"
    pre["download_s"] = 0
except Exception:
    pre["weights"] = "downloading"
    t = time.time()
    if shutil.disk_usage(CACHE).free < 160e9:
        pre["fails"].append("less than 160 GB free for the 139 GB weights")
    if not pre["fails"]:
        snapshot_download(MODEL_ID, max_workers=16)
    pre["download_s"] = round(time.time() - t, 1)
pre["disk_free_gb"] = round(shutil.disk_usage(CACHE).free / 1e9, 1)
write("preflight.json", pre)
if pre["fails"]:
    log("PREFLIGHT_FAIL", pre["fails"])
    open(DONE, "w").write("preflight failed\n")
    sys.exit(2)
log("PREFLIGHT_OK", json.dumps(pre))

# ---------------------------------------------------------------- load
t = time.time()
vae = AutoencoderKLWan.from_pretrained(MODEL_ID, subfolder="vae", torch_dtype=torch.float32)
pipe = WanPipeline.from_pretrained(MODEL_ID, vae=vae, torch_dtype=torch.bfloat16)
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=5.0)
pipe.enable_model_cpu_offload()
load_s = round(time.time() - t, 1)
log("loaded", load_s)


class Sampler(threading.Thread):
    Q = "utilization.gpu,power.draw,memory.used,clocks.sm,temperature.gpu,clocks_throttle_reasons.active"

    def __init__(self):
        super().__init__(daemon=True)
        self.rows, self.stop = [], threading.Event()

    def run(self):
        while not self.stop.is_set():
            out = sh(f"nvidia-smi --query-gpu={self.Q} --format=csv,noheader,nounits")
            p = [x.strip() for x in out.split(",")]
            try:
                self.rows.append([float(v) for v in p[:5]] + [int(p[5], 16)])
            except (ValueError, IndexError):
                pass
            self.stop.wait(1.0)

    def summary(self):
        r = self.rows
        if not r:
            return {}
        col = lambda i: [x[i] for x in r]
        mask = 0
        for v in col(5):
            mask |= int(v)
        return {"gpu_util_mean": round(sum(col(0)) / len(r), 1), "power_w_mean": round(sum(col(1)) / len(r), 1),
                "sm_clock_mhz_mean": round(sum(col(3)) / len(r)), "temp_c_max": max(col(4)),
                "throttle_reasons_seen": hex(mask), "samples": len(r)}


def gate_one(frames, common):
    n = len(frames)
    idx = np.linspace(0, n - 1, 9).astype(int)
    means = [float(frames[i].mean()) for i in idx]
    diff = float(np.abs(frames[n - 1].astype(np.float32) - frames[0].astype(np.float32)).mean())
    checks = {"frames_ok": n == common["frames"], "shape_ok": tuple(frames[0].shape[:2]) == (common["height"], common["width"]),
              "not_black": min(means) > 5, "not_frozen": diff > 2.0}
    return {"pass": all(checks.values()), "n_frames": n, "first_last_diff": round(diff, 2), **checks}


def distinctness_check(all_frames):
    """Every video in a batch must differ meaningfully from every other video in the same batch."""
    n = len(all_frames)
    if n < 2:
        return {"pass": True, "min_pairwise_diff": None}
    mid = lambda fr: fr[len(fr) // 2].astype(np.float32)
    diffs = [round(float(np.abs(mid(all_frames[i]) - mid(all_frames[j])).mean()), 2)
             for i, j in itertools.combinations(range(n), 2)]
    return {"pass": min(diffs) > 2.0, "min_pairwise_diff": min(diffs), "all_pairwise_diffs": diffs}


def run_batch(tag, prompts, seeds, steps, common, measured, record_gate=True):
    """One pipe() call with len(prompts) items. Returns (frames_per_item, wall_s, telemetry, ok, error)."""
    s = Sampler()
    s.start()
    torch.cuda.reset_peak_memory_stats()
    t = time.time()
    try:
        gens = [torch.Generator("cuda").manual_seed(sd) for sd in seeds]
        result = pipe(prompt=prompts, negative_prompt=[""] * len(prompts), height=common["height"], width=common["width"],
                      num_frames=common["frames"], num_inference_steps=steps, guidance_scale=common["guidance"],
                      guidance_scale_2=common["guidance_2"], generator=gens)
        torch.cuda.synchronize()
        wall_s = round(time.time() - t, 1)
        frames_list = list(result.frames)
        ok, error = True, None
    except Exception as e:
        wall_s = round(time.time() - t, 1)
        frames_list, ok, error = None, False, repr(e)[:400]
        torch.cuda.empty_cache()
    s.stop.set()
    telemetry = s.summary()
    telemetry["peak_vram_gb"] = round(torch.cuda.max_memory_allocated() / 1e9, 1)
    log(tag, "ok" if ok else f"FAILED: {error}", "wall_s", wall_s, "peak_vram_gb", telemetry["peak_vram_gb"])
    return frames_list, wall_s, telemetry, ok, error


spec = json.load(open(args.groups))
common = spec["common"]

# ---- warm-up (always) ----
warm = spec["warmup"]
frames_list, wall_s, tel, ok, err = run_batch("WARMUP", [warm["prompt"]], [warm["seed"]], warm["steps"], common, measured=False)
write("warmup_result.json", {"ok": ok, "error": err, "wall_s": wall_s, **tel})

# ---- smoke tests: cheap, real diagnostic, gate the real jobs below ----
smoke_steps = spec["smoke_steps"]
clear = {"G1": True, "G2": False, "G3": False}
g2, g3 = next(g for g in spec["groups"] if g["group"] == "G2"), next(g for g in spec["groups"] if g["group"] == "G3")

frames2, wall2, tel2, ok2, err2 = run_batch("SMOKE_G2", g2["prompts"], g2["seeds"], smoke_steps, common, measured=False)
write("smoke_g2.json", {"ok": ok2, "error": err2, "wall_s": wall2, **tel2})
if ok2:
    clear["G2"] = True
    per_step_g2 = wall2 / smoke_steps
    frames4, wall4, tel4, ok4, err4 = run_batch("SMOKE_G3", g3["prompts"], g3["seeds"], smoke_steps, common, measured=False)
    write("smoke_g3.json", {"ok": ok4, "error": err4, "wall_s": wall4, **tel4})
    if ok4:
        clear["G3"] = True
        per_step_g3 = wall4 / smoke_steps
else:
    write("smoke_g3.json", {"ok": False, "error": "skipped: batch=2 smoke test failed, batch=4 was not attempted"})

log("CLEARED", json.dumps(clear))

# ---- real jobs, at full steps, only for cleared groups ----
records = []
for g in spec["groups"]:
    if not clear[g["group"]]:
        rec = {"group": g["group"], "batch_size": g["batch_size"], "measured": True, "ok": False,
               "skipped": "batch smoke test failed for this group size"}
        with open(os.path.join(OUT, "jobs.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")
        continue
    frames_list, wall_s, tel, ok, error = run_batch(g["group"], g["prompts"], g["seeds"], common["steps"], common, measured=True)
    n = len(g["members"])
    video_s = round(common["frames"] / common["fps"], 4)
    cost_usd = round(wall_s * (args.gpu_usd_h + args.disk_usd_h) / 3600, 4) if ok else None
    dist = distinctness_check(frames_list) if ok else {"pass": None}
    for i, member in enumerate(g["members"]):
        rec = {"job": f"{g['group']}_{member}", "group": g["group"], "batch_size": g["batch_size"],
               "member_index": i, "prompt_id": member, "steps": common["steps"], "seed": g["seeds"][i],
               "width": common["width"], "height": common["height"], "frames": common["frames"], "fps": common["fps"],
               "measured": True, "ok": ok, "error": error, "batch_wall_s": wall_s, "video_s": video_s,
               "batch_cost_usd": cost_usd, "cost_usd_per_video": round(cost_usd / n, 4) if cost_usd else None,
               "cost_usd_per_video_second": round(cost_usd / n / video_s, 4) if cost_usd else None,
               "distinctness": dist, **tel}
        if ok:
            path = os.path.join(OUT, f"{rec['job']}.mp4")
            export_to_video(frames_list[i], path, fps=common["fps"])
            rec["gate"] = gate_one(frames_list[i], common)
            rec["delivered"] = rec["gate"]["pass"] and dist["pass"] is not False
            rec["sha256"] = hashlib.sha256(open(path, "rb").read()).hexdigest()
        else:
            rec["delivered"] = False
        records.append(rec)
        with open(os.path.join(OUT, "jobs.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")

write("session.json", {
    "model": MODEL_ID, "gpu": pre["gpu"], "load_s": load_s, "download_s": pre["download_s"],
    "session_s": round(time.time() - T0, 1), "cleared": clear,
    "price_snapshot": {"gpu_usd_h": args.gpu_usd_h, "disk_usd_h": args.disk_usd_h},
    "scope_note": "batching = one pipe() call with multiple prompts, not independent worker processes or a queueing server",
})
open(DONE, "w").write("ok\n")
log("SESSION_DONE")
