# The recorder became the book — 0.12.24-dev, 2026-09-29

**Dated record.** Never rewritten. Closes the def half of invariant 10, and with it the last of the
four field-gear replacements.

---

## The answer was written down fourteen checkpoints ago

The owner's decision this session, asked at the fork and answered in the same exchange:

> *"Fold it into the record book crews already carry"*

The 0.9.9-dev plan had already said the same thing, in a table of four answers:

> **Field recorder** | **the book** | One Core `TextBook`: carried in blank, written in the field,
> carried home as the evidence. **The recorder and the record stop being two things that can get
> separated.**

Three of those four shipped — the beacon retired (0.9.9-dev), the survey tag became a `GlowPod`
(0.10.7-dev), the sealed case became a designated archive `Shelf` (0.10.9-dev). **The recorder sat
for fourteen checkpoints with its answer already recorded.** Nothing was blocking it; no proof
asserted anything about it, which is exactly how a decided piece of work stays undone.

`docs/implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md` row 40 went further and specified the
implementation:

> *"A Core written-field-log route may use a native Book with a clearly described manual observation
> action... Preserve item loss, custody, mass and observation prerequisites... Rewrite kit validation
> and observation guards before deleting the Def."*

**That is what shipped, including the last clause — and the Def was not deleted.**

---

## The register was consulted, and it had something to say

The LAW requires it. Queried by `trace`, which is the column that names the Rimrooms feature a row
bears on: **`RR-EVD` (31 rows)** and **`RR-EXP` (74 rows)**.

Three instructions applied, and all three point the same way:

| Row | Instruction | How it landed |
|---|---|---|
| **[26] Adaptive Simple Storage** | *"Keep custody and evidence records separate from the containers"* | The record is a carried book. No container is required for it to exist, and none owns it |
| the materials and cargo family | *"Preserve each mod's normal material and weight behavior; add only a Backrooms cargo manifest and appraisal layer"* | The loadout reads `GetStatValue(StatDefOf.Mass)` off the item. A Core book weighs what Core says — **0.50**, where our recorder declared **1.6** |
| **[4] Core** | *"do not make a DLC feature the sole route through the campaign"* | `TextBook` is Core, in `Data/Core/Defs/Books/BookDefs.xml`. No DLC involved |

A register search for `book` returns **zero rows**, so no mod in the 294 is recorded as touching
Core's books. Nothing vetoed this and nothing else applied.

### The register's guidance had been unreachable from the tool

The LAW says *"read the per-mod reviews it points at"*. `register-query.py row 4` printed this:

```
      card     : open card
```

**That is a hyperlink label.** Every real instruction — Backrooms Dependency, **Planned Use**,
**Integration Approach**, **Compatibility Watch**, FinalDisposition — lives in the register's
`#cards` section and in **294 review records on disk** under `docs/research/reviews/mods/`, and the
tool read none of it. A LAW that points at a document its own tool cannot open is a LAW satisfied by
reading four short columns and calling it consulted.

Two queries were added:

- **`card <id|text>`** — one mod's full card, every field, plus whether the review record it names
  is actually on disk.
- **`use <trace>`** — for every mod bearing on the feature being built, **how this mod is supposed
  to use it**. That is the question the LAW actually asks.

The three instructions in the table above came out of `use RR-EVD` and `use RR-EXP`. None of them
was visible before.

---

## What changed

### The kit is resolved, never named

`ExpeditionCargo` held `KitDefs = { "RR_FieldRecorder" }` and a parallel `KitCounts = { 1 }` — with
a comment on it warning that arrays disagreeing about their own length are a bug waiting to happen.
Both are gone. The kit is now one def, resolved through the predicate that already existed:

```csharp
internal static ThingDef RecordBookDef { get { return CompRouteEvidence.NativeCarrierDef; } }
```

`NativeCarrierDef` is strict where a def name is not: Core's own book, a `Book` subclass, carrying
**exactly one** of our comps, with `CompBook` and `CompQuality`. A def-name string would match
another mod's `TextBook` just as happily.

**And it can return null**, so both callers refuse visibly on null. A silent null here would make
the kit check pass for a crew carrying nothing — the same failure shape as
`Named<TerrainDef>("Carpet")` returning null while a `??` fallback made wood plank flooring in the
depth-1 yellow rooms look deliberate for months.

### Two gates that had never agreed now ask one question

| | Before | After |
|---|---|---|
| Surveying a room | the recorder **in an inventory** | the book **in a crew member's inventory** |
| Recording an observation | the book **anywhere on the map** | the book **in a crew member's inventory** |

`FirstSliceSiteComponent.HasItem(pawn, defName)` — a name match, and the last one — is replaced by
`CarriesRecordBook(pawn)`, delegating to `CompRouteEvidence.IsSupportedCarrier`. **A legacy
`RR_RouteRecording` still counts**, because a crew in an old save is holding one and has not stopped
being able to write.

