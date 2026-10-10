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
# the 35B base (~70 GB) downloads while the voice trains, so the player stage starts at once
if ! have "train-player"; then
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

for k in voice player; do
  if ! have "train-$k"; then python $W/pod/train.py $k; done_ "train-$k"; fi
  to_gguf $k
  rm -rf $W/out/$k-merged          # free disk before the next stage
done
done_ ALL
