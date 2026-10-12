# A2 voice data readiness review

**Date:** 2026-10-11. **Scope:** source/metadata inspection and local ASR inventory. This review started no model, ASR, training, pod, service or audio playback. It does not certify unheard audio. The author wrote this evidence note and the separately requested reserved evaluation text/plan; frozen corpora, policy, generators and references were not changed.

## 1. Binding acceptance boundary

The owner's latest words are:

> they are all good just go ahead and finish up soi you in reguards of being ready for the pod run but no start yet and no pod rental yet

This approves the **32 recordings actually heard in the three listening sets**, including their three requested chuckles. It is preparation authorization, not approval of every future recording or permission to train/rent. The saved `training/voice/receipts/pilot32-owner-listening.json` and `pilot32-corpus-acceptance.json` record this scope. At inspection, `VOICE_QUALITY_GATE.json` still has `training_allowed=false`, and its full-corpus check explicitly distinguishes the accepted pilot from the future full collection.

Keep three states separate:

1. **Heard and accepted:** the approved A2 references and the exact 32 pilot WAVs linked by receipt/hash.
2. **Technically prepared:** complete, immutable full-source inventory and measured automated-QA/feature results. These can be finished without making someone listen to 1,378 clips.
3. **Full collection approved for later training:** an explicit decision covering the resulting dataset identity and its honestly stated QA/sampling method. This is not implied by pilot approval; launch/rental permission remains separately withheld.

The current [curator](../../../../training/voice/curate_dataset.py) requires `listened=true` for **every** reviewed clip. An ASR pass or a sampled audit must never be converted into false per-clip listening acknowledgments. If a future full-data acceptance policy allows automated checks plus targeted listening, record that as a separate, explicit policy/receipt with the actual heard subset. Do not silently reuse the per-clip-human schema for unheard rows. Until that policy is accepted, full data can be ready as a technically checked draft while its global quality gate remains closed.

## 2. Exact frozen text inventory

| Artifact | Rows | SHA256 |
| --- | ---: | --- |
| [SPEECH_CORPUS.jsonl](../../../../training/voice/SPEECH_CORPUS.jsonl) | 1,341 | `4590b9382eb6c8eba6bbd75ef9b0d4ae1a35c5d231a4a306fb50fbab2d47cef9` |
| [SPEECH_EVENT_CORPUS.jsonl](../../../../training/voice/SPEECH_EVENT_CORPUS.jsonl) | 37 | `c4f55f7d5592e183a2b240bc36f78f56464303cf4146325dedd331c2b3399beb` |

The combined plan has **1,378 unique IDs and 1,377 normalized lexical groups**. Every row has the same six text-authoring fields. There are 37 single `[laughter]` requests and no breath requests. All pace values are 1.0; neutral intensity is 0.0 and the other intended states use 0.35.

The only repeated lexical group is `what made our little project so nice`: one ordinary happy question and its laughter-prefixed variant. Both remain **held out** under the current marker-aware normalized split. This is intentional, not leakage.

| Intended state | Combined rows |
| --- | ---: |
| neutral | 522 |
| warm | 358 |
| happy | 76 |
| amused | 87 |
| excited | 67 |
| sad | 67 |
| concerned | 67 |
| frustrated | 67 |
| surprised | 67 |

Neutral/warm comprise 880 rows, **63.9%**, preserving ordinary friendly speech as the default. The 386 question turns have consistent question punctuation/intent labels in this text inspection. Other acts: 331 statements, 179 instructions, 192 reassurances, 168 asides and 122 exclamations.

There are **43 turns of three words or fewer**. Word counts are 1–16, median 8, with 10,601 words in total. There are no long training turns and no literal digit characters; dates/numbers in this bank are written as words. This avoids the old minimum-word filter but does not establish long-turn performance or production digit pronunciation. Actual hours must be measured from the completed recordings, not inferred from row count or borrowed from the rejected 7.6-hour dataset.

## 3. Heldout breadth and regression containment

The combined plan has 1,354 train rows and 24 heldout rows, representing **23 heldout lexical groups**. All 63 emotion/act combinations have planned TRAIN text; only 16 combinations have heldout text.

