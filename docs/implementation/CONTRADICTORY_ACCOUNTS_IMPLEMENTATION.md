# Two crew who disagree — 0.12.25-dev, 2026-09-29

**Dated record.** Never rewritten. Builds the oldest unbuilt content direction in the prep material,
and fixes a shipped defect that made a tutorial request unreachable as the chart describes it.

---

## The prep asked for it, the chart authorises it, and the mechanism threw it away

The prep material, in its own words:

> *"return with contradictory accounts"* — `UNIVERSE_ADAPTATION.md`
> *"return with contradictory accounts that open a case"* — `SYSTEMS_CATALOG.md`
> *"Contamination, contradictory accounts, hidden rule"* — `MOD_INTEGRATION_PLAN.md`

`docs/CAMPAIGN_CHART.md` — the authority, which beats any prep document — line 226:

| 5 | **Report a disagreement** | 2 | distortion logs | analyse a distortion record · **two crew accounts of the same room** |

**Two crew accounts of the same room were impossible.** This is the part reading the row would not
have told you.

`EvidenceObservationRecord.StableId` is per-room for **only** a room survey:

```csharp
return observationKind == EvidenceObservationKinds.RoomSurvey
    ? evidenceId + ":observation:" + observationKind + ":" + observedRoom
    : evidenceId + ":observation:" + observationKind;
```

So one evidence record held exactly one route mismatch, one recorder gap and one entity sighting —
**one witness each**. And `RecordEncounterObservations` loops over *every* present, non-downed crew
member, filing the mismatch and the gap with the **same** witness.

The second crew member's account therefore went one of two ways:

| Their account | Old behaviour |
|---|---|
| **identical facts** | `CompanyActionResult.Existing()` — merged into the first, witness never recorded |
| **different facts** | `CompanyActionResult.Refused("RR_Company_ReceiptMismatch")` — **thrown away** |

And the site tick **ignores the result** either way, so a contradiction between two crew standing in
one room left no trace anywhere in the save.

`RR_Request_ReportADisagreement` asks a `Testify` route for `<count>2</count>` on distortion logs.
Since `LivingWitnessCount("distortion")` could return at most **one per evidence record**, that
request was only ever satisfiable **across two separate coordinates** — never by an actual
disagreement, which is the thing it is named after.

**The contradiction was already being computed. It was being discarded as a receipt mismatch.**

---

## What was built

### An account is a saved thing now

`WitnessAccountRecord` holds who said it, where they were standing, what they place the marker at,
when, and **whether it agrees with the filed fact**. Agreement is corroboration; disagreement is a
dispute. Neither is discarded.

```csharp
bool agrees = prior.SameFact(kind, roomIndex, referencedRoomIndex, markerNumber, witnessRoom.index);
bool added = prior.AddAccount(witness, witnessRoom.index, referencedRoomIndex,
    markerNumber, Find.TickManager.TicksGame, agrees);
return added ? CompanyActionResult.Applied() : CompanyActionResult.Existing();
```

`SameFact` now decides **what kind** of account it is, not whether one exists.

### A dispute counts as testimony

`LivingWitnessCount` counts the filed witness **plus every account's witness**, alive and employed,
**without filtering on agreement**.

That last part is deliberate and it is the design decision in this checkpoint. Somebody was there
and said something. Filtering disputes out would make a disagreement *reduce* the witness count —
so the request named *"report a disagreement"* would get harder the moment a disagreement happened.

### One person is one account

A crew standing still ticks **every fifteen ticks**. `AddAccount` refuses any witness already on the
record, **including the one who filed the fact** — otherwise the filer corroborates themselves, the
list grows without bound, and a `Testify` route pays out on one person's word repeated.

`IsValidFor` asserts it again as a backstop: duplicate witness load ids make the record invalid.

### Three places a new saved field could have rotted silently

`EvidenceAnalysisReport` freezes a snapshot of the observations and `IsValidFor` compares that
snapshot against the live record using `SameSnapshot`. A saved field those two do not know about is
invisible until it matters:

| Threaded through | What it prevents |
|---|---|
| `SameSnapshot` → `SameAccounts` | a frozen report comparing **equal** to a record that has since gained a dispute |
| `SnapshotCopy` → deep copy of each account | the frozen report **aliasing** the live list and changing under it |
| `IsValidFor` → validate each account, reject duplicate speakers | an invalid account travelling inside a report that validates |

