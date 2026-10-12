# NOW — Unity voice handoff

## Current record, 2026-10-11

**Original A2 low warm alto is the fixed voice.** The owner wants a warm, familiar adult American girl-next-door voice, natural emotional range, jokes and genuine little laughs. Keep the low register comfortable; do not substitute sarcasm, anime acting, squeals or arbitrary pitch effects.

Latest directions, verbatim:

- "the original A2 but some type of emotional range  thats not forced and not just high pitch maxing"
- "come on we want a giorlfriend next door vibe that gigles and laughs and can joke and it sounds authentic"
- After hearing original-reference happy/chuckle samples: "sounds great but dont use nutral one nutral one it terrible"

**No A2 student training or RunPod work has started.** Live speech is still Piper. Source-audio inference and preprocessing are preparation, not our trained voice. The standing order "let me know before u start a training" remains binding; no actual new run/price is approved.

**Latest owner instruction, verbatim:** "they are all good just go ahead and finish up soi you in reguards of being ready for the pod run but no start yet and no pod rental yet". This accepts the delivered A/B/C sets, all 32 source recordings, and authorizes completing preparation. Training and pod rental are explicitly prohibited. Do not treat this as a priced launch decision.

## Keep and reject

| Recording | Decision / use |
| --- | --- |
| Original A2 | Accepted; permanent identity/everyday baseline |
| Initial A2 everyday/playful/soft/questions auditions | Accepted recordings; do not assume every later sentence has their acting |
| Cosy `2-natural-happy` | Accepted source performance, exact original A2 speaker reference |
| Cosy `4-little-chuckle` | Accepted source performance, actual laughter token |
| Mixed pilot, all 32 A/B/C recordings | Accepted after native audio delivery; exact heard WAVs/labels preserved in `receipts/pilot32-owner-listening.json` |
| Cosy `1-neutral` | Rejected; never use it for the everyday voice or training |
| Cosy `3-warm-pleased` | Unheard/unaccepted; not adopted |
| Qwen draft "I'm in a good mood now" | Rejected as monotone happy delivery |
| Qwen retry B2 / VoiceDesign D1 | Rejected as sarcastic / anime-cartoon respectively |

Original and accepted source/listening bytes are in `training/voice/reference/`; decisions/transcripts/hashes are in `SELECTED_VOICE.json`, `REFERENCE_PROFILES.json`, `SOURCE_DELIVERY_POLICY.json` and `receipts/source-auditions.json`. Preserve these; do not recreate A2 from a fresh description. The mutable quality gate keeps training/deployment disabled.

## Files to read and actual implementation

1. [Voice preparation review](implementation/VOICE_PRESPEND_REVIEW_2026-10-11.md) — inspected old failures, source facts, decisions, current evidence and limits.
2. [Active voice plan](../training/voice/VOICE_PLAN.md) — its lower Kokoro sections are explicitly historical, not launch instructions.
3. [Speech corpus plan](../training/voice/CORPUS_PLAN.md) — 1,341 conversational drafts, 65% neutral/warm, 378 questions, 43 short turns.
4. [Event corpus plan](../training/voice/EVENT_CORPUS_PLAN.md) — 37 planned chuckle turns, no breath examples; one lexical duplicate intentionally stays in the same split.
5. `training/voice/dataset_contract.py`, `speech_text.py`, `prep.py`, `model.py`, trainers and `infer.py` — labeled immutable data/features, learned delivery/voicing, compatible checkpoint pairs, actual TRAIN support and bounded synthesis.
6. `training/voice/make_dataset.py`, `source_workers.py` and `SOURCE_DELIVERY_POLICY.json` — sequential isolated source generators; every newly rendered label still requires performance QA. Current source expansion uses original A2 for everyday speech and approved instruction-conditioned happy/laughter sources.
7. `curate_dataset.py` — create a pending listening form; publish a NEW immutable reviewed subset without altering draft/rejected audio or global gates.
8. `quality_gate.py`, `VOICE_QUALITY_GATE.json`, `manifest.py`, `pod/*.sh` — source/receipt identity, separate actual paid approval, fixed deadlines, worker cleanup, durable-volume attestation and bounded stop requests.

