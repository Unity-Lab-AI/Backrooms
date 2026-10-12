#!/usr/bin/env bash
# On-pod clip generation: the pod records Unity's whole script with the A2 teachers, screens every clip with
# speech recognition, and leaves one dataset that run_voice.sh trains on in the same pod session.
# Owner, 2026-10-12: "cant we use a good fucking model and a pod to generate the clips for the traing pod to use
# right then iin the moment?" and "lets not use our 1500 lkets redo all 5k".
#
# Same teachers and pins as the local seed that made the approved A2 voice (make_dataset.py + source_workers.py,
# the one-at-a-time renderer that worked; the optimized batched Qwen worker is broken and is not used):
#   Qwen  Qwen/Qwen3-TTS-12Hz-1.7B-Base        @ fd4b254389122332181a7c3db7f27e918eec64e3  (qwen-tts 0.1.1, transformers 4.57.3)
#   Cosy  FunAudioLLM/Fun-CosyVoice3-0.5B-2512 @ 29e01c4e8d000f4bcd70751be16fa94bf3d85a18  (transformers 4.51.3)
#   Cosy code github.com/QwenAudio/CosyVoice   @ 074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc
# Both teacher environments use torch 2.7.1+cu118 (builds include sm_90 for H100).
#
# Parallelism: the script is split into GEN_SHARDS shards by id hash; every shard is an independent make_dataset.py
# --all run into its own folder (Qwen then Cosy inside it), all running at once on the one GPU. Shards merge with
# merge_source_datasets.py, are screened with inspect_source_audio.py (faster-whisper on the GPU), and
# auto_screen.py keeps only the clips that passed. Every stage leaves a marker; a restart resumes per shard.
#
# Called by start_template.sh (template mode) before bootstrap_voice.sh when VOICE_GENERATE_ON_POD=1.
# In:  $1 = delivered source root (…/source), $2 = work root on the volume.  Out: $2/dataset (screened, ready).
set -euo pipefail
SRC="$1"; G="$2"; V="$SRC/training/voice"
SHARDS="${GEN_SHARDS:-6}"
mkdir -p "$G/state" "$G/logs"
have() { [ -f "$G/state/$1" ]; }
done_() { touch "$G/state/$1"; echo "$(date -u +%FT%TZ) gen: $1 done"; }
CU118=https://download.pytorch.org/whl/cu118

# 1. Teacher environments (once per volume).
if ! have venv-qwen; then
  python3 -m venv "$G/venv-qwen"
  "$G/venv-qwen/bin/pip" install -q --upgrade pip
  "$G/venv-qwen/bin/pip" install -q "torch==2.7.1+cu118" "torchaudio==2.7.1+cu118" --index-url "$CU118"
  "$G/venv-qwen/bin/pip" install -q -r "$V/pod/requirements-teacher-qwen.txt" -c "$V/pod/constraints-teacher.txt" --extra-index-url "$CU118"
  done_ venv-qwen
fi
if ! have cosy-code; then
  rm -rf "$G/cosyvoice-code"
  git clone -q https://github.com/QwenAudio/CosyVoice.git "$G/cosyvoice-code"
  (cd "$G/cosyvoice-code" && git checkout -q 074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc && git submodule update -q --init --recursive)
  done_ cosy-code
fi
if ! have venv-cosy; then
  python3 -m venv "$G/venv-cosy"
  "$G/venv-cosy/bin/pip" install -q --upgrade pip
  "$G/venv-cosy/bin/pip" install -q "torch==2.7.1+cu118" "torchaudio==2.7.1+cu118" --index-url "$CU118"
  # openai-whisper 20231117 (a Cosy pin) only ships as an old sdist whose setup.py imports pkg_resources, which
  # current setuptools removed: build it first against setuptools<70 without build isolation.
  "$G/venv-cosy/bin/pip" install -q "setuptools<70" wheel
  # --no-deps: whisper's Linux pin triton<3 would pull torch 2.3.1 over the required 2.7.1+cu118
  "$G/venv-cosy/bin/pip" install -q --no-deps --no-build-isolation openai-whisper==20231117
  "$G/venv-cosy/bin/pip" install -q -r "$V/pod/requirements-teacher-cosy.txt" -c "$V/pod/constraints-teacher.txt" --extra-index-url "$CU118"
  done_ venv-cosy
fi

