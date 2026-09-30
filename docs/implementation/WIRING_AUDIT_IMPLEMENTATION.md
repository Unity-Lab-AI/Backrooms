# Everything is read by something — 0.12.32-dev, 2026-09-29

**Dated record.** Never rewritten. The **eleventh checker**, built against this project's most
expensive defect class, and the audit it was built out of.

---

## The owner asked for it, and the evidence was already on the table

> *"get to finishing it all and making sure its all wired up"*

Four times, something in this mod was authored and then read by nothing:

| When | What |
|---|---|
| **0.11.7-dev** | five `RR_*Staff` PawnKinds, authored and read by nothing |
| **0.11.8-dev** | no `IncidentDef` existed at all, so the storyteller did not know the mod was there |
| **0.12.11-dev** | **`RimroomsRequestDef`, `RequestRoutes` and seven authored requests were read by zero lines of C#.** The whole campaign was written and unreachable, and the chart recorded both steps as *done* |
| **0.12.30-dev** | **`EstablishCorporationContact()` had no caller**, which left two of the three shipped starts with no campaign at all, permanently |

**Every one of those passed every checker and every proof of its day.** Nothing was wrong with any
individual file. The wiring between them was missing and no tool looked at wiring.

---

## What "wired" means, and getting the rule wrong twice

### Defs

A def is wired when any **one** of three genuinely different things is true:

1. its `defName` appears in our C# — **resolved by name**;
2. its **type** is enumerated by our C# (`DefDatabase<ThatType>`) or is a type **RimWorld itself**
   consumes — **consumed by type**, which is how most content defs work and why they never appear
   in code by name;
3. its `defName` appears in **another def's XML** — a **cross-reference**.

My first attempt used only rule 1 and reported **106 dangling defs**. Almost all were content defs
consumed by type: the generator picks an inhabitant from `DefDatabase<RimroomsInhabitantDef>`, and
RimWorld resolves a `FactionDef` and a `ScenarioDef` without help.

Adding rule 2 got it to **3 dangling** — the three `RimroomsStartDef`s. **Those are not dangling
either.** `ScenPart_RimroomsStart` declares `public RimroomsStartDef startDef;` and each
`ScenarioDef` names one: `<startDef>RR_AsyncIndustriesStart</startDef>`. That is rule 3, and
leaving it out was my rule being wrong, not the code.

**With all three: 258 defs declared, zero dangling.** The def side was already fully wired.

### Actions

A `public` method returning `CompanyActionResult` is this mod's entire player-facing verb surface —
102 of them. One is wired when something other than its own declaration calls it.

That rule reproduces the `EstablishCorporationContact` defect exactly, and found **two more.**

---

## The two it found, resolved on their own merits

### `RenameCompany` — retired

It was **not a missing feature. It was a second path to a change that already works.**

`Dialog_RenameCompany` uses Core's `Dialog_Rename<T>`, whose accept sets `RenamableLabel`, whose
setter calls **the same `TrySetCompanyName`** — and its `OnRenamed` calls `NoteRenamed()`, which
records **the same `RR_Event_CompanyRenamed` event.** Identical validation, identical record, one of
them unreachable.

**Two entry points to one state change is how two validations drift apart**, and the one nobody uses
is the one that drifts without anybody noticing. So it is gone, with the reasoning left in its place.

### `TriggerEmergencyCutoff` — wired

This one **is** a real capability with no surface, and it is not a duplicate of the kill switch:

| | |
|---|---|
| **kill switch** | a **persistent thrown state**. The gate stays disabled until you clear it |
| **cutoff** | **ends this opening** and starts the emergency return window, and **the gate stays usable** |

The second is the safety action a player wants while watching a crew get into trouble: *end it now,
keep the gate for next time.* `EnterEmergency` has seven automatic callers — power lost, operator
lost, window expired, energy debit, kill switch — so the mechanism was sound and only the
**deliberate** version was unreachable.

It is now a gizmo, shown only while an opening is running and not already in emergency.

---

## The checker

`tools/check-wiring.py`, the eleventh. Fault-planted both ways:

| Planted fault | Exit | Caught |
|---|---|---|
| an action method loses its only caller | 1 | ✓ |
| a new unreferenced def appears | 1 | ✓ |
| *restored* | **0** | — |

The `CORE_CONSUMED` list is kept short and explicit, and the file says why: **a type added there
without a reason is a hole in the check.** That is the failure mode of an allow-list, and naming it
in the file is the only defence available.

---

## Receipts

| | |
|---|---|
| Version | 0.12.32-dev |
| Build | **179 C# files, 87 package files**, **0 warnings, 0 errors** |
| Assembly | `B86715C2EBD0300B0888F9C613EC3645AD9CEAAEA314FD45ED55230971D848CD`, identical across two clean rebuilds |
| Defs audited | **258**, dangling: **0** |
| Action methods audited | **102**, unwired: **2**, now **0** |
| Methods retired | **1**, as a duplicate of a live path |
| Capabilities given a surface | **1** |
| Checkers | **ELEVEN**, all passing |
| Proofs | **twenty-eight**, all exiting zero |
| Planted faults caught | **2 of 2** |
| Game launched | **no.** Wiring is exactly the kind of thing a launch would have found for me |
