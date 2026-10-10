# -*- coding: utf-8 -*-
"""People and bodies were depth-gated exactly like the dressing was, so a first level had none.

Owner, after walking it: *"i explored it all and there were zero weird events or people"*, and
*"not enough weird stuff like a room with a lost person or a room full of bodies"*.

**Both of those exist already and neither could appear.** `RR_Inhabitants.xml` declares
`RR_Inhabitant_Missing` -- a person who wandered in and did not leave -- and `RR_Inhabitant_
DeadRecent`, `DeadStripped`, `DeadCrew`. Every one carries `minDepth` of 2 or more, and
`InhabitantService.Legal` filters on `coordinate.Depth`. **So a depth-1 level has no people and
no bodies, for the same reason it had no laboratory: it was built empty.**

The same answer as the dressing, for the same reason. A coordinate's **reach** is its own depth
plus how far a player can walk from the spawn hall, so the legality list is drawn against what
the level can actually reach rather than against its doorstep. A first level can now hold the
wanderer, the missing person and the recent dead; the stripped and the lost crew still want more
distance; and the deepest families still want real depth.

**The placement still has to earn it.** A corpse is only put in a room whose own distance from
the hall qualifies for that family, so the rooms beside the threshold stay as quiet as they are
now and it gets worse the further in you walk -- which is the owner's *"variations and oddity and
events and locations and places that vary more even on the first level"*, said about people
rather than furniture.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVICE = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Threats", "InhabitantService.cs")

EDITS = [
    (u'''            List<RimroomsInhabitantDef> legal = Legal(coordinate.Depth,
                CoordinatePressureLadder.Band.Hostile, true);''',
     u'''            // **Drawn against what this level can REACH, not against its doorstep.** Every
            // dead family declares minDepth 2 or more, so a depth-1 coordinate produced an empty
            // list and the owner walked a level with no bodies in it at all. The reach is the
            // coordinate's depth plus how far a player can walk from the spawn hall, which is
            // the same rule the dressing uses.
            List<RimroomsInhabitantDef> legal = Legal(ReachOf(coordinate),
                CoordinatePressureLadder.Band.Hostile, true);'''),

    (u'''        private static List<RimroomsInhabitantDef> Legal(int depth,''',
     u'''        /// <summary>
        /// The deepest content this coordinate can hold anywhere in it.
        ///
        /// Its own depth plus the distance band a room can earn by being far from the spawn
        /// hall. **A level is not one depth** -- the room you arrive in and the room twelve
        /// doors away are different places, and gating on the coordinate's own number treated
        /// them as the same.
        /// </summary>
        internal static int ReachOf(CoordinateRecord coordinate)
        {
            int depth = coordinate == null || coordinate.Depth < 1 ? 1 : coordinate.Depth;
            return depth + Generation.RoomArchetypeService.MaximumDistanceBand;
        }

        /// <summary>
        /// Whether this room is far enough from the spawn hall to hold this family.
        ///
        /// The reach above says what the LEVEL can hold; this says where. Without it a depth-1
        /// coordinate would scatter the deepest dead across the yellow rooms by the door, which
        /// is the opposite of *"places that vary more"* -- it would make the arrival the
        /// strangest part.
        /// </summary>
        internal static bool RoomEarns(CoordinateRecord coordinate, RoomRecord room,
            RimroomsInhabitantDef family)
        {
            if (family == null) { return false; }
            if (coordinate == null || room == null) { return true; }
            int depth = coordinate.Depth < 1 ? 1 : coordinate.Depth;
            return Generation.RoomArchetypeService.EffectiveDepth(coordinate, room, depth)
                >= family.minDepth;
        }

        private static List<RimroomsInhabitantDef> Legal(int depth,'''),
]

text = io.open(SERVICE, encoding="utf-8").read()
problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    text = text.replace(old, new, 1)
io.open(SERVICE, "w", encoding="utf-8", newline="").write(text)
print("inhabitants draw against the level's reach, and rooms have to earn them")
