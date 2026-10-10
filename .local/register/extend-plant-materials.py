# -*- coding: utf-8 -*-
"""Plants for the wild-materials claims."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-generation.py")

text = io.open(PLANT, encoding="utf-8").read()
ANCHOR = "    # ------------------------------------------ 0.12.48-dev: the light count that killed everything"

NEW = '''    # ------------------------------------------ 0.12.52-dev: the wild variation of materials
    ("THE PALETTE GOES BACK TO A FLAT SIZE AT EVERY DEPTH", MAT,
     "            int size = ShallowPaletteSize + (depth < 1 ? 0 : depth - 1);",
     "            int size = ShallowPaletteSize;"),

    ("the palette size stops being consulted", MAT,
     "            int wanted = PaletteSizeFor(coordinate == null ? 1 : coordinate.Depth);",
     "            int wanted = ShallowPaletteSize;"),

    ("the deep palette shrinks below the shallow one", MAT,
     "        private const int DeepPaletteSize = 6;",
     "        private const int DeepPaletteSize = 1;"),

    ("THE SHALLOWEST BAND STOPS BEING MONOTONOUS", MAT,
     "        private const int ShallowPaletteSize = 2;",
     "        private const int ShallowPaletteSize = 6;"),

    ("the deepest palette grows without bound", MAT,
     "        private const int DeepPaletteSize = 6;",
     "        private const int DeepPaletteSize = 40;"),

    ("THE CACHE FORGETS DEPTH AND SERVES A SHALLOW PALETTE DEEP DOWN", MAT,
     'string key = coordinate == null ? "" : (coordinate.Id ?? "") + ":" + coordinate.Depth;',
     'string key = coordinate == null ? "" : coordinate.Id ?? "";'),

    ("THE DRESSING PATH GOES BACK TO CORE'S DEFAULT MATERIAL", CONTENT,
     "                thing = ThingMaker.MakeThing(definition," + chr(10)
     + "                    CoordinateMaterials.StuffFor(definition, coordinate));",
     "                thing = ThingMaker.MakeThing(definition," + chr(10)
     + "                    definition.MadeFromStuff ? GenStuff.DefaultStuffFor(definition) : null);"),

    ("WALLS GO BACK TO ONE OF TWO NAMED MATERIALS", GEN,
     "                ThingDef wallStuff = coordinate.Depth <= 1 ? bandWallStuff" + chr(10)
     + "                    : (CoordinateMaterials.StuffFor(wallDef, coordinate) ?? bandWallStuff);",
     "                ThingDef wallStuff = bandWallStuff;"),

    ("the surface band loses its wood walls", GEN,
     "ThingDef wallStuff = coordinate.Depth <= 1 ? bandWallStuff",
     "ThingDef wallStuff = false ? bandWallStuff"),

    ("the wall material loses its fallback", GEN,
     "(CoordinateMaterials.StuffFor(wallDef, coordinate) ?? bandWallStuff);",
     "CoordinateMaterials.StuffFor(wallDef, coordinate);"),

''' + ANCHOR

if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)

io.open(PLANT, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("material plants added")
