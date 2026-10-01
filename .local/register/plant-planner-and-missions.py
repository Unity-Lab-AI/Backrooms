# -*- coding: utf-8 -*-
"""Plant a fault, run the check, require failure, restore. Verified writes.

Every target is run clean before anything is planted -- the 0.12.39-dev lesson, where a plant
run reported 17 of 17 against a proof that was failing unconditionally.
"""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
PLANNER = SRC + "/Expedition/CrewPlanner.cs"
PANE = SRC + "/UI/OperationsCrewPlanner.cs"
DISPATCH_PANE = SRC + "/UI/OperationsExpeditions.cs"
EXPEDITION = SRC + "/Expedition/RimroomsExpeditionComponent.cs"
MISSIONS = SRC + "/Company/OddConsignmentMissions.cs"
SUPPLY = SRC + "/Company/OddSupplyContracts.cs"
RECORDS = SRC + "/Company/CampaignRecords.cs"
TERMS = SRC + "/UI/OperationsContractTerms.cs"
WINDOW = SRC + "/UI/MainTabWindow_Operations.cs"
SERVICES = SRC + "/Company/CampaignServices.cs"
COMPONENT = SRC + "/Company/RimroomsCampaignComponent.cs"
ORIGIN = SRC + "/Economy/CompRimroomsOddOrigin.cs"
KEYS = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_CrewPlanner.xml"
SUPPLY_KEYS = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_OddSupply.xml"
PROOF = ".local/register/proof-planner-and-missions.py"


# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
_RR_SENTINEL = os.path.join(".local", "register", ".plant-in-progress")


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


