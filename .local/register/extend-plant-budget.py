# -*- coding: utf-8 -*-
"""Plants for the open-map budget claims."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")

text = io.open(PLANT, encoding="utf-8").read()

PATHS = 'PROOF = ".local/register/proof-coordinate-layout.py"'
PATHS_NEW = ('BUDGET = SRC + "/Portals/OpenMapBudget.cs"\n'
             'FRONTIER = SRC + "/Portals/NaturalFrontierService.cs"\n'
             'STARTDEF = SRC + "/Scenario/RimroomsStartDef.cs"\n'
             'PARENT = SRC + "/Generation/RimroomsDestinationMapParent.cs"\n'
             'KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Portals.xml"\n'
             'PROOF = ".local/register/proof-coordinate-layout.py"')

ANCHOR = "]\n\n\ndef write_verified"

NEW = '''    # ------------------------------------------------------ the open-map budget
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

''' + ANCHOR

problems = []
if text.count(PATHS) != 1:
    problems.append("paths anchor %d" % text.count(PATHS))
if text.count(ANCHOR) != 1:
    problems.append("list anchor %d" % text.count(ANCHOR))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

text = text.replace(PATHS, PATHS_NEW, 1).replace(ANCHOR, NEW, 1)
io.open(PLANT, "w", encoding="utf-8", newline="").write(text)
print("budget plants added")
