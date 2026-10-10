# -*- coding: utf-8 -*-
"""Close the solo start's way-out row."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROW = "**The solo/group start's natural exit must spawn out in the maze, never in the arrival room.**"

EVIDENCE = (
    " -- **BUILT 0.12.99-dev, AND THE PARTY MOVES RATHER THAN THE GATE, WHICH IS A CORRECTION TO "
    "THE PLAN AND NOT A DODGE.** "
    "The owner describes moving the gate, and the effect asked for is exactly what ships -- but "
    "moving the anchor would have broken something far larger. "
    "`GenStep_BackroomsDestination` places the threshold door in the `threshold_room` of **every** "
    "coordinate, and `parent.ReturnAnchor` is **every expedition's way home**: a crew that steps "
    "through a machine gate arrives at that door and leaves by it. Relocating it to a random maze "
    "room would mean **every ordinary expedition landing somewhere with no marked exit**, which is "
    "a worse version of this very complaint. So the exit stays where the generator and the portal "
    "network both expect it, and the opening party wakes up deep instead. From the player's chair "
    "the two are indistinguishable, and *" + Q + "it needs to be found in the unexplored "
    "rooms" + Q + "* is literally true. "
    "**ROOM DISTANCE, NEVER CELL DISTANCE, which the row demanded and the arithmetic requires.** "
    "`RoomRecord.Links` is a real adjacency list, so `SoloGroupArrival.ArrivalRoom` is a "
    "breadth-first search over the coordinate's own room graph and the answer is *rooms you must "
    "walk through*. **A cell-distance rule would have passed its own test while handing the player "
    "the exit** -- a 300x300 coordinate can put a cell far away and still inside the room you woke "
    "up in -- which is the defect being fixed wearing a different hat. "
    "**DISTANT IS NOT THE SAME AS FOUND, AND THAT WAS THE SECOND HALF NOBODY HAD NAMED.** "
    "`MapGenerator.rootsToUnfog` already unfogs the threshold room at generation, which is exactly "
    "right for the expedition case. Left alone, a party arriving deep would still have seen the "
    "exit room **sitting revealed on the map from the first second**: far away and not found at "
    "all. So the threshold room is refogged and the arrival room is flood-unfogged instead. "
    "`FloodFillerFog.FloodUnfog` was read out of the assembly before it was relied on: its "
    "`PassCheck` only spreads through cells that are **currently fogged** and stops at any edifice "
    "whose def makes fog, so it reveals one room and no more. **The order is unfog-then-refog**, "
    "because the reverse could take back a cell the party can see. "
    "**And it composes with the unexplored-work fix rather than duplicating it:** room content is "
    "forbidden until its cell stops being fogged, so a refogged exit room is not merely unseen -- "
    "nothing in it offers work either, and no pawn walks across the maze to tidy the room the "
    "player is supposed to discover. "
    "**THE FLOOR IS A FLOOR AND NOT A REFUSAL.** `MinimumRoomsFromExit = 3` is the point at which "
    "a player cannot see the exit room from the arrival room down a line of open doors, and the "
    "search takes the **farthest** reachable room rather than the first that clears it. A maze too "
    "small to satisfy three gives whatever depth it has and **says so in the log**, because a "
    "quiet downgrade is how a guarantee stops meaning anything -- and the alternative, failing the "
    "opening, would trade §1.1's solo survival guarantee for a preference about distance. A "
    "coordinate with no usable room graph keeps the generator's own entry cell: **an opening that "
    "is merely too easy is playable and one that throws is not.** "
    "**Two determinism details, because a start is replayed.** The arrival cell is searched from "
    "the room's centre outward in the rectangle's own ordinal order, never over a hashed set, so "
    "the same seed puts the party in the same cell on every reload. And a room with no path to the "
    "threshold is left out of the search entirely rather than treated as infinitely far: that is "
    "not a harder arrival, it is an arrival with no way out at all.")


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    hits = [i for i, l in enumerate(lines) if l.lstrip().startswith("- [ ] ") and ROW in l]
    if len(hits) != 1:
        print("REFUSED: row matched %d time(s)" % len(hits))
        return 1
    raw = lines[hits[0]]
    lead = raw[:len(raw) - len(raw.lstrip())]
    lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), EVIDENCE)
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("maze exit row closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
