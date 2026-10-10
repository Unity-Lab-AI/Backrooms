# -*- coding: utf-8 -*-
"""Claims and plants for the three things just added, because unguarded content rots.

Doors to nowhere, lamp tones, and the two archetypes the owner named by hand. Each one is new
behaviour with nothing asserting it, and this project's whole record is that unguarded behaviour
quietly stops happening -- the glow that never ran, the sizing that was computed and discarded,
the `MakeHall` call a plant deleted while the method sat there.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")
PLANT = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")

proof = io.open(PROOF, encoding="utf-8").read()
ANCHOR = u'check("MOST LEFTOVER SLOTS BECOME BRANCHES, which is what makes it a maze",'

CLAIMS = u'''# ------------------------------------------------------------------ doors to nowhere
# Owner: *"odd contructions of doors walls corners deadends doors to now where not just doors on
# 4 cosides of nothing but square rooms"*. `DoorOpening` was that complaint written as code: an
# opening existed only at the midpoint of a wall facing a linked room.
check("A WALL WITH NOTHING BEHIND IT CAN STILL OPEN",
      "internal static bool FalseOpening(" in planner
      and "return FalseOpening(room, rooms, cell);" in planner,
      "-- defined AND reached from DoorOpening, which is the one function both the validator and "
      "the generator ask. A false door decided anywhere else would be a wall the validator proved "
      "and the generator did not build")

check("it is offset from the centre, because the centre is where a real door goes",
      "int at = low + (high - low) / 3;" in planner,
      "-- a door in the middle of a blank wall reads as a corridor that failed to arrive; a third "
      "along reads as somebody having put a door there")

check("never on the threshold hall",
      "if (room == null || room.index == 0) { return false; }" in planner,
      "-- that is where a player arrives and the one room meant to read as built. The maze starts "
      "after it")

check("and never on a wall that already carries a real doorway",
      "if (side == 0 && other.Bounds.minX > bounds.maxX) { return false; }" in planner,
      "-- two openings in one wall reads as a mistake rather than as a door that goes nowhere")

check("A FALSE OPENING CANNOT DISCONNECT ANYTHING",
      "int walls = (onEastWall ? 1 : 0) + (onWestWall ? 1 : 0)" in planner
      and "if (walls != 1) { return false; }" in planner,
      "-- one wall only, so never a corner, and the cell beyond is rock. It adds a dead end and "
      "removes no route, which is the only property CandidateIsSafe is proving")

# ----------------------------------------------------------------------- lamp tones
# Owner: *"we need more lights and mixedered varies of lights"*.
check("LAMPS DIFFER FROM EACH OTHER, PER INSTANCE",
      "private static void TintLamp(" in genstep
      and "TintLamp(lamp, coordinate, room, pillar);" in genstep,
      "-- CompGlower.GlowColor and GlowRadius are per-instance overrides in Core, the same "
      "mechanism that lights one door blue without touching any other door in the game. Defined "
      "AND called")

check("and the dim one is dimmer, never off",
      "glower.GlowRadius = glower.GlowRadius * 2f / 3f;" in genstep
      and "GlowRadius = 0" not in genstep,
      "-- *\\"the basic rooms are well lit\\"* is the theme. A dark Backrooms is a different place")

''' + ANCHOR

if proof.count(ANCHOR) != 1:
    print("PROOF ANCHOR PROBLEM: %d" % proof.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(proof.replace(ANCHOR, CLAIMS, 1))
print("seven claims added")

plant = io.open(PLANT, encoding="utf-8").read()
P_ANCHOR = u'''    ("the lone centre support comes back", GEN,'''
PLANTS = u'''    # ------------------------------------------------------------ doors to nowhere
    ("DOORS TO NOWHERE ARE NEVER OPENED", PLANNER,
     "            return FalseOpening(room, rooms, cell);", "            return false;"),

    ("a false door moves to the centre, where a real door goes", PLANNER,
     "            int at = low + (high - low) / 3;", "            int at = (low + high) / 2;"),

    ("the threshold hall grows a door to nowhere", PLANNER,
     "            if (room == null || room.index == 0) { return false; }",
     "            if (room == null) { return false; }"),

    ("A FALSE OPENING IS ALLOWED ON A CORNER, which cuts the room open", PLANNER,
     "            if (walls != 1) { return false; }", "            if (walls < 1) { return false; }"),

    ("a wall that already has a real door gets a second opening", PLANNER,
     "                if (side == 0 && other.Bounds.minX > bounds.maxX) { return false; }",
     "                if (false) { return false; }"),

    # ------------------------------------------------------------------- lamp tones
    ("LAMPS GO BACK TO ALL BEING THE SAME COLOUR", GEN,
     "                        TintLamp(lamp, coordinate, room, pillar);", ""),

    ("the dim lamp becomes a dark one", GEN,
     "                    glower.GlowRadius = glower.GlowRadius * 2f / 3f;",
     "                    glower.GlowRadius = 0;"),

''' + P_ANCHOR

if plant.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % plant.count(P_ANCHOR))
    raise SystemExit(1)
io.open(PLANT, "w", encoding="utf-8", newline="").write(plant.replace(P_ANCHOR, PLANTS, 1))
print("seven plants added")
