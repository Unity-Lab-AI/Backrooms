# -*- coding: utf-8 -*-
"""Add the starting-facility feedback loop to the queue, with the owner's direction verbatim.

This is a standing workflow rather than a one-off, so it gets a row. It is `[~]` because the tool
half is built and tested and the authoring half happens during the owner's launch.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ANCHOR = "## Public face: the site, the Workshop page and the collection"

SECTION = NL.join([
"### Owner direction — the starting facilities get fixed by hand and the fix becomes the default (2026-10-05)",
"",
"**Verbatim owner direction (2026-10-05), the loop:** *" + Q + "as i load up the different scenerios "
"we will be needing to fix the layout of the starting facilities(i will be manual using pawns to "
"change the layout and fix some thing, to which you will use the api mod to see what exactly i "
"change/add to the starting facilities that you will be making standard and default to the starting "
"scenrios so that the problems like broken conduit lines are repaired by me, then updated to match "
"for the mods defualt facilities)" + Q + "*",
"",
"**And verbatim on the first thing to do, also 2026-10-05:** *" + Q + "check off open items that we "
"complete/you complete, when i start it up" + Q + "*",
"",
"**Asked at two forks before the launch and answered.** On the wiring: *" + Q + "I'll hand-fix it, you "
"read it back" + Q + "*. On the missing battery: *" + Q + "optrion 2 but ill fix it manually like "
"question 1 and u will use the api mod to look where i change things and then fix the scenerio to "
"have those changes on start next time" + Q + "* — option 2 being **Async Industries only**. "
"**So nothing is auto-authored.** The owner places it, the tool reads it, the def follows.",
"",
"- [~] **The starting-facility feedback loop.** `.local/qa/facility-diff.py` is built and its "
"offline half is verified: `authored` renders a start def's layout exactly, `snapshot` tiles the "
"facility rect through `rimworld/get_cells_info` (read-only, 31×31 tiles under the bridge's "
"1024-cell cap, one cell of margin because the owner may build just outside the authored rect), "
"`diff` reports what changed and **emits paste-ready `<conduits>` and `<buildings>` XML**, and "
"`power` checks grid connectivity from the def alone. **Blueprints and frames count as the owner's "
"intent**, so a fix is readable before pawns finish building it. **Open:** the authoring itself, "
"which happens as the owner launches each start.",
"  - [~] **THE PRE-LAUNCH BASELINE, measured 2026-10-05 before any launch, so the diff has "
"something true to compare against.** **Neither facility has working power as authored.** "
"`RR_AsyncIndustriesStart`: **34 of 34** power-drawing buildings are unconnected, the nearest "
"conduit to any of them is **3 to 7 cells away**, there are **5 separate conduit grids** "
"(167/15/8/8/7 cells), and of the two `WoodFiredGenerator`s **one sits off the wire by 2 cells**. "
"`RR_FurnitureStoreStart`: **8 of 8** unconnected and its single generator is **3 cells off the "
"wire**. **Neither authors a battery**, though the Async Industries start card promises *" + Q
+ "one utility generator with a small reserve battery" + Q + "*. "
"**The number was checked before it was believed** — 34 of 34 is exactly the too-round figure that "
"caught a false reachability result at 0.12.9x, so the distances were measured individually rather "
"than trusted: 3, 3, 3, 6 and 7 cells on the sample. The conduit runs are corridor spines with no "
"spur reaching anything. **This is the owner's reported *" + Q + "broken conduit lines" + Q + "* "
"found deterministically, from data, with no launch needed.**",
"  - [~] **What the loop can and cannot carry, read off `RimroomsStartDef` rather than hoped for.** "
"**Carries:** a building's `thing`, `stuff`, `cell` and `rotation`; a conduit run; a door; an "
"autodoor; a pillar; `batteryFraction`; `fuelFraction`; a glazing wall run. **Does not carry:** a "
"**per-cell floor change**, because flooring is one facility-wide `floorTerrain` plus a per-room "
"boolean and there is no per-cell terrain list; and a **knocked-through wall**, because walls are "
"generated from the room rectangles, so a removal is a room edit rather than a building edit. "
"**Both limits are stated before the session rather than discovered after it**, since a change the "
"def cannot express is owner time that cannot be kept.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    if "the starting facilities get fixed by hand" in text:
        print("the section is already present; nothing written")
        return 1
    if text.count(ANCHOR) != 1:
        print("anchor matched %d time(s); refusing" % text.count(ANCHOR))
        return 1
    at = text.index(ANCHOR)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(
        text[:at] + SECTION + NL + text[at:])
    print("added the starting-facility feedback section with the direction verbatim")
    return 0


if __name__ == "__main__":
    sys.exit(main())
