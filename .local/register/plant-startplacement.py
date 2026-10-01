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
SERVICES = "src/RimroomsAsyncIndustries/Company/CampaignServices.cs"
COMPONENT = "src/RimroomsAsyncIndustries/Company/RimroomsCampaignComponent.cs"
GATECOMP = "src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs"
CHR_NL = chr(10)
STEPS = "src/RimroomsAsyncIndustries/UI/OperationsGateSteps.cs"
TABS = "src/RimroomsAsyncIndustries/UI/OperationsExpeditions.cs"
PORTALUI = "src/RimroomsAsyncIndustries/UI/OperationsPortalNetwork.cs"
PATCHFILE = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_StartGenSteps.xml"
SCENARIOS = "Mod/Rimrooms - Async Industries/1.6/Defs/ScenarioDefs/RR_Scenarios.xml"
ARRIVAL = SCEN + "/ScenPart_RimroomsArrival.cs"
PROOF = ".local/register/proof-startplacement.py"
STARTS_PROOF = ".local/register/proof-starts.py"
FACILITY_PROOF = ".local/register/proof-facilities.py"
FACILITY = "src/RimroomsAsyncIndustries/Generation/FacilityPlanner.cs"
ARCHETYPES = ("Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsRoomArchetypeDefs/"
              "RR_RoomArchetypes.xml")


# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
# **ONE SENTINEL PER SUITE, named after the suite.** All sixteen shared a single path, so when
# `plant-containment.py` left one behind after a failed restore, the next suite's `_rr_unmark()`
# deleted it -- and `check-plant-residue.py` reported a clean tree with a planted fault in it.
# Fourth instance of residue reaching the tree and the first the sentinel could not see.
_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def _rr_restore(path, original):
    """Put the file back, and do not believe it until it reads back identical.

    The failure this exists for was transient -- `OSError: [Errno 22]` on a path this same loop
    had already written twice -- so a retry turns it into a non-event. A restore that still will
    not verify raises with the sentinel left in place, which is what stops the sweep from planting
    the next fault on top of this one.
    """
    last = None
    for attempt in range(5):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(original)
            if io.open(path, encoding="utf-8").read() == original:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.25 * (attempt + 1))
    raise RuntimeError("RESTORE FAILED for %s after 5 attempts: %s. The sentinel %s is left in "
                       "place; tools/check-plant-residue.py will refuse until the file is "
                       "restored." % (path, last, _RR_SENTINEL))


