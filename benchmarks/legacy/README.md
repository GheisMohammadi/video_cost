[← Back to benchmarks/](../README.md)

# Legacy / unused scripts

These predate the round-based toolkit in `benchmarks/` and are kept for reference, not for new rounds.

| Script | Status | What it did |
|---|---|---|
| `wan22_ti2v_5b.py` | Used for round 0 | Ran the Wan 2.2 TI2V-5B pilot (a different, smaller model than round 1's A14B). Single manual run, no preflight, no guard. |
| `wan22_a14b_baseline.py` | Used for round 0 | Ran the first single A14B clips at 480p and 720p. Superseded by `wan22_a14b_session.py`, which adds preflight checks, telemetry, a quality gate and a frozen, multi-job list. |
| `run_on_pod.sh` | Used for round 0 | Installed dependencies and launched the scripts above on the pod. Superseded by `run_hour_session.sh`, which also arms the independent stop guard. |
| `wan22_a14b_saturate.py` | **Never run** | An early draft for a continuous, back-to-back request harness that saturates the GPU until a time limit is reached. Superseded before use by a fixed, frozen job list for a one-hour session (`wan22_a14b_session.py`), so this was never executed on a pod. Kept as a starting point for a future round that needs open-ended saturation testing rather than a fixed job list. |

If a future round needs true saturation testing (feed requests back-to-back until a time budget runs out, rather than a fixed list of jobs), start from `wan22_a14b_saturate.py` and bring it up to the same standard as `wan22_a14b_session.py` (preflight, quality gate, telemetry, frozen inputs) before trusting its numbers.
