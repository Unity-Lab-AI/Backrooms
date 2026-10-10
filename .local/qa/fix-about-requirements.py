# -*- coding: utf-8 -*-
"""Correct the mod's own description: it told every player it needs 294 mods, and it needs none.

`About.xml` declares **zero** `modDependencies` -- the block was removed at 0.12.86-dev on the
owner's direction, *"rework mod to not need any depeancie mods"* and *"we hope to have the mod as a
complete stand alone"*. Only `loadAfter` remains, with its 294 entries, which is sorting advice and
not a requirement.

The description never followed. It still says the build *"declares every member of it as a
dependency"*, naming all five expansions and 288 mods. **That is the most-read document this mod
has** -- it is what a player sees in the mod list -- and it was the one nothing checked, because
`check-doc-conformance.py` globs `.md`.

Found by generating the public repository's readme from this text and reading the result: the
readme said *"Needs no other mod and no expansion"* two lines above a section demanding five
expansions. A contradiction that obvious survived because nobody had put the two sentences next to
each other before.

BOM preserved by reading bytes and writing back what was there.
"""
import io
import sys

BOM = b"\xef\xbb\xbf"
PATH = "Mod/Rimrooms - Async Industries/About/About.xml"

OLD_REQUIREMENTS = (
"This build is authored against a specific collection and declares every member of it as a "
"dependency, so your mod manager can tell you what is missing instead of letting the game fail "
"later: RimWorld - Royalty, Ideology, Biotech, Anomaly and Odyssey, and the 288 mods loaded "
"alongside them.")

NEW_REQUIREMENTS = (
"This mod needs nothing but RimWorld itself. It declares no dependencies: not one mod, and not "
"one expansion. Royalty, Ideology, Biotech, Anomaly and Odyssey are each optional, and the parts "
"that use them simply are not there when they are not installed.")

OLD_LOAD = (
"Load this mod last. Every dependency is declared with loadAfter as well as being a requirement, "
"so a sorting manager will place it correctly on its own.")

NEW_LOAD = (
"Load this mod last. It lists 294 mods in loadAfter, which is sorting advice rather than a "
"requirement: a sorting manager will place it correctly on its own, and every one of those mods "
"is optional. Nothing is announced as compatible until it has been tested.")

OLD_WIKI = "https://github.com/Unity-Lab-AI/Backrooms"
NEW_WIKI = "https://github.com/G-Fourteen/Rimrooms-AsyncIndustries"

raw = io.open(PATH, "rb").read()
had_bom = raw.startswith(BOM)
text = raw[len(BOM):].decode("utf-8") if had_bom else raw.decode("utf-8")

changes = 0
for old, new, label in ((OLD_REQUIREMENTS, NEW_REQUIREMENTS, "the dependency claim"),
                        (OLD_LOAD, NEW_LOAD, "the loadAfter sentence"),
                        (OLD_WIKI, NEW_WIKI, "the wiki address")):
    found = text.count(old)
    if found != 1:
        print("NOT UNIQUE (%d): %s" % (found, label))
        sys.exit(1)
    text = text.replace(old, new, 1)
    changes += 1
    print("  rewrote %s" % label)

body = text.encode("utf-8")
io.open(PATH, "wb").write((BOM + body) if had_bom else body)
back = io.open(PATH, "rb").read()
if back.startswith(BOM) != had_bom:
    print("BOM CHANGED -- ABORT")
    sys.exit(1)
print("")
print("%d change(s); BOM %s" % (changes, "kept" if had_bom else "absent"))
