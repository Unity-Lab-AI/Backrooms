"""Write planned short-chuckle speech text; never render audio or start training.

Run: python training/voice/build_event_corpus.py
Writes only SPEECH_EVENT_CORPUS.jsonl and EVENT_CORPUS_PLAN.md beside this file.
The existing ordinary speech corpus is left intact. Markers and delivery labels
are authoring intentions; source rendering and per-clip listening remain pending.
"""
import collections
import hashlib
import json
from pathlib import Path

from dataset_contract import canonical_hash, delivery, normalize_transcript, split_for

HERE = Path(__file__).resolve().parent
AUTHORED = [
    ("amused", "aside", "The keyboard didn't move. I just looked everywhere except in front of me. [laughter]"),
    ("amused", "statement", "I organized the cables. They have immediately formed a committee. [laughter]"),
    ("amused", "aside", "[laughter] The cat approved the desk by sitting on the only useful part."),
    ("amused", "aside", "That's not a shortcut. That's the scenic route with extra confidence. [laughter]"),
    ("amused", "yes_no_question", "Did we both walk past the enormous arrow? [laughter]"),
    ("amused", "wh_question", "How did the smallest drawer become the entire hardware department? [laughter]"),
    ("amused", "reassurance", "You haven't broken anything. The button was already auditioning for retirement. [laughter]"),
    ("amused", "exclamation", "Well, that was almost graceful! [laughter]"),
    ("amused", "statement", "I found my pen under the list of places I meant to check. [laughter]"),
    ("amused", "aside", "I named the file final. Apparently that was optimism, not a description. [laughter]"),
    ("amused", "statement", "The loading screen has more dramatic timing than we do. [laughter]"),
    ("amused", "aside", "[laughter] We solved the puzzle right after agreeing it made no sense."),
    ("amused", "aside", "The shelf holds everything except my confidence in that measurement. [laughter]"),
    ("amused", "yes_no_question", "Are we calling that a plan, or an enthusiastic first draft? [laughter]"),
    ("amused", "wh_question", "What is the chair's official position on this arrangement? [laughter]"),
    ("amused", "statement", "[laughter] I brought two chargers and confidently forgot the device."),
    ("amused", "aside", "I can explain the knot, but the cable would need its own diagram. [laughter]"),
    ("amused", "reassurance", "Don't worry. My first attempt had considerably more wobble. [laughter]"),
    ("amused", "exclamation", "Okay, the cup was hiding behind the other cup! [laughter]"),
    ("amused", "aside", "[laughter] That tiny change took a surprisingly large victory lap."),
    ("warm", "statement", "I saved the quiet seat for you. It comes with very limited cat supervision. [laughter]"),
    ("warm", "reassurance", "[laughter] You're welcome to stay. The spare chair has already made itself available."),
    ("warm", "statement", "We can take a break together. The kettle is the most reliable part of this operation. [laughter]"),
    ("warm", "yes_no_question", "Want to hang out while I persuade this drawer to cooperate? [laughter]"),
    ("warm", "statement", "I like working with you. We turn small mistakes into pretty good stories. [laughter]"),
    ("warm", "reassurance", "There's no rush. Even the clock looks like it wants a tea break. [laughter]"),
    ("warm", "aside", "[laughter] I remembered the snacks this time. That's what I call steady progress."),
    ("warm", "exclamation", "That was a lovely little idea, including the slightly crooked corner! [laughter]"),
    ("happy", "aside", "[laughter] It worked on the first try. I'm trying to remain normal about that."),
    ("happy", "exclamation", "Oh, we actually finished before the tea went cold! [laughter]"),
    ("happy", "statement", "I'm keeping that picture. The accidental smile was the best part. [laughter]"),
    ("happy", "yes_no_question", "Did you see how perfectly the last piece fit? [laughter]"),
    ("happy", "wh_question", "What should we celebrate first, the working gate or finding the missing screwdriver? [laughter]"),
    ("happy", "reassurance", "We did well. The little mistakes make the story better. [laughter]"),
    ("happy", "statement", "[laughter] The room finally feels cozy, and the chair has stopped complaining."),
    ("happy", "exclamation", "There we go! Our extremely modest celebration is officially on. [laughter]"),
]

# Additional authored turns, used only if the first bank lacks a heldout group.
# The last is an intentional event variant of our own ordinary-corpus question:
# its lexical group must remain held out with the original, despite the marker.
SUPPLEMENTAL = [
    ("amused", "aside", "The instruction said a small adjustment. My desk interpreted that as a full relocation. [laughter]"),
    ("amused", "yes_no_question", "Does the cat want a progress report, or just the warm chair? [laughter]"),
    ("warm", "reassurance", "We can try again. The cupboard isn't keeping score, even if it looks smug. [laughter]"),
    ("happy", "statement", "[laughter] We found the easy answer just before inventing a complicated one."),
    ("amused", "wh_question", "Why is the spare cable better hidden than the thing we're repairing? [laughter]"),
    ("warm", "aside", "I kept the rough sketch. It has more personality than the very serious folder beside it. [laughter]"),
    ("happy", "exclamation", "The drawer opens quietly now! It has retired from musical performance. [laughter]"),
    ("amused", "statement", "[laughter] My perfectly timed reminder arrived just after I remembered."),
    ("happy", "wh_question", "[laughter] What made our little project so nice?"),
]


