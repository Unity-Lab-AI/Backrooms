# Voice preparation review — 2026-10-11

## Current task and decisions

The owner's current request is to make the English speech voice sound like a natural adult female gamer/coder: friendly, comfortable to hear, emotionally responsive, with meaningful questions, emphasis, timing and rising/falling delivery, before paying for RunPod.

The owner chose **expressive pretrained tools locally as possible source audio for our own model**. This authorizes local audition tools; it does not approve a paid run or a runtime replacement.

The first three Qwen auditions were rejected: **"none of those they all sound like highpitch children not correcyl a 20 yr old"**. That is listening evidence. They remain preserved under `.local/voice-lab/auditions/2026-10-11-qwen-r1/`. The owner then selected **A2 low warm alto** from the low-register second round and approved all four reference-anchored variations: **"okay those all of A2 sound great lets build it our we are usering ur and all we need for human Unity"**. No real person's reference recordings are used.

The desired identity remains an original young adult American female voice. A dark/gamer aesthetic is expressed through relaxed confidence, warmth, understated humor and grounded vocal texture. It is not a reason to add constant whispering, forced fry, high squeals or theatrical anger.

### Latest acting decisions

The owner kept the A2 direction, then rejected the pilot's happy line, *"I'm in a good mood now"*, as monotone. Two focused remedies were also rejected: **"B2 sounded sarcastic D1 sounded like a anime cartoon character"**. Both remain evidence, not training examples.

The binding target is **"the original A2 but some type of emotional range  thats not forced and not just high pitch maxing"**, with the **"giorlfriend next door vibe that gigles and laughs and can joke and it sounds authentic"**. Preserve A2's ordinary identity. Express emotion through appropriate phrasing, rhythm, emphasis, warmth and natural motion; include actual performed nonverbal examples.

CosyVoice3 subsequently rendered instruction-conditioned speech using **only the exact original A2 raw speaker reference**. The owner accepted the heard natural-happy and little-chuckle samples and rejected its neutral sample: **"sounds great but dont use nutral one nutral one it terrible"**. Source files `2-natural-happy` and `4-little-chuckle` are preserved exactly under `training/voice/reference/`. `1-neutral` is excluded; `3-warm-pleased` was not heard/accepted and is not adopted. The original A2 remains the everyday baseline.

`SOURCE_DELIVERY_POLICY.json` records source routing, accepted evidence and forbidden examples. Whole-corpus labels, other emotional states and our own student remain unaccepted. Sample acceptance is not paid-training authorization.

## Findings that change the old plan

| Finding | Verified source/evidence | Consequence |
| --- | --- | --- |
| Today's stream still uses stock Piper | .claude/tools/unity-speak.py; unity-voice.py and the brain produce words only | A better language model does not replace the acoustic voice |
| Emotion was not learned | Original model.py had no style/emotion/intensity input; infer.py used mathematical pitch/energy/rate presets | More steps on the rejected recordings do not add absent performances |
| The chosen Kokoro audition's delivery was lost | breed.py uses phrase speeds, emphasis markup and pauses; make_dataset.py saves only plain text/global speed/vector | A voice vector does not preserve the audition's acting |
| Most duration is unsuitable knowledge narration | 2,872/5,206 clips,55.17% of clips and62.95% of7.6293hours;266 repeated company-plan phrases,177 review prefixes,148 Provisional entries | Replace with a dedicated speech corpus |
| Conversation coverage is thin | Only72 question clips/38 unique question texts; own-line filter excludes1–3word reactions | Include questions, backchannels and short spontaneous speech |
| Heldout text leaks | 46/88 heldout clips have the exact transcript at another speed in training | Group transcript families before variants; separate listening set |
| Loss is not audible quality | Heldout mel/GTA use target alignment/F0/energy rather than text-only predicted prosody | Report reconstruction separately from actual free synthesis |
| Reusing output can keep old audio | Legacy clip ID only hashes text/speed; feature/trainer glob retains stale files | Immutable dataset/feature/checkpoint identities and exact manifests |
| Final model identity is absent | training/models/voice/ absent; smoke artifacts are not a final trained pair | Prevent automatic deployment by file existence |
| Paid-run rails are incomplete | Cloud-stop result unchecked, cap watcher isolated, markers/checkpoints not tied to recipe, partly mutable dependencies | Keep training closed until these are corrected |

All5,206 old WAVs are present, mono24kHz PCM16. There were no saturated samples. Clipping was not established as the explanation. Median leading/trailing quiet was0.3235/0.51765seconds at a roughly−60dBFS threshold; preserve natural breaths when revising boundary timing.

