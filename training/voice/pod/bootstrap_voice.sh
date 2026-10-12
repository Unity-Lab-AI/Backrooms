#!/usr/bin/env bash
# Source-only voice bootstrap. Closed quality gates are checked before any server or
# training work. A fixed local deadline bounds work independently of status reporting.
# Cloud stop requests have bounded retries and recorded command acknowledgments.
# An acknowledged request is NOT proof that provider billing has ended.
# Durable volume/image/API credentials and interruption recovery still need acceptance.
#
# Required: VOICE_DIGEST, PRICE_PER_HOUR, RUNPOD_POD_ID, VOICE_DATASET_DIR,
# VOICE_DATASET_ID, VOICE_VOLUME_ID, VOICE_VOLUME_RECEIPT, VOICE_VOLUME_RECEIPT_SHA256;
# runpodctl must already be installed/configured. The volume receipt records a named
# engineering verifier's provider and mount observations, not a new owner questionnaire.
# Actual BUDGET_USD/KEEP_HOURS and provider billing-start epoch are required;
# work defaults in run_voice.sh remain candidates until the priced owner decision.
# Source is delivered as a hash-bound packet, never fetched from a moving branch.
set -euo pipefail
# RunPod puts RUNPOD_POD_ID / RUNPOD_API_KEY in the container's main-process environment. A shell that lost them
# (SSH session, custom entrypoint) reads them back from PID 1, so the stop request can authenticate.
if [ -z "${RUNPOD_POD_ID:-}" ] || [ -z "${RUNPOD_API_KEY:-}" ]; then
  while IFS= read -r -d '' kv; do
    case "$kv" in RUNPOD_POD_ID=*|RUNPOD_API_KEY=*) name="${kv%%=*}"; [ -n "${!name:-}" ] || export "$kv" ;; esac
  done < /proc/1/environ 2>/dev/null || true
fi
VOICE_ENV_MODE="${VOICE_ENV_MODE:-image}"
case "$VOICE_ENV_MODE" in image|template) ;; *) echo "REFUSED: VOICE_ENV_MODE must be image or template" >&2; exit 2 ;; esac
export VOICE_ENV_MODE
VOICE_SCRIPT=$(readlink -f "${BASH_SOURCE[0]}")
VOICE_SOURCE=$(cd "$(dirname "$VOICE_SCRIPT")/.." && pwd)
python3 "$VOICE_SOURCE/quality_gate.py" --stage train

# Refusal is finite even when this container cannot stop its already-created pod.
# Check locally before server/clone/install/training; no authenticated capability is
# claimed merely because an executable exists.
for tool in python3 runpodctl timeout setsid flock; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "REFUSED: missing $tool. No work started; stop any created pod in the owner's console." >&2
    exit 2
  }
done
: "${RUNPOD_POD_ID:?missing pod ID; no work can start}"
: "${VOICE_DIGEST:?approved source digest required}"
: "${PRICE_PER_HOUR:?displayed create-time hourly price required}"
: "${VOICE_DATASET_DIR:?explicit approved v2 labeled dataset required}"
: "${VOICE_DATASET_ID:?approved v2 dataset identity required}"
: "${VOICE_VOLUME_ID:?verified provider volume ID required}"
: "${VOICE_VOLUME_RECEIPT:?saved engineering volume/mount verification required}"
: "${VOICE_VOLUME_RECEIPT_SHA256:?exact verified volume receipt hash required}"
if [ "$VOICE_ENV_MODE" = image ]; then
  : "${VOICE_IMAGE_DIGEST:?prepared immutable image reference required}"
  : "${VOICE_ENVIRONMENT_RECEIPT:?prepared environment verification receipt required}"
  : "${VOICE_ENVIRONMENT_RECEIPT_SHA256:?exact prepared environment receipt hash required}"
fi
: "${BUDGET_USD:?actual approved budget required}"
: "${KEEP_HOURS:?actual approved retention required}"
: "${VOICE_BILLING_STARTED_EPOCH:?actual provider launch timestamp required; not training-start time}"
[[ "$RUNPOD_POD_ID" =~ ^[A-Za-z0-9_-]+$ ]] || { echo "REFUSED: invalid pod ID" >&2; exit 2; }
python3 - <<'PY'
import hashlib, json, os
from pathlib import Path
raw = Path(os.environ['VOICE_VOLUME_RECEIPT']).read_bytes()
if hashlib.sha256(raw).hexdigest() != os.environ['VOICE_VOLUME_RECEIPT_SHA256']:
    raise ValueError('Volume verification receipt hash differs')
receipt = json.loads(raw)
if (receipt.get('schema') != 'unity-voice-volume-receipt-v1' or receipt.get('decision') != 'accepted'
        or receipt.get('scope') != 'durable-volume-preflight' or receipt.get('volume_id') != os.environ['VOICE_VOLUME_ID']
        or receipt.get('mount_path') != '/workspace' or not receipt.get('verified_by')
        or not receipt.get('recorded_at') or not receipt.get('provider_volume_evidence') or not receipt.get('mount_evidence')):
    raise ValueError('Volume receipt needs a named engineering verifier, matching ID/mount and recorded observations')
