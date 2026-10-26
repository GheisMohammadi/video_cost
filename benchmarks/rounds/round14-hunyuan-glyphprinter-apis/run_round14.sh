#!/usr/bin/env bash
# Runs ON THE POD: arm guard, install deps, run Hunyuan A1–A3.
set -euo pipefail
OUT=/workspace/out
mkdir -p "$OUT" /workspace/hfcache
export HF_HOME=/workspace/hfcache
export HF_HUB_CACHE=/workspace/hfcache
export HUGGINGFACE_HUB_CACHE=/workspace/hfcache
rm -f "$OUT/SESSION_DONE"

# Hard stop ~2.5h: one load + three ~35min gens + margin. Grace 20min for pull.
export HARD_S=${HARD_S:-9000}
export GRACE_S=${GRACE_S:-1200}
export IDLE_S=${IDLE_S:-1800}
export OUT_DIR=$OUT
export PROC_PATTERN='[r]ound14_hunyuan_session'
cp /workspace/pod_guard.sh /workspace/pod_guard_run.sh 2>/dev/null || true
nohup bash /workspace/pod_guard.sh > "$OUT/guard.out" 2>&1 &
echo "guard pid $!" >> "$OUT/session.log"
sleep 2

{
  echo "$(date -u '+%F %T') pip start"
  pip install --no-cache-dir -q -U 'diffusers>=0.35.0' transformers accelerate sentencepiece imageio imageio-ffmpeg hf_transfer hf_xet protobuf
  python3 -c "from diffusers import HunyuanVideo15Pipeline; print('import_ok')"
  echo "$(date -u '+%F %T') pip ok"
} >> "$OUT/pip.log" 2>&1 || {
  echo "deps failed" >> "$OUT/session.log"
  echo "deps failed" > "$OUT/SESSION_DONE"
  exit 1
}

python3 -u /workspace/round14_hunyuan_session.py >> "$OUT/session.log" 2>&1
code=$?
echo "runner exit code $code" >> "$OUT/session.log"
[ -f "$OUT/SESSION_DONE" ] || echo "runner exited with $code" > "$OUT/SESSION_DONE"
