# -*- coding: utf-8 -*-
"""Planted faults against `proof-tenure-and-disposition.py`.

## The ones that matter most

**A lease growing a term.** `CAMPAIGN_CHART.md` 1.1 is the single most
load-bearing rule in this package, and a term on a place is the most natural
thing in the world to add -- every leasing system anybody has ever played has
one. It would read as a feature rather than a violation, which is exactly why it
needs a plant rather than a comment.

**Eviction firing on time rather than on arrears.** One line moves it from *a
consequence of something the player controls* to *a countdown*, and nothing about
the code would look wrong.

**Escaping a containment charge for money.** Containment is the one reversible
disposition. If the way out paid anything at all, contain-then-cash would be
strictly better than selling, and the whole cost structure collapses.

**A certification going hollow.** Three ship and each has exactly one consumer.
Break the consumer and the card still appears, still says what it does, and does
nothing -- the lie-on-the-card defect the project tree already refuses.

Run from the repository root.
"""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
CERT_DEF = SRC + "/Personnel/RimroomsCertificationDef.cs"
CERTS = SRC + "/Company/StaffCertifications.cs"
SPINUP = SRC + "/Gate/GateSpinUp.cs"
REVIEW = SRC + "/Company/EvidenceReview.cs"
SERVICING = SRC + "/Gate/NativeGateServicing.cs"
JOBDRIVER = SRC + "/Gate/JobDriver_RimroomsGate.cs"
PLANNER = SRC + "/UI/OperationsCrewPlanner.cs"
RECORDS = SRC + "/Company/CampaignRecords.cs"
DISPOSITION = SRC + "/Company/EvidenceDispositionService.cs"
CONFIDENCE = SRC + "/Company/EvidenceConfidence.cs"
SURVIVOR = SRC + "/Threats/CompRimroomsSurvivor.cs"
VARIATION = SRC + "/Company/RequestVariation.cs"
GENERATION = SRC + "/Company/RequestGeneration.cs"
TENURE = SRC + "/Company/RemoteSiteTenure.cs"
SITES = SRC + "/Company/RemoteSites.cs"
SERVICES = SRC + "/Company/CampaignServices.cs"
CERT_DEFS = ("Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsCertificationDefs/"
             "RR_Certifications.xml")
RECIPES = "Mod/Rimrooms - Async Industries/1.6/Defs/RecipeDefs/RR_TrainingRecipes.xml"
PROOF = ".local/register/proof-tenure-and-disposition.py"
NL = chr(10)

