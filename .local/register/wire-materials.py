# -*- coding: utf-8 -*-
"""Row 1005: give a coordinate a material palette instead of hardcoding wood.

`RoomContentBuilder.Place` read `definition.MadeFromStuff ? ThingDefOf.WoodLog : null`, so every
stuffable fixture in every room of every coordinate in the game was wooden. The coordinate is
threaded into both placement helpers so the palette can be per coordinate rather than per room or
per item -- a room with three materials in it reads as noise, a coordinate fitted out in one reads
as a place.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Generation", "RoomContentBuilder.cs")

s = io.open(PATH, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d (wanted %d): %r" % (s.count(old), count, old[:70])
    s = s.replace(old, new)


# ------------------------------------------------------------------ the two signatures
sub("""        private static Thing Place(Map map, RoomRecord room, string defName, HashSet<IntVec3> reserved,
            int seed, int slot, bool minified = false, int count = 1)""",
    """        private static Thing Place(Map map, RoomRecord room, CoordinateRecord coordinate,
            string defName, HashSet<IntVec3> reserved,
            int seed, int slot, bool minified = false, int count = 1)""")

sub("        private static Thing TryPlace(Map map, RoomRecord room, ThingDef definition,",
    "        private static Thing TryPlace(Map map, RoomRecord room, CoordinateRecord coordinate,\n"
    "            ThingDef definition,")

# ------------------------------------------------------------------ the hardcoded material
sub("""            Thing thing = ThingMaker.MakeThing(definition, definition.MadeFromStuff ? ThingDefOf.WoodLog : null);""",
    """            // Row 1005. This was `definition.MadeFromStuff ? ThingDefOf.WoodLog : null`, which
            // made every stuffable fixture on every coordinate in the game wooden -- not the
            // def's own default, one hardcoded material. The palette is per coordinate and
            // derived from its seed, so a coordinate looks like somewhere and two coordinates
            // look different. See CoordinateMaterials.
            Thing thing = ThingMaker.MakeThing(definition,
                CoordinateMaterials.StuffFor(definition, coordinate));""")

# ------------------------------------------------------------------ the call sites
count = len(re.findall(r"Place\(map, room, ", s))
s = s.replace("Place(map, room, ", "Place(map, room, coordinate, ")
print("rewrote %d placement call site(s)" % count)

# TryPlace's own internal call to Place, if it has one, now carries the coordinate too because the
# same textual rewrite applied. Verify no call site was missed and none was double-written.
assert "Place(map, room, coordinate, coordinate, " not in s, "a call site was rewritten twice"
assert not re.search(r"Place\(map, room, (?!coordinate)", s), "a call site was missed"

io.open(PATH, "w", encoding="utf-8", newline="").write(s)
print("RoomContentBuilder threaded with the coordinate")