PLANTS = [
    # ------------------------------------------------------ row 728's absolute
    ("THE PLANNER STARTS OWNING CONNECTION EXISTENCE", EXPEDITION,
     '            if (coordinate == null || !Campaign.Coordinates.Contains(coordinate)) { return Refuse("RR_Exp_InvalidDestination"); }',
     '            if (!CrewPlanner.Assess(Campaign, gate, crew[0]).Ready) { return Refuse("RR_Exp_InvalidCrew"); }\n'
     '            if (coordinate == null || !Campaign.Coordinates.Contains(coordinate)) { return Refuse("RR_Exp_InvalidDestination"); }',
     PROOF),

    ("the gate code starts consulting the planner", SRC + "/Gate/GateIntegrity.cs",
     "        internal void TickIntegrity()\n        {",
     "        internal void TickIntegrity()\n        {\n"
     "            if (Expedition.CrewPlanner.MaxCrew < 1) { return; }", PROOF),

    ("the planner starts handing back a refusal", PLANNER,
     "        public static CandidateReport Assess(RimroomsCampaignComponent campaign,",
     "        public static Company.CompanyActionResult Veto() "
     "{ return Company.CompanyActionResult.Refused(\"RR_Plan_Dead\"); }\n\n"
     "        public static CandidateReport Assess(RimroomsCampaignComponent campaign,", PROOF),

    ("dispatch stops refusing an undebriefed crew itself", EXPEDITION,
     'return Refuse("RR_Exp_AwaitingDebrief");', "{ }", PROOF),

    # ------------------------------------------------------ row 728, named reasons
    ("A REASON GOES BACK TO BEING UNNAMED", PLANNER,
     'report.ReasonKey = "RR_Plan_Downed"; return report;', "return report;", PROOF),

    ("a reason loses its keyed string", KEYS,
     "  <RR_Plan_OverCapacity>", "  <RR_Plan_OverCapacityX>", PROOF),

    ("the operator check becomes a second opinion", PLANNER,
     "pawn == gate.AssignedOperator", "pawn.Name == null", PROOF),

    ("the debrief check becomes a second opinion", PLANNER,
     "campaign.AwaitingDebrief(pawn)", "false", PROOF),

    ("the capacity check is reimplemented instead of reused", PLANNER,
     "!ExpeditionCargo.CheckCapacity(pawn).Success",
     "MassUtility.GearAndInventoryMass(pawn) > MassUtility.Capacity(pawn)", PROOF),

    ("the movement check stops using Core's capacity", PLANNER,
     "PawnCapacityDefOf.Moving", "PawnCapacityDefOf.Consciousness", PROOF),

    ("the crew cap is written twice", PANE,
     "CrewPlanner.MaxCrew.ToString(CultureInfo.CurrentCulture)", '"3"', PROOF),

    # ------------------------------------------------------ row 728, the four checks
    ("a disabled skill starts counting as held", PLANNER,
     "record != null && !record.TotallyDisabled && record.Level > 0",
     "record != null && record.Level > 0", PROOF),

    # The first version of this plant wrapped the label in `var unused = (...)` and called it a
    # refusal. It was neither: the key stayed in the file, nothing was refused, and the claim
    # passed. A gap that is computed and never drawn is the real failure, so that is the plant.
    ("A SKILL GAP IS COMPUTED AND NEVER SHOWN", PANE,
     'listing.Label("RR_Plan_SkillGaps".Translate(', 'var unused = ("RR_Plan_SkillGaps".Translate(',
     PROOF),

    # Replaced at BOTH sites. Replacing one left the other matching a bare `in` test, which is
    # what made the counted form of the claim necessary.
    ("weight stops using Core's mass utility", PLANNER,
     "MassUtility.CanEverCarryAnything(pawn)", "pawn.inventory != null", PROOF),

    ("weight stops using Core's free-space reading", PLANNER,
     "MassUtility.FreeSpace(pawn)", "0f", PROOF),

    ("the window is quoted from the base instead of the tier", PANE,
     "gate.PortalWindowTicksForTier", "108000", PROOF),

    ("a sustained connection is given a fake total", PLANNER,
     "            if (gate.PortalOpeningIsIndefinite) { return -1f; }\n", "", PROOF),

    ("THE COST PREVIEW USES THE RAW PROP, NOT THE FOOTPRINT-SCALED DRAW", PLANNER,
     "gate.OpeningPowerDrawWatts", "3500f", PROOF),

    ("the reserve stops being quoted beside the cost", PANE,
     '            listing.Label("RR_Plan_Reserve".Translate(\n'
     "                WattDays(gate.ReturnReserveStoredWattDays),\n"
     "                WattDays(gate.EmergencyReturnCostWattDays)));\n", "", PROOF),

    ("the planner is drawn after the dispatch button", DISPATCH_PANE,
     "            listing.GapLine();\n            DrawCrewPlanner(listing, campaign, gate);\n"
     "            listing.GapLine();\n", "", PROOF),

    # ------------------------------------------------------ rows 1031/1032, the distinction
    ("SETTLEMENT STOPS CONSULTING THE FIELD CONDITION", SUPPLY,
     "                if (!FieldConditionMet(contract)) { continue; }\n", "", PROOF),

    ("a plain contract stops settling", MISSIONS,
     "if (contract.requiredSurveyedRooms <= 0) { return true; }",
     "if (contract.requiredSurveyedRooms <= 0) { return false; }", PROOF),

    ("the field condition stops being saved", RECORDS,
     'Scribe_Values.Look(ref requiredSurveyedRooms, "rr_requiredSurveyedRooms", 0);', "", PROOF),

    ("the saved field loses its default", RECORDS,
     'Scribe_Values.Look(ref requiredSurveyedRooms, "rr_requiredSurveyedRooms", 0);',
     'Scribe_Values.Look(ref requiredSurveyedRooms, "rr_requiredSurveyedRooms");', PROOF),

    ("a mission stops being distinguishable from a contract", RECORDS,
     "public bool IsOddConsignment", "public bool IsOddConsignmentUnused", PROOF),

    ("A MISSION DRAWS FROM THE UNION INSTEAD OF ITS OWN COORDINATE", MISSIONS,
     "List<string> pool = target.oddGoodsDefNames", "List<string> pool = KnownOddGoods()", PROOF),

    ("a mission stops naming a coordinate", MISSIONS,
     "coordinateId = target.Id,", "coordinateId = null,", PROOF),

    ("a mission asks for survey work already done", MISSIONS,
     "surveyed + ConsignmentSurveyStep", "surveyed", PROOF),

    ("a fully surveyed coordinate becomes a valid target", MISSIONS,
     "                if (coordinate.Rooms.All(room => room.Surveyed)) { continue; }\n", "",
     PROOF),

    ("the mission pick starts using Rand", MISSIONS,
     "int roll = Gen.HashCombineInt(campaignSeed, ~consignmentOfferIndex);",
     "int roll = Rand.Int;", PROOF),

    ("the pool is rolled against unsorted", MISSIONS,
     ".OrderBy(name => name, StringComparer.Ordinal)", "", PROOF),

    ("the coordinate tie-break stops being ordinal", MISSIONS,
     ".OrderBy(c => c.Id, StringComparer.Ordinal)", "", PROOF),

    ("a mission stops paying more than a contract", MISSIONS,
     "DemandPayment(definition, count) * (double)ConsignmentPremium",
     "DemandPayment(definition, count) * 1d", PROOF),

    ("missions stop being capped lower than contracts", MISSIONS,
     "MaxOpenConsignments = 1", "MaxOpenConsignments = 3", PROOF),

    ("A DEADLINE ARRIVES ON THE MISSION", MISSIONS,
     "            if (count < 1 || payment < 1) { consignmentOfferIndex++; return; }",
     "            int expiryTick = now + 180000;\n"
     "            if (count < 1 || payment < 1 || expiryTick < 0) { consignmentOfferIndex++; return; }",
     PROOF),

    ("the mission stops being ticked", SERVICES,
     "            if (now % 60 == 0) { UpdateOddConsignmentMissions(); }\n", "", PROOF),

    ("the mission stops being saved", COMPONENT,
     "            ExposeConsignmentMissions();\n", "", PROOF),

    ("the odd mark gains a coordinate and the claim is re-opened", ORIGIN,
     "    public sealed class CompRimroomsOddOrigin : ThingComp\n    {",
     "    public sealed class CompRimroomsOddOrigin : ThingComp\n    {\n"
     "        private string coordinateId;", PROOF),

    # ------------------------------------------------------ row 1033, the pane
    ("THE PANE GOES BACK TO ONE SET OF TERMS FOR EVERYTHING", WINDOW,
     "DrawContractTerms(listing, campaign, contract);",
     'listing.Label("RR_UI_ContractTerms".Translate());', PROOF),

    ("the survey contract loses its own terms", TERMS,
     '                listing.Label("RR_UI_ContractTerms".Translate());\n                return;\n',
     "                return;\n", PROOF),

    ("the pane stops saying what is wanted", TERMS,
     '            listing.Label("RR_UI_DemandWanted".Translate(\n'
     '                contract.RequiredCount.ToString("N0"), label));\n', "", PROOF),

    ("the pane stops saying how much was handed over", TERMS,
     "contract.DeliveredCount.ToString(\"N0\")", '"0"', PROOF),

    ("the pane stops saying ordinary stock will not do", TERMS,
     'listing.Label("RR_UI_DemandOddOnly".Translate());', "// nothing", PROOF),

    ("a demand key loses its string", SUPPLY_KEYS,
     "  <RR_UI_DemandWanted>", "  <RR_UI_DemandWantedX>", PROOF),

    ("an unresolvable definition goes blank instead of being stated", TERMS,
     '? "RR_UI_DemandUnknownThing".Translate().ToString()', '? ""', PROOF),

    ("the field condition stops being shown as progress", TERMS,
     "campaign.FieldConditionProgress(contract).ToString(\"N0\")", '"0"', PROOF),

    ("the pane stops saying whether the condition is met", TERMS,
     '                ? "RR_UI_ConsignmentFieldMet".Translate()\n'
     '                : "RR_UI_ConsignmentFieldUnmet".Translate());\n',
     "                ? \"RR_UI_DemandOddOnly\".Translate()\n"
     "                : \"RR_UI_DemandOddOnly\".Translate());\n", PROOF),

    ("the coordinate is shown by id instead of label", TERMS,
     "named == null ? contract.CoordinateId : named.Label", "contract.CoordinateId", PROOF),
]


def write_verified(path, text):
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


print("baseline -- each target must pass before anything is planted")
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
