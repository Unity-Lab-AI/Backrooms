# -*- coding: utf-8 -*-
"""Plant a fault, run the proof, require failure, restore. Verified writes, baseline checked first."""
import io
import os
import subprocess
import sys
import time

SCEN = "src/RimroomsAsyncIndustries/Scenario"
PART = SCEN + "/ScenPart_RimroomsStart.cs"
GEN = SCEN + "/GenStep_Headquarters.cs"
LAYOUT = SCEN + "/HeadquartersLayout.cs"
OPENING = SCEN + "/SoloGroupOpening.cs"
DEF = SCEN + "/RimroomsStartDef.cs"
PAGE = SCEN + "/Page_RimroomsCompanySetup.cs"
STARTS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsStartDefs/RR_Starts.xml"
CHR_NL = chr(10)
PATCHFILE = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_StartGenSteps.xml"
SCENARIOS = "Mod/Rimrooms - Async Industries/1.6/Defs/ScenarioDefs/RR_Scenarios.xml"
ARRIVAL = SCEN + "/ScenPart_RimroomsArrival.cs"
PROOF = ".local/register/proof-startplacement.py"

PLANTS = [
    # ------------------------------------------------------ the map size is the player's
    ("THE MOD STARTS OVERRIDING THE CHOSEN MAP SIZE AGAIN", PART,
     "        public override void PostGameStart()",
     "        public void ForceSize() { Find.GameInitData.mapSize = startDef.mapSize; }\n\n"
     "        public override void PostGameStart()", PROOF),

    # ------------------------------------------------------ 0.12.46-dev: Core owns the generator
    ("THE MOD STARTS CHOOSING THE MAP GENERATOR AGAIN", PART,
     "        public override void PostGameStart()",
     "        public void ForceGen() { Find.GameInitData.mapGeneratorDef = null; }\n\n"
     "        public override void PostGameStart()", PROOF),

    ("a start def names a generator again", STARTS,
     "    <arrivalCell>(30, 0, 23)</arrivalCell>",
     "    <mapGenerator>RR_Headquarters</mapGenerator>\n    <arrivalCell>(30, 0, 23)</arrivalCell>",
     PROOF),

    ("THE PATCH BECOMES DESTRUCTIVE", PATCHFILE,
     'Class="PatchOperationAdd"', 'Class="PatchOperationReplace"', PROOF),

    ("the patch stops targeting Core's generator", PATCHFILE,
     'Defs/MapGeneratorDef[defName="Base_Player"]/genSteps',
     'Defs/MapGeneratorDef[defName="RR_Headquarters"]/genSteps', PROOF),

    ("a gen step is dropped from the patch", PATCHFILE,
     "      <li>RR_HeadquartersFacility</li>\n", "", PROOF),

    ("THE GEN STEP THROWS AGAIN INSTEAD OF RETURNING", GEN,
     "            if (!HeadquartersLayout.Fits(part.startDef, map.Size)) { return null; }",
     "            if (!HeadquartersLayout.Fits(part.startDef, map.Size)) { throw new InvalidOperationException(\"no\"); }",
     PROOF),

    ("a gen step stops checking for null", GEN,
     "            if (start == null) { return; }\n            HeadquartersSetupComponent receipt",
     "            HeadquartersSetupComponent receipt", PROOF),

    ("THE TERRAIN STEP FLATTENS THE WHOLE MAP AGAIN", GEN,
     "            MapGenFloatGrid elevation = MapGenerator.Elevation;",
     "            foreach (IntVec3 cell in map.AllCells) { map.terrainGrid.SetTerrain(cell, start.outdoorTerrain); }" + CHR_NL
     + "            MapGenFloatGrid elevation = MapGenerator.Elevation;",
     PROOF),

    # Retargeted: rewriting RequireStart into StartForMap removed the line this was
    # written against. The guard is a sequence of early returns now.
    ("the generator goes back to demanding an exact map size", GEN,
     "if (!HeadquartersLayout.Fits(part.startDef, map.Size)) { return null; }",
     "if (map.Size.x != part.startDef.mapSize) { return null; }", PROOF),

    ("the start stops being placed on the chosen tile", GEN,
     "            if (map.Tile != Find.GameInitData.startingTile) { return null; }" + CHR_NL, "", PROOF),

    ("THE ROOMS STOP BEING OFFSET", GEN,
     "CellRect rect = room.Rect.MovedBy(new IntVec2(offset.x, offset.z));",
     "CellRect rect = room.Rect;", PROOF),

    ("the offset is computed once and then not used", GEN,
     "IntVec3 offset = HeadquartersLayout.Offset(start, map.Size);\n            if (!(start.arrivalCell + offset)",
     "IntVec3 offset = IntVec3.Zero;\n            if (!(start.arrivalCell + offset)", PROOF),

    ("the layout stops being centred", LAYOUT,
     "int offsetX = (mapSize.x - extent.Width) / 2 - extent.minX;",
     "int offsetX = 0;", PROOF),

    ("the edge margin disappears", LAYOUT,
     "EdgeMargin", "EdgeMarginUnused", PROOF),

    ("the offset stops being clamped to the map", LAYOUT,
     "                if (offsetX > maxX) { offsetX = maxX; }\n", "", PROOF),

    ("the setup page shows the authored size instead of the real one", PAGE,
     "Find.GameInitData.mapSize));", "start.mapSize));", PROOF),

    # ------------------------------------------------------ the natural gate
    ("THE OPENING GOES BACK TO INSIDE-START ONLY", OPENING,
     "if (start == null || !start.emergenceDoorCell.IsValid) { return null; }",
     "if (start == null || !start.insideStart) { return null; }", PROOF),

    ("a surface start gets dragged into the coordinate too", OPENING,
     "            if (start.insideStart)\n", "            if (true)\n", PROOF),

    ("the surface natural gate stops recording its event", OPENING,
     'campaign.RecordEvent("RR_Event_NaturalGateOpening", coordinate.Id);',
     "// nothing", PROOF),

    ("THE DOOR LOOKUP STOPS BEING OFFSET", OPENING,
     "IntVec3 cell = start.emergenceDoorCell + HeadquartersLayout.Offset(start, surface.Size);",
     "IntVec3 cell = start.emergenceDoorCell;", PROOF),

    ("a named door no longer has to be one of the start's own", DEF,
     "if (emergenceDoorCell.IsValid && (doors == null || !doors.Contains(emergenceDoorCell)))",
     "if (false)", PROOF),

    ("an inside start may omit its door", DEF,
     "if (insideStart && !emergenceDoorCell.IsValid)", "if (false)", PROOF),

    ("THE STORE LOSES ITS NATURAL GATE", STARTS,
     "    <emergenceDoorCell>(35, 0, 34)</emergenceDoorCell>\n", "", PROOF),

    ("the Store names a cell that is not one of its doors", STARTS,
     "<emergenceDoorCell>(35, 0, 34)</emergenceDoorCell>",
     "<emergenceDoorCell>(20, 0, 20)</emergenceDoorCell>", PROOF),

    # ------------------------------------------------------ reachability and fit
    # Planted on the SOLE access to a room. The first version removed (27,0,16) and caught
    # nothing, because the Store's corridors form a ring and that door is one of several routes
    # -- the layout is more robustly connected than the plant assumed, which is a good thing
    # found by a bad plant. (29,0,16) is the only way into the stockroom.
    ("A ROOM GETS SEALED OFF FROM THE ARRIVAL CELL", STARTS,
     "      <li>(29, 0, 16)</li>\n", "", PROOF),

    # ------------------------------------------------- 0.12.47-dev: burn into place
    ("THE TERRAIN STEP RUNS BEFORE THE ELEVATION GRID EXISTS AGAIN", SCENARIOS,
     "<defName>RR_HeadquartersTerrain</defName>" + CHR_NL + "    <order>100</order>",
     "<defName>RR_HeadquartersTerrain</defName>" + CHR_NL + "    <order>5</order>", PROOF),

    ("the terrain step runs after Core has already spawned the rock", SCENARIOS,
     "<defName>RR_HeadquartersTerrain</defName>" + CHR_NL + "    <order>100</order>",
     "<defName>RR_HeadquartersTerrain</defName>" + CHR_NL + "    <order>300</order>", PROOF),

    ("THE SITE ELEVATION RISES BACK ABOVE CORE'S ROCK THRESHOLD", GEN,
     "private const float BuildableElevation = 0.55f;",
     "private const float BuildableElevation = 0.95f;", PROOF),

    ("the elevation is read but never lowered", GEN,
     "if (elevation[cell] > BuildableElevation) { elevation[cell] = BuildableElevation; }",
     "if (elevation[cell] > BuildableElevation) { }", PROOF),

    ("THE BURN IS DEFINED BUT NEVER CALLED", GEN,
     "            BurnIntoPlace(start, map, offset);" + CHR_NL, "", PROOF),

    ("THE BURN RUNS AFTER THE WALLS ARE ALREADY UP", GEN,
     "            BurnIntoPlace(start, map, offset);" + CHR_NL
     + "            foreach (RimroomsRoomPlan room in start.rooms)" + CHR_NL + "            {" + CHR_NL
     + "                CellRect rect = room.Rect.MovedBy(new IntVec2(offset.x, offset.z));",
     "            foreach (RimroomsRoomPlan room in start.rooms)" + CHR_NL + "            {" + CHR_NL
     + "                BurnIntoPlace(start, map, offset);" + CHR_NL
     + "                CellRect rect = room.Rect.MovedBy(new IntVec2(offset.x, offset.z));", PROOF),

    ("the burn stops carving anything out", GEN,
     "                    thing.Destroy(DestroyMode.Vanish);", "                    continue;", PROOF),

    ("the burn stops copying the cell's thing list before mutating it", GEN,
     "new List<Thing>(cell.GetThingList(map))", "cell.GetThingList(map)", PROOF),

    ("THE NATURAL ROCK ROOF IS LEFT HANGING OVER THE FACILITY", GEN,
     "                if (roof != null && roof.isNatural) { map.roofGrid.SetRoof(cell, null); }",
     "                if (roof != null) { }", PROOF),

    ("WATER IS NO LONGER FILLED IN WITH SOIL", GEN,
     "if (terrain.IsWater || terrain.passability == Traversability.Impassable)",
     "if (false)", PROOF),

    ("impassable terrain stops being filled", GEN,
     "terrain.passability == Traversability.Impassable", "terrain.IsWater", PROOF),

    ("THE BURN STARTS KILLING LIVING THINGS", GEN,
     "if (thing.def.category == ThingCategory.Pawn || !thing.def.destroyable) { continue; }",
     "if (!thing.def.destroyable) { continue; }", PROOF),

    ("another mod's structure is cleared silently", GEN,
     "if (thing.def.category == ThingCategory.Building && thing.Faction != null)",
     "if (false)", PROOF),

    ("THE WALL REFUSES GROUND CORE GENERATED AGAIN", GEN,
     "                        Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, start.wallStuff);",
     "                        if (cell.GetEdifice(map) != null) { throw new InvalidOperationException("
     + "\"Headquarters wall intersects generated structure at \" + cell); }" + CHR_NL
     + "                        Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, start.wallStuff);", PROOF),

    ("A FAILED FACILITY RE-THROWS INSTEAD OF HANDING THE SPOT BACK", GEN,
     "                MapGenerator.PlayerStartSpot = IntVec3.Invalid;",
     "                MapGenerator.PlayerStartSpot = IntVec3.Invalid;" + CHR_NL + "                throw;", PROOF),

    ("a failed facility leaves the player standing inside a building that does not exist", GEN,
     "                MapGenerator.PlayerStartSpot = IntVec3.Invalid;", "", PROOF),

    # ------------------------------------------------- 0.12.47-dev: the colonists survive us
    ("THE ARRIVAL THROWS OUT OF CORE'S SCENARIO STEP AGAIN", ARRIVAL,
     '                Log.Error("[Rimrooms][Scenario] Headquarters receipt incomplete at arrival; " +',
     '                throw new InvalidOperationException("[Rimrooms] Native arrival requires the '
     'prepared headquarters receipt.");' + CHR_NL
     + '                Log.Error("[Rimrooms][Scenario] Headquarters receipt incomplete at arrival; " +', PROOF),

    ("AN INCOMPLETE RECEIPT STOPS DELIVERING CORE'S OWN ARRIVAL", ARRIVAL,
     "                try { base.GenerateIntoMap(map); }", "                try { }", PROOF),

    ("the incomplete-receipt branch disappears", ARRIVAL,
     "            if (receipt == null || receipt.receiptVersion != 2 || !receipt.setupComplete)",
     "            if (false)", PROOF),

    ("the fallback stops recording that stock was granted once", ARRIVAL,
     "                    receipt.arrivalStarted = true;" + CHR_NL, "", PROOF),

    ("the fallback stops guarding against a second grant", ARRIVAL,
     "                    if (receipt.arrivalStarted) { return; }" + CHR_NL, "", PROOF),

    # ------------------------------------------------- the facility is the player's to take apart
    ("THE WALLS STOP BELONGING TO THE PLAYER", GEN,
     "                        wall.SetFactionDirect(Faction.OfPlayer);" + CHR_NL, "", PROOF),

    ("the doors stop belonging to the player", GEN,
     "                door.SetFactionDirect(Faction.OfPlayer);" + CHR_NL, "", PROOF),

    ("the furniture stops belonging to the player", GEN,
     "                building.SetFactionDirect(Faction.OfPlayer);" + CHR_NL, "", PROOF),

    ("THE FLOOR STOPS RECORDING WHAT IT COVERED", GEN,
     "if (room.floor) { map.terrainGrid.SetTerrain(cell, start.floorTerrain); }",
     "if (room.floor) { }", PROOF),

    ("the facility starts authoring a def the minify mod cannot reach", GEN,
     "            int index = 0;", "            ThingDef invented = new ThingDef();" + CHR_NL
     + "            int index = 0;", PROOF),

    ("the facility starts interfering with designations", GEN,
     "                        GenSpawn.Spawn(wall, cell, map);",
     "                        GenSpawn.Spawn(wall, cell, map);" + CHR_NL
     + "                        map.designationManager.RemoveAllDesignationsOn(wall);", PROOF),

    ("A LAYOUT ROOFS A SPAN NOTHING HOLDS UP", STARTS,
     "<li><x>27</x><z>27</z><width>7</width><height>7</height>",
     "<li><x>27</x><z>27</z><width>40</width><height>40</height>", PROOF),

    ("the Store loses the inner walls that hold its showroom roof up", STARTS,
     "      <li><x>10</x><z>10</z><width>18</width><height>14</height><roofed>true</roofed><floor>true</floor></li>" + CHR_NL,
     "", PROOF),

    ("a layout grows past the smallest map RimWorld offers", STARTS,
     "<li><x>8</x><z>8</z><width>44</width><height>44</height><roofed>false</roofed><floor>false</floor></li>",
     "<li><x>8</x><z>8</z><width>240</width><height>240</height><roofed>false</roofed><floor>false</floor></li>",
     PROOF),
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
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    write_verified(path, original.replace(old, new, 1))
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
