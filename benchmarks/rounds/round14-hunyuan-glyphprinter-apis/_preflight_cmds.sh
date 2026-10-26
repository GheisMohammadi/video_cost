echo PREFLIGHT_START
df -h / /workspace 2>/dev/null || true
df --output=fstype,target / /workspace 2>/dev/null || true
nvidia-smi -L 2>/dev/null || true
python3 - <<'PY'
import time
try:
    import torch
    print("TORCH", torch.__version__)
    print("CUDA", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU", torch.cuda.get_device_name(0))
        t = torch.randn(2048, 2048, device="cuda")
        t0 = time.time()
        torch.mm(t, t)
        torch.cuda.synchronize()
        print("MATMUL_S", round(time.time() - t0, 3))
except Exception as e:
    print("PY_ERR", type(e).__name__, e)
PY
echo PREFLIGHT_END
exit
