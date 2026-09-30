# A gate read no damage at all — 0.12.38-dev

**Row closed:** 725 (machine subsystems — power reserves, calibration, stabilizers, monitoring,
emergency cutoff, cool-down, modules, repair, reliability). **It closes completely.**

No game was launched. Nothing here claims a gameplay, balance, performance or compatibility
result.

---

## 1. Seven of nine were already built, and were measured before anything was written

Row 725 lists nine subsystems. The row's own note claimed four were missing. Checking each
against the code found **seven already shipped** — the habit that has now closed nine rows this
session:

| Asked for | Already built as |
|---|---|
| power reserves | the bound battery, `ReturnReserveStoredWattDays`, the watt-day costs |
| calibration | `calibrated`, its work giver, its refusal, its readout |
| **stabilizers** | **`PortalWindowTier`** — a four-rung project ladder that multiplies the window and **stops the countdown entirely** at tier 4 |
| monitoring | the inspect readout, three gate alerts (0.10.5-dev), two containment alerts (0.12.35-dev) |
| emergency cutoff | `TriggerEmergencyCutoff`, the kill switch, and the containment procedure that calls it |
| cool-down | the opening clock and the return window |
| **modules** | **`GateEquipmentLinks`** — roles, `maxLinked`, single ownership across gates, built to *"reach fare and through walls"* with no distance or line-of-sight check |

The row said *"stabilizers, modules, repair and a reliability model"* were absent and *"confirmed
absent by grep"*. The grep was looking for the words. **Stabilizers and modules exist under
different names**, which is why the row stayed open for so long, and why the proof now asserts
both so nobody rebuilds them.

---

## 2. The real finding: a gate read no damage at all

Nothing in `CompRimroomsGate` looked at `HitPoints`. A gate could be shot to twelve per cent, set
on fire, and hit by a mortar, and it would still open a connection and hold it perfectly.
`calibrated` was lost only when the binding changed. **The machine the entire mod is built around
was the one building in the colony that damage did not affect.**

### The fix adds no mechanic

Damage below the threshold **loses calibration** — a state that already exists, already has a work
giver, already has a refusal and already reads in the inspect pane. So:

* a beaten-up gate refuses to open **with a reason the player can read**;
* fixing it is **Core's own repair work** — nothing here repairs anything, and the proof asserts
  that;
* bringing it back is **the calibration job that already existed**.

No new def, no new job, no new work giver.

The threshold is a **fraction** (half), not a hit-point count, because the profile contains mods
that change building health and armour and an absolute number would mean something different in
each of them. Half is generous enough that ordinary wear and a stray shot do not cost a
connection — it takes a real attack — which matters because losing calibration costs work to undo.

A live opening is ended through the **emergency path**, not just dropped. That is the difference
between a gate failing and a gate losing people: the emergency path is the one that starts the
return window.

### The seventh failure reason, added on purpose

`proof-areas-and-debrief.py` asserts the complete set of ways a gate can stop working. It was six,
asserted at 0.12.36-dev precisely so an addition has to be made deliberately. It is now seven, and
both proofs name the whole set.

**Row 98 is untouched.** Its claim is that ordinary map work near a gate cannot break it; this is a
change to the machine itself, and the proof still asserts that no reason anywhere in the class
reads an adjacent cell.

---

## 3. Reliability is a record, not a dice roll

The tempting reading of *"reliability"* is a failure chance that rises with use. That is wrong
here twice over. **Invariant 28 wants every rule learnable**, and a machine that sometimes fails
for no visible reason is the definition of unlearnable; and this mod's failures are all
deterministic and all named, which is what makes them fair. The proof asserts **no `Rand` call
anywhere** in the subsystem.

So reliability is **what actually happened**, counted per coordinate. `GateHistoryEntry` recorded
`times`, `firstTick` and `lastTick` and **nothing about how any of it went**, so the history could
not answer the one question a player would ask of it: *which of these addresses has been costing
me return windows.*

