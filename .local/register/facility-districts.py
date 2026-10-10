# -*- coding: utf-8 -*-
"""Complexes, neighbourhoods and institutions, on every level, with loot in them.

Owner: *"facilitys and :\\"buildings and neighboorhoods and complexes and shools and hospitals and
military and storages need loot inside of them too"*.

## Why there were no complexes

`FacilityPlanner.Anchors` opens with

    if (coordinate == null || coordinate.Rooms == null || coordinate.Depth <= 1) { return null; }

**so a first level has no facilities at all** -- no school, no hospital, no military post, no
storage complex, just rooms that each happen to have a bench. It is the fourth system found this
week gated on `coordinate.Depth` rather than on distance from the arrival, and the fix is the rule
the archetypes, the inhabitants, the events, the shapes, the corridor widths and the wall
materials all already use: **distance from the spawn hall counts as depth.**

So the global gate goes and eligibility asks per room. The yellow arrival and its immediate
neighbours stay sparse, exactly as the comment beside the gate wanted, and everything past them
can be an institution. **The property the gate was protecting is kept; what changes is that it is
measured per room instead of per level.**

## Why they were small

`MaxRooms = 4`, because *"beyond four the coordinate stops having variety in it"*. That was
written when a level was a twenty-four-room line. A braided maze at depth 2 has forty-eight rooms,
and the owner has now asked for *"neighboorhoods and complexes"* by name -- which is a word for
something bigger than four rooms. Six, and a wider share of the floor eligible.

## And the loot

Twelve of the sixteen archetypes already carry loot. **Four carry none**: the office, the nursery,
the gallery and the duplicate. Those get a loot slot each, drawn from Core's own categories, in
the kind a player would expect to find there -- paperwork and oddments in an office, apparel in a
nursery, art materials in a gallery, and in the duplicate a copy of what the room it apes would
hold.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANNER = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation", "FacilityPlanner.cs")
DEFS = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                    "RimroomsRoomArchetypeDefs", "RR_RoomArchetypes.xml")

# -------------------------------------------------------------- the planner
P_EDITS = [
    (u"""        /// <summary>
        /// Largest. Beyond four the coordinate stops having variety in it, and the owner's
        /// condition is that a solo group can read the place and get out of it.
        /// </summary>
        private const int MaxRooms = 4;""",
     u"""        /// <summary>
        /// Largest.
        ///
        /// **This was four**, written when a level was a twenty-four-room line and four rooms was
        /// a sixth of it. A braided maze at depth 2 has forty-eight rooms, and the owner has asked
        /// for *"neighboorhoods and complexes"* by name -- which is a word for something bigger
        /// than four rooms. The condition it is still held to is theirs: a solo group has to be
        /// able to read the place and get out of it, which is why this is six and not twelve.
        /// </summary>
        private const int MaxRooms = 6;"""),

    (u"""        /// <summary>
        /// Share of eligible rooms that may end up inside a facility. Under a half on purpose:
        /// single rooms of their own kind are what a facility stands out against.
        /// </summary>
        private const float EligibleShare = 0.45f;""",
     u"""        /// <summary>
        /// Share of eligible rooms that may end up inside a facility.
        ///
        /// Still under two thirds on purpose -- single rooms of their own kind are what a facility
        /// stands out against, and a floor that is nothing but institutions has no institutions.
        /// Raised from 0.45 with `MaxRooms`, because the owner asked for complexes and a maze has
        /// the room count to carry them.
        /// </summary>
        private const float EligibleShare = 0.6f;"""),

    (u"""            if (coordinate == null || coordinate.Rooms == null || coordinate.Depth <= 1) { return null; }""",
     u"""            // **NO DEPTH GATE.** This read `coordinate.Depth <= 1`, so **a first level had no
            // facilities at all** -- no school, no hospital, no military post, no storage complex,
            // just rooms that each happened to have a bench. Owner: *"facilitys and buildings and
            // neighboorhoods and complexes and shools and hospitals and military and storages need
            // loot inside of them too"*.
            //
            // It is the fourth system found gated on the coordinate's own depth rather than on
            // distance from the arrival, and the rule that replaced it everywhere else applies
            // here: **distance from the spawn hall counts as depth.** The gate's intent -- the
            // yellow arrival stays sparse -- is kept and measured per room in `Plan`, which is
            // where the eligible set is decided.
            if (coordinate == null || coordinate.Rooms == null) { return null; }"""),

    (u"""                if (string.Equals(room.FamilyId, "threshold_room", StringComparison.Ordinal)) { continue; }
                if (CoordinatePressureLadder.IsQuietRoom(coordinate.Seed, room.Index, total)) { continue; }
                eligible.Add(room.Index);""",
     u"""                if (string.Equals(room.FamilyId, "threshold_room", StringComparison.Ordinal)) { continue; }
                if (CoordinatePressureLadder.IsQuietRoom(coordinate.Seed, room.Index, total)) { continue; }
                // **THE ARRIVAL STAYS SPARSE, AND THAT IS MEASURED PER ROOM.** This is the
                // property the old `coordinate.Depth <= 1` gate was protecting, kept -- the hall
                // and its immediate neighbours are never part of an institution, and everything
                // further out can be. The SAME function the archetypes, the inhabitants, the
                // events and the wall materials all read, so a room the dressing treats as deep
                // and the facility planner treats as shallow cannot exist.
                if (RoomArchetypeService.EffectiveDepth(coordinate, room, coordinate.Depth) <= 1)
                { continue; }
                eligible.Add(room.Index);"""),
]

text = io.open(PLANNER, encoding="utf-8").read()
problems = []
for old, _ in P_EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM (planner): %s" % problem)
    raise SystemExit(1)
for old, new in P_EDITS:
    text = text.replace(old, new, 1)
io.open(PLANNER, "w", encoding="utf-8", newline="").write(text)
print("facilities reach a first level, and a complex may be six rooms")

# ------------------------------------------------------------------- the loot
LOOT = [
    (u"RR_Room_Office", u"""      <li>
        <kind>CategoryMember</kind>
        <category>Manufactured</category>
        <count>1~3</count>
        <chance>0.8</chance>
        <stackCount>3~12</stackCount>
      </li>
"""),
    (u"RR_Room_Nursery", u"""      <li>
        <kind>CategoryMember</kind>
        <category>Apparel</category>
        <count>1~3</count>
        <chance>0.8</chance>
      </li>
"""),
    (u"RR_Room_Gallery", u"""      <li>
        <kind>CategoryMember</kind>
        <category>ResourcesRaw</category>
        <count>1~2</count>
        <chance>0.7</chance>
        <stackCount>10~40</stackCount>
      </li>
"""),
    (u"RR_Room_Duplicate", u"""      <li>
        <kind>CategoryMember</kind>
        <category>Manufactured</category>
        <count>1~2</count>
        <chance>0.7</chance>
        <stackCount>2~8</stackCount>
      </li>
"""),
]

defs = io.open(DEFS, encoding="utf-8-sig").read()
for name, slot in LOOT:
    marker = u"<defName>" + name + u"</defName>"
    if defs.count(marker) != 1:
        print("ANCHOR PROBLEM (defs): %d of %s" % (defs.count(marker), name))
        raise SystemExit(1)
    index = defs.index(marker)
    close = defs.index(u"</slots>", index)
    defs = defs[:close] + slot + u"    " + defs[close:]
    print("loot added to %s" % name)
io.open(DEFS, "w", encoding="utf-8-sig", newline="").write(defs)
print("every archetype now holds something worth carrying out")
