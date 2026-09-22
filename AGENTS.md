# AGENTS.md

Instructions for AI agents working in this repository.

## Secrets

- Never print, echo, log, quote, summarize, or paste any password, passphrase, token, or private key, in chat, in files, in commit messages, or in command output.
- Do not `cat`, `grep`, `head`, or otherwise display any file under `server/` (pod address, SSH key, passphrase). If a non-secret fact is needed from one of these files (for example an SSH target), extract only that fact with a targeted command, as `connect.sh` does.
- Do not use filters like `grep -v pass` to "hide" secrets — they miss lines. Extract only the specific value needed instead.
- Do not copy secrets into scripts, environment dumps, or docs. Reference the file path instead.
- Keep secret files out of git. `.gitignore` must keep covering `server/`, `connect.sh`, and any credential file such as an access token.
- If a secret is exposed by accident, say so immediately and recommend rotating it, without repeating the value.
- Using a credential to perform an action (for example, authenticating a `git push`) is fine once its purpose is confirmed, but never let the credential value itself appear in a command, its output, or a committed file — pass it through an askpass-style helper or an environment variable read directly from the file instead.

## Project

Video generation benchmarks and cost comparisons across hosted GPU providers, APIs, and bare-metal servers, in support of a distributed GPU network for AI video generation. See the root `README.md` for the project's structure and rounds index.

## Pod access

- `./connect.sh` opens an SSH session to the pod named in the file its `NOTES` variable points to under `server/`. Set `POD_NOTES=server/<file>.txt` to target a different pod-notes file if more than one exists. Key and passphrase are also read from `server/`.
- The SSH proxy only gives an interactive shell; a command passed directly to `./connect.sh` hangs. Pipe commands into stdin instead, ending with `exit`:
  `(sleep 8; echo 'nvidia-smi; exit'; sleep 5) | ./connect.sh`

## Pod environment: verify, do not assume

Container disk size, GPU model and driver, and how `/workspace` is mounted vary between pods and are not predictable from a previous session. Before caching model weights or starting a long job:
- Check free disk space (`df -h /`) and confirm the intended cache directory is not on a network filesystem (`df --output=fstype <dir>` should not report `fuse` or `nfs`; such mounts can report misleadingly large free space and be much slower than local disk).
- Prefer the local container disk for model-weight caches unless a network-mounted volume's throughput and quota have been confirmed.
- Some pod images preset `HUGGINGFACE_HUB_CACHE` (sometimes pointing at a network volume), which overrides `HF_HOME`. Set `HF_HOME`, `HF_HUB_CACHE`, and `HUGGINGFACE_HUB_CACHE` explicitly to the same, verified local path.
- Some images enable a fast-download feature flag (for example `HF_HUB_ENABLE_HF_TRANSFER=1`) without shipping the package it depends on. Install the required package and verify the import before relying on it, or the download will fail partway through.
- Run a GPU compute check (for example a small matrix multiply, timed) before starting any real job. A GPU can appear present but be non-functional; catching that immediately avoids billing for idle or broken compute.

## Long-running jobs

- Launch with `nohup ... &`, then poll a log file. Do not hold the SSH session open waiting for output — long waits over this kind of proxy are unreliable.
- Never run `pgrep -f NAME` inside a wait loop whose own invoking command line also contains the literal string `NAME` — it will match itself. Use a bracket pattern (`pgrep -f '[N]AME'`) or invoke the check from a separate script file.
- For any job that costs money while it runs, use an independent stop mechanism (a separate watchdog process, not just the job's own exit path) so a stuck or crashed job cannot keep billing indefinitely. See `benchmarks/pod_guard.sh` for the pattern used in this repository.

## Copying files back from a pod

There is no `scp` or other file-transfer channel through the SSH proxy. To copy a file back: base64-encode it and print it between two marker lines inside the session, capture the output, decode it locally, and verify the result against a checksum computed on the pod (for example with `md5sum`). Terminal escape sequences can appear in the captured output, so match on line endings rather than line starts when parsing it.

## Stopping a pod

- From inside the pod: `runpodctl stop pod $RUNPOD_POD_ID` (the pod's own scoped credential is typically stop-only; a command like `runpodctl get pod` from inside the pod may return an authorization error even though the stop command works).
- Confirm before stopping if a session isn't clearly finished — stopping is not always reversible, and a stopped pod's disk contents are not guaranteed to persist. After stopping, verify the billing/spend rate has dropped, and note that restarting a pod may require re-downloading model weights.

## Benchmark organization

Reusable scripts live in `benchmarks/`; each test round (plan, clips, raw data, report) lives in `benchmarks/rounds/roundN-<slug>/`. See the root `README.md` for the rounds index and how to start a new round, and `benchmarks/README.md` for what each script does and the order they run in.

## Writing style for this repository

- Write documentation and code comments as stateless statements of fact: what a thing is, what it does, and why — not as a narrative of who decided what or when. A comment should stand on its own to someone with no memory of how the code came to be.
- Do not name or refer to any individual, account, username, or team by name in code, comments, commit messages, or documentation. Use role-neutral phrasing (for example "the hosting provider's panel" rather than naming a specific person who read it) or state the fact directly (for example "the disk unit is assumed" rather than attributing the assumption to someone).
- Do not add tool, product, or vendor attribution for whatever produced a change (no "generated by", "co-authored by", or similar) in commit messages, pull request descriptions, or file contents, unless explicitly asked for.
