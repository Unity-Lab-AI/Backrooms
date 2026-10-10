# -*- coding: utf-8 -*-
"""Nothing in the battery covered the assembly bill, which is why nobody noticed.

No proof and no plant mentioned `EnsureAssemblyBill` or `RR_AssembleMachineGate`. So the code that
queued a hundred steel of work the moment a door was commissioned was never asserted, never
planted against, and shipped from the day it was written.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-gate-links.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-gate-links-carry.py")

ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

CLAIMS = u'''console = _read(_SRC, "Gate", "CompRimroomsGateConsole.cs")
nativebinding = _read(_SRC, "Gate", "NativeGateBinding.cs")
gaterecipe = _read_mod("Defs", "RecipeDefs", "RR_GateRecipes.xml")

# ----------------------------------------- the assembly is the player's decision
# Owner: *"the machining table to op[en the gate needs to be a bill currently they instantly try
# to open the gate and build it and i have no say in the mattter even tho nothing is connected or
# built yet and havent started the mission line yet"*.
#
# `BindNativeInfrastructure` ended with `EnsureAssemblyBill`, which **added an unsuspended
# `Bill_Production` to the machining table**, so commissioning a door sent crafters off with a
# hundred steel and eight components immediately. **Nothing in this battery mentioned the bill**,
# so it was never asserted and never planted against.
check("COMMISSIONING A GATE QUEUES NOBODY'S WORK",
      "public void SyncAssemblyBill()" in console
      and "EnsureAssemblyBill" not in console
      and "EnsureAssemblyBill" not in nativebinding
      and "BillStack.AddBill" not in console
      and "new Bill_Production(" not in console,
      "-- *ensure* was the whole defect. The bill is added by the player, from the machining "
      "table's own recipe list, when they are ready")

check("and it may only suspend, never un-suspend and never re-time",
      "if (Gate == null || !Gate.AssemblyComplete) { return; }" in console
      and "bill.suspended = true;" in console
      and "existing.repeatMode = BillRepeatModeDefOf.RepeatCount;" not in console
      and "existing.suspended = Gate.AssemblyComplete" not in console,
      "-- suspending a finished bill cannot take a decision away; it stops a repeating bill "
      "spending another hundred steel on a gate that exists. Un-suspending one would overrule a "
      "player who suspended it on purpose, and the repeat mode and count are theirs")

check("and the recipe was on the table's own list the whole time",
      "<recipeUsers><li>TableMachining</li></recipeUsers>" in gaterecipe
      and "Designate the native door, communications console, battery and machining table in"
      in gaterecipe,
      "-- **the recipe's own description is an instruction to a player who then adds the bill**, "
      "and nothing had to be built to give them the choice. The choice had been taken")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)

# A mod-side reader, beside the existing source reader.
BIND_ANCHOR = u'gatecomp = _read(_SRC, "Portals", "CompRimroomsEmergence.cs")'
if BIND_ANCHOR not in text:
    BIND_ANCHOR = u'gatecomp = _read(_SRC, "Gate", "CompRimroomsGate.cs")'
if text.count(BIND_ANCHOR) != 1:
    print("BINDING ANCHOR PROBLEM: %d -- check how proof-gate-links reads its files"
          % text.count(BIND_ANCHOR))
    raise SystemExit(1)
text = text.replace(
    BIND_ANCHOR,
    BIND_ANCHOR + u'''


def _read_mod(*parts):
    return _io.open(_os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", *parts),
                    encoding="utf-8-sig").read()''', 1)
text = text.replace(ANCHOR, CLAIMS, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("three claims added for the assembly bill")

# ------------------------------------------------------------------------ plants
P_ANCHOR = u"PLANTS = ["
P_NEW = u'''PLANTS = [
    # ------------------- the gate assembling itself the moment it is commissioned
    ("THE GATE QUEUES ITS OWN ASSEMBLY AGAIN", CONSOLE,
     "        public void SyncAssemblyBill()", "        public void EnsureAssemblyBill()"),

    ("commissioning adds an unsuspended bill to somebody's table", CONSOLE,
     "            foreach (Bill_Production bill in table.BillStack.Bills.OfType<Bill_Production>()",
     "            table.BillStack.AddBill(new Bill_Production(recipe));" + chr(10)
     + "            foreach (Bill_Production bill in table.BillStack.Bills.OfType<Bill_Production>()"),

    ("THE BILL IS UN-SUSPENDED BEHIND THE PLAYER'S BACK", CONSOLE,
     "            if (Gate == null || !Gate.AssemblyComplete) { return; }",
     "            if (Gate == null) { return; }"),

    ("the player's repeat count is overruled", CONSOLE,
     "                bill.suspended = true;",
     "                bill.suspended = true;" + chr(10)
     + "                bill.repeatCount = 1;"),

    ("the recipe leaves the machining table's own list", RECIPE,
     "<recipeUsers><li>TableMachining</li></recipeUsers>",
     "<recipeUsers><li>ElectricSmithy</li></recipeUsers>"),
'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(P_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(P_ANCHOR, P_NEW, 1)

T_ANCHOR = u'COMP = SRC + "/Portals/CompRimroomsEmergence.cs"'
if suite.count(T_ANCHOR) != 1:
    print("TARGET ANCHOR PROBLEM: %d" % suite.count(T_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(
    T_ANCHOR,
    T_ANCHOR
    + u'\nCONSOLE = SRC + "/Gate/CompRimroomsGateConsole.cs"'
    + u'\nRECIPE = ("Mod/Rimrooms - Async Industries/1.6/Defs/RecipeDefs/RR_GateRecipes.xml")', 1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite)
print("five plants added")
