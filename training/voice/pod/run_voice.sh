#!/usr/bin/env bash
# Runs on the RunPod pod: Unity's own voice, trained from random weights, on one H100-class GPU.
# Stages: setup -> dataset (her designed voice reads her lines, ~7.6 h) -> prep (phonemes, mel, pitch, energy)
# -> acoustic model and vocoder trained AT THE SAME TIME on the one GPU -> one sample per emotion preset.
# Every stage logs to /workspace/voice.log and leaves a marker in /workspace/state/voice-*, so a restart skips
# finished stages and both trainings resume from their last checkpoint (acoustic every 2000 steps, vocoder every 5000).
# /workspace is the NETWORK VOLUME: dataset, features and checkpoints survive the pod being stopped or deleted.
# Result in /workspace/out: acoustic.pt, vocoder.pt, voice-meta.json, samples/<emotion>.wav, SHA256SUMS
set -euo pipefail
W=/workspace; V=$W/repo/training/voice; mkdir -p $W/state $W/out/samples $W/ckpt
exec > >(tee -a $W/voice.log) 2>&1
done_() { touch "$W/state/voice-$1"; echo "=== $(date +%T) done: $1"; }
have() { [ -f "$W/state/voice-$1" ]; }
ACOUSTIC_STEPS="${ACOUSTIC_STEPS:-120000}"; VOCODER_STEPS="${VOCODER_STEPS:-200000}"

if ! have setup; then
  apt-get update -qq && apt-get install -y -qq espeak-ng >/dev/null || true
  pip install -q kokoro==0.9.4 misaki==0.9.4 espeakng_loader phonemizer-fork pyworld soundfile
  python -c "import torch, torchaudio, pyworld, kokoro; assert torch.cuda.is_available(); print('setup ok', torch.__version__)"
  done_ setup
fi
if ! have dataset; then python $V/make_dataset.py $W/dataset 12; done_ dataset; fi
if ! have prep; then python $V/prep.py $W/dataset $W/feats; done_ prep; fi

# both models on the one GPU: the acoustic model is small, the vocoder is the long pole
pids=()
if ! have acoustic; then
  ( cd $V && python train_acoustic.py $W/feats $W/ckpt --steps "$ACOUSTIC_STEPS" --batch 32 > $W/acoustic.log 2>&1 && done_ acoustic ) &
  pids+=($!)
fi
if ! have vocoder; then
  ( cd $V && python train_vocoder.py $W/dataset $W/feats $W/ckpt --steps "$VOCODER_STEPS" --batch 16 > $W/vocoder.log 2>&1 && done_ vocoder ) &
  pids+=($!)
fi
for p in "${pids[@]}"; do wait "$p"; done
have acoustic && have vocoder || { echo "a training stage failed (acoustic.log / vocoder.log)"; exit 1; }

# ship only what speaks: the acoustic weights and the vocoder generator, no optimizer or discriminator state
python - <<'PY'
import torch
a = torch.load("/workspace/ckpt/acoustic.pt", map_location="cpu")
torch.save({"model": a["model"], "n_symbols": a["n_symbols"], "step": a["step"]}, "/workspace/out/acoustic.pt")
v = torch.load("/workspace/ckpt/vocoder.pt", map_location="cpu")
torch.save({"G": v["G"], "step": v["step"]}, "/workspace/out/vocoder.pt")
PY
cp $W/ckpt/voice-meta.json $W/out/
LINE="Hey, welcome in! Scar's out planting crops, and honestly? Watching her work is weirdly relaxing."
for emo in neutral warm hype panic laugh choked; do
  python $V/infer.py $W/out "$LINE" $W/out/samples/$emo.wav --emotion $emo
done
(cd $W/out && sha256sum acoustic.pt vocoder.pt voice-meta.json > SHA256SUMS)
done_ ALL