The old hypotheses that extrapolation necessarily caused warbly formants, every synthetic clip has no prosody, or source data is an absolute mathematical ceiling are **not proven**. Existing vocabulary includes punctuation and lexical stress marks. The confirmed problems are rejected audible source, missing explicit conditioning, unsuitable/unbalanced examples and inadequate validation.

## Voice identity and delivery are separate choices

First select acceptable relaxed speech identity. Then keep that identity across:

- Friendly ordinary conversation and longer explanations.
- Acknowledgment, hesitation, thinking aloud and small corrections.
- Genuine yes/no, wh-, clarification and tag questions.
- Quiet reassurance, concern, disappointment and sadness.
- Restrained excitement, surprise, amusement and urgency.
- Word-level contrastive emphasis and intentional phrase pauses.

Emotion should affect rhythm, emphasis, voice quality and appropriate pitch motion together. It must not mean every excited line becomes a squeal or every sad line becomes artificially slow. Punctuation matters, but question type and context matter too; not every question has the same rising ending.

Keep delivery instructions out of spoken text. The speaking request should carry text, approved voice identity, emotion/intensity, speech act, pace and supported focus information separately. Untrained nonverbal laughter/sobbing must not be advertised as implemented.

## Small listening suite before building hours

Use held-out conversational material, not mod-register/manual sentences:

| Skill | Example / intended contrast |
| --- | --- |
| Ordinary peer chat | Hey, come hang out. I'm fixing this gate before we jump back in. |
| Statement versus checking question | You changed that setting. / You changed that setting? |
| Genuine question | Did you change that setting? |
| Wh-question | Where did you put the battery? |
| Short reactions | Yeah. / Wait, what? / Oh no. / Nice. / Mm-hm. |
| Contrastive focus | I wanted the blue door, not the red one. |
| Relief / excitement | There we go. It actually worked. |
| Sympathy | That was rough. Take a second; I'll stay here. |
| Concern | Are you okay? You went quiet. |
| Thinking/correction | I think it's the power cable... wait, check the switch first. |
| Dry amusement | Of course the door opens now. Very helpful. |
| Technical speech | Set the research priority to two, then check the battery charge. |
| Names/numbers | Gee, Scar, Unity, RimWorld, Async, GPU, sixteen gigabytes, twenty percent. |
| Longer turn | A calm30–45second explanation with natural phrase boundaries and no identity drift |

Speaker identity/naturalness and appropriateness are listening decisions. F0/RMS/ASR measurements can reveal specific faults; they cannot certify humanity or age.

## Local auditions and reproducibility

Tools:

- training/voice/audition.py
- training/voice/AUDITION_BRIEF.json — rejected round1
- training/voice/AUDITION_BRIEF_LOW_REGISTER.json — completed low-register second round
- training/voice/variations.py and A2_VARIATIONS.json — completed accepted four-variation audition
- training/voice/SELECTED_VOICE.json and REFERENCE_PROFILES.json — accepted identity/reference transcripts and hashes
- training/voice/reference/ — permanent exact raw and listening recordings
- .local/voice-lab/.venv-qwen/ — isolated environment; global speech packages unchanged
- .local/voice-lab/models/qwen3-tts-voicedesign/ — ignored downloaded teacher
- .local/voice-lab/auditions/ — ignored WAVs, receipts and acoustic review

Teacher snapshot: Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign at5ecdb67327fd37bb2e042aab12ff7391903235d3. qwen-tts0.1.1; transformers4.57.3; accelerate1.12.0; existing local torch2.7.1+cu118. The sample script uses local files only after download, one candidate at a time, bounded output and available-memory check.

Raw audio is retained. Listening copies have a modest broad RMS-level adjustment with a peak ceiling; no pitch shifting, time stretching or voice effects. Each receipt stores prompt/seed/versions/source revision/audio hashes/render duration/memory. This is **source-tool audition**, not our trained model or a runtime performance claim.

R1 estimated voiced F0 medians: A275.1Hz, B337.0Hz, C302.8Hz. WORLD estimates do not establish perceived age; low tails can contain creak/octave errors. The owner rejection remains the authority on this set. CPU ASR recovered A's intended wording; intelligibility does not prove emotional quality.

