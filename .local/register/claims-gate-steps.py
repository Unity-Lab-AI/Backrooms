# -*- coding: utf-8 -*-
"""Claims and plants for the numbered checks, the specific refusals, and the facility."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-starts.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-startplacement.py")

ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

CLAIMS = u'''def _file(*parts):
    return io.open(os.path.join(SRC, "RimroomsAsyncIndustries", *parts),
                   encoding="utf-8-sig").read()


_steps = _file("UI", "OperationsGateSteps.cs")
_gate = _file("Gate", "CompRimroomsGate.cs")
_portals = _file("UI", "OperationsPortalNetwork.cs")
_hq = _file("Scenario", "GenStep_Headquarters.cs")
_startdef = _file("Scenario", "RimroomsStartDef.cs")
_expeditions = _file("UI", "OperationsExpeditions.cs")

# ------------------------------------------- the machine tab is numbered, and the checks are live
# Owner: *"the whole machine  tab needs to be numbered and everything step 1 step 2... ect ect so
# fucking simple a 6 yr old chimp can do it"*, *"it needs to have checks showing the start up
# connection checks are complete or unfinished yet"*, *"and it need to explain conciselky how"*.
check("THE MACHINE TAB OPENS WITH NUMBERED START-UP CHECKS",
      "private void DrawGateStartupChecks(Listing_Standard listing" in _steps
      and "DrawGateStartupChecks(listing, campaign);" in _expeditions
      and _expeditions.index("DrawGateStartupChecks(listing, campaign);")
      < _expeditions.index("DrawNativeGateBinding(listing, campaign);"),
      "-- DEFINED AND CALLED, and called FIRST: the checks are the thing that says which of the "
      "two panels below to use, and in which order")

check("and there are ELEVEN of them, each with a done flag and a how",
      "".join([("Number = %d," % n) in _steps and 1 or 0 and "" for n in range(1, 12)]) == ""
      and all(("Number = %d," % n) in _steps for n in range(1, 12))
      and all(('"RR_Steps_%dLabel"' % n) in _steps for n in range(1, 12))
      and all(('"RR_Steps_%dHow"' % n) in _steps for n in range(1, 12))
      and "public string How;" in _steps
      and "public bool Done;" in _steps,
      "-- a step with a label and no instruction is the panel the owner was already looking at")

check("AND THE FIRST UNFINISHED ONE IS NAMED ON ITS OWN LINE",
      "GateStep next = steps.FirstOrDefault(step => !step.Done);" in _steps
      and '"RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)' in _steps
      and '"RR_Steps_Progress".Translate(' in _steps,
      "-- *\\"im fucking lost on what to do ive done like 50 things in a row\\"*. Eleven lines is "
      "still a list to read; the answer to *what do i do* is one of them and it is said once at "
      "the top")

check("and the done ones do NOT repeat their instruction",
      '"RR_Steps_LineDone".Translate(step.Number.ToString(), step.Label)' in _steps
      and '"RR_Steps_LineToDo".Translate(step.Number.ToString(), step.Label, step.How)' in _steps,
      "-- otherwise the list becomes a wall of advice about things already handled")

check("and a binding fault is reported as a FAULT rather than as a step",
      '"RR_Steps_Fault".Translate(gate.NativeBindingFailureKey.Translate())' in _steps,
      "-- it is something that was done and has since broken, and it blocks every step after the "
      "one it broke")

check("THE ORDER MATCHES WHAT THE CODE ACTUALLY ENFORCES",
      _steps.index("Number = 4,") < _steps.index("Number = 5,")
      and _steps.index("Number = 8,") < _steps.index("Number = 10,")
      and "workshop != null && workshop.IsGateControl" in _steps
      and "station != null && station.IsGateControl" in _steps,
      "-- gate control on the TABLE must precede the assembly, because `AvailableOnNow` withdraws "
      "the recipe from a bench in normal operation; gate control on the CONSOLE must precede "
      "staffing, because `BeginSpinUp` refuses while either is doing its day job. A player "
      "following the list top to bottom never meets a step that cannot be done yet")

# ---------------------------------------------- the refusals name their cause
check("CALIBRATION REFUSES WITH THE REASON, AND 'ALREADY DONE' IS ONE OF THEM",
      "public string CalibrationBlockerKey()" in _gate
      and 'if (calibrated) { return "RR_Gate_AlreadyCalibrated"; }' in _gate
      and "string blocker = CalibrationBlockerKey();" in _gate
      and "return pawn != null && pawn == assignedOperator && CalibrationBlockerKey() == null;"
      in _gate,
      "-- one message covered all eight conditions INCLUDING `calibrated`, so a player whose crew "
      "had finished the work was told it could not start. And `CanCalibrate` asks the blocker "
      "rather than restating it, so the predicate and the message cannot disagree")

check("and staffing the console does the same",
      "public string StaffConsoleBlockerKey()" in _gate
      and "string blocker = StaffConsoleBlockerKey();" in _gate
      and '"RR_Gate_JobUnavailable"' not in _gate,
      "-- one key covered four problems with four different fixes, and it is GONE rather than "
      "merely bypassed")

check("AND THE PORTAL PANEL SAYS WHY WHEN IT HAS NO BUTTON TO OFFER",
      '"RR_Portals_NoLaboratoryAddress".Translate()' in _portals
      and "private static IEnumerable<string> GateOpeningBlockers(CompRimroomsGate gate)" in _portals
      and "foreach (string blocker in GateOpeningBlockers(gate))" in _portals
      and '"RR_Portals_BlockedConsoleNormalOp".Translate(gate.LinkedConsole.LabelCap)' in _portals,
      "-- the open buttons are drawn per remembered address, so a gate with none showed an empty "
      "panel. **That is what the owner spent an afternoon on.** It names which component is in "
      "normal operation, because the save said the table was switched and the console was not")

# ---------------------------------------------- the facility is a plan, and it is checked
# Owner: *"it should be designed intelligently with like ballistic glass  walls for viewing the
# machine remotely and safely with security zones and shit and lab rooms and shit i mean wtf is
# this this is a 50million dollar facilty"*.
check("THE VIEWING WALLS ARE NAMED AS STRINGS, NEVER AS A CROSS-REFERENCE",
      "public List<RimroomsWallRunPlan> glazing" in _startdef
      and "public List<string> thingDefNames" in _startdef
      and "private static ThingDef ResolveFirstLoaded(List<string> names)" in _hq
      and "DefDatabase<ThingDef>.GetNamedSilentFail(names[index])" in _hq,
      "-- a `ThingDef` field is resolved at load and an unresolved one discards the WHOLE "
      "containing def. That took `Door` and `Autodoor` out of the game once and produced 587 red "
      "lines before the main menu. The glass is from an Optional mod")

check("and a profile without the glass gets a wall, not a hole",
      "if (glass == null) { continue; }" in _hq
      and 'throw new InvalidOperationException("Headquarters glazing has no generated wall at "'
      in _hq,
      "-- a solid viewing wall is a cosmetic loss; a missing wall is a hole in a sealed gate hall")

check("THE AIRLOCK IS TWO AUTOMATIC DOORS IN SERIES",
      "public List<IntVec3> autodoors" in _startdef
      and 'DefDatabase<ThingDef>.GetNamedSilentFail("Autodoor") ?? ThingDefOf.Door' in _hq
      and "An autodoor cell must also be listed in doors" in _startdef,
      "-- *\\"with security zones and shit\\"*. `ThingDefOf.Autodoor` does not exist, so it is "
      "looked up by name with an ordinary door standing in rather than failing a start over a "
      "door's kind")

check("AND THE HEADQUARTERS POWER REBUILD CAN NO LONGER COST THE START",
      "try { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }" in _hq
      and "The headquarters power net could not be resolved at " in _hq,
      "-- this was bare inside a GenStep, which is exactly the shape that cost two launches in "
      "the destination generator. A facility that resolves its net one tick late is playable; one "
      "that does not exist is a dead game")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, CLAIMS, 1))
print("thirteen claims added")

# New path constants for the three UI files these plants touch.
T_ANCHOR = u'CHR_NL = chr(10)'
T_NEW = (u'CHR_NL = chr(10)' + chr(10)
         + u'STEPS = "src/RimroomsAsyncIndustries/UI/OperationsGateSteps.cs"' + chr(10)
         + u'TABS = "src/RimroomsAsyncIndustries/UI/OperationsExpeditions.cs"' + chr(10)
         + u'PORTALUI = "src/RimroomsAsyncIndustries/UI/OperationsPortalNetwork.cs"')

P_ANCHOR = u"PLANTS = ["
P_NEW = u'''PLANTS = [
    # ---------------------------- the numbered checks, the refusals, and the facility
    ("THE NUMBERED CHECKS STOP BEING DRAWN", TABS,
     "            DrawGateStartupChecks(listing, campaign);" + CHR_NL, ""),

    ("the checks are drawn after the panels they are meant to direct", TABS,
     "            DrawGateStartupChecks(listing, campaign);" + CHR_NL
     + "            DrawNativeGateBinding(listing, campaign);",
     "            DrawNativeGateBinding(listing, campaign);" + CHR_NL
     + "            DrawGateStartupChecks(listing, campaign);"),

    ("A STEP LOSES ITS INSTRUCTION", STEPS,
     '                How = "RR_Steps_9How".Translate(),', "                How = null,"),

    ("the first unfinished step stops being named", STEPS,
     '            { listing.Label("RR_Steps_NextUp".Translate(next.Number.ToString(), next.Label, next.How)); }',
     "            { }"),

    ("the gate-control steps stop reading the components", STEPS,
     "                Done = workshop != null && workshop.IsGateControl,",
     "                Done = true,"),

    ("CALIBRATION GOES BACK TO ONE MESSAGE FOR EIGHT CAUSES", GATECOMP,
     "            string blocker = CalibrationBlockerKey();" + CHR_NL
     + "            if (blocker != null) { return CompanyActionResult.Refused(blocker); }",
     '            if (!CanCalibrate(assignedOperator)) { return CompanyActionResult.Refused("RR_Gate_CalibrationUnavailable"); }'),

    ("an already-calibrated gate stops saying so", GATECOMP,
     '            if (calibrated) { return "RR_Gate_AlreadyCalibrated"; }' + CHR_NL, ""),

    ("the predicate derives the conditions a second time", GATECOMP,
     "            return pawn != null && pawn == assignedOperator && CalibrationBlockerKey() == null;",
     "            return !IsOpening && assemblyComplete && !calibrated && pawn != null;"),

    ("THE EMPTY PORTAL PANEL GOES SILENT AGAIN", PORTALUI,
     '                    { listing.Label("RR_Portals_NoLaboratoryAddress".Translate()); }',
     "                    { }"),

    ("the blockers are listed and then not drawn", PORTALUI,
     "                    foreach (string blocker in GateOpeningBlockers(gate))" + CHR_NL
     + "                    { listing.Label(blocker); }" + CHR_NL, ""),

    ("THE GLAZING BECOMES A HARD CROSS-REFERENCE", DEF,
     "        public List<string> thingDefNames = new List<string>();",
     "        public List<ThingDef> thingDefNames = new List<ThingDef>();"),

    ("a missing glass def leaves a hole instead of a wall", GEN,
     "                    if (glass == null) { continue; }" + CHR_NL, ""),

    ("the headquarters power rebuild goes bare again", GEN,
     "            try { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }",
     "            map.powerNetManager.UpdatePowerNetsAndConnections_First(); if (false)"),
'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(T_ANCHOR) != 1:
    print("TARGET ANCHOR PROBLEM: %d" % suite.count(T_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(T_ANCHOR, T_NEW, 1)
if suite.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(P_ANCHOR))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite.replace(P_ANCHOR, P_NEW, 1))
print("thirteen plants added")
