# A2 expansion source renderer

This renderer creates only the new recordings needed for the owner's approved
at-least-5,000-recording preparation target. It does not replace the original
1,378-job recipe, train a student, rent a pod, publish an image or deploy a voice.
The existing 1,378-job source files and immutable inputs remain unchanged.

## Inputs and identities

- `make_dataset_optimized.py` and `source_workers_optimized.py` are new source tools.
- Default expanded inputs are `SPEECH_CORPUS_EXPANDED.jsonl` and
  `SPEECH_EVENT_CORPUS_EXPANDED.jsonl`. They may include the original jobs.
- The original `SPEECH_CORPUS.jsonl` and `SPEECH_EVENT_CORPUS.jsonl` are the exclusion
  inventory. A matching original ID is skipped only when all six fields match
  exactly. Changed originals, overlapping IDs and repeated new lexical groups
  fail before any teacher loads. The exclusion receipt records actual counts and
  corpus hashes. Only the approximately 3,622 new jobs are authored.
- The selected original A2, accepted original/soft Qwen references, accepted Cosy
  happy/chuckle instructions, teacher weights, code and isolated environments use
  the same pinned source contracts as the original renderer. Cosy neutral remains
  prohibited. There is no pitch/time manipulation or synthetic emotion scaling.
- Recipe schema remains **3** and metadata remains `unity-voice-dataset-v2`.
  `source_id` remains the canonical hash of the complete renderer. Clip IDs remain
  the established hash of source ID, exact job and exact route.
- Renderer hashes include both new tool files, the imported original builder and
  worker helpers, `dataset_contract.py`, `speech_text.py`, profiles, policy,
  accepted source receipt, actual source files and installed package metadata.
  New optimization parameters and the immutable job grouping schedule are part
  of the renderer identity. The old renderer's source ID is never assigned to
  newly generated WAVs or changed to describe these optimizations.

## Actual optimization

Qwen 0.1.1's installed `generate_voice_clone` supports a list of target texts and
a reusable list of `VoiceClonePromptItem` objects. Fixed group sizes are **1, 2 or
4**. Groups use one approved reference profile, sort by lexical word count,
character count and ID, and remain identical when the same recipe is resumed.
One SHA-derived seed belongs to the **entire group**. It is not an independent
per-clip seed; changing batch size or group inventory changes output identity.
The source contract makes no bit-for-bit cross-device reproducibility claim.

The worker observes the pinned Qwen talker generation result's first-codebook
EOS flags. If any group member has no actual EOS, the group is rejected before
publication. This guards against silently publishing a generation-limit cutoff;
ASR and listening must still establish correct words and natural performance.

Cosy remains serial. Its pinned `add_zero_shot_spk` builds an in-memory frontend
cache. Each key hashes the full source ID, original reference SHA and text, exact
instruction name and exact instruction string. The cached prompt tokens are
compared with extraction of that exact instruction. Happy and relaxed-smile
instructions have separate entries. `save_spkinfo` is never called, and no cache
is saved inside a model directory. ONNX tokenizer and speaker providers are set
to CPU and read back; Torch synthesis stays on CUDA.

Teachers run in separate sequential processes. At least eight GiB of free local
GPU memory is required before loading. Fixed batch 2 is an **unbenchmarked
initial choice**. Memory sufficiency and speed must be observed on the real rig;
GPU utilization alone does not prove extra safe capacity. There is no automatic
OOM retry or silent fallback to a different batch size.

## Publication and failure containment

All WAVs in a group are validated before any group member is published. Files are
24 kHz mono PCM16. The unchanged source bounds are 0.25–30 seconds; unchanged
student preprocessing bounds still apply, including 512 phonemes. The owner's
longest training turns are short paragraphs of 3–5 medium sentences. A recording
that exceeds the actual limits is preserved for review rather than truncated.

Every WAV uses an exclusive temporary creation and no-replace publication.
Metadata is fsynced. A `source-owner.lock` prevents concurrent orchestrators in
one folder. A stale lock, orphan WAV, torn journal, missing group timing record,
partially published group, OOM or source mismatch requires explicit review.
Failures get their own receipt; interrupted output is never automatically
deleted, relabeled or rerendered under altered parameters.

`source-timing.jsonl` records actual group IDs, seeds, job IDs, inference walltime,
audio duration, Qwen EOS observations and peak/free GPU memory. Inference timing
is synchronized and explicitly excludes model loading, prompt setup and file
publication. `source-build.json` binds the final dataset, recipe, runtime receipts,
optimization identity and complete timing file SHA. Neither is human acceptance.

Owned worker deadlines use `VOICE_SOURCE_SETUP_SECONDS` (default 180, maximum
1,800) plus `VOICE_SOURCE_CLIP_SECONDS` (default 300, maximum 1,800) per remaining
recording, with a seven-day absolute maximum. A timeout terminates only that
owned child tree. It does not stop unrelated programs. Failure/timeout receipts
and unfinished group files remain available for review.

## Execution and bounded comparison

These commands are **authoring instructions**, not evidence that either new
teacher path has executed. Run only after the original teacher process exits.
The expanded input files must already exist. A fresh output folder is required
for each changed renderer, group size or benchmark scope.

```powershell
& 'C:/Program Files/Python310/python.exe' -B -u training/voice/make_dataset_optimized.py `
  .local/voice-lab/dataset/A2-expanded-new-3622-optimized-v1 `
  --all --qwen-batch-size 2 `
  --model-dir .local/voice-lab/models/qwen3-tts-base `
  --qwen-python .local/voice-lab/.venv-qwen/Scripts/python.exe `
  --cosy-python .local/voice-lab/.venv-cosy/Scripts/python.exe `
  --cosy-code-dir .local/voice-lab/models/cosyvoice-code `
  --cosy-model-dir .local/voice-lab/models/cosyvoice3
```

Adding `--plan-only` produces a frozen recipe using standard-library file hashes
and environment metadata probes only. It loads no model and touches no GPU.

A later explicitly requested bounded source comparison may use the same command
with `--benchmark-teacher qwen --benchmark-limit 12` instead of `--all`, and fresh
folders for `--qwen-batch-size 1`, `2` and `4`. It selects the same representative
new texts, both grouped lexical splits and available approved reference routes.
Sampling seeds and resulting WAVs differ by source identity; comparing elapsed
time does not establish identical audio or approved quality. Cosy can likewise
use `--benchmark-teacher cosy --benchmark-limit 12`, comparing against a separate
uncached source authoring run when one is explicitly prepared.

## Downstream compatibility

The original standard-library `make_dataset.load_recipe`, `expected_rows` and
`read_metadata` can inspect this schema-3 recipe. The existing offline source ASR
tool can inspect its exact metadata. Merger code must additionally call
`make_dataset_optimized.validate_optimized_plan`, verify all new and imported
helper hashes, and bind the new source-build runtime/timing files. A merged
dataset preserves each parent row's original raw ID, source ID and WAV SHA.
It needs a separate truthful merge receipt, not a fabricated single renderer.

Owner approval of the 32 heard recordings is limited to those exact WAV bytes,
texts and controls. No optimized recording inherits human acceptance merely
because it has the same target text or A2 reference. All new source identity,
transcript, natural emotion and performed laughter remain review work. Student
training and pod rental remain prohibited until the owner's later explicit go.
