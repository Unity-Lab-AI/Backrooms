# Student architecture readiness - 2026-10-11

## Scope and evidence level

Owner accepted the 32 source recordings through the lead agent. This review performed source inspection only; it did not listen to recordings, import student modules, execute model/feature code, run tests, train locally or remotely, rent/start a pod, start a service, change a game, or publish anything.

**Result: bounded student source repairs and timing controls implemented; runtime, numerical equivalence, recovery behavior and learned speech quality remain unverified.** This document does not authorize training or replace the closed quality gate. The lead owns the running full source render, its later acceptance/preparation, receipts and immutable manifest.

`dataset_contract.py`, `speech_text.py`, generator/worker, policy and references were held unchanged throughout this wave to preserve the running renderer recipe.

## Confirmed source gaps and repairs

| Source finding | Implemented repair | Current code |
| --- | --- | --- |
| Aligner formed a B x channels x frames x tokens broadcast plus its gradients | Equivalent squared-distance expression uses channel norms and batched matrix multiplication, producing B x frames x tokens directly; numerical/throughput equivalence is not measured | model.py:99 |
| Predictor hidden values outside real tokens could enter the second convolution near a padded sequence end | Mask both hidden convolution outputs before subsequent layers; model parameter shapes remain unchanged | model.py:83 |
| Feature token arrays were cast to integer before dtype validation | Shared strict NPZ inventory, int64 tokens, float32 curves/mel, finite/range/pitch-voicing/hop checks and exact event-token counts before conversion | feature_arrays.py:17 |
| Feature identity did not bind actual preparation/array validation source | Prep adds prep_sha256/feature_arrays_sha256 to frontend config and recomputes frontend_id; both trainers/inference reject older preparation identity | prep.py:70; feature_arrays.py:9 |
| Data/config identity did not bind the full own-student implementation | Shared student_source binds exact code files, enforced in both working/thin checkpoints, inference and GTA exports | student_state.py:12 |
| Restart reseeded random sampling and abandoned the in-progress acoustic batch order | Both trainers save/restore Python, NumPy, Torch and all CUDA random state; acoustic also saves validated complete epoch batches and next cursor | student_state.py:34; train_acoustic.py:205 |
| Resume did not bind batch/frame configuration; finite loss alone did not ensure finite gradients | Resume requires original training configuration and valid finite state; gradient norm validation stops before a nonfinite optimizer update | train_acoustic.py:194; train_vocoder.py:126 |
| Fixed .tmp names could replace earlier interrupted writes | Unique checkpoint temporary names; previous torn artifacts remain; successful latest working checkpoint replacement is atomic | train_acoustic.py:249; train_vocoder.py:212 |
| Inference lacked practical bounded long turns/phrase timing | Out-of-band phrase pauses and chunk planning, preserving the ordinary short unpaused path; explicit focus fails instead of fabricating emphasis | speech_turns.py:35; infer.py:185 |
| Metadata/event coverage and output extent needed stronger rejection | Validate finite train-only support counts/ranges, exact paired implementation, finite model weights and one-hop waveform extent | infer.py:36; infer.py:90; infer.py:156 |

The existing matching acoustic/vocoder feature identity and source-vs-oracle-GTA provenance remain enforced. GTA still means oracle reconstruction using target alignment/prosody; it is not text-only synthesis quality. Unknown phonemes, unsupported markup and heldout-only event support still fail.

## Controls and honest limits

- `Voice.say(text, emotion, intensity, pace, speech_act, *, pauses=None, focus=None)` preserves existing positional arguments.
- `pauses=[{"after":"Give me a second","seconds":0.35}]` anchors a unique exact lexical phrase. Terminal punctuation remains on the spoken side. Pauses are actual digital silence, never spoken labels or new emotional supervision.
- CLI: `--pause-after "Give me a second=0.35"`; at most 16 anchors, each 0.05..2 seconds. Missing, ambiguous, duplicate or event-splitting anchors fail.
- Plain unpaused text of at most 240 characters remains one whole-span G2P/model call. Longer turns split at punctuation/whitespace into at most 240-character chunks; known event markers remain intact. Limits: 12,000 characters, 64 chunks, 120 seconds total audio including silence. Every chunk still has the existing 512-token/3,000-frame limit and TRAIN delivery/event checks.
- Automatic chunk joins insert 80 ms silence with 5 ms gain-only boundary ramps. These are bounded engineering joins, not learned breath timing, expressive pause control or established seamless long-form speech. New joins require later listening.
- An explicit speech_act is used for all chunks; otherwise punctuation fallback runs per chunk. Ambiguous/rhetorical utterances require caller-supplied supported intent.
- `focus` or CLI `--focus` explicitly fails. No word-level performed supervision exists; no duration/F0/energy nudge or pitch-maxing preset was added. Normal phoneme/stress output is retained.
- Learned delivery remains limited to actual TRAIN emotion/act/intensity/pace support. Current drafts use neutral intensity 0.0, others 0.35 and pace 1.0; no broad scalar range is established by those labels.
- Laughter needs marked, audibly performed TRAIN examples for the requested delivery. There is no promised giggle/belly-laugh taxonomy. Breath has no accepted source examples and remains unavailable.
- The existing 256-frame per-token limit remains approximately 2.73 seconds at 24 kHz/hop256, including a single event token. Longer isolated nonverbal performances are not promised.

