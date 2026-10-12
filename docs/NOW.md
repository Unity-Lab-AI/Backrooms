# NOW — Unity A2 voice: local preparation handoff

> **Lead review, 2026-10-12. Read this first.** The handoff below is ChatGPT's and is accurate about *what was built*. The lead's review of it is in [VOICE_LEAD_REVIEW_2026-10-12.md](implementation/VOICE_LEAD_REVIEW_2026-10-12.md). In short:
> - The background job is healthy. Leave it alone.
> - **It is not ready to rent a pod.** The pod self-stop would likely fail, an SSH drop ends the run, the upload happens on paid time, and there is no registry. All pod and student code is frozen until the job ends.
> - The 9 emotion labels rest on only 4 real render conditions, and laughter is never verified.
> - The corpus text reads like an assistant, not a gamer-girl streamer.
> - The stream VRAM budget is ~3 GB over 16 GB while `unity-local` still writes voice lines.
>
> Next steps wait on the owner: listen to ~20 clips, decide the corpus text, then run a 1-hour local proof on real recorded clips. **Nothing trains or rents without the owner's go.** The TODO rows are under "Voice -- ChatGPT handoff, lead review and pod readiness".

**Updated 2026-10-12, after the 2026-10-11 voice work.** Project root: `C:\Users\gfour\Desktop\Backrooms`. This handoff is for the lead agent to resume local preparation without waiting for all recordings. The previous handoff is preserved as [pre-background-NOW.md](implementation/evidence/voice-prespend-2026-10-11/pre-background-NOW.md); the earlier rejected-voice handoff is [prior-NOW.md](implementation/evidence/voice-prespend-2026-10-11/prior-NOW.md).

## 1. What is ready, and what is running

- Original **A2 low warm alto** is the approved identity: `unity-a2-low-warm-alto-v1`. The accepted 32-source listening set is curated and prepared. Our own acoustic/vocoder student is **untrained**. Live speech still uses Piper.
- The expanded **5,000 text jobs exist**: 4,850 ordinary turns and 150 laughter-marked turns. All 1,378 existing jobs are retained unchanged; only 3,622 additions will be recorded. This is a text inventory, not 5,000 completed or accepted WAVs.
- Docker recovery and the authorized local Linux environment build are complete. Actual packages, runtime files, image ID and archive are saved. The image has not been published to a registry and no pod exists for this work.
- A persistent hidden local preparation supervisor was actually launched at **2026-10-12 06:05:52 UTC**, PID **12020**. It is waiting for the existing seed recording/screening jobs, then will run expansion, QA, merge, features and local delivery. No student training command is in this pipeline.
- At the saved **06:07:20 UTC** snapshot, the seed had **945/1,378 recordings**, **944 screened**, **0.6272 hours** of source audio and **108,429,460 WAV bytes**. Seed and screening completion receipts did not yet exist. Read the live status for later progress; these counts are historical snapshots.
- **Training, rental, uploads and deployment remain prohibited.** `VOICE_QUALITY_GATE.json` keeps training/deployment false and owner training authorization unaccepted. Finishing this background job does not change those flags or accept unheard audio.

Current immutable source digest, **89 inputs**:

```text
7138ec0643a19b3db60ffa1dc5bd4d2739b93e5ca25a439b7f3490f4dedf7e00
```

[VOICE_MANIFEST.json](../training/voice/VOICE_MANIFEST.json) is the complete file-by-file frozen input inventory. [background-handoff.json](implementation/evidence/voice-prespend-2026-10-11/background-handoff.json) saves its full SHA map, launch arguments and actual progress snapshot. The older 43-input digest is historical and cannot launch this recipe.

## 2. Owner directions — keep these binding

The owner selected original A2, accepted its everyday/playful/soft/question variations, and requested natural emotional range without forcing higher pitch. Desired delivery is a warm, familiar adult American girl-next-door/gamer-coder voice with authentic jokes, smiles and little chuckles.

Exact later directions:

> the original A2 but some type of emotional range  thats not forced and not just high pitch maxing

> sounds great but dont use nutral one nutral one it terrible

> they are all good just go ahead and finish up soi you in reguards of being ready for the pod run but no start yet and no pod rental yet