Accounts are compared **in order**, not as a set. Order-insensitive comparison would hide reordered
testimony, and reordering testimony is the kind of thing this record exists to make impossible.

### No schema version bump, deliberately

`observationSchemaVersion` exists to distinguish *"booleans that predate structured observations"*,
and its own comment says **never synthesize rows from them**. An old save has **no accounts**, and
that is *true of it* — nobody was recording them. An empty list needs no version to be honest, so
the constant stays at 1 and the collection loads as empty rather than null.

### The player can see it, which is the whole difference from discarding it

- **`RR_Event_AccountsDisagree`** fires **once**, when a dispute first opens, compared across the
  recording call because the result is ignored there. Invariant 28 wants every rule learnable, and a
  contradiction the company never mentions is not learnable.
- The evidence readout names every account: **`RR_UI_AccountAgrees`** and
  **`RR_UI_AccountDisagrees`**, each with who, when, and what room and marker they place it at.

The event string says the readout names them. **It was written after the readout existed**, not
before — a string promising a screen that does not exist is a lie with a translation key.

---

## The register was consulted, and it shaped the design

`use RR-EVD` and `use RR-STA` — the latter being the largest trace at **149 rows**. Three
instructions applied:

| Instruction | How it landed |
|---|---|
| *"Keep custody, casework, and interview goals reachable through vanilla prisoner controls"* | **No prisoner mechanics were touched.** These are employed staff giving accounts; nothing detains anybody |
| *"leave native social-fight logic intact and keep Rimrooms staff/case records separate"* | A dispute is a row on an evidence record. **No thought, mood or opinion is written**, so two crew who disagree do not start a social fight |
| *"Keep the company's evaluation based on actual pawn traits, skills, and relationships"* | The record stores **who said what**, and nothing invents a reliability stat RimWorld does not have. Which account the company files is the first one, and resolving the dispute is a player decision — that is the next checkpoint |

---

## What this deliberately does not do yet

**Nothing resolves a dispute.** The accounts sit on the record, the readout names them, and the
analysis reports them. The **interview** — `TODO.md` item *"Add analyze/interview/compare/review
workflows"*, which grep confirmed ships analysis and not interview — is the next checkpoint, and it
is the thing that lets a branch decide which account to file.

That is stated here rather than implied, because a dispute with no resolution path would otherwise
look like the kind of dead end this project keeps finding. **It is not one**: the request that asks
for two accounts is satisfied by the accounts existing, not by resolving them.

---

## The proof, fault-planted six ways

`.local/register/proof-contradictory-accounts.py` — the **twenty-third** — asserts **29 claims**
across seven groups.

| Planted fault | Exit | Caught |
|---|---|---|
| the old receipt-mismatch refusal comes back | 1 | ✓ |
| a disagreement stops counting as testimony | 1 | ✓ |
| the duplicate-witness guard is removed | 1 | ✓ |
| **the analysis snapshot stops comparing accounts** | 1 | ✓ |
| **the snapshot aliases the live account list** | 1 | ✓ |
| the site tick stops telling the player | 1 | ✓ |
| *restored* | **0** | — |

The two in bold are the silent kind. Neither changes any observable behaviour until a report is
frozen and the record then gains a dispute, at which point the report quietly agrees with a record
it no longer matches. **A fault plant is the only way to know a claim about those is real.**

---

## Receipts

| | |
|---|---|
| Version | 0.12.25-dev |
| Build | **174 C# files, 86 package files**, **0 warnings, 0 errors** |
| Assembly | `23D01F47CBECAB5D810E3FB3418D17AAFD0F3FF0D3A8903B1398D8CB30736DBE`, identical across two clean rebuilds |
| New gameplay content | **none.** One saved record type, three keyed strings |
| Save break | **none.** Additive collection, no version bump, empty on an old save |
| Register | `use RR-EVD` and `use RR-STA` (149 rows); three instructions applied |
| Checkers | **nine**, all passing |
| Proofs | **twenty-three**, all exiting zero |
| Planted faults caught | **6 of 6** |
| Game launched | **no.** Nobody has ever disagreed about anything in this mod |
