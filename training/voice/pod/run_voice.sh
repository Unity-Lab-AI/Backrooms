#!/usr/bin/env bash
# Runs on the RunPod pod: Unity's own voice, trained from random weights, on one H100-class GPU.
# Source-only v2: explicitly supplied approved labeled metadata.jsonl/WAV corpus -> prep
# -> acoustic model and vocoder trained AT THE SAME TIME on the one GPU (the vocoder fills the gaps while the
#    acoustic model runs its alignment search on the CPU) -> when the acoustic model is done it exports its own
#    ground-truth-aligned mels and the vocoder spends its last GTA_STEPS learning those -> one sample per emotion.
# While it trains: timestamped progress samples every 30 min and gpu.txt (utilization).
# Worker stages are namespaced by source digest, dataset, frontend and work configuration.
# Every stage logs to /workspace/voice.log and leaves a marker in its private state directory, so a restart skips
# finished configured stages. Resume is proposed from periodic checkpoints; exact RNG
# continuity and interrupted-process recovery have not been accepted.
# /workspace MUST be the verified durable volume. Provider/mount evidence is required;
# these scripts do not prove survival across pod or volume deletion.
# Result in /workspace/out/models/<run-id> is one atomic checked pair; samples are separate.
# Legacy CSV generation and audition recordings are never automatically used as training data.
# Local deadline/stop safeguards exist in source; reliable live provider stopping and
# storage/recovery acceptance remain separate closed quality-gate checks.
set -euo pipefail
# Independent worker deadlines supplement the bootstrap's supervised process group.
# No direct/manual runner invocation is allowed without its recorded budget deadline.
for tool in python3 timeout setsid runpodctl; do
  command -v "$tool" >/dev/null 2>&1 || { echo "REFUSED: missing $tool" >&2; exit 2; }
done
: "${VOICE_DEADLINE_EPOCH:?fixed supervisor deadline required}"
: "${RUNPOD_POD_ID:?configured provider stop ID required}"
: "${VOICE_VOLUME_ID:?verified provider volume ID required}"
: "${VOICE_VOLUME_RECEIPT:?saved engineering volume/mount verification required}"
: "${VOICE_VOLUME_RECEIPT_SHA256:?verified volume receipt hash required}"
[ "${VOICE_BUDGET_SUPERVISED:-}" = "1" ] || { echo "REFUSED: run through the budget supervisor" >&2; exit 2; }
python3 - <<'PY'
import hashlib, json, os, time
from pathlib import Path
record = json.loads(Path('/workspace/state/voice-budget-v2.json').read_text(encoding='utf-8'))
if record.get('schema') != 'unity-voice-budget-v2' or record['deadline_epoch'] != int(os.environ['VOICE_DEADLINE_EPOCH']):
    raise ValueError('Runner deadline differs from its recorded budget')
if time.time() >= record['deadline_epoch']:
    raise ValueError('Fixed budget deadline expired')
raw = Path(os.environ['VOICE_VOLUME_RECEIPT']).read_bytes()
if hashlib.sha256(raw).hexdigest() != os.environ['VOICE_VOLUME_RECEIPT_SHA256']:
    raise ValueError('Volume receipt digest differs')
receipt = json.loads(raw)
if (receipt.get('schema') != 'unity-voice-volume-receipt-v1' or receipt.get('decision') != 'accepted'
        or receipt.get('scope') != 'durable-volume-preflight' or receipt.get('volume_id') != os.environ['VOICE_VOLUME_ID']
        or receipt.get('mount_path') != '/workspace' or not receipt.get('verified_by')
        or not receipt.get('recorded_at') or not receipt.get('provider_volume_evidence') or not receipt.get('mount_evidence')
        or record.get('volume_id') != receipt['volume_id']
        or record.get('volume_receipt_sha256') != os.environ['VOICE_VOLUME_RECEIPT_SHA256']):
    raise ValueError('Recorded volume identity/evidence differs from the supervisor budget')
