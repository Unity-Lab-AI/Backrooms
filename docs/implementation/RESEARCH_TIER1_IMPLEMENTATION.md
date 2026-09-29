# The second rung of every branch — 0.11.4-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including two things it got wrong on
the way. Never rewritten.

---

## What this is

**Step 6 of the build order in `docs/CAMPAIGN_CHART.md`, tier 1**: *"First entry — prepare a
measured short expedition and interpret a first return."*

Seven projects, one per branch, each requiring its own tier-0 root and **one completed route log**.
No distortion or entity log at this band: those need something to have gone wrong, and that is
tier 2's business.

---

## The seven

| Branch | Project | Capability | What it moves | New site? |
|---|---|---|---|---|
| Facilities and power | **Efficient Aperture** | `RR_Cap_EfficientAperture` | opening draw ×0.85 | yes |
| Fieldcraft and medicine | **Rescue Training** | `RR_Cap_RescueTraining` | return window ×2 | supersedes |
| Measurement and evidence | **Corroboration** | `RR_Cap_Corroboration` | analysis work ×0.75 | yes |
| Spatial mapping and topology | **Alternate Exits** | `RR_Cap_AlternateExits` | things moved per return, cap −1 | yes |
| Entities and containment | **Detection** | `RR_Cap_Detection` | contact grace ×3 | supersedes |
| Communications and logistics | **Relays** | `RR_Cap_Relays` | lead time ×0.75 | yes |
| Commerce and organisation | **Leases** | `RR_Cap_Leases` | catalogue price −20% | supersedes |

### Supersede, do not stack

Three of these replace their tier-0 capability rather than compounding with it. The read sites
check the tier-1 capability **first** and fall through, so a branch holding both gets the deeper
number and not the product of the two. A player should be able to read *"twice as long"* off a
card and have it be twice as long.

### Two that are worth the words

**Alternate Exits lowers the cap on how many things move, not the chance that any do.** The space
still moves things, still on the same schedule. A branch that has mapped more than one way through
notices fewer because it is no longer depending on a single remembered route. Invariant 74 again:
a horror mechanic a player can switch off is worse than one that fires every time.

**Relays shortens a delay, never a deadline.** Nothing is asked of the player while a shipment is
in transit and nothing fails when it lands — the supplier is simply slow, and this makes it less
so. It is also clamped so a shipment can never arrive before it has left.

---

## Two vestigial props, found and retired

The Facilities tier-1 project was going to raise `reserveChargePowerWatts`, so a branch could
refill its reserve faster.

**That prop is read by nothing.** Neither is `returnReserveCapacityWattDays`. Both appear in
exactly two places — the declaration and a `ConfigErrors` validation — and no system consults
either. They are residue from the power model retired in **0.9.1-dev**: the gate used to own a
reserve, and since it became a designated door bound to a Core battery, **the reserve *is* that
battery** and RimWorld's power net charges it.

Note the trap: the *property* `ReturnReserveCapacityWattDays` reads the battery, while the *field*
`returnReserveCapacityWattDays` read nothing. **One character of casing** between a value that
means something and a value that means nothing, in the same class.

The validation went with them. `emergencyReturnCost + recoveryOpeningCost > returnReserveCapacity`
looked like a guarantee and was not, because it compared the costs against a number unrelated to
the battery a player actually binds. The real guarantee is untouched, in `SpendNativeOpeningTick`,
which checks the actual stored energy every tick.

**This would have shipped an unlock that changed nothing** — the exact lie the previous checkpoint
built a proof to prevent, arriving one checkpoint later through a door that proof does not watch.
It asserts that a *capability* is read; this would have been a capability that **was** read,
modifying a prop that was not. Archived:
`historical-content/0.11.4-dev/RETIRED_VESTIGIAL_POWER_PROPS.md`.

**A dead prop is more dangerous than dead code**, because it reads exactly like a live one: a
plausible name, a sensible default, and a validation rule implying somebody cared.

---

## The proof gained a claim, and the first version of it was wrong

The chart's linkage rule says *"every tier above 0 must be reachable by more than one path"*. The
first implementation asserted that **every depth must contain projects tracing to two or more
roots**, and it failed:

```
FAIL depth 2 is reachable by more than one path (1 project, 1 distinct root)
FAIL depth 3 is reachable by more than one path (1 project, 1 distinct root)
```

**The assertion was wrong and the tree was right.** Depths 2 and 3 are the gate ladder's upper
rungs, and that ladder is *deliberately* a single linear chain of four — proved ordered and
monotonic in 0.10.9-dev. Requiring it to be wide would have contradicted its own design.

Re-reading the rule: it is about **entering** a branch, not about every depth being wide. So what
must hold is that the tree has several entrances — eight, already asserted — and that no project
downstream becomes a **chokepoint where separate branches merge**. A linear chain inside one
branch is fine. A project that two different branches both must pass through is not.

Re-stated that way it passes, and it still catches something real: planting a second prerequisite
so that Commerce required Logistics failed with *"two branches merge here, so one project gates
both"*.

**The temptation was to widen the ladder so the assertion passed.** That is the failure recorded
in invariant 110 — never change the thing being measured to satisfy a measurement that was wrong.

---

## The `--` gotcha, for the fifth time

An XML comment in the new tier-1 block contained `-- those need something to have gone wrong`.
XML comments cannot contain a double hyphen, the file stopped parsing, and **the build did not
notice** — it compiles C# and copies files, it does not parse def XML.

Two checkers did catch it, hard: `check-package-integrity.py` and `check-keyed-strings.py`. Only
the order of operations hid it, because the proof ran first. **The pipeline is sound**; this is
recorded because the same escape has now cost five separate failures and the count is the useful
part.

---

## Receipts

| | |
|---|---|
| Version | 0.11.4-dev |
| Build | 162 C# files, 85 package files, **0 warnings, 0 errors** |
| New defs | 7 `RimroomsProjectDef` — **18 total** |
| Capabilities | **14**, every one granted once and read by real code |
| Retired | 2 vestigial props and a validation clause that guaranteed nothing |
| New art, audio or texture | **none** |
| Harmony | **none** |
| Checkers | **eight**, all passing |
| Proofs | **four**, all holding |
| Game launched | **no** |

Next: tier 2 across the same branches, then the clean-up team.
