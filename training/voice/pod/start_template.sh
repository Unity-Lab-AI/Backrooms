#!/usr/bin/env bash
# Pod start command for the RunPod-template path (official RunPod PyTorch image + network volume at /workspace).
# It replaces the custom image's start_no_training.sh for this path and fixes what made that path unsafe:
#   - training is NOT started from an SSH shell, so a dropped connection cannot end the run;
#   - this script is the container's main process, so RUNPOD_POD_ID / RUNPOD_API_KEY are in its environment and
#     the pod can stop itself; they are also written to /etc/rp_environment for SSH sessions (RunPod convention);
#   - the dataset arrives on the network volume beforehand over RunPod's S3 API (upload_volume_s3.ps1), so no
#     upload happens on GPU time;
#   - any refusal before the budget supervisor starts stops the pod after a short hold, so a refused launch
#     cannot bill indefinitely.
#
# Everything the run trains from is the hash-bound delivery packet already on the volume:
#   /workspace/incoming/delivery.tar   (made locally by run_expanded_preparation / the delivery step)
# This script is uploaded beside it as /workspace/incoming/start_template.sh and is the pod's start command:
#   bash /workspace/incoming/start_template.sh
#
# Required env at pod create (no defaults are guessed for money or identity):
#   VOICE_DELIVERY_SHA256  sha256 of delivery.tar (packet.json archive_sha256)
#   VOICE_DIGEST           approved source digest (VOICE_MANIFEST.json "digest" inside the packet)
#   VOICE_DATASET_ID       approved dataset identity (packet.json)
#   VOICE_VOLUME_ID        the network volume id mounted at /workspace
#   PRICE_PER_HOUR         the pod's hourly price as shown at create time
#   BUDGET_USD, KEEP_HOURS approved budget and post-run retention
# Optional: VOICE_FAIL_HOLD_MIN (default 10) minutes to keep a refused pod up for log reading before it stops;
#           VOICE_PROGRESS_HTTP=1 serves /workspace/out read-only on port 8000; ACOUSTIC_*/VOCODER_*/GTA_STEPS/VOICE_SEED.
set -uo pipefail
W=/workspace
IN="$W/incoming"
LOG="$W/launch.log"
mkdir -p "$W/out" "$W/state"
exec >> "$LOG" 2>&1
say() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" | tee "$W/out/status.txt"; }
say "start_template: container up"

# RunPod's own startup (sshd, env export) keeps working for the owner's SSH access.
if [ -x /start.sh ]; then /start.sh > "$W/runpod-start.log" 2>&1 & fi
# Make the provider identity visible to SSH sessions too (the custom-image path lost it there).
env | grep -E '^RUNPOD_' | sed 's/^/export /' > /etc/rp_environment 2>/dev/null || true

stop_self() {
  local why="$1" hold="${VOICE_FAIL_HOLD_MIN:-10}"
  say "REFUSED: $why -- pod stops in $hold min (read $LOG over SSH meanwhile)"
  sleep "$((hold * 60))"
  for attempt in 1 2 3 4 5; do
    if [ -n "${RUNPOD_POD_ID:-}" ] && timeout 20s runpodctl pod stop "$RUNPOD_POD_ID" >> "$LOG" 2>&1; then
      say "stop requested after refusal (attempt $attempt)"; break
    fi
    sleep 5
  done
  sleep infinity                                       # if the stop failed, stay up so SSH still works
}

GEN="${VOICE_GENERATE_ON_POD:-0}"
# Owner: "voice need two pod s remembre one is feeding into the other". With on-pod generation the voice is split over
# two pods sharing one network volume: VOICE_ROLE=generate makes and screens the clips, writes gen/READY and stops
# itself; VOICE_ROLE=train waits for gen/READY on the same volume and trains on those clips. VOICE_ROLE=both keeps
# generation and training in one pod.
ROLE="${VOICE_ROLE:-both}"
case "$ROLE" in generate|train|both) ;; *) echo "VOICE_ROLE must be generate, train or both" >&2; exit 2 ;; esac
if [ "$GEN" = "1" ]; then
  REQUIRED="VOICE_SOURCE_COMMIT VOICE_DIGEST VOICE_VOLUME_ID PRICE_PER_HOUR BUDGET_USD KEEP_HOURS RUNPOD_POD_ID"