R2 A2 raw SHA256 is `df05af0bd6c0922a9946cab5e92bf692e079454f9a4de2d570e79f2c962267c8`; its unchanged listening version is `200b25d09866e3edb1916e2493c5e1a5021db36180a7c9ab8b707838fe219dfb`. The accepted reference is preserved, not recreated from a fresh description. Four subsequent performances used the pinned Base model at `fd4b254389122332181a7c3db7f27e918eec64e3`: everyday, playful, soft and questions. Their exact audio is now preserved under `training/voice/reference/`. The source-acceptance receipt records the actual owner quote; it does not accept unheard corpus rows or paid training.

## Implemented v2 source preparation

- **Authored speech corpus:** 1,341 unique normalized utterances, 872 neutral/warm, 378 genuine questions, 43 short turns; nine intended emotions and seven speech acts. Draft split is 1,318 train / 23 heldout. Corpus SHA256 is `4590b9382eb6c8eba6bbd75ef9b0d4ae1a35c5d231a4a306fb50fbab2d47cef9`. Audio performance acceptance remains pending. Similar paraphrase/template families can still overlap; exact grouping is not proof of broad unseen-text performance.
- **Learned conditioning path:** emotion, speech act, intensity and pace enter preprocessing, the model/prosody predictors, training and inference. Voiced/unvoiced state is represented separately. Unsupported combinations/ranges are refused; enum membership is not learning evidence.
- **Identity/recovery:** exact labeled WAV metadata, grouped lexical-text splits, train-only normalization, frontend/features/checkpoint pair identities, SHA-bound inventories, compatible working/shipping checkpoints, immutable exports and bounded inference. Legacy CSV data and smoke checkpoints are refused without deleting them.
- **Honest evaluation:** oracle reconstruction/GTA and text-only predicted heldout mels are separate outputs. Actual free-running student listening, performance and failure/resume acceptance remain open.
- **Exact GTA pairing:** vocoder resume/final checkpoints bind the exact oracle mel manifest and full acoustic checkpoint SHA, not only a shared feature pair. Thin shipping retains original working-checkpoint provenance; inference rejects another acoustic checkpoint's GTA vocoder.
- **First actual local source/prep batch:** 24 clips / 34.32 seconds rendered in 111.797 seconds after model/prompt setup; 23 train / 1 heldout, 48 phoneme symbols. Dataset ID `10e4430c0a18b10ac4d41e739c9b8258f08a490d18a8819a7c42af00e85698c2`; feature ID `3fd477932d3b04697ba6a41eb3044c6c03c0d4ba6f2a8bcbc10a8ec7c07f2dcf`. Both generation and actual preprocessing completed. This pilot is front-loaded: 16 neutral, only one of each other state, half short turns; it establishes source/prep mechanics only. Its builder/selection/receipt were frozen under `evidence/voice-prespend-2026-10-11/pilot1-*` before recipe improvements.

Qwen Base does not expose VoiceDesign's general emotion-instruction API; passing a raw `instruct` string into cloning does not control delivery. Reference performance and contextual wording proved insufficient for the rejected happy line. The accepted CosyVoice3 happy/chuckle route uses a real instruction-plus-reference path. Every newly rendered intended label still must match audible delivery before it becomes accepted supervision; a quiet reference may not give appropriate frustration/concern.

## Original-A2 acting source and nonverbal foundation

