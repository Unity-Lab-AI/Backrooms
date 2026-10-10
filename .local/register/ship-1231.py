# -*- coding: utf-8 -*-
"""Ledger for 0.12.31-dev: a wide gate out of plain doors."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def sub(rel, old, new):
    s = read(rel)
    assert old in s, '%s: anchor missing %r' % (rel, old[:70])
    assert s.count(old) == 1, '%s: anchor not unique %r' % (rel, old[:70])
    write(rel, s.replace(old, new, 1))


sub('CHANGELOG.md', u'## 0.12.30-dev', u"""## 0.12.31-dev - 2026-09-29 - a wide gate out of plain doors

- **You can build a wide gate out of ordinary doors now.** Put two or three plain doors side by side in the same wall, designate one as a gate, and bind the others into it. The whole run becomes one gate.
- **No mod needed for any gate size.** One-cell and two-cell were already free - the base game's ornate door is two wide - and a bound run covers three-wide and the big two-by-three shape. If you do run a door mod, its real wide doors still work exactly as before.
- **It is one gate, not several.** One opening, one spin-up, one address, and the same width read from both sides. The extra doors are part of the gate rather than gates of their own.
- **A bigger opening costs more.** More power to hold open and more work to bring up, in proportion, exactly as a real wide door does.
- **The run has to be a filled rectangle** and no bigger than the largest gate size. A ring of doors around a gap is not an opening.
- **Neither binding nor releasing can be done while the gate is working.** Release turns the extra doors back into ordinary doors.

Full record: [a wide gate out of plain doors](docs/implementation/GATE_DOOR_RUN_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.30-dev""")

sub('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - a wide gate out of plain doors (0.12.31-dev)

**Verbatim user quote:** *"get to it"*

**Owner answer on record for this fork, verbatim:** *"i suppose the fallback is okay of building mulitple doors 1x1 to make the sizes needed to fit vehicals and the like"* - answered as **BOTH paths**.

### What shipped

The adjacent-door-run fallback: 1x3 and 2x3 gates with no mods at all. Three rows (568, 610, 959) that were one feature.

### Files touched

`src/.../Gate/GateDoorRun.cs` **new**, `src/.../Gate/GateFootprint.cs`, `src/.../Gate/NativeGateBinding.cs`, `src/.../Gate/CompRimroomsGate.cs`, `1.6/Languages/English/Keyed/RR_NativeGate.xml`, `.local/register/proof-gate-door-run.py` **new**, `.local/register/fault-plant-1231.py` **new**, `docs/implementation/GATE_DOOR_RUN_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **THE RUN FLOWS THROUGH THE CODE THAT ALREADY EXISTED, AND THAT IS WHY THE CHANGE IS SMALL.** Everything about a gate's size already derives from one `CellRect`: `GateOccupiedRect` feeds `GateEntryCells` feeds `GateWidth`, and feeds `GateCellCount` which feeds the power draw and the spin-up work. **A straight line of N adjacent 1x1 doors IS a 1xN `CellRect`**, and two such lines are a 2xN one, so returning the union meant **nothing downstream had to learn that a run exists.** A run costs more to power and more work to bring up, in exactly the proportion a real wide door does, with no line written for it - the owner's *"costs more to run"* for free.
- **Invariant 32 held: one gate, one spin-up.** Exactly one door is the gate; the rest are extensions, and an extension reports `IsDesignated` **false** - no address, no console, no window, no operator. Three gates in a row pretending to be one opening would be three spin-ups and three addresses. A door already a gate, or already in another run, refuses; and a gate that is itself an extension cannot take anything in, or a chain of hosts forms and nothing is the gate.
- **Invariant 47 held: one width, both directions.** Derived once off the run's rectangle, with no second derivation anywhere. Per-endpoint measuring traps an animal in the Backrooms.
- **Invariant 41 held: throughput is never capped.** More entry cells, no quota, and the proof asserts by name that no counter, cap or permit limit was introduced.
- **A RUN IS A SOLID RECTANGLE OF A LEGAL SIZE.** A ring of doors around a gap has a legal-looking bounding box and is not an opening, so the union is accepted only when its area equals the number of doors in it and its shape is one of the **same four** a single door may be. **Legality is a property of the whole run**, not of the door being added, so extending proposes the door, checks, and puts it back on failure - and the candidate search asks the same way rather than reimplementing the rule, because a second copy would drift out of step.
- **The owner's existing rule applied unchanged:** *"gate doors expansions can NOT be done on a working gate"*. An opening and a spin-up both refuse, **in both directions** - you cannot extend a working gate and you cannot release one either.
- **BOTH DEFECTS IN THIS CHECKPOINT WERE MINE AND THE CHECKERS CAUGHT BOTH.** `check-keyed-strings` caught `Refused("RR_GateRun_" + suffix)` - **a runtime-built keyed string, the fifth time this project has caught that pattern**; replaced with thirteen literal keys. And `check-info-cards` caught the word **"doorway" five times** in player-facing text, when the vocabulary rule is that a plain door is a **door** - **a rule I had personally broken and had explained to me earlier in this same session.** The checker did not care, which is the entire argument for having it. Six comment uses went too: a comment teaching the wrong word is how the wrong word gets back into a string.
- **Twenty-eighth proof, 39 claims, fault-planted eleven ways and caught 11 of 11.** Three have no symptom until much later: a hole is only visible when something tries to walk through it, a released host only matters to a door that has become nothing, and **an unsaved run silently becomes three ordinary doors on the next reload.**
- Build 0.12.31-dev, **179 C# files, 87 package files**, **0 warnings, 0 errors**. Assembly `BA503ACA67B06719663B35D406E536C63DF266F55F926602B6958DE7CF76F757`, identical across two clean rebuilds. Ten checkers pass, **twenty-eight** proofs exit zero. **Gate sizes now reachable with no mods at all: 1x1, 1x2 (Core's OrnateDoor), 1x3 and 2x3 (bound run).** **No game was launched, so nobody has walked a vehicle through one.**

---

## Completed sessions""")

print('ledger written for 0.12.31-dev')
