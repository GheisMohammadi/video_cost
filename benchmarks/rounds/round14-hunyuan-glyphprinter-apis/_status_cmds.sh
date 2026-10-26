echo STATUS_START
pgrep -af 'run_round14|pod_guard|round14_hunyuan|pip' || true
ls -la /workspace/out/ 2>/dev/null || true
tail -n 30 /workspace/out/session.log 2>/dev/null || true
tail -n 20 /workspace/out/pip.log 2>/dev/null || true
tail -n 5 /workspace/out/guard.log 2>/dev/null || true
test -f /workspace/out/SESSION_DONE && echo SESSION_DONE_YES || echo SESSION_DONE_NO
df -h /workspace | tail -1
echo STATUS_END
exit
