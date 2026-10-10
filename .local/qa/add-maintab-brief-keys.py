# -*- coding: utf-8 -*-
"""The short lines that replace the main tab's paragraphs on screen.

Owner direction, 2026-10-04, verbatim: *"and all the tabs of operations are well
designed for a tripple A Mod currently it looks like its all just text wall and
shit"*.

Same rule as the expedition pass: **nothing existing is shortened.** Each long
string keeps every word and moves to the hover; these are the short lines that
draw in its place. Inserted after the long form so the pair stays together for
whoever translates them.

Inserted by line index read from the file rather than by a quoted anchor,
because four of these five strings are long enough that quoting them in a script
is the kind of transcription that drifts by one character and then matches
nothing.
"""
import io
import sys

NL = chr(10)
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/"

# (file, the key whose line we insert AFTER, the new line)
ADDITIONS = [
    ("RR_Company.xml", "RR_Company_OpeningObjective",
     "  <RR_Company_OpeningBriefTitle>Opening brief</RR_Company_OpeningBriefTitle>"),
    ("RR_Company.xml", "RR_UI_LedgerRecent",
     "  <RR_UI_LedgerTitle>Company ledger</RR_UI_LedgerTitle>"),
    ("RR_Investigation.xml", "RR_UI_LabInstructions",
     "  <RR_UI_LabTitle>Laboratory</RR_UI_LabTitle>"),
    ("RR_Investigation.xml", "RR_UI_EvidenceFieldWorkRemaining",
     "  <RR_UI_EvidenceFieldWorkTitle>Field work still outstanding"
     "</RR_UI_EvidenceFieldWorkTitle>"),
    ("RR_OperationsExpeditions.xml", "RR_Debug_CounterNote",
     "  <RR_Debug_CounterTitle>Development counters</RR_Debug_CounterTitle>"),
]

problems = 0
touched = {}


def load(name):
    if name not in touched:
        touched[name] = io.open(KEYED + name, encoding="utf-8-sig").read().split(NL)
    return touched[name]


for name, after_key, new_line in ADDITIONS:
    lines = load(name)
    if new_line in lines:
        print("already present: %s" % new_line.strip()[:58])
        continue
    hits = [index for index, line in enumerate(lines)
            if line.strip().startswith("<%s>" % after_key)]
    if len(hits) != 1:
        print("ANCHOR KEY NOT UNIQUE (%d) in %s: %s" % (len(hits), name, after_key))
        problems += 1
        continue
    at = hits[0]
    touched[name] = lines[:at + 1] + [new_line] + lines[at + 1:]
    print("%-30s added after %s" % (name, after_key))

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for name in touched:
    io.open(KEYED + name, "w", encoding="utf-8-sig", newline=NL).write(NL.join(touched[name]))
    print("wrote %s" % name)
