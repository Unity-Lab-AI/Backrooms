# -*- coding: utf-8 -*-
"""Claims and plants for the ramp/open distinction, the breezeway, and the rotation rule."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-starts.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-startplacement.py")

ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

CLAIMS = u'''# ------------------------------------- a ramp is not an open connection
# Owner, 2026-10-01: *"every check mark is complete but it still says: the lab connection to that
# address is not connected.. but the checked staps says otherwise"*. Step 11 read
# `IsOpening || IsSpinningUp`, so pressing "open a session" ticked all eleven while the connection
# was still ramping -- and `PortalTravelService` then refused the crossing with
# `RR_PortalTravel_SessionClosed`, **which was true**. The tick was the thing that was wrong.
check("A RAMPING CONNECTION DOES NOT COUNT AS AN OPEN ONE",
      "Done = haveGate && gate.IsOpening," in _steps
      and "bool ramping = haveGate && gate.IsSpinningUp;" in _steps
      and "(gate.SpinUpProgress * 100f).ToString(\\"F0\\")" in _steps
      and '"RR_Steps_11HowRamping"' in _steps
      # The old disjunction is GONE, not merely bypassed.
      and "gate.IsOpening || gate.IsSpinningUp" not in _steps,
      "-- `IsSpinningUp` is defined as `!IsOpening`, so they are distinct states and the step says "
      "which one it is in, with the live percentage. The ramp is work and it bleeds back down if "
      "the operator leaves, which is the one thing a player watching it needs told")

check("AND THE LIST SAYS WHAT TO DO ONCE IT IS OPEN",
      '"RR_Steps_NowCross".Translate()' in _steps
      and "if (gate != null && gate.IsOpening)" in _steps,
      "-- the eleven checks end at a live connection and the player's goal is on the far side of "
      "it. Nothing said *now send somebody*, which is why a completed list still left the owner "
      "asking what they were missing")

# ------------------------------- Core moves the centre of an even-dimension building
check("THE FOOTPRINT MODEL APPLIES CORE'S ROTATION ADJUSTMENT",
      "{0: (0, 0), 1: (0, -1), 2: (-1, -1), 3: (-1, 0)}" in
      io.open(os.path.join(REPO, "tools", "check-start-layout.py"), encoding="utf-8").read()
      and "{0: (0, 0), 1: (0, -1), 2: (-1, -1), 3: (-1, 0)}" in
      io.open(os.path.join(REPO, ".local", "register", "build-async-facility.py"),
              encoding="utf-8").read(),
      "-- `GenAdj.AdjustForRotation` swaps the axes for a horizontal rotation and then shifts the "
      "centre by one for an even dimension, so a 3x2 console facing SOUTH occupies the rows at "
      "and BELOW its position. **Three copies of this rule disagreed with Core** and all three "
      "said the owner's console overlapped the glass it is sitting against")

check("AND A BENCH WHOSE INTERACTION CELL IS A WALL IS REFUSED",
      "has its interaction cell on the wall" in
      io.open(os.path.join(REPO, "tools", "check-start-layout.py"), encoding="utf-8").read()
      and "def interaction_cell(" in
      io.open(os.path.join(REPO, "tools", "check-start-layout.py"), encoding="utf-8").read(),
      "-- `IsOperatorOnStation` requires the pawn to stand on exactly that cell. **The rule found "
      "a real defect the day it was written**: the Furniture Store's comms console had its "
      "interaction cell in the staff room's north wall, so it had never been usable -- and "
      "reaching the corporation is that scenario's whole achievement")

# ---------------------------------------- the power room and the breezeway
# Owner: *"actuall make onbe of the rooms a power room and where the generators are should be a
# breeze way thats unroffeced area complete just that area they are in thats inclose by walls and
# doors"*, and *"generators out side batteries inside"*.
_async = [s for s in starts if s["defName"] == "RR_AsyncIndustriesStart"][0]
_rooms = {(r[0], r[1]): r for r in _async["rooms"]}
check("ROOFED FALSE CLEARS A ROOF RATHER THAN SKIPPING IT",
      "map.roofGrid.SetRoof(cell, room.roofed ? RoofDefOf.RoofConstructed : null);" in
      io.open(os.path.join(SRC, "RimroomsAsyncIndustries", "Scenario",
                           "GenStep_Headquarters.cs"), encoding="utf-8-sig").read(),
      "-- every room is nested inside a roofed compound, so a nested room asking for no roof got "
      "one anyway from the pass that ran first. `roofed: false` was meaningless for exactly the "
      "case it is needed in")

check("THE GENERATORS STAND IN A WALLED, DOORED, UNROOFED BREEZEWAY",
      (22, 34) in _rooms and _rooms[(22, 34)][4] is False
      and any(thing == "WoodFiredGenerator" and 23 <= origin[0] <= 26 and 35 <= origin[1] <= 40
              for thing, origin, _rot in _async["buildings"])
      and (22, 37) in [tuple(d) for d in _async["doors"]],
      "-- *\\"generators out side batteries inside\\"*. A fuel generator in a sealed room cooks the "
      "room; venting it to the sky while keeping it inside the compound is what a breezeway is "
      "for. It is the only unroofed room in the facility and it has a door like any other")

check("and the batteries are inside, in a power room of their own",
      (22, 25) in _rooms and _rooms[(22, 25)][4] is True
      and sum(1 for thing, origin, _rot in _async["buildings"]
              if thing == "Battery" and 23 <= origin[0] <= 26 and 26 <= origin[1] <= 31) >= 4
      and not any(thing == "Battery" and origin[0] >= 29 for thing, origin, _rot
                  in _async["buildings"]),
      "-- the bank moved out of the control room, which is where it was only because the first "
      "authoring had nowhere better to put it")

check("AND THE OWNER'S OWN POSITIONS ARE WHERE THE OWNER PUT THEM",
      any(thing == "CommsConsole" and origin == (32, 33) and rot == 2
          for thing, origin, rot in _async["buildings"])
      and any(thing == "TableMachining" and origin == (45, 33)
              for thing, origin, _rot in _async["buildings"]),
      "-- read out of `Autosave-3.rws` and converted by the layout offset of (120,120) on their "
      "300-cell map. *\\"thats where i want them so fix there spawn position\\"*")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, CLAIMS, 1))
print("eight claims added")

P_ANCHOR = u"PLANTS = ["
P_NEW = u'''PLANTS = [
    # ------------------- a ramp is not an open connection, and the facility's power
    ("A RAMPING CONNECTION COUNTS AS OPEN AGAIN", STEPS,
     "                Done = haveGate && gate.IsOpening,",
     "                Done = haveGate && (gate.IsOpening || gate.IsSpinningUp),", STARTS_PROOF),

    ("the ramp stops reporting its progress", STEPS,
     "                How = ramping" + CHR_NL
     + '                    ? "RR_Steps_11HowRamping".Translate(',
     "                How = false" + CHR_NL
     + '                    ? "RR_Steps_11HowRamping".Translate(', STARTS_PROOF),

    ("THE LIST STOPS SAYING HOW TO SEND SOMEBODY THROUGH", STEPS,
     '            { listing.Label("RR_Steps_NowCross".Translate()); }',
     "            { }", STARTS_PROOF),

    ("CORE'S ROTATION ADJUSTMENT IS DROPPED FROM THE CHECKER",
     "tools/check-start-layout.py",
     "    shift = {0: (0, 0), 1: (0, -1), 2: (-1, -1), 3: (-1, 0)}[rotation % 4]",
     "    shift = {0: (0, 0), 1: (0, 0), 2: (0, 0), 3: (0, 0)}[rotation % 4]", STARTS_PROOF),

    ("the interaction-cell rule goes", "tools/check-start-layout.py",
     '                fail("%s: %s at %s has its interaction cell on the wall %s'
     ' -- nobody can ever "',
     '                pass  # ("%s: %s at %s has its interaction cell on the wall %s'
     ' -- nobody can ever "', STARTS_PROOF),

    ("ROOFED FALSE GOES BACK TO MERELY SKIPPING", GEN,
     "                        map.roofGrid.SetRoof(cell, room.roofed ? RoofDefOf.RoofConstructed : null);",
     "                        if (room.roofed) { map.roofGrid.SetRoof(cell, RoofDefOf.RoofConstructed); }",
     STARTS_PROOF),

    ("THE BREEZEWAY GETS A ROOF OVER THE GENERATORS", STARTS,
     "      <li><x>22</x><z>34</z><width>6</width><height>8</height><roofed>false</roofed><floor>true</floor></li>",
     "      <li><x>22</x><z>34</z><width>6</width><height>8</height><roofed>true</roofed><floor>true</floor></li>",
     STARTS_PROOF),

    ("the breezeway loses its door, so it stops being a room", STARTS,
     "      <li>(22, 0, 37)</li>" + CHR_NL, "", STARTS_PROOF),

    ("THE CONSOLE MOVES OFF WHERE THE OWNER PUT IT", STARTS,
     "      <li><thing>CommsConsole</thing><cell>(32, 0, 33)</cell><rotation>2</rotation></li>",
     "      <li><thing>CommsConsole</thing><cell>(32, 0, 27)</cell></li>", STARTS_PROOF),

    ("the assembly bench moves off where the owner put it", STARTS,
     "      <li><thing>TableMachining</thing><cell>(45, 0, 33)</cell></li>",
     "      <li><thing>TableMachining</thing><cell>(41, 0, 16)</cell></li>", STARTS_PROOF),
'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(P_ANCHOR))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite.replace(P_ANCHOR, P_NEW, 1))
print("ten plants added")
