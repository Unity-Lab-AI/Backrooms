# -*- coding: utf-8 -*-
"""A natural gate is a door you do not also need. Owner's rule, and it is the right one.

> *"i found a door that was a gate, but it was where a normal door should of been (gates natural
> need to not also be used and needed as normal doors, becasue on the other side was the rest of
> the backrooms map)"*

`GuaranteedFrontiers` collected **every** `Building_Door` on the coordinate and picked two, and
`Evaluate` was happy with any of them. So a door between two rooms -- a door the player has to
walk through to get around the level -- became a permanently open one-way gate to somewhere else.
That is unplayable in the obvious way and wrong in a deeper one: **a way onward is a thing you
find, and you cannot find a door you already use.**

## The rule, and why it is also the best possible answer

A way onward must be a **dead-end door**: walkable on exactly one side, with rock behind it.

Those already exist and the owner asked for them last checkpoint -- `FalseOpening` puts *"doors
to now where"* a third of the way along a blank wall, and `PlaceNativeDoors` builds a real door in
each. **So the door that should not be there is the one that leads somewhere else.** That is the
Backrooms as the owner has been describing it from the start, and it costs no new content.

It is measured from the map rather than from the layout record, because that is what the player
sees: a door with one walkable side has nothing behind it whatever the planner intended.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTIER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                        "NaturalFrontierService.cs")
GUARANTEE = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Portals",
                         "GuaranteedFrontiers.cs")

# ------------------------------------------------- the predicate, in the service
PRED_ANCHOR = u"""        /// <summary>
        /// Whether this doorway is one that leads onward and has not been recorded yet."""

PRED = u'''        /// <summary>
        /// Whether this door is a dead end: walkable on exactly one side, with rock behind it.
        ///
        /// ## The owner's rule
        ///
        /// *"gates natural need to not also be used and needed as normal doors, becasue on the
        /// other side was the rest of the backrooms map"*.
        ///
        /// A door between two rooms is a door the player walks through to get around the level.
        /// Making it a permanently open one-way gate to another map takes that route away and
        /// turns ordinary movement into a trap. **And a way onward is something you find; you
        /// cannot find a door you were already using.**
        ///
        /// ## Why a dead-end door is exactly the right answer
        ///
        /// These already exist, and the owner asked for them one checkpoint ago:
        /// `RoomLayoutPlanner.FalseOpening` puts *"doors to now where"* a third of the way along
        /// a blank wall, and `PlaceNativeDoors` builds a real Core door in each. **So the door
        /// that should not be there is the door that leads somewhere else** -- which is the
        /// setting, written in geometry, at no content cost.
        ///
        /// Measured from the MAP, not from the room graph, because that is what the player sees.
        /// A door with one walkable side has nothing behind it whatever the planner intended, and
        /// a door the player has since walled off stops being a candidate on its own.
        /// </summary>
        internal static bool LeadsNowhere(Thing door)
        {
            if (door == null || !door.Spawned || door.Map == null) { return false; }
            Map map = door.Map;
            int open = 0;
            IntVec3[] directions = { IntVec3.North, IntVec3.East, IntVec3.South, IntVec3.West };
            for (int index = 0; index < directions.Length; index++)
            {
                IntVec3 side = door.Position + directions[index];
                if (!side.InBounds(map)) { continue; }
                // Another door counts as a way through: two doors in a row is still a route.
                if (side.Walkable(map) || side.GetEdifice(map) is Building_Door) { open++; }
            }
            // Exactly one walkable side. A door in open floor has four, an ordinary door between
            // two spaces has two, and a dead end has one.
            return open == 1;
        }

''' + PRED_ANCHOR

# ------------------------------------------------------- the check, inside Evaluate
EVAL_ANCHOR = u"""            IntVec3 approach = PortalAddressService.ApproachCellFor(door);
            if (!PortalAddressService.UsableThreshold(door, approach, door.Map))
            { return "RR_Frontier_Obstructed"; }"""

EVAL = u"""            IntVec3 approach = PortalAddressService.ApproachCellFor(door);
            if (!PortalAddressService.UsableThreshold(door, approach, door.Map))
            { return "RR_Frontier_Obstructed"; }

            // **A GATE IS NEVER A DOOR SOMEBODY NEEDS.** Owner: *"gates natural need to not also
            // be used and needed as normal doors, becasue on the other side was the rest of the
            // backrooms map"*. Checked here so the glow, the float menu and the discovery all
            // agree -- `IsFrontierCandidate` and `Discover` both come through this method.
            if (!LeadsNowhere(door)) { return "RR_Frontier_LeadsNowhere"; }"""

text = io.open(FRONTIER, encoding="utf-8").read()
for old in (PRED_ANCHOR, EVAL_ANCHOR):
    if text.count(old) != 1:
        print("ANCHOR PROBLEM in NaturalFrontierService: %d of %r" % (text.count(old), old[:60]))
        raise SystemExit(1)
text = text.replace(PRED_ANCHOR, PRED, 1)
text = text.replace(EVAL_ANCHOR, EVAL, 1)
io.open(FRONTIER, "w", encoding="utf-8", newline="").write(text)
print("the service refuses a door that is also a route")

# ------------------------------------------- and the guaranteed pair picks from the same set
G_OLD = u"""                var door = all[index] as Building_Door;
                if (door == null || !door.Spawned || door.Destroyed) { continue; }
                // The way home is never a frontier, so it can never be one of the two either.
                if (site != null && door == site.ReturnAnchor) { continue; }
                doors.Add(door);"""
G_NEW = u"""                var door = all[index] as Building_Door;
                if (door == null || !door.Spawned || door.Destroyed) { continue; }
                // The way home is never a frontier, so it can never be one of the two either.
                if (site != null && door == site.ReturnAnchor) { continue; }
                // **AND NEITHER IS A DOOR THE PLAYER NEEDS.** Owner: *"gates natural need to not
                // also be used and needed as normal doors"*. The guarantee chose from every door
                // on the map, so a door between two rooms could become a permanently open one-way
                // gate and take an ordinary route away. The same predicate `Evaluate` uses, so
                // the pair cannot be chosen from doors the service would then refuse.
                if (!NaturalFrontierService.LeadsNowhere(door)) { continue; }
                doors.Add(door);"""

guarantee = io.open(GUARANTEE, encoding="utf-8").read()
if guarantee.count(G_OLD) != 1:
    print("ANCHOR PROBLEM in GuaranteedFrontiers: %d" % guarantee.count(G_OLD))
    raise SystemExit(1)
io.open(GUARANTEE, "w", encoding="utf-8", newline="").write(
    guarantee.replace(G_OLD, G_NEW, 1))
print("the guaranteed pair picks only from dead-end doors")