PY
owned_groups=()
forget_group() {
  local target="$1" group
  local keep=()
  for group in "${owned_groups[@]}"; do
    [ "$group" = "$target" ] || keep+=("$group")
  done
  owned_groups=("${keep[@]}")
}
stop_owned_group() {
  local group="$1"
  if kill -0 -- "-$group" 2>/dev/null; then
    kill -TERM -- "-$group" 2>/dev/null || true
    sleep 2
    kill -KILL -- "-$group" 2>/dev/null || true
  fi
}
runner_exit() {
  local code=$? group
  trap - EXIT TERM INT HUP
  # Signal every sibling first, then allow one shared grace interval.
  for group in "${owned_groups[@]}"; do
    kill -TERM -- "-$group" 2>/dev/null || true
  done
  [ "${#owned_groups[@]}" -eq 0 ] || sleep 2
  for group in "${owned_groups[@]}"; do
    kill -KILL -- "-$group" 2>/dev/null || true
    wait "$group" 2>/dev/null || true
  done
  exit "$code"
}
trap runner_exit EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
trap '' HUP          # a dropped terminal never ends a paid run
remaining_seconds() {
  python3 - <<'PY'
import os, time
remaining = int(os.environ['VOICE_DEADLINE_EPOCH']) - int(time.time())
if remaining <= 0:
    raise ValueError('Fixed budget deadline reached; no new worker may start')
print(remaining)
PY
}
bounded_run() {
  local remaining process code input_fd
  remaining=$(remaining_seconds) || return 2
  # Preserve heredoc stdin across background launch instead of accepting /dev/null.
  exec {input_fd}<&0
  setsid timeout --signal=TERM --kill-after=10s "${remaining}s" "$@" <&"$input_fd" &
  process=$!
  exec {input_fd}<&-
  owned_groups+=("$process")
  if wait "$process"; then
    forget_group "$process"
    return 0
  else
    code=$?
    stop_owned_group "$process"
    forget_group "$process"
    return "$code"
  fi
}
# Preparation is not launch approval. Refuse before setup, generation, logs or training.
VOICE_SOURCE=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
python3 "$VOICE_SOURCE/quality_gate.py" --stage train
: "${VOICE_DIGEST:?approved source digest required}"
: "${VOICE_DATASET_DIR:?explicit approved labeled dataset directory required}"
: "${VOICE_DATASET_ID:?approved v2 dataset identity required}"
V="$VOICE_SOURCE"
GOT=$(python3 "$V/manifest.py" --check)
[ "$GOT" = "$VOICE_DIGEST" ] || { echo "Source digest differs from approval" >&2; exit 2; }
# Standard-library validation occurs before setup or training. It is not listening acceptance.
DATASET_IDENTITY=$(python3 - "$V" "$VOICE_DATASET_DIR" "$VOICE_DATASET_ID" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1])
from dataset_contract import load_dataset
_, identity = load_dataset(sys.argv[2], verify_audio=True)
if identity['dataset_id'] != sys.argv[3]:
    raise ValueError('Supplied corpus differs from approved VOICE_DATASET_ID')
