# -*- coding: utf-8 -*-
"""Bring the art write-up's figures back to what is on disk.

It was written when 15 textures shipped and when the machine gate was still classed as a building
awaiting rotations. Eighteen ship now, and the machine gate is an interface icon: it is the Set Gate
gizmo's picture, drawn flat, and an icon has no world-space facing to be missing.

Every number below was measured in the same run that wrote it.
"""
import io
import sys

PATH = "docs/FOR_REV.md"

EDITS = [
    ("So the honest answer to *how did you make those PNGs* is: **I didn't. I cut them.** What "
     "follows is how 13 source images at 1254×1254 became the 15 textures the game actually loads, "
     "and every number below is measured rather than estimated.",
     "So the honest answer to *how did you make those PNGs* is: **I didn't. I cut them.** What "
     "follows is how 13 source images at 1254×1254 became the 18 textures the game actually loads, "
     "and every number below is measured rather than estimated."),

    ("| Textures out | **15 files**, 128×128 to 384×128 |",
     "| Textures out | **18 files**, 128×128 to 384×128 |"),

    ("| Total shipped size | **532 KB** |",
     "| Total shipped size | **570 KB** |"),

    ("| `single` | One frame, and the def is marked **not rotatable** | machine gate, gate console, "
     "utility generator, field analysis bench | These are drawn as front elevations with a clear "
     "face. **There is no back view and no side view in existence**, so they ship honestly "
     "non-rotatable rather than showing one frame four times |",
     "| `single` | One frame, and the def is marked **not rotatable** | gate console, utility "
     "generator, field analysis bench, field recorder, sealed evidence case, survey tag | These are "
     "drawn as front elevations with a clear face. **There is no back view and no side view in "
     "existence**, so they ship honestly non-rotatable rather than showing one frame four times |\n"
     "| `icon` | One frame, used in the interface and never placed | machine gate | It is the Set "
     "Gate button's picture. A gizmo is drawn flat, so a face-on drawing is exactly right and there "
     "is no facing to be missing |"),

    ("**The four `single` buildings are printed under a heading called ROTATIONS WANTED on every "
     "run.**",
     "**The six `single` buildings are printed under a heading called ROTATIONS WANTED on every "
     "run.**"),
]


def main():
    text = io.open(PATH, encoding="utf-8-sig").read()
    missed = []
    for old, new in EDITS:
        if old not in text:
            missed.append(old[:70])
            continue
        text = text.replace(old, new, 1)
    if missed:
        print("REFUSED: %d edit(s) did not match; nothing written" % len(missed))
        for item in missed:
            print("  - %s" % item)
        return 1
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
    print("corrected %d figure(s) in %s" % (len(EDITS), PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
