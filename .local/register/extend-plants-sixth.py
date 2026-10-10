# -*- coding: utf-8 -*-
"""Plants for the sixth-launch fixes."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(REPO, ".local", "register")

# ------------------------------------------------------------------ conduit plants
P = os.path.join(REG, "plant-generation.py")
t = io.open(P, encoding="utf-8").read()
A = "    # ------------------------------------------ 0.12.48-dev: the light count that killed everything"
NEW = '''    # ------------------------------------------ 0.12.53-dev: the conduit blowout
    ("THE WHOLE-ROOM CONDUIT CARPET COMES BACK", GEN,
     "            return wiredCells;" + chr(10) + "        }",
     "            foreach (IntVec3 cell in consumerFootprints.SelectMany(room => room.Cells)" + chr(10)
     + "                .Distinct()) { SpawnNativeConduit(map, voidFloor, conduitDef, cell, wiredCells); }" + chr(10)
     + "            return wiredCells;" + chr(10) + "        }"),

    ("the grid stops handing back what it wired", GEN,
     "        private static HashSet<IntVec3> SpawnNativePowerNetwork(Map map, TerrainDef voidFloor,",
     "        private static HashSet<IntVec3> SpawnNativePowerNetworkUnused(Map map, TerrainDef voidFloor,"),

    ("THE STRAY PASS RUNS BEFORE THE DRESSING EXISTS", GEN,
     "                ConnectStrayConsumers(map, voidFloor, conduitDef, wiredCells, generator);" + chr(10),
     ""),

    ("the stray pass stops sweeping for power consumers", GEN,
     "                    thing.TryGetComp<CompPowerTrader>() != null)" + chr(10)
     + "                .OrderBy(thing => thing.Position.x).ThenBy(thing => thing.Position.z)",
     "                    false)" + chr(10)
     + "                .OrderBy(thing => thing.Position.x).ThenBy(thing => thing.Position.z)"),

    ("THE STRAY PASS STARTS THROWING AND CAN COST THE COORDINATE", GEN,
     "                    TrySpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells);",
     "                    SpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells);"),

    ("the non-throwing conduit form disappears", GEN,
     "        private static void TrySpawnNativeConduit(Map map, TerrainDef voidFloor, ThingDef conduitDef,",
     "        private static void TrySpawnNativeConduitUnused(Map map, TerrainDef voidFloor, ThingDef conduitDef,"),

    ("the stray pass stops respecting the conduit cap", GEN,
     "                if (wiredCells.Count >= MaxNativePowerConduits) { return; }" + chr(10)
     + "                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells,",
     "                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells,"),

''' + A
if t.count(A) != 1:
    print("GEN PLANT ANCHOR PROBLEM: %d" % t.count(A))
    raise SystemExit(1)
io.open(P, "w", encoding="utf-8", newline="").write(t.replace(A, NEW, 1))
print("conduit plants added")


# ------------------------------------------------------------------ gate-look plants
P2 = os.path.join(REG, "plant-gate-links-carry.py")
t2 = io.open(P2, encoding="utf-8").read()
PATHS = 'PROOF = ".local/register/proof-gate-links.py"'
PATHS_NEW = ('DOORPATCH = "Mod/Rimrooms - Async Industries/1.6/Patches/RR_NativeGateProviders.xml"\n'
             'PROOF = ".local/register/proof-gate-links.py"')
A2 = "]\n\n\ndef write_verified"
NEW2 = '''    # ------------------------------------------ 0.12.53-dev: a gate looks like a gate
    ("A LIVE GATE STOPS BEING BLUE", COMP,
     "                if (live) { colorable.SetColor(LiveGlowColor.ToColor); }",
     "                if (false) { colorable.SetColor(LiveGlowColor.ToColor); }"),

    ("a live gate stops casting light", COMP,
     "                glower.GlowRadius = live ? LiveGlowRadius : 0f;",
     "                glower.GlowRadius = 0f;"),

    ("the glower comp is never added to the door", DOORPATCH,
     '<li Class="CompProperties_Glower">', '<li Class="CompProperties_GlowerUnused">'),

    ("the colourable comp is never added to the door", DOORPATCH,
     '<li Class="CompProperties_Colorable" />', '<li Class="CompProperties_ColorableUnused" />'),

    ("EVERY DOOR IN THE GAME STARTS GLOWING", COMP,
     "    public class CompRimroomsEmergence : ThingComp, IThingGlower",
     "    public class CompRimroomsEmergence : ThingComp"),

    ("the glow veto stops asking whether this is a live gate", COMP,
     "        public bool ShouldBeLitNow() { return IsLiveGate; }",
     "        public bool ShouldBeLitNow() { return true; }"),

    ("the patch default radius stops being dark", DOORPATCH,
     "<glowRadius>0</glowRadius>", "<glowRadius>8</glowRadius>"),

    ("A MARKED DOOR WITH NO WAY THROUGH STARTS GLOWING", COMP,
     "                if (!IsDesignated || parent == null || Verse.Current.Game == null) { return false; }",
     "                if (parent == null || Verse.Current.Game == null) { return false; }"),

    ("the live test stops asking the network", COMP,
     "                RimroomsPortalNetwork network = Verse.Current.Game.GetComponent<RimroomsPortalNetwork>();" + chr(10)
     + "                if (network == null || network.Connections == null) { return false; }",
     "                RimroomsPortalNetwork network = null;" + chr(10)
     + "                if (network == null) { return true; }"),

    ("a dead gate keeps its colour", COMP,
     "                else if (colorable.Active) { colorable.Disable(); }", "                else { }"),

    # ------------------------------------------ and is walked through like one
    ("RIGHT-CLICKING THE GATE NO LONGER OFFERS TO WALK THROUGH IT", COMP,
     "        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)",
     "        public IEnumerable<FloatMenuOption> CompFloatMenuOptionsUnused(Pawn selPawn)"),

    ("the menu stops ordering a real crossing", COMP,
     "                Show(PortalTravelService.OrderCrossing(selPawn, subject));",
     "                Show(CompanyActionResult.Applied());"),

    ("THE MENU STARTS DECIDING ELIGIBILITY ITSELF", COMP,
     "            string refusal = RimroomsPortalCrossingService.EligibilityFailureKey(selPawn);",
     "            string refusal = selPawn.Drafted ? \\"RR_PortalTravel_NoPerson\\" : null;"),

    ("a pawn who cannot cross is hidden instead of told why", COMP,
     "                yield return new FloatMenuOption(" + chr(10)
     + '                    "RR_DoorCross_EnterRefused".Translate(refusal.Translate()), null);',
     "                yield break;"),

    ("the menu is offered on a door that is not a live gate", COMP,
     "            if (!IsLiveGate) { yield break; }", "            if (false) { yield break; }"),

    ("the enter string is never written", KEYED,
     "<RR_DoorCross_Enter>", "<RR_DoorCross_EnterUnused>"),

    ("the refusal string is never written", KEYED,
     "<RR_DoorCross_EnterRefused>", "<RR_DoorCross_EnterRefusedUnused>"),

''' + A2
problems = []
if t2.count(PATHS) != 1:
    problems.append("paths %d" % t2.count(PATHS))
if t2.count(A2) != 1:
    problems.append("list %d" % t2.count(A2))
if problems:
    for problem in problems:
        print("PLANT ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
t2 = t2.replace(PATHS, PATHS_NEW, 1).replace(A2, NEW2, 1)
io.open(P2, "w", encoding="utf-8", newline="").write(t2)
print("gate-look plants added")
