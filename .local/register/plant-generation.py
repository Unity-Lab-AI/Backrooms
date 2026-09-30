# -*- coding: utf-8 -*-
"""Plant a fault, run the generation proof, require exit 1, restore. Verified writes."""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
MAT = SRC + "/Generation/CoordinateMaterials.cs"
CONTENT = SRC + "/Generation/RoomContentBuilder.cs"
INHAB = SRC + "/Threats/InhabitantService.cs"
IDEF = SRC + "/Threats/RimroomsInhabitantDef.cs"
GEN = SRC + "/Generation/GenStep_BackroomsDestination.cs"
PROOF = ".local/register/proof-generation-batch.py"

PLANTS = [
    ("the hardcoded wood comes back", CONTENT,
     "                CoordinateMaterials.StuffFor(definition, coordinate));",
     "                definition.MadeFromStuff ? ThingDefOf.WoodLog : null);"),

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
