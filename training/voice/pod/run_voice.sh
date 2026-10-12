#!/usr/bin/env bash
# Runs on the RunPod pod: Unity's own voice, trained from random weights, on one H100-class GPU.
# Stages: setup -> dataset (her designed voice reads her lines, ~7.6 h) -> prep (phonemes, mel, pitch, energy)
# -> acoustic model and vocoder trained AT THE SAME TIME on the one GPU (the vocoder fills the gaps while the
#    acoustic model runs its alignment search on the CPU) -> when the acoustic model is done it exports its own
#    ground-truth-aligned mels and the vocoder spends its last GTA_STEPS learning those -> one sample per emotion.
# While it trains: progress/<emotion>.wav every 30 min from the newest checkpoints, gpu.txt (utilization).
# Every stage logs to /workspace/voice.log and leaves a marker in /workspace/state/voice-*, so a restart skips
# finished stages and both trainings resume from their last checkpoint (acoustic every 2000 steps, vocoder 5000).
# /workspace is the NETWORK VOLUME: dataset, features and checkpoints survive the pod being stopped or deleted.
# Result in /workspace/out: acoustic.pt, vocoder.pt, voice-meta.json, samples/<emotion>.wav, SHA256SUMS
set -euo pipefail
W=/workspace; V=$W/repo/training/voice; mkdir -p $W/state $W/out/samples $W/out/progress $W/ckpt
exec > >(tee -a $W/voice.log) 2>&1
done_() { touch "$W/state/voice-$1"; echo "=== $(date +%T) done: $1"; }
have() { [ -f "$W/state/voice-$1" ]; }
# sized for one 80 GB H100: 96k mel frames per acoustic batch (~750 passes over her 2.5 M frames in 20k steps),
# 32 windows per vocoder batch; the last GTA_STEPS of the vocoder run on the acoustic model's own mels
ACOUSTIC_STEPS="${ACOUSTIC_STEPS:-20000}"; ACOUSTIC_FRAMES="${ACOUSTIC_FRAMES:-96000}"
VOCODER_STEPS="${VOCODER_STEPS:-120000}"; VOCODER_BATCH="${VOCODER_BATCH:-32}"; GTA_STEPS="${GTA_STEPS:-20000}"
LINE="Hey, welcome in! Scar's out planting crops, and honestly? Watching her work is weirdly relaxing."

if ! have setup; then
  apt-get update -qq && apt-get install -y -qq espeak-ng >/dev/null || true
  pip install -q kokoro==0.9.4 misaki==0.9.4 espeakng_loader phonemizer-fork pyworld soundfile numba
  python -c "import torch, torchaudio, pyworld, kokoro, numba; assert torch.cuda.is_available(); print('setup ok', torch.__version__, torch.cuda.get_device_name())"
  done_ setup
fi
if ! have dataset; then python $V/make_dataset.py $W/dataset 12; done_ dataset; fi
if ! have prep; then python $V/prep.py $W/dataset $W/feats; done_ prep; fi

# watchers: GPU utilization every 60 s, a listenable sample of every emotion every 30 min
( while true; do echo "$(date -u +%T) $(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader)" >> $W/out/gpu.txt; sleep 60; done ) &
( while true; do sleep 1800
    if [ -f $W/ckpt/acoustic.pt ] && [ -f $W/ckpt/vocoder.pt ]; then
      for emo in neutral warm hype panic laugh choked; do
        python $V/infer.py $W/ckpt "$LINE" $W/out/progress/$emo.wav --emotion $emo >/dev/null 2>&1 || true
      done
      date -u +%FT%TZ > $W/out/progress/when.txt
    fi
  done ) &

pids=()
if ! have acoustic; then
  ( cd $V && python train_acoustic.py $W/feats $W/ckpt --steps "$ACOUSTIC_STEPS" --frames "$ACOUSTIC_FRAMES" >> $W/acoustic.log 2>&1 \
      && python train_acoustic.py $W/feats $W/ckpt --export-gta $W/gta >> $W/acoustic.log 2>&1 && done_ acoustic ) &
  pids+=($!)
fi
if ! have vocoder-real; then
  ( cd $V && python train_vocoder.py $W/dataset $W/feats $W/ckpt --steps $((VOCODER_STEPS - GTA_STEPS)) --batch "$VOCODER_BATCH" \
      >> $W/vocoder.log 2>&1 && done_ vocoder-real ) &
  pids+=($!)
fi
for p in "${pids[@]}"; do wait "$p"; done
have acoustic && have vocoder-real || { echo "a training stage failed (acoustic.log / vocoder.log)"; exit 1; }
if ! have vocoder; then
  (cd $V && python train_vocoder.py $W/dataset $W/feats $W/ckpt --steps "$VOCODER_STEPS" --batch "$VOCODER_BATCH" --gta $W/gta >> $W/vocoder.log 2>&1)
  done_ vocoder
fi

# ship only what speaks: the acoustic weights and the vocoder generator, no optimizer or discriminator state
python - <<'PY'
import torch
a = torch.load("/workspace/ckpt/acoustic.pt", map_location="cpu")
torch.save({"model": a["model"], "n_symbols": a["n_symbols"], "step": a["step"]}, "/workspace/out/acoustic.pt")
v = torch.load("/workspace/ckpt/vocoder.pt", map_location="cpu")
torch.save({"G": v["G"], "step": v["step"]}, "/workspace/out/vocoder.pt")
PY
cp $W/ckpt/voice-meta.json $W/out/
for emo in neutral warm hype panic laugh choked; do
  python $V/infer.py $W/out "$LINE" $W/out/samples/$emo.wav --emotion $emo
done
(cd $W/out && sha256sum acoustic.pt vocoder.pt voice-meta.json > SHA256SUMS)
done_ ALL
