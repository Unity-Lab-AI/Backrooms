# -*- coding: utf-8 -*-
"""Training is work, a decision has a cost, and the only clock is still the gate.

## What this batch was for

Five owner rows, and the thread running through all of them is **a choice that
costs something**:

  * *"certifications, training jobs, field history, trust/stress/exposure and
    equipment familiarity; preserve pawn autonomy and vanilla skill/trait
    systems"* -- certifications and training jobs were the remainder.
  * *"Make sale/study/use/contain/release/recruit/detain/transfer choices visible
    with financial, staff, faction, legal-in-world, trust, and security
    consequences"* -- contain, release, transfer and detain did not exist.
  * *"evidence provenance/custody/type/value/risk/confidence ... and destruction
    choice"* -- confidence scoring and destruction.
  * *"Generate bounded story variations from client/faction ... company tier,
    previous outcomes, opening duration ..."* -- four inputs the generator could
    not see.
  * *"space leasing/claiming with cost, boundaries, term ... renewal, eviction"*.

## The claim that matters most, and it is a refusal

**THERE IS NO LEASE TERM AND THERE MUST NOT BE ONE.** `CAMPAIGN_CHART.md` 1.1:
*"A gate's connection has a duration. Nothing else in this mod has a duration."*
A term is a countdown on a thing the player is asked to maintain, so the row
asking for one is answered by **saying so** rather than by building a smaller
version of it -- the same way the chart records four prep documents' timed
investigations as superseded.

Eviction is allowed because it is built to 1.1's own test: it is the consequence
of something the player controls, it is visible on the ledger, and **no time
passing ever evicts anybody.**

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
    """Source with comments stripped.

    **An absence claim reads the documentation too**, and good documentation explains the thing
    it is avoiding BY NAMING IT. That cost two claims a run in the previous batch, in both
    directions. Every absence assertion here goes through this.
    """
    return re.sub(r"//.*", "", re.sub(r"/\*.*?\*/", "", text, flags=re.S))


def xml_only(text):
    """XML with comments stripped. **The same trap, in the other language.**

    `RR_TrainingRecipes.xml` explains in a comment that Core's research benches are
    `Building_ResearchBench` and therefore cannot take a bill -- which is exactly the reasoning
    the claim below wanted to assert, and asserting *"ResearchBench does not appear"* read the
    explanation and failed. **Third instance this session of a claim reading its own
    documentation**, so the stripper now exists for both languages.
    """
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


print("proof-tenure-and-disposition")
print("-" * 78)

cert_def = read(SRC, "Personnel", "RimroomsCertificationDef.cs")
certs = read(SRC, "Company", "StaffCertifications.cs")
spinup = read(SRC, "Gate", "GateSpinUp.cs")
review = read(SRC, "Company", "EvidenceReview.cs")
servicing = read(SRC, "Gate", "NativeGateServicing.cs")
jobdriver = read(SRC, "Gate", "JobDriver_RimroomsGate.cs")
planner = read(SRC, "UI", "OperationsCrewPlanner.cs")
cert_defs = read(MOD, "Defs", "RimroomsCertificationDefs", "RR_Certifications.xml")
recipes = read(MOD, "Defs", "RecipeDefs", "RR_TrainingRecipes.xml")
records = read(SRC, "Company", "CampaignRecords.cs")
disposition = read(SRC, "Company", "EvidenceDispositionService.cs")
confidence = read(SRC, "Company", "EvidenceConfidence.cs")
survivor = read(SRC, "Threats", "CompRimroomsSurvivor.cs")
variation = read(SRC, "Company", "RequestVariation.cs")
generation = read(SRC, "Company", "RequestGeneration.cs")
tenure = read(SRC, "Company", "RemoteSiteTenure.cs")
sites = read(SRC, "Company", "RemoteSites.cs")
services = read(SRC, "Company", "CampaignServices.cs")

# ================================================= certifications and training jobs
cert_names = re.findall(r"<defName>(RR_Cert_[A-Za-z]+)</defName>", cert_defs)
cert_recipes = re.findall(r"<recipeDefName>(RR_Train[A-Za-z]+)</recipeDefName>", cert_defs)
recipe_names = re.findall(r"<defName>(RR_Train[A-Za-z]+)</defName>", recipes)

check("EVERY CERTIFICATION NAMES A TRAINING JOB THAT EXISTS",
      len(cert_names) > 0 and len(cert_recipes) == len(cert_names)
      and all(name in recipe_names for name in cert_recipes),
      "-- a certification with no bill behind it could never be earned, and would sit in every "
      "readout as something a person might hold. Certs %s, recipes %s"
      % (cert_names, recipe_names))

check("and a certification with no recipe is refused at load",
      "names no training recipe, so nobody could ever earn it." in cert_def,
      "-- enforced rather than trusted, the same way the inhabitant tells are")

# **THE TRAINING IS REAL WORK, which is the owner's word: *jobs*.**
# **COUNTED, NOT MERELY PRESENT.** The first version asserted the worker class appeared `in`
# the file; there are three recipes, so a plant that stripped it from one left two behind and
# satisfied the claim. Third instance of that mistake this session -- `in` cannot tell one site
# from three, and every recipe has to carry the worker or its certification is unearnable.
check("THE TRAINING IS AN ORDINARY BILL, not a button",
      recipes.count("<workAmount>") == len(recipe_names)
      and recipes.count("RimroomsAsyncIndustries.Personnel."
                        "RecipeWorker_RimroomsCertification") == len(recipe_names)
      and "public override void Notify_IterationCompleted(Pawn billDoer" in certs,
      "-- modelled on `RR_AssembleMachineGate`: a pawn walks over, works, and the worker records "
      "it against whoever did it. No new work giver, no new job driver, no new building")

check("AND CORE ENFORCES THE SKILL FLOOR, not this mod",
      recipes.count("<skillRequirements>") == len(recipe_names)
      and "minimumSkill" not in cert_def,
      "-- a floor checked after the work was done would mean spending thousands of ticks of "
      "somebody's day and being told no at the end")

check("the training bench is one a branch can actually reach",
      "<li>TableMachining</li>" in recipes and "ResearchBench" not in xml_only(recipes),
      "-- bills need a `Building_WorkTable` and Core's research benches are "
      "`Building_ResearchBench` with no bill stack at all, so a recipe on one would be a "
      "certification nobody could ever earn")

check("A CERTIFICATION IS HELD BY LOAD ID, never by a Pawn reference",
      "internal string crewLoadId;" in certs
      and "pawn.GetUniqueLoadID()" in certs
      and "Pawn pawn;" not in code_only(certs),
      "-- a colonist who leaves, dies or is captured must not be held alive by the branch's "
      "paperwork. Same reasoning that retired every live reference from `LostPawnRegister`")

check("and training somebody twice records nothing and says nothing",
      "if (HasCertification(pawn, certification.defName))" in certs
      and "return CompanyActionResult.Existing();" in certs
      and "if (!result.Success || result.AlreadyApplied) { return; }" in certs,
      "-- the bill is repeatable and `AvailableOnNow` is asked about the BENCH, not the pawn, so "
      "idempotence is the honest answer rather than a refusal nobody could see")

# **EVERY CERTIFICATION IS READ BY SOMETHING.** The project tree's rule, applied here.
check("EVERY SHIPPED CERTIFICATION IS ACTED ON BY NAMED CODE",
      '"RR_Cert_GateOperator"' in code_only(certs)
      and '"RR_Cert_FieldAnalyst"' in code_only(review)
      and '"RR_Cert_ReserveTechnician"' in code_only(servicing),
      "-- *an unlock a player is told about and that changes nothing is worse than no unlock: it "
      "is a lie on the card*")

check("and each one reaches a live call site",
      "dialCampaign.CertificationDialFactor(assignedOperator)" in spinup
      and "gate.ReconditionWorkFor(pawn)" in jobdriver
      and "campaign.CertificationsOf(candidate.Pawn)" in planner,
      "-- a factor nothing multiplies by is the same hollow card one step further in")

# **THE PICKER AND THE ACTION HAVE TO AGREE.** Widening one alone is the refusal-mismatch defect.
check("THE REVIEWER PICKER AND THE REVIEW ACTION AGREE ABOUT THE CERTIFICATION",
      review.count('HasCertification(pawn, "RR_Cert_FieldAnalyst")') == 1
      and review.count('HasCertification(reviewer, "RR_Cert_FieldAnalyst")') == 1,
      "-- `ReviewerFor` admits a trained analyst below the Intellectual floor, so `ReviewAnalysis` "
      "must too. A picker that offers somebody and an action that refuses them is the defect that "
      "cost the owner an afternoon on the gate, in a different coat")

check("and the certification only ever WIDENS who may review",
      "if (skill < MinimumReviewerIntellectual" in review
      and "&& !HasCertification(pawn," in review,
      "-- the floor still admits everybody it admitted before, so a branch that has trained "
      "nobody reviews exactly as it did")

check("NOTHING ABOUT A PAWN IS CHANGED BY BEING CERTIFIED",
      "skills.Learn" not in code_only(certs) and "hediff" not in code_only(certs).lower()
      and "traits" not in code_only(certs).lower(),
      "-- the row says *preserve pawn autonomy and vanilla skill/trait systems*. A certification "
      "is a record the COMPANY keeps; the ordinary learning comes from the recipe's `workSkill`")

# ================================================= the four dispositions
check("THE DISPOSITION IS ADDITIVE BESIDE THE STATUS, never more EvidenceStatus members",
      "public enum EvidenceDisposition" in records
      and "internal EvidenceDisposition disposition;" in records
      and "Located = 0, Recovered = 1, Secured = 2, Analyzed = 3, Missing = 4 }" in records,
      "-- `Analyzed` is terminal and eight places compare against it. Three more members would "
      "change every one of those comparisons and break every save storing the value")

check("and a record can be analysed AND decided about at once",
      "disposition = decided;" in records and "status" not in
      re.sub(r"\s+", " ", records[records.index("internal void MarkDisposition"):
                                  records.index("internal void MarkDisposition") + 400]),
      "-- the two are orthogonal, and folding them into one field would make the player choose "
      "which fact they get to know")

check("ALL FOUR DISPOSITIONS EXIST, and each is reachable",
      "public CompanyActionResult ContainRecord(" in disposition
      and "public CompanyActionResult ReleaseRecord(" in disposition
      and "public CompanyActionResult TransferRecord(" in disposition
      and "public CompanyActionResult DestroyRecord(" in disposition
      and "private void Detain(Pawn pawn)" in survivor,
      "-- *contain/release/.../detain/transfer*. Detain belongs to a person rather than a "
      "record, which is why it is on the survivor comp")

check("CONTAINMENT COSTS MONEY EVERY DAY, on its own ledger line",
      "public long DailyContainmentUsd" in disposition
      and 'AddObligation(dayId + ":containment", "RR_Ledger_Containment"' in disposition
      and "AddContainmentObligation(dayId, nextOperatingCostTick);" in services,
      "-- its own line rather than folded into overhead, for the reason the remote sites give: a "
      "branch that contains everything should watch itself going broke and know which line did it")

check("TRANSFER PAYS LESS THAN THE EXCHANGE WOULD",
      "public const float TransferRate = 0.6f;" in disposition
      and "OrdinaryExchangeRate * TransferRate" in disposition,
      "-- if it paid the same it would be sale with extra words. Taking less is the whole "
      "decision, and it is the *legal-in-world* consequence stated as a price")

check("and the thing is gone once it is released, transferred or destroyed",
      disposition.count("DisposeOfItem(record);") == 4
      and "item.Destroy(DestroyMode.Vanish);" in disposition,
      "-- a record marked released with the book still on the shelf would be a lie the player "
      "can see. Found %d call(s)" % disposition.count("DisposeOfItem(record);"))

check("A TRANSFER THAT CANNOT BE PAID DOES NOT HAND THE THING OVER",
      "if (!posted.Success) { return posted; }" in disposition,
      "-- the thing leaves only once the money is on the books, or a refused posting would give "
      "it away for nothing")

# **THE ANTI-EXPLOIT.** Containment is the one reversible disposition and it must not pay.
check("ESCAPING A CONTAINMENT CHARGE PAYS NOTHING",
      "public CompanyActionResult DestroyFromContainment(" in disposition
      and "PostTransaction" not in disposition[
          disposition.index("public CompanyActionResult DestroyFromContainment("):
          disposition.index("public CompanyActionResult DestroyFromContainment(") + 1200],
      "-- a daily charge forever needs a way out, or a player pays for a decision made before "
      "they understood it. Paying for the escape would launder a contained record into money")

check("and nothing charges a fee for changing your mind",
      "ReleaseFee" not in disposition and "releaseFee" not in disposition
      and "RenewalFee" not in tenure and "renewalFee" not in tenure,
      "-- the owner's row: *a release fee must never be added -- a cost for changing your mind is "
      "the same trap in a different coat*")

check("DETAINING SOMEBODY USES CORE'S PRISONER SYSTEM, not a second model",
      "pawn.guest.SetGuestStatus(Faction.OfPlayer, GuestStatus.Prisoner);" in survivor,
      "-- needs, recruitment, escape risk, the warden job and the faction reading all already "
      "exist and all already apply")

check("and detaining with nowhere to hold anybody is refused BY NAME",
      "RR_Survivor_NoPrisonerBed" in survivor and "bed.ForPrisoners" in survivor,
      "-- a prisoner wandering the base with no visible cause is the worst version of this")

# ================================================= confidence, derived
check("CONFIDENCE IS DERIVED AND NEVER STORED",
      "public EvidenceConfidence ConfidenceOf(EvidenceRecord record)" in confidence
      and "Scribe" not in confidence
      and "confidence" not in code_only(records).lower(),
      "-- a stored score could disagree with its own inputs: settle a dispute and it would still "
      "read *contradicted* until something remembered to recompute. Same reason the material "
      "palette is rebuilt rather than saved")

check("an unsettled dispute caps confidence however good the rest is",
      "if (UnsettledDisputes(record).Any()) { return EvidenceConfidence.Weak; }" in confidence,
      "-- two of the branch's own people contradicting each other cannot be made up for by "
      "volume, which is exactly why `ReviewAnalysis` refuses to sign off while one is open. The "
      "two rules agree by construction")

check("CONFIDENCE MOVES WHAT THE CORPORATION PAYS, so the score is load-bearing",
      "public float ConfidenceValueFactor(EvidenceRecord record)" in confidence
      and "* ConfidenceValueFactor(record)" in disposition,
      "-- a score nothing reads is a readout, and the owner's row pairs *confidence* with "
      "*value* on one line")

check("and it never pays LESS than an unverified record",
      "default: return 1f;" in confidence,
      "-- a penalty for handing over something thin would push a player to sit on findings, "
      "which is what the containment charge already costs them for")

# ================================================= story variation
check("THE FOUR UNREAD INPUTS ARE READ NOW",
      "public int CompanyTier" in variation
      and "TimesCancelled(" in variation
      and "public int BestOpeningTier" in variation
      and "public int HostileFactionCount" in variation,
      "-- company tier, previous outcome, opening duration and client/faction. The other four on "
      "the row reached generation at 0.12.12-dev through `CanTakeRoute`")

check("IT IS A BIAS AND NEVER A FILTER",
      "DrawWeightedFamily(freshest, roll)" in generation
      and "return takeable >= 2 && kinds.Count >= 2;" in generation,
      "-- `FamilyEligible` still decides what is ANSWERABLE. A fifth hard condition is how a "
      "branch ends up with nothing on the table, which is the trap `CoordinateMotif` names for "
      "room themes")

check("and the pull is bounded in both directions",
      "private const float MaximumPull = 1.6f;" in variation
      and "Mathf.Clamp(factor, 1f / MaximumPull, MaximumPull)" in variation,
      "-- the owner's word is *bounded*. A weight that can reach zero is a filter wearing a "
      "weight's clothes and brings the empty-table risk back")

check("LEAST-ASKED-FIRST IS UNTOUCHED",
      "int asked = TimesAsked(eligible[index].defName);" in generation
      and "TimesAsked(definition.defName) == fewest" in generation,
      "-- that is the fairness rule stopping the company repeating its cheapest request for "
      "ever. The weighting applies INSIDE the tie, where the choice was arbitrary")

check("and the draw is derived, never Rand",
      "CampaignSeed.Derive(campaignSeed," in generation
      and "Rand." not in code_only(variation),
      "-- the same branch asked at the same point gets the same request, so a save reloaded "
      "twice does not produce two different campaigns")

check("AND NO DEF FIELD WAS ADDED FOR A FACTION NOTHING WOULD FILL",
      "faction" not in re.sub(r"\s+", "", read(SRC, "Company", "RequestDefs.cs")).lower(),
      "-- a `faction` field with no authored content behind it would be the hollow unlock this "
      "package keeps refusing. What a player's WORLD looks like is real data instead")

# ================================================= tenure: no term, ever
# **THE CLAIM THAT MATTERS MOST, AND IT IS A REFUSAL.**
# **THE SAME PATTERN ON BOTH FILES, which the first version did not do:** the site register was
# checked for `termTick|leaseTerm|termDays` and not for `expir`, so a plant that put an
# `expiryTick` into registration walked straight past it. A clock is a clock whichever file grows
# it, so there is one pattern and both files are held to it.
CLOCK_NAMES = r"(termTick|leaseTerm|termDays|expir|deadline|timeout|countdown)"
check("THERE IS NO LEASE TERM, AND THERE IS NO CLOCK ON A PLACE",
      not re.search(CLOCK_NAMES, code_only(tenure), re.I)
      and not re.search(CLOCK_NAMES, code_only(sites), re.I),
      "-- CAMPAIGN_CHART 1.1: *nothing else in this mod has a duration*. A term is a countdown "
      "on a thing the player is asked to maintain, so the row is answered by saying so rather "
      "than by building a smaller version of it")

check("EVICTION IS DRIVEN BY ARREARS, never by time passing",
      "public int SiteArrearsCount" in tenure
      and "SiteArrearsCount >= ArrearsBeforeEviction" in tenure
      and "registeredTick" in tenure,
      "-- 1.1 permits the gate's window because it is *the consequence of things the player "
      "controls*. This is built to the same test: visible on the ledger, cleared by paying")

# **A POSITIONAL CLAIM ENCODES LAYOUT, NOT THE PROPERTY, and a plant proved it again.** The
# first version compared the index of the arrears event against the index of `EvictOnePlace()`.
# Moving the call *below the closing brace* -- out of the unpaid branch entirely, so it runs on
# every operating day whether the branch paid or not -- still satisfied that ordering, and the
# suite reported MISSED. `NOW.md` already records this exact class from the previous batch.
#
# The property is **containment**: eviction has to be the last thing inside the block the arrears
# event opens. Asserted on whitespace-normalised, comment-stripped source, so it is insensitive
# to formatting while still proving the two sit in one block.
_flat_services = re.sub(r"\s+", " ", code_only(services))
check("and it is reached only from the unpaid branch of the operating day",
      'RecordEvent("RR_Event_OperatingArrears", branchId); EvictOnePlace(); }' in _flat_services,
      "-- a branch that keeps paying keeps its places for ever, which is the whole argument for "
      "this being allowed at all")

check("ONE PLACE AT A TIME, and the branch keeps the one it has run longest",
      "record.registeredTick > newest.registeredTick" in tenure
      and "remoteSites.Remove(newest);" in tenure,
      "-- taking everything at once turns a cash-flow problem into a campaign-ending event with "
      "no step in between, and the newest place is the one it had least reason to hold")

check("AND AN EVICTION IS RECORDED AS ONE, not as a release",
      '"RR_Event_RemoteSiteEvicted"' in tenure
      and '"RR_Event_RemoteSiteReleased"' not in tenure,
      "-- the branch did not choose this, and a history that cannot tell the two apart is a "
      "history that lies about what happened")

check("RENEWAL IS THE ORDINARY REGISTRATION, and costs nothing",
      "public string RenewalFailureKey()" in tenure
      and "string arrears = RenewalFailureKey();" in sites,
      "-- the branch has already lost the place and still owes the money. Charging again for the "
      "recovery would be charging twice for one mistake")

check("and it is refused only while what is owed is outstanding",
      'return SiteArrearsCount > 0 ? "RR_Site_ArrearsOutstanding" : null;' in tenure,
      "-- a condition the player clears by paying rather than by waiting, which is what keeps it "
      "the right side of 1.1")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: training is work, every disposition costs something, confidence is derived "
      "and load-bearing, and the only clock is still the gate")
