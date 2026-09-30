# -*- coding: utf-8 -*-
"""Assert an interview settles which account is filed, keeps both, and can refuse at every clause.

The property this exists for
---------------------------
`TODO.md`: *"Add analyze/interview/compare/review workflows"* -- where analysis shipped, **compare**
shipped at 0.12.25-dev, and **interview** did not. Two crew could disagree and nothing resolved it.

**NOBODY IS LYING, AND THAT IS THE DESIGN.** `RecordFieldObservation` validates a fact through
`HasDisplacedMarker` **before** it looks for a prior observation, so a disputing account was already
checked against the map and found true. Two honest accounts conflict because **the marker moved
between the two observations** -- silent between-visit displacement has shipped since 0.10.3-dev.

So an interview cannot be a lie detector, and must not pretend to be one. The register is explicit:

    "Keep the company's evaluation based on actual pawn traits, skills, and relationships."
    "Keep custody, casework, and interview goals reachable through vanilla prisoner controls."

Four things have to stay true:

  * **NO INVENTED STAT.** RimWorld has no reliability or honesty statistic and this must not grow
    one. The only skill consulted is `SkillDefOf.Social` on a real pawn.

  * **NO PRISONER MECHANIC.** These are employed staff giving statements to a colleague. Nothing
    detains anybody and nothing here is reachable through a prisoner interaction.

  * **BOTH ACCOUNTS SURVIVE.** Settling records which account the company files. It does not rewrite
    the fact and does not delete the other account. An evidence chain that erased the testimony it
    did not file would be worth less than one that keeps both and says which.

  * **EVERY CLAUSE CAN REFUSE**, invariant 136. An analysed record especially: its report is frozen,
    and reopening a filed conclusion would let the snapshot disagree with the record it came from.

Run from the repository root.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def strip_cs_comments(text):
    """The reasoning names the very things the claims search for -- prisoner, reliability, Social.
    Prose must never satisfy a claim."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.split("\n"))


def body_of(text, signature):
    start = text.index(signature)
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise AssertionError("unbalanced body for %r" % signature)


interview = strip_cs_comments(read(os.path.join(SRC, "Company", "EvidenceInterview.cs")))
observations = strip_cs_comments(read(os.path.join(SRC, "Company", "EvidenceObservations.cs")))
pane = strip_cs_comments(read(os.path.join(SRC, "UI", "OperationsEvidence.cs")))
keys = read(os.path.join(MOD, "Languages", "English", "Keyed", "RR_Investigation.xml"))
portal_keys = read(os.path.join(MOD, "Languages", "English", "Keyed", "RR_Portals.xml"))

settle = body_of(interview, "public CompanyActionResult SettleDisputedAccount(")
picker = body_of(interview, "public Pawn InterviewerFor(")

print("")
print("proof: an interview files one account, keeps both, and refuses at every clause")
print("")

# ------------------------------------------------------------------ 1. no invented stat
print("1. no invented stat, and no prisoner mechanic")
check("the only skill consulted is Social",
      "SkillDefOf.Social" in interview and
      not re.search(r"SkillDefOf\.(?!Social)[A-Za-z]+", interview),
      "-- the register asks for evaluation based on actual pawn skills, and Social is the real one")
check("no reliability, honesty or credibility statistic is invented",
      not re.search(r"(?i)\b(reliabilit|credibilit|honest|truthful|accurac)", interview),
      "-- RimWorld has no such stat and this must not grow one")
check("the skill floor is a named constant, not a literal in a condition",
      "MinimumInterviewerSocial" in interview and
      "public const int MinimumInterviewerSocial" in interview)
check("no prisoner, warden or detention concept appears",
      not re.search(r"(?i)(prisoner|warden|detain|guest|IsSlave)", interview),
      "-- the register: keep interview goals reachable through vanilla prisoner controls, which "
      "means not reimplementing them here")
check("the interviewer must be the player's own employed staff",
      "IsEmployedPawn(interviewer)" in settle and "Faction.OfPlayer" in interview)

# ------------------------------------------------------------------ 2. both accounts survive
print("")
print("2. both accounts survive the settlement")
settle_method = body_of(observations, "internal void Settle(")
check("settling records which account was filed",
      "filedWitnessLoadId = filedLoadId" in settle_method)
check("settling does NOT touch the observation's own facts",
      not re.search(r"\b(roomIndex|referencedRoomIndex|markerNumber|witnessRoomIndex)\s*=", settle_method),
      "-- rewriting the fact would make the filed account the only one that ever existed")
check("settling does NOT remove any account",
      "accounts" not in settle_method,
      "-- the account the company did not file stays on the record with its witness named")
check("a settled fact is still recognisably disputed",
      "public bool Disputed" in observations and
      "public bool Settled { get { return interviewTick >= 0; } }" in observations,
      "-- two separate questions: whether anyone disagreed, and whether the company chose")

