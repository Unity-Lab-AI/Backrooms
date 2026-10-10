# -*- coding: utf-8 -*-
"""Documents for 0.12.78-dev."""
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HASH = sys.argv[1] if len(sys.argv) > 1 else None
if not HASH or len(HASH) != 64:
    print("usage: docs-1278.py <assembly sha256>")
    raise SystemExit(1)

CHANGELOG = os.path.join(REPO, "CHANGELOG.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
TODO = os.path.join(REPO, "docs", "TODO.md")

entry = u"""# Changelog

## 0.12.78-dev - 2026-10-01 - a locked door said nothing, and no start shipped the book

- **A locked gate refused every crossing in silence.** Ordering somebody through checked that the
  cell on the near side was standable and reachable, and never asked whether the door would open.
  It now says so: *"That gate's door is locked, so nobody can walk through it."*
- **No start shipped the record book every expedition requires.** The laboratory spawned 112
  fixtures and not one book, so the first dispatch always refused. It carries two now - one to
  take, one in reserve.
- **And for the starts that begin with nothing, the corporation sends them.** Build and calibrate
  a gate with no book anywhere and blank record books arrive. It will send again if you lose
  them, and never while you still have one.
- **The quest to go through your own gate already reached every start** and is now asserted rather
  than assumed - the request line has no scenario check anywhere in it, and its first two requests
  are power the gate and assemble and calibrate it.
- **One door the facility was missing.** The east-west service corridor was walled off at its east
  end, with no way out of the compound on that side.

Full record: [a locked door said nothing](docs/implementation/CROSSING_AND_BOOK_IMPLEMENTATION.md).
No gameplay, balance, performance or compatibility result is claimed.

"""
text = io.open(CHANGELOG, encoding="utf-8").read()
io.open(CHANGELOG, "w", encoding="utf-8", newline="").write(
    entry + text[len(u"# Changelog\n"):].lstrip(u"\n"))
print("CHANGELOG written")

record = u"""
---

## Session 2026-10-01 - the api, a locked door, and a start that could not run its own first job (0.12.78-dev)

**Verbatim user quotes:** *"if i use approach gate and dispach to coordinate it says no book, i
have no books... and if i try directly clicking a pawn on it it mentions a bunch of shit about the
power not being enough reservers. look at the game and dont give me shit the api mod is not working
make it work look at the running game look at those messages look at the logs wtf!"*; *"fix the api
u fuck"*; *"and check where i had to move stuff and where i had to add a door and add power conduit
and fix the spawn to have current lsaayout of devices generators batteries and the like"*; *"and you
fixed both those problems with sending someone through dirrectly and whith sending them through
with the operations tab?"*; *"make sure the other scenerios properly get the book in a drop when
they need it and start the quest to go through their built gate"*.

**Files touched:** `Company/RecordBookDelivery.cs` (new), `Portals/PortalTravelService.cs`,
`Company/CampaignServices.cs`, `Company/RimroomsCampaignComponent.cs`, `Keyed/RR_Portals.xml`,
`Keyed/RR_Requests.xml`, `build-async-facility.py`, `RR_Starts.xml`,
`tools/qa/rimbridge_readonly.py`, `.local/qa/scan-facility.py` (new),
`proof-gate-circuit.py`, `proof-starts.py`, `proof-corporate-contact.py`,
`plant-gate-circuit.py`, `plant-startplacement.py`,
`plant-contact-and-book.py` (new, suite TWENTY-ONE).

**Mod register.** Row **77, Doors Expanded**, applied directly and for the first time in anger:
the owner's gate is a `DoorsExpanded.Building_DoorRemote`, because that mod replaces Core's
`Autodoor` thingClass. The fix goes through Core's `Building_Door.PawnCanOpen`, which is public and
virtual, so **nothing names that mod or references its assembly** — the register's own disposition
for that row.

### THE API WAS WORKING AND I WAS LOOKING IN THE WRONG PLACE

Owner: *"the api mod is not working make it work"*. **It was running the whole time.**
`[RimBridge] GABP server running standalone on port 5174` and a bridge token were both in the log.
I had probed 8765, 8080, 9000 and 5000 over plain HTTP with no token. GABP is a framed protocol and
`tools/qa/rimbridge_readonly.py` already spoke it.

**What was genuinely missing is what the owner asked for.** The client's fixed allowlist had five
selectors — ping, status, game, mods, logs — and **not one read a message**. So *"look at those
messages"* was not answerable by the instrument. Five parameterless reads added (messages, alerts,
letters, selection, colonists) plus a bounded cell-rect read and camera state. Still read-only; it
still never discovers, starts, configures or controls a process.

### THE LIVE GATE ANSWERED EVERYTHING IN ONE INSPECT STRING

```
Door locked
Grid excess: 1185 W (533 Wd stored)
Calibrated | Operator on station: Gee
Linked battery charge: 533.13/2400.00 watt-days
Charge needed for normal window plus emergency return: 49.59 watt-days
Opening time: 7075 in-game minutes remaining | Status: Normal
```

**2400 watt-days of capacity is four batteries summed**, so the previous checkpoint's net-wide fix
was live and working. **533 stored against 49.59 needed** — power was never the problem. The
"bunch of shit about power" was the **inspect readout**, not a refusal.

**`Door locked` was the whole blocker**, and `OrderCrossing` never asked. It validated the
APPROACH cell — on the near side — so a crew was ordered somewhere they could reach, through
something they could not pass, with no reason given.

### I TOLD THE OWNER TWO THINGS THAT WERE WRONG

Both were the same mistake: **comparing counts without reading the footprints.**

| What I said | What was true |
|---|---|
| *"You hand-laid ~100 power conduits; the start wires almost nothing"* | I counted **17 runs** against **191 cells**. Expanded, the runs are **205 cells**, and live is **191 PowerConduit + 14 HiddenConduit = 205**. **Exact match.** The owner added none |
| *"You added 10 shelves"* | A shelf is 1x2. **19 live against 28 authored — nine were removed** |

Same shape as the grave footprint earlier in the day, which was caught by reading Core's `<size>`
rather than assuming. **The second time it was not caught, it was published to the owner.**

### WHAT THE OWNER ACTUALLY CHANGED, MEASURED

Facility origin solved at **(120, 120)** from three single-instance devices. Every multi-cell
device compared against Core's own `<size>`.

**Conduits, ballistic glass, generators, the machining table, the smithy, the research benches and
the glow pods are all exactly as authored.** Nothing was moved — including the comms console and
machining bench repositioned at 0.12.74-dev. Everything with a delta is **fewer**: nine shelves,
five lamps, three beds, two stools, two tables, one battery, one comms console, one stove, one
heater.

**One door, at facility-relative (51, 24)** — the compound's **east perimeter wall**, at the dead
end of the service corridor the 42-cell conduit run follows. **No authored door was missing.** It
is authored now.

### THE BOOK, AND WHY NO CLAIM CAUGHT IT

`ExpeditionCargo.RecordBooksRequired` is **1** of Core's `TextBook`. The laboratory start spawned
**112 fixtures across 17 types and none of them a book**, so `RR_Exp_MissingRecordBook` refused the
first dispatch on every fresh lab start.

The recorder was folded into the book at 0.12.24-dev and **the stock was never updated.** Nothing
in the battery asserted that a start ships what its own systems require, so the claim added for it
is **derived** — it reads the required count and the carrier def out of the source. A hand-typed
item list is how the original change slipped past.

### AND THE STARTS THAT BEGIN WITH NOTHING GET THEM SENT

Owner: *"make sure the other scenerios properly get the book in a drop when they need it"*. The
Store spawns 27 fixtures and no book; the solo start spawns nothing at all.

`RecordBookDelivery` is **deterministic, not an incident** — same reasoning as the clean-up team,
*"a promise must not be at the mercy of a dice roll"*. It fires on corporation contact, a
**calibrated** gate, and **no book anywhere the branch can reach**: a floor, a shelf, or a pack on
either side of an open connection. That last test is what stops it being a tap — it can fire again
if a book is lost and never while one still exists.

**The quest half already worked and is now asserted rather than assumed.** `RequestLine.cs` and
`RimroomsRequestDef.cs` contain **no scenario id at all**, and the claim for it is negative and
derived: a positive claim listing three scenarios would pass while a fourth was quietly excluded.

### `proof-corporate-contact.py` HAD NEVER BEEN PLANTED AGAINST

One of the oldest proofs in the battery, and **no suite verified that any of its claims could
fail** — which is exactly the shape of the defect beside it. Suite **twenty-one**, 12 of 12.

And the new claims caught two of their own defects before shipping: a door claim that asserted the
**call** and not the **act**, which a plant defeated with `if (false)` (**twelfth instance of
machinery-not-behaviour**), and a plant that tested a mod name in a **comment** the proof strips.

**212 C# files, 92 package files**, zero warnings, zero errors. Assembly SHA-256
`__HASH__`, measured after the version bump, reproduced by two clean rebuilds.
**Sixteen checkers pass, FORTY-NINE proofs hold, 12 of 12 in the new suite, 771 plant anchors
findable.**
"""
record = record.replace(u"__HASH__", HASH)
text = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(text + record)
if record not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"---\n\n## TOMBSTONES"
ENTRY = u"""---

## The crossing, the book, and the live read - 2026-10-01 (0.12.78-dev) - DONE

Owner, verbatim:

> **"if i use approach gate and dispach to coordinate it says no book, i have no books... and if i
> try directly clicking a pawn on it it mentions a bunch of shit about the power not being enough
> reservers. look at the game and dont give me shit the api mod is not working make it work look at
> the running game look at those messages look at the logs wtf!"**

> **"fix the api u fuck"**

> **"and check where i had to move stuff and where i had to add a door and add power conduit and fix
> the spawn to have current lsaayout of devices generators batteries and the like"**

> **"and you fixed both those problems with sending someone through dirrectly and whith sending them
> through with the operations tab?"**

> **"make sure the other scenerios properly get the book in a drop when they need it and start the
> quest to go through their built gate"**

- [x] **"the api mod is not working make it work"** - **it was running the whole time**, port 5174
  with a token, both in the log. I had probed four wrong ports over plain HTTP. **What was genuinely
  missing** is that the read allowlist had no selector for messages, so *"look at those messages"*
  was unanswerable by the instrument. Five parameterless reads added, plus a bounded cell-rect read
  and camera state
- [x] **"it says no book, i have no books"** - every dispatch needs one Core `TextBook`; the start
  spawned **112 fixtures across 17 types and no book**. Two go on the archive shelves
- [x] **"it mentions a bunch of shit about the power not being enough reservers"** - the live gate
  reads **533 stored against 49.59 needed**. Power was never the problem; that is the **inspect
  readout**, not a refusal
- [x] **"clicking on the portal and trying to send them through not working"** - **`Door locked`**.
  `OrderCrossing` validated the approach cell on the near side and never asked whether the door
  would open
- [x] **"and you fixed both those problems"** - **answered honestly: no, not at the time.** Both
  were diagnosed and neither was fixed until after that question
- [x] **"where i had to add a door"** - exactly one, at facility-relative **(51, 24)**, the
  compound's east perimeter wall at the dead end of the service corridor. **No authored door was
  missing**
- [x] **"and add power conduit"** - **the owner added none.** I claimed they had hand-laid about a
  hundred; I had counted **17 runs against 191 cells**. Expanded the runs are **205**, and live is
  **205**. A published claim that was wrong
- [x] **"where i had to move stuff"** - **nothing was moved.** Conduits, glass, generators, bench,
  smithy, research benches and glow pods are all exactly as authored. Every delta is furniture
  deconstructed
- [x] **"make sure the other scenerios properly get the book in a drop when they need it"** -
  `RecordBookDelivery`, deterministic, on a calibrated gate with no book anywhere the branch can
  reach
- [x] **"and start the quest to go through their built gate"** - **already worked**, and is asserted
  now rather than assumed: no scenario id anywhere in the request line, first two requests are power
  the gate and assemble and calibrate
"""
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(
    todo.replace(ANCHOR, ENTRY + u"\n" + ANCHOR, 1))
print("TODO recorded and closed")
