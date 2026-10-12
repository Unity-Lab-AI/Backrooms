# Voice: lead review of the ChatGPT handoff (2026-10-12)

The owner asked for this review in these words: *"chatgpt add a bunch of work to the voive stuff so look it all over of what all changed that u arent aware of ... error check it and understand how the training will/needs to work"*, and *"fyi be aware chatgpt used agents so i dont always trust their work"*.

**How it was done:**
- Three read-only reviews ran in parallel: the student model code, the source-data pipeline, and the pod and launch stack.
- The lead read the handoff (`docs/NOW.md`), the live job state, git and the system.
- Every claim below was checked against code or live state. Where something was checked by hand or by tracing rather than by running, it says so.
- Nothing was executed, trained, rented or edited under `training/voice/`, because the running background job fails closed if any of its 89 frozen inputs change.

## 1. What the work is now

The rejected Kokoro-blend voice (round 2 #5) is gone. The voice is a new one called **A2 "low warm alto"**:
- It was designed with Qwen3-TTS VoiceDesign (seed 11032), and the owner approved it.
- Training audio is rendered by two *teacher* models: Qwen3-TTS Base, which clones from A2 reference audio, and CosyVoice3, which follows instructions.
- The owner heard and accepted a 32-clip mixed pilot.

| Stage | Tool | State |
|---|---|---|
| Text | `build_corpus.py`, `build_event_corpus.py`, `build_expanded_corpus.py` -> 5,000 lines (4,850 ordinary + 150 laughter-marked), 9 emotion labels, 7 speech acts | done |
| Audio | `make_dataset.py` (seed, 1,378) and `make_dataset_optimized.py` (expansion, 3,622) through `source_workers*.py` | seed recording now |
| Screening | `inspect_source_audio.py` (faster-whisper ASR, CPU), `summarize_source_screen.py`, `recheck_source_words.py` | running with the seed |
| Merge and curate | `merge_source_datasets.py`, `merge_source_qa.py`, `curate_dataset.py` (a listening form; nothing unheard is accepted) | waiting |
| Features | `prep.py` + `feature_arrays.py` + `speech_text.py` | pilot done (`feats/A2-reviewed-32-v4-ready`) |
| Student (ours, from random weights) | `model.py` (FastSpeech2-style, own aligner, pitch/energy/duration, emotion + speech-act conditioning, laughter/breath tokens), `vocoder.py` (HiFi-GAN V1), `train_acoustic.py`, `train_vocoder.py`, `student_state.py`, `infer.py`, `speech_turns.py` | **never run after the rewrite** |
| Pod | `pod/` Dockerfile + locked environment, `bootstrap_voice.sh`, `run_voice.sh`, preflight, upload, publish, eval | built locally, **not launchable** (section 4) |
| Gate | `quality_gate.py` + `VOICE_QUALITY_GATE.json`: `training_allowed: false`, 9 of 10 checks unaccepted | closed by design |

The background supervisor (`run_expanded_preparation.py`, PID 12020) does the following in order:
1. Waits for the seed recording and its screening.
2. Renders the 3,622 expansion clips.
3. Screens, merges, builds features and packs a delivery tar.

It runs **no training**. The live job is healthy: the seed is at about 1,025 of 1,378, with 969 of 1,015 screened clean. The reviewer's estimated finish is the evening of 2026-10-12 or overnight.

### How training will work

The **acoustic model** takes phonemes plus an emotion embedding (9) plus a speech-act embedding (7) plus an MLP over (intensity, pace), all summed into the encoder input. From that it predicts per-phoneme duration, pitch and energy, then decodes a mel spectrogram.
- Durations come from its own aligner: forward-sum CTC plus a monotonic alignment search, compiled with numba. That search is **still exact** when traced.
- `[laughter]` and `[breath]` are single dedicated tokens, and their length is learned like any other phoneme.

The **vocoder** (HiFi-GAN V1) turns mel into 24 kHz audio. It trains on real mels first, then on the acoustic model's ground-truth-aligned (GTA) mels. Mel and audio hop counts match exactly (a 384-sample reflect pad and 256 samples per frame).

`infer.py` refuses any (emotion, act) pair, intensity or pace outside what TRAIN data contains. It splits paragraphs into bounded chunks, and the speech act is guessed from punctuation.

## 2. Findings, most important first

1. **The emotion labels mostly aren't real.** *Confirmed in `SOURCE_DELIVERY_POLICY.json:42-78`.*
   - The 9 labels are rendered through only 4 conditions: neutral and warm use Qwen original; sad, concerned and frustrated use Qwen soft; happy, excited and surprised use Cosy natural_happy; amused and laughter use Cosy relaxed_smile.
   - Qwen Base cloning has no emotion control.
   - Every clip has pace 1.0, and intensity 0.0 (neutral) or 0.35 (everything else). So the intensity and pace inputs are trained on constants, and "frustrated" can't sound different from "sad".
2. **Laughter is never verified.** All screened rows have `event_audibility: "not_inferred"` (`inspect_source_audio.py:138`), and the ASR strips the event tags. A clip where the teacher skipped the laugh still passes. Only 150 of 5,000 lines (3%) carry laughter, and no breath audio was accepted.
3. **The text doesn't sound like her.**
   - It reads like a polite assistant describing chores: *"The spice jars are arranged with their labels facing the front."*, or *[excited] "There are familiar landmarks near the entrance, so we can begin without rushing ahead."*
   - 34% of ordinary lines start with "The", and stock phrases repeat dozens of times ("we can keep the" ×60).
   - The lines are built from pipe-delimited topic templates (`build_expanded_corpus.py:104`).
   - There's almost no gaming or streaming, no reactions, and laughter is tacked onto bland sentences.
   - Since a model learns delivery from what it hears, this is a direct cause of "not human".
4. **Checkpoints are tied to source bytes** (`student_state.py:5-17`).
   - Any edit to 9 files (`infer.py` included), even a comment or a line-ending change, makes training refuse to resume and `infer.py` refuse to load.
   - Resume and export also need identical `--frames`, `--seed` and `--batch`.
   - The GTA vocoder is tied to the exact `acoustic.pt` hash, so more acoustic training after the export breaks the pair.
   - That's sensible for a release, but it makes iterating very hard.
5. **One frozen receipt is CRLF:** `receipts/local-environment-build.json`. With `*.json eol=lf`, a clone would get different bytes and the pod's manifest check would fail. **Fixed** in `.gitattributes` (`-text` for that file only, so it's stored as-is). No file changed.
6. **The expansion runs on an unbenchmarked renderer** (`make_dataset_optimized.py`, Qwen batch 2), and it's fail-closed per batch with no retry (`source_workers_optimized.py:232,242-244`). One runaway line stops all 3,622. The merge also requires 5,000 or more rows exactly (`merge_source_datasets.py:280`), so any dropped clip fails the run at the very end.
7. **Silent-hang risk:** if the seed screener dies without a `summary.json`, the supervisor polls until its 48 h deadline (`run_expanded_preparation.py:178-183`).
8. **Smaller items:**
   - `zero_infinity` was turned off in CTC (`model.py:116`), so an infinite loss is now a hard stop.
   - The aligner distance via `|q|²+|k|²-2qk` under global TF32 loses some precision (`model.py:102`).
   - `cudnn.benchmark` with variable-length batches makes the early steps slow.
   - The binarization loss starts at step 6,000, so a 1-hour run may never reach it.
   - The vocoder saves only every 5,000 steps.
