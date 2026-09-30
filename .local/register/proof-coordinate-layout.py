# -*- coding: utf-8 -*-
"""A Backrooms coordinate's geometry holds at every depth it can be generated at.

Why this exists
---------------
**The geometry of a coordinate had no proof coverage at all.** Forty proofs, thirteen checkers,
and not one of them asserted the map size, the room count, the room dimensions, the slot spacing
or the connectivity of the generated graph. That is measurable: every constant in
`RoomLayoutPlanner` was changed at 0.12.49-dev and **all forty proofs still passed.**

It is the same blind spot that let a light count stop every coordinate generating from 0.7.8-dev
to 0.12.47-dev -- thirty-nine checkpoints -- because a proof that reads source text cannot see
that two numbers no longer agree.

How this proof avoids becoming the thing it is checking
-------------------------------------------------------
**It parses the constants out of the C# and recomputes from them.** It does not hard-code 300, or
14, or 6. If somebody changes `Margin`, this recomputes with the new margin and still asserts that
rooms land inside the map. A proof that carried its own copy of the numbers would be a second
derivation -- exactly the defect class this project keeps getting caught by.

What it cannot do
-----------------
It re-implements the planner's **integer arithmetic** in Python to check it. That is a second
derivation of the arithmetic, used deliberately and only here, because the alternative is spending
a player's launch to find out that a room landed off the edge of the map. The C# remains the source
of truth; a divergence between the two shows up as a failure here, which is the point.

**And the model has a hole that a plant found.** It parses the CONSTANTS out of the C# and then
computes with its own copy of the FORMULAS -- so changing a constant is caught, and **deleting a
step from the algorithm is not.** A plant that removed `if (span % 2 != 0) { span--; }` from
`SlotRoomSpan` walked straight past the computed evenness claim, because the model was still doing
the subtraction itself.

Every modelled formula is therefore paired with a **source claim** that the step still exists in
the C#. The model asserts the property; the source claim asserts the code still computes it. One
without the other is exactly the mention-versus-assertion defect this project keeps meeting.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


planner = read(os.path.join(SRC, "Generation", "RoomLayoutPlanner.cs"))
service = read(os.path.join(SRC, "Generation", "DestinationService.cs"))
genstep = read(os.path.join(SRC, "Generation", "GenStep_BackroomsDestination.cs"))


def constant(text, name, kind="int"):
    """The value the C# actually holds, not a copy of it."""
    match = re.search(r"const\s+%s\s+%s\s*=\s*(-?\d+)\s*;" % (kind, re.escape(name)), text)
    return int(match.group(1)) if match else None


print("")
print("the constants are read from the source, never copied")
print("-" * 78)

MAP_W = constant(service, "MapWidth")
MAP_H = constant(service, "MapHeight")
MARGIN = constant(planner, "Margin")
GAP = constant(planner, "SlotGap")
MIN_SLOTS = constant(planner, "MinSlotsPerAxis")
MAX_SLOTS = constant(planner, "MaxSlotsPerAxis")
MAX_ROOMS = constant(planner, "MaxRooms")
PILLAR_SPACING = constant(planner, "PillarSpacing")
PILLAR_THRESHOLD = constant(planner, "PillarThreshold")

values = {
    "MapWidth": MAP_W, "MapHeight": MAP_H, "Margin": MARGIN, "SlotGap": GAP,
    "MinSlotsPerAxis": MIN_SLOTS, "MaxSlotsPerAxis": MAX_SLOTS, "MaxRooms": MAX_ROOMS,
    "PillarSpacing": PILLAR_SPACING, "PillarThreshold": PILLAR_THRESHOLD,
}
missing = sorted(name for name, value in values.items() if value is None)
check("every constant this proof reasons about was found in the source",
      not missing,
      "-- could not read: %s. A renamed constant must fail here rather than be silently "
      "skipped, or this proof would pass by reading nothing" % missing)
if missing:
    print("")
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)

print("     read: %s" % ", ".join("%s=%d" % (k, values[k]) for k in sorted(values)))

check("a coordinate is square", MAP_W == MAP_H,
      "-- %dx%d; the planner's slot grid is computed from MapWidth on both axes"
      % (MAP_W, MAP_H))

