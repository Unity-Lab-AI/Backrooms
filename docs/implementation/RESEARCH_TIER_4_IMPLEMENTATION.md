# Six rungs, and two that could not exist — 0.12.29-dev, 2026-09-29

**Dated record.** Never rewritten. Completes the research ladder, and the two absences are the part
worth reading.

---

## Surveyed, not assumed

The row said *"re-run the sweep, do not carry an old verdict"*, and it was right to. **0.12.5-dev
deleted four tier 3 projects** because the systems their unlocks would have modified were not
written — four invented effects, caught by invariant 136. Tier 3 became writeable at 0.12.18-dev
only because arc 5 had since built those systems.

So every branch was surveyed for a **fifth unclaimed knob a player could name the effect of**, and
the survey came back **six, not eight**.

| Branch | Knob | What a player sees |
|---|---|---|
| Facilities | `dialSpinUpWorkRequired` | bringing any gate up takes a fifth less work |
| Fieldcraft | `RecoveryRate` | a crew shakes the place off twice as fast **once out of it** |
| Commerce | `OrdinaryExchangeRate` 0.85 → 0.95 | the company stops underpaying for ordinary salvage |
| Measurement | `MinimumInterviewerSocial` 4 → 2 | most of the branch can take a statement, not just its two most sociable staff |
| Spatial | `WorldFrontierRarity` 40 → 28 | ways in turn up on your own maps noticeably more often |
| Entities | `MaxPenalty` 10 → 6 | the worst the place can weigh on somebody drops from severe to noticeable |

Every one of those numbers was **unclaimed before this tier** — checked against all 28 existing
capability read sites, each of which is read exactly once.

**Measurement's knob only exists because of the previous checkpoint.** The interview shipped at
0.12.28-dev with a Social 4 floor; a project that lowers a floor is observable, and there would have
been nothing there to move a day earlier.

---

## Logistics has no tier 4, and that is a finding

Every Logistics knob is taken:

| Knob | Claimed by |
|---|---|
| order capacity | `RR_Cap_StandingOrders`, tier 0 |
| lead time | `RR_Cap_Relays`, tier 1 |
| dispatch delay | `RR_Cap_ForwardDispatch`, tier 2 |
| unattended delivery | `RR_Cap_UnattendedDelivery`, tier 3 |

What is left in `RimroomsProcurementComponent` is `MaximumOpenOrders` at **100**,
`MaximumPhysicalStacksPerOrder` at **4096** and `MaximumStacksDeliveredPerTick` at **4**. Those are
safety bounds a player will never reach — raising any of them changes nothing anybody could name.

**A fifth Logistics project would have been the fifth invented effect this project has caught.** So
it is not written, and the proof asserts both that it does not exist *and* that the lower tiers still
claim those four knobs — **so if a lower tier ever stops claiming one, the proof starts failing and
Logistics gets its tier 4 after all.**

## The gate line cannot have a fifth rung

Its fourth is already *"a connection that no longer counts down. It holds for as long as the gate is
powered, staffed and fed."* And `portalIndefiniteTier` is **4**, which the ladder reaches.

**There is nothing above indefinite.** This absence is not a gap in the work; it is the shape of the
thing. The proof pins the ladder at exactly four rungs with the standing connection on top, so
adding a fifth fails.

### An absence cannot be seen by reading

That is why both are proof claims rather than comments. A reader opening the def file sees six
tier-4 projects and **has no way to tell whether the other two were considered and declined or
simply forgotten.** The proof is the only thing that can carry that difference forward.

---

## Three restraints survived, and one owner answer

| Restraint | How it held |
|---|---|
| the per-coordinate frontier cap is **not** a research knob (0.12.18-dev) | Spatial took the **ordinary-map rarity** instead — a different number about a different place. `MaximumFrontiersPerCoordinate` *and* `MaximumFrontiersPerOrdinaryMap` are both untouched: only *how often*, never *how many* |
| shelter never reaches zero (0.12.18-dev) | Entities took the **penalty ceiling**, not the shelter rate a second time. And the new ceiling is **6** against a minimum of 1 — a branch can learn to carry the place, not to stop feeling it |
| the larger gate sizes must cost more to run (owner) | Practised dialling discounts the **requirement**, not the floor, so a well-worn address is quick and never free |
| *"option 1"* — naturals reach through depth 3, then stop (owner) | `MaximumNaturalDepth` stays **3** and is not research-driven. Raising it would have contradicted an answer already on record |

One more, unprompted: **the odd exchange premium is untouched.** Commerce learns to stop being
fleeced on scrap; it does not learn to make the Backrooms pay better, because that premium is what
the whole economy is built on.

---

## A false finding, caught before it was written

Midway through the survey my grep reported that **three gate projects grant nothing** — no
capability, no unlock flag. Three hollow projects shipped, the exact defect invariant 136 exists for.

I checked before asserting. The gate line drives `PortalWindowTier` by **counting completed projects
by defName** from `portalWindowTierProjects`, which the def file's own comment says. They are fully
wired. **My grep looked for `grantsCapabilities` and `unlocks*` and the mechanism is neither.**

**Fourth time this session my measurement was the defect rather than the code** — after the queue
count, the assembly-hash grep, and the keyed-string parser. Invariant 203 is about exactly this:
condemning working code on a failed search is worse than trusting a wrong comment, because it
invites somebody to "fix" what works.

---

## The proof, fault-planted eight ways

`.local/register/proof-research-tier4.py` — the **twenty-sixth** — asserts **40 claims**. The
existing `proof-research-branches.py` picked up all six new capabilities automatically and verified
each has a real read site, which is why this one concentrates on what that cannot see.

| Planted fault | Exit | Caught |
|---|---|---|
| a tier 4 project grants a capability nothing reads | 1 | ✓ |
| a tier 4 prerequisite points at another branch | 1 | ✓ |
| **a seventh tier 4 project appears for Logistics** | 1 | ✓ |
| **a fifth rung is added to the gate ladder** | 1 | ✓ |
| the per-coordinate frontier cap becomes a research knob | 1 | ✓ |
| the natural depth reach becomes a research knob | 1 | ✓ |
| the penalty ceiling drops to the minimum | 1 | ✓ |
| practised dialling makes a gate free | 1 | ✓ |
| *restored* | **0** | — |

---

## Receipts

| | |
|---|---|
| Version | 0.12.29-dev |
| Build | **176 C# files, 87 package files**, **0 warnings, 0 errors** |
| Assembly | `5AC7B632E73EF27710CE5EEE10311007B14579C62788353AF41C6F6619753E7A`, identical across two clean rebuilds |
| Projects | **38**, up from 32 |
| Tier 4 projects | **6**, and **2 branches deliberately without one** |
| New gameplay content | **none.** Six capabilities, six existing numbers made research-driven |
| Invented effects | **zero**, which is the whole point of the survey |
| Checkers | **ten**, all passing |
| Proofs | **twenty-six**, all exiting zero |
| Planted faults caught | **8 of 8** |
| Game launched | **no.** Not one of these numbers has been watched changing |
