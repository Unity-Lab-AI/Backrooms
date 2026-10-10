# -*- coding: utf-8 -*-
"""Two plants went stale when room spans gained a second source, and one of them hid a real gap.

1. **The evenness claim guarded one function and there are now two.** `SlotRoomSpan` forces an
   even span, and so does the new `VariedRoomSpan` -- so a plant deleting the subtraction from the
   first was satisfied by the second still containing the line. The claim counted a string, and
   the string had moved house.

   **This is the same lesson as the `AllComps.Add(` claim that two call sites satisfied**, and it
   matters more here: `CellRect.CenterCell` is where every door and every corridor is aimed, and
   an odd span moves it off the slot centre.

2. **A plant anchored on `MaxSlotsPerAxis = 8`**, which is 10 now. Retargeted at the constant by
   name rather than by value, so the next retune does not silently stop guarding it.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")
PLANT = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")

proof = io.open(PROOF, encoding="utf-8").read()
OLD = u'''check("THE SPAN IS FORCED EVEN IN THE SOURCE, NOT JUST IN THIS PROOF'S MODEL",
      "if (span % 2 != 0) { span--; }" in planner,
      "-- a plant that deleted this line passed the computed evenness claim, because the model "
      "was still doing the subtraction itself. A modelled property needs a source claim beside it")'''
NEW = u'''check("THE SPAN IS FORCED EVEN IN THE SOURCE, NOT JUST IN THIS PROOF'S MODEL",
      planner.count("if (span % 2 != 0) { span--; }") >= 2,
      "-- a plant that deleted this line passed the computed evenness claim, because the model "
      "was still doing the subtraction itself. A modelled property needs a source claim beside "
      "it -- and there are TWO span sources now, `SlotRoomSpan` and `VariedRoomSpan`, so "
      "counting one of them was satisfied by the other. CellRect.CenterCell is where every door "
      "and corridor is aimed; an odd span moves it off the slot centre")'''
if proof.count(OLD) != 1:
    print("PROOF ANCHOR PROBLEM: %d" % proof.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(proof.replace(OLD, NEW, 1))
print("evenness claim counts both span sources")

plant = io.open(PLANT, encoding="utf-8").read()
P_OLD = u'''    ("depth stops changing the slot grid", PLANNER,
     "internal const int MaxSlotsPerAxis = 8;", "internal const int MaxSlotsPerAxis = 3;"),'''
P_NEW = u'''    ("depth stops changing the slot grid", PLANNER,
     "internal const int MaxSlotsPerAxis =", "internal const int MaxSlotsPerAxisUnused ="),

    # The SECOND span source. Deleting the evenness guard from one of them used to pass, because
    # the claim counted a string that exists in both.
    ("THE VARIED SPAN STOPS BEING EVEN, so doors miss the slot centre", PLANNER,
     "            int span = baseline + offset;" + NL
     + "            if (span % 2 != 0) { span--; }" + NL,
     "            int span = baseline + offset;" + NL),

    ("rooms stop varying in size, so the level is a grid of identical boxes again", PLANNER,
     "VariedRoomSpan(spacing, slot, seed, depth)", "SlotRoomSpan(spacing)"),

    ("THE GRAND THRESHOLD HALL IS LOST", PLANNER,
     "rooms.Add(MakeHall(coordinate, order[0], order[1], spacing, seed, depth));", ""),

    ("the hall grows to four slots and breaks the chain's adjacency", PLANNER,
     "                consumed = 2;", "                consumed = 4;"),

    ("the maze goes back to one branch in three", PLANNER,
     "% 4 == 3)", "% 3 != 0)"),'''
if plant.count(P_OLD) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % plant.count(P_OLD))
    raise SystemExit(1)
io.open(PLANT, "w", encoding="utf-8", newline="").write(plant.replace(P_OLD, P_NEW, 1))
print("slot plant retargeted; five layout plants added")
