#!/usr/bin/env bash
# Independent stop guard. Start it BEFORE the benchmark; it does not depend on the benchmark code.
# It stops the pod when any of these happens:
#   1. hard deadline (HARD_S seconds after this script starts)
#   2. SESSION_DONE marker seen, then GRACE_S seconds to copy results out
#   3. the session process was seen running and then has been absent for IDLE_S seconds (crash)
# Env: HARD_S (default 4500 = 75 min), GRACE_S (default 900), IDLE_S (default 1200), DRY_RUN=1 to log instead of stopping,
#      OUT_DIR (default /root/out), PROC_PATTERN (default [w]an22_a14b_session).
HARD_S=${HARD_S:-4500}
GRACE_S=${GRACE_S:-900}
IDLE_S=${IDLE_S:-1200}
OUT_DIR=${OUT_DIR:-/root/out}
PROC_PATTERN=${PROC_PATTERN:-[w]an22_a14b_session}  # bracket trick: pgrep must not match its own command line
mkdir -p "$OUT_DIR"
LOG="$OUT_DIR/guard.log"
START=$(date +%s)
seen=0; gone_since=""; done_at=""

stop_pod() {
  echo "$(date -u '+%F %T') STOP: $1" >> "$LOG"
  if [ -n "$DRY_RUN" ]; then echo "DRY_RUN stop: $1" >> "$LOG"; exit 0; fi
  runpodctl stop pod "$RUNPOD_POD_ID" >> "$LOG" 2>&1
  exit 0
}

echo "$(date -u '+%F %T') guard armed: hard=${HARD_S}s grace=${GRACE_S}s idle=${IDLE_S}s" >> "$LOG"
while true; do
  now=$(date +%s)
  [ $((now - START)) -ge "$HARD_S" ] && stop_pod "hard deadline ${HARD_S}s"
  if [ -f "$OUT_DIR/SESSION_DONE" ]; then
    [ -z "$done_at" ] && done_at=$now
    [ $((now - done_at)) -ge "$GRACE_S" ] && stop_pod "session done plus grace ${GRACE_S}s"
  fi
  if pgrep -f "$PROC_PATTERN" > /dev/null; then
    seen=1; gone_since=""
  elif [ "$seen" = 1 ] && [ ! -f "$OUT_DIR/SESSION_DONE" ]; then
    [ -z "$gone_since" ] && gone_since=$now
    [ $((now - gone_since)) -ge "$IDLE_S" ] && stop_pod "session process gone for ${IDLE_S}s without SESSION_DONE"
  fi
  sleep 5
done
