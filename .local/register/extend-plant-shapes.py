# -*- coding: utf-8 -*-
"""Plants for the stage-three shape and corridor-width claims."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")

text = io.open(PLANT, encoding="utf-8").read()
ANCHOR = "    # ------------------------------------------------------ the open-map budget"

NEW = '''    # ------------------------------------------------------ rooms are not rectangles
    ("ROOMS GO BACK TO BEING PLAIN RECTANGLES", PLANNER,
     "            if (room == null || depth <= 1) { yield break; }",
     "            if (room != null) { yield break; }"),

    ("the generator stops leaving any rock standing inside a room", GEN,
     "                    if (intrusions.Contains(cell)) { continue; }" + NL, ""),

    ("THE CENTRE CROSS STARTS GETTING FILLED IN", PLANNER,
     "                        if (x == center.x || z == center.z) { continue; }" + NL, ""),

    ("a corner mass starts reaching into the wall ring", PLANNER,
     "                        if (x <= bounds.minX + 1 || x >= bounds.maxX - 1) { continue; }" + NL,
     ""),

    ("the corner reach stops being clamped to a third of the room", PLANNER,
     "            int reach = System.Math.Min((depth - 1) * 2, System.Math.Min(extentX - insetX, extentZ - insetZ) / 3);",
     "            int reach = (depth - 1) * 2;"),

    ("SHALLOW COORDINATES START DEFORMING TOO", PLANNER,
     "            if (room == null || depth <= 1) { yield break; }",
     "            if (room == null) { yield break; }"),

    ("the planner stops modelling the rock it leaves standing", PLANNER,
     "                foreach (IntVec3 rock in RockIntrusionCells(room, depth))" + NL
     + "                { floor[rock.x, rock.z] = false; }" + NL, ""),

    ("AN UNCARVED CELL LOSES ITS ROOF AND OPENS A HOLE IN THE WORLD", GEN,
     "                    map.roofGrid.SetRoof(cell, overheadRoof);" + NL
     + "                    if (intrusions.Contains(cell)) { continue; }",
     "                    if (intrusions.Contains(cell)) { continue; }" + NL
     + "                    map.roofGrid.SetRoof(cell, overheadRoof);"),

    ("HALLWAYS GO BACK TO ONE WIDTH", GEN,
     "int halfWidth = RoomLayoutPlanner.CorridorHalfWidthBetween(room, other, depth);",
     "int halfWidth = 2;"),

    ("the planner models a corridor width the generator does not carve", PLANNER,
     "                    int reach = CorridorHalfWidthBetween(room, other, depth) - 1;",
     "                    int reach = 1;"),

''' + ANCHOR

if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)

io.open(PLANT, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("stage-three plants added")
