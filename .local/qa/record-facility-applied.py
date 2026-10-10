# -*- coding: utf-8 -*-
"""Close the facility-application row, and add the solo-start natural gate the owner just reported."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROW = "**Apply the owner's facility changes to `RR_AsyncIndustriesStart`.**"
ANCHOR = "### Owner direction — one pawn must not be pinned at the console until it starves (2026-10-06)"

EVIDENCE = (
    " -- **APPLIED 0.12.99-dev. Every cell is the owner's own**, per "
    "*" + Q + "ANd thhese places i put everything is exact and purposfully and should use them "
    "exactly" + Q + "*. Written into the def: **18 conduit runs covering 233 cells, all "
    "`HiddenConduit`** (the owner's choice once told both kinds ship in Core); **6 removed wall "
    "cells**; the **autodoor at (39,41)**; **4 added walls** including the two **Steel** ones "
    "flanking that door; **43 added buildings** with their material; **8 trade beacons**, one in the "
    "middle of each room that already holds a shelf; the **card table complete with its four "
    "stools**, which read back as frames because the owner had no cloth; **4 coolers at -8 C** for "
    "the freezer; and **12 authored entries dropped**. "
    "**FOUR GENERATOR CAPABILITIES HAD TO BE BUILT FIRST and the first was the blocker for twenty "
    "of the twenty-six wall changes.** The buildings loop threw on any cell holding an edifice, so "
    "a `Cooler` -- whose whole purpose is to sit in a wall -- was refused. It now honours the game's "
    "own `BuildingProperties.canPlaceOverWall`, which is true on `Vent`, `Cooler` and `Autodoor`, "
    "and replaces **our own** wall exactly as the game does when a player builds one; anything "
    "without the flag still throws, because an authored bench on an authored wall is a mistake. "
    "Then `removedWalls`, skipped as the rooms are built so there is no rubble and no work order; "
    "`HiddenConduit` resolved by name with `PowerConduit` as the fallback, because a hard lookup "
    "would cost the whole start to save a cosmetic preference; and `targetTemperature`, with **`NaN` "
    "as the absent value rather than 0, because 0 is a temperature somebody means**. "
    "**AND THE READ WAS WRONG TWICE BEFORE IT WAS RIGHT, both caught by instruments rather than by "
    "me.** Seven things showed as *partial footprints* because a thing the owner MOVED overlaps its "
    "own old position, so filtering by authored occupancy ate half of each -- fixed by clustering "
    "every live cell and diffing **anchors**, which is what a move actually is. Then "
    "`check-start-layout` found **two generators overlapping**, because an authored thing was "
    "counted present if *any* cell of its footprint held its def -- true for a thing shifted one "
    "cell. Testing the **anchor** instead took the absences from 8 to 12 and the overlap went. "
    "**Three further findings, each a real conflict rather than a tool fault.** The owner's stove "
    "covers the receiving-bay stock cell, so **the bay moved** -- their placement is exact, so the "
    "cell that is not theirs is the one that yields. The comms console came back facing north "
    "because `get_cells_info` carries no rotation, which put its interaction cell **inside a wall**; "
    "a moved thing now inherits the facing it was authored with. And the autodoor is listed among "
    "the buildings rather than in `<autodoors>`, because that list is for a door replacing an "
    "authored wall and this one replaces none -- the owner built the wall segment around it. "
    "**`check-start-layout` was taught two things rather than bypassed:** a wall-mountable thing may "
    "cover a wall cell, and such a thing on the facility's **outer** wall is not *outside a room* -- "
    "which is how a freezer is built, since it has to exhaust somewhere that is not the room it "
    "cools. A bench or a bed on a wall is still refused, which is most of what that rule was for. "
    "**Verdict: *3 starting layouts are geometrically sound*.**")

SOLO = NL.join([
"### Owner direction — the solo start's way out must be found, not handed over (2026-10-06)",
"",
"**Verbatim owner report (2026-10-06):** *" + Q + "i added heaters too and rmoved some" + Q + "* "
"(confirming the read, which found **4 added and 6 removed**), and then the solo start: "
"*" + Q + "and something i saw in the backrooms solo/group start... the natural gate needs to spawn "
"in somewhere in the backrooms maze not in the main starting room(the solo start u have to find your "
"way to get out not just have the natural exit gate right next to u in main backroom room at start "
"it needs to be found in the unexplored rooms, so continue the work on all that we need to complete "
"and add this to that todo list" + Q + "*",
"",
"- [ ] **The solo/group start's natural exit must spawn out in the maze, never in the arrival "
"room.** The owner's reason is the whole design of that opening: *" + Q + "the solo start u have to "
"find your way to get out" + Q + "*. An exit beside the player at spawn turns a survival opening "
"into a menu. "
"**And it composes with the unexplored-work fix landed in this batch:** a coordinate starts fogged "
"except its entry cell, and content is forbidden until its cell is seen, so an exit placed deep in "
"the maze is genuinely *found* rather than merely distant. **The placement rule needs stating as a "
"minimum room distance from the arrival room rather than a cell distance**, because a 300×300 "
"coordinate can put a cell far away and still inside the room you woke up in.",
"",
])


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    hits = [i for i, l in enumerate(lines)
            if l.lstrip().startswith(("- [ ] ", "- [~] ")) and ROW in l]
    if len(hits) != 1:
        print("facility row matched %d time(s); refusing" % len(hits))
        return 1
    raw = lines[hits[0]]
    lead = raw[:len(raw) - len(raw.lstrip())]
    lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), EVIDENCE)
    text = NL.join(lines)
    if "the solo start's way out must be found" not in text:
        if text.count(ANCHOR) != 1:
            print("solo anchor matched %d time(s); refusing" % text.count(ANCHOR))
            return 1
        at = text.index(ANCHOR)
        text = text[:at] + SOLO + NL + text[at:]
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
    print("facility row closed; solo-start row added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
