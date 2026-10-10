# -*- coding: utf-8 -*-
"""Claims and plants for the corporate start's integrity fault and the door toggle."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-starts.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-startplacement.py")

ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

CLAIMS = u'''def _rr_read(*parts):
    return io.open(os.path.join(REPO, *parts), encoding="utf-8-sig").read()


services = _rr_read("src", "RimroomsAsyncIndustries", "Company", "CampaignServices.cs")
component = _rr_read("src", "RimroomsAsyncIndustries", "Company", "RimroomsCampaignComponent.cs")
gatecomp = _rr_read("src", "RimroomsAsyncIndustries", "Gate", "CompRimroomsGate.cs")
starts_xml = _rr_read("Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                      "RimroomsStartDefs", "RR_Starts.xml")

# ------------------------------- the corporate start disabled itself on turn one
# Owner: *"it says : Company Records could not be reconsiled blah blah blah.... and none of our
# buttons work"*. `[Rimrooms][Save] Campaign integrity failed` is logged on the line immediately
# before `Initialized ... scenario=async_industries`, because `InitializeBranch` validates the
# records it has just seeded.
#
# `BuildProjectTree` set `insightCommitted = done` and **never set `insightOperationId`**, and
# `ValidateRecordRelationships` requires a committed insight to carry one. So every pre-completed
# project was a save-integrity fault, `stateFaultKey` was set and `CanOperate` went false -- every
# button in the mod refusing. **The corporate start is the only one that names completed
# projects**, so it is the only start this broke, and it broke it from the day it was written.
check("A PRE-COMPLETED PROJECT CARRIES THE RECEIPT ITS COMMITMENT IMPLIES",
      "insightOperationId = done ? projectId + \\":insight\\" : null," in services
      and "string projectId = branchId + \\":project:\\" + definition.defName;" in services
      and "insightCommitted = done," in services,
      "-- the validator requires `!insightCommitted || insightOperationId` is non-empty, and this "
      "field was never written. The id is the format `InvestigationServices` uses when the player "
      "commits an insight, built from the record's own id so the two cannot drift")

check("and the validator still refuses a committed insight with no receipt",
      "(!p.insightCommitted || !string.IsNullOrWhiteSpace(p.insightOperationId))" in component,
      "-- the rule was right. **A committed insight with no receipt is exactly the double-payment "
      "hole this check exists for**, so it is the seeding that changed and not the rule")

check("and the corporate start is the only one that begins with research finished",
      starts.count("<completedProjects>") == 1
      and "RR_GateTelemetry" in starts_xml and "RR_Commerce_NegotiatedTerms" in starts_xml,
      "-- eight projects, all of them faults until now. The other two starts carry an empty list, "
      "which is why they never showed this")

# -------------------------------------------- a toggle on the door, where a player looks
# Owner: *"i have no idea how the gate is suppose to work as there doesnt be a toggle option to
# turn it from a normal door to a machine gate door"*. `CompGetGizmosExtra` opened with
# `if (parent.Faction != Faction.OfPlayer || !IsDesignated) { yield break; }`, so an undesignated
# door offered NOTHING and the only route from a door to a gate was a pane in the Operations tab
# -- which the state fault above was also refusing.
check("AN UNDESIGNATED DOOR OFFERS THE WAY TO BECOME A GATE",
      "private IEnumerable<Gizmo> MakeGateGizmos()" in gatecomp
      and "foreach (Gizmo gizmo in MakeGateGizmos()) { yield return gizmo; }" in gatecomp
      and "if (parent.Faction != Faction.OfPlayer || !IsDesignated) { yield break; }"
      not in gatecomp,
      "-- DEFINED AND CALLED, and the old early return is GONE rather than merely bypassed")

check("and it only ever offers what the binding would accept",
      "UI.MainTabWindow_Operations.SoleCandidate(" in gatecomp
      and gatecomp.count("UI.MainTabWindow_Operations.SoleCandidate(") == 3
      and "campaign.Headquarters != parent.Map" in gatecomp
      and "ShowOrderResult(BindNativeInfrastructure(console, battery, bench));" in gatecomp,
      "-- all three providers, the headquarters requirement checked before the button is shown so "
      "a button that can only refuse is never shown, and the decision left entirely to "
      "`BindNativeInfrastructure`. **A second place to ask, not a second opinion**")

check("and an ambiguous or missing provider is named rather than silent",
      "RR_NativeGate_NoSingleConsole" in gatecomp
      and "RR_NativeGate_NoSingleBattery" in gatecomp
      and "RR_NativeGate_ChooseBench" in gatecomp,
      "-- the player needs to know which piece to build or which choice to make, and *\\"it did "
      "nothing\\"* tells them neither")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, CLAIMS, 1))
print("six claims added to proof-starts.py")

# ------------------------------------------------------------------------- plants
P_ANCHOR = u"PLANTS = ["
P_NEW = u'''PLANTS = [
    # ------------------------- the fault that disabled a whole scenario on turn one
    ("THE CORPORATE START DISABLES ITSELF ON TURN ONE AGAIN", SERVICES,
     '                    insightOperationId = done ? projectId + ":insight" : null,' + chr(10), ""),

    ("a pre-completed project is committed with an empty receipt", SERVICES,
     '                    insightOperationId = done ? projectId + ":insight" : null,',
     '                    insightOperationId = done ? "" : null,'),

    ("THE VALIDATOR STOPS REQUIRING A RECEIPT, so a double payment can hide", COMPONENT,
     "(!p.insightCommitted || !string.IsNullOrWhiteSpace(p.insightOperationId))",
     "(!p.insightCommitted || true)"),

    ("the corporate start stops beginning with its research finished", STARTS,
     "      <li>RR_GateTelemetry</li>" + chr(10), ""),

    # ------------------------------------------- the toggle on the door
    ("AN UNDESIGNATED DOOR GOES BACK TO OFFERING NOTHING", GATECOMP,
     "            if (!IsDesignated)" + chr(10) + "            {" + chr(10)
     + "                foreach (Gizmo gizmo in MakeGateGizmos()) { yield return gizmo; }" + chr(10)
     + "                yield break;" + chr(10) + "            }",
     "            if (!IsDesignated) { yield break; }"),

    ("the toggle appears on a door away from the headquarters", GATECOMP,
     "                || campaign.Headquarters != parent.Map",
     "                || false"),

    ("the toggle binds the first of several providers instead of refusing", GATECOMP,
     "                    if (console == null || battery == null || bench == null)",
     "                    if (false)"),
'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(P_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(P_ANCHOR, P_NEW, 1)

T_ANCHOR = u'STARTS = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsStartDefs/RR_Starts.xml"'
if suite.count(T_ANCHOR) != 1:
    print("TARGET ANCHOR PROBLEM: %d -- check the suite's own name for the starts file"
          % suite.count(T_ANCHOR))
    raise SystemExit(1)
suite = suite.replace(T_ANCHOR, T_ANCHOR
                      + u'\nSERVICES = SRC + "/Company/CampaignServices.cs"'
                      + u'\nCOMPONENT = SRC + "/Company/RimroomsCampaignComponent.cs"'
                      + u'\nGATECOMP = SRC + "/Gate/CompRimroomsGate.cs"', 1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite)
print("seven plants added")
