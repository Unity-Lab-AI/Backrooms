# -*- coding: utf-8 -*-
"""Close the cross-map zoning row."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"
Q = chr(34)

ROWS = [
    ("**Zoning is the control surface and HALF OF IT IS ALREADY IN THE GAME.**",
     " -- **CLOSED 0.12.99-dev AS AN ABSENCE AND A PAGE, because there was nothing honest left to "
     "build.** The row's measurement holds: `Pawn_PlayerSettings.allowedAreas` is a "
     "`Dictionary<Map, Area>`, scribed with the pawn, so RimWorld already keeps a separate allowed "
     "area per map and already saves it. **Cross-map zoning is a system to reach, not to build.** "
     "**AND THE MEASUREMENT WENT ONE STEP FURTHER, WHICH IS WHAT THE DELIVERABLE TURNED OUT TO BE.** "
     "Read out of the installed assembly: `allowedAreas` is private and the only public accessors "
     "are `AreaRestrictionInPawnCurrentMap` and `EffectiveAreaRestrictionInPawnCurrentMap`, both of "
     "which touch **only the map the pawn is standing on**. There is **no public per-map getter at "
     "all**. So a future session that wants a worker's area on a map they are not on will find no "
     "API, and **the obvious next move is reflection into a private field** -- which would make this "
     "mod the second author of a player setting, and the first disagreement between the two would be "
     "a colonist walking somewhere the player told them not to go. "
     "**So the deliverable is a proof of an absence**, which is the hardest kind of thing to keep "
     "true: `proof-cross-map-zoning.py`, proof 63, asserts that nothing assigns an area anywhere, "
     "that the string `allowedAreas` appears nowhere in the source, and that no reflection is "
     "pointed at `Pawn_PlayerSettings` at all. With **plant suite 40 against it, 7 of 7 caught** -- "
     "because a proof of an absence passes on an empty repository, on a typo in its own pattern, and "
     "on the day somebody renames what it was watching. "
     "**What the mod does instead was audited rather than assumed.** "
     "`RimroomsConnectedWorkComponent.ObserveAreaHere` writes down the area a worker has on a map "
     "**while they are standing on it**, and cross-map planning consults that. It is **permissive "
     "on anything it has never seen** -- an unobserved map answers allowed, matching Core's own "
     "unrestricted default -- the cache is bounded and evicts the least recently confirmed rather "
     "than refusing to learn, and the definitive check still happens on arrival. **A cache of a "
     "reading is not a second copy of the setting:** it is never written back, and a stale "
     "observation costs a wasted walk and never a crossing the player forbade. "
     "**And the automatic crossings honour it for free**, because there is one implementation of "
     "stepping through a gate -- `ConnectedCrossing.StepToward`, three callers -- and the "
     "need-crossing goes through it. "
     "**THE READER-FACING HALF IS THE PART THAT WAS ACTUALLY MISSING.** A player would never guess "
     "they can zone on a coordinate: `wiki/company.md` now says the Architect's zone tools work "
     "there, that RimWorld keeps the per-map restriction and saves it, that this mod reads areas and "
     "never writes them, and **states the limitation plainly** -- the first trip to a map nobody has "
     "been zoned on yet can be a wasted walk, and never a crossing you forbade."),
]


def main():
    text = io.open(TODO, encoding="utf-8-sig").read()
    lines = text.split(NL)
    closed = 0
    for key, evidence in ROWS:
        hits = [i for i, l in enumerate(lines)
                if l.lstrip().startswith("- [ ] ") and key in l]
        if len(hits) != 1:
            print("REFUSED: %r matched %d open row(s)" % (key[:52], len(hits)))
            return 1
        raw = lines[hits[0]]
        lead = raw[:len(raw) - len(raw.lstrip())]
        lines[hits[0]] = "%s- [x] %s%s" % (lead, raw.lstrip()[6:].rstrip(), evidence)
        closed += 1
    io.open(TODO, "w", encoding="utf-8", newline=NL).write(NL.join(lines))
    print("closed %d zoning row(s)" % closed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
