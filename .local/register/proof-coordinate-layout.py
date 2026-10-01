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
      planner.count("if (span % 2 != 0) { span--; }") >= 2,
      "-- a plant that deleted this line passed the computed evenness claim, because the model "
      "was still doing the subtraction itself. A modelled property needs a source claim beside "
      "it -- and there are TWO span sources now, `SlotRoomSpan` and `VariedRoomSpan`, so "
      "counting one of them was satisfied by the other. CellRect.CenterCell is where every door "
      "and corridor is aimed; an odd span moves it off the slot centre")

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

# **THE GRAND PART IS THE ROOM YOU ARRIVE IN, AND THE REST IS MAZE.** Owner, after walking the
# first level that ever generated: *"not enough rooms"*, *"it needs to be more maze liek and scary
# inducing beyond the main starting themed opening room"*, and the resolution of what had looked
# like a contradiction with *"making the 0 level rooms be grand large spaces"*:
#
#   *"the normal yellow backrooms look isnt the whole floor but the main spanw room"*
#
# The previous claim here required depth 1 to be at most eight rooms of at least sixty cells, and
# that is exactly what produced the nine-room warehouse. It refused this change, the refusal sent
# me back to the owner's words, and the words were more precise than the claim.
_hall_span = SPACING_AT_DEPTH_1 * 2 - SLOT_GAP if 'SPACING_AT_DEPTH_1' in dir() else None

check("A FIRST LEVEL IS A MAZE, NOT A WAREHOUSE",
      profile[0][4] >= 18,
      "-- *\"not enough rooms\"*. Depth 1 builds %d rooms; nine on a 300x300 map is a warehouse"
      % profile[0][4])

check("and its rooms are small enough to be rooms rather than halls",
      profile[0][3] <= 48,
      "-- %d cells across. Eighty-cell rooms are what the owner walked through and called not "
      "enough rooms: a handful of them fills the map" % profile[0][3])

check("AND ROOM SIZES ARE ACTUALLY VARIED, not merely variable",
      "internal static int VariedRoomSpan(" in planner
      and planner.count("VariedRoomSpan(spacing, slot, seed, depth)") >= 2,
      "-- defined and called at BOTH room-making sites. A plant swapped the calls back to the "
      "flat span and left the function sitting there, and every claim about variation still held")

# **THE LAMPS ARE HUNG, NOT MERELY HANGABLE.** Owner: *"the main grand themed backrooms universe
# rooms need like a wall light on every column wall used as in the universe of backrooms the basic
# rooms are well lit"*. One light per room, in an eighty-cell hall, is not that. Defined AND
# called -- the fourth time today a claim guarded a definition while a plant deleted the call.
check("A WALL LAMP IS HUNG ON EVERY PILLAR",
      "private static void SpawnPillarLamps(" in genstep
      and "SpawnPillarLamps(map, coordinate, wallDef, lightDef, wallMounted," in genstep,
      "-- one lamp per room left a depth-1 hall with a single sconce in eighty cells")

check("and they are counted as lights, not left for a re-derivation to miss",
      "placedLights.Add(lamp);" in genstep,
      "-- re-deriving how many lights should exist is the defect that stopped every coordinate "
      "generating for thirty-nine checkpoints. What was placed is what is counted")

# **SHAPE REACHES THE FIRST LEVEL AT ALL.** Owner: *"you can have back to back roomes and mazes
# of halways of varied widtchs and lengs ... triangle, octangones, rombones, all the geomentry ...
# not just doors on 4 cosides of nothing but square rooms"*. Three shape systems each opened with
# `depth <= 1` and refused to run, so every room on the level the owner walked was a rectangle
# joined by identical corridors. Distance from the spawn hall is depth now.
check("SHAPE AND WIDTH ARE MEASURED FROM THE SPAWN HALL, NOT FROM THE COORDINATE",
      "internal static int ShapeDepthOf(" in planner
      and "int band = hops / LinksPerShapeBand;" in planner,
      "-- the hall and its neighbours stay square, which is the arrival reading as the one built "
      "thing, and everything past it comes apart")

# ------------------------------------------------------------------ doors to nowhere
# Owner: *"odd contructions of doors walls corners deadends doors to now where not just doors on
# 4 cosides of nothing but square rooms"*. `DoorOpening` was that complaint written as code: an
# opening existed only at the midpoint of a wall facing a linked room.
check("A WALL WITH NOTHING BEHIND IT CAN STILL OPEN",
      "internal static bool FalseOpening(" in planner
      and "return FalseOpening(room, rooms, cell);" in planner,
      "-- defined AND reached from DoorOpening, which is the one function both the validator and "
      "the generator ask. A false door decided anywhere else would be a wall the validator proved "
      "and the generator did not build")

