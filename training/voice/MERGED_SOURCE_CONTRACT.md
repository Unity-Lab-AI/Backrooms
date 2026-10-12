# Preserved multi-source A2 dataset and QA contract

2026-10-11. These new helpers have received source inspection/AST checks only. **Neither merger has been run at this checkpoint.** No student training, source generation, ASR execution, service change, rental, listening approval or live voice apply is performed by them.

The owner-approved expansion target is at least 5,000 varied recordings and several hours of speech before considering a pod. The planned inventory is **1,378 unchanged seed recordings + 3,622 new optimized recordings = 5,000**. Longest training turns are three to five medium sentences, within the existing source duration bounds. Actual hours/quality must be observed; clip count alone is not acceptance.

Read [source throughput/expansion](SOURCE_THROUGHPUT_PLAN.md), [QA policy](SOURCE_QA_POLICY.md), [voice plan](VOICE_PLAN.md), [runtime plan](RUNTIME_INTEGRATION_PLAN.md), [dataset contract](dataset_contract.py) and [current handoff](../../docs/NOW.md). The data agent's expanded text destinations are `training/voice/SPEECH_CORPUS_EXPANDED.jsonl` and `training/voice/SPEECH_EVENT_CORPUS_EXPANDED.jsonl` (**being authored at this source checkpoint; verify their actual delivery before running**). They must preserve the 1,378 original six-field jobs; the optimized builder excludes those exact unchanged jobs and renders only the 3,622 additions.

## Dataset merge CLI

```powershell
python training/voice/merge_source_datasets.py `
  .local/voice-lab/dataset/A2-merged-5000-draft-v1 `
  --parent .local/voice-lab/dataset/A2-full-1378-draft-v3 `
  --parent .local/voice-lab/dataset/A2-extras-3622-optimized-v1 `
  --minimum-clips 5000
```

The existing seed path is actual. The extras and merged destinations above are **planned example names**, until the lead creates/records their actual directories. Use the actual completed extras directory in the command. `--parent` order is intentional: frozen original seed first, additions afterward. Default minimum is 5,000; an explicit smaller value is available for a separately authorized engineering case and does not satisfy the production target.

[merge_source_datasets.py](merge_source_datasets.py) uses standard-library source contracts; it does not import Torch, teacher models, NumPy or an ASR model. For each parent it requires:

- An exact complete v2 `metadata.jsonl`, current schema-3 `render-recipe.json` and completed `source-build.json`. Canonical recipe/source identities, the six job fields, source policy routes and expected rendered rows must agree.
- One selected voice identity across all parents; distinct complete parent paths; both grouped lexical partitions; unchanged actual WAV SHA256 and mono PCM16/24,000Hz/0.25–30-second headers; no orphan `.wav`, timeout or failure artifacts. Model/provider fingerprints are checked as recorded recipe provenance, not by loading or benchmarking providers.
- Recorded builder/worker/shared source fingerprints match their actual local files. Optimized parents additionally bind the imported old builder/worker files, optimization schedule/seeds, runtime optimization identity and complete ordered `source-timing.jsonl`; each Qwen item must have recorded EOS evidence. Provider model files are not copied into the merged dataset.
- Exact source-build dataset/runtime/recipe hashes, source-only status and teacher environment descriptor bindings. Old and optimized sources legitimately have different `source_id` values; these are preserved in every metadata row.
- No repeated rendered IDs or original job IDs across parents, and no added normalized lexical group present in earlier parents or duplicated among additions. Only the frozen 8abb seed's known pair `speech_40b93d87ee480f529324` / `event_c902830ce8352bb49922` is exempt: the ordinary question and its `[laughter]` variant deliberately remain one lexical split group. No generic duplicate exception is granted.

The merger copies existing WAV bytes into a new owned sibling work directory, rechecks destination hashes, writes original rows unchanged and records all parent recipe/build/runtime/metadata/code fingerprints. Parents and their WAVs are never rewritten or relabeled. It then validates the merged metadata and publishes with the existing atomic **no-replace** directory helper. A failure retains `.merging-*` evidence. There is no overwrite, automatic recovery/cleanup or silent re-render.

Output:

```text
NEW_MERGED_DATASET/
  metadata.jsonl                 exact v2 rows, unchanged IDs/source IDs/WAV hashes
  wavs/*.wav                     copied original bytes
  merge-rows.jsonl                each row's parent index/dataset, original job ID and route
  merge-provenance.json           canonical merge ID, merged dataset identity, parent identities/hashes
  parent-evidence/000/...         exact original metadata/recipe/build/runtime copies
  parent-evidence/001/...         exact optimized parent evidence and timing journal
```

There is **no single fabricated `render-recipe.json` or `source-build.json` at the merged root**. Each parent retains its truthful renderer. `load_merged(directory)` returns `(rows, dataset_identity, merge_provenance, row_mapping)` after validating metadata/audio/provenance/evidence bindings. Ordinary v2 preprocessing reads the merged `metadata.jsonl`; old single-renderer source screening helpers must still run on each parent separately.

## QA merge CLI and required inputs

For **each completed parent** first obtain:

1. `BASE_SCREEN_DIR/inspection-recipe.json`, `screening.jsonl`, `summary.json` from the actual full base screen.
2. `SOURCE_SUMMARY_DIR/summary.json`, `clips.jsonl`, `listening-tasks.json` from `summarize_source_screen.py` without `--partial`.
3. `SECOND_ASR_DIR/recheck-recipe.json`, `summary.json`, and actual `rechecks.jsonl` when the requested subset is nonempty, from `recheck_source_words.py`.

The second recognizer covers the summary's unresolved-wording subset, **not all 5,000 recordings**. A zero-request result may legitimately have no `rechecks.jsonl`, but must still have its exact complete recipe/summary. Missing requested results or an interrupted/expired subset fails the merger.

```powershell
python training/voice/merge_source_qa.py `
  .local/voice-lab/dataset/A2-merged-5000-draft-v1 `
  .local/voice-lab/dataset/A2-merged-5000-qa-v1 `
  --parent-qa .local/voice-lab/dataset/A2-full-1378-draft-v3 `
    .local/voice-lab/dataset/A2-full-1378-screen-v2 `
    .local/voice-lab/dataset/A2-full-1378-preparation-v1/source-summary `
    .local/voice-lab/dataset/A2-full-1378-preparation-v1/word-recheck `
  --parent-qa .local/voice-lab/dataset/A2-extras-3622-optimized-v1 `
    .local/voice-lab/dataset/A2-extras-3622-screen-v1 `
    .local/voice-lab/dataset/A2-extras-3622-summary-v1 `
    .local/voice-lab/dataset/A2-extras-3622-word-recheck-v1
```

Every `--parent-qa` takes **four paths in order**: dataset, base screen, full source summary, completed second-ASR directory. Repeat it once per exact parent. These preparation/expansion names are planned until actual outputs exist; the lead records the authoritative paths. No parent may be omitted, substituted or repeated. Output must be new and outside every input directory.

[merge_source_qa.py](merge_source_qa.py) validates the merged provenance, every original source row/hash/text/delivery/route, completed full source/screen snapshots, complete inventory and second-pass requested/result bindings. It recomputes narrow transcript comparisons and prior-heard claims against the actual SHA-bound owner pilot receipts. Sharing a voice, transcript or seed does not mean a clip was heard. It verifies screened seconds against actual WAV frame duration.

All original base flags and raw transcripts, source-summary supplemental flags, actual second raw transcripts/segments/relations and original receipt references remain in `clips.jsonl` and copied per-parent evidence. A second recognizer agreeing with the intended words does not erase the base disagreement/flags. A missing second opinion is explicitly `not_requested`, never fabricated text.

QA output:

```text
NEW_QA_OUTPUT/
  summary.json                   canonical QA ID; all-parent/all-row inventory, hours, counts and hashes
  clips.jsonl                    all merged rows with untouched base/summary/actual second-ASR evidence
  listening-tasks.json            exact merged WAV paths/IDs/hashes and targeted review groups
  parent-qa/000/{base,summary,second,owner}/...
  parent-qa/001/{base,summary,second,owner}/...
```

Listening groups preserve all flags, second-ASR unresolved/agreed-against-target results, unheard event rows and existing stratified/outlier candidates. Ordinary laughter wording is not an event. Every requested event stays pending audible review unless its exact WAV, text, voice and intended delivery match an actual prior owner-heard record. No laughter subtype, breath or broad intensity capability is invented.

The immutable result has `complete_parent_inventory=true` and `complete_row_inventory=true` only after every parent/base row and every requested second result passes validation. It retains `source_performance_acceptance=pending`, `corpus_acceptance_granted=false`, `full_corpus_human_listening_inferred=false`, and false training/rental/deployment fields. Complete technical QA is a review packet, not corpus/student approval.

## Lead's next sequence and limits

1. Preserve/finish the frozen 1,378 seed render and its base screen; keep original receipts/WAVs intact.
2. Review/benchmark the separate optimized implementation and generate only the 3,622 approved new texts into a fresh extras dataset. No competing teacher while seed work is still active.
3. Complete each parent's full base/summary/second-ASR outputs; do not invoke the old single-source `finish_source_preparation.py` on the merged root because it expects one real render recipe.
4. Run the two new mergers on actual completed paths. Record exact 5,000 inventory and **actual several-hour duration**, all flags/event/listening backlog and retained/rejected decisions. If rejected rows reduce the accepted target, generate traceable replacement sources; do not automatically accept or duplicate old rows to keep the count.
5. Prepare fresh v2 features for an accepted merged manifest only when authorized; changing dataset identity invalidates old checkpoint/feature reuse. An owner acceptance receipt must bind this new exact dataset, not a 32-clip pilot or either parent alone.
6. Keep the paid/deployment quality gates closed until actual requirements and owner decisions are recorded. The logical-message paragraph streaming design is later runtime work; no live change is implied by this merge.

Current evidence is source/AST inspection only, with exact CLI/contracts documented. Actual large-file I/O, atomic publication/recovery, per-parent QA integration and complete 5,000 production result remain unexecuted by this agent and require saved observations. The root owns manifest/handoff/background pipeline configuration and will run the actual preparation separately.