# This validates the recorded attestation, not a provider API or the actual mounted device.
PY
if [ "$VOICE_ENV_MODE" = image ]; then
  python3 "$VOICE_SOURCE/pod/preflight_voice.py" --environment --source-digest "$VOICE_DIGEST"
else
  python3 "$VOICE_SOURCE/pod/preflight_voice.py" --template --source-digest "$VOICE_DIGEST"
fi
export BUDGET_USD KEEP_HOURS VOICE_BILLING_STARTED_EPOCH
W=/workspace
SERVE="$W/out"
mkdir -p "$SERVE" "$W/state"
status() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" > "$SERVE/status.txt"; }

stop_group() {
  local group="$1"
  [ "$group" -gt 0 ] || return 0
  if kill -0 -- "-$group" 2>/dev/null; then
    kill -TERM -- "-$group" 2>/dev/null || true
    sleep 5
    kill -KILL -- "-$group" 2>/dev/null || true
  fi
}

stop_cloud() {
  local attempt code
  for attempt in 1 2 3 4 5; do
    status "requesting pod stop; attempt $attempt of 5; provider billing unconfirmed"
    if timeout --signal=TERM --kill-after=5s 20s runpodctl pod stop "$RUNPOD_POD_ID" \
        > "$W/state/voice-stop-attempt-$attempt.log" 2>&1; then
      printf '%s request_acknowledged; billing_state_not_observed\n' "$(date -u +%FT%TZ)" \
          > "$SERVE/stop-request.txt"
      return 0
    else
      code=$?
      printf '%s attempt=%s exit=%s stop_unconfirmed\n' "$(date -u +%FT%TZ)" "$attempt" "$code" \
          >> "$SERVE/stop-request.txt"
    fi
    [ "$attempt" -eq 5 ] || sleep 2
  done
  status "STOP UNCONFIRMED: local work was stopped; owner must stop/check this pod in the console"
  printf '%s pod=%s stop request failed/timed out; provider billing may continue\n' \
      "$(date -u +%FT%TZ)" "$RUNPOD_POD_ID" > "$SERVE/STOP_UNCONFIRMED.txt"
  echo "STOP UNCONFIRMED: owner console intervention required" >&2
  return 1
}

if [ "${VOICE_BUDGET_SUPERVISED:-}" != "1" ]; then
  # One live supervisor per volume; do not change a previous budget/rate on resume.
  exec 9> "$W/state/voice-supervision.lock"
  flock -n 9 || { echo "REFUSED: another voice supervisor holds this volume" >&2; exit 2; }
  WORKER=0
  supervisor_exit() {
    local code=$?
    trap - EXIT TERM INT HUP
    stop_group "$WORKER"
    if ! stop_cloud; then
      [ "$code" -ne 0 ] || code=1
    fi
    exit "$code"
  }
  trap supervisor_exit EXIT
  trap 'exit 143' TERM
  trap 'exit 130' INT
  trap '' HUP          # a dropped terminal never ends a paid run
  CLOCK=$(python3 - "$W/state/voice-budget-v2.json" <<'PY'
import json, math, os, time
from pathlib import Path
path = Path(__import__('sys').argv[1])
price, budget, keep = (float(os.environ[k]) for k in ('PRICE_PER_HOUR', 'BUDGET_USD', 'KEEP_HOURS'))
if not all(math.isfinite(value) for value in (price, budget, keep)) or price <= 0 or budget <= 0 or keep < 0:
    raise ValueError('Price/budget must be finite positive values; retention must be finite nonnegative')
wall = budget / price * 3600
# Reserve at least three minutes for five bounded stop attempts/local cleanup.
seconds = int(wall - max(wall * .08, 180))
if seconds < 60:
    raise ValueError('Budget is too small to bound work plus stop retries')
now = int(time.time())
billing_start = int(os.environ['VOICE_BILLING_STARTED_EPOCH'])
if not 0 < billing_start <= now:
    raise ValueError('Billing start must be the actual recorded provider launch epoch')
record = {'schema': 'unity-voice-budget-v2', 'price_per_hour': price, 'budget_usd': budget,
          'volume_id': os.environ['VOICE_VOLUME_ID'], 'volume_receipt_sha256': os.environ['VOICE_VOLUME_RECEIPT_SHA256'],
          'billing_started_epoch': billing_start}
if path.exists():
    previous = json.loads(path.read_text(encoding='utf-8'))
    terms = ('schema', 'price_per_hour', 'budget_usd', 'volume_id')
    if any(previous.get(key) != record[key] for key in terms):
        raise ValueError('Saved budget/rate/volume differs; explicit accounting review required, never reset on resume')
    # A resume on a NEW pod (same volume) has a later billing start. The deadline stays the one computed from
    # the FIRST start, so a restart can only shorten the remaining budget, never extend it.
    record['billing_started_epoch'] = previous['billing_started_epoch']
    record['volume_receipt_sha256'] = previous['volume_receipt_sha256']
    started = previous['started_at']
else:
    started = billing_start
if isinstance(started, bool) or not isinstance(started, int) or not 0 < started <= now:
    raise ValueError('Invalid saved budget start time')
record.update(started_at=started, deadline_epoch=started + seconds)
if path.exists():
    if previous != record:
        raise ValueError('Saved deadline differs; refuse an extended/reset budget')
else:
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(record, stream, indent=2)
record['keep_seconds'] = int(keep * 3600)
record['remaining_seconds'] = max(0, record['deadline_epoch'] - now)
print(json.dumps(record, sort_keys=True))
PY
)
  export VOICE_CLOCK="$CLOCK"
  VOICE_DEADLINE_EPOCH=$(python3 -c "import json, os; print(json.loads(os.environ['VOICE_CLOCK'])['deadline_epoch'])")
  REMAINING=$(python3 -c "import json, os; print(json.loads(os.environ['VOICE_CLOCK'])['remaining_seconds'])")
  export VOICE_DEADLINE_EPOCH
  printf '%s\n' "$CLOCK" > "$SERVE/cost-clock.json"
  [ "$REMAINING" -gt 0 ] || { status "budget already expired; refusing work"; exit 2; }
  # Enforcement has no application watcher to silently die. If this timeout process
  # fails/exits, this parent stops its process group. Each trainer also has this deadline.
  status "starting fixed-deadline local supervisor; cloud stop remains unverified"
  setsid timeout --signal=TERM --kill-after=15s "${REMAINING}s" \
      env VOICE_BUDGET_SUPERVISED=1 bash "$VOICE_SCRIPT" &
  WORKER=$!
  if wait "$WORKER"; then
    status "configured work/retention ended; requesting provider stop"
    exit 0
  else
    code=$?
    status "supervised work ended with exit $code; local cleanup and stop request follow"
    exit "$code"
  fi
