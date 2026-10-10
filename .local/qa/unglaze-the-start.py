# -*- coding: utf-8 -*-
"""Take the other mod's glass out of the starting scenario.

## Owner direction, 2026-10-04, verbatim

*"every dlc shall be optional and this goes back to a todo i told you was major
work, where we will completely make the mod 100% functional and stand alone not
needing any other mods, and DLCs only add content and everything the mod needs is
supplied wwith the mod as the mod, which will have all things needed to
operate(but one thing, issues like the ballistic glass we used needs to be taken
out of the starting scenerio to acturatley make sure it isnt needed to play the
mod"*

## What was there, measured

`RR_Starts.xml` named `RB_ReinforcedGlassWall` and `RB_GlassWall` from ReBuild:
Doors and Corners, register row 185, stance Optional. Those were the **only two**
non-Core def references in the shipped starts -- every other reference in
`RR_Starts.xml` and `RR_Scenarios.xml` resolves to Core or to this package.

## The mechanism was already safe, and that was not the point

`GenStep_Headquarters` resolves the run with `ResolveFirstLoaded` and leaves an
ordinary wall standing when nothing matches, with the reason in a comment: *"a
solid viewing wall is a cosmetic loss and a missing wall is a hole in a sealed
gate hall."* So a Core-only player already got a plain wall and nothing broke.

**The owner's words are *"to acturatley make sure it isnt needed"*, and that is a
claim-accuracy problem rather than a crash problem.** A shipped starting scenario
that names another mod's defs cannot be audited as stand-alone by reading it; you
have to go and read the C# that resolves it. Removing the names makes the claim
checkable, which is why a rule goes in beside this change.

## What is kept, and what is not lost

**The `glazing` field, its plan shape and the genstep stay.** They cost nothing
and a scenario may legitimately use them; what comes out is the shipped start's
*data*. And nothing is lost against today's Core-only experience: a Core-only
player received a plain steel wall at those eleven cells before this change and
receives the same plain steel wall after it.

The earlier owner direction this served -- *"ballistic glass  walls for viewing
the machine remotely and safely"* -- is **kept in the queue and struck in place**
rather than deleted. RimWorld's Core has no see-through wall at all, so serving it
Core-only needs either a def this package ships or a different answer, and that
is a decision rather than a tidy-up.
"""
import io
import re
import sys

NL = chr(10)
PATH = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsStartDefs/RR_Starts.xml"

REPLACEMENT = (
    "    <!-- **THE VIEWING WALL'S GLASS IS GONE, 0.12.87-dev.** Owner, 2026-10-04:" + NL
    + "         \"issues like the ballistic glass we used needs to be taken out of the starting" + NL
    + "         scenerio to acturatley make sure it isnt needed to play the mod\"." + NL
    + NL
    + "         This named RB_ReinforcedGlassWall and RB_GlassWall from ReBuild: Doors and" + NL
    + "         Corners, register row 185, stance Optional. They were the ONLY two non-Core def" + NL
    + "         references in any shipped start, and the genstep already fell back to a plain" + NL
    + "         wall when ReBuild was absent, so nothing broke and nothing changes for a" + NL
    + "         Core-only player: the same eleven cells were plain steel wall before and are" + NL
    + "         plain steel wall now." + NL
    + NL
    + "         What changes is that the claim is checkable. A shipped start that names another" + NL
    + "         mod's defs cannot be audited as stand-alone by reading it; you have to go and" + NL
    + "         read the C# that resolves it. check-register-compliance.py now refuses any" + NL
    + "         non-Core def reference in a shipped start or scenario." + NL
    + NL
    + "         The glazing field, the run plan and the genstep all stay: they cost nothing and" + NL
    + "         a scenario may use them. The earlier owner direction this served, \"ballistic" + NL
    + "         glass  walls for viewing the machine remotely and safely\", stays open in the" + NL
    + "         queue - Core ships no see-through wall, so answering it Core-only is a decision" + NL
    + "         rather than a tidy-up. -->" + NL
)

text = io.open(PATH, encoding="utf-8-sig").read()

if "THE VIEWING WALL'S GLASS IS GONE" in text:
    print("already removed")
    sys.exit(0)

# The authored comment above the block goes with it: it describes the thing being removed.
block = re.search(
    r"[ \t]*<!-- The viewing wall\..*?</glazing>[ \t]*\r?\n",
    text, re.S)
if block is None:
    print("COULD NOT FIND THE COMMENT-PLUS-GLAZING BLOCK; nothing written")
    sys.exit(1)

removed = block.group(0)
for name in ("RB_ReinforcedGlassWall", "RB_GlassWall"):
    if name not in removed:
        print("SAFETY CHECK FAILED: %s is not inside the block being removed" % name)
        sys.exit(1)

text = text[:block.start()] + REPLACEMENT + text[block.end():]
io.open(PATH, "w", encoding="utf-8-sig", newline=NL).write(text)

check = io.open(PATH, encoding="utf-8-sig").read()
for name in ("RB_ReinforcedGlassWall", "RB_GlassWall"):
    if name in check:
        raise SystemExit("ABORT: %s is still referenced after the write" % name)

print("unglaze-the-start")
print("  block removed            : %d lines" % removed.count(NL))
print("  RB_* references left     : 0")
print("  <glazing> blocks left    : %d" % check.count("<glazing>"))
print("  file                     : %d lines" % (check.count(NL) + 1))
