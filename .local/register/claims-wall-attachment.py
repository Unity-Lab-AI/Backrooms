# -*- coding: utf-8 -*-
"""Claims and plants for the wall attachment that had no wall: the second launch's defect."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-generation.py")

ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

CLAIMS = u'''# ------------------------------------ the wall lamp that had no wall behind it
# `PowerConnectionMaker.TryConnectToAnyPowerNet`, Core 1.6, dereferences
# `GenConstruct.GetWallAttachedTo(pc.parent).Position` for any `isAttachment` def WITHOUT a null
# check. `BackroomsPalette` resolves `WallLamp`, which is one. Core's power rebuild is step four of
# fifteen in `Map.FinalizeInit`, so the throw discarded the finished level, `EnsureSite` reported
# failure, and `SoloGroupOpening` never moved anybody inside. Owner: *"why are my colonists on the
# world map!!!!!!!!! they should be in the backrooms in this scenerio"*.
#
# And: *"we loaded solo/group start into the backrooms correctly before"* -- **they did.**
# `FindWallAttachmentCell` finds the wall and then faces it, and for a long time it was the only
# placer. The two added after it both got the arithmetic wrong.
check("THE ATTACHMENT RULE IS ASKED OF CORE'S OWN FUNCTION",
      "private static bool WallAttachmentHolds(Map map, ThingDef def, IntVec3 cell, Rot4 facing)"
      in genstep
      and "return GenConstruct.GetWallAttachedTo(cell, facing, map) != null;" in genstep
      and "if (map == null || def == null || def.building == null || !def.building.isAttachment)"
      in genstep,
      "-- Core is what dereferences the answer, so Core is the only thing whose opinion matters. A "
      "local copy of the rule could disagree with it, and that disagreement is this project's most "
      "expensive defect shape")

check("ONE SPAWNER PLACES EVERY LAMP, and it refuses an unattached one",
      "private static Thing SpawnAttachableLight(Map map, ThingDef lightDef, ThingDef floorLightDef,"
      in genstep
      and genstep.count("SpawnAttachableLight(map,") == 3
      # Not one bare spawn of a light or lamp left anywhere in the generator.
      and "GenSpawn.Spawn(lamp," not in genstep
      and genstep.count("GenSpawn.Spawn(light,") == 1,
      "-- the room lights, the pillar lamps and the corridor dressing. All three placed a WallLamp "
      "their own way and two of the three were wrong; a rule enforced in one place cannot be "
      "forgotten by the next placer somebody adds")

check("THE PILLAR LAMP FACES THE PILLAR, which is the opposite of what it did",
      "Rot4 facing = Rot4.FromIntVec3(directions[side]).Opposite;" in genstep
      and "if (!WallAttachmentHolds(map, lightDef, cell, facing)) { continue; }" in genstep,
      "-- Core reads the wall at `position + rotation.FacingCell`, so a lamp one cell north of a "
      "pillar must face SOUTH. Facing north looked two cells past the pillar, found open floor, "
      "and handed Core a null wall. The comment's intent was right and the arithmetic was inverted")

check("and the corridor lamp no longer assumes a wall to the north",
      "Thing lamp = SpawnAttachableLight(map, lightDef, floorLightDef, cell, Rot4.North);" in genstep
      and "for (int index = 0; index < 4; index++)" in genstep
      and "if (!WallAttachmentHolds(map, lightDef, cell, candidate)) { continue; }" in genstep,
      "-- a corridor side cell has its wall on exactly one side and almost never the north one, "
      "so the spawner tries all four before giving up on the fixture")

check("and a room with no wall to mount on gets a FLOOR lamp, not the wall fixture",
      'ThingDef floorLightDef = DefDatabase<ThingDef>.GetNamedSilentFail("StandingLamp");'
      in genstep
      and "roomLightDef = wallMounted ? floorLightDef ?? lightDef : lightDef;" in genstep
      and "lightDefs.Add(roomLightDef);" in genstep
      and "lightDefs[index].size));" in genstep,
      "-- this used to fall through placing the palette's WallLamp on an open floor cell facing "
      "north. The room still gets a light, which is what *\\"the basic rooms are well lit\\"* asked "
      "for; it is a standing one, which is the palette's own fallback")

check("AND A SWEEP CATCHES WHATEVER STILL SLIPS THROUGH, before Core is asked to wire",
      "private static void RemoveUnattachedAttachments(Map map, CoordinateRecord coordinate,"
      in genstep
      and "GenConstruct.GetWallAttachedTo(thing) == null)" in genstep
      and "thing.Destroy(DestroyMode.Vanish);" in genstep
      and "if (placedLights != null) { placedLights.Remove(thing); }" in genstep
      and genstep.index("RemoveUnattachedAttachments(map, coordinate, placedLights);")
      < genstep.index("HashSet<IntVec3> wiredCells = SpawnNativePowerNetwork("),
      "-- the rule has three obedient callers; this is what makes the FOURTH harmless. It also "
      "covers the archetype dressing, which spawns arbitrary modded defs at a scattered facing "
      "and never checked. The worst case is a dark corner")

check("and the removed lamp leaves the power validation's list with it",
      "RemoveUnattachedAttachments(map, coordinate, placedLights);" in genstep
      and genstep.index("RemoveUnattachedAttachments(map, coordinate, placedLights);")
      < genstep.index("string powerFault = ValidateNativePowerNetwork("),
      "-- the validation reads the lights that were PLACED rather than recounting them, which is "
      "the fix that ended thirty-nine checkpoints of dead coordinates. A destroyed lamp left in "
      "that list would report a fault that is not there")

check("and a corridor fixture is checked too, not only the lamp",
      "if (!WallAttachmentHolds(map, definition, cell, Rot4.North)) { continue; }" in genstep,
      "-- they are Core defs by name, but a profile is free to patch one into an attachment, and "
      "an unattached attachment costs the whole level")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, CLAIMS, 1))
print("eight claims added for the wall attachment")

P_ANCHOR = u"PLANTS = ["
P_NEW = u'''PLANTS = [
    # ------------------------------ the wall attachment that had no wall behind it
    ("THE ATTACHMENT RULE STOPS ASKING CORE", GEN,
     "            return GenConstruct.GetWallAttachedTo(cell, facing, map) != null;",
     "            return true;"),

    ("a non-attachment is treated as needing a wall", GEN,
     "            if (map == null || def == null || def.building == null || !def.building.isAttachment)",
     "            if (map == null || def == null || def.building == null)"),

    ("THE PILLAR LAMP FACES AWAY FROM THE PILLAR AGAIN", GEN,
     "                        Rot4 facing = Rot4.FromIntVec3(directions[side]).Opposite;",
     "                        Rot4 facing = Rot4.FromIntVec3(directions[side]);"),

    ("the pillar lamp stops checking that it attached", GEN,
     "                        if (!WallAttachmentHolds(map, lightDef, cell, facing)) { continue; }" + NL,
     ""),

    ("THE CORRIDOR LAMP GOES BACK TO A BARE NORTH-FACING SPAWN", GEN,
     "                    Thing lamp = SpawnAttachableLight(map, lightDef, floorLightDef, cell, Rot4.North);",
     "                    Thing lamp = MakeBuilding(lightDef, null);" + NL
     + "                    GenSpawn.Spawn(lamp, cell, map, Rot4.North);"),

    ("the spawner stops trying the other three walls", GEN,
     "                for (int index = 0; index < 4; index++)" + NL
     + "                {" + NL
     + "                    var candidate = new Rot4(index);" + NL
     + "                    if (!WallAttachmentHolds(map, lightDef, cell, candidate)) { continue; }",
     "                for (int index = 0; index < 0; index++)" + NL
     + "                {" + NL
     + "                    var candidate = new Rot4(index);" + NL
     + "                    if (!WallAttachmentHolds(map, lightDef, cell, candidate)) { continue; }"),

    ("A ROOM WITH NO WALL GETS THE WALL FIXTURE ON THE FLOOR AGAIN", GEN,
     "                        roomLightDef = wallMounted ? floorLightDef ?? lightDef : lightDef;",
     "                        roomLightDef = lightDef;"),

    ("the floor-standing fallback is never resolved", GEN,
     '                ThingDef floorLightDef = DefDatabase<ThingDef>.GetNamedSilentFail("StandingLamp");',
     "                ThingDef floorLightDef = null;"),

    ("THE SWEEP THAT CATCHES THE FOURTH PLACER GOES", GEN,
     "                RemoveUnattachedAttachments(map, coordinate, placedLights);" + NL,
     ""),

    ("the sweep finds them and leaves them standing", GEN,
     "                thing.Destroy(DestroyMode.Vanish);",
     "                thing.SetForbidden(false, false);"),

    ("a swept lamp stays in the list the power validation reads", GEN,
     "                if (placedLights != null) { placedLights.Remove(thing); }" + NL,
     ""),

    ("the sweep runs after Core has already been asked to wire", GEN,
     "                RemoveUnattachedAttachments(map, coordinate, placedLights);" + NL + NL
     + "                HashSet<IntVec3> wiredCells = SpawnNativePowerNetwork(",
     "                HashSet<IntVec3> wiredCells = SpawnNativePowerNetwork("),

    ("a corridor fixture stops being checked", GEN,
     "                if (!WallAttachmentHolds(map, definition, cell, Rot4.North)) { continue; }" + NL,
     ""),
'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(P_ANCHOR))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite.replace(P_ANCHOR, P_NEW, 1))
print("thirteen plants added")