> Expand to at least 5,000 varied recordings with several hours of speech before considering a pod (Recommended)

> longest replies trained on anly need to be short paragraphs like 3-5 medium sentences. she will never be a lecutrure but lets leave it open ended so even tho not trained to do pages and pages lets let her anyways

> and when you are done and ready to hand off to the other agent thats the boss, write a proper Now.md write up documenting all the files youve used and everything weve done today on this voice model so it not in the dark on any of it you dont have to wait on the 5k samples just set it all up and finalized but the 5k traing clips can be run in the back ground after you wrap up so that once it lands its all done.. we are nt waiting 12 hours to hand it back to the boss ai. so you need to wrap it up but for the local run and he will pick up the continueation of the 12 hour run

Docker authorization was **"Yes — local Docker build only"**. The standing **"let me know before u start a training"** still applies. Background source recordings are authorized; student training, pod rental/start and paid run approval are separate and absent.

Cosy `1-neutral` is the rejected performance. **Original A2 everyday/neutral remains accepted.** Do not discard original A2 neutral by confusing these. Flat happy delivery, sarcastic B2, cartoon/anime D1 and the old Kokoro voice recipe remain rejected. No real person's recording or celebrity clone is used.

## 3. First actions for the lead

1. Read this handoff, [VOICE_PLAN.md](../training/voice/VOICE_PLAN.md), [SOURCE_QA_POLICY.md](../training/voice/SOURCE_QA_POLICY.md), [expanded text plan](../training/voice/EXPANDED_CORPUS_PLAN.md), [optimized source contract](../training/voice/OPTIMIZED_SOURCE_CONTRACT.md), [merge contract](../training/voice/MERGED_SOURCE_CONTRACT.md) and [runtime integration plan](../training/voice/RUNTIME_INTEGRATION_PLAN.md).
2. Read the live job files below. **Do not run the launcher again** or start a second source teacher. PIDs in this document are snapshots; verify executable, command line, status timestamp and output before acting on a PID.
3. Leave frozen voice inputs, teacher environments/models and gate JSON unchanged while this job runs. The supervisor checks manifest/source/gate integrity every 30 seconds and fails closed on changes. Other project work outside these inputs can continue.
4. If the job completes, inspect `result.json`, merged QA, actual audio hours, durations and feature/delivery identities. The result remains `completed_candidate_not_accepted`. Review/curate the recordings before accepting a full training dataset.
5. If it fails, read `failure.json` and per-stage stderr. Preserve source, partial outputs and receipts. Resolve the actual error and plan a fresh, explicitly reviewed continuation; do not delete evidence, silently lower batch size or replace the source identity.

### Active local job paths

All paths below are relative to the project root unless an absolute path is shown.

| File / process | Purpose and current ownership |
| --- | --- |
| `.local/voice-lab/background/A2-expanded-2026-10-12-v2/launcher.json` | Actual launch receipt: PID 12020, exact arguments, 89-input digest and no-training/no-rental scope |
| `.local/voice-lab/background/A2-expanded-2026-10-12-v2/pipeline/status.json` | Live atomic stage, timestamp, elapsed time and owned child PIDs; refreshed about every 30 seconds |
| `.local/voice-lab/background/A2-expanded-2026-10-12-v2/run.stdout.log` / `run.stderr.log` | Supervisor output and errors |
| `.local/voice-lab/background/A2-expanded-2026-10-12-v2/pipeline/logs/` | Per-stage stdout/stderr and owned-process cleanup records when needed |
| `.local/voice-lab/background/A2-expanded-2026-10-12-v2/start-background-source.ps1` | Already-used hidden host launcher; refuses a duplicate receipt |
| `.local/voice-lab/background/A2-expanded-2026-10-12-v2/host-readback.json` | Final host read-back at 06:14:19 UTC: supervisor, seed and screening process command lines observed; supervisor stderr empty |
| Seed: `.local/voice-lab/dataset/A2-full-1378-draft-v3/` | Existing original generator PID 31052; Qwen proxy/worker last recorded as 30868/29028; not children owned by the new supervisor |
| Seed QA: `.local/voice-lab/dataset/A2-full-1378-screen-v2/` | Existing CPU ASR watcher PID 3800; also not owned by the new supervisor |
| `.local/voice-lab/background/A2-expanded-2026-10-12-v1/` | Preserved first sandbox launch: reported PID 34580 did not persist; no pipeline status appeared. `launch-observation.json` records this. **Use v2.** |

