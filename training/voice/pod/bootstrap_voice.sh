#!/usr/bin/env bash
# The voice pod's own launch command (set at create time -- no SSH needed). Same rails as the brain pod
# (training/pod/bootstrap.sh): pulls the voice scripts from the repo branch, refuses to train anything but the exact
# inputs it was launched for, runs run_voice.sh under a hard cost cap, and serves /workspace/out over HTTP on 8000
# (GET only) so progress (status.txt, voice.log.txt) and the finished voice download through the RunPod proxy:
# https://<pod-id>-8000.proxy.runpod.net/
# /workspace MUST be a network volume: a stopped or deleted pod then loses nothing, and a new pod on the same
# volume resumes from the last checkpoint with the cost clock still counting from the first start.
#
# Required env (set at create time, nothing is guessed):
#   VOICE_DIGEST   the "digest" from training/voice/VOICE_MANIFEST.json (python training/voice/manifest.py --check)
#   PRICE_PER_HOUR the pod's price in USD/h as RunPod showed it at create time
# Optional: BUDGET_USD (default 50), ACOUSTIC_STEPS, ACOUSTIC_FRAMES, VOCODER_STEPS, VOCODER_BATCH, GTA_STEPS (see run_voice.sh), KEEP_HOURS (default 1), SHELLS_BRANCH, SHELLS_REPO
set -u
W=/workspace; mkdir -p $W/out $W/state; SERVE=$W/out
BRANCH="${SHELLS_BRANCH:-feature/bug-testing}"
REPO="${SHELLS_REPO:-https://github.com/Unity-Lab-AI/Backrooms.git}"
cd $W
# read-only on purpose: http.server answers GET/HEAD for files in out/ and nothing else -- no endpoint here can
# start a run, extend the time, restart the pod, change the cap or reach the scripts. Nobody can spend through it;
# control stays with the owner's RunPod account, and the pod stops itself.
python3 -m http.server 8000 --directory $SERVE >/dev/null 2>&1 &
SERVER=$!
status() { echo "$(date -u +%FT%TZ) $*" > $SERVE/status.txt; }
stop_pod() {
  status "$* -- stopping pod"
  kill "$SERVER" 2>/dev/null
  if command -v runpodctl >/dev/null 2>&1 && [ -n "${RUNPOD_POD_ID:-}" ]; then runpodctl stop pod "$RUNPOD_POD_ID"; fi
  exit 0
}

# a pod that cannot stop itself must not start paid work
if ! command -v runpodctl >/dev/null 2>&1 || [ -z "${RUNPOD_POD_ID:-}" ]; then
  status "FAILED: runpodctl or RUNPOD_POD_ID missing -- this pod could not stop itself, so nothing was trained. Stop it from the RunPod console."
  wait "$SERVER"
fi
# ---- cost cap: wall time since the FIRST start of this pod (kept on the volume, so a restart never resets it)
BUDGET="${BUDGET_USD:-50}"
if ! python3 -c "import sys; p=float(sys.argv[1]); assert 0 < p < 20" "${PRICE_PER_HOUR:-x}" 2>/dev/null; then
  stop_pod "PRICE_PER_HOUR missing or not a price -- refusing to run without a cost cap"
fi
[ -f $W/state/voice_started_at ] || date +%s > $W/state/voice_started_at
CAP_S=$(python3 -c "import sys; print(int(float(sys.argv[1]) / float(sys.argv[2]) * 3600 * 0.92))" "$BUDGET" "$PRICE_PER_HOUR")
( while true; do
    used=$(( $(date +%s) - $(cat $W/state/voice_started_at) ))
    echo "$used s used of $CAP_S s (budget \$$BUDGET at \$$PRICE_PER_HOUR/h)" > $SERVE/cost.txt
    if [ "$used" -ge "$CAP_S" ]; then stop_pod "cost cap reached"; fi
    sleep 60
  done ) &

KEEP_HOURS="${KEEP_HOURS:-1}"
finish() {   # serve what exists for $1 hours (default KEEP_HOURS), then stop this pod; never sleeps forever
  sleep "$(python3 -c "import sys; print(int(float(sys.argv[1]) * 3600))" "${1:-$KEEP_HOURS}")"
  stop_pod "retention over"
}
fail() { status "FAILED: $*"; tail -c 20000 $W/voice.log > $SERVE/voice.log.txt 2>/dev/null; finish 0.25; }

status "cloning"
rm -rf "$W/repo"          # a restart pulls the newest scripts, never a stale copy
git clone -q --depth 1 --filter=blob:none --sparse -b "$BRANCH" "$REPO" $W/repo &&   (cd $W/repo && git sparse-checkout set --no-cone /training/voice/ /training/data/brain/train.jsonl)   || fail "clone of $BRANCH"
(cd $W/repo && git rev-parse HEAD) > $SERVE/source-commit.txt
# hash-bound: scripts, her voice vector and the text must be byte for byte what was approved at launch
GOT=$(cd $W/repo && python3 training/voice/manifest.py --check)
[ -n "${VOICE_DIGEST:-}" ] && [ "$GOT" = "$VOICE_DIGEST" ] || fail "input digest $GOT is not the approved ${VOICE_DIGEST:-<unset>}"
status "training"
( while true; do tail -c 20000 $W/voice.log > $SERVE/voice.log.txt 2>/dev/null
    for f in acoustic vocoder; do { tail -n 3 $W/$f.log; echo "--- held-out checks:"; grep HELDOUT $W/$f.log | tail -n 20; } > $SERVE/$f.log.txt 2>/dev/null; done
    ls $W/state > $SERVE/state.txt 2>/dev/null; sleep 30; done ) &
# step counts and batch sizes default inside run_voice.sh; env overrides pass straight through
if bash $W/repo/training/voice/pod/run_voice.sh; then status "DONE"; else fail "run_voice.sh (see voice.log.txt)"; fi
tail -c 20000 $W/voice.log > $SERVE/voice.log.txt; ls $W/state > $SERVE/state.txt
finish              # keep serving for the retention window, then stop
