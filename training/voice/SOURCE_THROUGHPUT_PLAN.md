# A2 source throughput and corpus scale plan

Prepared 2026-10-11. **Source inspection and planning only.** The current 1,378-job source render continues with its frozen renderer. This document does not alter its inputs, launch a competing GPU model, benchmark teachers, train the student, rent a pod or change live Piper.

Read [NOW](../../docs/NOW.md), [the voice plan](VOICE_PLAN.md), [source delivery policy](SOURCE_DELIVERY_POLICY.json), [source QA policy](SOURCE_QA_POLICY.md), [independent evaluation plan](EVALUATION_PLAN.md) and [runtime integration plan](RUNTIME_INTEGRATION_PLAN.md). Original A2 remains the identity. No rejected Cosy neutral, synthetic pitch boost or new unreviewed speaker is a speed shortcut.

## 1. Direct answers and measurement limits

**The 1,378 recordings are the seed source batch, not the final approved scope.** The owner subsequently approved expansion to **at least 5,000 varied recordings with several hours of speech before considering a pod**, with the longest training replies comprising **three to five medium sentences**. Both minimum clip count and useful speech duration matter. Neither 1,378 nor 5,000 guarantees intelligible, natural, expressive student speech. Decide using accepted audio hours, unique linguistic coverage, recorded emotional/act/event performance, and actual unseen student results. Do not claim the seed corpus is final training readiness.