### Evidence already produced

- Two 24-clip Qwen draft batches rendered/prepared in ignored `.local/voice-lab/auditions/`. The first is short/front-loaded; the second balances states/questions. Its failed happy clip remains rejected. These do not certify all labels.
- Exact pre-event source/frontend baseline saved under `implementation/evidence/voice-prespend-2026-10-11/pre-event-frontend/`. Legacy factory and prior NOW are preserved beside it.
- New event frontend represents `[laughter]` / `[breath]` as single dedicated tokens, never pronounced labels. Actual TRAIN event+delivery support is hashed and required by inference. No event subtype or breath performance is claimed learned.
- Pre-event feature caches/checkpoints intentionally fail the new frontend identity; reprepare into fresh directories. WAVs remain untouched. A new no-event balanced-pilot preparation completed after the frontend change.
- Working/final GTA vocoders bind the exact acoustic checkpoint and oracle mel manifest; thin shipping retains provenance.
- Both pod shell syntax parses exited 0. Python source/embedded Python AST and scoped diff checks passed; those are syntax evidence, not functional model/failure tests.
- `curate_dataset.py template` actually exported the 24-row pending review form beside the source directory. Its earlier Windows hard-link failure was corrected to non-replacing rename, preserving the temporary.
- **Mixed source pilot completed:** `.local/voice-lab/auditions/2026-10-11-A2-mixed-32-v3/` contains 32 newly rendered draft recordings, 84.16 seconds, using 17 Qwen and 15 Cosy jobs sequentially. All nine intended states and seven speech acts are represented. No Cosy neutral route is used.
- Actual new features are in the sibling `2026-10-11-A2-mixed-32-v3-features/`: 49 symbols, 31 train / 1 heldout. Laughter is a dedicated token, with two TRAIN marker occurrences and one heldout request. Audibility and emotional labels still need listening approval. Dataset ID `b780c669e80c6b6986f80063e601715106f297cbd1769209d653e079a4fbd3bd`; feature ID `82395b5965bc3d0c7efb1ad4e49eb9443efbe8cafe31a51631cbd3680da98360`.
- The original pending listening form is `.local/voice-lab/auditions/2026-10-11-A2-mixed-32-v3-review.json`. Exact earlier identities, runtime provider readbacks and limits are saved in [preparation-evidence.json](implementation/evidence/voice-prespend-2026-10-11/preparation-evidence.json). The **historical** 43-input manifest digest `7abfe3cddaaaecd3106248a661bc57b2d2dd50162c69f5acf5ee292d73a4a224` matched at that checkpoint; later changes invalidate it. Regenerate after integration. It is not an approved paid-run recipe.
- **Listening delivery:** `.local/voice-lab/auditions/2026-10-11-A2-mixed-32-listening-v1/` contains three sets, `LISTENING_GUIDE.md` with timestamps/transcripts and individual clips, and `listening-packet.json` binding every new clip to its original WAV hash. Sets A/B/C cover all 32 once (8/15/9 clips), each with the accepted original A2 first; about 2½ minutes total. Only constant listening-volume gain and 0.8-second gaps were added. Raw data remains unchanged. Delivery itself granted no acceptance; the later explicit owner decision below does.
- **Delivery correction and later acceptance:** the owner first reported invisible Markdown embeds; those replies were delivery failures. After native WAV delivery, the subsequent explicit "they are all good" accepts all 32. The original pending form is preserved. A new accepted form and immutable curated dataset were created; never replace the delivery-failure replies with invented earlier acceptance.
- **Accepted pilot:** `.local/voice-lab/dataset/A2-reviewed-32-v3/`, dataset ID `06e9c2b2043e523b684eb7ce32a171dff91ce64af180f2f4a20faeefc710f9e7`; all 32 raw WAV bytes unchanged. Current features after the student-source readiness changes are `.local/voice-lab/feats/A2-reviewed-32-v4-ready/`, feature ID `0401fbbfab96717480da47d51d2434a5214a4715f527380f506acdedc8ef5139`. Earlier feature IDs are historical; the changed prep source intentionally invalidates them. Pilot-only corpus receipt binds this exact dataset; it cannot approve a different unheard corpus.
- **Current preparation in progress:** full 1,378-row local source rendering to `.local/voice-lab/dataset/A2-full-1378-draft-v3/`, with CPU-only existing cached ASR screening in sibling `A2-full-1378-screen-v2/`. This is source inference/QA, not own-model training. Full recordings remain draft unless matched to actual accepted bytes; heuristic/ASR checks cannot establish voice, emotion or laughter quality. Pod environment/delivery helpers and own-student source fixes are being integrated. Do not launch from the old manifest while this wave is in progress.

