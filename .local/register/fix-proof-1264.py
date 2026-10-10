# -*- coding: utf-8 -*-
"""Claims for the wiring order and the guarded rebuild.

The conduit guard added at 0.12.63-dev was correct and ran too early to see anything: conduits
were laid **before** the generator, the climate unit, the ceiling lights and the pillar lamps were
spawned, so every powered building in the coordinate landed on a cell that already held one of
ours. A mod that attaches a hidden conduit under a powered building then makes a second
transmitter on that cell, Core refuses it, and the rebuild throws out of `GenStep.Generate` --
which stopped the level, so the gate door was never marked.

Two claims, because there are two independent guarantees now: the duplicate should not happen, and
if it happens anyway it cannot cost the coordinate.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

NEW = u'''# -------------------------------------------- the wiring goes down last
# **THE GUARD WAS RIGHT AND RAN TOO EARLY.** `SpawnNativePowerNetwork` was the first thing in the
# generator, before the generator building, the climate unit, the ceiling lights and the pillar
# lamps existed -- so conduits went onto empty cells and every powered building was then spawned
# on top of one. Several mods attach a hidden conduit under a powered building automatically, so
# that is a second transmitter on a cell that already had ours, on every one of those cells.
check("THE CONDUITS ARE LAID AFTER EVERYTHING THAT DRAWS POWER EXISTS",
      genstep.index("RoomContentBuilder.Populate(map, coordinate, entryCell")
      < genstep.index("HashSet<IntVec3> wiredCells = SpawnNativePowerNetwork(")
      and genstep.index("SpawnPillarLamps(map, coordinate, wallDef, lightDef, wallMounted,")
      < genstep.index("HashSet<IntVec3> wiredCells = SpawnNativePowerNetwork("),
      "-- the ORDER is the fix. `AlreadyTransmits` can only answer truthfully about cells that "
      "already hold what they are going to hold, and a conduit is not an edifice and does not "
      "block standability, so nothing placed above it changes")

check("and a power-grid failure can no longer cost the coordinate",
      "private static void RebuildPowerNets(Map map, CoordinateRecord coordinate)" in genstep
      and "try { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }" in genstep
      and genstep.count("map.powerNetManager.UpdatePowerNetsAndConnections_First();") == 1
      and genstep.count("RebuildPowerNets(map, coordinate);") == 3,
      "-- THREE call sites, one implementation. Core throws out of the rebuild when its "
      "transmitter bookkeeping is inconsistent, and because that runs inside `GenStep.Generate` "
      "the throw stopped the whole level: the map existed unfinished, `EnsureSite` reported "
      "failure and `SoloGroupOpening` never marked the gate door. **The decision was already "
      "written down twelve lines below** about the power validation -- *\\"a coordinate whose "
      "heater or one lamp failed to join the grid is dark and cold and completely playable. A "
      "coordinate that does not exist costs the player the gate that leads to it\\"* -- and the "
      "rebuild it validates did not honour it")

check("and the dead throwing conduit spawner is gone rather than left to be called",
      "private static void SpawnNativeConduit(" not in genstep,
      "-- it had no callers and threw `RR_Generation_ContentPlacementFailed` on a cell that could "
      "not take a conduit, which is the exact behaviour this checkpoint removed everywhere else")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("three claims added for the wiring order and the guarded rebuild")
