# Planned short-chuckle speech event corpus

Prepared 2026-10-11 after the owner accepted the original-A2 Cosy happy/chuckle source auditions. The rejected Cosy neutral audition is not an approved replacement voice.

## Scope

These are original, short, friendly English joke/reaction turns for a small genuine chuckle in the accepted A2 identity. Every line contains exactly one literal `[laughter]` event marker. The source should render an audible short chuckle, not speak the marker name. No `[breath]` examples are authored because their source performance has not been accepted.

**All new event performances remain pending rendering and per-clip listening review.** Marker counts and intended labels do not establish audible events, specific laugh types, training quality or a learned runtime ability. No theatrical, anime, sexual, profane, taunting or body-role performance is requested.

The existing 1,341-line `SPEECH_CORPUS.jsonl` is unchanged. This separate event bank can be combined through the source builder's explicit recipe. Do not add laughter to every ordinary turn; the larger conversational corpus remains the main material. These are fictional audition utterances, not evidence of observed actions or events on stream.

## Artifact

`build_event_corpus.py` writes only this note and `SPEECH_EVENT_CORPUS.jsonl`. Re-run with `python training/voice/build_event_corpus.py`; this is text authoring, not audio generation or training.

Each JSONL row contains exactly `id`, `text`, `emotion`, `intensity`, `pace` and `speech_act`. Content-hash IDs include the exact marker position and delivery controls. Lexical transcript grouping uses the current contract, which removes supported event markers; ordinary and event variants of identical spoken words stay in the same split group.

- Rows / unique lexical transcripts: 37 / 37.
- Planned train / heldout groups: 36 / 1.
- All intensity values: 0.35; all intended pace values: 1.0.
- One laughter marker per row; zero breath markers.
- Corpus SHA256: `c4f55f7d5592e183a2b240bc36f78f56464303cf4146325dedd331c2b3399beb`.

| Intended emotion | Rows |
| --- | ---: |
| amused | 20 |
| warm | 8 |
| happy | 9 |

| Intended speech act | Rows |
| --- | ---: |
| aside | 10 |
| exclamation | 5 |
| reassurance | 5 |
| statement | 9 |
| wh_question | 4 |
| yes_no_question | 4 |

## Review requirements

Listen for speaker identity, a short nonverbal chuckle at the marked position, natural transition back into speech, clear words, appropriately modest mood and comfortable timing. Check question intonation against the explicit question labels; trailing event markers do not turn a question into a statement.

If the source omits the chuckle, says 'laughter' aloud, inserts extra words, changes identity or produces an exaggerated laugh, reject and preserve that render. A voiced smile or amused pitch alone does not fulfill a nonverbal event marker. Correct delivery labels only through explicit listening curation, not guesses from text or event counts.

The current normalized transcript split prevents exact lexical variants from leaking across train/heldout. If the supplemental question from our ordinary corpus is used, both its ordinary and event versions remain in its existing heldout group. It does not prove unseen-text generalization or justify training on unreviewed audio. Breath, sobbing, whisper and multiple laugh-type controls remain outside this bank.

The text-authoring run checked allowed controls, unique IDs/lexical transcripts, exact marker counts and presence of both grouped partitions. No source audio, model execution, training or acoustic test was performed by this builder.