The original tool sessions were recording **87860** and CPU screening **66138**; a later agent may not have their session handles, so use saved files and verified host process records. Sandboxed process listings did not expose host jobs; host-authorized read-only CIM showed the existing seed/ASR processes. The v2 host launcher produced actual live status; the failed sandbox launch was not represented as success.

The job's **48-hour local deadline** is a failure bound, not a promised duration or paid budget. Prior short seed clips ran about 6.98 clips/minute over one measured window. Batch 2 and longer paragraphs have not been benchmarked. A 12-hour forecast is not verified. Keep the PC awake and preserve the running jobs for continuation. Final source-manifest read-back passed unchanged; 44 relative links across this handoff, voice plan and review resolved to existing local files.

### Background sequence and planned outputs

[run_expanded_preparation.py](../training/voice/run_expanded_preparation.py) actually runs this local-only sequence:

1. Wait for the existing seed `source-build.json` and complete screening `summary.json`; verify their dataset identities.
2. Make a full seed summary and second CPU ASR recheck of residual word disagreements.
3. Run the new optimized renderer for **only 3,622 additions**, fixed Qwen batch 2 and exact approved Cosy instruction/reference caching. Teachers are sequential; no second GPU teacher overlaps the original seed.
4. Screen expansion rows concurrently on CPU, then summarize/recheck the complete expansion.
5. Merge unchanged seed/expansion WAVs and both QA packets; require at least 5,000 clips and retain each parent's actual provenance/source IDs.
6. Create a fully pending listening form. No unheard row is marked listened/accepted.
7. Prepare fresh candidate features locally on CPU, verify dataset/feature equality, perform offline source/data preflight and make a local delivery archive.
8. Save a locked launch config with source/data identities filled and price/image/provider/storage/authorization fields unset. Verify delivery dataset/source/archive/status before saving the final candidate result.

**Planned until they appear**, under the v2 `pipeline/` directory:

- `seed-summary/`, `seed-word-recheck/`
- `expansion-source/`, `expansion-screen/`, `expansion-summary/`, `expansion-word-recheck/`
- `merged-5000-candidate/`, `merged-source-qa/`, `candidate-listening.pending.json`
- `local-candidate-features/`, `delivery/delivery.tar`, `delivery/packet.json`
- `launch-config.locked.json`, `result.json`; or `failure.json` if interrupted/refused

This supervisor is not an automatic resume engine. The existing seed watcher has its own eight-hour bound; the expansion watcher has its own at-most-24-hour bound inside the 48-hour supervisor. If a preexisting process dies without its completion receipt, the supervisor waits until its bound unless a saved timeout receipt is seen. The lead must inspect liveness/logs and plan recovery. Failed feature extraction leaves its `.preparing-*` sibling intact. Partial optimized groups/orphan WAVs require explicit review; do not reuse a different recipe in the same folder.

## 4. Work completed during this voice preparation

### A2 identity, emotion and actual listening

The approved original was generated with Qwen VoiceDesign seed 11032, then reused as the speaker reference. The original raw reference SHA is `df05af0bd6c0922a9946cab5e92bf692e079454f9a4de2d570e79f2c962267c8`.

[SELECTED_VOICE.json](../training/voice/SELECTED_VOICE.json), [REFERENCE_PROFILES.json](../training/voice/REFERENCE_PROFILES.json), [SOURCE_DELIVERY_POLICY.json](../training/voice/SOURCE_DELIVERY_POLICY.json) and [source-auditions.json](../training/voice/receipts/source-auditions.json) preserve literal selections, configurations, source revisions and hashes. Fourteen raw/listening reference WAVs exist in `training/voice/reference/`: original, everyday, playful, soft, questions, natural happy and chuckle pairs.

Qwen Base uses reference audio/text and does not supply the same acting instruction interface as VoiceDesign. Its happy contrast was inadequate, so accepted original-reference Cosy `2-natural-happy` and `4-little-chuckle` supply happy/chuckle source deliveries. Everyday/warm uses Qwen original; sad/concerned/frustrated uses approved Qwen soft; happy/excited/surprised uses Cosy natural happy; amused/events uses Cosy relaxed smile. These are intended route labels, not proof every future performance is correct.

