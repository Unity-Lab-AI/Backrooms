# -*- coding: utf-8 -*-
"""Two plants that stopped testing what they claim to test.

## 1. A plant that was only passing because of a bug

`plant-housekeeping.py` plants `<!-- <Mass>5</Mass> -->` into a patch and expects
`check-register-compliance.py` to refuse it as *a patch altering another def's stat bases*.

**It plants the stat base inside an XML comment.** Since 0.12.75-dev that checker strips XML
comments -- a fix made because it had refused a patch for containing the word `statBases` **in the
comment explaining that the value cannot be a `statBases` entry**. So the checker is now right to
ignore this, and the plant was only ever tripping on the defect that was fixed.

**A plant that tests a bug rather than a rule is worse than no plant**: it goes green while the
rule it names is unguarded. It plants a real stat base now.

## 2. A plant aimed at a document that stopped being supervised

`plant-integrations.py` plants a shared-research claim into `docs/MULTIPLAYER.md` and expects the
row 791 claim guard to refuse it. That document left `READER_FACING` when the wiki replaced it, so
the guard no longer applies -- the same consequence three plants in `plant-playing-and-help.py`
caught earlier in this session.

Re-aimed at `docs/wiki/multiplayer.md`, which **is** in the set and is the page a player opens.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOUSE = os.path.join(REPO, ".local", "register", "plant-housekeeping.py")
INTEG = os.path.join(REPO, ".local", "register", "plant-integrations.py")

# ---------------------------------------------------------------- 1. a real stat base
OLD_HOUSE = (u'    ("A PATCH STARTS ALTERING ANOTHER DEF\'S STAT BASES", PATCH,\n'
             u'     "<Patch>", "<Patch>\\n  <!-- <Mass>5</Mass> -->", REGISTER),')
NEW_HOUSE = (u'    # **Not inside a comment.** The first version of this plant wrapped the stat\n'
             u'    # base in `<!-- ... -->`, and `check-register-compliance.py` strips XML\n'
             u'    # comments since 0.12.56-dev -- so the checker was right to ignore it and the\n'
             u'    # plant was only ever tripping on the defect that fix removed. A plant that\n'
             u'    # tests a bug instead of a rule goes green while the rule is unguarded.\n'
             u'    ("A PATCH STARTS ALTERING ANOTHER DEF\'S STAT BASES", PATCH,\n'
             u'     "<Patch>",\n'
             u'     "<Patch>\\n  <Operation Class=\\"PatchOperationAdd\\">\\n'
             u'    <xpath>/Defs/ThingDef[defName=\\"GlowPod\\"]/statBases</xpath>\\n'
             u'    <value><Mass>5</Mass></value>\\n  </Operation>", REGISTER),')

text = io.open(HOUSE, encoding="utf-8").read()
if text.count(OLD_HOUSE) != 1:
    print("HOUSE ANCHOR PROBLEM: %d" % text.count(OLD_HOUSE))
    raise SystemExit(1)
io.open(HOUSE, "w", encoding="utf-8", newline="").write(text.replace(OLD_HOUSE, NEW_HOUSE, 1))

# ---------------------------------------------------------------- 2. aim at the wiki
text = io.open(INTEG, encoding="utf-8").read()

OLD_TARGET = u'DOC = "docs/MULTIPLAYER.md"'
NEW_TARGET = (u'DOC = "docs/MULTIPLAYER.md"\n'
              u'# **The reader-facing claim guard moved to the wiki.** `MULTIPLAYER.md` keeps the\n'
              u'# server detail a maintainer needs and is no longer held to the row 791 guard, which\n'
              u'# is what the plant below detected by going MISSED.\n'
              u'WIKI_DOC = "docs/wiki/multiplayer.md"')
if text.count(OLD_TARGET) != 1:
    print("INTEG TARGET ANCHOR PROBLEM: %d" % text.count(OLD_TARGET))
    raise SystemExit(1)
text = text.replace(OLD_TARGET, NEW_TARGET, 1)

OLD_PLANT = (u'    ("ROW 791: a real shared-research claim lands in a reader-facing document", DOC,\n'
             u'     "## What you need", "## What you need\\n\\nResearch is synchronised research across every "\n'
             u'     "company on the server.", CHECKER),')
NEW_PLANT = (u'    ("ROW 791: a real shared-research claim lands in a reader-facing document", WIKI_DOC,\n'
             u'     "## What it would be",\n'
             u'     "## What it would be\\n\\nResearch is synchronised research across every "\n'
             u'     "company on the server.", CHECKER),')
if text.count(OLD_PLANT) != 1:
    print("INTEG PLANT ANCHOR PROBLEM: %d" % text.count(OLD_PLANT))
    raise SystemExit(1)
text = text.replace(OLD_PLANT, NEW_PLANT, 1)
io.open(INTEG, "w", encoding="utf-8", newline="").write(text)

after_house = io.open(HOUSE, encoding="utf-8").read()
after_integ = io.open(INTEG, encoding="utf-8").read()
failures = []
if u'<!-- <Mass>5</Mass> -->' in after_house:
    failures.append("the commented stat base is still planted")
if u'PatchOperationAdd' not in after_house:
    failures.append("the real stat base was not written")
if u'WIKI_DOC = "docs/wiki/multiplayer.md"' not in after_integ:
    failures.append("the wiki target was not added")
if u'shared-research claim lands in a reader-facing document", DOC,' in after_integ:
    failures.append("the plant still aims at the unsupervised document")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("both plants re-aimed: a real stat base, and the wiki page")
