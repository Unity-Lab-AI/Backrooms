# -*- coding: utf-8 -*-
"""Every surface says what it is, reaches what it names, and pays what it promised.

## What this batch was for

Four owner directions meet here, and all four are about **a thing being readable
and reachable from where the player is standing** rather than only from the
Operations window:

  * *"we also need to be making sure all mod ingame decriptions and informational
    informations for everything is properly in the cards like the game does
    currently"* -- the station had **no inspect card at all**, and the beacon was
    silent in exactly the state where a player needed telling.
  * *"Make each screen deep-link to the relevant pawn, building, map, quest, item,
    research project..."* -- a pawn and a research project had no route out, and
    the research row printed a raw `defName` behind a null action.
  * *"Add schedule, warning, recall, evacuation, emergency close, lost-connection,
    failed return, and rescue workflows"* -- schedule was the last one left.
  * *"and once u follow the quests to get the gate up and running(full totorieal
    quest line payouts on each successful step(the company rewards getting to the
    goals)"*.

## The two properties worth proving, because both have bitten before

**ONE SOURCE FOR A RULE.** The payouts ask `GateStartupChecklist.Steps`, which is
the same list the machine tab and the door's inspect card read. Writing the eleven
conditions a second time is the *"two derivations of one rule"* defect that
produced `RR_Gate_CalibrationUnavailable` meaning eight different things.

**THE ONLY CLOCK IS THE GATE.** `docs/CAMPAIGN_CHART.md` 1.1 is absolute: a gate's
connection has a duration and nothing else in this mod does. The scheduling
surface adds no clock -- it reads the gate's existing window, it is off by
default, and the thing it fires only ever tells the crew to walk home.

Run from the repository root. Exit status is the result.
"""
import io
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# `.local/register/<this>` -- three levels up. Two resolves to `.local`, every read returns ""
# and every absence claim passes against nothing.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

failures = []


def check(claim, held, because=""):
    print("  %-4s %s %s" % ("OK" if held else "FAIL", claim, because if not held else ""))
    if not held:
        failures.append(claim)


def read(*parts):
    path = os.path.join(*parts)
    if not os.path.isfile(path):
        raise SystemExit("ABORT: %s does not exist, so no claim about it means anything" % path)
    text = io.open(path, encoding="utf-8-sig").read()
    if not text.strip():
        raise SystemExit("ABORT: %s is empty, so no claim about it means anything" % path)
    return text


def code_only(text):
    """Source with comments removed.

    **TWO CLAIMS IN THIS FILE FAILED ON THEIR FIRST RUN BECAUSE OF THIS**, and both were the
    claim being wrong rather than the code. An absence claim -- *this file does not contain
    `deadline`*, *this file does not contain `evidence.Count(AwaitsReview)`* -- reads the
    documentation too, and good documentation explains the thing it is avoiding BY NAMING IT.
    `GateStandingRecall.cs` says out loud that anything matching *expiry* or *deadline* is
    refused, and `EvidenceReview.cs` says a second `evidence.Count(AwaitsReview)` would be a
    second definition. Both correct, both comments, both of them tripping an assertion about
    code.

    This is the same lesson `NOW.md` already records from the other direction -- *a plant that
    edits a comment tests nothing* -- and it has now cost a claim in both directions. Every
    absence claim here goes through this.
    """
    without_block = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", without_block)


print("proof-operations-reach")
print("-" * 78)

links = read(SRC, "UI", "OperationsLinks.cs")
personnel = read(SRC, "UI", "OperationsPersonnel.cs")
binding = read(SRC, "UI", "OperationsGateBinding.cs")
supply = read(SRC, "Procurement", "CorporateSupplyGizmos.cs")
station = read(SRC, "Gate", "CompRimroomsGateConsole.cs")
beacon = read(SRC, "Economy", "CompRimroomsCreditBeacon.cs")
recall = read(SRC, "Gate", "GateStandingRecall.cs")
payouts = read(SRC, "Gate", "GateStartupPayouts.cs")
gate = read(SRC, "Gate", "CompRimroomsGate.cs")
equipment = read(SRC, "Gate", "GateEquipmentLinks.cs")
roles = read(MOD, "Defs", "RimroomsGateEquipmentDefs", "RR_GateEquipment.xml")
gate_keyed = read(MOD, "Languages", "English", "Keyed", "RR_Gate.xml")
link_keyed = read(MOD, "Languages", "English", "Keyed", "RR_GateLinks.xml")