The mixed pilot produced **32 recordings / 84.160042 seconds**, 17 Qwen then 15 Cosy, with nine intended states and seven speech acts. Markdown audio delivery initially showed no playable clips to the owner. Native audio delivery then succeeded, and the owner accepted all 32. The actual receipt binds the heard waveform SHA, transcript and controls; source approval is not copied onto new unheard recordings.

| Actual artifact | Identity / use |
| --- | --- |
| `.local/voice-lab/auditions/2026-10-11-A2-mixed-32-v3/` | Original mixed draft and source provenance |
| `.local/voice-lab/auditions/2026-10-11-A2-mixed-32-listening-v1/` | A/B/C listening packet, timestamps and guide; original reference first, constant gain and gaps only |
| `.local/voice-lab/auditions/2026-10-11-A2-mixed-32-v3-review-accepted.json` | Later actual human listening decision; original pending review retained |
| [pilot32-owner-listening.json](../training/voice/receipts/pilot32-owner-listening.json) | Exact accepted source-wave bindings; SHA `76315cb661ed5bf9fda7fc2b8fd52c04c35b365c53e020d937d442eddecc4e94` |
| [pilot32-corpus-acceptance.json](../training/voice/receipts/pilot32-corpus-acceptance.json) | Accepted curated pilot only; SHA `da13a442410ca8c9f470e85012d642af6d1a76ce15ce9eeb59ce3ae3c212f34f` |
| `.local/voice-lab/dataset/A2-reviewed-32-v3/` | Curated unchanged WAVs; dataset `06e9c2b2043e523b684eb7ce32a171dff91ce64af180f2f4a20faeefc710f9e7` |
| `.local/voice-lab/feats/A2-reviewed-32-v4-ready/` | Current actual pilot features `0401fbbfab96717480da47d51d2434a5214a4715f527380f506acdedc8ef5139`: 49 symbols, 31 train / 1 heldout, dedicated laughter token |

Earlier pilot feature caches and rejected legacy data remain historical. Do not revive the old Kokoro 5,206-clip source recipe, earlier pitch/energy presets, CSV format or old smoke checkpoints. The accepted 32 clips do not prove a sufficiently trained model; the pilot also has fewer train clips than the candidate vocoder batch 32.

### Source corpus and quality work

[build_expanded_corpus.py](../training/voice/build_expanded_corpus.py) created [SPEECH_CORPUS_EXPANDED.jsonl](../training/voice/SPEECH_CORPUS_EXPANDED.jsonl) and [SPEECH_EVENT_CORPUS_EXPANDED.jsonl](../training/voice/SPEECH_EVENT_CORPUS_EXPANDED.jsonl). Root independently read the text rows and confirmed exact 5,000 IDs and equality of all original job objects. [EXPANDED_CORPUS_PLAN.md](../training/voice/EXPANDED_CORPUS_PLAN.md) saves coverage and SHA values.

- 2,799 single-sentence turns, 1,641 two-sentence turns, 560 paragraphs of three or four medium sentences, 39–57 words. Longest training examples satisfy the requested short-paragraph direction; this does not impose a total live reply length cap.
- 95,437 lexical words; **8.37–11.36 speech hours is a word-rate estimate only**. Actual retained audio hours must be measured later.
- 65% neutral/warm; intended states: neutral 2,000, warm 1,250, happy 250, amused 300, excited 250, sad 250, concerned 250, frustrated 250, surprised 200.
- All seven speech acts; exact normalized split is 4,895 train / 105 heldout. The separate 38-row evaluation suite has zero exact lexical overlap. Shared scene sentences/paraphrases may still overlap; the text bank is not a guarantee of independent semantic families.
- 3,622 additions have distinct normalized lexical groups. The one old intentional ordinary/event duplicate remains. Fixed drafted pace is 1.0; neutral intensity 0.0 and other intensity 0.35. Wider ranges, breath performances, sobs and laugh subtypes are not supervised.
- Ordinary expanded SHA: `3e268623e8a6a555207c5ac91f5db9646d59909ca50a4838720cc66acb806498`; event expanded SHA: `6b263d8e6226285950e71ea4844e80a5d47859f805d2075bbcde8495824b874d`.