else
  REQUIRED="VOICE_DELIVERY_SHA256 VOICE_DIGEST VOICE_DATASET_ID VOICE_VOLUME_ID PRICE_PER_HOUR BUDGET_USD KEEP_HOURS RUNPOD_POD_ID"
fi
for v in $REQUIRED; do
  [ -n "${!v:-}" ] || stop_self "missing $v"
done
command -v runpodctl >/dev/null 2>&1 || stop_self "runpodctl missing from this image (use the official RunPod PyTorch template)"
mountpoint -q "$W" || stop_self "$W is not a mount; attach the network volume $VOICE_VOLUME_ID"

if [ "$GEN" = "1" ]; then
  # On-pod generation: the source is a pinned commit (never a moving branch), checked against the approved digest.
  [[ "$VOICE_SOURCE_COMMIT" =~ ^[0-9a-f]{40}$ ]] || stop_self "VOICE_SOURCE_COMMIT must be a full 40-hex commit"
  ROOTSRC="$W/src-$VOICE_SOURCE_COMMIT"
  if [ ! -d "$ROOTSRC/.git" ]; then
    rm -rf "$ROOTSRC.tmp"
    git clone -q "${VOICE_SOURCE_REPO:-https://github.com/Unity-Lab-AI/Backrooms.git}" "$ROOTSRC.tmp"       && (cd "$ROOTSRC.tmp" && git checkout -q "$VOICE_SOURCE_COMMIT") && mv "$ROOTSRC.tmp" "$ROOTSRC"       || stop_self "could not clone commit $VOICE_SOURCE_COMMIT"
  fi
  GOT=$(cd "$ROOTSRC" && python3 training/voice/manifest.py --check) || stop_self "manifest check failed in the cloned source"
  [ "$GOT" = "$VOICE_DIGEST" ] || stop_self "cloned source digest $GOT is not the approved $VOICE_DIGEST"
  SRC="$ROOTSRC/training/voice"
  say "source $VOICE_SOURCE_COMMIT verified ($GOT)"
else
  # 1. The packet must be byte-exact before anything inside it is trusted.
  [ -f "$IN/delivery.tar" ] || stop_self "no $IN/delivery.tar on the volume (upload it with upload_volume_s3.ps1 first)"
  GOT=$(sha256sum "$IN/delivery.tar" | cut -d' ' -f1)
  [ "$GOT" = "$VOICE_DELIVERY_SHA256" ] || stop_self "delivery.tar sha256 $GOT is not the approved $VOICE_DELIVERY_SHA256"
  say "delivery.tar verified ($GOT)"

  # 2. Unpack once with the packet's own verifier (taken out of the verified tar), never re-unpacked on resume.
  D="$W/delivery/$VOICE_DATASET_ID"
  if [ ! -d "$D" ]; then
    T=$(mktemp -d)
    python3 - "$IN/delivery.tar" "$T" <<'PY' || stop_self "could not read the verifier out of delivery.tar"
import sys, tarfile
with tarfile.open(sys.argv[1], "r:") as tar:
    for name in ("source/training/voice/pod/accept_delivery.py", "source/training/voice/pod/atomic_publish.py"):
        data = tar.extractfile(name).read()
        open(sys.argv[2] + "/" + name.rsplit("/", 1)[1], "wb").write(data)
PY
    (cd "$T" && python3 accept_delivery.py "$IN/delivery.tar" "$D" --archive-sha256 "$VOICE_DELIVERY_SHA256" \
        --source-digest "$VOICE_DIGEST" --dataset-id "$VOICE_DATASET_ID") || stop_self "accept_delivery refused the packet"
    rm -rf "$T"
  fi
  SRC="$D/source/training/voice"
  [ -f "$SRC/pod/bootstrap_voice.sh" ] || stop_self "delivered source has no pod/bootstrap_voice.sh"
  say "delivery accepted at $D"
fi