## Source tools and environment

Ignored local folders:

- `.local/voice-lab/.venv-qwen/` — qwen-tts0.1.1 / Transformers4.57.3.
- `.local/voice-lab/models/qwen3-tts-base/` — pinned `fd4b254389122332181a7c3db7f27e918eec64e3`; Base has no direct natural-language emotion API.
- `.local/voice-lab/.venv-cosy/` — observed custom local inference stack; global/live packages preserved.
- `.local/voice-lab/models/cosyvoice-code/` — pinned `074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc`; Matcha submodule `dd9105b34bf2be2230f4aa1e4769fb586a3c824e`.
- `.local/voice-lab/models/cosyvoice3/` — pinned `29e01c4e8d000f4bcd70751be16fa94bf3d85a18`; required files ~5.42GB.

Cosy inference uses the original A2 WAV and its real instruction+reference API, concatenates all audio chunks and explicitly records CPU ONNX providers/CUDA Torch synthesis. Never cache a Cosy speaker ID across different instructions: it would reuse the earlier prompt text. Do not combine the two environments or keep both GPU models resident. Source tools will not be required by the finished own-weight runtime.

## Next work before spending

1. Mixed pilot listening is complete. Preserve its actual owner acceptance and exact references; do not reuse the rejected neutral clip or adopt unaccepted source performances.
2. Complete the full conversational + chuckle recordings and source screening now in progress; preserve rejects and correct wrong text by re-rendering, never relabel wrong words. Keep unheard performance acceptance separate and use fresh immutable reviewed data/features.
3. Complete source-only preflight, then obtain explicit authorization before any v2 student/model training or free-synthesis/interruption verification that trains a model. Existing old smoke results do not transfer.
4. The current `Voice.say` source supports explicit unique phrase pauses and bounded long-turn chunks without cutting event markers. Explicit word focus is refused until real word-level performed supervision exists; native lexical stress is still represented. Wider intensity/pace, sobs and giggle subtypes are unsupported. Single event duration is currently bounded to about2.73seconds. Actual trained-student playback remains future work.
5. Pin the actual container/dependency/work recipe, verify provider/mount durability, credentials/stop/failure behavior and realistic measured run cost. Source stop-request acknowledgment is not proof billing ended.
6. Regenerate immutable inputs AFTER integration. Mutable gate flags and final priced/deployment approvals are excluded to avoid a circular approval digest. Obtain explicit approval of the concrete digest/dataset/price/budget/work/volume/retention configuration before any student training.
7. Train our acoustic model/vocoder, hear actual held-out neutral/question/emotional/laughter/long-turn student speech, measure game/OBS/brain coexistence, then accept and apply the runtime separately.

Do not close the full voice TODO or claim a human-sounding own model from source auditions. No game `Mods/` staging, game launch, live service change, central memory update, commit or remote publication was performed. The game folder remains protected by the owner's prior direction.
