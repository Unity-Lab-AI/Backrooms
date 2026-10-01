# -*- coding: utf-8 -*-
"""Plant a fault, run the generation proof, require exit 1, restore. Verified writes."""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
NL = chr(10)
MAT = SRC + "/Generation/CoordinateMaterials.cs"
CONTENT = SRC + "/Generation/RoomContentBuilder.cs"
INHAB = SRC + "/Threats/InhabitantService.cs"
IDEF = SRC + "/Threats/RimroomsInhabitantDef.cs"
GEN = SRC + "/Generation/GenStep_BackroomsDestination.cs"
PROOF = ".local/register/proof-generation-batch.py"

PLANTS = [
    # ------------------------------- the furniture rule that stopped a level being built
    # `Place` refused any cell whose footprint had an edifice within one. The room's wall, its
    # pillar lattice, the rock in its shaped corners, the lamp on every pillar and every fixture
    # already placed are all edifices, on top of the reserved three-cell route cross -- so a room
    # could be left with ONE placeable cell. The first fixture took it and the second threw out
    # of `GenStep.Generate`, stopping the level halfway: the owner got a Backrooms map with no
    # content and a door that was never marked.
    ("THE WALKABLE MARGIN GOES BACK TO BEING MANDATORY", CONTENT,
     "                if (!footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null))"
     + NL + "                { return cell; }",
     "                if (footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null))"
     + NL + "                { continue; }"),

    ("the cell without a margin is found and then thrown away", CONTENT,
     "            return withoutMargin;", "            return IntVec3.Invalid;"),

    ("EVERY FAMILY FIXTURE BECOMES REQUIRED AGAIN", CONTENT,
     "                count, false);", "                count, true);"),

    ("a decoration goes back to being a throwing Place call", CONTENT,
     '                            Decorate(map, room, coordinate, "Stool", reserved, seed, 1);'
     + NL + "                            break;" + NL + '                        case "survey_lobby":',
     '                            Place(map, room, coordinate, "Stool", reserved, seed, 1);'
     + NL + "                            break;" + NL + '                        case "survey_lobby":'),

    ("the cell search is derived a second time inside TryPlace", CONTENT,
     "            IntVec3 cell = FixtureCell(map, room, reserved, thing, rotation, preferred);"
     + NL + "            if (!cell.IsValid) { return null; }",
     "            IntVec3 cell = interior_unused;" + NL + "            if (!cell.IsValid) { return null; }"),

    ("A LANDMARK REFUSAL GOES SILENT AGAIN", CONTENT,
     '                    Log.Warning("[Rimrooms][Generation] No cell for the landmark " + defName',
     '                    Log.Warning("[Rimrooms][Generation] No cell for a landmark" + ("" + defName'),

    ("the route cross is derived in two places again", CONTENT,
     "                { if (OnRouteCross(room, cell)) { reserved.Add(cell); } }",
     "                { if (Math.Abs(cell.x - room.Bounds.CenterCell.x) <= 1) { reserved.Add(cell); } }"),

    # ------------------------------------------- two transmitters on one cell
    # Core refuses the second and leaves its bookkeeping inconsistent, so
    # PowerConnectionMaker.TryConnectToAnyPowerNet throws out of Map.FinalizeInit and then out of
    # every Update for the rest of the session.
    ("A SECOND TRANSMITTER LANDS ON A CELL THAT ALREADY HAS ONE", GEN,
     "            if (AlreadyTransmits(map, cell)) { return; }" + NL
     + "            Thing conduit = MakeBuilding(conduitDef, null);" + NL
     + "            conduit.SetFaction(Faction.OfPlayer);" + NL
     + "            GenSpawn.Spawn(conduit, cell, map, Rot4.North);" + NL
     + "        }",
     "            Thing conduit = MakeBuilding(conduitDef, null);" + NL
     + "            conduit.SetFaction(Faction.OfPlayer);" + NL
     + "            GenSpawn.Spawn(conduit, cell, map, Rot4.North);" + NL
     + "        }"),

    ("the guard is kept on one path and dropped from the other", GEN,
     "            // Not a generator fault: the cell is already wired, by somebody else, and that is"
     + NL + "            // exactly as good as wiring it ourselves." + NL
     + "            if (AlreadyTransmits(map, cell)) { return; }" + NL, ""),

    ("and it stops asking Core whether the thing transmits", GEN,
     "                if (thing != null && thing.def != null && thing.def.EverTransmitsPower)",
     "                if (thing != null && thing.def != null && thing.def == conduitDefUnused)"),

    # Anchored on the WHOLE statement since 0.12.52-dev. The dressing path now uses the same
    # call, four spaces deeper, and a 16-space anchor is a substring of a 20-space one -- so this
    # matched twice and the harness refused to run rather than mis-score a fault it never planted.
    ("the hardcoded wood comes back", CONTENT,
     "            Thing thing = ThingMaker.MakeThing(definition," + chr(10)
     + "                CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot));",
     "            Thing thing = ThingMaker.MakeThing(definition," + chr(10)
     + "                definition.MadeFromStuff ? ThingDefOf.WoodLog : null);"),

    ("THE SORT GOES, so a mod list can change a coordinate's appearance", MAT,
     "                .OrderBy(definition => definition.defName, StringComparer.Ordinal)\n", ""),

    ("the palette stops coming from the coordinate's seed", MAT,
     "                : DestinationService.StableHash(coordinate.Seed,\n"
     '                    (coordinate.Id ?? "") + ":materials", MaterialVersion);',
     "                : MaterialVersion;"),

    ("a Rand call creeps into the derivation", MAT,
     "            var chosen = new List<ThingDef>();",
     "            var chosen = new List<ThingDef>();\n            int unused = Rand.Range(0, 1);"),

    ("Core's own stuff-generation opt-out is ignored", MAT,
     "            if (!definition.stuffProps.allowedInStuffGeneration) { return false; }\n", ""),

    ("a material gets named, so there is a list to fall out of date", MAT,
     '        private static bool Usable(ThingDef definition)',
     '        private static bool Named() { return "Plasteel" != null; }\n\n'
     '        private static bool Usable(ThingDef definition)'),

    ("our own defs become eligible fixture material", MAT,
     '            return definition.defName == null || !definition.defName.StartsWith("RR_",\n'
     "                StringComparison.Ordinal);",
     "            return true;"),

    ("the fallback to Core's default goes, so a fixture can have no material", MAT,
     "            return GenStuff.DefaultStuffFor(definition);",
     "            return null;"),

    ("the palette cache stops being scoped to one game", MAT,
     "            int generation = Current.Game == null ? -1 : Current.Game.GetHashCode();",
     "            int generation = cachedGeneration;"),

    ("inhabitant selection stops filtering on depth", INHAB,
     "family.minDepth <= depth", "family.minDepth >= 0"),

    ("wealth stops reaching the band", INHAB,
     "            float wealth = CoordinatePressureLadder.ColonyWealth();",
     "            float wealth = 0f;"),

    ("inhabitant selection stops being seeded", INHAB,
     "        private static int DestinationServiceSeed(CoordinateRecord coordinate)",
     "        private static int NotSeeded(CoordinateRecord coordinate)"),

    ("the band floor comes off the inhabitant def", IDEF,
     "        public CoordinatePressureLadder.Band minBand",
     "        internal CoordinatePressureLadder.Band minBand"),

    ("rock stops coming from the world's own types", GEN,
     "Find.World.NaturalRockTypesIn(map.Tile)", "System.Linq.Enumerable.Empty<ThingDef>()"),
    # ------------------------------------------ 0.12.52-dev: every type, for all things, randomly
    ("LEVEL ZERO STOPS BEING THE STANDARD YELLOW STYLE", MAT,
     "            if (depth > CoherentDepth)", "            if (depth >= 0)"),

    ("the coherent band swallows every depth", MAT,
     "        internal const int CoherentDepth = 1;", "        internal const int CoherentDepth = 99;"),

    ("the yellow-room palette widens until it is not monotonous", MAT,
     "        private const int ShallowPaletteSize = 2;",
     "        private const int ShallowPaletteSize = 9;"),

    ("DEEPER IN STOPS DRAWING FROM EVERY TYPE CORE ALLOWS", MAT,
     "            List<ThingDef> allowed = GenStuff.AllowedStuffsFor(definition)",
     "            List<ThingDef> allowed = new List<ThingDef>(PaletteFor(coordinate))"),

    ("the wild path stops being indexed per fixture", MAT,
     '                    (coordinate.Id ?? "") + ":wild:" + definition.defName + ":" + variant,',
     '                    (coordinate.Id ?? "") + ":wild",'),

    ("THE WILD PATH STOPS BEING SORTED AND A MOD LIST CHANGES A COORDINATE", MAT,
     "                .OrderBy(candidate => candidate.defName, StringComparer.Ordinal)" + chr(10)
     + "                .ToList();",
     "                .ToList();"),

    ("the wild path stops honouring Core's stuff-generation opt-out", MAT,
     "                    candidate.stuffProps.allowedInStuffGeneration)",
     "                    true)"),

    ("a Rand call creeps into the wild path", MAT,
     "            return allowed[Math.Abs(seed) % allowed.Count];",
     "            return allowed[Rand.Range(0, allowed.Count)];"),

    ("a def with no allowed material fails the pass instead of falling through", MAT,
     "            if (allowed.Count == 0) { return null; }",
     "            if (allowed.Count == 0) { return allowed[0]; }"),

    # Disambiguated when StuffForRoom was added: the same line now exists in both, and the
    # harness refused to run rather than score the wrong one. The preceding condition is what
    # tells them apart - `depth` in StuffFor, `effective` in StuffForRoom.
    ("the wild result is computed and then ignored", MAT,
     "            if (depth > CoherentDepth)" + NL
     + "            {" + NL
     + "                ThingDef wild = WildStuffFor(definition, coordinate, variant);" + NL
     + "                if (wild != null) { return wild; }",
     "            if (depth > CoherentDepth)" + NL
     + "            {" + NL
     + "                ThingDef wild = WildStuffFor(definition, coordinate, variant);" + NL
     + "                if (false) { return wild; }"),

    # ------------------------------------------- the yellow look stops being local to the hall
    ("THE WHOLE FLOOR GOES BACK TO ONE MATERIAL, not just the spawn hall", GEN,
     "int wallDepth = RoomArchetypeService.EffectiveDepth(coordinate, room, coordinate.Depth);",
     "int wallDepth = coordinate.Depth;"),

    ("the per-room wall choice is computed and then ignored", GEN,
     "CoordinateMaterials.StuffForRoom(wallDef, coordinate, room, room.Index)",
     "CoordinateMaterials.StuffFor(wallDef, coordinate, room.Index)"),

    ("StuffForRoom stops looking at the room at all", MAT,
     "            int effective = RoomArchetypeService.EffectiveDepth(coordinate, room, depth);",
     "            int effective = depth;"),

    ("TWO IDENTICAL FIXTURES IN ONE ROOM GO BACK TO ONE MATERIAL", CONTENT,
     "                    CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot));",
     "                    CoordinateMaterials.StuffFor(definition, coordinate, 0));"),

    # Anchored on the whole statement: the 16-space form is a substring of the 20-space one in
    # TryPlace, so a bare indented line matches twice and the harness refuses to run.
    ("only one of the two placement helpers passes a variant", CONTENT,
     "            Thing thing = ThingMaker.MakeThing(definition," + chr(10)
     + "                CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot));",
     "            Thing thing = ThingMaker.MakeThing(definition," + chr(10)
     + "                CoordinateMaterials.StuffFor(definition, coordinate, 0));"),

    ("WALLS GO BACK TO ONE MATERIAL FOR THE WHOLE LEVEL", GEN,
     "                ThingDef roomWallStuff = wallDepth <= CoordinateMaterials.CoherentDepth" + NL
     + "                    ? wallStuff" + NL
     + "                    : (CoordinateMaterials.StuffForRoom(wallDef, coordinate, room, room.Index) ?? wallStuff);",
     "                ThingDef roomWallStuff = wallStuff;"),

    ("the spawn hall loses its wood walls, so the arrival stops reading as the Backrooms", GEN,
     "wallDepth <= CoordinateMaterials.CoherentDepth" + NL + "                    ? wallStuff",
     "false" + NL + "                    ? wallStuff"),

    ("the wall material loses its fallback", GEN,
     "(CoordinateMaterials.StuffForRoom(wallDef, coordinate, room, room.Index) ?? wallStuff);",
     "CoordinateMaterials.StuffForRoom(wallDef, coordinate, room, room.Index);"),

    # ------------------------------------------ 0.12.54-dev: the scale sweep
    ("THE CONDUIT CAP GOES BACK TO THE 60x60 NUMBER", GEN,
     "        private const int MaxNativePowerConduits = 4000;",
     "        private const int MaxNativePowerConduits = 512;"),

    ("the cap is raised so high it can never bind", GEN,
     "        private const int MaxNativePowerConduits = 4000;",
     "        private const int MaxNativePowerConduits = 400000;"),

    ("AN UNREACHABLE CONSUMER DESTROYS THE COORDINATE AGAIN", GEN,
     "            if (!destination.IsValid) { return new List<IntVec3>(); }",
     '            if (!destination.IsValid) { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }'),

    ("a broken conduit trail destroys the coordinate again", GEN,
     "                if (!previous.TryGetValue(cursor, out predecessor)) { return new List<IntVec3>(); }",
     '                if (!previous.TryGetValue(cursor, out predecessor)) { throw new InvalidOperationException("RR_Generation_ContentPlacementFailed"); }'),

    ("the known-consumer routes go back to the throwing placement", GEN,
     "                // An empty route means this consumer could not be reached. Skipped, not fatal:" + chr(10)
     + "                // the same rule the stray pass and the power validation already follow." + chr(10)
     + "                for (int step = 0; step < route.Count; step++)" + chr(10)
     + "                {" + chr(10)
     + "                    if (wiredCells.Count >= MaxNativePowerConduits) { break; }" + chr(10)
     + "                    TrySpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells);",
     "                for (int step = 0; step < route.Count; step++)" + chr(10)
     + "                {" + chr(10)
     + "                    SpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells);"),

    ("one of the two cap guards goes", GEN,
     "                if (wiredCells.Count >= MaxNativePowerConduits) { break; }" + chr(10)
     + "                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells, consumer);",
     "                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells, consumer);"),

    # ------------------------------------------ 0.12.53-dev: the conduit blowout
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

    # The call line now exists in BOTH wiring loops, so it is anchored on the `return` that only
    # the stray pass uses -- the consumer loop uses `break`. Duplicate-string trap, again.
    ("THE STRAY PASS STARTS THROWING AND CAN COST THE COORDINATE", GEN,
     "                    if (wiredCells.Count >= MaxNativePowerConduits) { return; }" + chr(10)
     + "                    TrySpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells);",
     "                    if (wiredCells.Count >= MaxNativePowerConduits) { return; }" + chr(10)
     + "                    SpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells);"),

    ("the non-throwing conduit form disappears", GEN,
     "        private static void TrySpawnNativeConduit(Map map, TerrainDef voidFloor, ThingDef conduitDef,",
     "        private static void TrySpawnNativeConduitUnused(Map map, TerrainDef voidFloor, ThingDef conduitDef,"),

    ("the stray pass stops respecting the conduit cap", GEN,
     "                if (wiredCells.Count >= MaxNativePowerConduits) { return; }" + chr(10)
     + "                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells,",
     "                List<IntVec3> route = FindConduitRoute(map, voidFloor, wiredCells,"),

    # ------------------------------------------ 0.12.48-dev: the light count that killed everything
    ("THE LIGHT COUNT FORMULA COMES BACK", GEN,
     "                string powerFault = ValidateNativePowerNetwork(map, generator, climate, placedLights);",
     "                int expectedPowerLights = coordinate.Rooms.Count;" + chr(10)
     + "                string powerFault = ValidateNativePowerNetwork(map, generator, climate, placedLights);"),

    ("the validator stops reading the lights that were placed", GEN,
     "                    placedLights.Add(light);" + chr(10), ""),

    ("THE MAP-WIDE CONSUMER SWEEP GOES", GEN,
     "            foreach (Thing thing in map.listerThings.AllThings)",
     "            foreach (Thing thing in new List<Thing>())"),

    ("the sweep stops looking for power consumers", GEN,
     "                if (thing.TryGetComp<CompPowerTrader>() != null) { consumers.Add(thing); }" + chr(10), ""),

    ("A POWER FAULT BECOMES FATAL AGAIN", GEN,
     "                if (powerFault != null)" + chr(10) + "                {" + chr(10)
     + '                    Log.Warning("[Rimrooms][Generation] Coordinate " + coordinate.Id +',
     "                if (powerFault != null)" + chr(10) + "                {" + chr(10)
     + "                    throw new InvalidOperationException(\"RR_Generation_ContentPlacementFailed\");" + chr(10)
     + '                    Log.Warning("[Rimrooms][Generation] Coordinate " + coordinate.Id +'),

    ("the power fault stops being reported at all", GEN,
     "                if (powerFault != null)", "                if (false)"),

    ("the structural validation stops running", GEN,
     "                ValidatePlacedLayout(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);" + chr(10),
     ""),

    ("THE WALL LAMP GOES BACK TO FLOATING OVER THE FLOOR", GEN,
     "                    GenSpawn.Spawn(light, lightCells[index], map, lightFacings[index]);",
     "                    GenSpawn.Spawn(light, lightCells[index], map, Rot4.North);"),

    ("the lamp stops being mounted on a wall", GEN,
     "                bool wallMounted = lightDef.building != null && lightDef.building.isAttachment;",
     "                bool wallMounted = false;"),

    ("the placement starts naming WallLamp instead of reading the def", GEN,
     "                bool wallMounted = lightDef.building != null && lightDef.building.isAttachment;",
     '                bool wallMounted = lightDef.defName == "WallLamp";'),

    ("the facing stops pointing at the wall", GEN,
     "                    facing = Rot4.FromIntVec3(direction);", "                    facing = Rot4.North;"),

    ("a lamp may be mounted on a door", GEN,
     "                    if (wall == null || wall.def != wallDef) { continue; }",
     "                    if (wall == null) { continue; }"),

    ("A ROOM WITH NOWHERE TO MOUNT FAILS THE COORDINATE AGAIN", GEN,
     "            return IntVec3.Invalid;",
     '            throw new InvalidOperationException("RR_Generation_NoSafeRoomCell");'),

    ("the fallback to a floor-standing cell goes", GEN,
     "                    if (!lightCell.IsValid)", "                    if (false)"),

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


caught = 0
for label, path, old, new in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) != 1:
        print("PLANT SETUP BROKEN (%d matches): %s" % (original.count(old), label))
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
