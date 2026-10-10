# -*- coding: utf-8 -*-
"""Claims for the hallways and the food, and the last three stale plants.

Five corridor plants came back MISSED, and the reason is the honest one: **I had added no claim
for any of the corridor work.** A plant that nothing refuses is a plant telling you a guarantee
does not exist yet, which is exactly what it was for.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")
LAYOUT = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")
LINKS = os.path.join(REPO, ".local", "register", "plant-gate-links-carry.py")
GENERATION = os.path.join(REPO, ".local", "register", "plant-generation.py")

# ------------------------------------------------------------------- the claims
ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

CLAIMS = u'''# ------------------------------------------------------- a hallway is a room
# Owner: *"the hall ways are just rectangles and arnt correctly the themed color and materials"*,
# and *"i see the whole map is almost like a string of pears. when it should just be basicly
# \\"rooms\\" as halways with the exact shit thats in the rooms"*.
#
# **Two hardcoded values were the whole of it.** The corridor floor was the raw carve terrain --
# `concrete`, what rock becomes when you clear it -- while every room got the band's palette floor
# from `PaintRoom`. And the corridor walls were `ThingDefOf.Steel`, literally, while a room's
# walls come from the coordinate's own materials and carry the band's colour. A themed yellow room
# opened onto a grey steel tunnel, on every link, at every depth.
#
# `docs/UNIVERSE_ADAPTATION.md` had already said so: a coordinate is *"made of rooms and routes"*
# and the instruction is to *"reuse recognizable room categories, materials, fluorescent lighting,
# service infrastructure, and furniture as the baseline"*.
check("A CORRIDOR IS FLOORED AND WALLED LIKE THE ROOMS IT JOINS",
      "private static void PaintCorridorCell(" in genstep
      and "BackroomsPalette.SetFloor(map, cell, terrain, look.floorColor);" in genstep
      and "private static void PlaceCorridorWall(" in genstep
      and "PlaceWall(map, cell, wallDef, wallStuff);" in genstep
      and "wall.TryGetComp<CompColorable>()?.SetColor(look.wallColor);" in genstep
      and "PlaceWall(map, new IntVec3(x, 0, centerZ - halfWidth), ThingDefOf.Wall, ThingDefOf.Steel)"
      not in genstep,
      "-- the palette comes from `BackroomsPalette.SetFloor`, which is the call `PaintRoom` makes, "
      "so a corridor cannot drift from the rooms it joins. And the hardcoded steel is GONE, not "
      "merely overridden")

check("and the hallways are lit and furnished, against their walls only",
      "private static void DressCorridors(" in genstep
      and "DressCorridors(map, coordinate, corridorSides, lightDef, placedLights," in genstep
      and "if (offset != 0 && (offset == halfWidth - 1 || offset == 1 - halfWidth))" in genstep
      and "CorridorLampSpacing" in genstep and "CorridorFixtureSpacing" in genstep,
      "-- DEFINED AND CALLED. `BuildCorridors` reports the cells one in from each corridor wall "
      "and **never the centre line**, so everything placed is against a wall and the route stays "
      "as clear as a room's reserved cross. A collected list nothing spends is this run's most "
      "repeated defect")

check("and a corridor fixture can never be wider than one cell",
      "if (definition.size.x != 1 || definition.size.z != 1) { continue; }" in genstep,
      "-- a wider footprint against a corridor wall is how a route stops being a route")

# --------------------------------------------------------------- food down there
# Owner: *"there wasnt enough \\"people-food\\" in the back rooms need to be able to survive a bit
# if it was a solo start"*. Food was in ONE of sixteen archetypes, behind `minDepth 2` and a 70%
# roll -- and the solo start begins inside a coordinate with whatever the coordinate holds.
check("A COORDINATE HOLDS FOOD, IN MORE THAN ONE KIND OF ROOM",
      archetypes.count("<category>FoodMeals</category>") >= 3
      and archetypes.count("<category>FoodRaw</category>") >= 2,
      "-- the canteen, the storeroom and the dormitory. The storeroom carries the highest weight "
      "of any archetype at 1.4, so that is the one that actually feeds somebody")

check("and the canteen can appear on a FIRST level",
      "<defName>RR_Room_Canteen</defName>" in archetypes
      and canteen_block is not None
      and "<minDepth>1</minDepth>" in canteen_block,
      "-- it was `minDepth 2`, so the level the owner walked could not contain the only room in "
      "the library that held anything to eat")

''' + ANCHOR

BINDING_ANCHOR = u'''genstep = strip_cs_comments(read(os.path.join(SRC, "Generation",'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1 or text.count(BINDING_ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d / %d" % (text.count(ANCHOR), text.count(BINDING_ANCHOR)))
    raise SystemExit(1)

# The archetype defs, and the canteen's own block, bound beside the other file reads.
index = text.index(BINDING_ANCHOR)
line_end = text.index(u"\n", text.index(u"\n", index) + 1) + 1
binding = (u'archetypes = read(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6",\n'
           u'                              "Defs", "RimroomsRoomArchetypeDefs",\n'
           u'                              "RR_RoomArchetypes.xml"))\n'
           u'# The canteen\'s own block, so a claim about its depth cannot be satisfied by some\n'
           u'# other archetype\'s minDepth somewhere else in the same file.\n'
           u'_c = archetypes.find("<defName>RR_Room_Canteen</defName>")\n'
           u'canteen_block = None if _c < 0 else archetypes[_c:archetypes.find("</Rimrooms'
           u'AsyncIndustries.Generation.RimroomsRoomArchetypeDef>", _c)]\n')
text = text[:line_end] + binding + text[line_end:]
text = text.replace(ANCHOR, CLAIMS, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("claims added for the hallways and the food")

# -------------------------------------------------------------- the stale plants
STALE = [
    (LAYOUT,
     u'''     "            int reach = System.Math.Min((depth - 1) * 2, System.Math.Min(extentX - insetX, extentZ - insetZ) / 3);",''',
     u'''     "            int reach = System.Math.Min((depth - 1) * 2," + NL
     + "                System.Math.Min(extentX - insetX, extentZ - insetZ) / 3);",'''),
    (LINKS,
     u'''     "            if (!IsLiveGate) { yield break; }", "            if (false) { yield break; }"),''',
     u'''     "            if (!IsLiveGate)" + chr(10) + "            {", "            if (false)" + chr(10) + "            {"),'''),
    (GENERATION,
     u'''    ("furniture lands on the middle of a corridor and blocks the route", GEN,
     "                                if (offset != 0 && (offset == halfWidth - 1 || offset == 1 - halfWidth))"
     + NL + "                                { sides.Add(cell); }",
     "                                sides.Add(cell);"),''',
     u'''    # Anchored on the horizontal run only: the same guard exists on both axes, so the bare
    # condition matches twice and a plant that matches twice proves nothing while looking fine.
    ("furniture lands on the middle of a corridor and blocks the route", GEN,
     "                                SetWalkableRoofedCell(map, cell, look.floor);" + NL
     + "                                PaintCorridorCell(map, cell, look, x);" + NL
     + "                                // One in from the wall, and never the centre line." + NL
     + "                                if (offset != 0 && (offset == halfWidth - 1 || offset == 1 - halfWidth))"
     + NL + "                                { sides.Add(cell); }",
     "                                SetWalkableRoofedCell(map, cell, look.floor);" + NL
     + "                                PaintCorridorCell(map, cell, look, x);" + NL
     + "                                sides.Add(cell);"),'''),
]

for path, old, new in STALE:
    body = io.open(path, encoding="utf-8").read()
    if body.count(old) != 1:
        print("STALE ANCHOR PROBLEM in %s: %d of %r"
              % (os.path.basename(path), body.count(old), old[:58]))
        raise SystemExit(1)
    io.open(path, "w", encoding="utf-8", newline="").write(body.replace(old, new, 1))
    print("refreshed a plant in %s" % os.path.basename(path))
