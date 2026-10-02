# A locked door said nothing — 0.12.78-dev

**Date:** 2026-10-01
**Assembly SHA-256:** `80A40D4655E2D6AF1A7CD3861F341431CD6D8C2FCCE7265FD4487D94BF92F759`

---

## What the owner reported, from a running game

> *"if i use approach gate and dispach to coordinate it says no book, i have no books... and if i
> try directly clicking a pawn on it it mentions a bunch of shit about the power not being enough
> reservers. look at the game and dont give me shit the api mod is not working make it work look
> at the running game look at those messages look at the logs wtf!"*

Two blockers, one of them mis-reported by the game's own text.

---

## The bridge was working; the instrument was incomplete

`[RimBridge] GABP server running standalone on port 5174` and a bridge token were **both in the
log**. Four wrong ports had been probed over plain HTTP. GABP is a framed protocol and
`tools/qa/rimbridge_readonly.py` already spoke it.

**What was genuinely missing is what was asked for.** The read allowlist held five selectors —
ping, status, game, mods, logs — and **not one read a message**. Five parameterless reads added
(messages, alerts, letters, selection, colonists), plus a bounded cell-rect read and camera state.

Still read-only. It still never discovers, starts, configures or controls a process.

---

## The live gate answered everything in one inspect string

```
Door locked
Power needed: 50 W
Grid excess: 1185 W (533 Wd stored)
Calibrated
Operator on station: Gee
Linked battery charge: 533.13/2400.00 watt-days
Charge needed for normal window plus emergency return: 49.59 watt-days
Opening time: 7075 in-game minutes remaining
Status: Normal
```

| Reading | What it settles |
|---|---|
| **2400 watt-days capacity** | four batteries summed — the previous checkpoint's net-wide fix is live |
| **533 stored vs 49.59 needed** | **power was never the problem** |
| **`Door locked`** | **the whole blocker** |
| Opening time remaining | the connection was already open |

The "bunch of shit about power" is the **inspect readout**, not a refusal.

---

## Defect one: a locked door refused in silence

`OrderCrossing` validated that the **approach cell** was standable and reachable. That cell is on
the **near** side. Nothing asked whether the door itself would open.

So a crew was ordered somewhere they could reach, through something they could not pass, with no
reason given.

`DoorBlockerKey` asks through Core's **`Building_Door.PawnCanOpen`**, which is `public virtual`.
The owner's gate is a `DoorsExpanded.Building_DoorRemote` — that mod replaces Core's `Autodoor`
thingClass — so its remote-lock override answers for itself and **nothing here names that mod or
references its assembly.** That is register row 77's own disposition.

A held-open or already-open door is never refused; neither needs permission.

---

## Defect two: no start shipped the record book

`ExpeditionCargo.RecordBooksRequired` is **1** of Core's `TextBook`.

| Start | Fixtures | Books |
|---|---|---|
| Laboratory | 112 across 17 types | **0** |
| Store | 27 | **0** |
| Solo | 0 | **0** |

The recorder was folded into the book at 0.12.24-dev and **the stock was never updated.** So the
first dispatch refused on every fresh start, forever.

The laboratory carries **two** now — one to take, one in reserve.

### And the starts that begin with nothing get them sent

`RecordBookDelivery` is **deterministic, not an incident** — the clean-up team's reasoning: *a
promise must not be at the mercy of a dice roll*.

| Condition | Why |
|---|---|
| corporation contact | nothing arrives from a corporation that has not heard of this branch |
| a **calibrated** gate | the work this rewards is done; before that a book has nothing to use it on |
| **no book anywhere the branch can reach** | a floor, a shelf, or a pack on either side of an open connection |

That last test is what stops it being a tap. **It can fire again if a book is lost, and never
while one still exists.**

### The quest half already worked

`RequestLine.cs` and `RimroomsRequestDef.cs` contain **no scenario id at all**, and the first two
tutorial requests are *power the gate* and *assemble and calibrate*. For a start with no facility
that **is** build-a-gate-and-go-through-it.

Asserted now rather than assumed, with a **negative** claim: a positive one listing three
scenarios would pass while a fourth was quietly excluded.

---

## Two published claims that were wrong

Both the same mistake: **comparing counts without reading footprints.**

| Claimed | True |
|---|---|
| *"you hand-laid ~100 conduits; the start wires almost nothing"* | **17 runs** were compared to **191 cells**. Expanded, the runs are **205**; live is 191 + 14 hidden = **205**. Exact match — none were added |
| *"you added 10 shelves"* | a shelf is 1×2. **19 live vs 28 authored — nine removed** |

Same shape as the grave footprint caught earlier the same day by reading Core's `<size>`. **The
second time it was not caught before it reached the owner.**

---

## What the owner actually changed

Facility origin solved at **(120, 120)** from three single-instance devices; every multi-cell
device compared against Core's own `<size>`.

**Exactly as authored:** conduits, ballistic glass, generators, machining table, smithy, research
benches, glow pods. **Nothing was moved**, including the comms console and bench repositioned at
0.12.74-dev.

**Every delta is fewer**, consistent with deconstruction: nine shelves, five lamps, three beds,
two stools, two tables, one battery, one comms console, one stove, one heater.

**One door added, at facility-relative (51, 24)** — the compound's east perimeter wall at the dead
end of the service corridor the 42-cell conduit run follows. **No authored door was missing.** It
is authored now.

---

## Verification

**`proof-corporate-contact.py` had never been planted against** — one of the oldest proofs in the
battery, and nothing had tested whether its claims could fail. That is the same shape as the
defect beside it. Suite **twenty-one**, 12 of 12.

The new claims caught two of their own defects before shipping:

- a door claim that asserted the **call** and not the **act**, defeated by `if (false)` —
  **twelfth instance of machinery-not-behaviour**,
- a plant that tested a mod name in a **comment** the proof strips, so it tested nothing.

```
16 checkers pass        49 proofs hold        771 plant anchors findable
212 C# files            92 package files      0 warnings, 0 errors
```
