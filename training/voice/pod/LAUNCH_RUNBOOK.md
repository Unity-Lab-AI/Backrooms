# Voice pod launch runbook (RunPod-template path)

> **On-pod generation mode (the owner's chosen design, 2026-10-12).** The pod records the 5,000-line script itself, screens every clip, trains on what passed, and everything comes home to `D:` afterwards. In this mode there is **no delivery.tar and no upload**: the pod clones the source at a pinned commit and checks it against the approved digest. Set `VOICE_GENERATE_ON_POD=1`, `VOICE_SOURCE_COMMIT=<40-hex commit>`, `VOICE_DIGEST=<VOICE_MANIFEST digest at that commit>`, `VOICE_VOLUME_ID`, `PRICE_PER_HOUR`, `BUDGET_USD`, `KEEP_HOURS`, `VOICE_PROGRESS_HTTP=1`, and optionally `GEN_SHARDS` (default 6) and `VOICE_GEN_MAX_HOURS` (default 4). Start command: `bash -c "git clone -q https://github.com/Unity-Lab-AI/Backrooms.git /tmp/b && cd /tmp/b && git checkout -q $VOICE_SOURCE_COMMIT && bash training/voice/pod/start_template.sh"`.
> - **Generation has its own hard time limit**, taken from the budget left since the pod started. Progress is in `out/gen-progress.txt` and `out/gen.log`, and the screen result is in `out/screen-report.json`.
> - **Corpus approval in this mode** is the owner approving the exact script files (`STREAM_CORPUS.jsonl`, `STREAM_EVENT_CORPUS.jsonl`, by hash) plus the screen rule (`keep only rows screened with no flags and a matching WAV hash`) and a minimum clip count. `quality_gate.py` then checks that every generated row came from that script. Steps A.1 (wait for the local job) and A.8 (upload) below do not apply in this mode.
> - **Proven so far:** the full generation chain ran locally on 26 lines (2 shards in parallel, merge, per-shard ASR screen, filter: 24 kept). Both teacher environments install and import on Linux (Docker, `python:3.10-slim`, torch 2.7.1+cu118), after three fixes: openai-whisper built against setuptools<70 without deps (its triton<3 pin dragged torch to 2.3.1), and torch pinned by `constraints-teacher.txt`.


**No pod is rented until the owner says so.** Owner, 2026-10-12: *"NO POD RENT UNTIL I SAY!"*, and the standing order *"let me know before u start a training"*. This runbook gets everything ready so that the go is one approved step.

## Why this path, not the custom image

ChatGPT's locked Docker image (`unity-a2-prep:20261011-v2`) is still a valid **image** mode (`VOICE_ENV_MODE=image`). It is not launchable today:
- **No registry.** The image exists only on this PC.
- **Self-stop fails.** Its sshd entrypoint drops the RunPod credentials, so the stop request can't authenticate.
- **SSH drops end the run.** Training starts from an SSH shell, and a hang-up tears it down.
- **The upload costs GPU time.** It's scp to a running H100.

The **template** path (`VOICE_ENV_MODE=template`) keeps ChatGPT's safety pieces (the quality gate, the hash-bound delivery packet, the fixed budget deadline, the process-group timeouts, the bounded stop retries, the run-ID namespacing) and fixes those four:

| Problem | Template path |
|---|---|
| Image needs a registry | Official RunPod PyTorch image; the pinned packages (`requirements-template.txt`, the same versions as the image) go into `/workspace/venv`, and `preflight_voice.py --template` checks them |
| Self-stop can't authenticate | `start_template.sh` is the container's main process (it has `RUNPOD_*`), and `bootstrap_voice.sh` reads them back from `/proc/1/environ` if a shell lost them |
| An SSH drop ends the run | The run starts from the start command under `setsid nohup`, and the supervisor ignores HUP |
| Upload on paid GPU time | `upload_volume_s3.ps1` puts the packet on the network volume over RunPod's S3 API, with **no pod running** |
| A refused launch keeps billing | `start_template.sh` stops the pod after `VOICE_FAIL_HOLD_MIN` (default 10) on any refusal before the budget supervisor exists |
| A restart on a new pod was refused | Resume keeps the **first** start and deadline. Only price, budget and volume must match, so a restart can only shorten the remaining budget |
| No progress view without SSH | `VOICE_PROGRESS_HTTP=1` serves `/workspace/out` read-only on port 8000 (status, logs, gpu.txt, progress samples) |
| GPU check only accepted an exact "H100" + image CUDA | Template mode accepts one sm_90 H100/H200; torch 2.7.1+cu126 is pinned by the venv |

## Steps

### A. Before the owner's go (no money spent)

1. Let the background preparation finish (`python .local/voice-lab/monitor.py`). It ends in `pipeline/result.json` and makes `pipeline/delivery/delivery.tar` + `packet.json`.
2. Owner listening and corpus decision (see `docs/implementation/VOICE_LEAD_REVIEW_2026-10-12.md` §8). Accept the corpus with `curate_dataset.py`, then flip the closed gates in `VOICE_QUALITY_GATE.json` the way `quality_gate.py` requires. Training stays refused until then, by design.
3. Merge `feature/voice-pod-ready` into the working branch. This changes frozen inputs, so it happens **only after the job ends**. Then regenerate `VOICE_MANIFEST.json` (`python training/voice/manifest.py`) and **rebuild the delivery packet**, so the packet carries the fixed pod scripts and the new digest.
4. Run the local 1-hour proof (review §6) and listen.
5. Install AWS CLI v2 (one UAC prompt): `msiexec /i https://awscli.amazonaws.com/AWSCLIV2.msi`.
6. **Owner, in the RunPod console:** Settings > S3 API Keys > Create. Give the session the user id (`user_...`) and the `rps_...` key as `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`. Nothing can make these through the API.

### B. On the owner's go

7. **Network volume** (billed per GB-hour until deleted; ~50 GB): create it in a data center that has **both** H100 stock **and** the S3 API. **US-MO-1** had H100 SXM ($3.99/h secure) on 2026-10-11; re-read live stock and price first.
8. Upload: `powershell -File training/voice/pod/upload_volume_s3.ps1 -PacketDirectory <pipeline/delivery> -VolumeId <id> -DataCenter US-MO-1`. Run it with `-DryRun` first. It reads back each object's size.
9. **Pod** (quote the hourly price to the owner first):
   - 1x H100 SXM, **secure cloud**, same data center, network volume at `/workspace`, CUDA ≥ 12.6 (`minCudaVersion 12.6`), port 8000/http
   - Image: the official RunPod PyTorch template (Ubuntu, Python 3.10+, runpodctl included)
   - Start command: `bash /workspace/incoming/start_template.sh`
   - Env: `VOICE_DELIVERY_SHA256`, `VOICE_DIGEST`, `VOICE_DATASET_ID`, `VOICE_VOLUME_ID` (printed by the upload), `PRICE_PER_HOUR` (as shown), `BUDGET_USD`, `KEEP_HOURS` (owner), `VOICE_PROGRESS_HTTP=1`
10. Watch `https://<pod-id>-8000.proxy.runpod.net/`: `status.txt`, `voice.log.txt`, `acoustic.log.txt` / `vocoder.log.txt` (held-out lines), `gpu.txt`, and `progress/<run>/…` samples every 30 min. Check the measured steps/s in the first hour against the estimate.

### C. After

11. **Bring everything home to the USB drive:** `powershell -File training/voice/pod/pull_results_s3.ps1 -VolumeId <id> -DataCenter US-MO-1 -RunName <name>`.
    - It copies the full screened dataset (every kept clip with its script line, the screen results, what was dropped and why), the trained models, the samples and every log to **`D:oice-lab\pod-results\<name>\`**, then checks every file's size against the volume.
    - Owner, 2026-10-12: *"why would i make them if they are only therei while its rented"*. The clips are the asset. They always come home, never to C:.
    - Listen with the owner.
12. **Delete the pod**, and delete the volume **only after step 11 reports VERIFIED** (the volume bills until deleted).

## What is still unproven (said plainly)

- None of this has run on RunPod. The template path is code-reviewed and syntax-checked; the PID-1 credential read was tested on a fake environ file. The official image's `/start.sh` and `/etc/rp_environment` behaviour is RunPod convention, not observed here.
- The student code is still unexecuted at scale. That is what the local 1-hour proof is for.
- The step and time estimates (acoustic 20k, vocoder 120k, ~9-10 h, ~$36-40 on an H100) were measured on the old code at 4070 speed and scaled. They are not measured on the new code or the 5,000-clip set.