# ====================================================== the cards say what a thing is
check("THE STATION HAS AN INSPECT CARD, which it did not",
      "public override string CompInspectStringExtra()" in station
      and "RR_NativeGate_StationUnbound" in station
      and "RR_NativeGate_StationBound" in station,
      "-- the gate had one and the beacon had one; the thing a player clicks to RUN a gate had "
      "nothing, and every piece of its state was readable only by noticing which gizmo label "
      "happened to be showing")

check("and it says why nothing is being crafted when it is running the gate",
      "RR_NativeGate_StationGateControl" in station
      and "RR_NativeGate_StationNormalOp" in station,
      "-- gate control holds the bench's ordinary bills suspended by design, and without a line "
      "saying so that design is indistinguishable from a fault")

check("AND IT IS SILENT ON A BENCH NOBODY BOUND",
      "if (campaign == null) { return null; }" in station,
      "-- this comp is on Core's comms console and machining table, so an unbound bench in an "
      "ordinary colony has to read exactly as it always did")

check("THE BEACON SPEAKS IN THE STATE WHERE IT USED TO BE SILENT",
      "RR_CreditBeacon_Undesignated" in beacon
      and "if (waiting <= 0L) { return null; }" in beacon,
      "-- it read `if (!designated) return null` and stopped, so bonds piled up inside its "
      "radius with nothing banking them and nothing anywhere on the thing saying one toggle was "
      "the answer")

check("and only when there is actually something for it to bank",
      "BondService.BondsInRadius(parent.Map, parent.Position, Props.radius, out waiting);"
      in beacon,
      "-- it sits on Core's OrbitalTradeBeacon, so every trade beacon in every colony carries "
      "it. Dormant-until-designated is the rule, and this speaks at the one moment it is worth "
      "hearing rather than on every beacon anybody owns")

# ====================================================== the links reach what they name
check("THE RESEARCH ROW NO LONGER PRINTS A RAW defName AT THE PLAYER",
      "UI.OperationsLinks.ResearchLabel(tier.requiredResearchDefName)" in supply
      and "tier.LabelCap, tier.requiredResearchDefName), null));" not in supply,
      "-- it showed an internal identifier the game displays nowhere else, behind a null action, "
      "so the one screen that said *you need a research project* named it unrecognisably and "
      "gave no way to go and look")

check("and that row is now a link to the project",
      "UI.OperationsLinks.ShowResearch(required)" in supply,
      "-- the deep link the direction asked for")

check("THE RESEARCH LINK USES CORE'S OWN ROUTE",
      "Find.MainTabsRoot.SetCurrentTab(button);" in links
      and "button.TabWindow as MainTabWindow_Research" in links
      and "window.Select(project)" in links,
      "-- `MainTabWindow_Research.Select` is the public method the research tree's own search box "
      "calls. Confirmed by decompiling the installed assembly rather than remembered")

check("AND IT DOES NOT SET THE PLAYER'S CURRENT PROJECT",
      "SetCurrentProject" not in links,
      "-- a deep link shows somebody where a thing is. Choosing to research it is still theirs, "
      "and quietly reassigning their research would be taking a decision away")

check("A LINK THAT CANNOT ARRIVE IS NEVER OFFERED",
      "CameraJumper.CanJump(target)" in links
      and "if (!CanReach(target)) { return; }" in links,
      "-- *a button that can only refuse is worse than no button*, which is this package's own "
      "rule from the catalogue gizmo. A float-menu row with a null action looks identical to one "
      "with a real action")

check("THE PAWN LINK EXISTS AND REFUSES BY NAME",
      "OperationsLinks.Show(pawn)" in personnel
      and "RR_Personnel_ShowPawnUnreachable" in personnel,
      "-- this screen holds the richest readout of a person anywhere in the package and had no "
      "way to go and look at them. An off-site applicant is a real person who is not standing "
      "anywhere yet, which is worth saying rather than hiding")

