# -*- coding: utf-8 -*-
"""Review, the fourth workflow, and staff prior exposure. Both were named open prep items.

Why this proof exists
---------------------
Owner, 2026-10-01: *"andf yes do those three things you listed as well"*. Two of the three are
features:

* **the `review` workflow** -- *"Add analyze/interview/compare/review workflows"*. Analyse
  shipped first, compare at 0.12.25-dev, interview at 0.12.28-dev, and the row has read
  *"Review remains of the four"* since.
* **staff prior exposure** -- *"field history, trust/stress/exposure and equipment
  familiarity"*, open across two separate rows for most of the project.

Both are exactly the shape that goes wrong here. **Four of five bond defects, and seven before
them, were built, correct and unreachable.** So almost every claim below is about something being
*called*, *saved*, or *visible* -- not about it existing.

And one claim exists to protect every other consumer: **`EvidenceStatus` must not have gained a
member.** `Analyzed` is terminal and eight places compare against it, and the enum is saved by
value, so a sixth member would change all of them and break saves.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
KEYED = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Languages",
                     "English", "Keyed")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(*parts):
    return io.open(os.path.join(*parts), encoding="utf-8-sig").read()


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n")
                     if not line.lstrip().startswith("//"))


review = strip_comments(read(SRC, "Company", "EvidenceReview.cs"))
exposure = strip_comments(read(SRC, "Company", "StaffExposure.cs"))
records = strip_comments(read(SRC, "Company", "CampaignRecords.cs"))
component = strip_comments(read(SRC, "Company", "RimroomsCampaignComponent.cs"))
debrief = strip_comments(read(SRC, "Company", "StaffDebrief.cs"))
spinup = strip_comments(read(SRC, "Gate", "GateSpinUp.cs"))
evidence_ui = strip_comments(read(SRC, "UI", "OperationsEvidence.cs"))
expeditions_ui = strip_comments(read(SRC, "UI", "OperationsExpeditions.cs"))
crew_ui = strip_comments(read(SRC, "UI", "OperationsCrewPlanner.cs"))
investigation_keyed = read(KEYED, "RR_Investigation.xml")
# The objective chain's SHORT lines live beside the pane that draws them; the long
# instructions stayed where they were. Both files have to be read or the claim below can
# only see half of each branch.
expeditions_keyed = read(KEYED, "RR_OperationsExpeditions.xml")
crew_keyed = read(KEYED, "RR_CrewPlanner.xml")

print("")

# =============================================================== REVIEW IS REACHABLE
check("THE REVIEW WORKFLOW HAS A BUTTON, AND THE BUTTON CALLS THE SERVICE",
      "public CompanyActionResult ReviewAnalysis(EvidenceRecord record, Pawn reviewer)" in review
      and "ShowResult(campaign.ReviewAnalysis(record, reviewer))" in evidence_ui
      and "private static void DrawReview(" in evidence_ui
      and "else { DrawReview(listing, record); }" in evidence_ui,
      "-- **DEFINED AND CALLED, from a control the player can press.** `RedeemBondsInRadius` "
      "worked and had one caller nobody had built. A service with no reachable caller is the "
      "defect that accounts for four of five bond defects")

check("and the objective hint names review as the next step",
      # **TWO KEYS PER BRANCH NOW, and the claim asserts both.** The objective line draws
      # a three-word `brief` and carries the full instruction on its hover, so this checks
      # the branch sets BOTH -- a branch that set only the long key would show a blank
      # objective, and one that set only the brief would lose the instruction entirely.
      'else if (campaign.AwaitsReview(record))' in expeditions_ui
      and '{ key = "RR_UI_NextReview"; brief = "RR_UI_NextReviewBrief"; pane = 6; }'
      in expeditions_ui
      and "public bool AwaitsReview(EvidenceRecord record)" in review
      and "<RR_UI_NextReview>" in investigation_keyed
      and "<RR_UI_NextReviewBrief>" in expeditions_keyed,
      "-- a workflow the player is never told about is one nobody runs")

check("and the sign-off is shown on the record afterwards",
      "RR_UI_ReviewEndorsed" in evidence_ui and "RR_UI_ReviewReturned" in evidence_ui
      and "<RR_UI_ReviewEndorsed>" in investigation_keyed
      and "<RR_UI_ReviewReturned>" in investigation_keyed,
      "-- *\"a dispute the company records but never shows anybody is a dispute that may as well "
      "have been discarded\"*, which is what became of every second crew account until "
      "0.12.25-dev")

# The key list is computed OUT OF THE SERVICE, never typed here: a hand-kept list of refusal
# keys is a second derivation that goes stale the first time a refusal is added.
service_keys = sorted(set(re.findall(r'"(RR_Review_[A-Za-z]+)"', review)))
missing_keys = [key for key in service_keys
                if ("<%s>" % key) not in investigation_keyed]
check("AND EVERY ONE OF THE %d REFUSALS IT CAN RETURN HAS A STRING" % len(service_keys),
      len(service_keys) >= 9 and not missing_keys,
      "-- missing: %s. A refusal with no string prints a raw key at the player, and a control "
      "that refuses in silence is how somebody concludes a button is broken"
      % ", ".join(missing_keys))

# =============================================================== REVIEW IS SOUND
check("THE ANALYST CANNOT REVIEW THEIR OWN REPORT",
      "if (record.Analyst != null && reviewer == record.Analyst)" in review
      and 'CompanyActionResult.Refused("RR_Review_ReviewerIsAnalyst")' in review
      and "if (analyst != null && pawn == analyst) { continue; }" in exposure + review,
      "-- a second pair of eyes belonging to the same head is not a second pair of eyes. **That "
      "is the entire mechanism**, refused in the service AND excluded from the candidate search")

check("and a review cannot sign off on an unsettled dispute",
      "if (UnsettledDisputes(record).Any())" in review
      and 'CompanyActionResult.Refused("RR_Review_DisputesOutstanding")' in review,
      "-- two of the branch's own people contradicting each other on the record. The interview "
      "clears it, which is **how the four workflows chain** rather than sit side by side")

check("and returning a report is a real outcome, not a failure",
      "bool endorsed = !record.AnalysisReport.DetailsUnavailable;" in review
      and "record.MarkReviewed(reviewer, Find.TickManager.TicksGame, endorsed);" in review
      and '"RR_Event_ReviewReturned"' in review,
      "-- a report whose observation detail never existed is one the company cannot stand "
      "behind, and saying so is worth more to the player than a rubber stamp")

check("and a report cannot be signed off twice",
      "if (record.Reviewed)" in review
      and "if (reviewedTick >= 0) { return; }" in records,
      "-- guarded in the service and again in the record, so a second caller cannot overwrite "
      "who signed it")

# =============================================================== THE ENUM IS UNTOUCHED
check("EVIDENCESTATUS DID NOT GAIN A MEMBER, WHICH WOULD HAVE BROKEN EVERY SAVE",
      "public enum EvidenceStatus { Located = 0, Recovered = 1, Secured = 2, Analyzed = 3, "
      "Missing = 4 }" in records,
      "-- `Analyzed` is terminal and eight places compare against it; the enum is saved by "
      "value. **Review is recorded BESIDE the status, never instead of it** -- the same additive "
      "discipline `observationSchemaVersion` uses in the same record for the same reason")

check("and the review fields are saved",
      'Scribe_References.Look(ref reviewer, "rr_reviewer");' in records
      and 'Scribe_Values.Look(ref reviewedTick, "rr_reviewedTick", -1);' in records
      and 'Scribe_Values.Look(ref reviewEndorsed, "rr_reviewEndorsed");' in records,
      "-- and an older record loads with reviewedTick -1, which reads as *not reviewed* and is "
      "exactly true")

# =============================================================== EXPOSURE IS RECORDED
check("STAFF PRIOR EXPOSURE IS RECORDED WHERE THE FACT IS ALREADY KNOWN",
      "internal void NoteFieldExposure(Pawn pawn, string coordinateId)" in exposure
      and "NoteFieldExposure(pawn, coordinateId);" in debrief,
      "-- **DEFINED AND CALLED** from `NoteReturnedFromField`, the one place in the mod where "
      "*this person came back from there* is established. A second caller would be a second "
      "definition of *came back*")

check("and it is recorded BEFORE the debrief hold's idempotence guard",
      debrief.index("NoteFieldExposure(pawn, coordinateId);")
      < debrief.index("if (HoldFor(pawn) != null) { continue; }"),
      "-- the hold is a transient obligation and the history is permanent. Below the guard, a "
      "second completion would skip the history along with the hold")

check("and the history survives the save",
      "ExposeFieldExposure();" in component
      and 'Scribe_Collections.Look(ref fieldExposure, "rr_fieldExposure", LookMode.Deep);'
      in exposure,
      "-- the defect this replaces is a fact that existed for a few hours of game time and was "
      "then thrown away. An unsaved history is the same bug with extra steps")

check("and it holds load ids, never live pawn references",
      "internal string crewLoadId;" in exposure
      and "Scribe_References" not in exposure
      and "Pawn pawn" in exposure and "internal Pawn" not in exposure,
      "-- a colonist who leaves, dies or is captured must not be held alive by the branch's "
      "paperwork. Same reasoning as the lost-pawn register")

# =============================================================== EXPOSURE IS SPENT
check("EXPOSURE CHANGES WHAT A DIAL COSTS, WHICH IS THE POINT OF IT",
      "public float ExposureDialFactor(Pawn gateOperator, string coordinateId)" in exposure
      and "required *= dialCampaign.ExposureDialFactor(assignedOperator, coordinateId);" in spinup,
      "-- **DEFINED AND CALLED** inside `SpinUpWorkRequiredFor`, the single place that decides "
      "what bringing a gate up costs. *\"staff prior exposure affecting how an expedition "
      "goes\"*")

check("and it asks whether they walked THIS address, not how experienced they are",
      "public bool HasBeenTo(Pawn pawn, string coordinateId)" in exposure
      and "record.coordinateIds.Contains(coordinateId)" in exposure
      and "HasBeenTo(gateOperator, coordinateId) ? OperatorExposureFactor : 1f" in exposure,
      "-- a veteran of ten other routes has not walked this one, and the discount is for "
      "knowing the way")

check("and it applies ONCE, where the branch's own familiarity compounds",
      "public const float OperatorExposureFactor = 0.9f;" in exposure
      and spinup.count("ExposureDialFactor") == 1
      and "for (int step = 0; step < prior; step++)" in spinup,
      "-- the loop is the BRANCH's record, one discount per previous connection. A person has "
      "either walked it or not, and the tenth walk does not teach them the way a tenth filed "
      "report teaches the branch")

check("AND THE FLOOR STILL HOLDS, SO A WELL-WORN ROUTE IS NEVER FREE",
      "return Mathf.Max(floor, required);" in spinup
      and spinup.index("required *= dialCampaign.ExposureDialFactor")
      < spinup.index("return Mathf.Max(floor, required);"),
      "-- the discount is applied before the clamp, in that order, and this claim is the order. "
      "A spin-up of zero is a gate that opens itself")

# =============================================================== EXPOSURE IS VISIBLE
check("THE PLAYER IS TOLD WHO HAS BEEN THROUGH, AND WHO KNOWS THE ROUTE",
      "campaign.FieldTripsFor(candidate.Pawn)" in crew_ui
      and "campaign.HasBeenTo(candidate.Pawn, address)" in crew_ui
      and "gate.SpinUpCoordinateId" in crew_ui
      and all(("<%s>" % key) in crew_keyed for key in
              ("RR_Plan_ExposureNone", "RR_Plan_ExposureTrips", "RR_Plan_ExposureKnowsRoute")),
      "-- **a modifier the player cannot see is the same defect as one that never runs.** Three "
      "lines: a novice, a veteran who has not walked this route, and one who has")

check("and a novice is labelled rather than left blank",
      'if (trips <= 0) { listing.Label("RR_Plan_ExposureNone".Translate()); }' in crew_ui,
      "-- this panel already lists unready candidates instead of hiding them, because *a staff "
      "member who has vanished from the list is indistinguishable from one who was never hired*")

check("and the ramping address is read-only outside the gate",
      "public string SpinUpCoordinateId { get { return spinUpCoordinateId; } }" in spinup
      and "set { spinUpCoordinateId" not in spinup,
      "-- the panel needs to know what is being dialled; nothing outside the gate may change it")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: review is the fourth workflow and it is reachable; prior exposure is "
      "recorded, saved, spent on the dial, and visible")