Heldout state counts: neutral 10, warm 7, happy 3, excited 1, sad 1 and frustrated 2. **Amused, concerned and surprised have zero heldout rows.** The sole heldout laughter example is happy and shares its group with the ordinary question. Therefore:

- A good heldout loss cannot establish generalization for all nine states or laughter across all contexts.
- Retain the existing hashes/split while rendering. Do not move variants between partitions to improve a score.
- Use the new reserved listening suite for broader later student evaluation; keep it out of all source/training/normalization inputs.
- Near paraphrases and small authored-template families can still share wording across partitions. The current exact normalized split fixes exact lexical leakage, not every form of family overlap.

The preserved rejected legacy CSV still has 5,206 rows, 88 old heldout clips and **46 heldout clips whose exact transcript is in training** at another speed. That old name-hash split must not return. Legacy CSV, prepared leftovers and old smoke checkpoints are historical evidence, not v2 inputs. The current [dataset contract](../../../../training/voice/dataset_contract.py) and fresh feature manifests provide the new boundary.

## 4. Recipe and label risks

The inspected 32-clip recipe at `.local/voice-lab/auditions/2026-10-11-A2-mixed-32-v3/render-recipe.json` has recipe ID `17b5bc8c20cc797d4cdff9f131bf118ae8adcd1df65f4f6ae4ff19fa997308a7`, source ID `8abb75d3e26e8036311731861e5333f1cdaf0fe5f4044385716e4cfe56473798` and file SHA256 `5447776787d38814253b6d0e61e7b41e6d27df3f95e873800cd2f0aa27b66e30`. It records 8 Qwen original, 9 Qwen soft, 10 Cosy natural-happy and 5 Cosy relaxed-smile jobs. Its original `audio_acceptance=pending` is historical render state; the later listening receipt is the approval evidence. Do not rewrite the frozen recipe to disguise that sequence.

[SOURCE_DELIVERY_POLICY.json](../../../../training/voice/SOURCE_DELIVERY_POLICY.json) keeps the original A2 identity, prohibits Cosy neutral and records rejected alternatives. Neutral/warm use Qwen original; sad/concerned/frustrated use Qwen soft; positive states use Cosy, while event rows explicitly use the relaxed-smile route. This is a deliberate mixed-source recipe, not deployment of either source engine.

The policy is still an intended-performance route, not a calibrated emotional-control API. Important full-data review targets:

- **Teacher/state confounding:** provider differences are correlated with emotion families. Check identity and timbre across Qwen/Cosy transitions rather than accepting one `voice_id` string as proof.
- **Shared soft reference:** sadness, concern and frustration can collapse into the same subdued tone. Look for alert caution and mild firmness separately from disappointment.
- **Happy route reused for excitement/surprise:** these can become the same pleasant tone or drift upward. Check their intended distinction without demanding theatrical extremes.
- **Warm chuckles:** laughter-marked warm turns deliberately override the ordinary warm Qwen route. Their identity must stay consistent.
- **Ambiguous wording:** sentences such as “A different result isn't automatically a bad one” can naturally sound like calm reassurance. Audio, not the prose label, determines whether it is actually surprised. “I may already have three ideas” can be neutral/amused instead of excited.
- **No actual chuckle in ordinary wording:** “At least we can laugh about it” has no event marker. Do not count that as event supervision merely because it mentions laughter.
- **Modest controls only:** fixed 0.35/1.0 coverage does not calibrate wider intensity, pace interpolation, breath, whisper, sobbing or named laugh types. Unsupported word-focus requests remain unsupported.

## 5. Existing offline ASR inventory

No new model is needed to inspect ordinary English word fidelity. The following files were inventoried and hashed; neither recognizer was loaded in this review.

| Cached recognizer | Exact snapshot directory | model.bin bytes | model.bin SHA256 |
| --- | --- | ---: | --- |
| faster-whisper base | `C:/Users/gfour/.cache/huggingface/hub/models--Systran--faster-whisper-base/snapshots/ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66` | 145,217,532 | `d01c3014881c9c6f3133c182f3d2887eb6ca1c789a7538c5c007196857a0a6a9` |
| faster-whisper small | `C:/Users/gfour/.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120` | 483,546,902 | `3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671` |

