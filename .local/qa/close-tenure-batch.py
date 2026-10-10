# -*- coding: utf-8 -*-
"""Close what this batch built. Evidence on the row's own line, nothing past it."""
import io
import sys

NL = chr(10)
TODO = "docs/TODO.md"

CLOSED = [
 # ======================================================== certifications and training jobs
 ('- [~] Add configurable company roles, staff schedules, certifications, training jobs,',
  'CLOSED 0.12.90-dev, **and one of the three things this row listed as missing was already '
  'built.** '
  '**Staff prior exposure was not open at all** — `Company/StaffExposure.cs` ships '
  '`NoteFieldExposure` (called from the one place *came back from there* is already known), '
  '`ExposureDialFactor` (read by `GateSpinUp`), and `FieldTripsFor`/`HasBeenTo` (read by the crew '
  'planner). Measured against the source rather than taken from the row. '
  '**Certifications and training jobs are new.** A certification is the **person-level twin of a '
  'company project**: a project spends insight and work to give the whole branch a capability, a '
  'certification spends one person’s work to give that person a qualification, and it stays '
  'with them. The row lists roles and certifications separately and that is the difference — a '
  'role is what somebody is **assigned** to do. '
  '**The training job is a real bill, which is the owner’s own word: *jobs*.** Each one is a '
  '`RecipeDef` the player adds to a bench, modelled exactly on `RR_AssembleMachineGate`: a pawn '
  'walks over, works, and `RecipeWorker_RimroomsCertification` records it against whoever did it. '
  '**No new work giver, no new job driver and no new building** — Core’s bill system already '
  '*is* this mechanism. And **Core enforces the skill floor** through `skillRequirements`, which '
  'matters beyond tidiness: a floor checked after the work was done would mean spending thousands '
  'of ticks of somebody’s day and being told no at the end. '
  '**Three ship and every one is read by named code** — the project tree’s rule, because '
  '*an unlock a player is told about and that changes nothing is worse than no unlock*. '
  '`RR_Cert_GateOperator` takes work off the spin-up dial, `RR_Cert_FieldAnalyst` qualifies a '
  'reviewer whatever their Intellectual, `RR_Cert_ReserveTechnician` makes reconditioning '
  'cheaper. **Security and medical logistics have none, deliberately:** no existing surface would '
  'act on one, and a fourth card promising nothing is what the project tree refuses by leaving '
  'transport and orbital support without a tier 0. '
  '**And the row’s own last clause is honoured literally** — *"preserve pawn autonomy and '
  'vanilla skill/trait systems"*: nothing grants a skill, a trait, a hediff or a passion. The '
  'certification is a record the **company** keeps; the ordinary learning comes from the '
  'recipe’s `workSkill` and Core handles it.'),

 # ======================================================== the dispositions
 ('- [~] Make sale/study/use/contain/release/recruit/detain/transfer choices visible',
  'CLOSED 0.12.90-dev, all four that were missing. **A choice with no consequence is a label**, '
  'which is why the row asks for consequences and why each of these has one a player can feel. '
  '**Contain** keeps the thing off the exchange and **charges the branch every day, on its own '
  'ledger line** — modelled on `DailyRemoteSiteOverheadUsd` down to not being folded into '
  'overhead, for the same stated reason: a branch that contains everything it finds should be '
  'able to watch itself going broke and know which line is doing it. '
  '**Release** puts it back: pays nothing, costs nothing, and the thing is gone. '
  '**Transfer** hands it to the corporation for **less than the exchange would pay** — if it '
  'paid the same it would be sale with extra words, so taking less *is* the decision, and that is '
  'the *legal-in-world* consequence expressed as a price rather than as a paragraph. It needs '
  'contact, because there is nobody to hand it to otherwise. '
  '**Detain** is the one that belongs to a person rather than a record, so it sits beside the '
  'passage offer on the survivor — **take them home as one of yours, or hold them.** The '
  'consequence is **Core’s entire prisoner system**: needs, recruitment, escape risk, the '
  'warden job and the faction reading all already exist and all already apply, which is why this '
  'is a few lines rather than a subsystem. Refused **by name** when there is nowhere to hold '
  'anybody, because a prisoner wandering the base with no visible cause is the worst version. '
  '**And nothing charges a fee for changing your mind**, per the owner’s own rule on the '
  'leasing row. The schema is **additive beside `EvidenceStatus`**, never more members of it: '
  '`Analyzed` is terminal and eight places compare against it.'),

 # ======================================================== confidence and destruction
 ('- [~] Implement evidence provenance/custody/type/value/risk/confidence,',
  'CLOSED 0.12.90-dev, both halves the row named. '
  '**Confidence is DERIVED and never stored**, and that is the design rather than an '
  'optimisation: it is a function of the record’s own observations, disputes, analysis and '
  'sign-off, all of which are already saved. A stored score would be a **second copy that could '
  'disagree with its own inputs** — settle a dispute and it would still read *contradicted* '
  'until something remembered to recompute. Same reasoning `CoordinateMaterials` gives for '
  'rebuilding a palette rather than saving one, and it is why this needed no save migration. '
  'Four bands rather than a percentage, because a percentage invites a player to read precision '
  'that is not there; the band names which fact to go and fix. **An unsettled dispute caps it at '
  'Weak whatever else is true** — two of the branch’s own people contradicting each other '
  'cannot be made up for by volume, which is exactly why `ReviewAnalysis` refuses to sign off '
  'while one is open. **The two rules agree by construction.** '
  '**And it is load-bearing rather than a readout:** confidence moves what the corporation pays '
  'for a transfer, which is the honest reading of the row pairing *confidence* with *value* on '
  'one line. It never pays **less** than an unverified record, because a penalty for handing over '
  'something thin would push a player to sit on findings — and sitting on findings is what the '
  'containment charge already costs them for. '
  '**Destruction** is its own disposition and deliberately not folded into release: releasing '
  'puts a thing **back**, where it still exists; destroying means it exists nowhere. It is also '
  '**the only option that needs nothing** — no buyer, no contact, nowhere to put it — which is '
  'why a branch out of options still has it. And it is the one way out of a containment charge, '
  'paying **nothing**, so contain-then-cash can never beat selling.'),

 # ======================================================== story variation
 ('- [~] Generate bounded story variations from client/faction, coordinate, staffing,',
  'CLOSED 0.12.90-dev, the four inputs the generator could not see. '
  '**Company tier** against what a family pays — a tier-five branch asked for a two-hundred '
  'credit errand is the company not noticing it grew, and the opposite mistake is just as bad. '
  '**Previous outcome** — a family the branch has turned down repeatedly is one the company '
  'stops leading with; damping rather than exclusion, because *"the player may cancel, the '
  'corporation may not"* cuts both ways. **Opening duration** against how deep a family’s '
  'arc goes, because work that goes deep needs a window that stays open. **Client and faction '
  'identity**, read as how many factions in the player’s own world are hostile. '
  '**It is a bias and never a filter, and that distinction is load-bearing.** `FamilyEligible` '
  'still decides what is *answerable* — two takeable routes of two different kinds — and '
  'nothing here touches it. **Adding a fifth hard condition is how a branch ends up with nothing '
  'on the table at all**, which is the trap `CoordinateMotif` already names for room themes. '
  'Every factor is clamped into a bounded range in both directions, because the owner’s word '
  'is *"bounded"* and a weight that can reach zero is a filter wearing a weight’s clothes. '
  '**Least-asked-first is untouched** — that is the fairness rule stopping the company repeating '
  'its cheapest request for ever; the weighting applies **inside the tie**, which is exactly '
  'where the code was choosing at random. Derived from the branch seed, never `Rand`. '
  '**And no `faction` field was added to the def**, deliberately: there is no authored content '
  'behind one, so it would have been the hollow unlock this package keeps refusing. What a '
  'player’s **world** looks like is real data that varies between campaigns.'),

 # ======================================================== tenure, and the refusal
 ('- [~] Add space leasing/claiming with cost, boundaries, term,',
  'CLOSED 0.12.90-dev — **and "term" is REFUSED rather than built, which is the interesting '
  'half.** '
  '`docs/CAMPAIGN_CHART.md` §1.1 is absolute and checker-enforced: *"A gate’s connection has '
  'a duration. **Nothing else in this mod has a duration.**"* The owner’s words behind it '
  'were *"nothing ever ever have time restripctions but the gate"*, and §1.1 states what that '
  'forbids in so many words — **no countdown on anything a player is asked to do**. A lease term '
  'is a countdown on a thing the player is asked to maintain. **So there is no term, there will '
  'not be one, and `RemoteSiteTenure.cs` is where that is recorded** — the same way the chart '
  'records four prep documents’ *"timed distortion investigations"* as **superseded**. A row '
  'asking for something a LAW forbids is answered by saying so, not by building a smaller '
  'version of it. '
  '**Eviction is allowed because it is a consequence, not a clock**, and it is built to §1.1’s '
  'own test — the gate’s window is permitted precisely because it is *"the consequence of '
  'things the player controls"* and *"a thing the player can see, understand and act on"*. A '
  'place goes **only** because the branch stopped paying for it, the unpaid bill is on the ledger, '
  'and paying clears it. **No time passing ever evicts anybody**; a branch that keeps paying keeps '
  'its places for ever. One place per operating day and the newest first, so a cash-flow problem '
  'never becomes a campaign-ending event with no step in between — and it is recorded as an '
  '**eviction**, not a release, because the branch did not choose it and a history that cannot '
  'tell those apart lies about what happened. '
  '**Renewal costs nothing**, because *"a cost for changing your mind is the same trap in a '
  'different coat"* is on this row and the branch that lost a place and still owes for it has '
  'already paid twice. It is the ordinary registration, refused only while the arrears are '
  'outstanding — a condition cleared by paying rather than by waiting.'),

 # ======================================================== three measured stale
 ('- [~] Room functions, applicant pools, training/certification, wellbeing',
  'CLOSED 0.12.90-dev, every clause resolved. **Applicant pools** shipped long ago. **Room '
  'functions** landed at 0.12.89-dev — quarantine, armory, radio, receiving and canteen as gate '
  'equipment link roles, each knowing what should be kept on it and what goes wrong when it is '
  'not. **Training and certification** landed in this batch, on their own row above. '
  '**Wellbeing is superseded because RimWorld ships it** — needs, mood, health and recreation '
  'are Core’s, and a second wellbeing model beside them would be the duplicate-system defect '
  'the existing-content policy exists to refuse. '
  'The row’s parenthetical — *"needs the cross-map adapters to be meaningful across '
  'maps"* — is satisfied: the adapters ship, and a role is bound per gate on the branch rather '
  'than per map, so a sprawling installation works.'),

 ('- [~] Make equipment meaningfully change what is detected or generated',
  'CLOSED 0.12.90-dev as the split verdict it already was, with nothing left open on either '
  'half. **Seed reproducibility is held absolutely** — invariant 27: anything feeding the layout '
  'fingerprint is snapshotted rather than read live, so no already-saved coordinate can be '
  'invalidated by equipment changing. That is the half the row protects and it is protected. '
  '**The equipment half is superseded**, and re-opening it would reverse a closed decision rather '
  'than complete an open one: the field gear was retired under the existing-content policy, so '
  'authoring new gear to change what a coordinate generates would reopen exactly the category '
  'M2 closed. '
  '**What equipment DOES change is still real and still grows** — familiarity drives gate '
  'spin-up (0.8.9-dev), and 0.12.90-dev adds operator certification beside it. Those change what '
  'the branch can *do*, which is the lever that survived; what a coordinate *generates* stays a '
  'pure function of its seed, on purpose.'),

 ('- [~] **"they only gave me noraml books named wrong things"**',
  'CLOSED 0.12.90-dev — **the thing this row was waiting for got built, and the row was left '
  'open to let the owner overrule a call that no longer needs making.** Its own note said the '
  'label half was deliberately not built because '
  '`Patches/RR_ExistingEvidenceBook.xml` attaches the comp to **every Core `TextBook`**, so a '
  '`TransformLabel` there *"would retitle every novel in the game"*. '
  '**That is exactly what the `companyIssued` flag solved at 0.12.87-dev.** '
  '`CompRouteEvidence.TransformLabel` returns the company label **only** when the book was marked '
  'as company-issued — marked at grant time by `ScenPart_RimroomsArrival` and '
  '`GenStep_Headquarters` — and returns the original label for everything else. So a company '
  'book is named as one, every novel in every colony in the game is untouched, and the objection '
  'that kept the row open no longer applies. The owner’s chosen option, *"its own label and '
  'an inspect card"*, is now built in both halves.'),

 ('- [~] **Gate size and what it lets through.**',
  'CLOSED 0.12.90-dev, **measured against the source rather than assumed.** Every item the row '
  'listed as open is built, most of it at 0.12.87-dev. '
  '**What size lets through, at the traversal chokepoint:** `PortalTraversalPolicy` carries '
  '`WidthForPeople`, `WidthForHerdAnimals` and `WidthForVehicles`, and `FitFailureKey(Pawn, int, '
  'int)` checks multi-cell bodies **before** the body-size ladder. The owner specified it '
  'directly: *"people through 1x1 cdoor gates, herd animals through 2x1 and vehicals through 3.1 '
  'and 3x2 depending size"*. **Bulk cargo, pack animals and vehicles** are that same ladder. '
  '**Depth as well as width**, which was the missing geometry: `GateFootprint.GateOpeningDepth` '
  'is what distinguishes 1x3 from 2x3, and `VehicleFitFailureKey` refuses a vehicle that is too '
  'long *or* too wide — before it, width 3 returned *no limit* and two of the four legal '
  'footprints were indistinguishable. **Hostiles** are handled at the same single chokepoint, '
  'which is the rule that matters: an inhabitant never decides anything about a gate. **What the '
  'opening draws** shipped with the blue glow and the colourable door, per *"its not blue!!! it '
  'doesnt have a light aura"* — Core’s own `CompGlower` and `CompColorable`, per instance, '
  'no new texture and no new def. **Abreast and no-quota** were already archived at 0.9.2-dev.'),
]

