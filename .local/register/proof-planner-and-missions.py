# -*- coding: utf-8 -*-
"""Rows 728, 1031, 1032, 1033: the crew planner, and missions as distinct from contracts.

The absolutes in these rows are the point of this file:

  * **Row 728: *"must not own connection existence"*.** The planner is a readout. It returns no
    `CompanyActionResult`, nothing in the expedition or gate code calls it, and deleting it would
    change no outcome in the game. `Dispatch` stays the only authority on whether a crossing
    happens. Asserted structurally: the type is referenced from `UI/` and nowhere else.

  * **Row 1032: a mission must be distinct from a contract.** The distinction is a field
    condition -- survey work at depth -- and it is asserted to be *load-bearing*: settlement must
    consult it, and a record without one must still settle exactly as it always did.

  * **No deadline.** `check-campaign-absolutes.py` owns that rule; this asserts the mission did
    not smuggle one in under another name.

  * **Row 1033: the pane must describe the contract in front of it.** It printed the *survey*
    contract's terms on every contract, including odd-goods demands, which is worse than silence.

One measured fact this rests on, and it closed off the obvious design: **`ThingOrigin` has three
values and carries no coordinate**, and `CompRimroomsOddOrigin.AllowStackWith` lets odd stacks
merge. So no demand can ever verify *which* coordinate a good came from, and a mission that
claimed to would be lying. The field condition is checked against recorded survey state instead.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages", "English",
                     "Keyed")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"^\s*///.*$", "", text, flags=re.M)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


planner = strip_cs_comments(read(os.path.join(SRC, "Expedition", "CrewPlanner.cs")))
planner_pane = strip_cs_comments(read(os.path.join(SRC, "UI", "OperationsCrewPlanner.cs")))
dispatch_pane = strip_cs_comments(read(os.path.join(SRC, "UI", "OperationsExpeditions.cs")))
expedition = strip_cs_comments(read(os.path.join(SRC, "Expedition",
                                                 "RimroomsExpeditionComponent.cs")))
missions = strip_cs_comments(read(os.path.join(SRC, "Company", "OddConsignmentMissions.cs")))
supply = strip_cs_comments(read(os.path.join(SRC, "Company", "OddSupplyContracts.cs")))
records = strip_cs_comments(read(os.path.join(SRC, "Company", "CampaignRecords.cs")))
terms = strip_cs_comments(read(os.path.join(SRC, "UI", "OperationsContractTerms.cs")))
window = strip_cs_comments(read(os.path.join(SRC, "UI", "MainTabWindow_Operations.cs")))
services = strip_cs_comments(read(os.path.join(SRC, "Company", "CampaignServices.cs")))
component = strip_cs_comments(read(os.path.join(SRC, "Company", "RimroomsCampaignComponent.cs")))
origin = strip_cs_comments(read(os.path.join(SRC, "Economy", "CompRimroomsOddOrigin.cs")))
planner_keys = read(os.path.join(KEYED, "RR_CrewPlanner.xml"))
supply_keys = read(os.path.join(KEYED, "RR_OddSupply.xml"))

# --------------------------------------------------------------------------------------------
print("")
print("row 728's absolute: the planner does not own connection existence")
print("-" * 90)

# A readout cannot refuse. If it ever returned a CompanyActionResult, somebody would eventually
# check it -- and the row forbids exactly that.
check("the planner returns no action result",
      "CompanyActionResult" not in planner.replace(
          "ExpeditionCargo.CheckCapacity(pawn).Success", ""),
      "-- the one call it makes reads `.Success` off somebody else's result and returns a key; "
      "handing one back would invite a caller to gate on it")

check("the planner refuses nothing",
      "Refuse(" not in planner and "CompanyActionResult.Refused" not in planner)

# The structural half, and the one that cannot rot: nothing outside the interface may reference
# it. A call from Dispatch, CheckCrew or any gate code would make it load-bearing.
referencing = []
for path in sorted(glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)):
    rel = os.path.relpath(path, SRC).replace("\\", "/")
    if rel.startswith("UI/") or rel == "Expedition/CrewPlanner.cs":
        continue
    if "CrewPlanner" in strip_cs_comments(read(path)):
        referencing.append(rel)
check("nothing outside the interface references the planner", not referencing,
      "-- %s does. Row 728: *\"must not own connection existence\"*, so a call from the "
      "expedition or gate code is the thing this claim exists to catch" % ", ".join(referencing))

check("dispatch still holds every refusal itself",
      'return Refuse("RR_Exp_InvalidCrew")' in expedition
      and 'return Refuse("RR_Exp_AwaitingDebrief")' in expedition,
      "-- the planner explains dispatch's answers; it must not become them")

# --------------------------------------------------------------------------------------------
print("")
print("row 728: every reason is named, and they are the conditions dispatch actually enforces")
print("-" * 90)

REASONS = ("RR_Plan_Dead", "RR_Plan_NotEmployed", "RR_Plan_IsOperator",
           "RR_Plan_AwaitingDebrief", "RR_Plan_Downed", "RR_Plan_MentalState",
           "RR_Plan_CannotMove", "RR_Plan_NotAtHeadquarters", "RR_Plan_Hauling",
           "RR_Plan_OverCapacity")
for reason in REASONS:
    check("%s is a named reason" % reason,
          reason in planner and ("<%s>" % reason) in planner_keys,
          "-- before this, five of these were one key: RR_Exp_InvalidCrew")

# Each reason must read the same state dispatch reads. A planner with its own idea of "downed"
# would say ready about somebody dispatch refuses, which is worse than saying nothing.
check("the operator check is the gate's own assigned operator",
      "pawn == gate.AssignedOperator" in planner,
      "-- dispatch refuses `crew.Contains(gate.AssignedOperator)`; any other spelling is a "
      "second opinion")
check("the debrief check is the campaign's own",
      "campaign.AwaitingDebrief(pawn)" in planner)
check("the capacity check is the cargo code's own",
      "ExpeditionCargo.CheckCapacity(pawn)" in planner,
      "-- a mass calculation of our own here would drift from the one that actually refuses")
check("the movement check is Core's own capacity",
      "PawnCapacityDefOf.Moving" in planner)
# Counted, not merely present. The panel uses the cap twice -- once to print it and once to
# compare against it -- and a plant that replaced one with a literal `"3"` left the other
# matching. Every claim in this file that says "is used" now says how many times.
check("the crew cap comes from one place",
      "MaxCrew = 3" in planner and planner_pane.count("CrewPlanner.MaxCrew") >= 2,
      "-- dispatch accepts 1..3; the panel prints it and compares against it, and a literal in "
      "either place drifts the first time that changes (found %d use site(s))"
      % planner_pane.count("CrewPlanner.MaxCrew"))

# --------------------------------------------------------------------------------------------
print("")
print("row 728: skill, weight, window and cost -- the four checks the row names")
print("-" * 90)

check("skills are Core's own, not content of ours",
      "SkillDefOf.Intellectual" in planner and "SkillDefOf.Medicine" in planner
      and "SkillDefOf.Shooting" in planner)
check("a disabled skill does not count as held",
      "record != null && !record.TotallyDisabled && record.Level > 0" in planner
      and "if (record == null || record.TotallyDisabled) { continue; }" in planner,
      "-- a pawn incapable of a skill has a record for it, and reading only the level would "
      "report them as covering it. BOTH readers are asserted: `TotallyDisabled` appearing "
      "somewhere in the file is not a claim that the gap finder consults it")
check("a skill gap is reported and not enforced",
      'listing.Label("RR_Plan_SkillGaps".Translate(' in planner_pane
      and "MissingSkills" in planner,
      "-- a player may have good reasons to send two shooters and no medic. The claim is on the "
      "`listing.Label(` call: a key held in a variable and never drawn satisfies a search for "
      "the key and shows the player nothing")
check("weight is Core's own mass utility",
      planner.count("MassUtility.FreeSpace") >= 2
      and planner.count("MassUtility.CanEverCarryAnything") >= 2,
      "-- per candidate and per crew, two readers each; one occurrence surviving a plant on the "
      "other is what a bare `in` test cannot see (found %d and %d)"
      % (planner.count("MassUtility.FreeSpace"),
         planner.count("MassUtility.CanEverCarryAnything")))
check("the window is the gate's own tier calculation",
      "gate.PortalWindowTicksForTier" in planner_pane
      and "PortalOpeningIsIndefinite" in planner_pane,
      "-- the ladder is four company projects; quoting a base window would be wrong for any "
      "branch that had advanced")
check("a sustained connection is not given a fake total",
      "if (gate.PortalOpeningIsIndefinite) { return -1f; }" in planner
      and "RR_Plan_WindowSustained" in planner_pane,
      "-- at the indefinite tier there is a rate and no total, and inventing one would be worse "
      "than saying so. The guard is matched whole: `return -1f;` appears three times in that "
      "method, so testing for it proves nothing about which branch survives")
check("the cost preview uses the footprint-scaled draw",
      "gate.OpeningPowerDrawWatts" in planner,
      "-- GateFootprint scales the raw prop by cell count and discounts it by "
      "RR_Cap_EfficientAperture, so the raw prop is not what any gate above 1x1 actually draws")
check("the cost is quoted against the reserve",
      '"RR_Plan_Reserve".Translate(' in planner_pane
      and "WattDays(gate.EmergencyReturnCostWattDays)" in planner_pane,
      "-- watt-days are only useful next to the number they have to cover. Matched on the call: "
      "`RR_Plan_Reserve` is a prefix of `RR_Plan_ReserveShort`, so the short-reserve warning "
      "alone satisfied the old test")
check("the planner is drawn before the dispatch button",
      dispatch_pane.index("DrawCrewPlanner") < dispatch_pane.index('"RR_UI_DispatchCrew"'),
      "-- its whole value is being readable instead of pressing the button and being told "
      "'invalid crew'")

# --------------------------------------------------------------------------------------------
print("")
print("rows 1031 and 1032: a mission is distinct from a contract, and the difference bites")
print("-" * 90)

check("a mission is a record with a field condition",
      "requiredSurveyedRooms" in records
      and re.search(r"public bool IsOddConsignment\s*$", records, re.M) is not None
      and "contract.IsOddConsignment" in terms
      and "c.IsOddConsignment" in missions,
      "-- declaration AND both readers. `IsOddConsignment` is a prefix of any renaming of it, so "
      "a plant that appended `Unused` to the property satisfied the old test")
check("the field condition is saved with a default",
      'Scribe_Values.Look(ref requiredSurveyedRooms, "rr_requiredSurveyedRooms", 0)' in records,
      "-- an undefaulted field would change how every contract in an existing save behaves")
check("a record with no condition reports it met",
      "if (contract.requiredSurveyedRooms <= 0) { return true; }" in missions,
      "-- that is what lets one settlement path serve a plain contract and a mission")

# THE claim of this batch. If settlement does not consult the condition, a mission is a contract
# with a longer title and rows 1031/1032 are not closed.
check("SETTLEMENT CONSULTS THE FIELD CONDITION",
      "if (!FieldConditionMet(contract)) { continue; }" in supply,
      "-- without this a consignment pays out on delivery alone and is indistinguishable from "
      "a contract, which is exactly what row 1032 says it must not be")
check("there is one settlement path, not two",
      "SettleSupplyContracts" in supply and "SettleConsignment" not in missions,
      "-- two paths that both consume goods and both pay money will eventually disagree about "
      "one of them")

check("a mission draws from the coordinate it names",
      "target.oddGoodsDefNames" in missions,
      "-- the contract draws from the union of every coordinate; a mission is about a place")
check("a mission names the coordinate on the record",
      "coordinateId = target.Id" in missions)
check("a mission demands survey work not already done",
      "surveyed + ConsignmentSurveyStep" in missions
      and "if (required <= surveyed) {" in missions,
      "-- a condition already satisfied when offered is not a reason to explore anything")
check("a fully surveyed coordinate is never asked for",
      "coordinate.Rooms.All(room => room.Surveyed)" in missions,
      "-- an unanswerable demand is the defect the contract generator was built to avoid")
check("the pick is deterministic, never Rand",
      "Gen.HashCombineInt(campaignSeed" in missions and "Rand." not in missions,
      "-- reloading must not reroll a hard mission into an easy one")
check("the pool is sorted ordinally before anything is rolled against it",
      "OrderBy(name => name, StringComparer.Ordinal)" in missions,
      "-- invariant 26")
check("the coordinate choice is tie-broken ordinally",
      "OrderBy(c => c.Id, StringComparer.Ordinal)" in missions,
      "-- two coordinates at one depth must resolve the same way on every load")
check("a mission pays more than a contract for the same goods",
      "ConsignmentPremium = 2f" in missions
      and "DemandPayment(definition, count) * (double)ConsignmentPremium" in missions,
      "-- it buys the survey work as well, and the survey work is the part that was wanted. The "
      "constant existing is not the claim; the multiplication is")
check("missions are capped lower than contracts",
      "MaxOpenConsignments = 1" in missions,
      "-- three simultaneous demands for deeper survey work read as a backlog, not a direction")

# No deadline, under any name. check-campaign-absolutes.py owns the rule; this asserts the new
# file did not reach for one.
check("the mission ships no deadline",
      not re.search(r"(expir|deadline|timeLimit|timeout)", missions, re.I),
      "-- the company waits as long as it takes, and a mission is harder because of what it "
      "asks rather than because of a clock")

check("the mission is ticked", "UpdateOddConsignmentMissions();" in services)
check("the mission is saved", "ExposeConsignmentMissions();" in component)

# The measured fact that closed off the obvious design. If the origin mark ever gains a
# coordinate, this claim fails and the mission can be made stricter -- which is the point.
check("the odd mark still carries no coordinate",
      "coordinateId" not in origin and "AllowStackWith" in origin,
      "-- ThingOrigin is Outside/Backrooms/Unknown and odd stacks merge, so no demand can "
      "verify WHICH coordinate a good came from. The field condition is checked against "
      "recorded survey state instead, which cannot be faked by hauling")

# --------------------------------------------------------------------------------------------
print("")
print("row 1033: the pane describes the contract in front of it")
print("-" * 90)

check("the pane no longer prints one set of terms for everything",
      'listing.Label("RR_UI_ContractTerms".Translate());' not in window
      and "DrawContractTerms(listing, campaign, contract);" in window,
      "-- it printed the SURVEY contract's terms on odd-goods demands, which is worse than "
      "silence: silence sends a player looking, a confident wrong answer stops them")
check("the survey terms are still shown on a survey contract",
      'if (!contract.IsOddSupply)' in terms
      # **ON THE HOVER OF THE PANE'S OWN HEADING, which is a stronger assertion than the
      # one it replaces.** This used to check that the string was passed to `Label`; it now
      # checks that it is the `detail:` of a `DrawHeading` whose `heading:` is the short
      # line, so a pass that dropped the hover and left the heading -- forty-one words of
      # survey method silently gone -- fails here instead of reading as a tidy-up.
      and 'heading: "RR_UI_ContractTermsBrief".Translate(),' in terms
      and 'detail: "RR_UI_ContractTerms".Translate());' in terms,
      "-- the old text was right for the contract it was written for, and every word of it is "
      "still reachable -- it moved to the heading's tooltip rather than being cut")

for key in ("RR_UI_DemandWanted", "RR_UI_DemandDelivered", "RR_UI_DemandOddOnly"):
    check("%s is drawn and resolves" % key,
          key in terms and ("<%s>" % key) in supply_keys)

check("what was wanted and what was handed over are both shown",
      "contract.RequiredCount" in terms and "contract.DeliveredCount" in terms,
      "-- all three demand fields were saved, given public accessors, and read by nothing but "
      "the settlement code")
check("a missing definition is stated rather than blank",
      "RR_UI_DemandUnknownThing" in terms,
      "-- an uninstalled mod leaves a demand whose thing cannot be resolved")
check("a mission's field condition is shown as progress",
      "FieldConditionProgress" in terms and "RR_UI_ConsignmentSurvey" in terms,
      "-- a player who cannot see how far along they are cannot decide whether to push on")
check("a mission says whether the condition is met",
      "RR_UI_ConsignmentFieldMet" in terms and "RR_UI_ConsignmentFieldUnmet" in terms)
check("the named coordinate is shown by label, not by id",
      "named == null ? contract.CoordinateId : named.Label" in terms)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the planner explains dispatch and owns nothing, a mission does not settle "
      "without the survey work, and the pane says what each contract actually wants")