Both snapshots also contain `config.json`, `tokenizer.json` and `vocabulary.txt`. The user site contains `faster_whisper` **1.2.1** and `ctranslate2` **4.8.1** under `C:/Users/gfour/AppData/Roaming/Python/Python310/site-packages`. The Qwen environment's `pyvenv.cfg` enables system-site packages and uses `C:/Program Files/Python310`; the Cosy environment also has its own `whisper` package. The inspected default `.cache/whisper` had no model files. Cosy's speech tokenizer/Whisper feature components are not automatically a standalone transcript QA service.

The installed `faster_whisper/transcribe.py` exposes `WhisperModel(..., compute_type=..., local_files_only=...)`. A subsequent authorized QA tool should select the exact cached directory, English, CPU/int8 and offline behavior explicitly; avoid a mutable model nickname that can trigger a download. `.local/voice-lab/auditions/2026-10-11-qwen-r2-low/asr-review.json` records earlier faster-whisper-base CPU/int8 transcripts; those are pronunciation evidence only, not emotional approval. No reusable first-party full-corpus ASR QA tool was found in the targeted first-party voice-lab/training/tool search at inspection.

## 6. Efficient automated QA for every full-source row

These are proposed preparation checks, **not results of this review**. Run them through a separate QA tool/report after the frozen renderer has produced its complete inventory. Do not edit frozen helpers/policy/recipes halfway through generation.

### Inventory and basic signal checks

- Bind the report to full recipe/source/dataset IDs, every exact clip ID and WAV SHA256, frontend version, QA tool hash and recognizer snapshot/package identities.
- Reconcile exactly 1,378 requested jobs against metadata and WAVs. Explain every omitted/rejected job; do not quietly reduce the training set or call a partially rendered batch complete.
- Check each stored WAV's actual mono 24 kHz format, finite samples, bounds, nonzero signal, endpoint quiet and saturation. Current preparation accepts 0.25–30 seconds and rejects excessive clipping/silence; add distributions and outlier flags rather than only a binary pass.
- Save total original samples/hours, duration quantiles, RMS/peak/clipping distributions, leading/trailing quiet, provider/state buckets and individual outlier IDs. Use original audio samples for duration; preparation may add less than one hop of zero padding.
- Detect byte-identical outputs under differing transcripts and likely repeated/missing speech. Resume must preserve orphan WAVs/torn metadata for explicit recovery, never silently overwrite them.

### Transcript and pronunciation triage

- Transcribe all clips with one cached CPU/int8 recognizer. Store raw transcript and comparison normalization separately, with elapsed time and exact source hashes. ASR is triage, not proof of human delivery.
- Remove event markers only from expected lexical text. Preserve the difference between missing words, extra words, a spoken marker name, name errors and number errors.
- Normalize ordinary punctuation/case and legitimate numeric equivalents without making “fifteen” and “fifty” equivalent. The planned bank uses number words; ASR may output digits. Keep both forms in the record.
- For short acknowledgments, use exact lexical comparisons and inspect uncertainty; percentage error on a one-word turn is inherently coarse. Do not let a VAD minimum duration discard “Yeah” or “Yep.”
- Run the cached small recognizer only on base-model disagreements/outliers if useful. Two recognizers agreeing is stronger transcription evidence, not independent confirmation of emotion or chuckles.
- Check Mira/Kade/Tobin/Jess/Rook and other names, C sharp, Python, RimWorld/Rimrooms, dates, percentages and easily confused quantities. The reserved evaluation adds actual digits/time notation absent from the training text.

### Voice/event triage

- Compare pitch, loudness, boundary timing and available speaker descriptors with the corresponding approved A2 examples, stratified by source/state. Use outliers as listening targets, not a hard “adult woman equals N Hz” rule. Pitch estimation can have octave errors and cannot certify perceived age.
- A transcript pass cannot confirm genuine laughter. Preserve a per-event pending flag until audible event evidence is reviewed. Check exact marker position, short chuckle duration, transition back to words, and absence of a spoken “laughter.” No currently inventoried independent event detector was established as available, and no detector should be fabricated from a marker count.
- Strongly prioritize the **37 event rows** and every disagreement/outlier for listening. This is a small subset rather than a demand to listen to the full collection. Previously heard clips can retain their actual acceptance only when the exact audio/hash and intended controls match; newly synthesized audio does not inherit listening by sharing text or seed.

