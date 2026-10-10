# -*- coding: utf-8 -*-
"""Drop the dispositions whose labels stopped being retired on 2026-10-06.

`check-retired-content.py` derives retired vocabulary from defs that are archived under
`historical-content/` and no longer declared by the package. The owner's full reversal brought
six of those defs back, so sixteen phrases in this file now describe live content. The checker
asked for them to be removed *"so the file cannot rot"*, which is the checker working.

Prints what it removes and what it keeps, because a silent prune of a vocabulary file is
indistinguishable from losing it.
"""
import io
import json
import sys

PATH = "tools/retired-vocabulary.json"

# Reported by `python tools/check-retired-content.py`, verbatim, not guessed.
STALE = [
    "analysis bench",
    "control console",
    "emergency return",
    "emergency return cutoff",
    "faded institutional",
    "faded institutional carpet",
    "field analysis",
    "field analysis bench",
    "fluorescent fixture",
    "gate control",
    "gate control console",
    "institutional carpet",
    "liminal fluorescent",
    "liminal fluorescent fixture",
    "return cutoff",
    "utility generator",
]


def main():
    data = json.load(io.open(PATH, encoding="utf-8"))
    phrases = data.get("phrases")
    if not isinstance(phrases, dict):
        print("REFUSED: %s has no phrases object" % PATH)
        return 1

    missing = [p for p in STALE if p not in phrases]
    if missing:
        print("REFUSED: %d phrase(s) the checker reported are not in the file: %s"
              % (len(missing), ", ".join(missing)))
        return 1

    for phrase in STALE:
        print("  remove  %-32s -> %s" % (phrase, phrases.pop(phrase)))

    data["phrases"] = dict(sorted(phrases.items()))
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("")
    print("removed %d, kept %d" % (len(STALE), len(phrases)))
    for phrase in sorted(phrases):
        print("  keep    %s" % phrase)
    return 0


if __name__ == "__main__":
    sys.exit(main())