PLANTS = [
    # ================================================= certifications and training jobs
    ("A CERTIFICATION LOSES ITS TRAINING JOB", CERT_DEFS,
     "    <recipeDefName>RR_TrainFieldAnalyst</recipeDefName>" + NL, "", PROOF),

    ("a certification names a training job that does not exist", CERT_DEFS,
     "<recipeDefName>RR_TrainGateOperator</recipeDefName>",
     "<recipeDefName>RR_TrainGateOperatorXX</recipeDefName>", PROOF),

    ("the load-time rule demanding a training job is removed", CERT_DEF,
     '                    " names no training recipe, so nobody could ever earn it.";',
     '                    " ";', PROOF),

    ("THE TRAINING BECOMES A BUTTON instead of work", RECIPES,
     "    <workerClass>RimroomsAsyncIndustries.Personnel."
     "RecipeWorker_RimroomsCertification</workerClass>" + NL,
     "", PROOF),

    ("the training stops recording against whoever did the work", CERTS,
     "        public override void Notify_IterationCompleted(Pawn billDoer",
     "        private void UnusedIteration(Pawn billDoer", PROOF),

    # **CORE HAS TO ENFORCE THE FLOOR.** A floor checked after the work wastes the pawn's day.
    ("A SKILL FLOOR MOVES OUT OF CORE and into a post-hoc check", RECIPES,
     "    <skillRequirements>" + NL + "      <Intellectual>4</Intellectual>" + NL
     + "    </skillRequirements>" + NL, "", PROOF),

    ("the training moves to a bench that cannot take bills", RECIPES,
     "      <li>TableMachining</li>" + NL + "      <li>CraftingSpot</li>",
     "      <li>SimpleResearchBench</li>", PROOF),

    ("A CERTIFICATION IS HELD BY A LIVE PAWN REFERENCE", CERTS,
     "        internal string crewLoadId;", "        internal Pawn pawn;", PROOF),

    ("training somebody twice records it twice", CERTS,
     "            if (HasCertification(pawn, certification.defName))" + NL
     + "            { return CompanyActionResult.Existing(); }" + NL, "", PROOF),

    ("and it announces every repeat", CERTS,
     "            if (!result.Success || result.AlreadyApplied) { return; }",
     "            if (!result.Success) { return; }", PROOF),

    # **THE HOLLOW CARD, three times.**
    ("THE OPERATOR CERTIFICATION STOPS TAKING WORK OFF THE DIAL", SPINUP,
     "            { required *= dialCampaign.CertificationDialFactor(assignedOperator); }",
     "            { }", PROOF),

    ("THE TECHNICIAN CERTIFICATION STOPS SAVING ANY WORK", JOBDRIVER,
     "                if (workDone >= gate.ReconditionWorkFor(pawn))",
     "                if (workDone >= gate.ReconditionWorkRequired)", PROOF),

    ("the crew planner stops showing what anybody was trained to do", PLANNER,
     "                    campaign.CertificationsOf(candidate.Pawn);",
     "                    new List<Personnel.RimroomsCertificationDef>();", PROOF),

    # **THE REFUSAL MISMATCH.** Widening the picker alone offers somebody the action refuses.
    ("THE REVIEW ACTION STOPS HONOURING THE CERTIFICATION the picker admits on", REVIEW,
     "                    && !HasCertification(reviewer, \"RR_Cert_FieldAnalyst\")))",
     "                    ))", PROOF),

    ("the certification NARROWS who may review instead of widening", REVIEW,
     "                if (skill < MinimumReviewerIntellectual" + NL
     + "                    && !HasCertification(pawn, \"RR_Cert_FieldAnalyst\")) { continue; }",
     "                if (!HasCertification(pawn, \"RR_Cert_FieldAnalyst\")) { continue; }", PROOF),

    ("being certified starts changing the pawn", CERTS,
     "            RecordEvent(\"RR_Event_Certified\", pawn.LabelShortCap, certification.LabelCap);",
     "            pawn.skills.Learn(RimWorld.SkillDefOf.Intellectual, 5000f);", PROOF),

    # ================================================= the four dispositions
    ("THE DISPOSITION BECOMES MORE EvidenceStatus MEMBERS", RECORDS,
     "    public enum EvidenceDisposition", "    public enum UnusedDisposition", PROOF),

    ("A DISPOSITION DISAPPEARS", DISPOSITION,
     "        public CompanyActionResult DestroyRecord(EvidenceRecord record)",
     "        private CompanyActionResult UnusedDestroy(EvidenceRecord record)", PROOF),

    ("detain disappears from the person side", SURVIVOR,
     "        private void Detain(Pawn pawn)", "        private void UnusedDetain(Pawn pawn)",
     PROOF),

    ("CONTAINMENT BECOMES FREE", DISPOSITION,
     "        public long DailyContainmentUsd", "        private long UnusedContainmentUsd",
     PROOF),

    ("the containment bill stops reaching the operating day", SERVICES,
     "                AddContainmentObligation(dayId, nextOperatingCostTick);" + NL, "", PROOF),

    ("TRANSFER STARTS PAYING WHAT THE EXCHANGE WOULD", DISPOSITION,
     "        public const float TransferRate = 0.6f;",
     "        public const float TransferRate = 1f;", PROOF),

    ("a released record leaves the thing standing on the shelf", DISPOSITION,
     "            DisposeOfItem(record);" + NL
     + "            record.MarkDisposition(EvidenceDisposition.Released,"
     + " Find.TickManager.TicksGame);",
     "            record.MarkDisposition(EvidenceDisposition.Released,"
     + " Find.TickManager.TicksGame);", PROOF),

    ("A TRANSFER HANDS THE THING OVER EVEN WHEN THE MONEY FAILED", DISPOSITION,
     "                if (!posted.Success) { return posted; }" + NL, "", PROOF),

    # **THE EXPLOIT.** Contain-then-cash must never beat selling.
    ("ESCAPING A CONTAINMENT CHARGE STARTS PAYING OUT", DISPOSITION,
     "            if (record.Disposition != EvidenceDisposition.Contained)" + NL
     + "            { return CompanyActionResult.Refused(\"RR_Disposition_NotContained\"); }" + NL
     + "            DisposeOfItem(record);",
     "            if (record.Disposition != EvidenceDisposition.Contained)" + NL
     + "            { return CompanyActionResult.Refused(\"RR_Disposition_NotContained\"); }" + NL
     + "            PostTransaction(\"rr_bail:\" + record.Id, 500L,"
     + " \"RR_Ledger_RecordTransfer\", record.Id);" + NL
     + "            DisposeOfItem(record);", PROOF),

    ("detaining stops using Core's prisoner system", SURVIVOR,
     "                pawn.guest.SetGuestStatus(Faction.OfPlayer, GuestStatus.Prisoner);",
     "                pawn.guest.SetGuestStatus(null);", PROOF),

    ("detaining with nowhere to hold anybody stops being refused", SURVIVOR,
     "            else if (!AnyPrisonerBed(pawn))" + NL
     + "            { detain.Disable(\"RR_Survivor_NoPrisonerBed\".Translate()); }" + NL, "",
     PROOF),

    # ================================================= confidence
    ("CONFIDENCE STARTS BEING STORED, so it can disagree with its own inputs", CONFIDENCE,
     "        public EvidenceConfidence ConfidenceOf(EvidenceRecord record)",
     "        public void Scribe() { }" + NL
     + "        public EvidenceConfidence ConfidenceOf(EvidenceRecord record)", PROOF),

    ("an unsettled dispute stops capping confidence", CONFIDENCE,
     "            if (UnsettledDisputes(record).Any()) { return EvidenceConfidence.Weak; }" + NL,
     "", PROOF),

    ("CONFIDENCE STOPS MOVING THE PRICE and becomes a readout", DISPOSITION,
     "                * ConfidenceValueFactor(record);", ";", PROOF),

    ("an unverified record starts being paid LESS", CONFIDENCE,
     "                default: return 1f;", "                default: return 0.5f;", PROOF),

    # ================================================= story variation
    ("AN INPUT THE GENERATOR COULD NOT SEE GOES BACK TO BEING UNREAD", VARIATION,
     "        public int HostileFactionCount", "        private int UnusedHostileCount", PROOF),

    ("the weighting stops reaching the generator", GENERATION,
     "            RimroomsRequestDef chosen = DrawWeightedFamily(freshest, roll);",
     "            RimroomsRequestDef chosen = freshest[roll % freshest.Count];", PROOF),

    ("THE BIAS BECOMES A FILTER by losing its lower bound", VARIATION,
     "            return Mathf.Clamp(factor, 1f / MaximumPull, MaximumPull);",
     "            return Mathf.Clamp(factor, 0f, MaximumPull);", PROOF),

    ("LEAST-ASKED-FIRST IS LOST, so the company repeats its cheapest request", GENERATION,
     "                int asked = TimesAsked(eligible[index].defName);",
     "                int asked = 0;", PROOF),

    ("the draw goes back to Rand", VARIATION,
     "            float pick = (Math.Abs(roll) % 100000) / 100000f * total;",
     "            float pick = Verse.Rand.Value * total;", PROOF),

    # ================================================= tenure: the 1.1 claims
    # **THE MOST LOAD-BEARING RULE IN THE PACKAGE.**
    ("A LEASE GROWS A TERM", TENURE,
     "        internal const int ArrearsBeforeEviction = 3;",
     "        internal const int ArrearsBeforeEviction = 3;" + NL
     + "        private const int LeaseTermTicks = 3600000;", PROOF),

    ("a place grows an expiry", SITES,
     "            string id = branchId + \":site:\" + parent.ID;",
     "            int expiryTick = Find.TickManager.TicksGame + 3600000;" + NL
     + "            string id = branchId + \":site:\" + parent.ID;", PROOF),

    ("EVICTION FIRES ON TIME PASSING instead of on arrears", TENURE,
     "            get { return SiteArrearsCount >= ArrearsBeforeEviction"
     + " && LiveRemoteSiteCount > 0; }",
     "            get { return Find.TickManager.TicksGame % 3600000 == 0"
     + " && LiveRemoteSiteCount > 0; }", PROOF),

    ("eviction starts running whether the branch paid or not", SERVICES,
     "                EvictOnePlace();" + NL + "            }",
     "            }" + NL + "            EvictOnePlace();", PROOF),

    ("EVERY PLACE GOES AT ONCE, with no step in between", TENURE,
     "            remoteSites.Remove(newest);",
     "            remoteSites.RemoveAll(record => record != null && record.Live);", PROOF),

    ("the branch loses the place it has run longest instead of the newest", TENURE,
     "                if (newest == null || record.registeredTick > newest.registeredTick)",
     "                if (newest == null || record.registeredTick < newest.registeredTick)",
     PROOF),

    ("an eviction is recorded as an ordinary release", TENURE,
     '            RecordEvent("RR_Event_RemoteSiteEvicted", id, label ?? "");',
     '            RecordEvent("RR_Event_RemoteSiteReleased", id);', PROOF),

    ("RENEWAL GROWS A FEE", TENURE,
     "        public string RenewalFailureKey()",
     "        private const long RenewalFeeUsd = 500L;" + NL
     + "        public string RenewalFailureKey()", PROOF),

    ("renewal stops being checked at registration", SITES,
     "            string arrears = RenewalFailureKey();" + NL
     + "            if (arrears != null) { return CompanyActionResult.Refused(arrears); }" + NL,
     "", PROOF),

    ("and renewal is refused for a reason other than what is owed", TENURE,
     '            return SiteArrearsCount > 0 ? "RR_Site_ArrearsOutstanding" : null;',
     '            return LiveRemoteSiteCount > 0 ? "RR_Site_ArrearsOutstanding" : null;', PROOF),
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
