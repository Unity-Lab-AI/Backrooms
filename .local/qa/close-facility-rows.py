# -*- coding: utf-8 -*-
"""Close the seven facility rows the owner's hand-fix and this batch actually completed.

Owner direction 2026-10-05: *"check off open items that we complete/you complete, when i start it
up"*. Each row below was read against the shipped def and the generator before it was ticked --
counted, not assumed -- because a tick nobody measured is worse than an open row.
"""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

# (unique fragment of the row, evidence appended to it)
ROWS = [
    ("**The generator cannot place a vent or a cooler yet, and that is the blocker for 20 of the 26.**",
     " -- **CLOSED 0.12.99-dev, and the fix is the game's own permission rather than a special case.** "
     "`GenStep_Headquarters.cs:351` reads `plan.thing.building.canPlaceOverWall` -- true on `Vent`, "
     "`Cooler` and `Autodoor` in Core -- and replaces **our own** generated wall on that cell, which is "
     "exactly what the game does when a player builds one. **A bed on a wall is still refused**, which "
     "is most of what the original throw was ever for. `check-start-layout` was **taught** the property "
     "rather than switched off, per the standing rule that a ceiling I set myself is mine to manage."),

    ("**Six genuine wall deletions need a way to be expressed.**",
     " -- **CLOSED 0.12.99-dev with the smaller of the two options the row itself named.** "
     "`RimroomsStartDef.removedWalls` is a `List<IntVec3>` and the room walk at "
     "`GenStep_Headquarters.cs:236` skips an edge cell the list holds. **Six cells ship** -- "
     "(37,34), (38,34), (40,34), (41,34), (42,39), (42,44) -- and the row's own arithmetic is why: "
     "*" + Q + "The second is smaller and does not move three room rectangles to express six cells." + Q
     + "* The offset is applied to the cut list exactly as it is to every other coordinate, so a "
     "removal lands where the owner removed it on a 300x300 map rather than in authored space."),

    ("**Trade beacons, one per room that already holds a shelf.**",
     " -- **CLOSED 0.12.99-dev. Eight beacons, one per qualifying room, sited by the owner's rule.** "
     "`OrbitalTradeBeacon` at (30,30), (15,19), (30,19), (45,19), (43,11), (13,29), (13,39) and "
     "(13,47) -- **the middle of the room, never beside a shelf**, which is the owner's wording: "
     "*" + Q + "trade beacons in middle of rooms that already have shelfs in them" + Q + "*. The "
     "negative half of the direction is honoured by the count rather than by a comment: "
     "*" + Q + "if room doesnt have a shelf no trade beacon is wanted and not required" + Q + "*, so "
     "rooms without one got none."),

    ("**The card table ships complete.**",
     " -- **CLOSED 0.12.99-dev. A finished `PokerTable` and its four `Stool`s, not four frames.** "
     "The table is at (25,12) in `WoodLog` with stools at (24,12), (24,13), (27,12) and (27,13). "
     "It read back as **four `PokerTable` frames** because the owner could not finish it, and a frame "
     "is the owner's intent rather than the owner's result -- so the def places the result. "
     "*" + Q + "dont worry about cloth" + Q + "* settles the material question by the owner saying to "
     "ignore it, which is why `WoodLog` carries it and nothing waits on a fabric."),

    ("**The four freezer coolers carry their temperature.**",
     " -- **CLOSED 0.12.99-dev, and the sentinel is `NaN` because 0 is a temperature somebody means.** "
     "`RimroomsStartDef.targetTemperature` defaults to `float.NaN`; `GenStep_Headquarters.cs:378` "
     "writes it into `CompTempControl.targetTemperature` only when it is not `NaN`. The four at "
     "(51,19) through (51,22) each carry **-8**. **A zero default would have been a silent setting** -- "
     "every cooler in every start quietly re-targeted to freezing, with nothing in the def saying so. "
     "A freezer that ships at room temperature is a freezer that quietly is not one, and so is a "
     "larder that ships frozen."),

    ("**Two absent `TextBook`s are NOT deletions and must not be removed from the def.**",
     " -- **CLOSED 0.12.99-dev by NOT acting, which is the whole content of the row.** Both "
     "`TextBook`s remain authored. A `TextBook` is an `Item` rather than a building, so a pawn hauls "
     "it the moment the map starts and its authored cell is empty by the time anything reads the map -- "
     "**absence at a coordinate is not evidence of deletion for a haulable.** The eight real absences "
     "were removed: six `Heater`, one `ElectricStove`, one `ElectricSmithy`, matching the owner's "
     "*" + Q + "ive removed too many heaters" + Q + "* and their later confirmation "
     "*" + Q + "i added heaters too and rmoved some" + Q + "* -- the read found **4 added and 6 "
     "removed**, which is both halves of that sentence. **The naming defect on these two books is a "
     "separate open row and is not closed by this one.**"),

    ("**The starting conduit becomes `HiddenConduit` throughout.**",
     " -- **CLOSED 0.12.99-dev. Eighteen runs, all hidden, and the transmitter test sees both kinds.** "
     "Owner's answer when asked which type: *" + Q + "All HiddenConduit" + Q + "*. "
     "`StartingConduitDef()` resolves `HiddenConduit` **by name with a `PowerConduit` fallback** rather "
     "than through `ThingDefOf`, because `ThingDefOf` would need a field this mod does not own and a "
     "missing def must degrade to the visible wire rather than throw during map generation. "
     "**And the widening was the part that would have shipped a fault:** the *is this cell already a "
     "transmitter* test asked only for `PowerConduit`, so a cell already holding a hidden conduit would "
     "have been given a second one on top. It now asks for both."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith("- [ ] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:48], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d facility row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
