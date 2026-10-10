# -*- coding: utf-8 -*-
"""Prepend the 0.12.90-dev entry. Newest first, nothing above it rewritten.

CHANGELOG.md has NO BOM. Last batch this script was written with `utf-8-sig` and added one,
which `git diff --stat` caught as a one-line deletion. Read and written as plain utf-8 here.
"""
import io
import sys

NL = chr(10)
PATH = "CHANGELOG.md"

ENTRY = """## 0.12.90-dev - 2026-10-05 - Training is work, a decision costs something, and the only clock is still the gate

- **CERTIFICATIONS AND TRAINING JOBS, and the training is a real bill rather than a button.**
  Owner: *"Add configurable company roles, staff schedules, certifications, training jobs, field
  history, trust/stress/exposure and equipment familiarity; preserve pawn autonomy and vanilla
  skill/trait systems"*. A certification is the **person-level twin of a company project**: a
  project spends insight and work to give the branch a capability, a certification spends one
  person's work to give that person a qualification, and it stays with them. Each one names a
  `RecipeDef` the player adds to a bench, modelled on `RR_AssembleMachineGate` - a pawn walks
  over, works, and the recipe worker records it against whoever did it. **No new work giver, no
  new job driver and no new building**, because Core's bill system already is this mechanism.
- **And Core enforces the skill floor, not this mod.** The recipes carry `skillRequirements`, so
  RimWorld refuses the bill to an unqualified pawn up front. A floor checked after the work was
  finished would mean spending thousands of ticks of somebody's day and being told no at the end.
- **Three certifications ship and every one is read by named code**, which is the project tree's
  rule: *an unlock a player is told about that changes nothing is worse than no unlock*. A trained
  operator takes work off the spin-up dial, a trained analyst may sign off a report whatever their
  Intellectual, a trained technician reconditions a gate for less work. **Security and medical
  logistics have none, deliberately** - no existing surface would act on one, and a fourth card
  promising nothing is what the project tree already refuses by leaving transport without a tier 0.
- **The row's last clause is honoured literally.** *"Preserve pawn autonomy and vanilla
  skill/trait systems"*: nothing grants a skill, a trait, a hediff or a passion. A certification is
  a record the **company** keeps, and the ordinary learning comes from the recipe's `workSkill`.
- **One of the three things that row listed as missing was already built.** Staff prior exposure
  ships and is wired - recorded where *came back from there* is already known, read by the
  spin-up dial and by the crew planner. Measured against the source rather than taken from the row.
- **CONTAIN, RELEASE, TRANSFER AND DETAIN, each with a consequence a player can feel.** Owner:
  *"Make sale/study/use/contain/release/recruit/detain/transfer choices visible with financial,
  staff, faction, legal-in-world, trust, and security consequences"*. Sale, study and recruit
  already had surfaces; these four did not exist. **Contain charges the branch every day on its
  own ledger line** - modelled on the remote-site share down to not being folded into overhead,
  for the same stated reason: a branch that contains everything should watch itself going broke
  and know which line did it. **Transfer pays less than the exchange would**, because if it paid
  the same it would be sale with extra words - taking less *is* the decision, and that is the
  legal-in-world consequence expressed as a price rather than a paragraph.
- **Detain is the one that belongs to a person**, so it sits beside the passage offer: take them
  home as one of yours, or hold them. The consequence is **Core's entire prisoner system** -
  needs, recruitment, escape risk, the warden job, the faction reading - which is why it is a few
  lines rather than a subsystem. Refused **by name** when there is nowhere to hold anybody.
- **CONFIDENCE IS DERIVED AND NEVER STORED**, and that is the design. It is a function of the
  record's own observations, disputes, analysis and sign-off, all already saved; a stored score
  would be a second copy that could disagree with its own inputs - settle a dispute and it would
  still read *contradicted* until something remembered to recompute. Four bands rather than a
  percentage, because a percentage invites precision that is not there. **An unsettled dispute
  caps it at Weak whatever else is true**, which is exactly why review refuses to sign off while
  one is open: the two rules agree by construction.
- **And it is load-bearing rather than a readout:** confidence moves what the corporation pays for
  a transfer, which is the honest reading of the row pairing *confidence* with *value* on one
  line. It never pays **less** than an unverified record, because a penalty for handing over
  something thin would push a player to sit on findings - and sitting on findings is what the
  containment charge already costs them for.
- **Destruction is its own choice and deliberately not folded into release.** Releasing puts a
  thing **back**, where it still exists; destroying means it exists nowhere. It is also **the only
  option that needs nothing** - no buyer, no contact, nowhere to put it - which is why a branch
  out of options still has it, and it is the one way out of a containment charge. **It pays
  nothing**, so contain-then-cash can never beat selling.
- **The generator can see four things about the branch it is generating for.** Owner: *"Generate
  bounded story variations from client/faction, coordinate, staffing, discovered rules, company
  tier, previous outcomes, opening duration, and available equipment"*. Four of those arrived at
  0.12.12-dev; **company tier, previous outcome, opening duration and the world's faction
  pressure did not.** Tier against what a family pays, so a tier-five branch is not asked for a
  two-hundred-credit errand. A family the branch keeps turning down is one the company stops
  leading with. Deep work needs a window that stays open.
- **It is a bias and never a filter, and the distinction is load-bearing.** `FamilyEligible` still
  decides what is *answerable*; a fifth hard condition is how a branch ends up with nothing on the
  table at all, which is the trap `CoordinateMotif` names for room themes. Every factor is clamped
  in both directions - the owner's word is *bounded*, and a weight that can reach zero is a filter
  wearing a weight's clothes. **Least-asked-first is untouched**; the weighting applies inside the
  tie, where the code was choosing at random. **And no `faction` field was added to the def**,
  because there is no authored content behind one and it would have been the hollow unlock this
  package keeps refusing.
- **EVICTION AND RENEWAL - AND "TERM" IS REFUSED RATHER THAN BUILT.** `CAMPAIGN_CHART.md` 1.1 is
  absolute and checker-enforced: *a gate's connection has a duration, nothing else in this mod
  has a duration*. **A lease term is a countdown on a thing the player is asked to maintain**, so
  the row is answered by saying so - the same way the chart records four prep documents' timed
  investigations as superseded. A row asking for something a LAW forbids is answered, not built
  smaller.
- **Eviction is allowed because it is a consequence, not a clock**, built to 1.1's own test: a
  place goes **only** because the branch stopped paying for it, the unpaid bill is on the ledger,
  and paying clears it. **No time passing ever evicts anybody.** One place per operating day and
  the newest first, so a cash-flow problem never becomes a campaign-ending event with no step in
  between - and it is recorded as an **eviction**, not a release, because the branch did not
  choose it. **Renewal costs nothing**: a branch that lost a place and still owes for it has
  already paid twice.
- **Three rows closed on measurement rather than work.** The company book's label was waiting on a
  problem the `companyIssued` flag solved at 0.12.87-dev - the label applies only to a
  company-issued book and every novel in the game is untouched, so the objection that kept the row
  open no longer applies. Gate size and what it lets through: widths for people, herd animals and
  vehicles, depth as well as width, hostiles at the same single chokepoint, and the blue glow -
  all built. Equipment versus seed reproducibility: held absolutely on one half, superseded on the
  other, with nothing left open on either.
- **Two instruments added, and four claims in them were wrong before they were right.**
  `proof-tenure-and-disposition.py` is 40 claims and `plant-tenure-and-disposition.py` reports
  **46 of 46 caught**. One claim read its own XML comment - the third time this session a claim
  has read the documentation explaining the thing it was asserting the absence of, so a comment
  stripper now exists for both languages. One asserted a needle that appears **three** times and
  was satisfied by the two the plant left behind. One checked a clock-name pattern on one file and
  a narrower one on the other, so an `expiryTick` walked past it. **And one was positional again**
  - comparing call indices, which a plant satisfied by moving the call out of its block entirely;
  the property was containment, not order, and `NOW.md` already recorded that exact class.
- Instruments: **18 checkers, 54 proofs, 28 plant suites.** Queue: 67 open, 21 partial, 38
  post-completion test, 0 completed-and-unarchived.

"""

text = io.open(PATH, encoding="utf-8").read()
if "## 0.12.90-dev" in text:
    print("already present")
    sys.exit(0)
head = "# Changelog" + NL + NL
if not text.startswith(head):
    print("CHANGELOG does not start with the expected heading; nothing written")
    sys.exit(1)
io.open(PATH, "w", encoding="utf-8", newline=NL).write(head + ENTRY + text[len(head):])
print("prepended the 0.12.90-dev entry (%d lines)" % (ENTRY.count(NL) + 1))