if [ "$ROLE" != "generate" ]; then
# 3. Pinned environment in a venv on the volume (kept across pods; reinstalled only if the pin list changes).
REQ="$SRC/pod/requirements-template.txt"
REQ_SHA=$(sha256sum "$REQ" | cut -d' ' -f1)
if [ "$(cat "$W/venv/.requirements-sha256" 2>/dev/null)" != "$REQ_SHA" ]; then
  say "installing pinned packages into $W/venv"
  rm -rf "$W/venv"
  python3 -m venv "$W/venv" || stop_self "python3 -m venv failed"
  "$W/venv/bin/pip" install -q --upgrade pip || stop_self "pip upgrade failed"
  "$W/venv/bin/pip" install -q -r "$REQ" --extra-index-url https://download.pytorch.org/whl/cu126 \
      || stop_self "pinned package install failed (see $LOG)"
  echo "$REQ_SHA" > "$W/venv/.requirements-sha256"
fi
"$W/venv/bin/pip" freeze > "$W/out/pip-freeze.txt"
export PATH="$W/venv/bin:$PATH"
python3 -c "import torch; assert torch.cuda.is_available(); print('cuda ok', torch.__version__, torch.cuda.get_device_name(0))" \
    || stop_self "CUDA not usable in the venv"

# 4. Volume receipt from what this pod actually observes (the mount), and the billing start = container start.
RECEIPT="$W/state/volume-receipt.json"
if [ ! -f "$RECEIPT" ]; then
  python3 - "$RECEIPT" <<'PY' || stop_self "could not write the volume receipt"
import json, os, subprocess, sys, time
mount = subprocess.run(["findmnt", "-no", "SOURCE,FSTYPE,OPTIONS", "/workspace"], capture_output=True, text=True).stdout.strip()
df = subprocess.run(["df", "-B1", "/workspace"], capture_output=True, text=True).stdout.strip()
receipt = {"schema": "unity-voice-volume-receipt-v1", "decision": "accepted", "scope": "durable-volume-preflight",
           "volume_id": os.environ["VOICE_VOLUME_ID"], "mount_path": "/workspace",
           "verified_by": "start_template.sh automatic mount observation on pod " + os.environ["RUNPOD_POD_ID"],
           "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "provider_volume_evidence": "pod created with networkVolumeId=" + os.environ["VOICE_VOLUME_ID"],
           "mount_evidence": {"findmnt": mount, "df": df}}
with open(sys.argv[1], "x", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, indent=2)
PY
fi
export VOICE_VOLUME_RECEIPT="$RECEIPT"
export VOICE_VOLUME_RECEIPT_SHA256=$(sha256sum "$RECEIPT" | cut -d' ' -f1)
export VOICE_BILLING_STARTED_EPOCH=$(stat -c %Y /proc/1)
fi

# 5. Read-only progress view (GET/HEAD only; nothing here can start, extend or spend). Up before generation so
#    the owner can watch the clips being made, not only the training.
if [ "${VOICE_PROGRESS_HTTP:-0}" = "1" ]; then
  python3 -m http.server 8000 --bind 0.0.0.0 --directory "$W/out" > /dev/null 2>&1 &
  say "progress served read-only on port 8000"
fi

if [ "$GEN" = "1" ] && [ "$ROLE" = "train" ]; then
  # 5a. Training pod: the clips come from the clip pod through the shared volume.
  WAIT=$(python3 -c "import os; print(int(float(os.environ.get('VOICE_WAIT_HOURS', '1')) * 3600))")
  say "waiting for the clip pod (gen/READY, up to ${WAIT}s)"
  until [ -f "$W/gen/READY" ]; do
    [ "$SECONDS" -lt "$WAIT" ] || stop_self "no gen/READY from the clip pod within ${WAIT}s"
    sleep 60
  done
  DSDIR="$W/gen/dataset"
  VOICE_DATASET_ID=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['kept']['dataset_id'])" "$DSDIR/screen-report.json")
  cp "$DSDIR/screen-report.json" "$W/out/screen-report.json"
  say "clips from the clip pod: $(cat "$W/gen/READY")"