# ------------------------------------------------------------------ 3. every clause can refuse
print("")
print("3. every clause can refuse")
for key in ("RR_Interview_Inactive", "RR_Interview_RecordUnavailable", "RR_Interview_RecordClosed",
            "RR_Interview_NotDisputed", "RR_Interview_NoSuchAccount",
            "RR_Interview_WitnessUnavailable", "RR_Interview_InterviewerUnavailable",
            "RR_Interview_InterviewerIsWitness", "RR_Interview_InterviewerUnskilled"):
    check("%s is a refusal in the method" % key, '"%s"' % key in settle)
    check("%s is translated" % key, "<%s>" % key in keys)

check("an analysed record refuses rather than reopening",
      "record.analyzedTick >= 0" in settle and "RR_Interview_RecordClosed" in settle,
      "-- the frozen report would otherwise disagree with the record it was taken from")
check("settling twice is Existing, not a second settlement",
      "observation.Settled" in settle and "CompanyActionResult.Existing()" in settle)
check("the filed account must be one actually on this observation",
      "WitnessLoadIds.Contains(filedWitnessLoadId" in settle)
check("the interviewer may not be one of the witnesses",
      "RR_Interview_InterviewerIsWitness" in settle and
      "WitnessLoadIds.Contains(interviewerId" in settle)

# ------------------------------------------------------------------ 4. the picker is deterministic
print("")
print("4. who the company would send is deterministic")
check("the picker excludes everyone who gave an account",
      "speakers.Contains(loadId)" in picker)
check("ties break on load id rather than staff order",
      "string.Compare(loadId, bestId, StringComparison.Ordinal)" in picker,
      "-- invariant 26: sort before choosing, or the named interviewer changes between frames")
check("the picker and the action read ONE floor, not two constants",
      "InterviewerSocialFloor" in picker and "InterviewerSocialFloor" in settle,
      "-- a button naming somebody the action would then refuse is worse than no button, and "
      "0.12.29-dev made the floor research-driven, so two copies of it would drift apart")
check("the floor lowers with research but never to zero",
      "PractisedInterviewerSocial = 2" in interview and
      "RR_Cap_StatementDiscipline" in body_of(interview, "public int InterviewerSocialFloor"),
      "-- a project may cheapen a thing without abolishing it, as shelter never reaches zero")

# ------------------------------------------------------------------ 5. the saved shape holds
print("")
print("5. the settlement is saved, and cannot be half-written")
check("the settlement fields are saved",
      'Scribe_Values.Look(ref interviewTick, "rr_interviewTick", -1)' in observations and
      'Scribe_Values.Look(ref filedWitnessLoadId, "rr_filedWitnessLoadId")' in observations)
validity = body_of(observations, "internal bool IsValidFor(string evidenceId")
check("a settlement without a disagreement is invalid",
      "if (interviewTick >= 0)" in validity and "!Disputed" in validity)
check("settlement details without a tick are invalid too",
      "else if (!string.IsNullOrEmpty(filedWitnessLoadId)" in validity,
      "-- the same defect from the other side, and the side a partial save would produce")
check("the interviewer may not be the filed witness in a saved record",
      "string.Equals(interviewerLoadId, filedWitnessLoadId" in validity)
check("the analysis snapshot compares the settlement",
      "filedWitnessLoadId == other.filedWitnessLoadId" in
      body_of(observations, "internal bool SameSnapshot(EvidenceObservationRecord other)"),
      "-- a frozen report would otherwise agree with a record that has since been settled")
check("the snapshot copies the settlement",
      "filedWitnessLoadId = filedWitnessLoadId" in
      body_of(observations, "internal EvidenceObservationRecord SnapshotCopy()"))

# ------------------------------------------------------------------ 6. the player is told
print("")
print("6. the player can see it and act on it")
draw = body_of(pane, "private static void DrawInterview(")
check("the pane only offers an interview for a real disagreement",
      "!observation.Disputed" in draw)
check("a settled fact reads as settled, naming who filed and who interviewed",
      "RR_UI_AccountFiled" in draw and "<RR_UI_AccountFiled>" in keys)
check("the button names the interviewer before the player commits",
      "RR_UI_InterviewPrompt" in draw and "interviewer.LabelShortCap" in draw)
check("no available interviewer is stated, not hidden",
      "RR_Interview_NoInterviewer" in draw and "<RR_Interview_NoInterviewer>" in keys,
      "-- a missing button is not information")
check("the refusal reaches the player through the usual result path",
      "ShowResult(campaign.SettleDisputedAccount(" in draw)
check("filing is recorded as a campaign event",
      '"RR_Event_AccountFiled"' in interview and "<RR_Event_AccountFiled>" in portal_keys)

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: an interview files one account, keeps both, and can refuse at every clause")
