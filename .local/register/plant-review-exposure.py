# -*- coding: utf-8 -*-
"""Planted faults against review and staff prior exposure.

Both features are the shape that goes wrong here -- **built, correct and unreachable** -- so the
plants are weighted at the call, the save and the surface rather than the logic. The two that
matter most:

* **cutting the button** leaves `ReviewAnalysis` exactly as written and completely unusable,
  which is `RedeemBondsInRadius` with one caller nobody had built,
* **moving the exposure record below the debrief hold's idempotence guard** leaves every asserted
  character in place and silently stops recording a second trip. Machinery, not behaviour, for
  the twelfth time.

And one plant guards everybody else: **adding a member to `EvidenceStatus`** would change eight
comparisons and break saves that store the value.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

REVIEW = "src/RimroomsAsyncIndustries/Company/EvidenceReview.cs"
EXPOSURE = "src/RimroomsAsyncIndustries/Company/StaffExposure.cs"
RECORDS = "src/RimroomsAsyncIndustries/Company/CampaignRecords.cs"
COMPONENT = "src/RimroomsAsyncIndustries/Company/RimroomsCampaignComponent.cs"
DEBRIEF = "src/RimroomsAsyncIndustries/Company/StaffDebrief.cs"
SPINUP = "src/RimroomsAsyncIndustries/Gate/GateSpinUp.cs"
EVIDENCE_UI = "src/RimroomsAsyncIndustries/UI/OperationsEvidence.cs"
EXPEDITIONS_UI = "src/RimroomsAsyncIndustries/UI/OperationsExpeditions.cs"
CREW_UI = "src/RimroomsAsyncIndustries/UI/OperationsCrewPlanner.cs"
KEYED = "Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/RR_Investigation.xml"

PROOF = ".local/register/proof-review-exposure.py"

NL = chr(10)

PLANTS = [
    # ============================================== review: built and unreachable
    ("THE REVIEW BUTTON GOES, SO THE WORKFLOW IS UNUSABLE", EVIDENCE_UI,
     '            { ShowResult(campaign.ReviewAnalysis(record, reviewer)); }',
     "            { }", PROOF),

    ("the readout never calls the review panel at all", EVIDENCE_UI,
     "                else { DrawReview(listing, record); }",
     "                else { }", PROOF),

    ("the objective hint stops naming review, so nobody learns the step exists", EXPEDITIONS_UI,
     '            else if (campaign.AwaitsReview(record))' + NL
     + '            { key = "RR_UI_NextReview"; brief = "RR_UI_NextReviewBrief"; pane = 6; }'
     + NL, "", PROOF),

    ("a refusal loses its string and prints a raw key at the player", KEYED,
     "  <RR_Review_ReviewerIsAnalyst>", "  <RR_Review_ReviewerIsAnalystXX>", PROOF),

    # ============================================== review: soundness
    ("THE ANALYST CAN REVIEW THEIR OWN REPORT AGAIN", REVIEW,
     "            if (record.Analyst != null && reviewer == record.Analyst)" + NL
     + '            { return CompanyActionResult.Refused("RR_Review_ReviewerIsAnalyst"); }' + NL,
     "", PROOF),

    ("a review signs off on a record the company has not settled", REVIEW,
     "            if (UnsettledDisputes(record).Any())" + NL
     + '            { return CompanyActionResult.Refused("RR_Review_DisputesOutstanding"); }' + NL,
     "", PROOF),

    ("every report is endorsed, so the sign-off becomes a rubber stamp", REVIEW,
     "            bool endorsed = !record.AnalysisReport.DetailsUnavailable;",
     "            bool endorsed = true;", PROOF),

    ("a report can be signed off twice, overwriting who signed it", RECORDS,
     "            if (reviewedTick >= 0) { return; }" + NL, "", PROOF),

    # ============================================== the enum everybody depends on
    ("EVIDENCESTATUS GAINS A MEMBER AND EVERY SAVE BREAKS", RECORDS,
     "public enum EvidenceStatus { Located = 0, Recovered = 1, Secured = 2, Analyzed = 3, Missing = 4 }",
     "public enum EvidenceStatus { Located = 0, Recovered = 1, Secured = 2, Analyzed = 3, Missing = 4, Reviewed = 5 }",
     PROOF),

    ("the review fields stop being saved", RECORDS,
     '            Scribe_Values.Look(ref reviewedTick, "rr_reviewedTick", -1);' + NL, "", PROOF),

    # ============================================== exposure: recorded
    ("STAFF EXPOSURE IS NEVER RECORDED", DEBRIEF,
     "                NoteFieldExposure(pawn, coordinateId);" + NL, "", PROOF),

    ("EXPOSURE MOVES BELOW THE IDEMPOTENCE GUARD AND SILENTLY STOPS COUNTING", DEBRIEF,
     "                NoteFieldExposure(pawn, coordinateId);" + NL
     + "                if (HoldFor(pawn) != null) { continue; }",
     "                if (HoldFor(pawn) != null) { continue; }" + NL
     + "                NoteFieldExposure(pawn, coordinateId);", PROOF),

    ("the field history stops being saved", COMPONENT,
     "            ExposeFieldExposure();" + NL, "", PROOF),

    ("the history holds live pawn references instead of load ids", EXPOSURE,
     "        internal string crewLoadId;",
     "        internal string crewLoadId;" + NL + "        internal Pawn held;", PROOF),

    # ============================================== exposure: spent
    ("EXPOSURE IS RECORDED AND NEVER SPENT", SPINUP,
     "            { required *= dialCampaign.ExposureDialFactor(assignedOperator, coordinateId); }",
     "            { }", PROOF),

    ("exposure stops asking about THIS address and becomes raw experience", EXPOSURE,
     "            return HasBeenTo(gateOperator, coordinateId) ? OperatorExposureFactor : 1f;",
     "            return FieldTripsFor(gateOperator) > 0 ? OperatorExposureFactor : 1f;", PROOF),

    ("THE FLOOR STOPS HOLDING, SO A WELL-WORN ROUTE COULD BECOME FREE", SPINUP,
     "            return Mathf.Max(floor, required);",
     "            return required;", PROOF),

    # ============================================== exposure: visible
    ("THE PLAYER IS NEVER TOLD WHO HAS BEEN THROUGH", CREW_UI,
     "                int trips = campaign.FieldTripsFor(candidate.Pawn);",
     "                int trips = 0;", PROOF),

    ("a novice stops being labelled and reads as a blank row", CREW_UI,
     '                if (trips <= 0) { listing.Label("RR_Plan_ExposureNone".Translate()); }' + NL,
     "", PROOF),

    ("the ramping address becomes writable from outside the gate", SPINUP,
     "        public string SpinUpCoordinateId { get { return spinUpCoordinateId; } }",
     "        public string SpinUpCoordinateId { get { return spinUpCoordinateId; }"
     + " set { spinUpCoordinateId = value; } }", PROOF),
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


print("baseline -- the verifier must pass before anything is planted")
for command in sorted(set(plant[4] for plant in PLANTS)):
    code = subprocess.call([sys.executable, command],
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("  exit %d  %s" % (code, command))
    if code != 0:
        sys.stderr.write("BASELINE BROKEN: %s already fails, so every plant against it would "
                         "register as caught and the run would prove nothing.\n" % command)
        sys.exit(2)
print("")

opening = dict((path, io.open(path, encoding="utf-8").read())
               for path in set(plant[1] for plant in PLANTS))

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
for path, text in opening.items():
    if io.open(path, encoding="utf-8").read() != text:
        sys.stderr.write("%s IS NOT AS IT WAS FOUND -- CHECK BY HAND\n" % path)
        sys.exit(3)
if os.path.isfile(_RR_SENTINEL):
    sys.stderr.write("SENTINEL STILL PRESENT AT %s\n" % _RR_SENTINEL)
    sys.exit(3)
print("every touched file verified byte-identical to how it was found; no sentinel left behind")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
