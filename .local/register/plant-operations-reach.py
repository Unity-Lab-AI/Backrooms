# -*- coding: utf-8 -*-
"""Planted faults against `proof-operations-reach.py`.

## The ones that matter most

**A card going silent again.** The station had no inspect card at all and the
beacon said nothing in the one state where a player needed telling. Both are one
`return null` away from being back where they were, and neither failure would
throw, log or look broken -- the player would simply never learn the thing.

**A link losing its guard.** `CanJump` is what stops a row being offered that
cannot arrive. Replace it with `true` and the button still draws, still clicks,
and does nothing at all -- which is how somebody concludes a feature is broken.

**The schedule growing a clock of its own.** `CAMPAIGN_CHART.md` 1.1 is the single
most load-bearing rule in this package. A standing recall that closed the gate, or
that fired off its own counter rather than off the gate's window, would be the
first timer in the mod and would read as a feature rather than a violation.

**A goal paying twice.** The ledger's operation id is the only thing standing
between eleven tutorial payouts and an income stream. Put the gate's id in that
string and every door the branch builds pays the chain again.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

LINKS = "src/RimroomsAsyncIndustries/UI/OperationsLinks.cs"
PERSONNEL = "src/RimroomsAsyncIndustries/UI/OperationsPersonnel.cs"
BINDING = "src/RimroomsAsyncIndustries/UI/OperationsGateBinding.cs"
SUPPLY = "src/RimroomsAsyncIndustries/Procurement/CorporateSupplyGizmos.cs"
STATION = "src/RimroomsAsyncIndustries/Gate/CompRimroomsGateConsole.cs"
BEACON = "src/RimroomsAsyncIndustries/Economy/CompRimroomsCreditBeacon.cs"
RECALL = "src/RimroomsAsyncIndustries/Gate/GateStandingRecall.cs"
PAYOUTS = "src/RimroomsAsyncIndustries/Gate/GateStartupPayouts.cs"
GATE = "src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs"
EQUIPMENT = "src/RimroomsAsyncIndustries/Gate/GateEquipmentLinks.cs"
REVIEW = "src/RimroomsAsyncIndustries/Company/EvidenceReview.cs"
EVIDENCE_UI = "src/RimroomsAsyncIndustries/UI/OperationsEvidence.cs"
ROLES = ("Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsGateEquipmentDefs/"
         "RR_GateEquipment.xml")
LINK_KEYED = ("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/"
              "RR_GateLinks.xml")
PROOF = ".local/register/proof-operations-reach.py"
CHR_NL = chr(10)

PLANTS = [
    # ================================================= the cards say what a thing is
    ("THE STATION LOSES ITS INSPECT CARD AGAIN", STATION,
     "        public override string CompInspectStringExtra()",
     "        private string UnusedInspect()", PROOF),

    ("the station stops saying why nothing is being crafted", STATION,
     '                lines.Add((gateControl ? "RR_NativeGate_StationGateControl"' + CHR_NL
     + '                    : "RR_NativeGate_StationNormalOp").Translate().ToString());' + CHR_NL,
     "", PROOF),

    ("THE STATION STARTS TALKING ON AN ORDINARY COLONY BENCH", STATION,
     "                if (campaign == null) { return null; }",
     "                if (campaign == null) { }", PROOF),

    ("THE BEACON GOES SILENT IN THE STATE WHERE IT MATTERS", BEACON,
     '            return "RR_CreditBeacon_Undesignated".Translate(waiting.ToString("N0")).ToString();',
     "            return null;", PROOF),

    ("the beacon starts talking on every trade beacon in the colony", BEACON,
     "            if (waiting <= 0L) { return null; }", "            if (false) { return null; }",
     PROOF),

    # ================================================= the links reach what they name
    ("THE RESEARCH ROW GOES BACK TO PRINTING A RAW defName", SUPPLY,
     "                            UI.OperationsLinks.ResearchLabel(tier.requiredResearchDefName)),",
     "                            tier.requiredResearchDefName),", PROOF),

    ("the research row loses its link and goes back to a null action", SUPPLY,
     "                        required == null" + CHR_NL
     + "                            ? (Action)null" + CHR_NL
     + "                            : delegate { UI.OperationsLinks.ShowResearch(required); }));",
     "                        null));", PROOF),

    ("THE RESEARCH LINK STOPS SELECTING THE PROJECT, so it opens the tree at nothing", LINKS,
     "            if (window != null) { window.Select(project); }", "", PROOF),

    ("the research link starts reassigning the player's current project", LINKS,
     "            if (window != null) { window.Select(project); }",
     "            Find.ResearchManager.SetCurrentProject(project);", PROOF),

    ("A LINK IS OFFERED THAT CANNOT ARRIVE", LINKS,
     "            return target.IsValid && CameraJumper.CanJump(target);",
     "            return true;", PROOF),

    ("the jump stops guarding itself at the point of use", LINKS,
     "            if (!CanReach(target)) { return; }", "", PROOF),

    ("THE PAWN LINK DISAPPEARS", PERSONNEL,
     "            { OperationsLinks.Show(pawn); }", "            { }", PROOF),

    ("the pawn link refuses in silence instead of by name", PERSONNEL,
     '                refusal: OperationsLinks.CanReach(pawn)' + CHR_NL
     + "                    ? TaggedString.Empty" + CHR_NL
     + '                    : "RR_Personnel_ShowPawnUnreachable".Translate(pawn.LabelShortCap),',
     "                refusal: TaggedString.Empty,", PROOF),

    ("THE BUILDING LINK GOES BACK TO ITS OWN COPY OF THE CALL", BINDING,
     "            if (choice != null && OperationsLinks.CanReach(choice)" + CHR_NL
     + '                && listing.ButtonText("RR_NativeGate_InspectRole".Translate(choice.LabelCap)))'
     + CHR_NL + "            { OperationsLinks.Show(choice); }",
     "            if (choice != null && choice.Spawned" + CHR_NL
     + '                && listing.ButtonText("RR_NativeGate_InspectRole".Translate(choice.LabelCap)))'
     + CHR_NL + "            { CameraJumper.TryJumpAndSelect(choice); }", PROOF),

    # ================================================= the schedule rides the gate's own clock
    ("THE SCHEDULING SURFACE IS UNREACHABLE", GATE,
     "            foreach (Gizmo gizmo in StandingRecallGizmos()) { yield return gizmo; }" + CHR_NL,
     "", PROOF),

    # **THE 1.1 VIOLATION.** A standing recall with its own counter is the first timer in the mod.
    ("THE STANDING RECALL GROWS A CLOCK OF ITS OWN", RECALL,
     "            if (openingTicksRemaining > standingRecallTicks) { return; }",
     "            if (Find.TickManager.TicksGame % 60000 != 0) { return; }", PROOF),

    ("THE STANDING RECALL STARTS CLOSING THE GATE", RECALL,
     "            CompanyActionResult result = trips.Recall();",
     "            CompanyActionResult result = trips.Recall(); CloseOpening();", PROOF),

    ("it stops being off by default", RECALL,
     "            if (standingRecallTicks <= 0 || standingRecallIssued) { return; }",
     "            if (standingRecallIssued) { return; }", PROOF),

    ("A FOURTH THRESHOLD APPEARS, so the schedule can sit between two warnings", RECALL,
     "        internal static readonly int[] RecallOptionTicks = { 0, 417, 208, 83 };",
     "        internal static readonly int[] RecallOptionTicks = { 0, 417, 300, 208, 83 };",
     PROOF),

    ("a value off the list stops being refused", RECALL,
     "            for (int index = 0; index < RecallOptionTicks.Length; index++)" + CHR_NL
     + "            {" + CHR_NL
     + "                if (RecallOptionTicks[index] != ticks) { continue; }" + CHR_NL
     + "                standingRecallTicks = ticks;" + CHR_NL
     + "                return;" + CHR_NL
     + "            }",
     "            standingRecallTicks = ticks;", PROOF),

    ("THE ORDER FIRES EVERY TICK instead of once per opening", RECALL,
     "            standingRecallIssued = true;" + CHR_NL, "", PROOF),

    ("an order from a previous opening carries into the next one", GATE,
     "            ResetStandingRecall();" + CHR_NL, "", PROOF),

    ("the schedule is named for a deadline", RECALL,
     "        private int standingRecallTicks;", "        private int recallDeadlineTicks;",
     PROOF),

    # ================================================= the company pays for goals reached
    ("THE PAYOUTS STOP READING THE ONE CHAIN and go back to their own conditions", PAYOUTS,
     "            List<GateStartupChecklist.GateStep> steps = GateStartupChecklist.Steps(gate);",
     "            List<GateStartupChecklist.GateStep> steps = null;", PROOF),

    ("the prize at the end is flattened to a nudge", PAYOUTS,
     "            900,  // 11 a connection open. The prize.",
     "            40,   // 11 a connection open. The prize.", PROOF),

    ("THE PAYER STOPS BEING THE COMPANY and the money comes from nowhere", PAYOUTS,
     "                CompanyActionResult result = campaign.PostTransaction(" + CHR_NL
     + '                    operationId, amount, "RR_Startup_PayoutReason", null);',
     "                CompanyActionResult result = CompanyActionResult.Applied();", PROOF),

    # **THE EXPLOIT.** Put the gate in the id and every door pays the chain again.
    ("A GOAL PAYS ONCE PER GATE instead of once per branch", PAYOUTS,
     '                string operationId = "rr_startupGoal:" + step.Number;',
     '                string operationId = "rr_startupGoal:" + step.Number + ":"' + CHR_NL
     + "                    + gate.parent.thingIDNumber;", PROOF),

    ("the payouts grow their own saved bookkeeping beside the ledger", PAYOUTS,
     "            if (!result.Success || result.AlreadyApplied) { continue; }",
     "            if (!result.Success) { continue; } // Scribe_Values.Look(ref paid);", PROOF),

    ("THE ELEVEN LABELS ARE RESOLVED EVERY TICK FOR EVERY GATE", GATE,
     "            if (GateStartupPayouts.ShouldCheck(parent)) { GateStartupPayouts.Pay(this); }",
     "            GateStartupPayouts.Pay(this);", PROOF),

    # ================================================= the room functions are functions
    ("A NAMED ROOM FUNCTION DISAPPEARS", ROLES,
     "    <defName>RR_Link_Armory</defName>", "    <defName>RR_Link_Gunrack</defName>", PROOF),

    # **RE-AIMED 0.12.89-dev.** This anchored on `if (!role.Accepts(linked)) { continue; }`, which
    # the role-record change replaced -- `check-plant-anchors.py` caught it before the sweep did.
    # The fault is the same and the new form is stronger: dropping the guard entirely makes every
    # linked thing count toward every role's stock, so the canteen is stocked by the armory.
    ("A ROLE'S STOCK COUNTS EVERY LINK, so a rifle on a shelf stocks the canteen", EQUIPMENT,
     "                if (RoleOf(linked) != role) { continue; }" + CHR_NL, "", PROOF),

    ("the shortfall stops being read off the gate", EQUIPMENT,
     "                string shortfall = StockShortfallReadout(role);" + CHR_NL
     + "                if (shortfall != null) { parts.Add(shortfall); }" + CHR_NL, "", PROOF),

    ("A RISK BECOMES AN ADJECTIVE", LINK_KEYED,
     "A crew that meets something hostile down there has nothing to meet it with.",
     "There is something deeply unsettling about an empty armory.", PROOF),

    ("a risk points at a key that does not resolve", ROLES,
     "<riskKey>RR_GateLink_RiskCanteen</riskKey>",
     "<riskKey>RR_GateLink_RiskCanteenXX</riskKey>", PROOF),

    ("A ROLE NOTHING CAN FILL IS OFFERED AGAIN", EQUIPMENT,
     "                .Where(definition => definition.Fillable)" + CHR_NL, "", PROOF),

    ("the load-time rule on a half-declared stock need is removed", EQUIPMENT,
     "            if (stockTarget > 0 && string.IsNullOrEmpty(stockCategoryDefName))",
     "            if (false)", PROOF),

    # ================================================= the review count reached its surface
    ("THE AWAITING-REVIEW COUNT LOSES ITS SURFACE AGAIN", EVIDENCE_UI,
     '                heading: "RR_UI_ReviewAwaitingBrief".Translate(campaign.AwaitingReviewCount()),',
     '                heading: "RR_UI_ReviewAwaitingBrief".Translate(0),', PROOF),

    ("the count stops going through the one accessor", REVIEW,
     "            return RecordsAwaitingReview().Count();",
     "            return evidence.Count(AwaitsReview);", PROOF),
]

_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def write_verified(path, text):
    """Write, and do not believe it until it reads back identical. Retried both ways."""
    last = None
    for attempt in range(6):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.4 * (attempt + 1))
    sys.stderr.write("FATAL: could not write %s (%s) -- sentinel left in place on purpose\n"
                     % (path, last))
    sys.exit(3)


ORIGINALS = {path: io.open(path, encoding="utf-8").read()
             for path in sorted({plant[1] for plant in PLANTS})}

print("baseline -- the target must pass before anything is planted")
for command in sorted({plant[4] for plant in PLANTS}):
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
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
for path, text in ORIGINALS.items():
    if io.open(path, encoding="utf-8").read() != text:
        sys.stderr.write("%s IS NOT AS IT WAS FOUND -- CHECK BY HAND\n" % path)
        sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("every target verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
