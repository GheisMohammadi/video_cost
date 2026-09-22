#!/usr/bin/env bash
# Runs ON THE POD: arm the independent guard first, then install deps and run the session.
# Files expected in /root: pod_guard.sh, wan22_a14b_session.py, hour_test_jobs.json
# Logs: /root/out/guard.log, /root/out/session.log, results in /root/out/session/
# Weights go to /root/hf (local container disk). /workspace can be a slow network FUSE volume.
mkdir -p /root/out/session /root/hf
export WAN_CACHE=/root/hf
rm -f /root/out/SESSION_DONE
HARD_S=${HARD_S:-4500} GRACE_S=${GRACE_S:-900} nohup bash /root/pod_guard.sh > /root/out/guard.out 2>&1 &
sleep 2
# The pod image sets HF_HUB_ENABLE_HF_TRANSFER=1 but does not ship hf_transfer, so install it.
pip install --no-cache-dir -q diffusers transformers accelerate sentencepiece ftfy imageio imageio-ffmpeg numpy hf_transfer hf_xet > /root/out/pip.log 2>&1
if ! python3 -c "import diffusers, transformers, accelerate, imageio, hf_transfer" >> /root/out/pip.log 2>&1; then
  echo "dependency import check failed, see pip.log" > /root/out/session.log
  echo "deps failed" > /root/out/SESSION_DONE
  exit 1
fi
python3 /root/wan22_a14b_session.py /root/hour_test_jobs.json --out /root/out/session > /root/out/session.log 2>&1
code=$?
echo "runner exit code $code" >> /root/out/session.log
[ -f /root/out/SESSION_DONE ] || echo "runner exited with $code" > /root/out/SESSION_DONE