check("it is offset from the centre, because the centre is where a real door goes",
      "int at = low + (high - low) / 3;" in planner,
      "-- a door in the middle of a blank wall reads as a corridor that failed to arrive; a third "
      "along reads as somebody having put a door there")

check("never on the threshold hall",
      "if (room == null || room.index == 0) { return false; }" in planner,
      "-- that is where a player arrives and the one room meant to read as built. The maze starts "
      "after it")

check("and never on a wall that already carries a real doorway",
      "if (side == 0 && other.Bounds.minX > bounds.maxX) { return false; }" in planner,
      "-- two openings in one wall reads as a mistake rather than as a door that goes nowhere")

check("A FALSE OPENING CANNOT DISCONNECT ANYTHING",
      "int walls = (onEastWall ? 1 : 0) + (onWestWall ? 1 : 0)" in planner
      and "if (walls != 1) { return false; }" in planner,
      "-- one wall only, so never a corner, and the cell beyond is rock. It adds a dead end and "
      "removes no route, which is the only property CandidateIsSafe is proving")

# ----------------------------------------------------------------------- lamp tones
# Owner: *"we need more lights and mixedered varies of lights"*.
check("LAMPS DIFFER FROM EACH OTHER, PER INSTANCE",
      "private static void TintLamp(" in genstep
      and "TintLamp(lamp, coordinate, room, pillar);" in genstep,
      "-- CompGlower.GlowColor and GlowRadius are per-instance overrides in Core, the same "
      "mechanism that lights one door blue without touching any other door in the game. Defined "
      "AND called")

check("and the dim one is dimmer, never off",
      "glower.GlowRadius = glower.GlowRadius * 2f / 3f;" in genstep
      and "GlowRadius = 0" not in genstep,
      "-- *\"the basic rooms are well lit\"* is the theme. A dark Backrooms is a different place")

check("MOST LEFTOVER SLOTS BECOME BRANCHES, which is what makes it a maze",
      "% 4 == 3)" in planner,
      "-- owner: *\"it needs to be more maze liek\"*. One slot in three became a branch and the "
      "level read as a corridor with alcoves; three in four is something you can get lost in, and "
      "the quarter left as rock is what keeps it a maze rather than an open floor")

# DEFINED **AND CALLED**. Two plants walked past the first draft of these claims -- one deleted
# the `MakeHall` call and left the method, the other swapped `VariedRoomSpan` back to the flat
# one and left the function. **Computing a value correctly and using it are two different facts**,
# and that is the third time today the same gap has been found by running the plants.
check("THE THRESHOLD IS STILL A GRAND HALL, AND IT IS THE ONLY ONE",
      "private static RoomRecord MakeHall(" in planner
      and "rooms.Add(MakeHall(coordinate, order[0], order[1], spacing, seed, depth));" in planner
      and "spacing * 2 - SlotGap" in planner,
      "-- *\"the normal yellow backrooms look isnt the whole floor but the main spanw room\"*. "
      "It spans two slots, so at depth 1 it is about eighty cells across -- the span the whole "
      "level used to have -- while everything past it is about a third of that")

check("the hall takes TWO slots and not four, which is what keeps the chain connected",
      "consumed = 2;" in planner,
      "-- the serpentine exists so consecutive rooms are always grid neighbours and linking needs "
      "no pathfinding. Consuming two keeps that true; a 2x2 hall breaks the adjacency the whole "
      "layout rests on")

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
      # **BOTH READERS IN THE GENERATOR.** The pillar spawner and the pillar LAMPS both walk
      # this lattice, and a plant that rewrote one of them was satisfied by the other still
      # calling it. Two places deriving the same lattice independently is the defect that
      # stopped every coordinate generating for thirty-nine checkpoints; a lamp hung where no
      # pillar is would be the same mistake wearing a different hat.
      and genstep.count("RoomLayoutPlanner.PillarCells(room)") >= 2
      and "foreach (IntVec3 pillar in PillarCells(room))" in planner,
      "-- the generator spawns them and CandidateIsSafe proves the room is still walkable with "
      "them in it. Two independent derivations of the same lattice is precisely the defect that "
      "stopped every coordinate generating for thirty-nine checkpoints")