print(json.dumps(identity, sort_keys=True))
PY
)
export DATASET_IDENTITY
W=/workspace; mkdir -p "$W/state" "$W/out/samples" "$W/out/progress"
exec > >(tee -a $W/voice.log) 2>&1
# Proposed H100 work defaults, not measurements on the newly approved corpus.
# The last GTA_STEPS use oracle aligned mels, not free-running predicted prosody.
# Owner: "make sure we are peggin these GPUS pod when we do it". Unless set explicitly, the acoustic frame budget and
# the vocoder batch scale with the GPU's measured VRAM: 96,000 frames and batch 32 per 80 GB (H100), never below
# those, frames rounded to 1,000 and batch to 8. Both trainers keep all features on the GPU (no data loader) and the
# acoustic model already trains in bf16 autocast; the model math is unchanged, only how much goes through per step.
VRAM_MIB=$(timeout 10s nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1)
VRAM_MIB=${VRAM_MIB:-81559}
SCALE_FRAMES=$(( (96000 * VRAM_MIB / 81559 + 500) / 1000 * 1000 )); [ "$SCALE_FRAMES" -ge 96000 ] || SCALE_FRAMES=96000
SCALE_BATCH=$(( (32 * VRAM_MIB / 81559) / 8 * 8 )); [ "$SCALE_BATCH" -ge 32 ] || SCALE_BATCH=32
ACOUSTIC_STEPS="${ACOUSTIC_STEPS:-20000}"; ACOUSTIC_FRAMES="${ACOUSTIC_FRAMES:-$SCALE_FRAMES}"
VOCODER_STEPS="${VOCODER_STEPS:-120000}"; VOCODER_BATCH="${VOCODER_BATCH:-$SCALE_BATCH}"; GTA_STEPS="${GTA_STEPS:-20000}"
echo "GPU memory ${VRAM_MIB} MiB -> ACOUSTIC_FRAMES=$ACOUSTIC_FRAMES VOCODER_BATCH=$VOCODER_BATCH"
VOICE_SEED="${VOICE_SEED:-17}"
export ACOUSTIC_STEPS ACOUSTIC_FRAMES VOCODER_STEPS VOCODER_BATCH GTA_STEPS VOICE_SEED
python3 - <<'PY'
import os
for key in ('ACOUSTIC_STEPS', 'ACOUSTIC_FRAMES', 'VOCODER_STEPS', 'VOCODER_BATCH', 'GTA_STEPS'):
    if not os.environ[key].isdigit() or int(os.environ[key]) < 1:
        raise ValueError(key + ' must be a positive integer')
if int(os.environ['ACOUSTIC_FRAMES']) < 3000 or int(os.environ['GTA_STEPS']) >= int(os.environ['VOCODER_STEPS']):
    raise ValueError('Invalid frame budget or GTA/source phase split')
if not os.environ['VOICE_SEED'].isdigit() or not 0 <= int(os.environ['VOICE_SEED']) < 2 ** 32:
    raise ValueError('VOICE_SEED must be an integer in 0..4294967295')
PY

# Require an already prepared, hash-bound image. No apt/pip/download mutation is
# performed on rented time. The receipt is separate engineering evidence.
if [ "${VOICE_ENV_MODE:-image}" = template ]; then
  bounded_run python3 "$V/pod/preflight_voice.py" --template --source-digest "$VOICE_DIGEST"
else
  bounded_run python3 "$V/pod/preflight_voice.py" --environment --source-digest "$VOICE_DIGEST"
fi
bounded_run python3 - "$V/pod/ENVIRONMENT_SPEC.json" <<'PY'
import json, os, sys
import torch
spec = json.load(open(sys.argv[1], encoding='utf-8'))
name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else ''
# One or two Hopper-class GPUs (H100 any form factor, or H200); with two, the acoustic model and the source vocoder
# each get one (owner: "no way to speed it up than 11 hrs?"). The image path also pins the exact CUDA runtime;
# the template path pins torch 2.7.1+cu126 through requirements-template.txt and preflight --template.
n = torch.cuda.device_count() if torch.cuda.is_available() else 0
ok = (n in (1, 2)
      and all(torch.cuda.get_device_capability(i) >= (9, 0)
              and any(tag in torch.cuda.get_device_name(i) for tag in ('H100', 'H200')) for i in range(n)))
if os.environ.get('VOICE_ENV_MODE', 'image') == 'image':
    ok = ok and torch.version.cuda == spec['torch_cuda']
if not ok:
    raise ValueError('Expected one or two H100/H200 (sm_90) with the pinned CUDA runtime; no training started')
