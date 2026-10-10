# -*- coding: utf-8 -*-
"""Correct the rotation shortfall: it is 12 frames across 6 buildings, not 14 across 7.

`tools/cut-phase2-art.py` reclassified `RR_MachineGate` as an **icon** rather than a building, and
that is right: it is the Set Gate gizmo's picture, drawn flat in the interface, and a gizmo icon has
no world-space facing to be missing. It dropped out of ROTATIONS WANTED and the count fell with it.

Every document that quoted the old figure is corrected here rather than left to drift, because a
count a reader acts on is exactly the kind of dated assertion this project keeps catching.
"""
import io
import sys

EDITS = [
    ("docs/FOR_REV.md",
     "**Seven buildings are shipping non-rotatable because their other facings do not exist.**",
     "**Six buildings are shipping non-rotatable because their other facings do not exist.**"),

    ("docs/FOR_REV.md",
     "| machine gate | back and side of an arch drawn face on |\n",
     ""),

    ("docs/FOR_REV.md",
     "**14 frames.** The tool prints that count on every run",
     "**12 frames.** The tool prints that count on every run"),

    ("docs/NOW.md",
     "- **non-rotatable** — machine gate, gate console, generator, bench. Front elevations with no "
     "back and no side view. They ship `Graphic_Single` and the cutter prints them under "
     "**ROTATIONS WANTED**. **Seven buildings want rotations: 14 drawings, and only the owner can "
     "author them.**",
     "- **non-rotatable** — gate console, generator, bench, recorder, evidence case, survey tag. "
     "Front elevations with no back and no side view. They ship `Graphic_Single` and the cutter "
     "prints them under **ROTATIONS WANTED**. **Six buildings want rotations: 12 drawings, and "
     "only the owner can author them.** The machine gate is **not** among them — it is the Set "
     "Gate gizmo's icon, drawn flat in the interface, and an icon has no facing to be missing."),

    ("docs/NOW.md",
     "1. **14 drawings.** Seven buildings ship non-rotatable because their other facings do not "
     "exist — machine gate, gate console, utility generator, field analysis bench, field recorder, "
     "sealed evidence case, survey tag.",
     "1. **12 drawings.** Six buildings ship non-rotatable because their other facings do not "
     "exist — gate console, utility generator, field analysis bench, field recorder, sealed "
     "evidence case, survey tag.",),

    ("docs/ROADMAP.md",
     "14 rotation drawings",
     "12 rotation drawings"),
]


def main():
    missed = []
    for path, old, new in EDITS:
        text = io.open(path, encoding="utf-8-sig").read()
        if old not in text:
            missed.append("%s :: %s" % (path, old[:60]))
            continue
        io.open(path, "w", encoding="utf-8", newline="\n").write(text.replace(old, new, 1))
        print("  corrected %s" % path)
    if missed:
        print("")
        print("REFUSED on %d edit(s):" % len(missed))
        for item in missed:
            print("  - %s" % item)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