An actual **plan-only** production invocation inspected pinned files/environment metadata without loading a model: `.local/voice-lab/expanded-plan-2026-10-12-v1/render-recipe.json`. It reports **3,622 jobs / 1,378 skipped**; source `0bef0c96dc182ed03589c2dd96cbe593b426cdb67336670ceaa2cebbdcc245ac`, recipe `db157779470f0f8f58b392a4c951e34a9b3a57a9fb84d4fa8757366d79ebc936`. The later expansion builds its own recorded recipe; compare actual values rather than assuming an environment stayed unchanged.

Original seed source is `8abb75d3e26e8036311731861e5333f1cdaf0fe5f4044385716e4cfe56473798`, recipe `dba264ce8932ddff2da69147fd072c3c485223ba0d9db0a4e417fe49d9257680`. Its renderer recipe does not use the global manifest, so adding new preparation files did not rebrand the running seed.

The actual earlier partial QA snapshot was 449 rendered / 446 screened. Second CPU ASR rechecked nine residual word disagreements in 34.4 seconds: eight matched intended words; both recognizers heard "near" versus intended "nearer" in `a2-f9882de72a04cd2bfa7e7691`. This is a listening candidate, not conclusive proof or approval. Those preserved artifacts are `.local/voice-lab/dataset/A2-full-1378-summary-partial-v1/` and `A2-full-1378-word-recheck-partial-v1/`.

QA retains raw flags/transcripts, allows only narrow documented number/segmentation equivalences, and transfers prior listening only for exact matching WAV/text/control bindings. Events require audible-event review; absence of ASR flags does not establish adult identity, emotional quality or actual laughter. Read [SOURCE_QA_POLICY.md](../training/voice/SOURCE_QA_POLICY.md). Unknown ASR stage-direction markers may be refused by the strict transcript parser; if this occurs, preserve the failure and implement a separately reviewed screening revision rather than editing the running helper.

### Own-student source repairs and controls

[architecture-readiness.md](implementation/evidence/voice-prespend-2026-10-11/architecture-readiness.md) records source-level repairs: lower intermediate aligner allocation, predictor padding masks, strict int64/float32 feature checks, separate voiced/unvoiced targets, matched mel/audio hop counts, exact dataset/frontend/student/checkpoint identities, complete RNG and acoustic batch-cursor resume, finite gradient/state checks, unique temporary checkpoints and strict paired inference/GTA provenance.

Shared student code identity is `67b80dff1a5ca77c3544af2b525dd4c2ac45747c187cb0b3276a5115050dd18f`. The source files are `model.py`, `vocoder.py`, `prep.py`, `train_acoustic.py`, `train_vocoder.py`, `infer.py`, `feature_arrays.py`, `speech_turns.py`, `student_state.py`.

Actual local pilot preprocessing was completed. The later source reviews did **not** import/run our student, train weights, perform model math, benchmark or demonstrate interruption/RNG-exact recovery. These remain future validation. Both shell entry points and embedded Python passed syntax inspection; all 41 first-party Python files parsed at this final checkpoint.

`infer.py` supports only combinations/ranges/events actually represented in TRAIN metadata. Dedicated laughter/breath tokens exist, but no breath audio is accepted. Literal unique-phrase pauses and bounded utterance chunking are implemented; explicit word focus is refused without performed word-level supervision. Current limits: 512 phoneme tokens and 30 seconds per training clip; 120 seconds / 64 chunks / 12,000 characters per low-level `Voice.say` turn, with finite output checks. Paragraph tokens/durations need actual validation. Overlong source must be rejected and re-rendered from explicitly shorter new text, never squeezed by pitch/speed changes.

### Docker recovery, build and immutable environment

The reported Desktop error concerned the transient `run/dockerInference` endpoint. With Docker processes stopped and paths checked, only the transient directory was renamed to `C:\Users\gfour\AppData\Local\Docker\run.quarantined-20261011-A2-prep`. The backup remains. No reset/prune, data-volume deletion, reinstall or diagnostics upload occurred. Desktop 4.42.0 / engine 28.2.2 then started successfully.