fi

# Internal work is refused without the exact recorded deadline. A manually invoked
# runner cannot silently obtain an unbounded budget.
python3 - "$W/state/voice-budget-v2.json" <<'PY'
import json, os, time
from pathlib import Path
record = json.loads(Path(__import__('sys').argv[1]).read_text(encoding='utf-8'))
if record.get('schema') != 'unity-voice-budget-v2' or record['deadline_epoch'] != int(os.environ['VOICE_DEADLINE_EPOCH']):
    raise ValueError('Supervisor deadline is missing or differs from the budget receipt')
if time.time() >= record['deadline_epoch']:
    raise ValueError('Fixed budget deadline has already expired')
PY
python3 - "$VOICE_SOURCE" "$VOICE_DATASET_DIR" "$VOICE_DATASET_ID" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
from dataset_contract import load_dataset
_, identity = load_dataset(sys.argv[2], verify_audio=True)
if identity['dataset_id'] != sys.argv[3]:
    raise ValueError('Supplied corpus differs from approved VOICE_DATASET_ID')
print('Approved v2 source identity verified; no listening acceptance implied')
PY
cd "$W"
# Output stays private on the verified volume; retrieve through direct SSH.
# No unauthenticated HTTP service is started as a training side effect.
SERVER=0
SNAPSHOT=0
work_exit() {
  local code=$?
  trap - EXIT TERM INT HUP
  [ "$SNAPSHOT" -eq 0 ] || kill "$SNAPSHOT" 2>/dev/null || true
  [ "$SERVER" -eq 0 ] || kill "$SERVER" 2>/dev/null || true
  exit "$code"
}
trap work_exit EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
trap '' HUP
state_snapshot() {
  ls "$W/state" 2>/dev/null || true
  for file in "$W"/voice-runs/*/state/*; do
    [ ! -f "$file" ] || echo "${file#"$W"/}"
  done
}
status "verifying delivered immutable source"
CLONE=$(cd "$VOICE_SOURCE/../.." && pwd)
printf '%s\n' "$VOICE_DIGEST" > "$SERVE/source-digest.txt"
GOT=$(python3 "$CLONE/training/voice/manifest.py" --check)
[ "$GOT" = "$VOICE_DIGEST" ] || { status "source digest differs from approval; no training"; exit 2; }
status "configured training work"
( while true; do
    tail -c 20000 "$W/voice.log" > "$SERVE/voice.log.txt" 2>/dev/null || true
    for name in acoustic vocoder; do
      { tail -n 3 "$W/$name.log" 2>/dev/null || true
        echo "--- heldout checks (not listening acceptance):"
        grep HELDOUT "$W/$name.log" 2>/dev/null | tail -n 20 || true
      } > "$SERVE/$name.log.txt"
    done
    state_snapshot > "$SERVE/state.txt"
    sleep 30
  done ) &
SNAPSHOT=$!
bash "$CLONE/training/voice/pod/run_voice.sh"
status "configured work complete; voice acceptance remains separate"
tail -c 20000 "$W/voice.log" > "$SERVE/voice.log.txt" 2>/dev/null || true
state_snapshot > "$SERVE/state.txt"
KEEP_SECONDS=$(python3 -c "import math, os; value=float(os.environ['KEEP_HOURS']); assert math.isfinite(value) and value >= 0; print(int(value*3600))")
sleep "$KEEP_SECONDS"