check("and the building link goes through the same helper",
      "OperationsLinks.Show(choice)" in binding
      and "OperationsLinks.CanReach(choice)" in binding
      and "CameraJumper.TryJumpAndSelect(choice)" not in binding,
      "-- the pane already had a building link with its own copy of the call and `Spawned` as "
      "its guard. `CanJump` is strictly wider and still never offers a link to nowhere")

# ====================================================== the schedule rides the gate's own clock
check("THE SCHEDULING SURFACE EXISTS",
      "private int standingRecallTicks;" in recall
      and "internal IEnumerable<Gizmo> StandingRecallGizmos()" in recall
      and "foreach (Gizmo gizmo in StandingRecallGizmos())" in gate,
      "-- warning, recall, emergency close, lost-connection, failed return and rescue all "
      "shipped; schedule was the one left on the row")

# **CAMPAIGN_CHART 1.1.** A gate's connection has a duration and nothing else in this mod does.
check("IT ADDS NO CLOCK OF ITS OWN",
      "if (openingTicksRemaining > standingRecallTicks) { return; }" in recall,
      "-- it reads the gate's existing window, which is itself the consequence of power, tech, "
      "maintenance and workforce. That is the only clock 1.1 allows")

check("and it is off until the player sets it",
      "if (standingRecallTicks <= 0 || standingRecallIssued) { return; }" in recall,
      "-- a player who never opens the menu is never scheduled")

check("AND ITS THRESHOLDS ARE THE WARNING THRESHOLDS, NOT NEW ONES",
      "internal static readonly int[] RecallOptionTicks = { 0, 417, 208, 83 };" in recall
      and "const int tenMinutesRemaining = 417;" in gate
      and "const int fiveMinutesRemaining = 208;" in gate
      and "const int twoMinutesRemaining = 83;" in gate,
      "-- a schedule that could sit between two warnings would be a second opinion about when a "
      "window is nearly over. The player schedules to moments the gate already shouts about")

# **A PLANT CORRECTED THIS CLAIM.** The first version asserted
# `for (int index = 0; index < RecallOptionTicks.Length; index++)`, and that exact line appears
# TWICE in the file -- once validating the setter and once building the float menu. So a plant
# that tore the validation out entirely still satisfied it, against the menu's loop, and the
# suite reported MISSED. The property is not *a loop exists*; it is **that a value not on the
# list is not assigned**, which is this one line.
check("and a value off that list is refused",
      "if (RecallOptionTicks[index] != ticks) { continue; }" in recall,
      "-- so a save edit or a later caller cannot introduce the fourth threshold this "
      "deliberately does not have")

check("THE SCHEDULED RECALL ONLY EVER SENDS PEOPLE HOME",
      "trips.Recall()" in recall
      and "Close" not in code_only(recall),
      "-- it cannot close the gate, cannot strand anybody and cannot end the trip. That is what "
      "keeps it on the right side of *no countdown on anything a player is asked to do*")

check("and it is issued once per opening, from the same pass as the warnings",
      "IssueStandingRecall();" in gate
      and "ResetStandingRecall();" in gate
      and "standingRecallIssued = true;" in recall,
      "-- deciding it anywhere else would let the order and the shout drift apart by a tick, "
      "which reads as a bug. An order from a previous opening says nothing about this one")

check("AND IT IS NAMED FOR WHAT IT DOES, not for a deadline",
      not re.search(r"(expiry|deadline|timeout|expires)", code_only(recall), re.I),
      "-- `check-campaign-absolutes.py` refuses those names outright, and rightly: nothing is "
      "lost when this fires, so calling it a deadline would be a lie in the source")

# ====================================================== the company pays for goals reached
check("THE ELEVEN GOALS PAY, AND THE CHAIN IS THE SOURCE",
      "GateStartupChecklist.Steps(gate)" in payouts
      and "private static readonly long[] StepPayoutUsd" in payouts,
      "-- *the same eleven checks the machine tab's status board now reads. One source for "
      "both: a quest step and a status row must never be able to disagree*")

