# -*- coding: utf-8 -*-
"""The six short lines the second hover pass needs.

Each one is the glance-value version of a paragraph that moved to a hover. None
of them replaces or shortens an existing string -- every original keeps every
word, on the hover of the line added here.
"""
import io
import os
import sys

NL = chr(10)
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/"

# (key whose line we insert AFTER, the new line)
ADDITIONS = [
    ("RR_Release_Budget",
     "  <RR_Release_Held>Holding {0} of {1} places</RR_Release_Held>"),
    ("RR_Requests_NoContact",
     "  <RR_Requests_NoContactBrief>No contact from the corporation yet"
     "</RR_Requests_NoContactBrief>"),
    ("RR_Requests_PastTheHinge",
     "  <RR_Requests_PastTheHingeBrief>The company has stopped naming things"
     "</RR_Requests_PastTheHingeBrief>"),
    ("RR_Lab_Candidates",
     "  <RR_Lab_CandidateCount>{0} eligible benches — page {1} of {2}"
     "</RR_Lab_CandidateCount>"),
    ("RR_UI_ContractTerms",
     "  <RR_UI_ContractTermsBrief>Survey terms</RR_UI_ContractTermsBrief>"),
]

problems = 0
touched = {}


def find_file(key):
    for name in sorted(os.listdir(KEYED)):
        if not name.lower().endswith(".xml"):
            continue
        for line in io.open(KEYED + name, encoding="utf-8-sig").read().split(NL):
            if line.strip().startswith("<%s>" % key):
                return name
    return None


for after_key, new_line in ADDITIONS:
    name = find_file(after_key)
    if name is None:
        print("ANCHOR KEY NOT FOUND ANYWHERE: %s" % after_key)
        problems += 1
        continue
    if name not in touched:
        touched[name] = io.open(KEYED + name, encoding="utf-8-sig").read().split(NL)
    lines = touched[name]
    new_key = new_line.strip()[1:new_line.strip().index(">")]
    if any(line.strip().startswith("<%s>" % new_key) for line in lines):
        print("already present: %s" % new_key)
        continue
    hits = [index for index, line in enumerate(lines)
            if line.strip().startswith("<%s>" % after_key)]
    if len(hits) != 1:
        print("ANCHOR NOT UNIQUE (%d) in %s: %s" % (len(hits), name, after_key))
        problems += 1
        continue
    touched[name] = lines[:hits[0] + 1] + [new_line] + lines[hits[0] + 1:]
    print("%-28s %s after %s" % (name, new_key, after_key))

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for name in touched:
    io.open(KEYED + name, "w", encoding="utf-8-sig", newline=NL).write(NL.join(touched[name]))
    print("wrote %s" % name)