print('CUDA device:', name, 'torch', torch.__version__, 'cuda', torch.version.cuda)
PY
RUN_CONFIG=$(python3 - "$V" <<'PY'
import json, os, sys
sys.path.insert(0, sys.argv[1])
from dataset_contract import ACOUSTIC_CONFIG, VOCODER_CONFIG, canonical_hash, frontend_identity
record = {'schema': 'unity-voice-run-v2', 'source_digest': os.environ['VOICE_DIGEST'],
          'dataset': json.loads(os.environ['DATASET_IDENTITY']), 'frontend': frontend_identity(),
          'acoustic_config': ACOUSTIC_CONFIG, 'vocoder_config': VOCODER_CONFIG,
          'work': {key: int(os.environ[key]) for key in ('ACOUSTIC_STEPS', 'ACOUSTIC_FRAMES',
                   'VOCODER_STEPS', 'VOCODER_BATCH', 'GTA_STEPS', 'VOICE_SEED')}}
print(json.dumps(dict(record, run_id=canonical_hash(record)), sort_keys=True))
PY
)
export RUN_CONFIG
RUN_ID=$(python3 -c "import json, os; print(json.loads(os.environ['RUN_CONFIG'])['run_id'])")
R="$W/voice-runs/$RUN_ID"; STATE="$R/state"; CKPT="$R/ckpt"; FEATS="$R/features"
mkdir -p "$STATE" "$CKPT"
python3 - "$R/run-config.json" <<'PY'
import json, os, sys
from pathlib import Path
path = Path(sys.argv[1]); record = json.loads(os.environ['RUN_CONFIG'])
if path.exists():
    if json.loads(path.read_text(encoding='utf-8')) != record:
        raise ValueError('Run namespace configuration differs; preserve it')
else:
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(record, stream, indent=2)
PY
done_() { touch "$STATE/$1"; echo "=== $(date -u +%FT%TZ) configured stage complete: $1"; }
have() { [ -f "$STATE/$1" ]; }
echo "v2 worker namespace $RUN_ID; legacy features/checkpoints/stage markers are not reused"
# Always revalidate exact immutable features, including on a marked/resumed run.
bounded_run python3 "$V/prep.py" "$VOICE_DATASET_DIR" "$FEATS"
done_ prep

render_samples() {
  python3 "$V/pod/render_eval.py" "$FEATS" "$1" "$2"
}

# Sample rendering is evaluation only and stays inside a bounded owned worker.
export -f render_samples
export V FEATS
pids=()
stages=()
launch_stage() {
  local stage="$1" log="$2" remaining process
  shift 2
  remaining=$(remaining_seconds) || return 2
  setsid timeout --signal=TERM --kill-after=10s "${remaining}s" "$@" >> "$log" 2>&1 &
  process=$!
  owned_groups+=("$process")
  pids+=("$process")
  stages+=("$stage")
}
wait_stages() {
  local index process code active now last_gpu=0 last_sample
  last_sample=$(date +%s)
  while true; do
    active=0
    # Poll both workers, so failure of the second never waits for the first's completion.
    for index in "${!pids[@]}"; do
      process="${pids[$index]}"
      [ "$process" -ne 0 ] || continue
      if kill -0 "$process" 2>/dev/null; then
        active=$((active + 1))
        continue
      fi
      if wait "$process"; then
        forget_group "$process"
        done_ "${stages[$index]}"
        pids[$index]=0
      else
        code=$?
        echo "Worker ${stages[$index]} failed with exit $code; stopping every sibling" >&2
        exit "$code"
      fi
    done
    [ "$active" -gt 0 ] || break
    now=$(date +%s)
    if [ "$((now - last_gpu))" -ge 30 ]; then
      printf '%s run=%s ' "$(date -u +%FT%TZ)" "$RUN_ID" >> "$W/out/gpu.txt"
      bounded_run timeout --signal=TERM --kill-after=2s 5s nvidia-smi \
          --query-gpu=utilization.gpu,memory.used --format=csv,noheader >> "$W/out/gpu.txt" 2>&1 || true
      last_gpu="$now"
    fi
    if [ "$((now - last_sample))" -ge 1800 ] && [ -f "$CKPT/acoustic.pt" ] && [ -f "$CKPT/vocoder.pt" ]; then
      stamp="$(date -u +%Y%m%dT%H%M%SZ)-$BASHPID"
      if bounded_run bash -c 'render_samples "$1" "$2"' _ "$CKPT" "$W/out/progress/$RUN_ID/$stamp"; then
        echo "$stamp $RUN_ID" > "$W/out/progress/when.txt"
      else
        echo "Progress rendering failed; no listening result recorded" >&2
      fi
      last_sample=$(date +%s)
    fi
    sleep 1
  done
  pids=()
  stages=()
}
# Owner, 2026-10-12: "no way to speed it up than 11 hrs?" / "okay do whats best". The acoustic model and the
# source vocoder are independent and already run at the same time; with two GPUs each gets its own card instead of
# sharing one (counted by nvidia-smi; one GPU keeps the old shared behaviour).
VOICE_GPUS=$(nvidia-smi --query-gpu=index --format=csv,noheader 2>/dev/null | wc -l)
if [ "${VOICE_GPUS:-1}" -ge 2 ]; then ACOUSTIC_GPU=0; VOCODER_GPU=1; else ACOUSTIC_GPU=0; VOCODER_GPU=0; fi
echo "voice GPUs: $VOICE_GPUS (acoustic on $ACOUSTIC_GPU, vocoder on $VOCODER_GPU)"
if ! have acoustic; then
  CUDA_VISIBLE_DEVICES=$ACOUSTIC_GPU launch_stage acoustic "$W/acoustic.log" python3 "$V/train_acoustic.py" "$FEATS" "$CKPT" \
      --steps "$ACOUSTIC_STEPS" --frames "$ACOUSTIC_FRAMES" --seed "$VOICE_SEED"
