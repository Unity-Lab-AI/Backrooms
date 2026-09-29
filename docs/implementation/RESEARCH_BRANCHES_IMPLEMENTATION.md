# Seven ways into the tree, and every one of them does something — 0.11.3-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## What this is

**Step 6 of the build order in `docs/CAMPAIGN_CHART.md`**, tier 0: the entry band of the eight
research branches that were not the gate.

The gate branch was completed in 0.10.9-dev. This is the foundation rung of the rest.

---

## The design decision that shaped it

The chart lists nine branches across five tiers. Built naively that is somewhere around
**twenty-four to forty projects, each needing an effect**, and the obvious implementation is a
typed field per effect: `unlocksSurveyedRoutePlanning`, then `reducesPowerHeadroom`, then
`extendsReturnWindow`, and so on.

**That would be twenty-four chances to ship an effect nothing reads.** Nothing about a
`public bool unlocksSomething` tells you whether any system looks at it, and a project whose card
promises an unlock while no code honours it is **worse than a project with no effect** — it is a
lie the player paid insight for, and it is invisible. The def loads. The project completes. The
card reads correctly. Nothing happens.

That is the same failure class as the beacon condition that could never fire (0.10.7-dev) and the
tier ladder that could never be climbed (0.10.9-dev). Both compiled. Both looked right in every
individual file. Both were visible only in the relationship between two places.

So: **one generic mechanism.** A project declares `grantsCapabilities`, systems ask
`campaign.HasCapability("…")`, and an offline proof asserts the relationship **in both
directions**.

---

## The seven, and what each one actually moves

Every effect below is a real change to a value a real system already reads. Nothing was invented
to give a project something to do.

| Branch | Project | Capability | What it moves | Where |
|---|---|---|---|---|
| Facilities and power | **Reserve Discipline** | `RR_Cap_ReserveDiscipline` | gate headroom ×0.6 | `CompRimroomsGate.MinimumPowerHeadroomWatts` |
| Fieldcraft and medicine | **Return Drill** | `RR_Cap_ReturnDrill` | emergency return window ×1.5 | `CompRimroomsGate.EnterEmergency` |
| Measurement and evidence | **Second Reading** | `RR_Cap_SecondReading` | insight per analysed record ×2 | `InvestigationServices.AddAnalysisWork` |
| Spatial mapping and topology | **Coordinate Atlas** | `RR_Cap_CoordinateAtlas` | quiet returns ⅓ → ½ | `RevisitDisplacement.OnArrival` |
| Entities and containment | **Early Warning** | `RR_Cap_EarlyWarning` | contact grace ×2 | `FirstSlicePursuer.ContactGraceTicks` |
| Communications and logistics | **Standing Orders** | `RR_Cap_StandingOrders` | held cargo budget ×2 | `RimroomsProcurementComponent.CreateHeldCargo` |
| Commerce and organisation | **Negotiated Terms** | `RR_Cap_NegotiatedTerms` | catalogue price −10% | `RimroomsProcurementComponent` quote |

### Seven, not eight

**Transport and orbital support has no tier 0 project, deliberately.** The chart says it is
DLC-optional and never required. A project granting nothing, so that the count looked complete,
would be exactly the lie this checkpoint is built to prevent.

### Notes on two of them

**Coordinate Atlas raises the quiet share rather than stopping displacement.** The space has not
stopped moving things; the branch has got better at knowing when it did. That keeps the horror
mechanic intact — invariant 74 says a mechanic that fires every time is a mechanic rather than
horror, and one a player can *switch off* is worse still.

**Early Warning pays in time, not damage.** Every threat in this mod owes the player a readable
warning, a learnable rule and a countermeasure. Doubling the grace between recognising something
and it reaching you is all three at once.

---

## Why tier 0 has no prerequisites

Tier 0 **is** the entry band, so each of the seven is its own root. The chart's linkage rule says
every tier above 0 must be reachable by more than one path, because *"a branch that can only be
entered through one project is a single point of failure for a player who has not happened to
generate the right log"*.

At tier 0 that is satisfied by construction: **eight independent roots**, counting the gate's.
They cost insight and nothing else, which in practice means *"after your first analysed record"* —
insight only comes from analysis. None requires a distortion or entity log, because those need
something to have gone wrong, and a branch cannot be asked to have had a bad day before it may
begin studying anything.

---

## The proof

`.local/register/proof-research-branches.py`. The claim that matters:

> **Every capability any project grants is read by at least one source file, and every capability
> any source file reads is granted by at least one project.**

Both directions, because **a read with no grant is dead code and a grant with no read is a lie**.
Plus: no capability granted twice (the second would be free); at least two independent roots; no
root needing a distortion or entity log; every project carrying a real label and a description
longer than a stub; no prerequisite naming a project that does not exist; and no cycle, checked
transitively.

### Sanity-tested in both directions

| Planted | Result |
|---|---|
| A granted capability renamed so nothing reads it | **FAIL** ×2 — *"the card promises an unlock and no code honours it"* **and** the orphaned read site |
| A read site renamed so nothing grants it | **FAIL** ×2 — symmetrically |
| Both reverted | **PROOF HELD** |

That the plant produces **two** failures each time is the proof's design working: the two
directions catch the same break from opposite ends, so neither can be silently disabled.

---

## Two checkers needed teaching

`check-package-integrity.py` and `check-keyed-strings.py` both read `RR_Cap_*` as a broken
reference — one as an undeclared def, the other as a missing keyed string. **It is neither.** A
capability is an internal name a project grants and a source file asks for; a player never reads
one.

Both now classify `RR_Cap_*` alongside the existing internal identifiers (toil names, audio cues),
with a comment pointing at the proof. That is not a weakening: **the proof gives a stronger
guarantee than either checker could** — it catches a capability granted and never honoured, which
neither checker can see.

---

## Receipts

| | |
|---|---|
| Version | 0.11.3-dev |
| Build | 162 C# files, 85 package files, **0 warnings, 0 errors** |
| New defs | 7 `RimroomsProjectDef` — 11 total. A mechanics def, **no gameplay ThingDef** |
| New mechanism | `grantsCapabilities` / `HasCapability`, cached and rebuilt on completion |
| Systems wired | 7, each moving a value that already existed |
| New art, audio or texture | **none** |
| Harmony | **none** |
| Checkers | **eight**, all passing |
| Proofs | **four**, all holding |
| Game launched | **no** |

Next: tiers 1 and 2 across the same branches, then the clean-up team.
