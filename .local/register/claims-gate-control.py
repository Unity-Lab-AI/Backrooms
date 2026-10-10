# -*- coding: utf-8 -*-
"""Claims and plants for gate control: a component does its job or the gate's, never both."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-gate-links.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-gate-links-carry.py")

ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

CLAIMS = u'''spinup = _read(_SRC, "Gate", "GateSpinUp.cs")

# ------------------------------------------------- gate control, and it cuts both ways
# Owner: *"we should have a set to gate control for these components so other things arnt
# available and can toggle between normal op and gate op depending whats wanted.."*
check("A COMPONENT DOES ITS ORDINARY JOB OR THE GATE'S, AND THE PLAYER CHOOSES",
      "public bool IsGateControl { get { return gateControl && linkedGate != null; } }" in console
      and "public void SetGateControl(bool running)" in console
      and "action = delegate { SetGateControl(!running); }" in console
      and "RR_NativeGate_GateControlLabel" in console
      and "RR_NativeGate_NormalOpLabel" in console,
      "-- DEFINED AND CALLED, and the switch is offered only on a component actually bound to a "
      "gate, because a button that can only refuse is worse than no button")

check("and it BEGINS in normal operation",
      "private bool gateControl;" in console
      and 'Scribe_Values.Look(ref gateControl, "rr_gateConsoleGateControl", false);' in console,
      "-- commissioning a door must not change how the colony works. That was the other half of "
      "the complaint this came from, where binding queued a hundred steel of assembly nobody "
      "asked for")

check("ORDINARY COMPANY FUNCTIONS ARE WITHDRAWN IN GATE CONTROL",
      "if (IsGateControl) { yield break; }" in console
      and console.index("if (IsGateControl) { yield break; }")
      < console.index("Procurement.CorporateSupplyGizmos.For(parent)"),
      "-- *\\"so other things arnt available\\"*. The withdrawal is BEFORE the four gizmos, not "
      "after: a console running the gate is not also taking deliveries, paying credit, raising "
      "the alarm or placing the corporation call")

check("and a machining table's other bills are suspended, by id, and resumed exactly",
      "suspendedByGateControl.Add(bill.GetUniqueLoadID());" in console
      and "if (bill == null || bill.suspended) { continue; }" in console
      and 'bill.recipe.defName == "RR_AssembleMachineGate")' in console
      and "suspendedByGateControl.Contains(bill.GetUniqueLoadID())" in console
      and "suspendedByGateControl.Clear();" in console,
      "-- **recorded rather than inferred.** A bill the player had already suspended must stay "
      "suspended, and the current state cannot tell those two apart")

check("AND NORMAL OPERATION REFUSES THE GATE, so the modes are exclusive both ways",
      "&& console.IsGateControl;" in console
      and "RR_NativeGate_NotInGateControl" in spinup
      and "!spinUpStation.IsGateControl" in spinup
      and "!spinUpWorkshop.IsGateControl" in spinup,
      "-- the recipe is unavailable on a bench doing its day job, and spin-up refuses while "
      "either installation is still in normal operation. *\\"depending whats wanted\\"* only means "
      "something if both directions hold")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, CLAIMS, 1))
print("five claims added for gate control")

P_ANCHOR = u"PLANTS = ["
P_NEW = u'''PLANTS = [
    # --------------------------------------------------- gate control, both directions
    ("THE GATE-CONTROL SWITCH IS GONE", CONSOLE,
     "                    action = delegate { SetGateControl(!running); }",
     "                    action = delegate { }"),

    ("a component begins in gate control instead of its ordinary job", CONSOLE,
     'Scribe_Values.Look(ref gateControl, "rr_gateConsoleGateControl", false);',
     'Scribe_Values.Look(ref gateControl, "rr_gateConsoleGateControl", true);'),

    ("ORDINARY FUNCTIONS STAY AVAILABLE WHILE THE GATE IS RUNNING", CONSOLE,
     "            if (IsGateControl) { yield break; }" + chr(10), ""),

    ("the other bills are never suspended", CONSOLE,
     "                    bill.suspended = true;" + chr(10)
     + "                    suspendedByGateControl.Add(bill.GetUniqueLoadID());",
     "                    suspendedByGateControl.Add(bill.GetUniqueLoadID());"),

    ("a bill the player had already suspended is resumed on the way back", CONSOLE,
     "                    if (bill == null || bill.suspended) { continue; }",
     "                    if (bill == null) { continue; }"),

    ("THE RECIPE IS AVAILABLE ON A BENCH DOING ITS DAY JOB", CONSOLE,
     "            return gate != null && !gate.AssemblyComplete && console.IsGateControl;",
     "            return gate != null && !gate.AssemblyComplete;"),

    ("spin-up stops caring whether the installations were handed over", SPINUP,
     "            if (spinUpStation != null && !spinUpStation.IsGateControl)" + chr(10)
     + '            { return CompanyActionResult.Refused("RR_NativeGate_NotInGateControl"); }' + chr(10),
     ""),
'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(P_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(P_ANCHOR, P_NEW, 1)

T_ANCHOR = u'CONSOLE = SRC + "/Gate/CompRimroomsGateConsole.cs"'
if suite.count(T_ANCHOR) != 1:
    print("TARGET ANCHOR PROBLEM: %d" % suite.count(T_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(T_ANCHOR, T_ANCHOR + u'\nSPINUP = SRC + "/Gate/GateSpinUp.cs"', 1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite)
print("seven plants added")
