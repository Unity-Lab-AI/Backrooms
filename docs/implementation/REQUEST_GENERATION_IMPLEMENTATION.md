# The company stops naming things — 0.12.12-dev, 2026-09-29

**Dated record.** Never rewritten. Follows `REQUEST_LINE_IMPLEMENTATION.md` (0.12.11-dev), which
made a request reach a player; this makes the company keep asking after the hinge.

---

## The owner's decision, and the two levels it governs

***"Both — filter picks the family, card never shrinks."***

That resolved a conflict between the answer given today and the answer given earlier the same day
(`"1 and 3"`, shipped 0.11.1-dev). They operate at different levels and both stand:

| Level | Rule | Lives in |
|---|---|---|
| **Eligibility** | a family is offered only if the branch can take **two routes of two different kinds** | `RequestGeneration.cs` — new |
| **The card** | the **full authored floor, unfiltered**, plus derived extras | `RequestRoutes.Available` — **untouched** |

*You never see a request you cannot finish, and the request you do see never hides a route from
you.* **Nothing from 0.11.1-dev is reversed**, and the proof asserts `Available` does not consult
the filter — planting that reversal makes it fail.

---

## The flaw generation exposed in what shipped yesterday

0.12.11-dev measured satisfaction as **absolute state**: *does the branch hold twenty meals*, *has
it filed a route log*. That is correct for a tutorial request, which is asked **once** — a branch
that already owns a battery has already learned request 1's lesson, and completing it on sight is
the honest outcome.

**It is wrong for anything repeatable.** Absolute state is permanently true once true, so a
generated request would have paid out the instant the player accepted it. A payout button.

So a **generated** request now records where each of its routes stood when it appeared, and asks
for that much **more**. A **tutorial** request records nothing and keeps measuring absolutely.

- The baseline is taken at **offer**, not acceptance — the card reads the same from the moment it
  appears, and a player who starts the work before formally accepting is not punished for it.
- Keyed by **label key, not list index**, so a mod-list change that reorders routes cannot shift
  every baseline onto the wrong one.
- **Saved**, unlike the satisfied-route list, because it is not derivable from the world: once the
  branch has moved past the baseline there is nothing left to read it back from.

This also forced `RouteSatisfied` to split into `MeasureRoute` (a number) and a comparison. The
per-kind distinctions are all preserved in the measurement — `proof-request-line.py` **failed on
the refactor and was retargeted**, which is the proof working: a claim that survives its subject
moving is a claim keyed off nothing.

---

## The filter, and why every clause can refuse

**Invariant 136.** A filter whose clauses are trivially true is a hollow knob that looks like a
feature, and this project has deleted four research projects and three tier-2 constants for
exactly that. So each clause names something a branch can genuinely lack:

| Route | Takeable when | Refuses when |
|---|---|---|
| Deliver, Substitute | holds one, or the catalogue carries it | a thing never seen and not orderable |
| Purchase | catalogue carries it **and** in contact | before contact, procurement does not exist |
| Document | the branch has visited a coordinate | you cannot log a place nobody has been |
| Testify | a living employee witnessed that kind | no crew has seen one |
| Research | the project exists, is **unfinished**, and **qualifies** | short of the logs its tier demands |
| Redirect | the target project or request exists | a def that is not installed |

Two details that are load-bearing:

- **A finished project is not reachable.** A Research route against completed work is satisfied on
  sight, which is the payout button again, one level up.
- **Qualification is asked of `ProjectQualificationFailureKey`** — the same function the research
  screen uses. A second copy of the log-tier rule would eventually disagree with it.
- **`CatalogueCarries` was made `internal` and is shared**, not copied, so the filter and the
  derived-route half cannot drift about what is orderable.

### The pace has no clock

