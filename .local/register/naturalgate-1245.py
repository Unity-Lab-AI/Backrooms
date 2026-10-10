# -*- coding: utf-8 -*-
"""Give any start that names a door a natural gate, not only the inside start.

Owner, 2026-09-30: *"ther is a natural gate that leads to a seeded fixed backrooms and all
backrooms have portals that lead deeper and lead to the world maps tiles"*, and earlier: *"the
store start has a natural portal"*.

**Most of that already exists.** `NaturalFrontierService` finds further ways onward (bounded to
two per coordinate, depth capped at 3) and `RecordWorldExit` already makes a way out lead to a
world tile the branch does not hold. `CONNECTED_COLONY_PORTALS.md` states natural connections are
permanently open and exempt from the window rules, and calls *"the starts that begin with only a
natural gate"* load-bearing.

**What was missing is the seeding.** `SoloGroupOpening.Open` returns immediately unless
`insideStart`, so the Store got no connection at all -- nothing in the generator creates one, and
the owner's report was correct: there was no door to enter.

Steps 1 to 4 of `Open` -- mint the coordinate, generate its map, mark the named surface door,
register the connection -- are exactly what a surface start with a natural gate needs. Only step
5, moving the party inside, is specific to beginning in the Backrooms.

**And the door cell must be offset** now that the layout is placed onto the player's own map.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCEN = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Scenario")
OPENING = os.path.join(SCEN, "SoloGroupOpening.cs")
DEF = os.path.join(SCEN, "RimroomsStartDef.cs")

OPENING_EDITS = [
    (u"            if (start == null || !start.insideStart) { return null; }",
     u"""            // **Any start that names a door gets a natural connection**, not only the
            // inside start. Before 0.12.45-dev this returned here unless `insideStart`, so the
            // Furniture Store -- whose entire premise is a door in the back that should not be
            // there -- began with no Backrooms connection of any kind. Nothing in the
            // headquarters generator creates one, so there was nothing to enter.
            if (start == null || !start.emergenceDoorCell.IsValid) { return null; }"""),

    (u"""            // 5. Put them where they actually start. Done last, so a failure above leaves
            //    everybody standing safely on the surface rather than sealed in a coordinate
            //    with no registered way out.
            MoveOpeningPartyInside(surface, inside, entry);
            campaign.RecordEvent("RR_Event_SoloGroupOpening", coordinate.Id);
            return null;""",
     u"""            // 5. Put them where they actually start -- **only for a start that begins
            //    inside**. Done last, so a failure above leaves everybody standing safely on
            //    the surface rather than sealed in a coordinate with no registered way out.
            //
            //    A surface start with a natural gate stops here: the connection is registered
            //    and permanently open, and the crew are in their own building looking at a door
            //    that was not there yesterday. Whether they go through is theirs to decide.
            if (start.insideStart)
            {
                MoveOpeningPartyInside(surface, inside, entry);
                campaign.RecordEvent("RR_Event_SoloGroupOpening", coordinate.Id);
            }
            else
            {
                campaign.RecordEvent("RR_Event_NaturalGateOpening", coordinate.Id);
            }
            return null;"""),

    # The door cell is authored in layout coordinates, and the layout is now offset onto the
    # player's chosen map. Missing this would look for a door where no door is.
    (u"""            IntVec3 cell = start.emergenceDoorCell;
            if (!cell.IsValid || !cell.InBounds(surface)) { return null; }""",
     u"""            // Offset, because the layout is placed onto whatever map the player chose
            // rather than forcing its own size; see HeadquartersLayout. Reading the authored
            // cell directly would look for a door where no door is.
            IntVec3 cell = start.emergenceDoorCell + HeadquartersLayout.Offset(start, surface.Size);
            if (!cell.IsValid || !cell.InBounds(surface)) { return null; }"""),
]

DEF_EDITS = [
    (u"""            if (insideStart && (!emergenceDoorCell.IsValid ||
                doors == null || !doors.Contains(emergenceDoorCell)))
            { yield return "An inside start must name an emergenceDoorCell that is one of its own doors."; }""",
     u"""            // An inside start MUST name one. Any other start MAY -- and naming one is what
            // gives it a natural gate at 0.12.45-dev. Either way the cell has to be one of this
            // start's own doors, because a cell that is not in the doors list has no door
            // generated at it and the opening would find nothing to mark.
            if (insideStart && !emergenceDoorCell.IsValid)
            { yield return "An inside start must name an emergenceDoorCell."; }
            if (emergenceDoorCell.IsValid && (doors == null || !doors.Contains(emergenceDoorCell)))
            { yield return "emergenceDoorCell must be one of this start's own doors."; }"""),
]


def patch(path, edits, label):
    text = io.open(path, encoding="utf-8").read()
    problems = []
    for old, _ in edits:
        if text.count(old) != 1:
            problems.append("%d of %r" % (text.count(old), old[:64]))
    if problems:
        for problem in problems:
            print("ANCHOR PROBLEM in %s: %s" % (label, problem))
        raise SystemExit(1)
    for old, new in edits:
        text = text.replace(old, new, 1)
    io.open(path, "w", encoding="utf-8", newline="").write(text)
    print("  %s: %d edit(s)" % (label, len(edits)))


patch(OPENING, OPENING_EDITS, "SoloGroupOpening.cs")
patch(DEF, DEF_EDITS, "RimroomsStartDef.cs")
print("any start naming a door now begins with a natural gate")
