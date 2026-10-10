#!/usr/bin/env bash
# The pod's own launch command (set at create time -- no SSH needed). Pulls the training files from the repo
# branch, refuses to train anything but the exact data it was launched for, runs the whole training (run.sh) under
# a hard cost cap, and serves /workspace/gguf over HTTP on 8000 so progress (status.txt, run.log.txt) and the
# finished model download through the RunPod proxy: https://<pod-id>-8000.proxy.runpod.net/
#
# Required env (set at create time, nothing is guessed):
#   BRAIN_DIGEST   the "digest" from training/data/brain/MANIFEST.json that check_brain.py passed
#   PRICE_PER_HOUR the pod's price in USD/h as RunPod showed it at create time
# Optional: BUDGET_USD (default 25), KEEP_HOURS (default 1), SHELLS_BRANCH, SHELLS_REPO
set -u
W=/workspace; mkdir -p $W/gguf $W/state
BRANCH="${SHELLS_BRANCH:-feature/bug-testing}"
REPO="${SHELLS_REPO:-https://github.com/Unity-Lab-AI/Backrooms.git}"
cd $W
# read-only on purpose: http.server answers GET/HEAD for files in gguf/ and nothing else -- no endpoint here can
# start a run, extend the time, restart the pod, change the cap or reach the scripts. Nobody can spend through it;
# control stays with the owner's RunPod account, and the pod stops itself.
python3 -m http.server 8000 --directory $W/gguf >/dev/null 2>&1 &
SERVER=$!
status() { echo "$(date -u +%FT%TZ) $*" > $W/gguf/status.txt; }
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
BUDGET="${BUDGET_USD:-25}"
if ! python3 -c "import sys; p=float(sys.argv[1]); assert 0 < p < 20" "${PRICE_PER_HOUR:-x}" 2>/dev/null; then
  stop_pod "PRICE_PER_HOUR missing or not a price -- refusing to run without a cost cap"
fi
[ -f $W/state/started_at ] || date +%s > $W/state/started_at
CAP_S=$(python3 -c "import sys; print(int(float(sys.argv[1]) / float(sys.argv[2]) * 3600 * 0.92))" "$BUDGET" "$PRICE_PER_HOUR")
( while true; do
    used=$(( $(date +%s) - $(cat $W/state/started_at) ))
    echo "$used s used of $CAP_S s (budget \$$BUDGET at \$$PRICE_PER_HOUR/h)" > $W/gguf/cost.txt
    if [ "$used" -ge "$CAP_S" ]; then stop_pod "cost cap reached"; fi
    sleep 60
  done ) &

KEEP_HOURS="${KEEP_HOURS:-1}"
finish() {   # serve what exists for $1 hours (default KEEP_HOURS), then stop this pod; never sleeps forever
  sleep "$(python3 -c "import sys; print(int(float(sys.argv[1]) * 3600))" "${1:-$KEEP_HOURS}")"
  stop_pod "retention over"
}
fail() { status "FAILED: $*"; tail -c 20000 $W/run.log > $W/gguf/run.log.txt 2>/dev/null; finish 0.25; }

status "cloning"
rm -rf "$W/repo"          # a restart pulls the newest scripts and data, never a stale copy
git clone -q --depth 1 --filter=blob:none --sparse -b "$BRANCH" "$REPO" $W/repo && \
  (cd $W/repo && git sparse-checkout set --no-cone /training/pod/ /training/data/brain/ /training/data/tools.json \
     /training/check_player.py /training/check_voice.py /.local/autopilot/guards.py /.claude/tools/unity-voice.py) \
  || fail "clone of $BRANCH"
(cd $W/repo && git rev-parse HEAD) > $W/gguf/source-commit.txt
# hash-bound: the data must be byte for byte what was checked locally and approved at launch
GOT=$(cd $W/repo/training/data/brain && python3 - <<'EOF'
import hashlib, json
m = json.load(open("MANIFEST.json"))
for rel, want in m["files"].items():
    if hashlib.sha256(open(rel, "rb").read()).hexdigest() != want:
        print("MISMATCH:" + rel); raise SystemExit
print(hashlib.sha256("".join("%s  %s\n" % (m["files"][k], k) for k in sorted(m["files"])).encode()).hexdigest())
EOF
)
[ -n "${BRAIN_DIGEST:-}" ] && [ "$GOT" = "$BRAIN_DIGEST" ] || fail "data digest $GOT is not the approved ${BRAIN_DIGEST:-<unset>}"
rm -rf $W/data.new $W/pod.new; mkdir -p $W/data.new $W/pod.new
cp -r $W/repo/training/data/brain $W/data.new/brain || fail "copying training data"
cp $W/repo/training/pod/*.sh $W/repo/training/pod/*.py $W/pod.new/ || fail "copying pod scripts"
rm -rf $W/data $W/pod; mv $W/data.new $W/data; mv $W/pod.new $W/pod
status "training"
# progress visible from outside: the log is mirrored into the served folder every 30 s
( while true; do tail -c 20000 $W/run.log > $W/gguf/run.log.txt 2>/dev/null; ls $W/state > $W/gguf/state.txt 2>/dev/null; sleep 30; done ) &
if BRAIN_REPO=$W/repo bash $W/pod/run.sh; then status "DONE"; else fail "run.sh (see run.log.txt)"; fi
tail -c 20000 $W/run.log > $W/gguf/run.log.txt; ls $W/state > $W/gguf/state.txt
finish              # keep serving for the retention window, then stop