elif [ "$GEN" = "1" ]; then
  # 5b. Record the script on this pod, screen it, keep what passed. Generation runs BEFORE the budget supervisor,
  #     so it gets its own hard limit: the budget left since the pod started (92% rule), and never more than
  #     VOICE_GEN_MAX_HOURS (default 4). Running out stops the pod; finished shards stay on the volume.
  LIMIT=$(python3 -c "import os,time,sys; s=int(sys.argv[1]); cap=float(os.environ['BUDGET_USD'])/float(os.environ['PRICE_PER_HOUR'])*3600*0.92; used=time.time()-s; print(int(max(0, min(cap-used-1800, float(os.environ.get('VOICE_GEN_MAX_HOURS','4'))*3600))))" "$(stat -c %Y /proc/1)")
  [ "$LIMIT" -gt 600 ] || stop_self "not enough budget left to generate clips ($LIMIT s)"
  say "generating clips on this pod (limit ${LIMIT}s); progress in out/gen-progress.txt"
  ( while true; do
      { date -u +%FT%TZ; for d in "$W"/gen/render/shard-*; do [ -d "$d/wavs" ] && echo "$(basename "$d") $(ls "$d/wavs" | wc -l) clips"; done
        ls "$W/gen/state" 2>/dev/null | tr '
' ' '; echo; } > "$W/out/gen-progress.txt" 2>/dev/null; sleep 30; done ) &
  WATCH=$!
  timeout --signal=TERM --kill-after=60s "${LIMIT}s" bash "$SRC/pod/generate_on_pod.sh" "$ROOTSRC" "$W/gen" >> "$W/out/gen.log" 2>&1
  CODE=$?; kill "$WATCH" 2>/dev/null
  [ "$CODE" -eq 0 ] || stop_self "on-pod generation failed or ran out of time (exit $CODE; see out/gen.log)"
  cp "$W/gen/dataset/screen-report.json" "$W/out/screen-report.json"
  DSDIR="$W/gen/dataset"
  VOICE_DATASET_ID=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['kept']['dataset_id'])" "$DSDIR/screen-report.json")
  say "generated corpus ready: $(python3 -c "import json,sys; r=json.load(open(sys.argv[1])); print(r['kept_clips'], 'of', r['total_clips'], 'clips kept')" "$DSDIR/screen-report.json")"
  python3 -c "import json,sys; r=json.load(open(sys.argv[1])); print(r['kept']['dataset_id'], r['kept_clips'], 'of', r['total_clips'])" "$DSDIR/screen-report.json" > "$W/gen/READY"
  if [ "$ROLE" = "generate" ]; then
    say "clip pod finished; clips are on the volume for the training pod (gen/READY); stopping this pod"
    for attempt in 1 2 3 4 5; do
      timeout 20s runpodctl pod stop "$RUNPOD_POD_ID" >> "$LOG" 2>&1 && break; sleep 5
    done
    sleep infinity
  fi
else
  DSDIR="$D/dataset"
fi
export VOICE_ENV_MODE=template VOICE_DATASET_DIR="$DSDIR"
export VOICE_DIGEST VOICE_DATASET_ID VOICE_VOLUME_ID PRICE_PER_HOUR BUDGET_USD KEEP_HOURS RUNPOD_POD_ID

# 6. The budget supervisor (it trains on VOICE_DATASET_DIR), detached from any terminal. It stops the pod itself when work and retention end.
say "starting bootstrap_voice.sh (template mode)"
setsid nohup bash "$SRC/pod/bootstrap_voice.sh" >> "$W/bootstrap.log" 2>&1 < /dev/null &
BOOT=$!
wait "$BOOT"; CODE=$?
say "bootstrap_voice.sh exited $CODE"
# The budget supervisor requests the stop on its own exit path and records every attempt in out/stop-request.txt.
# No such record means bootstrap refused before the supervisor existed (closed gate, preflight): stop here instead.
[ -f "$W/out/stop-request.txt" ] || stop_self "bootstrap_voice.sh ended ($CODE) before its budget supervisor started"
# Stay up so a failed stop still leaves SSH access.
sleep infinity