9. **Over-engineering:** about 7,700 lines of Python with receipts, digests and gates everywhere, many of them self-attested strings. Validation is repeated 2–3 times. There are four overlapping audition scripts and two renderer stacks. **Provenance is proven; quality is not**: nothing tests emotional contrast, laughter or naturalness.

What held up: the alignment search is exact; the frame and hop maths is right; the held-out split is by transcript hash; the job is healthy and doing what the handoff says; Docker did only what it says (section 5).

## 3. System fit: `DumbAss`

Owner, verbatim: *"before we train anything we need to do a proper review of our GPU and system to be sure everything needed from image gen to the playing model to the twitch broweser to windows, to the voice model all have to fit on our system here, which i think is called dumbass. but should run better if i ever get a new system."*

The hardware: Ryzen 7 5800X (8 cores / 16 threads), 128 GB RAM, RTX 4070 Ti SUPER 16 GB (driver 617.14), C: 176 GB free, D: 1.7 TB free.

| While streaming | VRAM GB | Source |
|---|---|---|
| Windows + Twitch browser (Chromium) | ~1.5 | BRAIN_PLAN budget |
| OBS (NVENC encode, scenes) | ~2.0 | BRAIN_PLAN budget |
| RimWorld, 294 mods | ~3.0 | BRAIN_PLAN budget; peaks on big maps |
| `unity-brain` IQ4_XS + vision projector + 32K q8 KV + buffers | ~6.8 | measured model 6.2 GB in Ollama |
| `unity-local` 8B voice-text model (own Ollama on :11435, kept warm 30 min) | ~5.5 | still in use: the brain lost the pod voice eval |
| **Steady total** | **~18.8** | **over 16 GB by ~3** |
| + webcam render (SD 1.5, CPU-offloaded) | +1.0-2.2 | on demand |
| + our TTS student (~39 M params, fp16) | +0.3-0.5, or 0 on CPU | estimate |