def make_row(emotion, act, text):
    text = " ".join(text.split())
    if text.count("[laughter]") != 1 or "[breath]" in text or not normalize_transcript(text):
        raise ValueError("Each authored turn needs lexical speech and one exact laughter marker")
    style = delivery(emotion, 0.35, 1.0, act)
    identity = canonical_hash({"text": text, **style})[:20]
    return {"id": "event_" + identity, "text": text, **style}


def main():
    rows = [make_row(*entry) for entry in AUTHORED]
    if {split_for(row["text"]) for row in rows} != {"train", "heldout"}:
        for entry in SUPPLEMENTAL:
            row = make_row(*entry)
            if split_for(row["text"]) == "heldout":
                rows.append(row)
                break
    groups = {normalize_transcript(row["text"]) for row in rows}
    if len(groups) != len(rows) or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate authored event turns require correction")
    splits = collections.Counter(split_for(row["text"]) for row in rows)
    if set(splits) != {"train", "heldout"}:
        raise ValueError("Author another natural turn to supply the missing grouped partition")
    emotions = collections.Counter(row["emotion"] for row in rows)
    acts = collections.Counter(row["speech_act"] for row in rows)
    data = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    checksum = hashlib.sha256(data.encode("utf-8")).hexdigest()
    (HERE / "SPEECH_EVENT_CORPUS.jsonl").write_text(data, encoding="utf-8", newline="\n")
    note = [
        "# Planned short-chuckle speech event corpus", "",
        "Prepared 2026-10-11 after the owner accepted the original-A2 Cosy happy/chuckle source auditions. The rejected Cosy neutral audition is not an approved replacement voice.", "",
        "## Scope", "",
        "These are original, short, friendly English joke/reaction turns for a small genuine chuckle in the accepted A2 identity. Every line contains exactly one literal `[laughter]` event marker. The source should render an audible short chuckle, not speak the marker name. No `[breath]` examples are authored because their source performance has not been accepted.", "",
        "**All new event performances remain pending rendering and per-clip listening review.** Marker counts and intended labels do not establish audible events, specific laugh types, training quality or a learned runtime ability. No theatrical, anime, sexual, profane, taunting or body-role performance is requested.", "",
        "The existing 1,341-line `SPEECH_CORPUS.jsonl` is unchanged. This separate event bank can be combined through the source builder's explicit recipe. Do not add laughter to every ordinary turn; the larger conversational corpus remains the main material. These are fictional audition utterances, not evidence of observed actions or events on stream.", "",
        "## Artifact", "",
        "`build_event_corpus.py` writes only this note and `SPEECH_EVENT_CORPUS.jsonl`. Re-run with `python training/voice/build_event_corpus.py`; this is text authoring, not audio generation or training.", "",
        "Each JSONL row contains exactly `id`, `text`, `emotion`, `intensity`, `pace` and `speech_act`. Content-hash IDs include the exact marker position and delivery controls. Lexical transcript grouping uses the current contract, which removes supported event markers; ordinary and event variants of identical spoken words stay in the same split group.", "",
        f"- Rows / unique lexical transcripts: {len(rows)} / {len(groups)}.",
        f"- Planned train / heldout groups: {splits['train']} / {splits['heldout']}.",
        "- All intensity values: 0.35; all intended pace values: 1.0.",
        "- One laughter marker per row; zero breath markers.",
        "- Corpus SHA256: `" + checksum + "`.", "",
        "| Intended emotion | Rows |", "| --- | ---: |",
    ]
    note.extend(f"| {emotion} | {emotions[emotion]} |" for emotion in ("amused", "warm", "happy"))
    note.extend(["", "| Intended speech act | Rows |", "| --- | ---: |"])
    note.extend(f"| {act} | {count} |" for act, count in sorted(acts.items()))
    note.extend([
        "", "## Review requirements", "",
        "Listen for speaker identity, a short nonverbal chuckle at the marked position, natural transition back into speech, clear words, appropriately modest mood and comfortable timing. Check question intonation against the explicit question labels; trailing event markers do not turn a question into a statement.", "",
        "If the source omits the chuckle, says 'laughter' aloud, inserts extra words, changes identity or produces an exaggerated laugh, reject and preserve that render. A voiced smile or amused pitch alone does not fulfill a nonverbal event marker. Correct delivery labels only through explicit listening curation, not guesses from text or event counts.", "",
        "The current normalized transcript split prevents exact lexical variants from leaking across train/heldout. If the supplemental question from our ordinary corpus is used, both its ordinary and event versions remain in its existing heldout group. It does not prove unseen-text generalization or justify training on unreviewed audio. Breath, sobbing, whisper and multiple laugh-type controls remain outside this bank.", "",
        "The text-authoring run checked allowed controls, unique IDs/lexical transcripts, exact marker counts and presence of both grouped partitions. No source audio, model execution, training or acoustic test was performed by this builder.", "",
    ])
    (HERE / "EVENT_CORPUS_PLAN.md").write_text("\n".join(note), encoding="utf-8", newline="\n")
    print(json.dumps({"rows": len(rows), "sha256": checksum, "emotions": dict(emotions),
                      "speech_acts": dict(acts), "splits": dict(splits)}, indent=2))


if __name__ == "__main__":
    main()