check("and the payouts are scaled, early ones a nudge and finishing the prize",
      "900,  // 11 a connection open. The prize." in payouts,
      "-- the owner's own shape for it: *a payout on each step, not one reward at the end*")

check("THE PAYER IS THE COMPANY, THROUGH THE LEDGER",
      "campaign.PostTransaction(" in payouts
      and '"RR_Startup_PayoutReason"' in payouts,
      "-- *the company rewards getting to the goals*, in the mechanism as well as the fiction. "
      "It lands in the balance with a receipt and a reason")

check("AND NOTHING APPEARS FROM NOWHERE",
      "GenSpawn" not in payouts and "ThingMaker" not in payouts,
      "-- no items spawn and no stack is dropped on the floor. It comes through the existing "
      "credits economy, which is what the row asked for specifically")

# **THE LEDGER IS THE RECORD.** `PostTransaction` is idempotent on its operation id, so there is
# no second bookkeeping field that could drift from the branch's own books.
check("A GOAL CANNOT BE PAID TWICE, AND NO NEW STATE WAS ADDED TO ENSURE IT",
      'string operationId = "rr_startupGoal:" + step.Number;' in payouts
      and "Scribe" not in payouts,
      "-- a repeat with the same amount and reason returns `Existing()` and moves no money, so "
      "*has step six been paid* is already answered permanently by the ledger")

check("and it pays once per BRANCH, not once per gate",
      "+ step.Number;" in payouts and "thingIDNumber" not in payouts.split("ShouldCheck")[0],
      "-- the id names the step and nothing else. Paying per door would turn eleven payouts into "
      "an income stream: build ten doors, collect a hundred and ten receipts")

check("AND THE CHAIN IS NOT RESOLVED EVERY TICK",
      "private const int CheckInterval = 120;" in payouts
      and "GateStartupPayouts.ShouldCheck(parent)" in gate,
      "-- `Steps` resolves eleven keyed strings and walks the portal network. Cheap, not free, "
      "and nothing in the chain completes and un-completes inside two seconds")

# ====================================================== the room functions are functions
role_names = re.findall(r"<defName>(RR_Link_[A-Za-z]+)</defName>", roles)
check("THE FIVE NAMED ROOM FUNCTIONS EXIST",
      all(("RR_Link_" + name) in role_names for name in
          ["Quarantine", "Armory", "Radio", "Receiving", "Canteen"]),
      "-- gate, control, analysis and archive shipped; *quarantine/decontamination, armory, "
      "radio, receiving, cafeteria* were the named gap. Found: %s" % ", ".join(role_names))

check("AND A ROLE KNOWS WHAT SHOULD BE KEPT ON IT",
      "public string stockCategoryDefName;" in equipment
      and "public int stockTarget;" in equipment,
      "-- *Connect each room to concrete capabilities, stock needs, staff jobs, risks, and UI "
      "alerts*. A role that only ACCEPTS equipment is a label; one that knows what belongs on it "
      "is a function. An armory with no weapons in it is not an armory")

check("and the stock is counted on the role's own linked things, never map-wide",
      "SlotGroup group = linked.GetSlotGroup();" in equipment
      and "if (RoleOf(linked) != role) { continue; }" in equipment,
      "-- a branch with five rifles in a bedroom does not have an armory, and counting map-wide "
      "would have reported one. Same laundering the clue system already refuses")

# **AND IT IS THE ROLE THE PLAYER ASSIGNED, which `proof-gate-links.py` forced.** Core ships no
# weapon rack and no receiving bay, so the archive, the armory and the receiving bay are all
# shelves. Counting by `Accepts` would make one shelf satisfy all three at once.
check("AND BY THE ROLE THE PLAYER ASSIGNED, not every role the def could fill",
      "private List<string> gateEquipmentRoles" in equipment
      and "public RimroomsGateEquipmentDef RoleOf(Thing thing)" in equipment
      and "role.Accepts(t) && IsEquipmentLinkActive(t)" not in equipment,
      "-- the *working* count was the site this was missed on first, and the proof's claim caught "
      "it: the working total could have exceeded the linked total on the line beside it")