## 7. Feature and energy/alignment failure cases

Read [prep.py](../../../../training/voice/prep.py), [feature_arrays.py](../../../../training/voice/feature_arrays.py), [model.py](../../../../training/voice/model.py) and both trainers together. Current source uses an explicit 384-sample pad, hop 256, 80 mel bins and one exact waveform hop per frame; pitch has a separate voiced mask. Training-only pitch/energy normalization avoids the old heldout-statistic leak.

Full preparation must account for each manifest entry and save the feature/vocab/stats identities. Important failure cases are unknown/name phonemes, overlong tokens/frames, mel/waveform mismatch, nonfinite values, all-unvoiced/near-constant training pitch, degenerate energy variance, prolonged endpoint silence and missing actual events.

The mean linear-mel energy is a spectral feature, not calibrated loudness. More energy or a wider F0 range is not by itself “happy” or “human.” Pitch estimates during chuckles/creaky phonation can be irregular; silent/unvoiced frames must not become fake voiced pitch observations.

Laughter is one dedicated event token. Training alignment must eventually assign its genuine duration rather than borrowing neighboring words or silence. The source model bounds each predicted token to 256 frames and an utterance to 3,000 frames; an unexpectedly long source laugh or long leading silence can conflict with inference limits even when the complete clip is under 30 seconds. Do not promise alignment correctness from marker counts or untrained source inspection. Later authorized training must show finite losses, useful alignment, and separate free-running synthesis; oracle/GTA reconstruction alone is not that evidence.

The latest trainer source was fully read: shape/finite guards, source-bound checkpoints, saved RNG/data-order state and exact GTA acoustic/export provenance now exist. No additional concrete P0 signature/mel-hop/checkpoint fault was found in this source-only pass. These guards were not executed here. A future small-pilot vocoder run needs an explicit batch no larger than its TRAIN rows; default batch 32 can exceed a 32-clip pilot after heldout removal. The full planned train population is large enough for that default.

## 8. A manageable acceptance and prelaunch packet

Finish data preparation with these artifacts:

1. Full immutable render recipe, complete metadata/WAV inventory and actual measured hours.
2. Per-clip automated QA report, all disagreements/outlier IDs, dispositions and retained/rejected counts.
3. A targeted listening packet: approved original A2 anchor, remaining event examples/outliers and a small stratified random audit of provider/state/act/length buckets. Keep sample selection reproducible and identify every heard hash.
4. A receipt that accurately names **what was heard** and **what was technically checked**. Do not mark all 1,378 as human-listened or copy the 32-pilot acceptance into another dataset identity.
5. Frozen prepared feature manifest, train-only normalization, actual TRAIN delivery/event support and source/input identities. Wider controls remain disabled if the data does not establish them.
6. Reserved [LISTENING_EVAL_TEXT.jsonl](../../../../training/voice/LISTENING_EVAL_TEXT.jsonl) and [EVALUATION_PLAN.md](../../../../training/voice/EVALUATION_PLAN.md): 38 cases, 36 evaluation-only lexical groups, zero overlap with the planned training collection. They cover all nine states/seven acts, questions/statement contrasts, short turns, names/digits, laughter and a 174-word long-turn case. Keep them out of training/normalization.
7. An immutable launch-input manifest and the runtime/budget/resume plan owned by the other reviewers. A technically ready packet still does not create a pod or flip the owner's launch/rental permission.

The useful next approval concerns a **concrete full dataset identity and documented QA/sampling policy**, with exceptions made reviewable. It need not demand 1,378 manual playbacks. However, an automated or sampled policy must be named honestly rather than represented as exhaustive human listening. Student final-voice acceptance and live playback/device acceptance occur after training and remain separate.

## 9. Checks actually performed

This author read current source contracts, corpora, routing policy, 32-clip recipe, gate and pilot receipts; parsed JSON/text metadata; recalculated text hashes, lexical groups/splits and coverage statistics; inspected cached recognizer/package inventories; and hashed existing ASR model files without loading them. The rejected legacy leakage count was recalculated from its preserved CSV. No ASR, feature preparation, acoustic/vocoder/model training, model inference, audio playback, cloud action or implementation test was performed in this review.
