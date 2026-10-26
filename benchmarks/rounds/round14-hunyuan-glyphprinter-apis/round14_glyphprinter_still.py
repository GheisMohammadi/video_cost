"""Round 14 B1: GlyphPrinter still of the lawyer whiteboard script.

Requires GlyphPrinter repo + weights under /workspace/GlyphPrinter (see run notes).
Writes /workspace/out/glyphprinter_B1_board.png and raw_record_B1.json.
"""
import os, json, time, hashlib, traceback, sys

OUT = "/workspace/out"
os.makedirs(OUT, exist_ok=True)

SCRIPT_LINES = [
    "Thousands of U.S. advertisers are pursuing claims against Google.",
    "Advertisers are filing refunds for 20-30% of Ad Spend since 2016.",
    "Federal courts have ruled Google illegally monopolized search advertising.",
    "Get the facts, fit criteria and risks.",
    "DOWNLOAD EXPLAINER File Ad Refunds ADREFUNDS.COM",
]

PROMPT = (
    "A realistic photo of a whiteboard filled with clear black handwritten English text, "
    "four body lines and one smaller line at the bottom, high contrast, legible, "
    "no person in frame. The board text is: "
    + " / ".join(f'"{t}"' for t in SCRIPT_LINES)
)


def log(*a):
    print(*a, flush=True)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    # GlyphPrinter's public entry is Gradio app / inference.py with saved conditions.
    # Prefer their CLI if present; otherwise fail clearly for the session log.
    gp_root = "/workspace/GlyphPrinter"
    if not os.path.isdir(gp_root):
        raise SystemExit("GlyphPrinter not installed at /workspace/GlyphPrinter")
    sys.path.insert(0, gp_root)
    t0 = time.time()
    # Deferred import after path setup — package layout follows upstream README.
    try:
        from inference import run_inference  # type: ignore
    except Exception:
        run_inference = None

    out_path = f"{OUT}/glyphprinter_B1_board.png"
    if run_inference is None:
        # Fallback: document that interactive condition setup is required.
        rec = {
            "job": "B1_glyphprinter",
            "status": "skipped_no_cli",
            "note": "GlyphPrinter inference API not importable as run_inference; install per upstream README and re-run",
            "prompt": PROMPT,
        }
        with open(f"{OUT}/raw_record_B1.json", "w") as f:
            json.dump(rec, f, indent=1)
        log("B1 skipped: no runnable CLI import")
        return

    run_inference(prompt=PROMPT, output_path=out_path)
    gen_s = time.time() - t0
    sha = sha256_file(out_path)
    rec = {
        "job": "B1_glyphprinter",
        "status": "ok",
        "prompt": PROMPT,
        "generate_s": gen_s,
        "sha256": sha,
        "file": "glyphprinter_B1_board.png",
    }
    with open(f"{OUT}/raw_record_B1.json", "w") as f:
        json.dump(rec, f, indent=1)
    log("B1 ok", gen_s, sha)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
