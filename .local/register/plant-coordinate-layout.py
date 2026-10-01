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
BUDGET = SRC + "/Portals/OpenMapBudget.cs"
FRONTIER = SRC + "/Portals/NaturalFrontierService.cs"
STARTDEF = SRC + "/Scenario/RimroomsStartDef.cs"
PARENT = SRC + "/Generation/RimroomsDestinationMapParent.cs"
RELEASE = SRC + "/Generation/CoordinateRelease.cs"
RECORDS = SRC + "/Company/CampaignRecords.cs"
EMERGENCE = SRC + "/Portals/CompRimroomsEmergence.cs"
PLACES = SRC + "/UI/OperationsHeldPlaces.cs"
OPTABS = SRC + "/UI/MainTabWindow_Operations.cs"
ADDRESS = SRC + "/Portals/PortalAddressService.cs"
NETWORK = SRC + "/Portals/RimroomsPortalNetwork.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"
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
     "internal const int MaxSlotsPerAxis =", "internal const int MaxSlotsPerAxisUnused ="),

    # The SECOND span source. Deleting the evenness guard from one of them used to pass, because
    # the claim counted a string that exists in both.
    ("THE VARIED SPAN STOPS BEING EVEN, so doors miss the slot centre", PLANNER,
     "            int span = baseline + offset;" + NL
     + "            if (span % 2 != 0) { span--; }" + NL,
     "            int span = baseline + offset;" + NL),

    ("rooms stop varying in size, so the level is a grid of identical boxes again", PLANNER,
     "VariedRoomSpan(spacing, slot, seed, depth)", "SlotRoomSpan(spacing)"),

    ("THE GRAND THRESHOLD HALL IS LOST", PLANNER,
     "rooms.Add(MakeHall(coordinate, order[0], order[1], spacing, seed, depth));", ""),

    ("the hall grows to four slots and breaks the chain's adjacency", PLANNER,
     "                consumed = 2;", "                consumed = 4;"),

    ("the maze goes back to one branch in three", PLANNER,
     "% 4 == 3)", "% 3 != 0)"),

    ("THE WARREN STOPS TIGHTENING INWARD", PLANNER,
     "internal const int MaxRooms = 60;", "internal const int MaxRooms = 6;"),

    # The first level stops being a maze and goes back to a handful of halls.
    ("THE FIRST LEVEL GOES BACK TO A WAREHOUSE", PLANNER,
     "internal const int MinSlotsPerAxis = 6;", "internal const int MinSlotsPerAxis = 3;"),

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
    # ------------------------------------------------------ rooms are not rectangles
    ("ROOMS GO BACK TO BEING PLAIN RECTANGLES", PLANNER,
     "            if (room == null || depth <= 1) { yield break; }",
     "            if (room != null) { yield break; }"),

    ("the generator stops leaving any rock standing inside a room", GEN,
     "                    if (intrusions.Contains(cell)) { continue; }" + NL, ""),

    ("THE CENTRE CROSS STARTS GETTING FILLED IN", PLANNER,
     "                        if (x == center.x || z == center.z) { continue; }" + NL, ""),

    ("a corner mass starts reaching into the wall ring", PLANNER,
     "                        if (x <= bounds.minX + 1 || x >= bounds.maxX - 1) { continue; }" + NL,
     ""),

    ("the corner reach stops being clamped to a third of the room", PLANNER,
     "            int reach = System.Math.Min((depth - 1) * 2, System.Math.Min(extentX - insetX, extentZ - insetZ) / 3);",
     "            int reach = (depth - 1) * 2;"),

    ("SHALLOW COORDINATES START DEFORMING TOO", PLANNER,
     "            if (room == null || depth <= 1) { yield break; }",
     "            if (room == null) { yield break; }"),

    ("the planner stops modelling the rock it leaves standing", PLANNER,
     "                foreach (IntVec3 rock in RockIntrusionCells(room, depth))" + NL
     + "                { floor[rock.x, rock.z] = false; }" + NL, ""),

    ("AN UNCARVED CELL LOSES ITS ROOF AND OPENS A HOLE IN THE WORLD", GEN,
     "                    map.roofGrid.SetRoof(cell, overheadRoof);" + NL
     + "                    if (intrusions.Contains(cell)) { continue; }",
     "                    if (intrusions.Contains(cell)) { continue; }" + NL
     + "                    map.roofGrid.SetRoof(cell, overheadRoof);"),

    ("HALLWAYS GO BACK TO ONE WIDTH", GEN,
     "int halfWidth = RoomLayoutPlanner.CorridorHalfWidthBetween(room, other, depth);",
     "int halfWidth = 2;"),

    ("the planner models a corridor width the generator does not carve", PLANNER,
     "                    int reach = CorridorHalfWidthBetween(room, other, depth) - 1;",
     "                    int reach = 1;"),

    # ------------------------------------------------------ the open-map budget
    ("THE BUDGET GETS HARD-CODED INSTEAD OF READING THE GAME'S LIMIT", BUDGET,
     "int budget = scenario > 0 ? scenario : Prefs.MaxNumberOfPlayerSettlements;",
     "int budget = scenario > 0 ? scenario : 5;"),

    ("the scenario override stops being consulted", BUDGET,
     "int budget = scenario > 0 ? scenario : Prefs.MaxNumberOfPlayerSettlements;",
     "int budget = Prefs.MaxNumberOfPlayerSettlements;"),

    ("the per-scenario field is removed from the start def", STARTDEF,
     "        public int openMapBudget;", "        public int openMapBudgetUnused;"),

    ("THE BUDGET FLOOR GOES AND A SLIDER AT 1 BREAKS THE SOLO START", BUDGET,
     "internal const int MinimumBudget = 2;", "internal const int MinimumBudget = 1;"),

    ("the floor is defined but not applied", BUDGET,
     "return Mathf.Max(MinimumBudget, budget);", "return budget;"),

    ("a Backrooms level stops counting against the budget", BUDGET,
     "                    if (map.Parent is Generation.RimroomsDestinationMapParent) { held++; }" + NL,
     ""),

    ("colonies stop counting against the budget", BUDGET,
     "                    else if (map.IsPlayerHome && map.Parent is Settlement) { held++; }" + NL,
     ""),

    ("A GATE IS BLOCKED ONLY AFTER A COORDINATE HAS ALREADY BEEN MINTED", FRONTIER,
     "            if (!OpenMapBudget.CanOpenAnother)" + NL
     + "            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }" + NL
     + "            CompanyActionResult created = campaign.CreateDiscoveredCoordinate(discoveryId, depth, out discovered);",
     "            CompanyActionResult created = campaign.CreateDiscoveredCoordinate(discoveryId, depth, out discovered);" + NL
     + "            if (!OpenMapBudget.CanOpenAnother)" + NL
     + "            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }"),

    ("THE BUDGET STARTS CLOSING THE LAST DOOR HOME", FRONTIER,
     "            if (source != null)" + NL + "            {" + NL
     + "                CompanyActionResult wayOut = TryRecordWayOut(door, origin, campaign);",
     "            if (!OpenMapBudget.CanOpenAnother)" + NL
     + "            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }" + NL
     + "            if (source != null)" + NL + "            {" + NL
     + "                CompanyActionResult wayOut = TryRecordWayOut(door, origin, campaign);"),

    ("the doorway stops checking the budget at all", FRONTIER,
     "            if (!OpenMapBudget.CanOpenAnother)" + NL
     + "            { return CompanyActionResult.Refused(OpenMapBudget.BlockedKey); }" + NL, ""),

    ("the map-generation backstop goes", SERVICE,
     "            if (coordinate.Site == null && !Portals.OpenMapBudget.CanOpenAnother)" + NL
     + "            { return CompanyActionResult.Refused(Portals.OpenMapBudget.BlockedKey); }" + NL, ""),

    ("RECALLING AN ALREADY-GENERATED COORDINATE STARTS BEING REFUSED", SERVICE,
     "if (coordinate.Site == null && !Portals.OpenMapBudget.CanOpenAnother)",
     "if (!Portals.OpenMapBudget.CanOpenAnother)"),

    ("the player is never told why the gate refused", KEYED,
     "<RR_Frontier_TooManyGatesHeld>", "<RR_Frontier_TooManyGatesHeldUnused>"),

    ("WAYS ONWARD GO BACK TO TWO PER LEVEL", FRONTIER,
     "internal const int MinimumFrontiersPerCoordinate = 4;",
     "internal const int MinimumFrontiersPerCoordinate = 2;"),

    ("the ceiling on ways onward disappears", FRONTIER,
     "            int allowed = MinimumFrontiersPerCoordinate + rooms / RoomsPerExtraFrontier;" + NL
     + "            return allowed > MaximumFrontiersPerCoordinate ? MaximumFrontiersPerCoordinate : allowed;",
     "            return MinimumFrontiersPerCoordinate + rooms / RoomsPerExtraFrontier;"),

    ("the gate count starts reading depth instead of the size of the place", FRONTIER,
     "int rooms = coordinate == null || coordinate.Rooms == null ? 0 : coordinate.Rooms.Count;",
     "int rooms = coordinate == null ? 0 : coordinate.Depth;"),

    ("THE NATURAL CHAIN GOES BACK TO THREE BANDS", FRONTIER,
     "internal const int MaximumNaturalDepth = 6;", "internal const int MaximumNaturalDepth = 3;"),

    ("a coordinate map starts unloading itself and taking the player's work with it", PARENT,
     "            alsoRemoveWorldObject = false;" + NL + "            return false;",
     "            alsoRemoveWorldObject = false;" + NL + "            return true;"),

    # ------------------------------------------------------ letting a place go
    ("THE DISCOVERY-COSTS-A-SLOT FACT STOPS HOLDING", ADDRESS,
     "DestinationService.EnsureSite(campaign, coordinate, out siteMap, out siteEntry)",
     "DestinationService.EnsureSiteUnused(campaign, coordinate, out siteMap, out siteEntry)"),

    ("a release stops being written to the save", RECORDS,
     '            Scribe_Values.Look(ref releasedByPlayer, "rr_releasedByPlayer", false);' + NL,
     ""),

    ("THE EXPLORED-GRAPH GUARD STOPS EXEMPTING A DELIBERATE RELEASE", SERVICE,
     "            if (!releasedAndRebuildable && coordinate.Site == null && (coordinate.Status == CoordinateStatus.Ready ||",
     "            if (coordinate.Site == null && (coordinate.Status == CoordinateStatus.Ready ||"),

    ("THE EXEMPTION STARTS BYPASSING A LIVE MAP TOO", SERVICE,
     "                !Find.Maps.Any(existing => (existing.Parent as RimroomsDestinationMapParent)?.CoordinateId == coordinate.Id);",
     "                true;"),

    ("THE EXEMPTION OUTLIVES ITS REASON", SERVICE,
     "            coordinate.releasedByPlayer = false;" + NL, ""),

    ("THE EDGES ARE REMOVED BEFORE THE DOORS ARE TOLD WHERE THEY LED", RELEASE,
     "                RememberOn(edge.First, coordinate, map);" + NL
     + "                RememberOn(edge.Second, coordinate, map);" + NL,
     ""),

    ("THE MAP IS TORN DOWN BEFORE THE EDGES ARE REMOVED", RELEASE,
     "            for (int index = 0; index < shelved.Count; index++)" + NL
     + "            { network.ForgetConnection(shelved[index].Id); }",
     "            Current.Game.DeinitAndRemoveMap(map, false);" + NL
     + "            for (int index = 0; index < shelved.Count; index++)" + NL
     + "            { network.ForgetConnection(shelved[index].Id); }"),

    ("a release discards the graph, so the place comes back different", RELEASE,
     "            coordinate.status = CoordinateStatus.Discovered;",
     "            coordinate.rooms = null;"),

    ("the pairing is written onto the map being destroyed", RELEASE,
     "            if (anchor == null || anchor.Destroyed || anchor.Map == null || anchor.Map == releasing)",
     "            if (anchor == null || anchor.Destroyed || anchor.Map == null)"),

    ("RELEASING THE HEADQUARTERS BECOMES POSSIBLE", RELEASE,
     '            if (campaign.Headquarters == map) { return "RR_Release_Headquarters"; }' + NL, ""),

    ("A PLACE WITH PEOPLE IN IT BECOMES RELEASABLE", RELEASE,
     '            { return "RR_Release_CrewInside"; }', '            { }'),

    ("a prisoner or an animal stops counting as somebody inside", RELEASE,
     "pawn.Faction == Faction.OfPlayer || pawn.IsPrisonerOfColony))",
     "pawn.Faction == Faction.OfPlayer && pawn.RaceProps.Humanlike))"),

    ("A PLACE SOMEBODY IS CROSSING INTO BECOMES RELEASABLE", RELEASE,
     '                    if (crossings.IsConnectionInFlight(edge.Id)) { return "RR_Release_CrossingInFlight"; }' + NL,
     ""),

    ("the network gains a second, wider removal", NETWORK,
     "            connections.Remove(edge);",
     "            connections.Remove(edge);" + NL
     + "            connections.RemoveAll(other => other == null);"),

    ("THE DOOR STOPS REMEMBERING WHERE IT LED", EMERGENCE,
     '            Scribe_Values.Look(ref shelvedCoordinateId, "rr_emergenceShelvedCoordinate");' + NL,
     ""),

    ("the release stops telling the door anything", RELEASE,
     "            emergence.RememberShelvedPlace(coordinate.Id);",
     "            emergence.ForgetShelvedPlace();"),

    # **RE-OPENING IS GONE, SO THESE PLANTS INVERTED.** Owner: *"we do need to be able to
    # close natural portals u just can not re open them"*, *"thats the whole 5 limit
    # issue"*. They used to break the SHAPE of a re-open; each one now RESTORES a way to
    # re-open and requires the proof to refuse it. Replaced rather than deleted, so the
    # count stays honest.
    ("THE REOPEN METHOD COMES BACK", EMERGENCE,
     "        // `Reopen` lived here until 0.12.59-dev.",
     "        private CompanyActionResult Reopen(CoordinateRecord shelved)" + NL
     + "        { return PortalAddressService.RegisterNaturalAddress("
     + "parent, ApproachCell, shelved); }" + NL + NL
     + "        // `Reopen` lived here until 0.12.59-dev."),

    ("THE REOPEN GIZMO COMES BACK", EMERGENCE,
     "            bool marked = IsDesignated;",
     "            bool marked = IsDesignated;" + NL
     + "            yield return new Command_Action { defaultLabel = "
     + chr(34) + "RR_Release_ReopenLabel" + chr(34) + ".Translate() };"),

    ("the door stops remembering where it led, so a spent gate looks like any door",
     EMERGENCE,
     "internal string ShelvedCoordinateId { get { return shelvedCoordinateId; } }",
     "internal string ShelvedCoordinateIdUnused { get { return shelvedCoordinateId; } }"),

    ("THE HELD-PLACES PANE IS NEVER DISPATCHED TO", OPTABS,
     "                case 12: DrawHeldPlaces(listing, campaign); break;" + NL, ""),

    ("the help pane index is left behind and help opens the places list", OPTABS,
     "        private const int HelpPane = 13;", "        private const int HelpPane = 12;"),

    ("the pane stops showing the colonies that fill the budget", PLACES,
     "                listing.Label(\"RR_Release_ColonyRow\".Translate(colonies[index].Parent.Label));",
     "                continue;"),

    ("A RELEASE STOPS BEING CONFIRMED", PLACES,
     "                            destructive: true,", "                            destructive: false,"),

    ("A FAILED RELEASE BECOMES SILENT", PLACES,
     '                Messages.Message("RR_Release_Failed".Translate(label, refusal.Translate()),',
     '                Messages.Message("".Translate(),'),

    ("a release refusal loses its keyed string", KEYED,
     "<RR_Release_CrewInside>", "<RR_Release_CrewInsideUnused>"),

    ("the places pane label is never written", KEYED,
     "<RR_UI_Places>", "<RR_UI_PlacesUnused>"),

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
