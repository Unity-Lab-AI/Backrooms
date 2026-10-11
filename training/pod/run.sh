#!/usr/bin/env bash
# Runs on the RunPod pod: ONE shell, Unity's brain (Qwen3.5-9B + LoRA), on one H100-class GPU.
# Stages: setup -> preflight (2 steps on the longest rows) -> train + merge -> bf16 gguf -> imatrix ->
# Q4_K_M and IQ4_XS -> eval on the held-out voice and tool sets -> keep the picked quant.
# Every stage logs to /workspace/run.log and leaves a marker in /workspace/state/ so a re-run skips finished stages.
# Result: /workspace/gguf/unity-brain.gguf (+ .sha256, brain-eval.json, quant.txt)
set -euo pipefail
W=/workspace; mkdir -p $W/state $W/gguf $W/out
exec > >(tee -a $W/run.log) 2>&1
done_() { touch "$W/state/$1"; echo "=== $(date +%T) done: $1"; }
have() { [ -f "$W/state/$1" ]; }

# a stage marker only counts for the exact inputs it was made from (data + scripts). When any of them changed,
# every marker, checkpoint and old output is dropped so nothing stale is reused under a new name.
INPUTS=$( (cd $W && find data/brain pod -type f -print0 | sort -z | xargs -0 sha256sum) | sha256sum | cut -d' ' -f1)
if [ "$(cat $W/state/inputs 2>/dev/null)" != "$INPUTS" ]; then
  echo "=== inputs changed ($INPUTS): clearing training markers and outputs"
  rm -f $W/state/preflight $W/state/train $W/state/gguf-* $W/state/eval $W/state/ALL
  rm -rf $W/ckpt $W/out/brain-merged $W/out/brain-lora $W/out/*.gguf
  rm -f $W/gguf/unity-*.gguf* $W/gguf/brain-eval.json $W/gguf/quant.txt
  echo "$INPUTS" > $W/state/inputs
fi
cp $W/state/inputs $W/gguf/inputs.sha256

if ! have setup; then
  pip install -q --upgrade pip
  pip install -q "unsloth" "unsloth_zoo" datasets hf_transfer pillow
  pip install -q "transformers>=5"
  # the image's torchaudio is built for an older torch and transformers imports it on the way; nothing here uses audio
  pip uninstall -y -q torchaudio || true
  # fast kernels for the linear-attention layers; without them every step falls back to slow PyTorch
  pip install -q flash-linear-attention ninja || true
  MAX_JOBS=16 pip install -q causal-conv1d --no-build-isolation || true
  python -c "import fla, causal_conv1d; print('fast kernels ok')" || echo "fast kernels missing (slower, still correct)"
  rm -rf $W/llama.cpp
  git clone -q --depth 1 ${LLAMA_CPP_REF:+-b "$LLAMA_CPP_REF"} https://github.com/ggml-org/llama.cpp $W/llama.cpp
  pip install -q -e $W/llama.cpp/gguf-py sentencepiece
  # CUDA build: the quantizer, the imatrix and the server the eval talks to (sm_90 = H100/H200)
  cmake -S $W/llama.cpp -B $W/llama.cpp/build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="${CUDA_ARCH:-90}" -DLLAMA_CURL=OFF >/dev/null
  cmake --build $W/llama.cpp/build --target llama-quantize llama-imatrix llama-server -j"$(nproc)" >/dev/null
  done_ setup
fi
# what this run was actually built with, next to the model, so a result can be traced and repeated
{ echo "llama.cpp $(cd $W/llama.cpp && git rev-parse HEAD)"; pip freeze 2>/dev/null; } > $W/gguf/versions.txt
export HF_HUB_ENABLE_HF_TRANSFER=1

if ! have preflight; then python $W/pod/train.py --preflight; rm -rf $W/ckpt/preflight; done_ preflight; fi
if ! have train; then python $W/pod/train.py; done_ train; fi
# the base download is not needed once merged
rm -rf "${HF_HOME:-$HOME/.cache/huggingface}/hub/models--Qwen--Qwen3.5-9B"

if ! have gguf-bf16; then
  python $W/llama.cpp/convert_hf_to_gguf.py $W/out/brain-merged --outtype bf16 --outfile $W/out/brain.bf16.gguf
  done_ gguf-bf16
fi
if ! have gguf-imatrix; then
  $W/llama.cpp/build/bin/llama-imatrix -m $W/out/brain.bf16.gguf -f $W/out/calib.txt -o $W/out/brain.imatrix \
    -c 4096 --chunks 200 -ngl 999
  done_ gguf-imatrix
fi
if ! have gguf-quants; then
  $W/llama.cpp/build/bin/llama-quantize --imatrix $W/out/brain.imatrix $W/out/brain.bf16.gguf $W/out/brain.Q4_K_M.gguf Q4_K_M
  $W/llama.cpp/build/bin/llama-quantize --imatrix $W/out/brain.imatrix $W/out/brain.bf16.gguf $W/out/brain.IQ4_XS.gguf IQ4_XS
  done_ gguf-quants
fi
if ! have eval; then
  python $W/pod/eval.py $W/out/brain.Q4_K_M.gguf $W/out/brain.IQ4_XS.gguf
  done_ eval
fi
PICK=$(cat $W/out/picked.txt)
cp "$W/out/$PICK" $W/gguf/unity-brain.gguf
echo "${PICK#brain.}" | sed 's/\.gguf$//' > $W/gguf/quant.txt
(cd $W/gguf && sha256sum unity-brain.gguf > unity-brain.gguf.sha256)
rm -rf $W/out/brain-merged $W/out/brain.bf16.gguf     # free disk; the LoRA adapter and both quants stay
done_ ALL