CosyVoice3 model `FunAudioLLM/Fun-CosyVoice3-0.5B-2512` was pinned to `29e01c4e8d000f4bcd70751be16fa94bf3d85a18`; source code to `074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc` with the recorded Matcha submodule. Required model files total about 5.42 GB; alternate RL/export weights were excluded. All files remain ignored local source tools, with the original A2 as reference. The [official interface](https://github.com/QwenAudio/CosyVoice/blob/main/cosyvoice/cli/cosyvoice.py) and [supported event tokens](https://github.com/QwenAudio/CosyVoice/blob/main/cosyvoice/tokenizer/tokenizer.py) were inspected. The English target text used separately supplied delivery instructions; their actual suitability was established only for the heard accepted samples.

An isolated `.local/voice-lab/.venv-cosy/` preserves global Torch/Torchaudio 2.7.1+cu118. Source inference succeeded with Transformers 4.51.3, NumPy 1.26.4 and Windows CPU ONNXRuntime 1.18.0. CAMPPlus/tokenizer providers were read back as CPU; Torch synthesis uses CUDA. This is a custom observed source-audition setup, not the publisher's pinned Torch 2.3.1 environment or our final runtime benchmark. Caches are inside the writable ignored model folder. No global/live speech package was uninstalled.

`speech_text.py` now gives `[laughter]` and `[breath]` dedicated tokens, preserving ordinary phonemes/stress and removing event markers from lexical split groups. Preprocessing records exact event counts; checkpoint metadata hashes actual TRAIN event/combined delivery support. Inference refuses heldout-only/unseen-delivery events. Old pre-event feature/checkpoint identities intentionally fail; original WAVs stay unchanged, and the prior frontend was frozen in `evidence/voice-prespend-2026-10-11/pre-event-frontend/`.

This is event plumbing, not trained laughter. Source examples and listening remain mandatory; actual giggle/belly-laugh subtypes are not implemented. The existing 256-frame limit gives about 2.73 seconds per event token. Wider intensity/pace ranges, word-focused emphasis, explicit pause controls, sobs and long-turn runtime chunking remain unfinished. Breath examples have not been accepted merely because their token exists.

`curate_dataset.py` exports entirely pending per-clip review forms, then can publish a new immutable accepted/relabelled subset only from explicit named listening attestations. It preserves draft/rejected WAVs and copies accepted bytes unchanged, binds corrected labels/provenance to the literal review hash, and cannot approve the global corpus or training. Windows review publication uses non-replacing rename; a failed earlier hard-link temporary is preserved. The balanced pilot's actual pending form exists beside its immutable source directory.

## Paid-run source rails and remaining proof

### Completed mixed source checkpoint

`make_dataset.py` and `source_workers.py` now orchestrate separate reviewed Qwen/Cosy environments sequentially, with original-reference policy enforcement, exact immutable recipe/model/code/environment provenance and bounded owned-child cleanup. A metadata probe initially failed because the orchestrator hid user-site Torch that both reviewed environments deliberately inherit. Preserving that visibility, UTF-8 child output, active-precedence distribution reporting and bounded diagnostics corrected the actual failure. Both metadata probes then exited 0, followed by successful source rendering; no global package or live service was changed.

The actual mixed pilot produced **32 recordings / 84.16 seconds** in 274.969 seconds after recipe/environment hashing, with 17 Qwen and 15 Cosy jobs. All nine intended emotional states and seven speech acts are represented. The rejected Cosy neutral recording and instruction are excluded. Newly performed words, identity and acting are still draft until listening review; the accepted sample decisions do not approve these new recordings automatically.

Source directory: `.local/voice-lab/auditions/2026-10-11-A2-mixed-32-v3/`. Dataset ID `b780c669e80c6b6986f80063e601715106f297cbd1769209d653e079a4fbd3bd`. Recipe ID `17b5bc8c20cc797d4cdff9f131bf118ae8adcd1df65f4f6ae4ff19fa997308a7`.

Actual preprocessing completed into the sibling `2026-10-11-A2-mixed-32-v3-features/`: **49 symbols, 31 train / 1 heldout**, feature ID `82395b5965bc3d0c7efb1ad4e49eb9443efbe8cafe31a51631cbd3680da98360`. `<event:laughter>` is a single vocabulary token; two TRAIN requests and one heldout request are present. No breath support exists. Counts prove marker/token preparation, not audible nonverbal performance or learned laughter. The entirely pending 32-row form is `2026-10-11-A2-mixed-32-v3-review.json`; curation acceptance has not run.

Machine-readable identities, waveform hashes, runtime provider readbacks, active source environment provenance and explicit limitations are in [preparation-evidence.json](evidence/voice-prespend-2026-10-11/preparation-evidence.json). The regenerated manifest covers 43 inputs including the new workers, policy, event text/builder and all 14 accepted reference/listening WAVs. Regeneration/readback matched digest `7abfe3cddaaaecd3106248a661bc57b2d2dd50162c69f5acf5ee292d73a4a224`. It is the current preparation source identity; it does not approve an eventual paid run. Full corpus review, own-model execution/learning and deployment remain open.

Both pod entry points refuse a closed gate. The runner also requires an explicit dataset/digest, supervisor deadline, stop tooling and volume attestation. Bootstrap has a single supervisor lock, a persistent budget/rate/deadline that cannot silently reset on resume, fixed GNU `timeout` supervision, independently bounded trainer process groups, sibling-failure cleanup and five bounded stop attempts. At least three minutes of budget time is reserved for stopping. A successful CLI request is recorded as `request_acknowledged`, never proof billing ended; exhausted retries leave `STOP_UNCONFIRMED.txt`.

Required volume receipt fields are `schema=unity-voice-volume-receipt-v1`, `decision=accepted`, `scope=durable-volume-preflight`, `volume_id`, `mount_path=/workspace`, `verified_by`, `recorded_at`, `provider_volume_evidence` and `mount_evidence`. Its path/hash and provider ID must match the run. No such receipt was created here. A flag/receipt alone is not observation of provider storage.

First-party Python and embedded shell-Python syntax was parsed statically. Both Git Bash `-n` parses completed with exit 0 after an automatically reviewed read-only sandbox escalation; no shell commands ran. These are source syntax checks. Stop credentials/provider state, actual durability, concurrent interruption/RNG-exact resume, container/dependency pinning, complete accepted data and recoverable public artifact publication remain unverified. Existing partial download sets are refused, not transactionally repaired.

The source digest excludes mutable gate flags and final priced/deployment receipts, avoiding a self-referential approval hash. Gate **code**, source/preparation receipts and actual immutable inputs remain hashed. The later priced owner receipt must bind the final source digest, accepted dataset ID, exact price/budget and approved work/volume/retention configuration; changing a flag cannot approve another recipe.

## Later accepted listening and preparation integration

The earlier mixed-pilot checkpoint above preserves its status **at creation**.
It is superseded for listening by the owner's later actual decision:

> they are all good just go ahead and finish up soi you in reguards of being ready for the pod run but no start yet and no pod rental yet

Markdown audio delivery first failed visibly. Native audio then delivered the
three sets covering all 32. `receipts/pilot32-owner-listening.json` records the
actual heard WAV hashes/text/controls; `pilot32-corpus-acceptance.json` binds only
the new curated dataset. `.local/voice-lab/dataset/A2-reviewed-32-v3/` contains
unchanged raw WAVs, dataset ID
`06e9c2b2043e523b684eb7ce32a171dff91ce64af180f2f4a20faeefc710f9e7`.
Current features after the student-source fixes are
`.local/voice-lab/feats/A2-reviewed-32-v4-ready/`, feature ID
`0401fbbfab96717480da47d51d2434a5214a4715f527380f506acdedc8ef5139`.
Older feature IDs and the 43-input digest above are historical, not launch inputs.

[Architecture readiness](evidence/voice-prespend-2026-10-11/architecture-readiness.md)
records the bounded source fixes: reduced aligner intermediate allocation,
predictor padding masks, strict feature arrays, shared student-code/checkpoint
identities, saved random states and acoustic batch cursor, finite-state guards,
and bounded turn planning. Literal unique-phrase pauses and long-turn chunks are
implemented; explicit word focus is refused without performed supervision.
No own-student import, model computation, training or functional recovery test
was performed in that review. Source inspection is not evidence of learned voice.

Full 1,378-row local source rendering is underway at
`.local/voice-lab/dataset/A2-full-1378-draft-v3/`. CPU-only screening uses existing
cached ASR and never alters the source recordings or labels. The explicit partial
summary captured **449 rendered / 446 screened / 1,378 expected**; it is not a
full result. `SOURCE_QA_POLICY.md` and `summarize_source_screen.py` preserve every
original flag and recognize narrow segmentation/number equivalences. Exact prior
hearing transfers only when WAV bytes, text, identity and controls all match.
Every laughter entry remains individually named for event audibility review.

An actual optional second CPU recognizer screened nine residual transcript
disagreements in that partial snapshot: eight matched intended words; both
recognizers read "near" for intended "nearer" in the remaining question. This
is fallible transcript evidence, not automatic acceptance or proof of wrong
speech. Source/outlier/event review and final full-corpus acceptance remain
separate from approval of the 32 heard recordings.

The owner separately approved **"Yes — local Docker build only"**.
[Docker preparation](evidence/voice-prespend-2026-10-11/docker-local-preparation.md)
records the observed endpoint recovery and first preserved build failure. The
corrected v2 environment resolves dependencies from selected wheel/source
metadata, including missing `wrapt`; its actual build exited 0 and the installed
dependency check passed. All 103 pins match installed distributions, 887 runtime
files and 188 OS packages are inventoried. The image and its 3,429,147,136-byte
archive are saved in the v2 artifacts folder; the permanent observation is
`training/voice/receipts/local-environment-build.json`. Registry publication is
separate. Local image IDs must never be called registry-pullable digests.
No pod or student training is authorized; live Piper, game files and services
remain unchanged.

## Later 5,000-source expansion and immediate handoff, 2026-10-12

The owner selected at least 5,000 varied recordings/several actual speech hours,
limited longest training replies to 3–5 medium sentences, and retained longer
open-ended live replies. The owner then requested handing back to the lead without
waiting for audio, with local preparation continuing in the background.

Actual new artifacts: `build_expanded_corpus.py`, `SPEECH_CORPUS_EXPANDED.jsonl`,
`SPEECH_EVENT_CORPUS_EXPANDED.jsonl`, `EXPANDED_CORPUS_PLAN.md` contain exactly
5,000 text jobs, preserving all 1,378 original objects and adding 3,622 distinct
lexical groups. There are 560 paragraphs, currently 3–4 sentences / 39–57 words.
95,437 words imply 8.37–11.36 hours only at assumed 140–190 words/minute; actual
audio duration/quality remain unobserved. 65 percent of rows are neutral/warm.

New expansion-only tools are `make_dataset_optimized.py` and
`source_workers_optimized.py`, with fixed Qwen groups/EOS/timing evidence and
exact Cosy instruction/reference cache keys. Their plan-only production inventory
actually reported 3,622 new jobs / 1,378 skipped without loading models. Batch 2
has not been benchmarked or executed yet. Merge helpers preserve original WAVs,
separate source identities and all complete parent QA; no merged renderer fiction
or listening acceptance is created. The live integration plan documents bounded
paragraph subturns inside an open-ended logical message; that broker is unbuilt.

`run_expanded_preparation.py` is the actual no-training local supervisor. Hidden
host launch at 06:05:52 UTC produced PID 12020 and live status under
`.local/voice-lab/background/A2-expanded-2026-10-12-v2/`. It waits for the existing
seed/ASR, then generates additions and completes QA/merge/pending review/local
features/delivery. A first sandbox launch did not persist and is preserved as v1;
no pipeline stage began there. The active v2 status is the continuation entry.

At 06:07:20 UTC: seed 945/1,378 rendered, 944 screened, 0.6272 actual source hours.
The final checked manifest has 89 inputs, digest
`7138ec0643a19b3db60ffa1dc5bd4d2739b93e5ca25a439b7f3490f4dedf7e00`.
41 first-party Python files parsed; driver/source/merge interfaces were reviewed.
No student import/math/training, functional recovery test, pod, upload, live apply
or registry publication occurred. This is a setup handoff, not full-corpus or
student acceptance. Read [NOW.md](../NOW.md) and
[background-handoff.json](evidence/voice-prespend-2026-10-11/background-handoff.json)
for every input, exact launch, logs, scope and remaining work. Do not alter frozen
voice inputs or start competing jobs during continuation.

## Before RunPod

The launch gate is closed by default:

- training/voice/quality_gate.py
- training/voice/VOICE_QUALITY_GATE.json
- both training/voice/pod scripts check it before work
- manifest.py hashes gate code, source/engineering receipts, bootstrap and itself; mutable gate JSON and final priced/deployment approvals are excluded and checked separately

This prevents the old rejected recipe from proceeding under a stale Ready claim. It does **not** fix cloud billing, replace missing source performances, or turn flags into a quality result. Creating a pod can already incur cost; leave it uncreated while closed.

Required actual work:

1. Select and approve acceptable identity/source auditions.
2. Verify same identity across separate neutral/question/emotional lines; preserve original reference identity.
3. Build a dedicated, labeled, audible expressive corpus. Labels must describe real performances.
4. Carry conditioning through preprocessing, model training and inference; reject unlabeled legacy data.
5. Fix grouped splitting, exact data membership, frontend/architecture/artifact compatibility and bounded synthesis.
6. Define free-inference listening checks distinct from oracle reconstruction.
7. Correct run-resume identity, immutable inputs, validated volume, worker/cloud-stop failure handling and finite budget settings.
8. After these are concrete, obtain approval of actual recipe/digest/price before any training.
9. Deploy only an accepted acoustic/vocoder/frontend pair after local coexistence and playback observations.

No training, pod creation, live voice replacement, game staging or publication was performed in this preparation wave. Source auditions and static analysis do not close training/deployment acceptance.

## Primary sources checked

[Qwen official repository](https://github.com/QwenLM/Qwen3-TTS) documents description-driven VoiceDesign and separate reusable-reference workflow. It is an audition candidate, not a guarantee of acceptable output or matching instruction control on every model variant.

[Qwen VoiceDesign model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign) identifies the selected model; the exact snapshot above is recorded locally.

[FastSpeech2 paper](https://arxiv.org/abs/2006.04558) supplies context for duration/pitch/energy modeling. Emotional acting must still be supported by the chosen data and our actual conditioning path.