First local build v1 failed the dependency check because `smart-open` required `wrapt`, absent from its PyPI JSON dependency list. The resolver now reads selected wheel METADATA/source PKG-INFO; v1 evidence is preserved. Corrected **v2 build exited 0**, with `No broken requirements found.`

| Actual v2 artifact | Observed value / path |
| --- | --- |
| Local image | `unity-a2-prep:20261011-v2`, Linux amd64, Python 3.10.18 |
| Actual local ImageID / OCI index digest | `sha256:3786ba627ace02b521b97f5aa9ef0f647fcad2133e73b1d69c7d0ced0e9ffd3f` |
| Installed inventories | 103 distributions, all matching 103 selected-artifact pins; 887 runtime asset files; 188 OS packages |
| Runtime asset roles | English model 28; espeak library/bundled files 369; espeak data 489; libsndfile 1 |
| Frozen build context | `.local/voice-lab/pod-build-context-2026-10-11-v2/` |
| Build/inspection/artifacts | `.local/voice-lab/pod-build-artifacts-2026-10-11-v2/` |
| Image archive | `unity-a2-environment.docker.tar` in that artifact folder; 3,429,147,136 bytes; SHA `bb7630a5dfdcd9b7354921161baf32d22de66a3ca47a871412410f41c47f7faa` |
| Permanent receipt | [local-environment-build.json](../training/voice/receipts/local-environment-build.json), SHA `4d5c2f19facfffa8592dfa4d8d17178c1ce8f9bdc01fbe15eac167342f478fa1` |
| Permanent actual inventories | `training/voice/receipts/environment-2026-10-11-v2/`: `observation.json`, `package-lock.json`, `runtime-assets.json`, `os-packages.tsv` |

The inspection container was created and never started, files copied out, then only that exact owned container removed; cleanup receipt is saved. No training/inference/model/SSH/ABI test ran in this image. Local Docker may remain running, with no preparation container running at cleanup. The local image ID/index is **not a registry-pullable reference**. Registry publication, actual H100/driver/functional compatibility, durable provider storage, stop/billing observations and the final priced configuration remain unresolved. See [docker-local-preparation.md](implementation/evidence/voice-prespend-2026-10-11/docker-local-preparation.md) and [ENVIRONMENT_PLAN.md](../training/voice/pod/ENVIRONMENT_PLAN.md).

## 5. Complete code and document map

Use the actual relative links from this root. The manifest enumerates every frozen input individually; the tables below explain how they connect. Local teacher installations, background outputs and historical evidence are intentionally outside the copyable RimWorld mod.

