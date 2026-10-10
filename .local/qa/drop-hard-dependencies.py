# -*- coding: utf-8 -*-
"""Stop declaring 293 mods as hard requirements. The ordering stays.

## Owner direction, 2026-10-03, verbatim

*"and something i dont like that is going to take major major work and should be
added to the todo : rework mod to not need any depeancie mods"*

and reiterated the same day: *"and im reiterating the fact that we need to fix
the depancy list so that its accurate to what is required and we hope to have the
mod as a complete stand alone"*.

## This is the declaration half, and it is provably lossless

`About.xml` declared **293 hard `modDependencies`** and **294 `loadAfter`**
entries. Measured before writing a line: **every single `modDependencies`
packageId already appears in `loadAfter`**, and `loadAfter` additionally carries
`Ludeon.RimWorld`. So the dependency block carried **no ordering information that
the load-order block did not already carry.** Deleting it removes a
missing-dependency wall and a mod manager's red list, and changes the load order
by nothing at all.

That identity is re-proved here before anything is written, because *"they are
all in loadAfter"* read off a terminal once is not a reason to delete 1,462 lines.

## What this is NOT

**The guarantee half stays open.** Removing a declaration does not make absence
safe; it only stops advertising. The row in `docs/TODO.md` that says so -- *"the
guarantee half, and THIS is the 'major major work' the owner means"* -- is
untouched by this change, and the claim rule in `check-doc-conformance.py` is
tightened in the same commit so a package that declares nothing cannot start
implying it works with everything.
"""
import io
import re
import sys

NL = chr(10)
ABOUT = "Mod/Rimrooms - Async Industries/About/About.xml"

text = io.open(ABOUT, encoding="utf-8-sig").read()

block = re.search(r"[ \t]*<modDependencies>.*?</modDependencies>[ \t]*\r?\n", text, re.S)
if block is None:
    print("no <modDependencies> block -- already dropped")
    sys.exit(0)

body = block.group(0)
declared = re.findall(r"<packageId>([^<]+)</packageId>", body)
after_block = re.search(r"<loadAfter>(.*?)</loadAfter>", text, re.S)
if after_block is None:
    raise SystemExit("ABORT: no <loadAfter> block, so deleting the dependencies WOULD lose the "
                     "load order. Nothing written.")
load_after = set(value.strip().lower()
                 for value in re.findall(r"<li>([^<]+)</li>", after_block.group(1)))

orphans = sorted(set(d.strip() for d in declared
                     if d.strip().lower() not in load_after))
print("drop-hard-dependencies")
print("  hard dependencies declared : %d" % len(declared))
print("  loadAfter entries          : %d" % len(load_after))
print("  declared but NOT ordered   : %d" % len(orphans))
if orphans:
    for name in orphans[:20]:
        print("      %s" % name)
    raise SystemExit("ABORT: %d dependency/dependencies exist ONLY as a hard requirement, so "
                     "deleting the block would change the load order. Add them to loadAfter "
                     "first. Nothing written." % len(orphans))

# The deletion leaves a comment in its place, because a reader of About.xml who remembers the
# block needs to know it went deliberately. **NO DOUBLE HYPHEN ANYWHERE IN IT** -- `--` is
# illegal inside an XML comment and a de-hyphenation pass once ate the delimiters themselves.
replacement = (
    "  <!-- Owner direction, 2026-10-03: \"rework mod to not need any depeancie mods\", and"
    + NL
    + "       \"we hope to have the mod as a complete stand alone\". This file declared 293 hard"
    + NL
    + "       modDependencies; every one of them was already in loadAfter below, so the block"
    + NL
    + "       carried no ordering a manager did not already have. It only announced 293"
    + NL
    + "       requirements the assembly does not have: it references Assembly-CSharp and three"
    + NL
    + "       UnityEngine modules, and nothing else. Load order is unchanged. -->"
    + NL
)

text = text[:block.start()] + replacement + text[block.end():]
io.open(ABOUT, "w", encoding="utf-8-sig", newline=NL).write(text)

check = io.open(ABOUT, encoding="utf-8-sig").read()
if "<modDependencies>" in check:
    raise SystemExit("ABORT: the block is still present after the write")
still = set(value.strip().lower() for value in re.findall(
    r"<li>([^<]+)</li>", re.search(r"<loadAfter>(.*?)</loadAfter>", check, re.S).group(1)))
if still != load_after:
    raise SystemExit("ABORT: the loadAfter block changed; it must not have")
print("  <modDependencies>          : REMOVED, %d lines" % (body.count(NL)))
print("  loadAfter after the write  : %d entries, unchanged" % len(still))
print("  About.xml                  : %d lines -> %d lines"
      % (io.open(ABOUT, encoding="utf-8-sig").read().count(NL) + body.count(NL) + 1 - 6,
         check.count(NL) + 1))