### The observation was attributing itself to the wrong object

`TryFindFieldRecorder` searched the crew's inventories for a **second** object and credited the
observation to that. It was always redundant: by the time it ran, the caller had already established
that `record.item` is a bound route-evidence book held on this map.

So `TryFindRecordBook` credits **the record itself**, and requires it be in a crew member's
inventory. A book lying on the floor two rooms back is not being written in.

**The saved field names did not change.** `recorder`, `recorderLoadId`, `recorderCarrier` and
`recorderCarrierName` are what old saves contain, and renaming a saved field is a save break for a
cosmetic gain.

### The def stays, and that is the whole migration

**NO SAVE BREAK.** Saves made before the switch contain recorders in crew inventories and on the
floors of coordinates, and the owner's rule is explicit: *"Migration decision or declared
development-save break before removing any Def a saved Thing references."*

So it still loads, still weighs 1.6, still recovers from a failed site — `FailedSiteRecovery`
deliberately keeps naming it. Retirement is achieved entirely by removing every way to **get** one:

| Route | Disposition |
|---|---|
| `RR_MakeFieldRecorder` recipe | **retired with its whole file** — the abstract base had no other child |
| `1.6/Defs/ScenarioDefs/RR_Scenarios.xml` ×2 | both starts now grant `TextBook` |
| trade | `<tradeability>None</tradeability>`, overriding `ResourceBase`'s `Buyable` |
| the company catalogue | never carried one |
| its description | says plainly that it is superseded and no longer issued, built or bought |

Recipe retirement follows the precedent set three times in this repository already:
`RR_MakeReturnBeacon` (0.9.9-dev), `RR_MakeSurveyTags` (0.10.7-dev) and `RR_MakeEvidenceCase`
(0.10.9-dev) all left with their items.

---

## The replacement would have created a dead end, so it does not

Core gives books **`Flammability 1`** and **`DeteriorationRate 5`**, and sells `TextBook` only as
random outlander stock at **nought to two a visit**. A branch whose only record book burned would
have failed every future dispatch for ever, with no player-directed way to get another.

That is the same shape of defect as a way out with no marked anchor — found and fixed at 0.12.21-dev
— and it was **not** in the row, the plan, or the owner's answer. It came out of reading what Core
actually does with the object.

So `RR_Procurement_RecordBooks` joins the company catalogue, priced the way glow pods are priced and
for the same reason. Glow pods sit at **80×** market value where silver sits at **1000×**, because
*"a branch that cannot mark its own way back out files a great many more casualty reports."* The
company is buying its own paperwork; it does not charge a branch a fair market rate for the
privilege.

---

## The build caught my own XML

An em-dash habit put `--` inside an XML comment, which is illegal, and `BuildCommon.ps1` refused the
file before the compiler ever saw it. **Worth naming because the validation that caught it is not
one of the nine checkers** — it is the build's own XML parse, and it is the reason a malformed def
file has never shipped from here.

---

## The proof, fault-planted four ways

`.local/register/proof-record-book.py` — the **twenty-second** — asserts **28 claims** across six
groups: the def still loads, nothing grants it, the kit resolves strictly and refuses on null, both
gates ask one question, a lost book is recoverable, and the refusal reaches the player.

No previous proof mentioned `RR_FieldRecorder` at all. **That is why a decided piece of work could
sit undone for fourteen checkpoints and every sweep stay green.**

| Planted fault | Exit | Caught |
|---|---|---|
| a start grants a recorder again | 1 | ✓ |
| the crafting recipe comes back | 1 | ✓ |
| the recorder becomes tradeable again | 1 | ✓ |
| the site tick name-matches an item again | 1 | ✓ |
| *restored* | **0** | — |

Comments are stripped before every source claim. This change is documented at length **in the files
it changes**, and those comments name `RR_FieldRecorder` repeatedly while explaining why nothing
reads it — a naive search would be fooled in both directions, which invariant 130 exists because of.

---

## Receipts

| | |
|---|---|
| Version | 0.12.24-dev |
| Build | **174 C# files, 86 package files** (one fewer), **0 warnings, 0 errors** |
| Assembly | `B382E45C0ADF918FFF8BBAAC643C88DAB1B7CF8F0E9CDA74D60ABB22617030BE`, identical across **three** clean rebuilds |
| New gameplay content | **none.** One catalogue entry naming a Core def, and one def made untradeable |
| Gameplay art or audio shipped | **still zero** |
| Register | `trace RR-EVD` (31 rows) and `trace RR-EXP` (74 rows) read **through the new `use` query**; three instructions applied, all supporting |
| Checkers | **nine**, all passing |
| Proofs | **twenty-two**, all exiting zero |
| Planted faults caught | **4 of 4** |
| Save break | **none.** The def loads; the saved field names are untouched |
| Game launched | **no.** Every claim here is structural, and nobody has ever carried one of these books anywhere |
