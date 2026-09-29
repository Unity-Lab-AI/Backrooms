# Arcs 5 to 8 have work in them — 0.12.13-dev, 2026-09-29

**Dated record.** Never rewritten. Content against the pattern proved by
`REQUEST_GENERATION_IMPLEMENTATION.md` (0.12.12-dev).

---

## What this closes

`docs/CAMPAIGN_CHART.md` §7 step 8 authorises **arcs 5–8**, and until this checkpoint four of the
eight arcs had nothing a player could be asked to do:

| Arc | Chart's own words | Was |
|---|---|---|
| 5 | *"Remote sites need people, supplies, signals, protection, and an exit plan"* | systems built 0.12.6–0.12.9, **no requests** |
| 6 | *"Openings appear in towns. Witnesses, missing residents, public danger"* | **not built** |
| 7 | *"Heavy cargo and staff across the wider world"* | **not built** |
| 8 | *"Later coordinates combine known families, then introduce one unfamiliar rule at a time"* | systems partly built, **no requests** |

**Thirteen generated families, one per item the chart names.** Nothing invented:

| Arc | Families |
|---|---|
| **5** | relay stations · caches · field shelters · guarded leases · resupply · evacuation |
| **6** | witnesses · missing residents · public danger |
| **7** | heavy cargo · staff across the wider world |
| **8** | combining known families · one unfamiliar rule at a time |

With arc 4's five from 0.12.12-dev that is **18 generated families across arcs 4–8**, plus the
seven fixed tutorial requests: **25 request defs**.

### Arc 5's "still unwritten" list is now written

`NOW.md` has carried this line since 0.12.9-dev:

> **Still unwritten from the chart:** relay stations, caches, field shelters, guarded leases, and
> resupply and evacuation missions. **Check each against a real read site before building** —
> invariant 136.

Checked, and **every one had a real read site already**: `RR_Logistics_Relays`,
`RR_Commerce_Leases`, `RR_Commerce_NegotiatedTerms`, `RR_Logistics_StandingOrders` and
`RR_Fieldcraft_ReturnDrill` are research projects that have existed since 0.11.3–0.11.6. The
chart's arc-5 names and the research tree's branch names were **describing the same things from
two directions**, and nobody had connected them.

---

## Every route resolves against something that exists

This is the constraint that shaped all thirteen, and it is not a stylistic preference — it is
invariant 49 with teeth. Three route kinds name a def:

- `Document` / `Testify` name a **log kind**. A typo makes `TryLogKind` return false, the
  measurement zero, and the route **permanently unsatisfiable** — while still counting toward the
  two-different-kinds rule, so `ConfigErrors` passes, the package checker passes, and the request
  ships promising two ways through and having one.
- `Research` names a **project def**.
- `Redirect` names a **project or request def**.
- A generated `Purchase` names a thing **the catalogue carries**, or `CanTakeRoute` refuses it for
  ever and it can never count toward eligibility.

So the families were built from the ingredients that exist, and nothing was written that needed a
new one:

| | |
|---|---|
| things | `ComponentIndustrial`, `MealSurvivalPack`, `MedicineIndustrial`, `Silver`, `Steel`, `WoodLog` — all catalogue-carried |
| logs | `route`, `distortion`, `entity` |
| projects | 11 of the 25, none of them arc 4's three |

**No new ThingDef, PawnKindDef, art or audio.** Invariant 10 holds: this is 13 defs of the mod's
own request type, 26 routes, and 52 keyed strings.

---

## Per-arc coverage, not a total

The proof counts generated families **per arc** against the chart's list, and that distinction is
load-bearing. A total of eighteen is satisfied by **eighteen copies of arc 4**, and the point of
this checkpoint is that every arc has somewhere to put work.

Fault-planted exactly that way: moving one arc 6 family into arc 4 leaves the total at eighteen
and **still fails**, because arc 6 drops to two.

| Planted fault | Exit | Caught |
|---|---|---|
| an arc 6 family moved to arc 4, total unchanged | 1 | ✓ |
| *restored* | **0** | — |

The proof also refuses a generated family in arcs 1–3, because those are the tutorial line and
generate nothing.

---

## What the writing had to get right

The company's character is fixed by chart §4.3 — *"greedy and will basic do anything and put up
with anything to make sure you succssed"* — and greed is the **mechanism** for the patience, not a
contradiction of it. So across all thirteen, the second route is nearly always **the expensive
shortcut the company will happily accept**:

- buy the metal rather than recover it, and neither party mentions it again;
- hand over the hardware and formally pass the problem on, which *"nobody involved believes is a
  solution"*;
- pay enough silver that the staffing problem becomes a competitor's hiring department.

And the first route is nearly always **the capability the company would rather own**, because it
can sell that again. That is the same greed producing both halves, which is what makes the two
routes feel like one company talking rather than a menu.

---

## Receipts

| | |
|---|---|
| Version | 0.12.13-dev |
| Build | **173 C# files** (measured), 86 package files, **0 warnings, 0 errors** |
| C# changed | **none** — this is content against a proved pattern |
| Request defs | **25** — 7 tutorial, **18 generated** |
| New generated families | **13** |
| New keyed strings | **52** route labels and descriptions |
| Arc coverage | **4:5 · 5:6 · 6:3 · 7:2 · 8:2**, asserted per arc |
| Checkers | **eight**, all passing |
| Proofs | **seventeen**, all exiting zero |
| Claims in the generation proof | **48** |
| Game launched | **no**, and nothing in this mod has ever been played |
