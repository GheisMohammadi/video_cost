#!/usr/bin/env bash
# Runs ON THE POD: install the interpolation script's dependencies, then run it.
# Files expected in /root: interpolate_session.py, and an inputs manifest (e.g. inputs_combined.json)
# pointing at clips already present on the pod. Writes to /root/out5/ (a SEPARATE tree from
# round 6's /root/out/, since both share this pod and round 6's guard/marker/output must not be
# disturbed). Logs: /root/out5/session.log.
INPUTS=${1:-/root/inputs_combined.json}
mkdir -p /root/out5/session
pip install --no-cache-dir -q pillow numpy > /root/out5/pip_interp.log 2>&1
python3 /root/interpolate_session.py "$INPUTS" --out /root/out5/session --gpu-usd-h "${GPU_USD_H:-1.6}" --disk-usd-h "${DISK_USD_H:-0.028}" > /root/out5/session.log 2>&1
code=$?
echo "runner exit code $code" >> /root/out5/session.log
[ -f /root/out5/SESSION_DONE ] || echo "runner exited with $code" > /root/out5/SESSION_DONE
