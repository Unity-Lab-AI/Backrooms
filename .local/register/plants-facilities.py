# -*- coding: utf-8 -*-
"""Plants for the institutions and the loot, and the stale PASS line that said 2-4."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-facilities.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-startplacement.py")

# The summary still announced the old bounds.
text = io.open(PROOF, encoding="utf-8").read()
OLD = u"""print('PASS: facilities form, are contiguous, bounded 2-4, never consume a quiet or threshold room,')"""
NEW = u"""print('PASS: facilities form, are contiguous, bounded 2-6, never consume a quiet or threshold room,')"""
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM (summary): %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the summary no longer announces bounds the code stopped using")

# ------------------------------------------------------------------------ plants
P_ANCHOR = u"PLANTS = ["
P_NEW = u'''PLANTS = [
    # ------------------------------------- institutions, and the loot in them
    # Owner: *"facilitys and buildings and neighboorhoods and complexes and shools and hospitals
    # and military and storages need loot inside of them too"*. `Anchors` opened with
    # `coordinate.Depth <= 1` and returned null, so a FIRST LEVEL HAD NO INSTITUTIONS AT ALL.
    ("A FIRST LEVEL LOSES EVERY INSTITUTION AGAIN", FACILITY,
     "            if (coordinate == null || coordinate.Rooms == null) { return null; }",
     "            if (coordinate == null || coordinate.Rooms == null || coordinate.Depth <= 1) { return null; }",
     FACILITY_PROOF),

    ("the arrival stops staying sparse, so the yellow rooms become a complex", FACILITY,
     "                if (RoomArchetypeService.EffectiveDepth(coordinate, room, coordinate.Depth) <= 1)"
     + chr(10) + "                { continue; }" + chr(10), "", FACILITY_PROOF),

    ("a complex shrinks back to four rooms while the proof models six", FACILITY,
     "        private const int MaxRooms = 6;", "        private const int MaxRooms = 4;",
     FACILITY_PROOF),

    ("the eligible share drifts from the model that mirrors it", FACILITY,
     "        private const float EligibleShare = 0.6f;",
     "        private const float EligibleShare = 0.45f;", FACILITY_PROOF),

    ("AN ARCHETYPE GOES BACK TO HOLDING NOTHING WORTH CARRYING OUT", ARCHETYPES,
     "      <li>" + chr(10) + "        <kind>CategoryMember</kind>" + chr(10)
     + "        <category>Apparel</category>" + chr(10) + "        <count>1~3</count>" + chr(10)
     + "        <chance>0.8</chance>" + chr(10) + "      </li>" + chr(10), "", FACILITY_PROOF),
'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(P_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(P_ANCHOR, P_NEW, 1)

T_ANCHOR = u'STARTS_PROOF = ".local/register/proof-starts.py"'
if suite.count(T_ANCHOR) != 1:
    print("TARGET ANCHOR PROBLEM: %d" % suite.count(T_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(
    T_ANCHOR,
    T_ANCHOR
    + u'\nFACILITY_PROOF = ".local/register/proof-facilities.py"'
    + u'\nFACILITY = "src/RimroomsAsyncIndustries/Generation/FacilityPlanner.cs"'
    + u'\nARCHETYPES = ("Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsRoomArchetypeDefs/"'
    + u'\n              "RR_RoomArchetypes.xml")', 1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite)
print("five plants added for the institutions and the loot")
