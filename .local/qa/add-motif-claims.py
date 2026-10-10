# -*- coding: utf-8 -*-
"""Claims for the composition engine: the motif, the theme bias, and the kinds.

Placed before the exit gate. A claim after `if failures: sys.exit(1)` records a
failure nothing acts on.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-coordinate-layout.py"

GATE = (
    "if failures:" + NL
    + '    print("PROOF FAILED: %d claim(s)" % len(failures))' + NL
    + "    sys.exit(1)" + NL
)

CLAIMS = '''
# ======================================================================================
# A COORDINATE IS A PLACE, NOT A LIST OF ROOMS
#
# Owner, 2026-10-03: *"repeated patternes in variations"*, and at the composition fork
# *"option 3 but keep it not limited to my examples i want you to expand and expound on
# everything in a lsd way"*.
#
# Seven room shapes already existed and **every room rolled its own, independently of every
# other room** -- which is not a pattern, it is noise. Sixteen archetypes were drawn per room
# against their own weight alone, so a coordinate held a classroom beside a weapons locker
# beside a nursery. Neither was a legality fault, so nothing in the battery could see either:
# every form is safe by construction and every archetype is a legal archetype.
# ======================================================================================

motif_raw = read(os.path.join(SRC, "Generation", "CoordinateMotif.cs"))
archetype_service = read(os.path.join(SRC, "Generation", "RoomArchetypeService.cs"))
archetype_def = read(os.path.join(SRC, "Generation", "RimroomsRoomArchetypeDef.cs"))

check("A COORDINATE HAS ONE MOTIF, drawn from its own seed",
      "internal struct CoordinateMotif" in motif_raw
      and "internal static CoordinateMotif For(CoordinateRecord coordinate)" in motif_raw
      and 'StableHash(seed, id + ":motif", depth)' in motif_raw,
      "-- drawn from the saved record and nothing else, so a revisit draws the identical motif "
      "without a save-schema field. **That is what lets the carver and the reachability proof "
      "derive it independently and still agree** -- a motif saved on one side and recomputed on "
      "the other would be two derivations of one rule")

check("and the motif decides a room's shape, in ONE named function both readers use",
      "internal static int ShapeRollFor(RoomRecord room, int depth)" in planner
      and "internal static int ShapeFormOf(RoomRecord room, int depth, CoordinateMotif motif)"
      in planner
      and "int form = ShapeFormOf(room, depth, motif);" in planner
      and "int form = roll % ShapeForms;" not in planner_code,
      "-- it was `roll % ShapeForms`, an independent draw per room. Named rather than inlined so "
      "`check-planner-layouts.py` can MEASURE it: whether a floor reads as a pattern with "
      "variations is a number, and before this nothing could see it -- exactly as nothing could "
      "see the average degree before the probe was taught to count links")

check("AND THE MOTIF LOOSENS WITH DEPTH, which is one number producing both ends of the curve",
      "internal const int StrongestHold = 85;" in motif_raw
      and "internal const int WeakestHold = 25;" in motif_raw
      and "int hold = StrongestHold - (depth - 1) * HoldLostPerDepth;" in motif_raw,
      "-- shallow coordinates are strongly on-motif, and **the monotony is the image the setting "
      "rests on**: the yellow rooms read as a place precisely because they repeat. The deeper a "
      "space is the more often a room departs, so *\\"further in it gets very varied and "
      "weird\\"* is the same number falling rather than a second system. Measured: on-motif "
      "89.3% at depth 1 down to 36.5% at depth 8, with all seven shapes present at every depth "
      "and a random floor sitting at 14.3%")

check("the validator and the carver shape to the SAME motif",
      "RockIntrusionCells(room, ShapeDepthOf(rooms, room, depth), motif)" in planner
      and "private static bool CandidateIsSafe(List<RoomRecord> rooms, int depth, CoordinateMotif motif)"
      in planner
      and "CandidateIsSafe(rooms, DepthOf(coordinate), CoordinateMotif.For(coordinate))" in planner,
      "-- a validator proving a square room the carver then shapes is a validator proving a "
      "different room, which is the defect class that stopped every coordinate generating for "
      "thirty-nine checkpoints. Both derive the motif from the coordinate rather than passing it "
      "along a chain, so neither can be handed a different one")

check("A COORDINATE HAS A THEME, and an archetype carrying it is likelier",
      "internal static readonly string[] Themes" in motif_raw
      and "internal const float ThemeWeightFactor = 3f;" in motif_raw
      and "internal float WeightFor(System.Collections.Generic.List<string> themes)" in motif_raw
      and "* motif.WeightFor(archetype.themes);" in archetype_service,
      "-- archetypes were drawn against their own weight alone, so a coordinate held a classroom "
      "beside a weapons locker beside a nursery: a list of rooms rather than somewhere. **A bias "
      "and never a filter**, deliberately -- a market coordinate holding nothing but shops is a "
      "themed level rather than a Backrooms level, and the wrongness needs the one laboratory in "
      "the shopping centre")

check("and a theme nobody can draw is refused at load, by name",
      "System.Array.IndexOf(CoordinateMotif.Themes, themes[index]) >= 0" in archetype_def
      and "is not one of CoordinateMotif.Themes." in archetype_def,
      "-- a typo in a theme tag is otherwise completely silent: the archetype simply never gets "
      "its bias, and a coordinate meant to read as a market holds shops at the same rate as "
      "everything else. There is no observable symptom at all, which is the worst kind of defect "
      "this project meets")

# **THE THEME LIST IS APPEND-ONLY and that is load-bearing.** The index is drawn from the
# coordinate's seed, so inserting a theme in the middle re-themes every coordinate already
# saved -- a place a player has walked would come back as somewhere else.
check("the theme list is append-only, and says so where somebody would break it",
      "Ordered, and **never reordered**" in motif_raw
      and "Append only." in motif_raw,
      "-- the index comes from the coordinate's seed, so inserting a theme in the middle "
      "re-themes every coordinate already saved. A player's place would come back as somewhere "
      "else, with nothing in the log")

# ---------------------------------------------------------------- the kinds themselves
archetype_xml = read(os.path.join(
    "Mod", "Rimrooms - Async Industries", "1.6", "Defs", "RimroomsRoomArchetypeDefs",
    "RR_RoomArchetypes.xml"))
archetype_count = archetype_xml.count(
    "<RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>")
themed_count = archetype_xml.count("<themes>")
print("archetypes: %d, themed: %d" % (archetype_count, themed_count))

check("EVERY KIND THE OWNER NAMED EXISTS, by name",
      all(name in archetype_xml for name in (
          "RR_Room_MallConcourse", "RR_Room_ShopFront", "RR_Room_Barracks",
          "RR_Room_Checkpoint", "RR_Room_Apartment", "RR_Room_ServiceTunnel",
          "RR_Room_Roadway", "RR_Room_Substation")),
      "-- *\\"rooma corradors facilites infastructure roads neighborrs hood malls shoopping "
      "centers military\\"*: malls and shop fronts, military and checkpoints, neighbourhoods as "
      "apartments, infrastructure as service tunnels and substations, and **roads as a roadway** "
      "-- lane markings, a kerb and lighting at the spacing of a road, indoors and roofed")

check("and they are not the whole of it, which the owner asked for explicitly",
      archetype_count >= 40 and themed_count == archetype_count,
      "-- *\\"but keep it not limited to my examples i want you to expand and expound on "
      "everything in a lsd way\\"*. %d archetypes, every one themed, against seven shapes is "
      "over three hundred distinguishable rooms before a single slot is rolled -- which is how "
      "*\\"hundred s and hundreds\\"* is answered as a PRODUCT of authored parts rather than as "
      "hundreds of authored families" % archetype_count)

check("every archetype still asks for a capability rather than naming furniture",
      "<kind>Explicit</kind>" not in archetype_xml,
      "-- a hand-written list of defNames covers Core, misses every DLC, misses all 294 profile "
      "mods and rots the first time anything is renamed. Not one of the new kinds names a piece "
      "of furniture it hopes exists")

'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(GATE) != 1:
    print("exit gate not found exactly once (%d)" % text.count(GATE))
    sys.exit(1)
io.open(PROOF, "w", encoding="utf-8", newline=NL).write(text.replace(GATE, CLAIMS + GATE))
print("motif and composition claims inserted before the exit gate")
