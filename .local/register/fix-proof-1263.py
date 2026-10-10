# -*- coding: utf-8 -*-
"""Claims for the three fixes that came out of the eleventh launch.

None of them were asserted by anything. A fix nobody claims is a fix that comes back out.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

NEW = u'''# ------------------------------------------- furniture must never cost a level
# **A FURNITURE PLACEMENT RULE STOPPED A LEVEL BEING BUILT.** `Place` refused any cell whose
# footprint had an edifice within one, and the room's wall, its pillar lattice, the rock in its
# shaped corners, the lamp on every pillar and every fixture already placed are all edifices --
# on top of the three-cell route cross, which `Populate` reserves outright. A room could be left
# with one placeable cell, the first fixture took it, and the second threw out of
# `GenStep.Generate`. The owner got a Backrooms map with no content and a door that was never
# marked: *"i see the backrooms is there but the gate natural door is not"*.
check("THE WALKABLE MARGIN IS A PREFERENCE, NOT A REQUIREMENT",
      "private static IntVec3 FixtureCell(" in content
      and "IntVec3 withoutMargin = IntVec3.Invalid;" in content
      and "if (!withoutMargin.IsValid) { withoutMargin = cell; }" in content
      and "return withoutMargin;" in content,
      "-- the reserved route cross is what keeps a room walkable, and it is reserved separately "
      "and unconditionally. A fixture with no margin is a fixture against a wall")

check("and ONE function finds the cell, for every caller",
      content.count("FixtureCell(map, room, reserved, thing, rotation, preferred)") == 2
      and content.count("OrderBy(c => c.DistanceToSquared(preferred))") == 1,
      "-- `TryPlace` kept its own copy of the search loop. Two derivations of one rule is the "
      "defect that cost this project thirty-nine checkpoints")

check("ONLY THE LANDMARK IS REQUIRED; EVERY OTHER FIXTURE IS SCENERY",
      "private static Thing Decorate(" in content
      and "count, false);" in content
      and "count, true);" in content
      and 'if (required)' in content
      and content.count("Decorate(map, room, coordinate,") >= 12,
      "-- `ValidatePlacedLayout` requires exactly one clue per room and the clue is the "
      "landmark, so that one is refused loudly. A second stool is a second stool, and "
      "`DressRoom` four lines below already said so: *\\"failing generation because a decorative "
      "shelf had nowhere to go would take a working coordinate away from a player over "
      "scenery\\"*")

check("and no family fixture other than a landmark still throws",
      content.count("landmark = Place(map, room, coordinate,") >= 7
      and 'Place(map, room, coordinate, "Stool", reserved, seed, 1)' not in content
      and 'Place(map, room, coordinate, "Shelf", reserved, seed, 0);' not in content,
      "-- the twelve decoration call sites are the ones that could throw and had no reason to")

check("A LANDMARK REFUSAL SAYS WHICH ROOM",
      "No cell for the landmark " in content
      and "room.familyId" in content and "room.width" in content,
      "-- last time this threw, the log carried the method and a key and nothing else, so the "
      "room had to be reasoned about from the arithmetic of every room it could have been")

check("and the route cross is derived in exactly one place",
      "internal static bool OnRouteCross(" in content
      and "if (OnRouteCross(room, cell)) { reserved.Add(cell); } }" in content,
      "-- the layout probe counts placeable cells against it, so a second copy of the rule would "
      "let the probe and the generator disagree about what is reserved")

# -------------------------------------------------- two transmitters on one cell
# Core refuses the second transmitter on a cell and leaves its own bookkeeping inconsistent, so
# `PowerConnectionMaker.TryConnectToAnyPowerNet` threw out of `Map.FinalizeInit` and then out of
# every Update for the rest of the session. Hundreds of them in the owner's log.
check("A CONDUIT IS NEVER PUT ON A CELL THAT ALREADY TRANSMITS",
      "private static bool AlreadyTransmits(Map map, IntVec3 cell)" in genstep
      and "thing.def.EverTransmitsPower" in genstep
      and genstep.count("if (AlreadyTransmits(map, cell)) { return; }") == 2,
      "-- BOTH spawn paths, because `wiredCells` is this generator's own bookkeeping and cannot "
      "see a transmitter somebody else put there. Several mods in the owner's profile attach a "
      "hidden conduit under a powered building, and the lamps this generator puts on every "
      "pillar are powered buildings")

check("and it asks Core's own property rather than naming a def",
      "List<Thing> things = cell.GetThingList(map);" in genstep
      and 'GetNamedSilentFail("HiddenConduit")' in genstep,
      "-- `EverTransmitsPower` is the same property `PowerNetManager` registers on, so this "
      "cannot disagree with the thing that refuses the duplicate. The point is that we did not "
      "put the other transmitter there, so we cannot know its def")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("eight claims added for the margin, the landmark split and the conduit guard")
