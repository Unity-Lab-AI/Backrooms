# -*- coding: utf-8 -*-
"""Plant a fault, run the coordinate-layout proof, require exit 1, restore. Verified writes."""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
PLANNER = SRC + "/Generation/RoomLayoutPlanner.cs"
SERVICE = SRC + "/Generation/DestinationService.cs"
GEN = SRC + "/Generation/GenStep_BackroomsDestination.cs"
CONTAIN = SRC + "/Generation/BackroomsContainment.cs"
ROOFS = "Mod/Rimrooms - Async Industries/1.6/Defs/RoofDefs/RR_Roofs.xml"
PATCH = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_StartGenSteps.xml"
PROOF = ".local/register/proof-coordinate-layout.py"
NL = chr(10)

PLANTS = [
    # ------------------------------------------------------------------ the size
    ("THE COORDINATE SHRINKS BACK TO 60x60", SERVICE,
     "public const int MapWidth = 300;", "public const int MapWidth = 60;"),

    ("a coordinate stops being square", SERVICE,
     "public const int MapHeight = 300;", "public const int MapHeight = 260;"),

    # ------------------------------------------------------------------ the geometry
    ("THE MARGIN GOES NEGATIVE AND ROOMS FALL OFF THE MAP", PLANNER,
     "internal const int Margin = 14;", "internal const int Margin = -60;"),

    ("the slot gap closes and rooms share a wall", PLANNER,
     "internal const int SlotGap = 10;", "internal const int SlotGap = 0;"),

    ("ROOM SPANS STOP BEING EVEN AND DOORS MISS THE SLOT CENTRE", PLANNER,
     "            if (span % 2 != 0) { span--; }" + NL, ""),

    ("depth stops changing the slot grid", PLANNER,
     "internal const int MaxSlotsPerAxis = 8;", "internal const int MaxSlotsPerAxis = 3;"),

    ("THE WARREN STOPS TIGHTENING INWARD", PLANNER,
     "internal const int MaxRooms = 60;", "internal const int MaxRooms = 6;"),

    ("level zero stops being grand", PLANNER,
     "internal const int MinSlotsPerAxis = 3;", "internal const int MinSlotsPerAxis = 7;"),

    # ---------------------------------------- the formulas the proof's model only copies
    ("the spacing formula stops dividing by the slot count", PLANNER,
     "return (DestinationService.MapWidth - Margin * 2) / slots;",
     "return DestinationService.MapWidth - Margin * 2;"),

    ("a slot centre stops accounting for the slot index", PLANNER,
     "return Margin + spacing / 2 + spacing * index;",
     "return Margin + spacing / 2;"),

    ("the span stops leaving a gap for a corridor", PLANNER,
     "int span = spacing - SlotGap;", "int span = spacing;"),

    ("THE SERPENTINE STOPS ALTERNATING AND THE CHAIN JUMPS THE GRID", PLANNER,
     "int x = row % 2 == 0 ? column : slots - 1 - column;", "int x = column;"),

    ("the chain takes the whole grid and leaves no rock between its arms", PLANNER,
     "order.Count * 2 / 3", "order.Count"),

    ("the slot count stops rising with depth", PLANNER,
     "int slots = MinSlotsPerAxis + (depth < 1 ? 0 : depth - 1);",
     "int slots = MinSlotsPerAxis;"),

    # ------------------------------------------------------------------ the pillars
    ("THE PILLAR LATTICE OPENS PAST CORE'S ROOF SUPPORT DISTANCE", PLANNER,
     "internal const int PillarSpacing = 6;", "internal const int PillarSpacing = 20;"),

    ("a pillar lattice tight enough to seal a room", PLANNER,
     "internal const int PillarSpacing = 6;", "internal const int PillarSpacing = 1;"),

    ("small rooms start getting pillars they do not need", PLANNER,
     "internal const int PillarThreshold = 13;", "internal const int PillarThreshold = 4;"),

    ("A PILLAR LANDS ON THE CENTRE CROSS AND CAN BLOCK A DOORWAY", PLANNER,
     "                    if (x == center.x || z == center.z) { continue; }" + NL, ""),

    ("THE GENERATOR DERIVES ITS OWN LATTICE INSTEAD OF SHARING ONE", GEN,
     "foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))",
     "foreach (IntVec3 pillar in new List<IntVec3> { room.Bounds.CenterCell })"),

    ("the lone centre support comes back", GEN,
     "                foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))",
     "                PlaceWall(map, room.Bounds.CenterCell, wallDef, wallStuff);" + NL
     + "                foreach (IntVec3 pillar in RoomLayoutPlanner.PillarCells(room))"),

    # ------------------------------------------------------------------ the constants that went
    ("THE FIXED 19-CELL SPACING COMES BACK INTO THE VALIDATOR", SERVICE,
     "            if (a.x == b.x) { return a.z != b.z; }",
     "            if (a.x == b.x) { return Math.Abs(a.z - b.z) == 19; }"),

    ("the hard-coded slot table comes back", PLANNER,
     "        internal static bool TrySelect(CoordinateRecord coordinate, out List<RoomRecord> selected)",
     "        private static readonly int[,] Grid = { { 0, 0 }, { 1, 0 } };" + NL + NL
     + "        internal static bool TrySelect(CoordinateRecord coordinate, out List<RoomRecord> selected)"),

    ("the room clamp goes back to a literal", PLANNER,
     "        private static int Clamp(int value, int span)",
     "        private static int ClampUnused(int value, int span)"),

    ("the family split reverts to required and optional", SERVICE,
     "        private static readonly string[] UniqueFamilies =",
     "        private static readonly string[] RequiredFamilies = { \"x\" };" + NL + NL
     + "        private static readonly string[] UniqueFamilies ="),

    ("service_passage stops being guaranteed", SERVICE,
     'AtLeastOnceFamilies = { "service_passage" }', 'AtLeastOnceFamilies = { "survey_lobby" }'),

    # ------------------------------------------------------------------ the rock fill cost
    ("REGION REBUILDING RUNS DURING THE 90,000-CELL ROCK FILL", GEN,
     "            map.regionAndRoomUpdater.Enabled = false;" + NL, ""),

    ("a throw mid-fill would leave region updates switched off", GEN,
     "            finally { map.regionAndRoomUpdater.Enabled = updaterWasEnabled; }",
     "            finally { }"),

    # ------------------------------------------------------------------ no cave-ins
    ("THE BACKROOMS START CAVING IN AGAIN", ROOFS,
     "<canCollapse>false</canCollapse>", "<canCollapse>true</canCollapse>"),

    ("the coordinate roof stops being overhead mountain", ROOFS,
     "<isThickRoof>true</isThickRoof>", "<isThickRoof>false</isThickRoof>"),

    ("the coordinate roof def is renamed out from under the accessor", ROOFS,
     "<defName>RR_RoofBackroomsOverhead</defName>", "<defName>RR_RoofSomethingElse</defName>"),

    ("CORE'S OWN MOUNTAIN ROOF GETS PATCHED FOR EVERY COLONY", PATCH,
     "</Patch>",
     "  <Operation Class=\"PatchOperationAdd\">" + NL
     + "    <xpath>Defs/RoofDef[defName=\"RoofRockThick\"]</xpath>" + NL
     + "    <value><canCollapse>false</canCollapse></value>" + NL
     + "  </Operation>" + NL + NL + "</Patch>"),

    ("the generator goes back to Core's collapsing roof", GEN,
     "RoofDef overheadRoof = BackroomsContainmentMapComponent.OverheadRoof;",
     "RoofDef overheadRoof = RoofDefOf.RoofRockThick;"),

    ("the accessor loses its fallback", CONTAIN,
     "                    ?? RoofDefOf.RoofRockThick;", "                    ;"),

    ("THE FILE GOES BACK TO CALLING A CAVE-IN ACCEPTABLE", CONTAIN,
     "    /// ## And it does not collapse either, which this file used to get wrong",
     "    /// produces rubble and a collapse exactly as it does under any mountain" + NL
     + "    /// ## And it does not collapse either, which this file used to get wrong"),
]


def write_verified(path, text):
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


print("baseline -- the target must pass before anything is planted")
code = subprocess.call([sys.executable, PROOF],
                       stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
print("  exit %d  %s" % (code, PROOF))
if code != 0:
    sys.stderr.write("BASELINE BROKEN: the proof already fails, so every plant would register "
                     "as caught and the run would prove nothing.\n")
    sys.exit(2)
print("")

caught = 0
for label, path, old, new in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    write_verified(path, original.replace(old, new, 1))
    code = subprocess.call([sys.executable, PROOF],
                           stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
    write_verified(path, original)
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