Three decisions worth recording:

* **Counted, not rated.** A stored percentage would be a second number that could disagree with
  the counts it came from. The rate is derived on read.
* **No data reads as no data.** `Reliability` returns **-1** when nothing has been recorded, and
  the surface says *"no trip to here has finished yet"* — because 0% and 100% would both be
  inventing a claim about a coordinate nobody has come back from.
* **The coordinate is remembered explicitly.** The history is most-recently-used first, so *"the
  first entry is the one we are connected to"* is true today and would be a silent lie the first
  time anything else recorded a connection between opening and closing. One saved string is
  cheaper than that bug.

It is filed from `CloseOpeningCore`, the one place an opening is torn down, **before `failureKey`
is cleared** — because that field *is* the emergency, and reading it after clearing would record
every trip as a success. That ordering is a planted fault.

---

## 4. Two proof weaknesses the plants found, and one in an older proof

**The plants caught two of my own claims being too weak**, both the same defect class:

1. *"the player is told"* checked that the letter key and the percentage **appeared** in the
   method. Replacing `Find.LetterStack.ReceiveLetter(` with `Noop(` left both arguments in place
   and the claim passing while nothing was sent. **A claim that searches for a string is not a
   claim about behaviour** — the same thing a fault plant caught at 0.12.33-dev. Tightened to the
   whole call.
2. *"the outcome is filed against the right coordinate"* checked that `historyCoordinateId`
   appeared. It appears three times in that method, so removing the actual comparison left the
   claim passing while every outcome filed against the first entry. Tightened to the comparison.

**And the older proof had a scope hole.** `proof-areas-and-debrief.py` enumerated the gate's
failure reasons from `CompRimroomsGate.cs` — and **kept passing** when the seventh reason was
added, because the new one lives in `GateIntegrity.cs`, another file of the same partial class. The
count was right and the *scope* was wrong: a claim that reads as *"these are all the ways a gate
can stop working"* was really *"these are the ways one file can stop it"*. It now globs every
`Gate/*.cs`, so a new file of the class is covered the moment it exists. A plant that adds an
eighth reason in the new file now fails both proofs.

---

## 5. Register rows read before building

`register-query.py family facilities` (swept) and `trace RR-GATE`. The facilities family's standing
position is that this mod adds no construction or power mechanic of its own and leaves native
building alone. Honoured exactly: **the damage read is `HitPoints` against `MaxHitPoints`, both
Core's**, and the repair is Core's. A mod that changes building health, armour or repair rates
changes Core's numbers, and the threshold here reads whatever they become because it is a fraction.

Nothing is patched, nothing is required, and every mod may be absent.

---

## 6. Files

**New:** `src/.../Gate/GateIntegrity.cs`, `.local/register/proof-gate-subsystems.py`, this record.

**Edited:** `src/.../Gate/CompRimroomsGate.cs` (the tick, the opening refusal, the readout, the
outcome filing), `src/.../Gate/GateConnectionHistory.cs` (outcome counts, the derived rate, the
remembered coordinate, the reliability row),
`1.6/Languages/English/Keyed/RR_Gate.xml`, `RR_GateHistory.xml`,
`.local/register/proof-areas-and-debrief.py` (scope widened to the whole partial class),
`CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `docs/NOW.md`, `docs/TODO.md`,
`docs/FINALIZED.md`.

**No new gameplay content.** Seven keyed strings; no `ThingDef`, `JobDef`, `WorkGiverDef`, recipe,
bench, item, texture or sound.

## 7. Verification

* **Build 0.12.38-dev** — 190 C# files, 87 package files, **0 warnings, 0 errors**.
* **Assembly reproduced across two clean rebuilds.**
* **Twelve checkers pass. Thirty-five proofs exit zero.**
* **18 of 18 planted faults caught**, after two of my own claims were found too weak by the
  plants and tightened.
* **No game was launched.** Every statement here is structural.