check("A COORDINATE IS THE SIZE THE OWNER ASKED FOR",
      MAP_W >= 300,
      "-- owner direction, verbatim: *\"theri 300x300 gate\"*. Found %d" % MAP_W)

check("the slot range is a real range", MIN_SLOTS >= 2 and MAX_SLOTS > MIN_SLOTS,
      "-- %d..%d; a single slot count would make depth meaningless" % (MIN_SLOTS, MAX_SLOTS))


# --------------------------------------------------------------------------------------------
# The planner's integer arithmetic, recomputed from the constants above.
def slots_for(depth):
    value = MIN_SLOTS + max(0, depth - 1)
    return max(MIN_SLOTS, min(MAX_SLOTS, value))


def spacing_for(slots):
    return (MAP_W - MARGIN * 2) // slots


def span_for(spacing):
    value = spacing - GAP
    if value % 2:
        value -= 1
    return max(8, value)


def center_for(index, spacing):
    return MARGIN + spacing // 2 + spacing * index


def serpentine(slots):
    order = []
    for row in range(slots):
        for column in range(slots):
            x = column if row % 2 == 0 else slots - 1 - column
            order.append((x, row))
    return order


def chain_length(order):
    return max(6, min(MAX_ROOMS, min(len(order), len(order) * 2 // 3)))


max_room_span = span_for(spacing_for(MIN_SLOTS))

print("")
print("every depth a coordinate can be generated at")
print("-" * 78)

DEPTH_CEILING = 8
profile = []
for depth in range(1, DEPTH_CEILING + 1):
    slots = slots_for(depth)
    spacing = spacing_for(slots)
    span = span_for(spacing)
    order = serpentine(slots)
    chain = chain_length(order)
    first_min = center_for(0, spacing) - span // 2
    last_max = center_for(slots - 1, spacing) - span // 2 + span - 1
    gap = (center_for(1, spacing) - span // 2) - (center_for(0, spacing) - span // 2 + span - 1) - 1
    adjacent = all(abs(order[i][0] - order[i + 1][0]) + abs(order[i][1] - order[i + 1][1]) == 1
                   for i in range(chain - 1))
    profile.append((depth, slots, spacing, span, chain, first_min, last_max, gap, adjacent))

print("     depth slots spacing span rooms  x-extent      gap")
for depth, slots, spacing, span, chain, lo, hi, gap, _ in profile:
    print("     %5d %5d %7d %4d %5d  %3d..%-3d %8d" % (depth, slots, spacing, span, chain, lo, hi, gap))

check("NO ROOM IS EVER PLACED OFF THE MAP",
      all(lo >= 1 and hi < MAP_W - 1 for _, _, _, _, _, lo, hi, _, _ in profile),
      "-- DestinationService.WithinMap refuses minX < 1 or maxX >= MapWidth - 1, and a refused "
      "graph means the coordinate does not generate at all: %s"
      % [(d, lo, hi) for d, _, _, _, _, lo, hi, _, _ in profile if lo < 1 or hi >= MAP_W - 1])

check("every room is an even number of cells across",
      all(span % 2 == 0 for _, _, _, span, _, _, _, _, _ in profile),
      "-- CellRect.CenterCell is where every door and corridor is aimed, and an odd span moves "
      "it off the slot centre: %s"
      % [(d, s) for d, _, _, s, _, _, _, _, _ in profile if s % 2])

# ---- the model computes these; these claims assert the C# still does the same steps ----
print("")
print("     the formulas the model copies, asserted against the source")
check("THE SPAN IS FORCED EVEN IN THE SOURCE, NOT JUST IN THIS PROOF'S MODEL",
      "if (span % 2 != 0) { span--; }" in planner,
      "-- a plant that deleted this line passed the computed evenness claim, because the model "
      "was still doing the subtraction itself. A modelled property needs a source claim beside it")

check("the slot spacing is still computed from the margin and the slot count",
      "return (DestinationService.MapWidth - Margin * 2) / slots;" in planner,
      "-- the model copies this formula; if the C# stops dividing by the slot count, nothing "
      "computed here would notice")

check("a slot centre is still margin plus half a slot plus whole slots",
      "return Margin + spacing / 2 + spacing * index;" in planner,
      "-- the bounds claims all rest on this, and they rest on the model's copy of it")

check("the span is still the spacing less the gap",
      "int span = spacing - SlotGap;" in planner,
      "-- the gap is what a corridor is carved through; a span equal to the spacing leaves none")

check("the serpentine still alternates direction row by row",
      "int x = row % 2 == 0 ? column : slots - 1 - column;" in planner,
      "-- row-major WITHOUT the alternation makes consecutive entries jump the full width of the "
      "grid, and the chain would be linked between rooms that are not neighbours")

check("the chain still takes two thirds of the grid",
      "order.Count * 2 / 3" in planner,
      "-- taking all of it leaves no rock between the arms of the chain")

check("the slot count still rises with depth",
      "int slots = MinSlotsPerAxis + (depth < 1 ? 0 : depth - 1);" in planner,
      "-- the whole depth profile the model prints rests on this one line")

print("")
check("no room exceeds what the validator will accept",
      all(span <= max_room_span for _, _, _, span, _, _, _, _, _ in profile),
      "-- ValidateRooms bounds width and height by MaxRoomSpan, computed as %d from the coarsest "
      "slot grid" % max_room_span)

check("THERE IS ALWAYS ROCK BETWEEN NEIGHBOURING ROOMS FOR A CORRIDOR TO RUN THROUGH",
      all(gap >= 2 for _, _, _, _, _, _, _, gap, _ in profile),
      "-- BuildCorridors carves from one room's edge to the next; a gap under 2 leaves it "
      "nothing to carve and the rooms would share a wall: %s"
      % [(d, g) for d, _, _, _, _, _, _, g, _ in profile if g < 2])

check("THE SERPENTINE CHAIN IS CONNECTED AT EVERY DEPTH",
      all(adjacent for _, _, _, _, _, _, _, _, adjacent in profile),
      "-- consecutive rooms are linked directly, so if two consecutive slots are not grid "
      "neighbours the corridor builder throws RR_Generation_NonAdjacentRooms and every room "
      "past the break is unreachable")

check("the room count stays inside what the validator accepts",
      all(6 <= chain <= MAX_ROOMS for _, _, _, _, chain, _, _, _, _ in profile),
      "-- ValidateRooms refuses fewer than 6 or more than MaxRooms=%d" % MAX_ROOMS)

check("LEVEL ZERO IS GRAND, AND THE ROOM COUNT GOES DOWN TO PAY FOR IT",
      profile[0][3] >= 60 and profile[0][4] <= 8,
      "-- owner direction, verbatim: *\"making the 0 level rooms be grand large spaces and leas "
      "than 60-100 romms\"*. Depth 1 is %d rooms of %d cells; a hall that size cannot fit in the "
      "19-cell slot the planner used before" % (profile[0][4], profile[0][3]))

check("it gets denser and smaller deeper in, which is the other half of the direction",
      profile[-1][4] > profile[0][4] and profile[-1][3] < profile[0][3],
      "-- *\"this can propigate depper\"*. Depth 1: %d rooms of %d. Depth %d: %d rooms of %d"
      % (profile[0][4], profile[0][3], profile[-1][0], profile[-1][4], profile[-1][3]))

check("no depth ever exceeds the count the owner set as the ceiling",
      all(chain <= MAX_ROOMS for _, _, _, _, chain, _, _, _, _ in profile),
      "-- *\"leas than 60-100 romms\"*, and MaxRooms is %d" % MAX_ROOMS)


print("")
print("the pillars, which are what make a grand space possible")
print("-" * 78)

# RoofCollapseUtility.RoofMaxSupportDistance is 6.9 in the installed assembly.
ROOF_SUPPORT = 6.9
check("the pillar spacing is inside Core's own roof support distance",
      PILLAR_SPACING <= ROOF_SUPPORT,
      "-- RoofCollapseUtility.RoofMaxSupportDistance is %.1f; a lattice coarser than that leaves "
      "roofed cells out of reach of anything holding roof. Found %d"
      % (ROOF_SUPPORT, PILLAR_SPACING))

check("a room only gets pillars once it is wider than a roof spans unaided",
      PILLAR_THRESHOLD >= ROOF_SUPPORT and PILLAR_THRESHOLD <= ROOF_SUPPORT * 2 + 1,
      "-- below twice the support distance a room needs nothing; PillarThreshold is %d"
      % PILLAR_THRESHOLD)

sealed_at = []
for depth, slots, spacing, span, chain, _, _, _, _ in profile:
    if span <= PILLAR_THRESHOLD:
        continue
    low, high = 0, span - 1
    columns = list(range(low + PILLAR_SPACING, high - PILLAR_SPACING + 1, PILLAR_SPACING))
    if not columns:
        continue
    runs = ([columns[0] - low] +
            [columns[i + 1] - columns[i] - 1 for i in range(len(columns) - 1)] +
            [high - columns[-1]])
    if min(runs) < 1:
        sealed_at.append((depth, min(runs)))
check("THE PILLAR LATTICE NEVER SEALS A ROOM",
      not sealed_at,
      "-- a pillar row with no gap beside it cuts a room in half, and CandidateIsSafe would then "
      "reject every candidate and the coordinate would never generate: %s" % sealed_at)

check("THE LATTICE IS DECIDED IN EXACTLY ONE PLACE",
      "internal static IEnumerable<IntVec3> PillarCells(RoomRecord room)" in planner
      and "RoomLayoutPlanner.PillarCells(room)" in genstep
      and "foreach (IntVec3 pillar in PillarCells(room))" in planner,
      "-- the generator spawns them and CandidateIsSafe proves the room is still walkable with "
      "them in it. Two independent derivations of the same lattice is precisely the defect that "
      "stopped every coordinate generating for thirty-nine checkpoints")

check("no pillar is placed on the centre cross",
      "if (x == center.x || z == center.z) { continue; }" in planner,
      "-- doors and corridors meet a room at the midpoint of each wall, so a straight walk from "
      "any doorway to any other must never be blocked, whatever the room's size")

check("the lone centre support is gone",
      "PlaceWall(map, room.Bounds.CenterCell, wallDef, wallStuff);" not in genstep,
      "-- right for a 14-cell room, pointless in an 80-cell one, and it sat on the centre cross "
      "the lattice now leaves clear")


print("")
print("what stopped being a constant")
print("-" * 78)

check("THE FIXED 19-CELL SLOT SPACING IS GONE FROM THE VALIDATOR",
      "Math.Abs(a.z - b.z) == 19" not in service and "Math.Abs(a.x - b.x) == 19" not in service,
      "-- AreGridNeighbors carried the old spacing as a literal. A validator holding a constant "
      "the planner no longer uses is the same defect class as the light count")

check("adjacency is now a property of the rooms, not of a magic number",
      "if (first.Bounds.Overlaps(second.Bounds)) { return false; }" in service
      and "if (a.x == b.x) { return a.z != b.z; }" in service,
      "-- what BuildCorridors actually needs: a shared row or column and a straight run of rock "
      "between them")

check("the slot grid is a function of depth",
      "internal static int SlotsPerAxis(int depth)" in planner
      and "MIN_SLOTS_PLACEHOLDER" not in planner
      and "private static readonly int[,] Grid" not in planner,
      "-- the hard-coded 3x3 eight-slot table is gone")

check("the room size clamp follows the slot instead of a literal",
      "private static int Clamp(int value, int span)" in planner
      and "value > span ? span : value" in planner,
      "-- it was 8..17, because rooms sat 19 apart; the spacing is depth-derived now and so is "
      "the clamp")

check("the family rules split into unique and repeating",
      "UniqueFamilies" in service and "RepeatingFamilies" in service
      and "AtLeastOnceFamilies" in service
      and "RequiredFamilies" not in service and "OptionalFamilies" not in service,
      "-- threshold_room, office_copy and return_gallery stay unique because something depends "
      "on there being exactly one; the rest repeat across the warren")

check("service_passage is still guaranteed to exist",
      'AtLeastOnceFamilies = { "service_passage" }' in service,
      "-- the generator's climate room is FirstOrDefault(utility_room) ?? First(service_passage), "
      "and the second half of that throws when there is none")

check("REGION REBUILDING IS SUSPENDED WHILE THE ROCK IS PLACED",
      "map.regionAndRoomUpdater.Enabled = false;" in genstep
      and "finally { map.regionAndRoomUpdater.Enabled = updaterWasEnabled; }" in genstep,
      "-- up to %d cells of rock now, where it used to be 3,600. Core's own GenStep_RocksFromGrid "
      "does the same thing for the same reason, and the finally is what stops a throw mid-fill "
      "from leaving the map with region updates switched off" % (MAP_W * MAP_H))


print("")
print("THE BACKROOMS DO NOT CAVE IN, AND ONLY THE BACKROOMS")
print("-" * 78)

# Owner direction, 2026-09-30, verbatim: *"and remember backrooms can not and shall not have cave
# ins so removing walls floors columns shall not cause mountain overhead to column collapse"*,
# scoped the same minute to *"tgis is only for backrooms"*.
#
# Core gates every cave-in on RoofDef.canCollapse, in
# RoofCollapseCellsFinder.ProcessRoofHolderDespawned. It DEFAULTS TO TRUE and Core sets it false
# on none of its three roofs, so RoofRockThick collapses like anything else -- dropping
# CollapsedRocks and crushing what stands beneath.
roofs = read(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                          "RoofDefs", "RR_Roofs.xml"))
containment = read(os.path.join(SRC, "Generation", "BackroomsContainment.cs"))

check("A COORDINATE ROOF OF OUR OWN EXISTS AND CANNOT COLLAPSE",
      "<defName>RR_RoofBackroomsOverhead</defName>" in roofs
      and "<canCollapse>false</canCollapse>" in roofs,
      "-- RoofDef.canCollapse defaults to TRUE and Core sets it false on none of its three "
      "roofs, so overhead mountain caves in like anything else")

check("it is still overhead mountain in every way Core measures",
      "<isThickRoof>true</isThickRoof>" in roofs and "<isNatural>true</isNatural>" in roofs,
      "-- drop pods, projectiles, bombardment, RoomTempTracker, Fire, turret line of fire, the "
      "indoor mask, the lighting overlay and Designator_AreaNoRoof all read isThickRoof rather "
      "than the def's identity, which is why a roof of our own behaves identically. Invariant 13 "
      "needs that: a Backrooms coordinate has no outside")

check("CORE'S OWN ROOF IS NOT PATCHED, BECAUSE THIS IS ONLY FOR THE BACKROOMS",
      not any("RoofRockThick" in read(os.path.join(REPO, "Mod", "Rimrooms - Async Industries",
                                                   "1.6", "Patches", name))
              for name in os.listdir(os.path.join(REPO, "Mod", "Rimrooms - Async Industries",
                                                  "1.6", "Patches"))
              if name.endswith(".xml")),
      "-- owner direction, verbatim: *\"tgis is only for backrooms\"*. Patching RoofRockThick "
      "would stop mountains collapsing in every colony, for this player and for every other mod "
      "in the profile")

check("every roof a coordinate sets comes from the one accessor",
      "internal static RoofDef OverheadRoof" in containment
      and 'GetNamedSilentFail("RR_RoofBackroomsOverhead")' in containment
      and "RoofDefOf.RoofRockThick" not in genstep,
      "-- the generator, the carve, the corridors and the containment sweep all read it, so "
      "there is no site left that can put a collapsing roof on a coordinate")

check("a missing def degrades rather than generating a coordinate with a sky",
      "?? RoofDefOf.RoofRockThick;" in containment,
      "-- the fallback can cave in, which is strictly worse, and still better than an unroofed "
      "coordinate")

check("THE FILE THAT USED TO CALL A CAVE-IN ACCEPTABLE NO LONGER DOES",
      "produces rubble and a collapse exactly as it does under any mountain" not in containment
      and "can not and shall not" in containment,
      "-- that paragraph reasoned from VanishOnCollapse being false, which only means no HOLE "
      "opens; the roof still drops CollapsedRocks. The wording hid the severity")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a coordinate is 300x300, its rooms land inside it at every depth, level zero "
      "is grand and the warren tightens inward, and the pillar lattice that makes a grand space "
      "possible is decided in exactly one place")