**The voice-text model doesn't fit beside everything else.** The likely fix is to let `unity-brain` write the voice lines too:
- It won a local 10-line A/B 10 to 6.
- Turning it on is one file: `training/models/brain-voice.ok`.
- That brings the steady total to about 13.3 GB, plus the TTS. A render peak of about 15 GB still fits.

If RimWorld runs hot, `unity-face-sd.py` can switch to `enable_sequential_cpu_offload()` (≤ 1 GB). The TTS student can also run on the CPU: a 14 M-parameter HiFi-GAN is roughly real-time on a 5800X, though that's unmeasured.

The Qwen and Cosy teachers (about 8 GB now) are **build-time only** and must never run during a stream. Measure all of this live, with every service up, before the voice is swapped. A newer GPU (24 GB or more) would remove the squeeze.

## 4. Pod readiness: not ready

Owner, verbatim: *"making sure everything is doone, pushed and cascade to remotes and is 100% ready for pod rental then await instructions."*

Everything is pushed. It is **not** ready to rent, and none of the pod code can change until the background job finishes, because all 18 pod files are frozen inputs. The blockers:
1. **Self-stop would likely fail.**
   - The custom entrypoint (`start_no_training.sh:14`) runs sshd as PID 1, and SSH sessions don't inherit RunPod's `RUNPOD_POD_ID`/`RUNPOD_API_KEY`.
   - So `runpodctl pod stop` (`bootstrap_voice.sh:77`) fails unauthenticated, and the pod keeps billing.
2. **An SSH drop ends the run.** Training is started from an interactive shell, and `trap 'exit 129' HUP` (`bootstrap_voice.sh:107`) turns a dropped connection into teardown. There's no nohup, setsid or tmux.
3. **The dataset is uploaded by scp to a running H100** (`upload_dataset.ps1:25-28`), so hours of transfer happen on paid time. A network volume should be filled first from a cheap CPU pod.
4. **No progress view without SSH.** The GET-only status server from the first design was removed.
5. **The image is local only.** `preflight_voice.py:57-60` requires a registry digest, but no registry, credentials or push exist. The owner has to decide this.
6. **Strict checks fight the run:** a restarted pod with a new billing epoch refuses to resume (`run_voice.sh:139-149`); it requires exactly one GPU named "H100" (`:166-173`); there are 16 required env vars, three of them hand-written receipts.
7. **The CUDA side is fine:** torch 2.7.1+cu126 supports sm_90. Filter RunPod hosts to CUDA 12.6 or newer.

**Recommended path** (the pod reviewer's and the lead's):
- Drop the custom image for this run.
- Use RunPod's PyTorch template plus a network volume.
- Clone a **pinned commit**, check the manifest, and pip install into a venv on the volume.
- `nohup setsid` the runner and put the GET-only progress server back.
- Keep the good new pieces: the billing-epoch deadline, process-group timeouts, bounded stop retries and run-ID namespacing.