| Files under `training/voice/` | Responsibility |
| --- | --- |
| `audition.py`, `AUDITION_BRIEF_LOW_REGISTER.json`, `variations.py`, `A2_VARIATIONS.json`, `happy_audition.py`, `cosy_audition.py` | Audition/reference authoring tools; decisions are in the selected/config/policy/receipt files, not tool output alone |
| `SELECTED_VOICE.json`, `REFERENCE_PROFILES.json`, `SOURCE_DELIVERY_POLICY.json`, `reference/`, `receipts/` | Accepted identity, routes, exact permanent recordings and listening/environment observations |
| `build_corpus.py`, `CORPUS_PLAN.md`, `SPEECH_CORPUS.jsonl`, `build_event_corpus.py`, `EVENT_CORPUS_PLAN.md`, `SPEECH_EVENT_CORPUS.jsonl` | Frozen original 1,341 ordinary + 37 event seed jobs |
| `build_expanded_corpus.py`, `EXPANDED_CORPUS_PLAN.md`, `SPEECH_CORPUS_EXPANDED.jsonl`, `SPEECH_EVENT_CORPUS_EXPANDED.jsonl` | Complete 5,000 text inventory and measured text coverage; no new audio acceptance |
| `make_dataset.py`, `source_workers.py`, `dataset_contract.py`, `speech_text.py` | Original source builder/isolated workers and strict common schema/frontend; preserve while seed runs |
| `make_dataset_optimized.py`, `source_workers_optimized.py`, `OPTIMIZED_SOURCE_CONTRACT.md`, `SOURCE_THROUGHPUT_PLAN.md` | Expansion-only fixed Qwen groups and exact Cosy prompt caching, recorded seeds/EOS/timings; no silent fallback; batch 2 not benchmarked |
| `inspect_source_audio.py`, `summarize_source_screen.py`, `recheck_source_words.py`, `SOURCE_QA_POLICY.md` | Existing cached CPU ASR, conservative triage, original flags and exact prior hearing; no automatic human acceptance |
| `merge_source_datasets.py`, `merge_source_qa.py`, `MERGED_SOURCE_CONTRACT.md` | Byte-preserving complete parent merge and identity-bound QA retention; no fabricated single-renderer recipe |
| `curate_dataset.py` | Pending manual form and immutable human-reviewed subset; unheard rows remain pending |
| `finish_source_preparation.py` | Earlier seed-only orchestrator, not the new active 5,000 pipeline; do not start a competing job |
| `run_expanded_preparation.py` | Active local supervisor described above; strict output root/input existence, source/gate guard, fresh feature/delivery bindings and owned failure cleanup |
| `prep.py`, `feature_arrays.py`, `model.py`, `vocoder.py`, `train_acoustic.py`, `train_vocoder.py`, `student_state.py`, `infer.py`, `speech_turns.py` | Own-weight acoustic/vocoder, preprocessing, strict identities/resume and future inference; student still untrained |
| `LISTENING_EVAL_TEXT.jsonl`, `EVALUATION_PLAN.md`, `RUNTIME_INTEGRATION_PLAN.md` | 38 reserved independent evaluation texts, actual acceptance plan and still-unimplemented live integration |
| `VOICE_PLAN.md`, `manifest.py`, `VOICE_MANIFEST.json`, `quality_gate.py`, `VOICE_QUALITY_GATE.json` | Preparation narrative, immutable source inputs and separately validated closed acceptance/authorization gates |

| Files under `training/voice/pod/` | Responsibility |
| --- | --- |
| `Dockerfile`, `DEBIAN_SNAPSHOT.json`, `ENVIRONMENT_SPEC.json`, `environment.lock.json`, `resolve_environment.py`, `create_build_context.py`, `export_environment.py`, `start_no_training.sh`, `ENVIRONMENT_PLAN.md` | Pinned Linux recipe/build inventories and no-training initial container behavior |
| `LAUNCH_CONFIG.template.json`, `preflight_voice.py`, `prepare_launch.py`, `upload_dataset.ps1`, `accept_delivery.py` | Locked configuration, source/data/environment metadata checks and local immutable delivery; upload helper prints instructions, no upload executed |
| `bootstrap_voice.sh`, `run_voice.sh` | Future separately authorized student run, persistent budget/deadline, owned workers and bounded stop attempts; never call during this handoff |
| `atomic_publish.py`, `publish_voice.py`, `render_eval.py` | No-replace final directory publication and exact completed acoustic/vocoder/GTA/evaluation provenance; source reviewed, no student execution |

Additional evidence/docs used today: [VOICE_PRESPEND_REVIEW_2026-10-11.md](implementation/VOICE_PRESPEND_REVIEW_2026-10-11.md), [TODO.md](TODO.md), [data-readiness.md](implementation/evidence/voice-prespend-2026-10-11/data-readiness.md), [architecture-readiness.md](implementation/evidence/voice-prespend-2026-10-11/architecture-readiness.md), [preparation-evidence.json](implementation/evidence/voice-prespend-2026-10-11/preparation-evidence.json), Docker record, actual background receipt and preserved historical files in the same evidence folder. `AGENTS1.md`, `UNITY_MEMORY.md` and the current project decision index were consulted as project context; no central memory edits were made.

### Local source environments and cached weights

