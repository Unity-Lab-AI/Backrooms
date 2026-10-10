#!/usr/bin/env bash
# Runs on the RunPod pod. Voice first (cheap, proves the whole chain), then the player.
# Every stage logs to /workspace/run.log and leaves a marker in /workspace/state/ so a re-run skips finished stages.
# Results: /workspace/gguf/unity-voice.Q4_K_M.gguf and /workspace/gguf/unity-player.Q4_K_M.gguf
set -euo pipefail
W=/workspace; mkdir -p $W/state $W/gguf $W/out
exec > >(tee -a $W/run.log) 2>&1
done_() { touch "$W/state/$1"; echo "=== $(date +%T) done: $1"; }
have() { [ -f "$W/state/$1" ]; }

if ! have setup; then
  pip install -q --upgrade pip
  pip install -q "unsloth" "unsloth_zoo" datasets trl hf_transfer
  pip install -q "transformers>=5" || true
  git clone -q --depth 1 https://github.com/ggml-org/llama.cpp $W/llama.cpp
  pip install -q -e $W/llama.cpp/gguf-py sentencepiece
  # only the quantizer is needed, CPU build is enough
  cmake -S $W/llama.cpp -B $W/llama.cpp/build -DGGML_CUDA=OFF -DLLAMA_CURL=OFF >/dev/null
  cmake --build $W/llama.cpp/build --target llama-quantize -j"$(nproc)" >/dev/null
  done_ setup
fi
export HF_HUB_ENABLE_HF_TRANSFER=1
# fast kernels for the 35B's linear-attention layers; without them every step falls back to slow PyTorch
# (measured 52 s/step, ~5 h). Its own stage so a pod whose setup is already done still gets them.
if [[ "${SHELLS:-voice player}" == *player* ]] && ! have kernels; then
  # the image's torchaudio is built for an older torch; any import of it crashes, and transformers imports it
  # on the way to the fast kernels -- nothing here uses audio, so it goes
  pip uninstall -y -q torchaudio || true
  pip install -q flash-linear-attention ninja || true
  MAX_JOBS=16 pip install -q causal-conv1d --no-build-isolation || true
  python -c "import fla, causal_conv1d; print('fast kernels ok')" || echo "fast kernels missing"
  done_ kernels
fi
# the 35B base (~70 GB) downloads while the voice trains, so the player stage starts at once
if ! have "train-player" && [[ "${SHELLS:-voice player}" == *player* ]]; then
  (huggingface-cli download Qwen/Qwen3.6-35B-A3B --exclude "*.pth" >$W/prefetch.log 2>&1 || hf download Qwen/Qwen3.6-35B-A3B >>$W/prefetch.log 2>&1) &
fi

to_gguf() {   # $1 kind
  local k=$1
  if ! have "gguf-$k"; then
    python $W/llama.cpp/convert_hf_to_gguf.py $W/out/$k-merged --outtype bf16 --outfile $W/out/$k.bf16.gguf
    $W/llama.cpp/build/bin/llama-quantize $W/out/$k.bf16.gguf $W/gguf/unity-$k.Q4_K_M.gguf Q4_K_M
    rm -f $W/out/$k.bf16.gguf
    sha256sum $W/gguf/unity-$k.Q4_K_M.gguf > $W/gguf/unity-$k.Q4_K_M.gguf.sha256
    done_ "gguf-$k"
  fi
}

for k in ${SHELLS:-voice player}; do   # one pod per shell: SHELLS=player or SHELLS=voice
  if ! have "train-$k"; then python $W/pod/train.py $k; done_ "train-$k"; fi
  # the 35B base download is no longer needed once merged (frees ~70 GB before the gguf steps)
  if [ "$k" = player ]; then rm -rf "${HF_HOME:-$HOME/.cache/huggingface}/hub/models--Qwen--Qwen3.6-35B-A3B"; fi
  to_gguf $k
  rm -rf $W/out/$k-merged          # free disk before the next stage
done
done_ ALL
