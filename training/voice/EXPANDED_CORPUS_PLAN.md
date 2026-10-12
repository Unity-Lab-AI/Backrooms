# Expanded conversational source text plan

Prepared 2026-10-11. These are text jobs, not completed recordings or an accepted training dataset.

## Owner target and file contract

The owner requested at least 5,000 varied recordings and several actual hours before a paid pod. This separate candidate contains exactly **5,000 planned jobs**: **4,850 ordinary turns and 150 laughter-marked turns**. It preserves all **1,378 original job objects**, with their original IDs, text, states and controls, and adds **3,622 new exact lexical groups**. The original frozen files are unchanged. `build_expanded_corpus.py` writes only the two expanded text files and this plan; it performs no audio, ASR, feature extraction, model loading, training or cloud action.

Each JSONL row has exactly `id`, `text`, `emotion`, `intensity`, `pace`, `speech_act`, matching the current corpus parser. New IDs hash normalized lexical text plus state and act. The fixed controls remain pace 1.0, neutral intensity 0.0 and other intensity 0.35. No celebrity, forced pitch, extreme intensity, sarcastic/anime instruction, Cosy neutral choice, breath, copied dialogue or spoken stage directions are added.

## Content and utterance sizes

Most combined rows are single conversational turns; two-sentence replies add connected thoughts. The longest new source tier is **three to five medium sentences, 35–65 lexical words**, with everyday language. Current selected paragraphs use three or four sentences. Topics include meals, errands, friends, comfortable daily routines, games and cooperative play, coding/debugging, useful explanations, names, quantities, times and emotional responses. Quiet concern, frustration and disappointment are context-specific rather than dramatic acting on every sentence. All nine intended states and seven speech acts remain present; neutral/warm are exactly 65 percent of jobs.

The authoring banks contain coherent complete sentences. Bounded combinations within each scene produce connected turns; sentence fragments are reused in some variants. These are not 3,622 independently unrelated stories or a guarantee against close-family overlap. Exact normalized duplicates are excluded from every addition, including laughter-stripped duplicates; the original one intentional ordinary/event lexical group is preserved. The separately reserved 38-row evaluation suite has zero exact lexical overlap and remains excluded from training. The existing normalized split is unchanged; near paraphrases and shared sentence parts can still overlap partitions, so final independent listening remains necessary.

Names and numbers appear in useful peer conversation rather than repeated encyclopedic readings. Text spelling does not verify pronunciation. Digits, decimals, dates, C sharp, Python, JavaScript, SQL and UTF eight must pass the actual frontend/source review. Three-to-five sentence text is not proof of fitting **512 phoneme tokens** or **30 seconds**. Validate actual tokens and wave duration before inclusion. A performance exceeding bounds must be rejected and re-rendered from an explicitly shorter text job with a new identity; never compress it or force faster playback to conceal the failure. Longer pages remain runtime chunking work, not a request for longer source clips.

## Existing work, rendering and acceptance

The original 1,378 jobs are a seed candidate. Existing generated WAVs may be retained only with their actual recipe, source IDs, hashes and exact job matches. Render only the additional 3,622 jobs in a fresh source folder; do not rerecord or reset the original batch. Later merge preserves each parent's source identity/provenance and copies verified bytes. Several source IDs are legitimate when they describe actual separate immutable batches. Shared text or seed does not transfer human listening approval.

All new performance labels and laughter audibility remain **intended/unaccepted** until QA. Preserve exact previously heard approval for matching recordings only. Full-corpus automated screening and targeted listening can support a later honest owner decision; never fill `listened=true` for unheard material. This plan grants no corpus acceptance, student quality claim, training, rental, upload or deployment permission. The owner requested wrapping up without waiting for 5,000 audio files; background local completion is separate from this text delivery.

## Coverage inventory

```json
{
  "rows": 5000,
  "preserved_original_rows": 1378,
  "new_rows": 3622,
  "ordinary_rows": 4850,
  "event_rows": 150,
  "base_sha256": {
    "SPEECH_CORPUS.jsonl": "4590b9382eb6c8eba6bbd75ef9b0d4ae1a35c5d231a4a306fb50fbab2d47cef9",
    "SPEECH_EVENT_CORPUS.jsonl": "c4f55f7d5592e183a2b240bc36f78f56464303cf4146325dedd331c2b3399beb"
  },
  "outputs": {
    "SPEECH_CORPUS_EXPANDED.jsonl": {
      "rows": 4850,
      "sha256": "3e268623e8a6a555207c5ac91f5db9646d59909ca50a4838720cc66acb806498"
    },
    "SPEECH_EVENT_CORPUS_EXPANDED.jsonl": {
      "rows": 150,
      "sha256": "6b263d8e6226285950e71ea4844e80a5d47859f805d2075bbcde8495824b874d"
    }
  },
  "emotions": {
    "neutral": 2000,
    "warm": 1250,
    "happy": 250,
    "amused": 300,
    "excited": 250,
    "sad": 250,
    "concerned": 250,
    "frustrated": 250,
    "surprised": 200
  },
  "acts": {
    "statement": 2167,
    "yes_no_question": 584,
    "wh_question": 342,
    "instruction": 929,
    "reassurance": 484,
    "aside": 372,
    "exclamation": 122
  },
  "tiers": {
    "single": 2799,
    "pair": 1641,
    "paragraph": 560
  },
  "splits": {
    "train": 4895,
    "heldout": 105
  },
  "words": {
    "total": 95437,
    "min": 1,
    "median": 14.0,
    "mean": 19.0874,
    "max": 57
  },
  "new_unique_lexical_groups": 3622,
  "combined_lexical_groups": 4999,
  "reserved_evaluation_overlap": 0,
  "original_objects_unchanged": true,
  "estimated_hours_at_140_to_190_words_per_minute": [
    8.371666666666666,
    11.361547619047618
  ],
  "actual_audio_hours": null,
  "audible_performance_acceptance": "pending",
  "training_authorized": false,
  "new_paragraphs": {
    "rows": 560,
    "sentences_min": 3,
    "sentences_max": 4,
    "words_min": 39,
    "words_max": 57
  }
}
```

The hours range is a planning estimate from lexical word count divided by 140–190 words per minute. It excludes measured source timing, silence, chuckles, retries and rejected clips. **Actual audio hours are unknown** until all accepted WAVs are measured; 5,000 text rows alone do not satisfy the owner's several-hour recording requirement.

## Production checks actually performed

This text authoring run checked frozen base SHA256s, exact preserved job objects, safe unique IDs, six-field rows, finite known controls, exact total/state targets, new lexical uniqueness, reserved evaluation separation, existing contract splits and selected paragraph text bounds. It wrote the actual text artifacts and this inventory. No audio/model tests were run and no audible labels were approved.