# Scoped to PillarCells' own body. Stage three added the SAME guard line to RockIntrusionCells,
# and the plant harness replaces only the first occurrence -- so a plant that deleted the pillar
# guard left the intrusion copy standing and satisfying a whole-file claim. That is the
# duplicate-string trap this project has been caught by before, and it caught this claim the
# moment a second function needed the same rule.
pillar_at = planner.find("internal static IEnumerable<IntVec3> PillarCells(RoomRecord room)")
pillar_body = planner[pillar_at:planner.find(chr(10) + "        }" + chr(10), pillar_at)]     if pillar_at >= 0 else ""
check("no pillar is placed on the centre cross",
      pillar_at >= 0 and "if (x == center.x || z == center.z) { continue; }" in pillar_body,
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
print("rooms are not rectangles and hallways are not one width")
print("-" * 78)

# Owner direction, 2026-09-30, verbatim: *"and everything doesnt have to be square rooms and
# rectangle halways"*.
check("ROCK IS LEFT STANDING INSIDE A ROOM, SO IT IS NOT A RECTANGLE",
      "internal static IEnumerable<IntVec3> RockIntrusionCells(RoomRecord room, int depth)" in planner
      and "RoomLayoutPlanner.RockIntrusionCells(room," in genstep
      and "RoomLayoutPlanner.ShapeDepthOf(coordinate.Rooms, room, coordinateDepth)" in genstep,
      "-- the Bounds stays a rect because the validator, the doors, the corridors and the pillar "
      "lattice all read it. What changed is which cells get CARVED")

intrusion_at = planner.find("internal static IEnumerable<IntVec3> RockIntrusionCells")
intrusion_body = planner[intrusion_at:planner.find(chr(10) + "        }" + chr(10), intrusion_at)] \
    if intrusion_at >= 0 else ""

check("THE CENTRE CROSS IS NEVER FILLED, WHICH IS WHAT MAKES A SHAPE SAFE",
      intrusion_at >= 0 and "if (x == center.x || z == center.z) { continue; }" in intrusion_body,
      "-- doors are placed at the midpoint of each side and corridors aim at CenterCell, so a "
      "clear centre cross means every doorway reaches every other doorway WHATEVER shape the "
      "corners take. That is why no candidate is ever rejected for its shape")

check("rock is left only in the corners, inset from the walls",
      intrusion_at >= 0
      and "if (x <= bounds.minX + 1 || x >= bounds.maxX - 1) { continue; }" in intrusion_body
      and "if (z <= bounds.minZ + 1 || z >= bounds.maxZ - 1) { continue; }" in intrusion_body,
      "-- the perimeter is wall and the ring inside it is the walkway that keeps every doorway "
      "reachable")

check("the reach of a corner mass can never eat the middle of the room",
      "/ 3" in intrusion_body and "Math.Min" in intrusion_body,
      "-- clamped to a third of the room, so even at the deepest band a shape is an intrusion "
      "rather than a partition")

check("SHALLOW COORDINATES STAY RECTANGULAR",
      "if (room == null || depth <= 1) { yield break; }" in intrusion_body,
      "-- the yellow rooms read as a place precisely because they are monotonous, which is the "
      "same reason Derange leaves depth 1 alone. The wrongness is travelled toward")

# **BOTH READERS PASS THE SAME SHAPING DEPTH.** This used to assert that the generator passed
# `coordinateDepth` and the validator passed `depth` -- which is precisely what kept every shape
# system off at depth 1. The property was never the parameter name; it was that the room the
# validator proves walkable is the room that gets built.
check("the shape is decided in one place, like the pillars",
      planner.count("internal static IEnumerable<IntVec3> RockIntrusionCells") == 1
      and "foreach (IntVec3 rock in RockIntrusionCells(room, ShapeDepthOf(rooms, room, depth)))"
      in planner
      and genstep.count("RoomLayoutPlanner.RockIntrusionCells(room,") == 1
      and planner.count("internal static int ShapeDepthOf(") == 1,
      "-- the generator leaves these cells uncarved and CandidateIsSafe marks them unwalkable; "
      "two derivations of one rule is the defect that cost thirty-nine checkpoints")

# Scoped to the CARVE LOOP's own body. `SetRoof(cell, overheadRoof)` appears twice in this file --
# once in the base pass over every cell, once here - so a plant that reordered these two lines
# passed a claim that compared `find()` results across the whole file: the first hit was the base
# pass, hundreds of lines earlier, and the comparison was of the wrong pair.
carve_at = genstep.find("var intrusions = new HashSet<IntVec3>(")
carve_body = genstep[carve_at:genstep.find(chr(10) + "            }", carve_at)]     if carve_at >= 0 else ""
check("an intrusion is rock inside a room, never a hole in the world",
      carve_at >= 0
      and "map.roofGrid.SetRoof(cell, overheadRoof);" in carve_body
      and "if (intrusions.Contains(cell)) { continue; }" in carve_body
      and carve_body.find("map.roofGrid.SetRoof(cell, overheadRoof);") <
          carve_body.find("if (intrusions.Contains(cell)) { continue; }"),
      "-- the roof is set BEFORE the skip, so an uncarved cell is still roofed and invariant 13 "
      "holds across every shape")

check("HALLWAYS ARE NOT ALL ONE WIDTH",
      "internal static int CorridorHalfWidthBetween(RoomRecord first, RoomRecord second, int depth)"
      in planner
      and "RoomLayoutPlanner.CorridorHalfWidthBetween(room, other," in genstep
      and "RoomLayoutPlanner.ShapeDepthOf(rooms, room, depth)" in genstep
      and "private const int CorridorHalfWidth" not in genstep,
      "-- the constant is gone; the width comes from the shared function, so the reachability "
      "the planner proved is the reachability that gets built")

check("the planner models the same corridor width the generator carves",
      "int reach = CorridorHalfWidthBetween(room, other," in planner
      and "ShapeDepthOf(rooms, room, depth)" in planner
      and "for (int dz = -reach; dz <= reach; dz++)" in planner,
      "-- a model with a different width than the build is a model of a different map")

# The shape rule, modelled: fill every corner at the deepest reach and prove the room still
# flood-fills from its centre to all four edge midpoints, which is where the doors are.
def room_still_connected(span, depth):
    inset_x, inset_z = 2, 2
    extent_x, extent_z = span - 3, span - 3
    if extent_x - inset_x < 4 or extent_z - inset_z < 4:
        return True
    reach = min((depth - 1) * 2, min(extent_x - inset_x, extent_z - inset_z) // 3)
    if reach < 1:
        return True
    cx, cz = span // 2, span // 2
    rock = set()
    for east in (False, True):
        for north in (False, True):
            for dx in range(reach):
                for dz in range(reach):
                    if dx * dx + dz * dz > reach * reach:
                        continue
                    x = extent_x - dx if east else inset_x + dx
                    z = extent_z - dz if north else inset_z + dz
                    if x == cx or z == cz:
                        continue
                    if x <= 1 or x >= span - 2 or z <= 1 or z >= span - 2:
                        continue
                    rock.add((x, z))
    # Interior floor is every non-perimeter cell that is not rock.
    floor = set((x, z) for x in range(1, span - 1) for z in range(1, span - 1)
                if (x, z) not in rock)
    seen = set([(cx, cz)])
    queue = [(cx, cz)]
    while queue:
        x, z = queue.pop()
        for nx, nz in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
            if (nx, nz) in floor and (nx, nz) not in seen:
                seen.add((nx, nz))
                queue.append((nx, nz))
    doors = [(cx, 1), (cx, span - 2), (1, cz), (span - 2, cz)]
    return all(door in seen for door in doors)


broken = []
for depth, _slots, _spacing, span, _chain, _lo, _hi, _gap, _adj in profile:
    if not room_still_connected(span, depth):
        broken.append((depth, span))
check("NO SHAPE CAN EVER DISCONNECT A DOORWAY, AT ANY DEPTH",
      not broken,
      "-- modelled by filling every corner at the deepest reach and flood-filling from the room "
      "centre to all four edge midpoints, which is where the doors are: %s" % broken)

print("")
print("HOW MANY PLACES MAY BE HELD OPEN AT ONCE")
print("-" * 78)

# Owner direction, 2026-09-30, verbatim: *"dont let them go more than 5 remember the games
# mechanics and limits built in if they find a gate to a world map tile or a deeper backrroms and
# they have 5 mpas they should gett a warning this gate is blocked your holding open too many
# gates, but per scerio styled"*, clarified by *"5 is the limit of other colonies available so a
# backrooms level should be one colonly bacskicly in my thinking"*.
budget = read(os.path.join(SRC, "Portals", "OpenMapBudget.cs"))
frontier = read(os.path.join(SRC, "Portals", "NaturalFrontierService.cs"))
startdef = read(os.path.join(SRC, "Scenario", "RimroomsStartDef.cs"))
keyed = read(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                          "English", "Keyed", "RR_Portals.xml"))
parent = read(os.path.join(SRC, "Generation", "RimroomsDestinationMapParent.cs"))

# The method body alone. `return false;` appears several times in this file -- CanBeSettled,
# GravShipCanLandOn, InitializeCoordinate -- so a plant that flipped THIS one to true left the
# string present elsewhere and the claim satisfied.
remove_at = parent.find("public override bool ShouldRemoveMapNow(out bool alsoRemoveWorldObject)")
remove_body = parent[remove_at:parent.find(chr(10) + "        }", remove_at)] \
    if remove_at >= 0 else ""
check("A COORDINATE MAP IS STILL NEVER UNLOADED, WHICH IS WHY A CAP IS NEEDED AT ALL",
      remove_at >= 0 and "return false;" in remove_body and "return true;" not in remove_body,
      "-- a coordinate is a place you can go back to. That was free at 60x60 and is not at "
      "300x300, and the cap is what replaced the eviction the owner first asked for and then "
      "superseded")

# The BODY of the Budget property, comments stripped. The first version of this claim read the
# whole file and passed a plant that replaced the pref with a literal 5 in the code -- because the
# pref's NAME is also in the doc comment directly above it. A comment satisfied a claim about code.
budget_code = re.sub(r"///.*", "", budget)
budget_code = re.sub(r"//.*", "", budget_code)
budget_at = budget_code.find("internal static int Budget")
budget_body = budget_code[budget_at:budget_code.find(chr(10) + "        }", budget_at)] \
    if budget_at >= 0 else ""
check("THE BUDGET IS READ FROM THE GAME'S OWN COLONY LIMIT, NOT HARD-CODED",
      budget_at >= 0
      and "Prefs.MaxNumberOfPlayerSettlements" in budget_body
      and not re.search(r":\s*\d+\s*;", budget_body),
      "-- *\"remember the games mechanics and limits built in\"*. Core enforces that pref in "
      "SettleUtility as count >= Prefs.MaxNumberOfPlayerSettlements, and it is a 1-to-5 player "
      "slider, so a player who moves it to 3 gets 3")

check("a scenario may set its own budget, which is what per-scenario means",
      "public int openMapBudget;" in startdef
      and "part.startDef.openMapBudget" in budget
      and "scenario > 0 ? scenario" in budget,
      "-- *\"but per scerio styled\"*; zero defers to the player's own limit")

check("THE BUDGET HAS A FLOOR, OR THE SOLO START BREAKS ON A CLEAN NEW GAME",
      "MinimumBudget = 2" in budget and "Mathf.Max(MinimumBudget, budget)" in budget,
      "-- the pref can be set to 1, and the solo/group start opens a coordinate during "
      "PostGameStart when the surface map already counts as one held place. Without the floor "
      "that scenario would refuse its own opening")

check("a Backrooms level counts against the budget exactly as a colony does",
      "map.Parent is Generation.RimroomsDestinationMapParent) { held++; }" in budget
      and "map.IsPlayerHome && map.Parent is Settlement) { held++; }" in budget,
      "-- *\"a backrooms level should be one colonly bacskicly in my thinking\"*. Core's own "
      "count cannot see a coordinate map, so this counts both")

# The ORDER of the two checks inside Discover is the whole argument, so it is measured as an
# ordering rather than as the presence of a call.
way_out_at = frontier.find("CompanyActionResult wayOut = TryRecordWayOut(door, origin, campaign);")
block_at = frontier.find("if (!OpenMapBudget.CanOpenAnother)")
mint_at = frontier.find("campaign.CreateDiscoveredCoordinate(discoveryId, depth, out discovered)")
check("A BLOCKED GATE IS REFUSED BEFORE ANY COORDINATE IS MINTED",
      block_at >= 0 and mint_at >= 0 and block_at < mint_at,
      "-- minting one and then refusing would leave a place nobody can reach recorded against "
      "the branch. Block at %d, mint at %d" % (block_at, mint_at))

check("THE BUDGET NEVER CLOSES THE LAST DOOR HOME",
      way_out_at >= 0 and block_at >= 0 and way_out_at < block_at,
      "-- a doorway may lead OUT instead of deeper, and a way home costs no map: it records a "
      "world tile rather than minting a place. Checking the budget first would strand a crew "
      "that is deep and full up, which is the same trap the depth cap is ordered to avoid. "
      "Way-out at %d, budget at %d" % (way_out_at, block_at))

check("the one place a coordinate map is generated also enforces it",
      "coordinate.Site == null && !Portals.OpenMapBudget.CanOpenAnother" in service,
      "-- the doorway refusal is where a player should be TOLD; this is the backstop for a "
      "machine gate, a saved address or a recovery path. Only when a NEW map would be made: "
      "recalling a coordinate that already has its site must never be refused")

check("the refusal says what the owner said",
      "<RR_Frontier_TooManyGatesHeld>" in keyed
      and "</RR_Frontier_TooManyGatesHeld>" in keyed
      and "holding open too many gates" in keyed
      and 'BlockedKey = "RR_Frontier_TooManyGatesHeld"' in budget,
      "-- *\"they should gett a warning this gate is blocked your holding open too many "
      "gates\"*, and the message names the way out of it")

frontiers_at = frontier.find("internal static int FrontiersFor(CoordinateRecord coordinate)")
frontiers_body = frontier[frontiers_at:frontier.find(chr(10) + "        }", frontiers_at)] \
    if frontiers_at >= 0 else ""
check("WAYS ONWARD SCALE WITH THE SIZE OF THE PLACE",
      "MinimumFrontiersPerCoordinate = 4" in frontier
      and "MaximumFrontiersPerCoordinate = 6" in frontier
      and "Cap = FrontiersFor(record)" in frontier
      and "coordinate.Rooms.Count" in frontiers_body
      and "Depth" not in frontiers_body,
      "-- owner direction: four to six per level. Two was right for a six-room 60x60 coordinate "
      "and wrong for a 300x300 one")

check("THE CEILING ON WAYS ONWARD IS ACTUALLY APPLIED, NOT MERELY DECLARED",
      frontiers_at >= 0 and "MaximumFrontiersPerCoordinate" in frontiers_body,
      "-- a plant that deleted the clamp while leaving the constant walked past the first "
      "version of this, which only asked whether the constant existed. A chain of spaces still "
      "has to be finite")

depth_reach = re.search(r"MaximumNaturalDepth\s*=\s*(\d+)", frontier)
check("the natural chain reaches deeper than it did",
      depth_reach is not None and int(depth_reach.group(1)) >= 6,
      "-- raised from 3 to %s, together with the budget that makes a deeper chain affordable"
      % (depth_reach.group(1) if depth_reach else "MISSING"))

print("")
print("LETTING A PLACE GO, SO A MACHINE GATE CAN AIM DEEPER")
print("-" * 78)

# Owner direction, 2026-09-30: *"yeah so if the player discovers and goes through a natural gate
# how do they turn them off to use the machine gates for more controll and aiming deeper?"*, and
# the trap named: *"get 5 natural gates u cant use a machine gate"*. They chose an Operations
# held-places list with a Release button.
release = read(os.path.join(SRC, "Generation", "CoordinateRelease.cs"))
records = read(os.path.join(SRC, "Company", "CampaignRecords.cs"))
emergence = read(os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs"))
places = read(os.path.join(SRC, "UI", "OperationsHeldPlaces.cs"))
network = read(os.path.join(SRC, "Portals", "RimroomsPortalNetwork.cs"))
optabs = read(os.path.join(SRC, "UI", "MainTabWindow_Operations.cs"))

# COUNTED, because the call appears TWICE in that file -- natural and machine registration each
# generate the site -- and the plant harness replaces only the first. A presence test passed a
# plant that removed one of them. Same duplicate-string trap, and it is the most recurrent
# failure mode this project has.
address = read(os.path.join(SRC, "Portals", "PortalAddressService.cs"))
ensure_calls = address.count("DestinationService.EnsureSite(campaign, coordinate, out siteMap, out siteEntry)")
check("THE TRAP IS REAL: A DISCOVERY COSTS A SLOT IMMEDIATELY",
      ensure_calls == 2,
      "-- RegisterNaturalAddress generates the site AT DISCOVERY, because a natural edge is "
      "registered against the far side's own ReturnAnchor and that Thing does not exist until the "
      "map does. The previous checkpoint's record claimed discovery was free; it was wrong, and "
      "the budget check in Discover is load-bearing rather than over-eager. Found %d of the 2 "
      "expected registration paths" % ensure_calls)

check("a deliberate release is written down in the save",
      "internal bool releasedByPlayer;" in records
      and 'Scribe_Values.Look(ref releasedByPlayer, "rr_releasedByPlayer", false);' in records,
      "-- a released coordinate has no site and surveyed rooms, which is byte-for-byte what a "
      "broken reference looks like. Only a flag can tell them apart")

check("THE EXEMPTION IS THE ONLY WAY PAST THE EXPLORED-GRAPH GUARD",
      "bool releasedAndRebuildable = coordinate.releasedByPlayer &&" in service
      and "if (!releasedAndRebuildable && coordinate.Site == null && (coordinate.Status == CoordinateStatus.Ready"
      in service,
      "-- the guard exists so a broken reference cannot replace an already explored graph, and "
      "that is still exactly right for a fault")

check("and it still refuses a competing owner or a live map",
      "!Find.WorldObjects.AllWorldObjects.OfType<RimroomsDestinationMapParent>().Any(owner => owner.CoordinateId == coordinate.Id) &&"
      in service
      and "!Find.Maps.Any(existing => (existing.Parent as RimroomsDestinationMapParent)?.CoordinateId == coordinate.Id)"
      in service,
      "-- those are real conflicts rather than an explored graph, and a release is required to "
      "have removed both")

check("THE EXEMPTION IS SPENT THE MOMENT THE PLACE EXISTS AGAIN",
      "coordinate.releasedByPlayer = false;" in service,
      "-- an exemption that outlives its reason is a hole: it would let a genuinely broken "
      "reference through on some later load")

# The ORDER of the teardown is the whole of its safety, so it is measured as an ordering.
remember_at = release.find("RememberOn(edge.First, coordinate, map);")
forget_at = release.find("network.ForgetConnection(shelved[index].Id);")
teardown_at = release.find("Current.Game.DeinitAndRemoveMap(map, false);")
check("THE DOORS ARE TOLD WHERE THEY LED BEFORE THE EDGES ARE REMOVED",
      remember_at >= 0 and forget_at >= 0 and remember_at < forget_at,
      "-- the edge is the only record of the pairing. Remove it first and the door becomes an "
      "ordinary marked door with the place behind it unreachable for ever. Remember at %d, "
      "forget at %d" % (remember_at, forget_at))

check("AND THE EDGES ARE REMOVED BEFORE THE MAP IS TORN DOWN",
      forget_at >= 0 and teardown_at >= 0 and forget_at < teardown_at,
      "-- every endpoint lives on the map being destroyed, so the other order leaves records "
      "pointing at nothing. Forget at %d, teardown at %d" % (forget_at, teardown_at))

check("the record and its rooms survive the release, so the history is not rewritten",
      "coordinate.site = null;" in release
      and "coordinate.status = CoordinateStatus.Discovered;" in release
      and "Coordinates.Remove" not in release
      and "coordinate.rooms" not in release,
      "-- the record and its rooms survive; only the map and the world object go. A release that "
      "discarded the graph would give the player a different place back")

check("nothing is remembered onto the map being destroyed",
      "anchor.Map == releasing)" in release,
      "-- the far endpoint is about to cease to exist, so writing the pairing onto it would be "
      "writing it onto nothing")

release_at = release.find("internal static string RefusalFor(")
refusal_body = release[release_at:release.find(chr(10) + "        }", release_at)] \
    if release_at >= 0 else ""
for needle, why in [
        ("RR_Release_Headquarters", "the headquarters is not a place you let go of"),
        ("RR_Release_CrewInside", "a released map takes its contents with it, people included"),
        ("RR_Release_CrossingInFlight", "invariant 55: nobody may be part-way through"),
        ("RR_Release_NotHeldOpen", "a place with no live map has nothing to release")]:
    check("release refuses: " + needle, release_at >= 0 and needle in refusal_body, "-- " + why)

check("A PRISONER OR AN ANIMAL COUNTS AS SOMEBODY INSIDE",
      "pawn.Faction == Faction.OfPlayer || pawn.IsPrisonerOfColony" in refusal_body,
      "-- colonists are not the only thing the player would lose")

check("the network's one removal is narrow and deliberate",
      "internal bool ForgetConnection(string connectionId)" in network
      and network.count("connections.Remove") == 1,
      "-- the load path forbids silently removing an edge, because a broken-looking edge is "
      "evidence. This is neither silent nor a fault: the player asked, and every endpoint is "
      "about to stop existing")

check("THE DOOR REMEMBERS WHERE IT LED, AND IT IS SAVED",
      "private string shelvedCoordinateId;" in emergence
      and 'Scribe_Values.Look(ref shelvedCoordinateId, "rr_emergenceShelvedCoordinate");' in emergence
      and "emergence.RememberShelvedPlace(coordinate.Id);" in release,
      "-- a natural gate is permanently open and is never closed; what is released is the space "
      "behind it, and the door is the only thing left that knows which space")

# **CLOSING A NATURAL PORTAL IS ONE-WAY, AND THAT IS WHAT THE FIVE-MAP LIMIT IS FOR.**
# Owner: *"we do need to be able to close natural portals u just can not re open them"* and
# *"thats the whole 5 limit issue"*.
#
# These claims used to describe the SHAPE of a re-open. Three of them still held after the gizmo
# was removed, because the method they inspected had been left behind as dead code -- a proof
# passing by reading something unreachable, which reports a feature that cannot happen.
check("NOTHING RE-OPENS A RELEASED PLACE",
      "private CompanyActionResult Reopen(" not in emergence
      and "RR_Release_ReopenLabel" not in emergence,
      "-- a slot is freed by a decision that cannot be undone. A decision that can be undone is "
      "not a decision, and the limit would not bite")

check("and the method is deleted rather than orphaned",
      "Reopen(" not in emergence,
      "-- dead code that no gizmo reaches is exactly what a `...Unused` rename hides. If it is "
      "not reachable it should not be here")

check("THE DOOR STILL REMEMBERS WHERE IT LED, as a record and not an offer",
      "shelvedCoordinateId" in emergence and "RememberShelvedPlace" in emergence
      # The ACCESSOR by its exact signature, not just the backing field: a plant renamed the
      # property to `...Unused` and the field-only test stayed satisfied. The prefix trap, again.
      and "internal string ShelvedCoordinateId { get" in emergence,
      "-- a player standing in front of a spent door needs to know it was a way through. Losing "
      "the memory would make a released place indistinguishable from a door that never led "
      "anywhere")

check("THE HELD-PLACES PANE EXISTS AND IS REACHABLE",
      "private void DrawHeldPlaces(Listing_Standard listing, RimroomsCampaignComponent campaign)"
      in places
      and "case 12: DrawHeldPlaces(listing, campaign); break;" in optabs
      and '"RR_UI_Places"' in optabs
      and "HelpPane = 13" in optabs,
      "-- a pane nothing dispatches to is the defect check-wiring exists for, and the help pane "
      "index moves with it or help opens the places list")

check("it shows the colonies too, because they are the other half of the budget",
      "map.IsPlayerHome &&" in places and "RR_Release_ColonyRow" in places,
      "-- a player counting slots needs to see why three of five are gone before they blame the "
      "Backrooms")

check("the release is confirmed and the loss is counted first",
      "ItemsLeftBehind" in places and "destructive: true" in places
      and "RR_Release_Confirm" in places,
      "-- the interior regenerates from its seed, so anything left inside is gone; that is the "
      "honest price of not holding it open and the player is told the number")

check("NEITHER OUTCOME IS SILENT",
      "RR_Release_Failed" in places and "RR_Release_Done" in places,
      "-- the player pressed a button to free a slot, and a slot either was or was not freed")

release_keys = ["RR_Release_Heading", "RR_Release_Budget", "RR_Release_Button",
                "RR_Release_Confirm", "RR_Release_Done", "RR_Release_Failed",
                "RR_Release_Blocked", "RR_Release_Inactive", "RR_Release_UnknownPlace",
                "RR_Release_NotHeldOpen", "RR_Release_Headquarters", "RR_Release_CrewInside",
                "RR_Release_CrossingInFlight",
                "RR_Event_CoordinateReleased", "RR_UI_Places"]
missing_keys = [key for key in release_keys if ("<" + key + ">") not in keyed]
check("every release string the player can meet is written",
      not missing_keys,
      "-- a refusal the player cannot read is a silent failure: %s" % missing_keys)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: a coordinate is 300x300, its rooms land inside it at every depth, level zero "
      "is grand and the warren tightens inward, and the pillar lattice that makes a grand space "
      "possible is decided in exactly one place")
