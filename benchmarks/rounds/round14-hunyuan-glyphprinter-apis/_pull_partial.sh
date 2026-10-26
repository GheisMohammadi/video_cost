# Pull finished A1/A2 (and later A3) via base64 markers. Run pieces carefully.
echo PULL_START
cd /workspace/out
for f in hunyuan_A1_two_lines.mp4 hunyuan_A2_deferred_lines.mp4 hunyuan_A3_reorder.mp4 raw_record_A1_two_lines.json raw_record_A2_deferred_lines.json raw_record_A3_reorder.json jobs.jsonl session.json session.log guard.log; do
  if [ -f "$f" ]; then
    echo "HAVE:$f:$(wc -c < "$f"):$(md5sum "$f" | cut -c1-32)"
  else
    echo "MISS:$f"
  fi
done
echo PULL_META_END
# Emit A1 video
if [ -f hunyuan_A1_two_lines.mp4 ]; then
  echo B_A1_BEGIN
  base64 -w0 hunyuan_A1_two_lines.mp4
  echo
  echo B_A1_END
fi
exit
