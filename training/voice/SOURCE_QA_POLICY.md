# Full source screening and targeted listening policy

This policy produces a **candidate preparation packet**, not automatic full-corpus acceptance. The owner approved the 32 heard A2 source clips and explicitly prohibited training and pod rental. Future unheard recordings retain that boundary.

## Inputs and command

`summarize_source_screen.py` uses only Python's standard library. It loads no ASR/TTS/model, changes no recording or intended label, and imports no source generator. Inputs are the frozen schema-3 render recipe, source metadata/WAV hashes, `inspect_source_audio.py` inspection recipe and append-only screening results, and the hash-linked actual owner pilot receipts.

```text
python training/voice/summarize_source_screen.py DATASET SCREEN_DIR NEW_OUT_DIR
python training/voice/summarize_source_screen.py DATASET SCREEN_DIR NEW_PARTIAL_OUT_DIR --partial
```

Normal operation requires complete rendered/screened inventories and matching final source/QA receipts. `--partial` explicitly permits a snapshot of complete JSONL lines while writers are active. A torn unpublished last line is counted and omitted from the consumed prefix only in partial mode; it is never deleted. A partial packet cannot be called the completed 1,378-row preparation result.

Each output directory is new. `summary.json` binds recipe, metadata/screen snapshots, original QA recipe/code/report, this summarizer/policy and both owner receipt hashes. `clips.jsonl` retains exact intended source records, raw recognized text, original metrics/flags and supplemental comparisons. `listening-tasks.json` supplies IDs, WAV hashes, paths, wording and intended states for later gain-only listening packets. No audio is created here.

## Conservative transcript comparisons

The original ASR text, normalized fields, word error and flags are always preserved. Additional normalization recognizes a short explicit list of compound segmentation differences such as `note book`/`notebook`, `key board`/`keyboard` and `rim world`/`RimWorld`. It does not broadly concatenate tokens, rewrite names, expand ambiguous contractions or accept paraphrases.

Cardinal word/digit equivalents use ordered English number grammar: fifteen/15, fifty/50, twenty-four/24, one hundred and five/105, and decimal point forms. **Fifteen remains different from fifty; first remains distinct from one; 1.05 remains distinct from 1.5.** Ordinal words can match ordinal digits, and properly grouped thousands commas are handled. Uncertain time/date, dictated-code, fractional or abbreviated readings can remain flagged rather than being guessed. Numeric equivalence is a supplemental transcript classification, not an assertion about emotion or human delivery.

`exact_lexical_match` and `narrow_segmentation_or_number_equivalent` may explain an original transcript flag. They do not erase it or approve the clip. Remaining differences receive `unresolved_asr_disagreement`, even when the original threshold did not flag a small deletion/substitution. A second existing recognizer can help triage disagreements later; it is not loaded by this tool.

### Optional cached second opinion

`recheck_source_words.py` selects only the unresolved transcript IDs from a named summary's clips and listening queue. It verifies the summary's exact recipe, captured source/screen prefixes and each WAV SHA256; an active writer may append after the captured prefix. Shared WAV hashes are recognized once, while every ID retains its own text, controls, base transcript and prior-hearing record. Similar text or a lexical group does not substitute for an audio hash.

```text
python training/voice/recheck_source_words.py DATASET SUMMARY_DIR NEW_OUT_DIR --threads 4 --max-seconds 3600
```

The default points to the already cached `faster-whisper-small` snapshot `536b0662742c02347bc0e980a01041f333bce120` in the local Hugging Face cache. `--model-dir` can name another complete existing local directory explicitly; no model nickname or download path is used. The helper records all weight-file hashes and package versions, sets offline flags and `local_files_only=True`, and uses CPU/int8, one worker and at most four threads. A separate child is stopped at the declared deadline, including model loading; termination may take up to ten additional seconds. Completed newline-delimited rows survive a deadline/failure, with missing IDs and any torn tail reported. Each invocation requires a new output directory and never overwrites a prior result.

`recheck-recipe.json`, `rechecks.jsonl` and `summary.json` bind the original packet and retain both recognizers' transcripts/flags plus supplemental word comparisons. `second_matches_intended`, `two_recognizers_agree_against_intended` and `recognizers_disagree_unresolved` describe transcript evidence only. Two related recognizers can share an error; agreement cannot approve wording, human delivery, emotion or laughter. A prior exact human approval remains separately identified, even if either recognizer disagrees. Second-pass results neither clear base flags nor mutate the dataset or any acceptance/launch receipt.

## Priority and actual prior hearing

Listening candidates are grouped as:

1. **ASR/signal outliers:** unresolved wording, original level/quiet/rushed flags, changed known bindings, very large boundary-quiet fraction and levels more than 12 dB from a sufficiently populated teacher/state median. These are review cues, not proof of bad audio.
2. **Event audibility:** every laughter-marked source row, including any still unrendered or unscreened rows named in the summary inventory. Available unheard event recordings enter the listening tasks. A marker or ASR match cannot establish an actual chuckle.
3. **Stratified candidates:** up to two available unheard examples for each teacher/state/act bucket, in immutable recipe order. This is a reproducible coverage audit, not a claim of random unbiased sampling. An additional seeded random audit can be documented separately if needed.

The known owner receipt is validated through the pilot corpus acceptance receipt's exact SHA256 reference. A new row is classified as **exact previously heard binding** only when WAV SHA256, full text, voice identity and all delivery controls match the actual heard record. The summary names both current and prior IDs. Sharing text, generation seed, provider, voice ID or a similar acoustic result is insufficient. A hash match with different text/labels is called out separately.

Event audibility remains pending for all requested event rows except exact previously heard/accepted bindings. Ordinary wording about laughing is not an event. No breath or laugh-subtype capability is inferred, and this tool never sets `listened=true` for unheard material.

## Full-preparation and future acceptance

Complete inventory plus screening can make a full dataset **technically ready for review** without requiring 1,378 manual playbacks. The packet must identify actual hours, every failure/disagreement, retained/rejected counts, event cases and the actual heard subset. Outliers can be rejected, re-rendered or relabeled only through explicit recorded decisions; this tool never deletes or repairs them automatically.

An owner may later approve a named full dataset through a documented automated-QA/targeted-sampling policy. That receipt must state the method and limits, identify the exact dataset and heard hashes, and avoid pretending every clip was heard. Current per-clip-human curation is a separate contract; its listening acknowledgments cannot be filled from this screening report. This policy alone grants no corpus acceptance, student quality claim, deployment, training or pod-rental permission.

Final student listening remains separate. Reserve `LISTENING_EVAL_TEXT.jsonl` from source construction/training; it evaluates unseen wording, question/statement contrasts, names/numbers, all nine states, supported events and bounded long turns after an actual student pair exists. An ASR match, low reconstruction loss or absence of heuristic flags is never sufficient proof that speech sounds human.
