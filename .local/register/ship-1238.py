# -*- coding: utf-8 -*-
"""Ledger, queue and NOW.md for 0.12.38-dev. Row 725 closes completely."""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sub(rel, old, new):
    path = os.path.join(REPO, rel)
    s = io.open(path, encoding="utf-8").read()
    assert old in s, "%s: anchor missing %r" % (rel, old[:80])
    assert s.count(old) == 1, "%s: anchor not unique %r" % (rel, old[:80])
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("updated %s" % rel)


sub("CHANGELOG.md", u"## 0.12.37-dev", u"""## 0.12.38-dev - 2026-09-29 - a shot-up gate will not hold a connection

- **Damage to a gate now matters.** A gate could be shot to twelve per cent and still open a connection and hold it perfectly. Below half condition it loses its calibration, refuses to open, and says why - repair it with ordinary construction work and calibrate it again, exactly as you did the first time. If a connection is live when it goes, the crews get their return window rather than being cut off.
- **Every address you have dialled now records how the trips went.** How many came back clean, how many ended in an emergency, and the rate - shown when you pick that address out of the gate's history, which is where it helps. An address nobody has come back from yet says so rather than showing a made-up figure.
- **Nothing about this is random.** A gate fails for a reason you can read, every time.

Full record: [a gate read no damage at all](docs/implementation/GATE_SUBSYSTEMS_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.37-dev""")

sub("docs/FINALIZED.md", u"## Completed sessions", u"""## Session 2026-09-29 - a gate read no damage at all (0.12.38-dev)

**Verbatim user quote:** *"okay 13 left to do lets keep at it"*

### What shipped

Row 725 closes completely. Seven of its nine subsystems were already built; repair and reliability were the genuine gaps.

### Files touched

`src/.../Gate/GateIntegrity.cs` **new**, `src/.../Gate/CompRimroomsGate.cs`, `src/.../Gate/GateConnectionHistory.cs`, `1.6/Languages/English/Keyed/RR_Gate.xml`, `RR_GateHistory.xml`, `.local/register/proof-gate-subsystems.py` **new**, `.local/register/proof-areas-and-debrief.py`, `docs/implementation/GATE_SUBSYSTEMS_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **SEVEN OF NINE WERE ALREADY BUILT, and the row's own grep was looking for the wrong words.** The row said *"stabilizers, modules, repair and a reliability model"* were *"confirmed absent by grep"*. **Stabilizers exist as `PortalWindowTier`** - a four-rung project ladder that multiplies the opening window and **stops the countdown entirely** at tier 4 - and **modules exist as `GateEquipmentLinks`**, with roles, `maxLinked` and single ownership across gates, built to the owner's *"reach fare and through walls"* direction. Both are asserted by the proof now so nobody rebuilds them. **Ninth row this session that turned out already done or answered elsewhere.**
- **THE REAL FINDING: A GATE READ NO DAMAGE AT ALL.** Nothing in `CompRimroomsGate` looked at `HitPoints`. A gate could be shot to twelve per cent, set on fire and hit by a mortar and would still open a connection and hold it perfectly; `calibrated` was lost only when the binding changed. **The machine the entire mod is built around was the one building in the colony that damage did not affect.**
- **The fix adds no mechanic.** Damage below the threshold **loses calibration** - a state that already exists with a work giver, a refusal and a readout. So a beaten-up gate refuses to open with a readable reason, fixing it is **Core's own repair work** (the proof asserts nothing here repairs anything), and bringing it back is the calibration job that already existed. No new def, job or giver.
- **The threshold is a FRACTION, not a hit-point count.** The profile contains mods that change building health and armour, and an absolute number would mean something different in each of them. Half, which is generous enough that ordinary wear and a stray shot do not cost a connection - it takes a real attack - because losing calibration costs work to undo.
- **A live opening is ended through the EMERGENCY path, not dropped.** That is the difference between a gate failing and a gate losing people: the emergency path is the one that starts the return window.
- **THE SEVENTH FAILURE REASON WAS ADDED ON PURPOSE.** `proof-areas-and-debrief.py` asserted the complete set at **six** at 0.12.36-dev precisely so an addition has to be deliberate. Now seven, named in both proofs. **Row 98 is untouched** - its claim is about a gate's surroundings, and the proof still asserts no reason anywhere in the class reads an adjacent cell.
- **RELIABILITY IS A RECORD, NOT A DICE ROLL, and that was the design decision.** The tempting reading is a failure chance rising with use. Wrong twice over: **invariant 28 wants every rule learnable** and a machine that sometimes fails for no visible reason is the definition of unlearnable, and this mod's failures are all deterministic and all named, which is what makes them fair. The proof asserts **no `Rand` call anywhere** in the subsystem. So reliability is what actually happened, counted per coordinate - `GateHistoryEntry` recorded `times` and **nothing about how any of it went**.
- **Three decisions inside that.** **Counted, not rated** - a stored percentage would be a second number that could disagree with its own counts, so the rate is derived on read. **No data reads as no data** - `Reliability` returns **-1** and the surface says *"no trip to here has finished yet"*, because 0% and 100% would both invent a claim about a coordinate nobody has come back from. **The coordinate is remembered explicitly** - the history is most-recently-used first, so *"the first entry is the one we are connected to"* is true today and would be a silent lie the first time anything else recorded a connection between opening and closing.
- **It is filed before `failureKey` is cleared**, because that field **is** the emergency and reading it after clearing would record every trip as a success. That ordering is a planted fault.
- **THE PLANTS CAUGHT TWO OF MY OWN CLAIMS BEING TOO WEAK, both the same defect class.** (1) *"the player is told"* checked that the letter key **appeared** in the method; replacing `Find.LetterStack.ReceiveLetter(` with `Noop(` left the arguments in place and the claim passing while nothing was sent - **a claim that searches for a string is not a claim about behaviour**, which is what a plant caught at 0.12.33-dev too. (2) *"filed against the right coordinate"* checked that `historyCoordinateId` appeared, and it appears three times in that method, so removing the actual comparison left the claim passing while every outcome filed against the first entry. Both tightened.
- **AND AN OLDER PROOF HAD A SCOPE HOLE.** `proof-areas-and-debrief.py` enumerated the gate's failure reasons from `CompRimroomsGate.cs` and **kept passing** when the seventh reason arrived, because the new one lives in `GateIntegrity.cs` - **another file of the same partial class**. The count was right and the scope was wrong: a claim reading *"these are all the ways a gate can stop working"* was really *"these are the ways one file can stop it"*. It now globs every `Gate/*.cs`, so a new file of the class is covered the moment it exists, and a plant that adds an eighth reason in the new file fails both proofs.
- Build 0.12.38-dev, **190 C# files, 87 package files**, **0 warnings, 0 errors**, assembly identical across two clean rebuilds. Twelve checkers pass, **thirty-five** proofs exit zero, **18 of 18** planted faults caught. **No game was launched.**

---

## Completed sessions""")