The next request appears when the open one resolves, and never otherwise. **Two offer clocks were
retired in 0.11.0-dev** and none is coming back — chart §1.1. Variety comes from asking for the
**least-asked** eligible family first, tie-broken ordinally and then by the branch's own seed, so
a save reloaded twice does not produce two different campaigns.

The proof checks for `TicksGame %`, `nextRequestTick`, `interval` and `cooldown` by name.

---

## Arc 4's content, from the chart's own list

> *"Clients request surveys, samples, instruments, rescue, secure access"*

**One family per named item, nothing invented**, and every route satisfiable by one of the seven
real checks against a def that already exists:

| Family | Routes |
|---|---|
| a client wants a coordinate written up | Document(route) · Testify(route) |
| a client wants material by the crate | Deliver(Steel ×250) · Purchase(Steel ×250) |
| a client wants instruments left running | Deliver(GlowPod ×6) · Research(`RR_Measurement_SecondReading`) |
| a client has lost somebody down there | Research(`RR_Fieldcraft_RescueTraining`) · Testify(entity) |
| a client wants a door they can rely on | Research(`RR_GateStandingConnection`) · Purchase(ComponentIndustrial ×40) |

No `prerequisiteRequests` — a generated family is gated by eligibility, not by a chain. No expiry,
because there is no field for one.

---

## Save integrity had to change with it

A generated family may be asked for more than once, so request def names are no longer unique in a
save. What replaced that check is stricter about the things that matter:

- **ids carry an instance number** for generated requests; tutorial requests keep the plain id
  they have always had, so existing saves keep matching their own records.
- **a tutorial request may appear at most once** — a fixed request offered twice would be paid
  twice.
- **at most one open request in the whole save.** Both offer routines refuse while one is open, so
  two in a save means a guard was bypassed and the player has two payouts running.

---

## The check I would not have thought to write

`proof-request-generation.py` parses the request XML and asserts **every authored route can
actually fire**:

- every `Document`/`Testify` route names one of the three real log kinds;
- every `Research`/`Redirect` route names a def that exists;
- every generated `Purchase` route names something the catalogue carries.

**A `logKind` typo is invisible.** `TryLogKind` returns false, the measurement is zero, and the
route is permanently unsatisfiable — while still counting toward the two-different-kinds rule, so
`ConfigErrors` passes, the package checker passes, and a request ships with one real way through
while promising two. **Invariant 49: before designing a rule, check it can fire.** Planting
`entites` for `entity` makes the proof exit 1.

---

## Fault-planted six ways

| Planted fault | Exit | Caught |
|---|---|---|
| a `logKind` typo — route can never fire | 1 | ✓ |
| a Research route naming a missing project | 1 | ✓ |
| the Purchase clause becomes `return true` | 1 | ✓ |
| **the card starts consulting the filter** (owner decision reversed) | 1 | ✓ |
| generation no longer waits for the hinge | 1 | ✓ |
| **the baseline is recorded and then ignored** | 1 | ✓ |
| *restored* | **0** | — |

Every plant asserted its anchor before writing.

---

## Deliberately not in this checkpoint

**Arcs 5–8's generated families.** The machinery is proved by arc 4's five, and the remaining
thirteen — relay stations, caches, field shelters, guarded leases, resupply, evacuation, witnesses,
missing residents, public danger, heavy cargo, staff transfer, combined families, one unfamiliar
rule — are content against the same pattern. Next checkpoint.

---

## Receipts

| | |
|---|---|
| Version | 0.12.12-dev |
| Build | **173 C# files** (measured), 86 package files, **0 warnings, 0 errors** |
| New source | `Company/RequestGeneration.cs` |
| Request defs | **12** — 7 tutorial, **5 generated** |
| Filter clauses that can refuse | **6 of 6** |
| Checkers | **eight**, all passing |
| Proofs | **seventeen**, all exiting zero |
| Claims in the new proof | **43** |
| Planted faults caught | **6 of 6** |
| Game launched | **no**, and nothing in this mod has ever been played |