For scale, the published single-speaker [LJ Speech dataset](https://keithito.com/LJ-Speech-Dataset/) contains 13,100 clips and about 24 hours, with a 6.57-second mean clip duration. That is a reference scale, not a minimum or a promise for this architecture; its read speech also does not certify our conversational emotion target. We are not importing its voice.

The lead reported this snapshot when assigning the review; this agent did not remeasure GPU telemetry or source progress:

| Lead's snapshot | Value | Meaning |
| --- | --- | --- |
| Completed source clips | 689 / 1,378 | Draft source recordings, not accepted student examples or trained output |
| Recent rate | 100 clips in about 14.34 minutes; 6.98 clips/minute | Approximately 8.6 wall seconds per clip in that window |
| Audio collected at that point | 24.84 minutes | Mean approximately 2.16 audio seconds per clip so far; future clips may differ |
| GPU observation | 55% utilization, about 7.6 / 16.4GiB | A moment/window observation; not proof that useful work can safely double |

At that short mean, 5,000 clips would contain only about three hours of audio. At a hypothetical six-second mean, 5,000 would contain about 8.3 hours. These are arithmetic illustrations, not final-corpus targets or measured future durations. More varied connected sentences add useful material; splitting the same audio into tiny clips or rendering trivial paraphrases only inflates counts.

**The current renderer is active but has not been shown to run at maximum useful throughput.** It intentionally runs one teacher and one clip at a time. There are plausible batching/cache improvements, but no measured speedup yet. Preserve the running batch; measure candidates afterward in a separate directory.

## 2. Exact running recipe and likely bottlenecks

Read-only inspection of `.local/voice-lab/dataset/A2-full-1378-draft-v3/render-recipe.json` found:

- Source ID: `8abb75d3e26e8036311731861e5333f1cdaf0fe5f4044385716e4cfe56473798`.
- Recipe ID: `dba264ce8932ddff2da69147fd072c3c485223ba0d9db0a4e417fe49d9257680`.
- 1,073 Qwen jobs: 872 `original`, 201 `soft`.
- 305 Cosy jobs: 201 `natural_happy`, 104 `relaxed_smile` (including event routing).
- Qwen runs first, then its subprocess exits and Cosy runs. At the lead's 689-clip snapshot, the measured window was therefore Qwen work. Do not extrapolate that rate across Cosy without measuring Cosy separately.

| Current source location | Confirmed behavior | Performance interpretation |
| --- | --- | --- |
| [make_dataset.py](make_dataset.py), lines 449–459, 491–508 | Renderer binds source/reference/approval/code hashes and generation settings; teacher subprocesses run sequentially with bounded owned timeouts. | Model setup is amortized over each teacher batch, not repeated for every clip. Running both teachers simultaneously would change scheduling and memory/seed assumptions. |
| [source_workers.py](source_workers.py), lines 124–171 | Requires at least 8GiB free before teacher load; Qwen uses bfloat16 + SDPA. Lazily builds and reuses `create_voice_clone_prompt` per approved profile; `generate_voice_clone` receives one text. | Qwen reference extraction is already cached. The principal remaining candidate is batching its autoregressive generation/decode, not adding a cache already present. Autoregressive short sequences can leave GPU gaps even with available VRAM. |
| Same file, lines 137–146, 175–188 | CosyVoice3 uses fp16, no TensorRT/vLLM, and CPU ONNX speaker/tokenizer providers. Calls `inference_instruct2` with original A2 raw reference, empty `zero_shot_spk_id`, no streaming and speed 1.0. | Reference preprocessing repeats per Cosy clip. CPU ONNX/reference work plus sequential LLM/flow/vocoder stages may contribute idle periods; their actual proportions need timing. CPU providers are the reviewed Windows route, not a defect to silently change. |
| Same file, lines 189–205 | Checks audio, writes/flushes/fsyncs WAV, reopens and rechecks serialized PCM, hashes it and appends/flushes/fsyncs metadata. | Serialization/durable I/O is intentional. Measure its share before introducing asynchronous publication. Removing fsync or validation to claim speed would weaken recovery/evidence. |
| Installed Cosy `cosyvoice/cli/model.py`, lines 328–393, plus CosyVoice3 inheritance | Non-streaming model starts an internal LLM thread, joins before full waveform generation, clears per-request dictionaries and calls `torch.cuda.empty_cache()` at the end. | Pipeline stages and allocator/cache behavior are plausible bottlenecks. Changing vendor internals would be a new pinned renderer revision, not an in-flight patch. Threading support does not establish safe concurrent source generation. |

The installed Qwen source is `.local/voice-lab/.venv-qwen/Lib/site-packages/qwen_tts/inference/qwen3_tts_model.py` from `qwen-tts==0.1.1`; model internals are `qwen_tts/core/models/modeling_qwen3_tts.py`. The installed Cosy source is `.local/voice-lab/models/cosyvoice-code/cosyvoice/cli/{cosyvoice,frontend,model}.py`, pinned by the recipe. These local ignored providers are inspection evidence, not files to ship or alter during this batch.

## 3. Ranked candidates after the current batch

### A. Qwen length-bucketed batches of two, then four

The installed API accepts `text: str | list[str]`; lines 556–620 broadcast one reusable prompt to multiple texts, validate lengths, invoke one model generation and decode a list of outputs. Core lines 2240–2274 pad a batch and call the talker once. The official [Qwen Base example](https://github.com/QwenLM/Qwen3-TTS/blob/main/examples/test_model_12hz_base.py) and [voice-clone README](https://github.com/QwenLM/Qwen3-TTS#voice-clone) also show prompt reuse and batch generation. This confirms API capability; it does not establish speed/memory/acting quality on our Windows GPU.

Planned change: group only the same approved profile and compatible text lengths; begin with batch two, then consider four if measured memory permits. Keep original A2 references and current generation parameters; do not concatenate several transcripts into one teacher utterance. Validate each returned audio/row independently, preserve exact job order/output association, and retain failed partial outputs for review.

The longest item can drive padding and decoding work. Bucket estimated tokens/characters and bound total batch tokens, maximum generated tokens and predicted duration; do not simply double until VRAM is nearly full. A shorter max-token cap may truncate words and is not a free speed improvement.

**Seed/provenance change required:** current seeds are reset per clip from the identity hash. A batch uses shared sampling state and draw ordering; per-item outputs can change with batch partners, order, padding, early completion and resume grouping. Do not claim the old per-clip seed policy remains equivalent. Pin ordered batch membership/size, profile/reference hashes, exact generation defaults including subtalker defaults, implementation/environment and a reviewed batch-seed policy in a new recipe. Resume a missing item using its original batch context or require explicit recovery; silently generating it alone violates that policy. Starting a new renderer changes source/clip identities; preserve all existing WAVs.

### B. Cosy in-memory cache keyed by exact reference and instruction

Installed `frontend.py:168–189` extracts instruction tokens, reference features/speech tokens and speaker embedding for every empty-ID call. `cosyvoice.py:69–75` exposes `add_zero_shot_spk(prompt_text, prompt_wav, id)`, which stores the input dictionary in memory; `frontend_instruct2` removes LLM prompt speech tokens but retains reference flow inputs.

The pinned [official frontend source](https://github.com/FunAudioLLM/CosyVoice/blob/074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc/cosyvoice/cli/frontend.py) confirms the cache behavior. Its line numbers differ from the installed file's formatting; use the local numbers above for this workstation.

Planned first candidate: create one cache entry per **exact original A2 reference hash + exact instruction string/hash + model/frontend settings**. The two current instruction routes need separate entries. Verify the entry's instruction token values/lengths and reference bindings before use. No generic speaker-only cache ID: a nonempty ID retains its cached `prompt_text`, so passing a different `instruct_text` later can silently use the previous instruction. The current empty-ID choice deliberately avoids that fault.

Keep this cache in memory only. `save_spkinfo()` writes to the model directory; do not invoke it or contaminate immutable teacher files. A future cache must preserve per-clip seeding and be evaluated for waveform differences, text, speaker/acting and laughter. Expected reduction in repeated CPU/reference extraction is an inference from source; its actual speedup is unknown.

### C. Backend changes only after simple candidates are measured

Current Qwen uses SDPA. The official README recommends optional FlashAttention2 and links backend tooling, but installation/support on this pinned Windows stack is not established. Changing attention/dtype/backend belongs in a fresh isolated environment and renderer recipe, with quality/seed comparisons; do not install over the active environment. The same applies to Qwen vLLM-Omni.

The pinned [Cosy README](https://github.com/FunAudioLLM/CosyVoice/blob/074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc/README.md#vllm-usage) describes version-specific vLLM integration and separate environments. Its TensorRT-LLM speed statement concerns CosyVoice2, not evidence of our CosyVoice3 Windows instruction path. Do not promise a fourfold gain or enable concurrent requests from that statement. TensorRT/vLLM, GPU ONNX, vendor allocator changes and multi-request concurrency are later candidates requiring compatible dependencies, instruction/reference correctness, independent sampling and owned error/timeout handling.

Do not switch to `x_vector_only_mode=True`, a smaller model, a different speaker, speed >1.0 or greedy decoding merely to improve clip throughput. Those changes can alter cloning, acting or timing and require their own audible acceptance. Source quality is the constraint.

## 4. Proposed bounded teacher benchmark

**Planned after the frozen batch; not performed here.** The owner's performance question permits planning a bounded source-inference comparison. It does not authorize student training, paid rental or a competing teacher during current rendering. The lead schedules any actual benchmark after source completion/free memory and records it separately.

1. Freeze a small benchmark manifest: at most 24 unique representative texts, original/soft profiles, happy/amused instructions, questions, short and connected turns, and laughter where supported. Keep independent listening evaluation texts out of generated training corpora. Select fixed comparable text/route sets for every applicable candidate.
2. Use fresh candidate output directories and a fixed maximum walltime (proposed 30 minutes per candidate, one teacher at a time). Record exact code/model/environment/reference/configuration hashes, workload order, seed policy and GPU/coexistence state. No changes to the current 8abb batch or its receipt.
3. Record cold-load time separately; perform at most two warmup turns and keep their outputs marked warmup. Then time repeated fixed groups: Qwen single versus batch two, conditionally batch four; Cosy empty-ID versus exact-instruction cached single. Avoid combining batching/backend/cache changes in one comparison.
4. Use CUDA synchronization around GPU timing in the benchmark only; capture preprocessing, generation/decoding, validation/serialization and total walltime separately. Measure clips/minute **and audio seconds per wall second** for the same window; shorter or truncated output must not count as faster successful work. Record peak allocated/reserved/free VRAM, CPU RAM, CPU use and disk time, not one GPU percentage.
5. Admit a candidate only with a declared free-memory reserve for the actual game/brain/OBS workload (proposed at least 2GiB during generation, measured rather than guessed). Keep the existing 8GiB-before-load guard as a baseline; it does not guarantee a larger batch fits afterward. Reject/stop on the first OOM or loss of the reserved headroom, preserve artifacts and use a new smaller candidate. No automatic in-place batch fallback with hidden seed changes.
6. Keep owned subprocess deadlines and child cleanup. Cosy's internal thread can hang on errors; do not run the comparison without the same bounded worker supervision. One serialized metadata publisher owns all output mapping; a failed/torn batch remains evidence, not silently cleaned data.
7. Recheck WAV shape/rate/finite/clipping/duration, transcript completeness by ASR screening and manual listening of ordinary A2, a question, emotional contrasts and every laughter candidate. Compare identity/acting and audible artifacts; exact waveform hashes may differ even with the same semantic target. Record failures and useful throughput, not only fastest successful sample.
8. Publish a benchmark receipt and select a winner only after measured gain, memory safety, instruction correctness, recovery and audible source acceptance. Any implementation then uses a new immutable source recipe/dataset; no retroactive optimization claim for this running batch.

## 5. Expanding toward approximately 5,000 useful clips

The expansion is now owner-approved; this remains a plan for a separate corpus/renderer, not permission to replace in-flight frozen source text files. Keep the 1,378 seed batch, its original metadata/WAVs, ASR results and heard approval evidence. The expansion needs a new corpus file/recipe, unique IDs and an exact combined data manifest. Count at least 5,000 accepted varied recordings across the preserved useful seed material and new material, with several actual accepted speech hours; do not count rejected drafts or duplicate segmentation as useful expansion. Existing reviewed audio may be reused by hash rather than re-rendered, while every new recording remains pending its own QA. Multiple recorded source IDs must remain traceable to their own recipes; one selected voice identity stays fixed.

Prioritize:

- Connected varied English sentences and conversational turns; enough genuine lexical/phoneme/stress patterns instead of thousands of near-identical two-second clips. The longest training replies should have three to five medium sentences, naturally delivered within the existing 30-second source bounds. If a candidate exceeds that bound, preserve it as an explicit planned split/rewrite case; do not speed it up, truncate words or label a cropped recording as complete. Keep short responses too, with the full length distribution recorded.
- Ordinary A2 neutral/warm speech as the majority, plus sufficient distinct accepted performances per actual emotion/act combination. A label is not a performance; shared happy instruction does not automatically certify excited/surprised distinctions.
- Questions contrasted with statements, natural reassurance/instructions/asides, contractions, names, numbers and coder/game vocabulary. Preserve grouped normalized splits for repeated words or event variants.
- Supported laughter only when heard at the requested position. No invented breath data, giggle subtypes, wide intensity/pace ranges or focus supervision from new labels alone.
- Unseen reserved evaluation protected across the combined corpus. Unique transcripts/words/phoneme combinations and accepted **hours per style/act**, plus length distribution, are the readiness inventory.

At least 5,000 accepted varied recordings plus several speech hours is now the minimum expansion milestone before considering a pod, with more needed if accepted duration/coverage or student evaluation remains weak. This architecture has not established a data scaling curve or a quality plateau. Repeating training epochs cannot invent absent pronunciations/emotional performances, and more faulty source audio propagates faults. Review accepted source hours and planned learning/evaluation milestones before quoting a paid final run. Longer live pages remain allowed through paragraph streaming; the three-to-five-sentence training target is not a live reply-length cap.

### Separate optimized worker proposal

**Planned files, not created:** `training/voice/make_dataset_v4.py`, `source_workers_v4.py`, `benchmark_sources_v4.py`, and a separate expanded corpus file (lead owns its exact name/content). Keep current `make_dataset.py`/`source_workers.py`, their pinned providers and the 8abb recipe untouched until the current batch completes. A later reviewed v4 implementation should:

- Retain separate teacher environments, one resident teacher, original A2 policies, local-only model inputs, exact approval/file/environment provenance and owned deadlines. No worker changes are applied to the active seed batch.
- Offer explicit Qwen modes `single`, `batch2`, `batch4` with stable same-profile length buckets and pinned ordered membership/batch seeds. Each mode is a separate recipe; resume cannot silently regroup missing items. Returned item mapping and every output bound remain strict.
- Offer a separate Cosy `cached-single` candidate keyed by exact reference/instruction and verified cached instruction tensors. Cache is process-memory only; never write `spk2info.pt` into a model directory. Retain the reviewed CPU ONNX route unless a separate backend candidate is approved and accepted.
- Write an immutable ordered batch plan before GPU work and one serialized metadata publisher. Interrupted partial batches retain their files/receipt; no orphan cleanup, unrecorded seed fallback or inferred performance acceptance.
- Record cold load, stage timing, synchronized GPU time, actual speech duration, peak/free memory and useful accepted throughput. The benchmark helper must not generate training audio into the seed directory.
- Select optimizations only after the bounded post-seed comparison above. If batching has no safe gain, retain single mode; if caching changes acting/identity, retain empty-ID mode. The approved expanded corpus can still reuse accepted seed WAVs with their original source IDs and receipts.

The v4 proposal is concrete enough for a subsequent scoped implementation assignment, but no optimized helper exists or has demonstrated a speedup at this checkpoint.

## 6. Status and handoff

Created `training/voice/SOURCE_THROUGHPUT_PLAN.md` and updated `RUNTIME_INTEGRATION_PLAN.md` to reflect the later approved expansion and open-ended logical-message direction. Running source helpers, providers, corpus/reference/policy files and student code remain unchanged. Root should bind both documents in the manifest/handoff after integrating plans. No source voice module/model was imported, no benchmark or teacher inference was launched, and no student training or live apply occurred.

Confirmed: recipe route counts, installed API batching/reference-cache behavior and current worker scheduling/settings. Qualified: likely bottleneck shares, expected batch/cache gain, proposed reserves and corpus sufficiency. Open: actual backend compatibility, benchmark results, accepted full source hours, taught emotion/event distinctions, student learning and unheard generalization. Keep the full voice TODO and paid/deployment gates open.