check("AND WHY A ROOM IS NOT FUNCTIONAL IS READ OFF THE GATE",
      "RR_GateLink_RoleShortfall" in equipment
      and "string shortfall = StockShortfallReadout(role);" in equipment,
      "-- *expose why a room is not functional*. A linked armory with nothing in it reported "
      "exactly the same as a full one")

risk_keys = re.findall(r"<riskKey>([A-Za-z0-9_]+)</riskKey>", roles)
missing_risks = [key for key in risk_keys if ("<%s>" % key) not in link_keyed]
check("and every risk names a consequence that resolves",
      risk_keys and not missing_risks,
      "-- *Risk: 3* tells a player nothing. %s" % (
          ", ".join(missing_risks) if missing_risks else "found %d" % len(risk_keys)))

# Same gate the tells are held to: a fact beats an adjective.
ADJECTIVES = ("eerie", "creepy", "unsettling", "unnerving", "strange", "weird", "sinister",
              "ominous", "uncanny", "disturbing", "horrifying", "terrifying")
risk_bodies = {}
for key in risk_keys:
    found = re.search(r"<%s>(.*?)</%s>" % (key, key), link_keyed, re.S)
    if found:
        risk_bodies[key] = found.group(1)
risk_mood = sorted(key for key, body in risk_bodies.items()
                   if any(word in body.lower() for word in ADJECTIVES))
check("AND A RISK STATES WHAT GOES WRONG, NOT HOW IT FEELS",
      not risk_mood and len(risk_bodies) == len(risk_keys),
      "-- %s. The same rule the inhabitant tells are held to" % ", ".join(risk_mood))

# **THE STAND-ALONE GUARANTEE, APPLIED TO A ROLE.** `thingDefNames` is exact names and
# `ConfigErrors` can only see the list is non-empty.
check("A ROLE NOTHING IN THE LOADED GAME CAN FILL IS HIDDEN, NOT OFFERED",
      "public bool Fillable" in equipment
      and ".Where(definition => definition.Fillable)" in equipment,
      "-- a role naming only DLC or mod buildings would pass load and then silently accept "
      "nothing. `TableLong` was the first choice for the canteen and does not exist; the Core "
      "dining tables are Table2x2c and Table3x3c")

# **A PLANT CORRECTED THIS CLAIM TOO**, and the mistake was the same shape: it asserted that the
# ERROR MESSAGES existed. A message is not a rule. A plant that replaced the condition with
# `if (false)` left both strings sitting in the file and the claim reported green, so the suite
# said MISSED. What has to hold is the test that fires them.
check("and a stock target with nothing to count is refused at load",
      "if (stockTarget > 0 && string.IsNullOrEmpty(stockCategoryDefName))" in equipment
      and "if (!string.IsNullOrEmpty(stockCategoryDefName) && stockTarget <= 0)" in equipment
      and "A role with a stock target must name the category it stocks." in equipment,
      "-- either half alone produces a room function that looks implemented and does nothing")

# ====================================================== the review count reached its surface
review = read(SRC, "Company", "EvidenceReview.cs")
evidence_ui = read(SRC, "UI", "OperationsEvidence.cs")
check("THE AWAITING-REVIEW COUNT REACHED A SURFACE",
      "public IEnumerable<EvidenceRecord> RecordsAwaitingReview()" in review
      and "return RecordsAwaitingReview().Count();" in review
      and "campaign.AwaitingReviewCount()" in evidence_ui,
      "-- it had no caller for a whole checkpoint, which is this file's own warning: *built, "
      "correct and unreachable*. The fix for an unreachable surface is to reach it")

check("and the count is the branch's, counted through the one accessor",
      "evidence.Count(AwaitsReview)" not in code_only(review),
      "-- a second `evidence.Count(AwaitsReview)` would be a second definition of *awaiting "
      "review* that could drift from the first, and would leave the accessor unreached again")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the cards say what a thing is, the links reach what they name, the schedule "
      "rides the gate's own clock, and the company pays for goals reached")
