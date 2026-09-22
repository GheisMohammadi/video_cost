#!/usr/bin/env bash
# Runs on the pod: install deps, then run the Wan2.2 smoke test. Log: /root/out/run.log
set -euo pipefail
mkdir -p /root/out /workspace/hf
export WAN_CACHE=/workspace/hf
pip install --no-cache-dir -q diffusers transformers accelerate sentencepiece ftfy imageio imageio-ffmpeg
python3 /root/wan22_ti2v_5b.py
echo DONE
