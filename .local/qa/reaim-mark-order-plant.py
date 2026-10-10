# -*- coding: utf-8 -*-
"""The mark-order plant was deleting the line instead of moving it.

Two entries in `plant-unnerving-register.py` carried the identical
`(target, old, new)` signature -- *"AN INHABITANT IS PLACED WITHOUT BEING
MARKED"* and *"the mark moves after the spawn"* both removed the same line. The
second was meant to test a different claim: that the mark happens **before** the
spawn, so there is no frame in which an inhabitant exists as an unexplained
stranger. Deleting the line tests the first claim twice.

That duplication is also why the table had a dedupe loop bolted after it, which
is what made `tools/check-plant-anchors.py` report `has no readable PLANTS
table`. Fixing the plant removes the need for the loop, and the table is a plain
literal again.

Re-aimed to **move** the mark below the spawn, which is the regression the
ordering claim actually guards.
"""
import io
import sys

NL = chr(10)
PATH = ".local/register/plant-unnerving-register.py"

OLD = (
    '    ("the mark moves after the spawn, leaving a frame with no tell", SERVICE,' + NL
    + '     "            pawn.TryGetComp<CompRimroomsSurvivor>()?.MarkInhabitant(family.defName);"'
    + NL
    + "     + CHR_NL," + NL
    + '     "", PROOF + " --after-spawn-variant"),'
)

NEW = (
    "    # **THIS PLANT USED TO DELETE THE LINE, which is the plant above it.** Both carried the"
    + NL
    + "    # same signature, which is why the table needed a dedupe loop bolted after it -- and"
    + NL
    + "    # that loop is what made `check-plant-anchors.py` report no readable table. The claim"
    + NL
    + "    # this is for is the ORDERING: marked before the spawn, so there is no frame in which"
    + NL
    + "    # an inhabitant exists as an unexplained stranger. So it moves the line." + NL
    + '    ("THE MARK MOVES BELOW THE SPAWN, leaving a frame with no tell", SERVICE,' + NL
    + '     "            pawn.TryGetComp<CompRimroomsSurvivor>()?.MarkInhabitant(family.defName);"'
    + NL
    + "     + CHR_NL" + NL
    + '     + "            if (family.kind == InhabitantKind.Survivor)",' + NL
    + '     "            if (family.kind == InhabitantKind.Survivor)", PROOF),'
)

text = io.open(PATH, encoding="utf-8").read()
if "THE MARK MOVES BELOW THE SPAWN" in text:
    print("already re-aimed")
    sys.exit(0)
if text.count(OLD) != 1:
    print("TARGET NOT UNIQUE (%d); nothing written" % text.count(OLD))
    sys.exit(1)

io.open(PATH, "w", encoding="utf-8", newline=NL).write(text.replace(OLD, NEW))
print("re-aimed the mark-order plant to move the line rather than delete it")
