# -*- coding: utf-8 -*-
"""Find claims in the published wiki that today's work made false.

Owner, 2026-10-06: *"shit like this needs to be found cia a full review and corrected in the
wiki"*, pointing at a credits page still saying **"No gameplay art or audio is shipped"**.

**A GREP FOR ONE WRONG SENTENCE FINDS ONE WRONG SENTENCE.** This looks for the *shapes* a stale
claim takes, so the next one is caught too:

  * absolute denials about shipped content -- "no new", "nothing is shipped", "no custom"
  * claims that everything in play is somebody else's content
  * named things that have been renamed
  * counts, which rot the moment anything is added

Reported, never auto-edited: a claim needs a person to decide whether the sentence or the world
changed.
"""
import io
import os
import re
import sys

WIKI = os.path.join("docs", "wiki")

# (label, pattern, why it is suspicious now)
SUSPECTS = [
    ("denies shipping content",
     r"(no|never|nothing)\b[^.]{0,60}\b(new |custom |original )?(art|audio|sound|texture|sprite|"
     r"item|building|bench|asset)s?\b[^.]{0,40}(ship|add|includ|provid|carr)",
     "the mod ships original art, audio, items, benches and terrain as of 2026-10-06"),

    ("claims everything is somebody else's content",
     r"every (object|thing|item)[^.]{0,60}(existing|native|game or mod) content",
     "no longer true: original gameplay content ships"),

    ("names a thing that was renamed",
     r"\broute recording\b",
     "the journal's label is 'company field journal' since the paper journal art landed"),

    ("counts that rot",
     r"\b(twelve|thirteen|fourteen|fifteen|sixteen|\d{1,3}) (menu|slide|texture|drawing|png|image|"
     r"sound|cue|mod|page)s?\b",
     "a number in prose is a dated assertion; check it against the package"),

    ("promises no rotation or no facings",
     r"(does not|doesn't|never) rotate",
     "several buildings gained authored facings; check which"),
]


def main():
    if not os.path.isdir(WIKI):
        print("REFUSED: no %s" % WIKI)
        return 1
    findings = []
    for name in sorted(os.listdir(WIKI)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(WIKI, name)
        for number, line in enumerate(io.open(path, encoding="utf-8-sig").read().split("\n"), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("|") or stripped.startswith("<!--"):
                continue
            for label, pattern, why in SUSPECTS:
                if re.search(pattern, stripped, re.I):
                    findings.append((name, number, label, stripped[:120], why))

    print("wiki claim audit")
    print("  pages read : %d" % len([n for n in os.listdir(WIKI) if n.endswith(".md")]))
    print("  suspects   : %d" % len(findings))
    print("")
    for name, number, label, text, why in findings:
        print("  %s:%d  [%s]" % (name, number, label))
        print("      %s" % text)
        print("      why: %s" % why)
        print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