fi
if ! have vocoder-source; then
  CUDA_VISIBLE_DEVICES=$VOCODER_GPU launch_stage vocoder-source "$W/vocoder.log" python3 "$V/train_vocoder.py" \
      "$VOICE_DATASET_DIR" "$FEATS" "$CKPT" --steps "$((VOCODER_STEPS - GTA_STEPS))" \
      --batch "$VOCODER_BATCH" --seed "$VOICE_SEED"
fi
wait_stages
have acoustic && have vocoder-source || { echo "A training stage failed" >&2; exit 1; }
# Completed exact exports are hash-checked by the trainer; interrupted temp siblings
# remain intact. Predicted heldout mels are NEVER passed as directly aligned GAN targets.
bounded_run python3 "$V/train_acoustic.py" "$FEATS" "$CKPT" --frames "$ACOUSTIC_FRAMES" \
    --seed "$VOICE_SEED" --export-gta "$R/oracle-gta"
if ! have vocoder; then
  launch_stage vocoder "$W/vocoder.log" python3 "$V/train_vocoder.py" \
      "$VOICE_DATASET_DIR" "$FEATS" "$CKPT" --steps "$VOCODER_STEPS" \
      --batch "$VOCODER_BATCH" --seed "$VOICE_SEED" --gta "$R/oracle-gta"
  wait_stages
fi
bounded_run python3 "$V/train_acoustic.py" "$FEATS" "$CKPT" --frames "$ACOUSTIC_FRAMES" \
    --seed "$VOICE_SEED" --export-heldout-inference "$R/predicted-heldout"

# A complete exact publication is reusable; partial siblings are preserved. A
# second run namespace cannot overwrite another completed model or its receipts.
PUBLISHED="$W/out/models/$RUN_ID"
bounded_run python3 "$V/pod/publish_voice.py" "$FEATS" "$CKPT" "$PUBLISHED"
bounded_run bash -c 'render_samples "$1" "$2"' _ "$PUBLISHED" "$W/out/samples/$RUN_ID/$(date -u +%Y%m%dT%H%M%SZ)-$BASHPID"
done_ configured-work-complete
echo "Configured v2 work complete; final listening, billing-stop reliability and deployment remain separate."