PLANTS = [
    # ------------------- a ramp is not an open connection, and the facility's power
    ("A RAMPING CONNECTION COUNTS AS OPEN AGAIN", STEPS,
     "                Done = haveGate && gate.IsOpening,",
     "                Done = haveGate && (gate.IsOpening || gate.IsSpinningUp),", STARTS_PROOF),

    ("the ramp stops reporting its progress", STEPS,
     "                How = ramping" + CHR_NL
     + '                    ? "RR_Steps_11HowRamping".Translate(',
     "                How = false" + CHR_NL
     + '                    ? "RR_Steps_11HowRamping".Translate(', STARTS_PROOF),

    ("THE LIST STOPS SAYING HOW TO SEND SOMEBODY THROUGH", STEPS,
     '            { listing.Label("RR_Steps_NowCross".Translate()); }',
     "            { }", STARTS_PROOF),

    ("CORE'S ROTATION ADJUSTMENT IS DROPPED FROM THE CHECKER",
     "tools/check-start-layout.py",
     "    shift = {0: (0, 0), 1: (0, -1), 2: (-1, -1), 3: (-1, 0)}[rotation % 4]",
     "    shift = {0: (0, 0), 1: (0, 0), 2: (0, 0), 3: (0, 0)}[rotation % 4]", STARTS_PROOF),

    ("the interaction-cell rule goes", "tools/check-start-layout.py",
     '                fail("%s: %s at %s has its interaction cell on the wall %s'
     ' -- nobody can ever "',
     '                pass  # ("%s: %s at %s has its interaction cell on the wall %s'
     ' -- nobody can ever "', STARTS_PROOF),

    ("ROOFED FALSE GOES BACK TO MERELY SKIPPING", GEN,
     "                        map.roofGrid.SetRoof(cell, room.roofed ? RoofDefOf.RoofConstructed : null);",
     "                        if (room.roofed) { map.roofGrid.SetRoof(cell, RoofDefOf.RoofConstructed); }",
     STARTS_PROOF),

    ("THE BREEZEWAY GETS A ROOF OVER THE GENERATORS", STARTS,
     "      <li><x>22</x><z>34</z><width>6</width><height>8</height><roofed>false</roofed><floor>true</floor></li>",
     "      <li><x>22</x><z>34</z><width>6</width><height>8</height><roofed>true</roofed><floor>true</floor></li>",
     STARTS_PROOF),

    ("the breezeway loses its door, so it stops being a room", STARTS,
     "      <li>(22, 0, 37)</li>" + CHR_NL, "", STARTS_PROOF),

    ("THE CONSOLE MOVES OFF WHERE THE OWNER PUT IT", STARTS,
     "      <li><thing>CommsConsole</thing><cell>(32, 0, 33)</cell><rotation>2</rotation></li>",
     "      <li><thing>CommsConsole</thing><cell>(32, 0, 27)</cell></li>", STARTS_PROOF),

    ("the assembly bench moves off where the owner put it", STARTS,
     "      <li><thing>TableMachining</thing><cell>(45, 0, 33)</cell></li>",
     "      <li><thing>TableMachining</thing><cell>(41, 0, 16)</cell></li>", STARTS_PROOF),

    # ---------------------------- the numbered checks, the refusals, and the facility
    ("THE NUMBERED CHECKS STOP BEING DRAWN", TABS,
     "            DrawGateStartupChecks(listing, campaign);" + CHR_NL, "", STARTS_PROOF),

    ("the checks are drawn after the panels they are meant to direct", TABS,
     "            DrawGateStartupChecks(listing, campaign);" + CHR_NL
     + "            DrawNativeGateBinding(listing, campaign);",
     "            DrawNativeGateBinding(listing, campaign);" + CHR_NL
     + "            DrawGateStartupChecks(listing, campaign);", STARTS_PROOF),

    ("A STEP LOSES ITS INSTRUCTION", STEPS,
     '                How = "RR_Steps_9How".Translate(),', "                How = null,", STARTS_PROOF),

    ("the first unfinished step stops being named", STEPS,
     '            { listing.Label("RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)); }',
     "            { }", STARTS_PROOF),

    ("the gate-control steps stop reading the components", STEPS,
     "                Done = workshop != null && workshop.IsGateControl,",
     "                Done = true,", STARTS_PROOF),

    ("CALIBRATION GOES BACK TO ONE MESSAGE FOR EIGHT CAUSES", GATECOMP,
     "            string blocker = CalibrationBlockerKey();" + CHR_NL
     + "            if (blocker != null) { return CompanyActionResult.Refused(blocker); }",
     '            if (!CanCalibrate(assignedOperator)) { return CompanyActionResult.Refused("RR_Gate_CalibrationUnavailable"); }',
     STARTS_PROOF),

    ("an already-calibrated gate stops saying so", GATECOMP,
     '            if (calibrated) { return "RR_Gate_AlreadyCalibrated"; }' + CHR_NL, "", STARTS_PROOF),

    ("the predicate derives the conditions a second time", GATECOMP,
     "            return pawn != null && pawn == assignedOperator && CalibrationBlockerKey() == null;",
     "            return !IsOpening && assemblyComplete && !calibrated && pawn != null;", STARTS_PROOF),

    ("THE EMPTY PORTAL PANEL GOES SILENT AGAIN", PORTALUI,
     '                    { listing.Label("RR_Portals_NoLaboratoryAddress".Translate()); }',
     "                    { }", STARTS_PROOF),

    ("the blockers are listed and then not drawn", PORTALUI,
     "                    foreach (string blocker in GateOpeningBlockers(gate))" + CHR_NL
     + "                    { listing.Label(blocker); }" + CHR_NL, "", STARTS_PROOF),

    ("THE GLAZING BECOMES A HARD CROSS-REFERENCE", DEF,
     "        public List<string> thingDefNames = new List<string>();",
     "        public List<ThingDef> thingDefNames = new List<ThingDef>();", STARTS_PROOF),

    ("a missing glass def leaves a hole instead of a wall", GEN,
     "                    if (glass == null) { continue; }" + CHR_NL, "", STARTS_PROOF),

    ("the headquarters power rebuild goes bare again", GEN,
     "            try { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }",
     "            map.powerNetManager.UpdatePowerNetsAndConnections_First(); if (false)", STARTS_PROOF),

    # ------------------------------------- institutions, and the loot in them
    # Owner: *"facilitys and buildings and neighboorhoods and complexes and shools and hospitals
    # and military and storages need loot inside of them too"*. `Anchors` opened with
    # `coordinate.Depth <= 1` and returned null, so a FIRST LEVEL HAD NO INSTITUTIONS AT ALL.
    ("A FIRST LEVEL LOSES EVERY INSTITUTION AGAIN", FACILITY,
     "            if (coordinate == null || coordinate.Rooms == null) { return null; }",
     "            if (coordinate == null || coordinate.Rooms == null || coordinate.Depth <= 1) { return null; }",
     FACILITY_PROOF),

    ("the arrival stops staying sparse, so the yellow rooms become a complex", FACILITY,
     "                if (RoomArchetypeService.EffectiveDepth(coordinate, room, coordinate.Depth) <= 1)"
     + chr(10) + "                { continue; }" + chr(10), "", FACILITY_PROOF),

    ("a complex shrinks back to four rooms while the proof models six", FACILITY,
     "        private const int MaxRooms = 6;", "        private const int MaxRooms = 4;",
     FACILITY_PROOF),

    ("the eligible share drifts from the model that mirrors it", FACILITY,
     "        private const float EligibleShare = 0.6f;",
     "        private const float EligibleShare = 0.45f;", FACILITY_PROOF),

    ("AN ARCHETYPE GOES BACK TO HOLDING NOTHING WORTH CARRYING OUT", ARCHETYPES,
     "      <li>" + chr(10) + "        <kind>CategoryMember</kind>" + chr(10)
     + "        <category>Apparel</category>" + chr(10) + "        <count>1~3</count>" + chr(10)
     + "        <chance>0.8</chance>" + chr(10) + "      </li>" + chr(10), "", FACILITY_PROOF),

    # ------------------------- the fault that disabled a whole scenario on turn one
    ("THE CORPORATE START DISABLES ITSELF ON TURN ONE AGAIN", SERVICES,
     '                    insightOperationId = done ? projectId + ":insight" : null,' + chr(10), "",
     STARTS_PROOF),

    ("a pre-completed project is committed with an empty receipt", SERVICES,
     '                    insightOperationId = done ? projectId + ":insight" : null,',
     '                    insightOperationId = done ? "" : null,', STARTS_PROOF),

    ("THE VALIDATOR STOPS REQUIRING A RECEIPT, so a double payment can hide", COMPONENT,
     "(!p.insightCommitted || !string.IsNullOrWhiteSpace(p.insightOperationId))",
     "(!p.insightCommitted || true)", STARTS_PROOF),

    ("the corporate start stops beginning with its research finished", STARTS,
     "      <li>RR_GateTelemetry</li>" + chr(10), "", STARTS_PROOF),

    # ------------------------------------------- the toggle on the door
    ("AN UNDESIGNATED DOOR GOES BACK TO OFFERING NOTHING", GATECOMP,
     "            if (!IsDesignated)" + chr(10) + "            {" + chr(10)
     + "                foreach (Gizmo gizmo in MakeGateGizmos()) { yield return gizmo; }" + chr(10)
     + "                yield break;" + chr(10) + "            }",
     "            if (!IsDesignated) { yield break; }", STARTS_PROOF),

    ("the toggle appears on a door away from the headquarters", GATECOMP,
     "                || campaign.Headquarters != parent.Map",
     "                || false", STARTS_PROOF),

    ("the toggle binds the first of several providers instead of refusing", GATECOMP,
     "                    if (console == null || battery == null || bench == null)",
     "                    if (false)", STARTS_PROOF),

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
     "    <arrivalCell>(39, 0, 29)</arrivalCell>",
     "    <mapGenerator>RR_Headquarters</mapGenerator>\n    <arrivalCell>(39, 0, 29)</arrivalCell>",
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
     # The compound is roofed and floored now: the whole facility is one building and its gaps
     # are interior service corridors rather than open yard.
     "<li><x>8</x><z>8</z><width>44</width><height>44</height><roofed>true</roofed><floor>true</floor></li>",
     "<li><x>8</x><z>8</z><width>240</width><height>240</height><roofed>true</roofed><floor>true</floor></li>",
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
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
