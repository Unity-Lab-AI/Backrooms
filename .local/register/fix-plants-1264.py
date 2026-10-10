# -*- coding: utf-8 -*-
"""Plants for the wiring order and the guarded rebuild."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-generation.py")

ANCHOR = u"PLANTS = ["

NEW = u'''PLANTS = [
    # ------------------------------------ the wiring order, and the rebuild that threw
    # The conduit guard was correct and ran too early to see anything: conduits were laid before
    # the generator, the climate unit, the ceiling lights and the pillar lamps were spawned, so
    # every powered building landed on a cell that already held one of ours. A mod that attaches a
    # hidden conduit under a powered building then makes a second transmitter there, Core refuses
    # it, and the rebuild threw out of GenStep.Generate -- which stopped the level, so the gate
    # door was never marked. Three launches in a row.
    ("THE CONDUITS GO BACK TO BEING LAID BEFORE ANYTHING DRAWS POWER", GEN,
     "                HashSet<IntVec3> wiredCells = SpawnNativePowerNetwork(map, voidFloor, conduitDef,"
     + NL + "                    GenAdj.OccupiedRect(generatorCell, Rot4.North, generatorDef.size), consumerFootprints);"
     + NL + "                // Native spawn notifications are queued; rebuild connections now without ticking",
     "                // Native spawn notifications are queued; rebuild connections now without ticking"),

    ("A POWER-GRID THROW TAKES THE WHOLE LEVEL AGAIN", GEN,
     "            try { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }",
     "            if (true) { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }"),

    ("the rebuild is guarded in one place and bare in another", GEN,
     "                RebuildPowerNets(map, coordinate);" + NL
     + "                // Whatever the dressing just placed that draws power, wired now that it exists.",
     "                map.powerNetManager.UpdatePowerNetsAndConnections_First();" + NL
     + "                // Whatever the dressing just placed that draws power, wired now that it exists."),

    ("and the stray pass stops naming the coordinate it failed on", GEN,
     "                RebuildPowerNets(map, coordinate);" + NL + "            }" + NL + "        }",
     "                map.powerNetManager.UpdatePowerNetsAndConnections_First();" + NL
     + "            }" + NL + "        }"),

    ("THE DEAD THROWING CONDUIT SPAWNER COMES BACK", GEN,
     "        private static bool AlreadyTransmits(Map map, IntVec3 cell)",
     "        private static void SpawnNativeConduit(Map map, TerrainDef voidFloor, ThingDef conduitDef,"
     + NL + "            IntVec3 cell, HashSet<IntVec3> wiredCells)" + NL + "        {" + NL
     + "            if (!wiredCells.Add(cell)) { return; }" + NL
     + "            throw new InvalidOperationException(\\"RR_Generation_ContentPlacementFailed\\");" + NL
     + "        }" + NL + NL
     + "        private static bool AlreadyTransmits(Map map, IntVec3 cell)"),
'''

text = io.open(SUITE, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("five plants added for the wiring order and the guarded rebuild")