NOTES = [
 ('- [~] Containment, interviews, settlement openings, outposts, vehicles, VGE hooks.',
  'CONTAINMENT CLOSED 0.12.90-dev — it is one of the four dispositions on the choices row '
  'above, with a daily charge on its own ledger line and a way out that pays nothing. '
  '**The row stays `[~]` because vehicles and the VGE hooks are still open and still on their own '
  'rows**, and nothing in this batch touched either.'),
]

text = io.open(TODO, encoding="utf-8").read()
problems = 0

for anchor, evidence in CLOSED:
    found = text.count(anchor)
    if found != 1:
        print("ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:88]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    marker = "- [~] " if anchor.startswith("- [~]") else "- [ ] "
    row = "- [x] " + text[at:line_end][len(marker):]
    text = text[:at] + row + " — **" + evidence + "**" + text[line_end:]

for anchor, note in NOTES:
    found = text.count(anchor)
    if found != 1:
        print("NOTE ANCHOR NOT UNIQUE (%d): %s" % (found, anchor[:88]))
        problems += 1
        continue
    at = text.index(anchor)
    line_end = text.index(NL, at)
    text = text[:line_end] + " — **" + note + "**" + text[line_end:]

if problems:
    print("%d row(s) not touched; nothing written" % problems)
    sys.exit(1)
io.open(TODO, "w", encoding="utf-8", newline=NL).write(text)
print("closed %d rows, noted %d" % (len(CLOSED), len(NOTES)))