This needs the job to finish first, then a reviewed code change with a new manifest.

## 5. Docker: what it actually did

Owner, verbatim: *"it opened docker and did some stuff too."*

- **What changed:** Docker Desktop 4.42.0 / engine 28.2.2. Only the transient `run/dockerInference` directory was quarantined (`%LOCALAPPDATA%/Docker/run.quarantined-20261011-A2-prep`, backup kept).
- **What was built:** the local image `unity-a2-prep:20261011-v2` (Python 3.10.18, 103 pinned packages, 10.1 GB unpacked). Its archive `.local/voice-lab/pod-build-artifacts-2026-10-11-v2/unity-a2-environment.docker.tar` is 3.4 GB and gitignored.
- **Containers:** one inspection container was created, never started, then removed.
- **What did not happen:** no reset, prune, reinstall or registry push.

## 6. Local proof run (when the owner says go)

Owner, verbatim: *"we will train a small model locally to test fesabuility and setup for a hour traing test run to see if its learning and if it at all sounds right before we rent a pod on runpod."*

- **Data:** the 32-clip pilot (`feats/A2-reviewed-32-v4-ready`, 84 s) only proves the pipeline runs, because it memorises. For a real test:
  1. Snapshot the 1,000+ seed clips already recorded (`dataset/A2-full-1378-draft-v3`) into a **new folder outside `training/voice/`**. That folder is still being written, so copy a prefix of `metadata.jsonl` plus the matching WAVs.
  2. Run `prep.py <snapshot> <new feats>` on the CPU.
- **Training, about 1 hour on the 4070:**
  - acoustic `--frames 12000` (~30 min)
  - vocoder `--batch 8` (~30 min; the default of 32 is refused below 32 train clips)
  - `--export-gta`, then about 15 minutes of GTA vocoder
  - `infer.py` on independent text, then listen
  - Set `PYTHONDONTWRITEBYTECODE=1` and `NUMBA_CACHE_DIR=.local/voice-lab/numba-cache`.
- **Expectations:** the step speeds for this code are unmeasured. The binarization loss won't engage before step 6,000. Only neutral/statement/question and the trained 0.35 combinations will be accepted at inference.
- **GPU:** while the Qwen recorder runs it holds about 8 GB, so either wait for the job or keep the batches small. Never run this during a stream.

## 7. Making the Twitch model actually emote

Owner, verbatim: *"we are going to have to maybe retrain or adjust propmpts or something so that the model doing the twitch accually uses laughter and emotions and human ticked and modujulated speech inconjunction with what the voice model can do."*

1. **Fix the vocabulary at the voice end first.** The brain can only be taught tags the voice was trained on. Today that's the 4 real render conditions behind 9 labels, 7 speech acts and `[laughter]`. Either collapse the labels to what's real, or render real contrast for each label.
2. **Then teach the brain to write delivery:**
   - an emotion/state per line;
   - `[laughter]` and `[breath]` where natural;
   - human texture: fillers, reactions, self-corrections, short asides.
   
   Start with the voice prompt (`.claude/tools/unity-voice.py`, `.local/qa/stream-host.py`). If prompting doesn't hold, add tagged rows to `training/data/brain/` and retrain.
3. **The runtime path is unbuilt** (`training/voice/RUNTIME_INTEGRATION_PLAN.md`): a persistent synth, a queue, ordered playback acknowledgements, and keeping the tags through the overlay chain, which strips non-verbal markers today. The clean-stream LAW still applies to every spoken line.

## 8. Recommended order

1. Let the background job finish. Don't touch frozen inputs.
2. **Owner listens** to about 20 clips across the soft-profile labels and the laughter lines, and decides on the corpus text: regenerate it in her streamer voice, or keep it.
3. Run the local 1-hour proof on a snapshot of real recorded clips, and listen.
4. Then a reviewed code pass (new manifest):
   - fix the pod blockers;
   - relax the byte-identity locks for iteration;
   - collapse or realise the emotion labels;
   - add a laughter-presence check.
5. Re-measure the stream VRAM budget live, and decide brain-as-voice-writer.
6. Only then quote and rent the pod.