sub("README.md", u"**Current development version: 0.12.37-dev.**",
    u"**Current development version: 0.12.38-dev.**")

# ------------------------------------------------------------------ the queue row
sub("docs/TODO.md",
    u"- [~] Add machine subsystems/upgrades: power reserves, calibration, stabilizers, monitoring, "
    u"emergency cutoff, cool-down, modules, repair, and reliability. — **Partly built.**",
    u"- [x] Add machine subsystems/upgrades: power reserves, calibration, stabilizers, monitoring, "
    u"emergency cutoff, cool-down, modules, repair, and reliability. — **COMPLETE 0.12.38-dev.** "
    u"**Seven of the nine were already built and this row's own grep was looking for the wrong "
    u"words:** stabilizers exist as **`PortalWindowTier`** (a four-rung project ladder that "
    u"multiplies the window and stops the countdown entirely at tier 4) and modules exist as "
    u"**`GateEquipmentLinks`** (roles, `maxLinked`, single ownership across gates). Both are now "
    u"asserted by proof so nobody rebuilds them. **Repair and reliability were the real gaps, and "
    u"the finding was that a gate read NO DAMAGE AT ALL** — it could be shot to twelve per cent "
    u"and still hold a connection. Below half condition it now loses calibration, refuses to open "
    u"with a readable reason, and a live opening ends through the **emergency** path so the crews "
    u"get their return window. Fixing it is Core's own repair; bringing it back is the calibration "
    u"job that already existed. **Reliability is a record, not a dice roll** — outcomes counted "
    u"per coordinate, the rate derived on read, **-1 for no data** so nothing invents a claim "
    u"about an address nobody has come back from, and **no `Rand` call anywhere**. The seventh "
    u"gate failure reason was added deliberately to the asserted set. Record "
    u"`implementation/GATE_SUBSYSTEMS_IMPLEMENTATION.md`, proof `proof-gate-subsystems.py`. Was: "
    u"**Partly built.**")

print("ledger and queue written for 0.12.38-dev")