- Root/preprocessing interpreter: `C:\Program Files\Python310\python.exe` (3.10.6); user site supplies Torch/Torchaudio 2.7.1+cu118, NumPy 2.2.6, Misaki 0.9.4, PyWORLD 0.3.5, SoundFile 0.13.1.
- Source interpreters: `.local/voice-lab/.venv-qwen/Scripts/python.exe` and `.venv-cosy/Scripts/python.exe`. They inherit system/user-site packages. **Do not set `PYTHONNOUSERSITE=1`** or alter pip packages while active; that hides inherited Torch or changes provenance.
- Qwen Base: `.local/voice-lab/models/qwen3-tts-base/`, revision `fd4b254389122332181a7c3db7f27e918eec64e3`; original VoiceDesign revision `5ecdb67327fd37bb2e042aab12ff7391903235d3`.
- Cosy model `.local/voice-lab/models/cosyvoice3/`, revision `29e01c4e8d000f4bcd70751be16fa94bf3d85a18`; code `.local/voice-lab/models/cosyvoice-code/`, revision `074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc`, with Matcha revision `add9105b34bf2be2230f4aa1e4769fb586a3c824e`.
- Existing ASR root: `C:\Users\gfour\.cache\huggingface\hub\`. Base snapshot `models--Systran--faster-whisper-base\snapshots\ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`; second recognizer `models--Systran--faster-whisper-small\snapshots\536b0662742c02347bc0e980a01041f333bce120`. CPU/int8, offline, four threads; no new ASR downloads needed.

These Windows source installations are not the Linux student's container environment. Qwen/Cosy source teachers will not enter the intended deployed own-student speaking path.

## 6. Live integration design and remaining work

[RUNTIME_INTEGRATION_PLAN.md](../training/voice/RUNTIME_INTEGRATION_PLAN.md) inspected the existing `.claude/tools/unity-say.py`, `unity-voice.py`, `unity-speak.py`, `persona-studio.cjs`, `persona-studio.html`, `stream-overlay.html`, `obs-setup.py`, `twitch-bridge.cjs`, `studio-watch.cjs`, agent/pump instructions and related configuration. Their exact relative links and call-chain findings are in that plan. No live file/service/OBS state was changed.

Current gaps include text-only delivery, stripped nonverbal markers, per-line Piper model load, an age-based speech lock, a 60-second playback wait, latest-only studio state with no completion acknowledgment and hidden OBS failures. Longer replies require an authenticated persistent synth/queue, delivery controls after final wording, bounded paragraph subturns, ordered playback acknowledgments, backpressure, cancellation and explicit failure handling. **No overall logical-message length cap is desired.** The existing low-level 120-second turn cap remains; paragraph-streaming runtime integration is still planned, not implemented.

Planned runtime schema/config/worker/client/playback files in that plan do not yet exist. Avoid claim-by-documentation: implementing and observing that path remains in TODO. Do not wire an untrained student into the live voice.

### After the background candidate lands

- Measure actual WAV count/hours and QA completeness; inspect residual words, pronunciation, long paragraphs, adult identity, emotional contrast and actual laughs. Preserve all flags and prior exact hearing. The several-hour requirement applies to recordings, not scripts.
- Resolve unacceptable/out-of-bounds clips using new identities and explicit curation, with enough accepted varied clips to satisfy the owner target. A full accepted-corpus receipt must bind its actual final dataset; pilot approval alone is insufficient.
- Reprepare the final accepted dataset after curation, in the pinned Linux environment for the eventual run. Local candidate features are not uploaded by the delivery packet. Preserve their identity as local evidence.
- Separately validate the unexecuted own-student math/free synthesis/checkpoint recovery, and improve grouped independent coverage if necessary. Source inspection and successful dependency installation do not establish trained quality.
- Resolve registry publication authorization and exact immutable image reference, H100/driver compatibility, provider/storage evidence, credentials/stop/billing behavior, measured throughput and the actual priced work/budget/retention configuration. Current config fields stay null; no prices or cloud attestations were invented.
- Present the concrete final digest/data/environment/work/price to the owner **before any training or rental**. Any immutable input change requires a new reviewed manifest/receipt; the present running source recipe remains frozen until complete.
- Only after explicit authorization: train the own-weight acoustic/vocoder, hear independent text-only neutral/question/emotional/laughter/paragraph results, accept the exact pair, implement/validate runtime/playback coexistence and then separately deploy.

The setup handoff is complete; the background candidate, full-corpus acceptance, student training and deployment are not complete. No game launch/staging, live voice replacement, service/OBS change, external agent message, Git commit/push or registry publication occurred. Non-voice project work is outside this task; consult current project decisions and the preserved previous handoff rather than reconstituting it from this voice record.