## Required preparation/recovery boundaries

1. Prepare fresh full-source features after rendering/acceptance; old pilot feature directories intentionally fail the new preparation-source identity. Preserve the old directories/evidence/WAVs.
2. Ship feature_arrays.py, speech_turns.py and student_state.py with all files in the shared student_source inventory below. Thin acoustic/vocoder checkpoints retain the identical student_source field. Working checkpoints additionally retain optimizer/scheduler/RNG/training configuration and acoustic data_order; thin deployment weights cannot resume training.
3. A changed student code file requires a fresh approved checkpoint run; earlier unidentified/legacy smoke checkpoints are refused. CUDA device count and batch/frame configuration must match working recovery. Total requested steps may be extended only through the owner's approval/launch contract.
4. RNG/order recovery is implemented, not demonstrated. TF32/cuDNN benchmarking and GPU kernels mean no bit-exact replay claim.
5. A 32-record source pilot can contain fewer than 32 TRAIN records; a future authorized small training case must choose a batch that fits. The full source dataset remains the intended training input.
6. The lead's reserved listening evaluation covers emotion/question/pronunciation/event/long-turn routes independently of training text. Sparse source heldout emotion coverage is not a quality pass.
7. Full source acceptance, fresh platform-specific features, actual pinned pod environment/assets, durable volume/stop/cost rails and explicit owner-priced training authorization are separate gates. No training or paid resource was started by this wave.

## Static checks actually performed

- Fully inspected model, preparation, both trainers, inference and shared contract/frontend sources.
- Python AST parsing of changed/helper sources; UTF-8/LF normalization of exclusive edited files.
- Scoped git diff --check passed.
- Read-only parallel trainer review reported no additional concrete P0 normal-path blocker; noted the small-pilot batch boundary above.
- No executable/model smoke check, import probe, feature preparation, training, playback or runtime acceptance was performed in this scope.

## Exact student implementation snapshot

Shared student_source_id: `67b80dff1a5ca77c3544af2b525dd4c2ac45747c187cb0b3276a5115050dd18f`

| File (training/voice/) | SHA256 |
| --- | --- |
| model.py | `47153b71266fed30c0633a3f55281b97dbeb0bff32b62b47d274052f810eb447` |
| vocoder.py | `f6e8543d98c8a0e25a88fd903827c276225aa8713b7c06fe11c6d94ff34822d8` |
| prep.py | `bc845dc41bc9111bd296f9405f68f25c97f5fa5f178f288284074feaa5cab3bb` |
| train_acoustic.py | `58fc541ad97030705108ac405b8d1aba77c927d8f208cfc5f833aed2c76e5f5f` |
| train_vocoder.py | `12572f0e1ebad9be9381ba0e75c612a4853d287844e5b1ca23b743fddf4d9657` |
| infer.py | `3cccad9983f92caa61ebaa69eeabdb36916fba66a185cd2dbd8ff187b8269b6b` |
| feature_arrays.py | `3039687c3e48af953576e5d49afec7836618a3df3a3394a28bf38d72e454850e` |
| speech_turns.py | `fd5b5a56d33af5923c8190450bbed0c242331618efe6d33a4fae2eb4beb8cd4b` |
| student_state.py | `ef3d48779b5c0bb2eb4db7d2d1b4ad544fb677c07abf61f0f9ec225c64847bd7` |

The code hashes above are reproducible byte hashes, not evidence of trained quality. The record itself is excluded from student_source to avoid a digest cycle; the lead's final source manifest may include this evidence document.