# 2. Teacher weights at the pinned revisions (huggingface download receipts are what teacher_inputs verifies).
fetch() {   # repo revision dir
  "$G/venv-qwen/bin/python" - "$1" "$2" "$3" <<'PY'
import json, sys
from huggingface_hub import snapshot_download
repo, rev, out = sys.argv[1:4]
snapshot_download(repo_id=repo, revision=rev, local_dir=out)
json.dump({"repo": repo, "revision": rev}, open(out + "/audition-source.json", "w"))
PY
}
M="$SRC/.local/voice-lab/models"; mkdir -p "$M"
have model-qwen || { fetch Qwen/Qwen3-TTS-12Hz-1.7B-Base fd4b254389122332181a7c3db7f27e918eec64e3 "$M/qwen3-tts-base"; done_ model-qwen; }
have model-cosy || { fetch FunAudioLLM/Fun-CosyVoice3-0.5B-2512 29e01c4e8d000f4bcd70751be16fa94bf3d85a18 "$M/cosyvoice3"; done_ model-cosy; }
# The ASR screener, same snapshot the local screening used.
have model-asr || { fetch Systran/faster-whisper-base ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66 "$G/asr-model"; done_ model-asr; }

# 3. Shard the script (ordinary + laughter corpora) by id hash; every shard keeps at least one laughter row.
if ! have shards; then
  python3 - "$V" "$G" "$SHARDS" <<'PY'
import hashlib, json, os, sys
V, G, K = sys.argv[1], sys.argv[2], int(sys.argv[3])
for name, out in (("STREAM_CORPUS.jsonl", "corpus"), ("STREAM_EVENT_CORPUS.jsonl", "events")):
    rows = [l for l in open(os.path.join(V, name), encoding="utf-8") if l.strip()]
    parts = [[] for _ in range(K)]
    for line in rows:
        parts[int(hashlib.sha1(json.loads(line)["id"].encode()).hexdigest(), 16) % K].append(line)
    for k, part in enumerate(parts):
        if not part:
            raise SystemExit("shard %d has no %s rows; lower GEN_SHARDS" % (k, out))
        os.makedirs(os.path.join(G, "shards"), exist_ok=True)
        open(os.path.join(G, "shards", "%s-%d.jsonl" % (out, k)), "w", encoding="utf-8", newline="\n").writelines(part)
print("sharded into", K)
PY
  done_ shards
fi

# 4. Render every shard at once (each its own make_dataset.py process, resumable per shard).
pids=()
for k in $(seq 0 $((SHARDS - 1))); do
  have "render-$k" && continue
  ( cd "$SRC" && "$G/venv-qwen/bin/python" -B -u training/voice/make_dataset.py "$G/render/shard-$k" --all \
        --corpus "$G/shards/corpus-$k.jsonl" --event-corpus "$G/shards/events-$k.jsonl" \
        --model-dir "$M/qwen3-tts-base" --qwen-python "$G/venv-qwen/bin/python" \
        --cosy-python "$G/venv-cosy/bin/python" --cosy-code-dir "$G/cosyvoice-code" --cosy-model-dir "$M/cosyvoice3" \
        > "$G/logs/render-$k.log" 2>&1 && touch "$G/state/render-$k" ) &
  pids+=($!)
done
fail=0; for p in "${pids[@]}"; do wait "$p" || fail=1; done
[ "$fail" -eq 0 ] || { echo "gen: a render shard failed; see $G/logs/render-*.log (finished shards are kept)" >&2; exit 1; }

# 5. Merge, screen with ASR, keep only clips that passed.
if ! have merge; then
  args=(); for k in $(seq 0 $((SHARDS - 1))); do args+=(--parent "$G/render/shard-$k"); done
  (cd "$SRC" && "$G/venv-qwen/bin/python" -B training/voice/merge_source_datasets.py "$G/merged" "${args[@]}" \
      --minimum-clips "${GEN_MINIMUM_CLIPS:-4500}") > "$G/logs/merge.log" 2>&1
  done_ merge
fi
# The screener is bound to one renderer's recipe, so each shard is screened where it was rendered (all at once),
# then the screenings are combined; auto_screen.py matches them to the merged rows by id and WAV hash.
pids=()
for k in $(seq 0 $((SHARDS - 1))); do
  have "screen-$k" && continue
  ( cd "$SRC" && "$G/venv-qwen/bin/python" -B -u training/voice/inspect_source_audio.py "$G/render/shard-$k" "$G/screen/shard-$k"         --model-dir "$G/asr-model" --threads 4 > "$G/logs/screen-$k.log" 2>&1 && touch "$G/state/screen-$k" ) &
  pids+=($!)
done
fail=0; for p in "${pids[@]}"; do wait "$p" || fail=1; done
[ "$fail" -eq 0 ] || { echo "gen: a screen shard failed; see $G/logs/screen-*.log" >&2; exit 1; }
if ! have filter; then
  cat "$G"/screen/shard-*/screening.jsonl > "$G/screening-all.jsonl"
  "$G/venv-qwen/bin/python" "$V/pod/auto_screen.py" "$G/merged" "$G/screening-all.jsonl" "$G/dataset" > "$G/logs/filter.log" 2>&1
  done_ filter
fi
echo "gen: dataset ready at $G/dataset"
