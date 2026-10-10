# -*- coding: utf-8 -*-
"""Ledger for 0.12.32-dev: everything is read by something."""
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


sub('CHANGELOG.md', u'## 0.12.31-dev', u"""## 0.12.32-dev - 2026-09-29 - everything is read by something

- **You can cut a connection now without disabling the gate.** A new button on a working gate ends the opening immediately and starts the emergency return window, so anyone on the far side comes home - and the gate is still there for next time. That is different from the kill switch, which stays thrown until you clear it.
- **The whole mod was audited for things that were built and then never hooked up.** 258 definitions and 102 actions checked. The cutoff above was one of two that had no way to reach them; the other turned out to be a duplicate of something that already worked, and was removed.
- **A check now refuses to ship anything this mod adds that nothing reads.** Four times in this project's history something was written and left unreachable - once it was the entire contract line.

Full record: [everything is read by something](docs/implementation/WIRING_AUDIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.31-dev""")

sub('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - everything is read by something (0.12.32-dev)

**Verbatim user quote:** *"get to finishing it all and making sure its all wired up"*

### What shipped

A full wiring audit of the mod, the **eleventh checker** to keep it true, and the two unwired things it found.

### Files touched

`tools/check-wiring.py` **new**, `src/.../Company/CampaignServices.cs`, `src/.../Gate/CompRimroomsGate.cs`, `1.6/Languages/English/Keyed/RR_NativeGate.xml`, `docs/implementation/WIRING_AUDIT_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **THE OWNER ASKED FOR IT AND THE EVIDENCE WAS ALREADY ON THE TABLE.** Four times something in this mod was authored and read by nothing: five `RR_*Staff` PawnKinds (0.11.7-dev), no `IncidentDef` at all (0.11.8-dev), **`RimroomsRequestDef` and seven authored requests read by zero lines of C# with the chart recording both steps as done** (0.12.11-dev), and **`EstablishCorporationContact()` with no caller, leaving two of three starts with no campaign** (0.12.30-dev). **Every one passed every checker and proof of its day** - nothing was wrong with any individual file, and no tool looked at wiring.
- **I GOT THE DEF RULE WRONG TWICE BEFORE GETTING IT RIGHT.** Rule 1 alone (named in C#) reported **106 dangling defs**; almost all were content defs consumed **by type** - the generator picks an inhabitant from `DefDatabase<RimroomsInhabitantDef>` and RimWorld resolves a `FactionDef` itself. Adding rule 2 left **3**: the `RimroomsStartDef`s. **Those are not dangling either** - `ScenPart_RimroomsStart` declares `public RimroomsStartDef startDef;` and each `ScenarioDef` names one in XML, which is rule 3, a **cross-reference**. **With all three rules: 258 defs, zero dangling.** The def side was already fully wired, and twice the measurement was the defect rather than the code.
- **The action rule found two, and each was resolved on its own merits rather than uniformly.** 102 public `CompanyActionResult` methods - this mod's whole player-facing verb surface - checked for a caller outside their own declaration.
- **`RenameCompany` RETIRED.** Not a missing feature: a **second path to a change that already works**. `Dialog_RenameCompany` uses Core's `Dialog_Rename<T>`, whose accept sets `RenamableLabel`, whose setter calls **the same `TrySetCompanyName`**, and whose `OnRenamed` calls `NoteRenamed()` recording **the same event**. Identical validation, identical record, one unreachable. **Two entry points to one state change is how two validations drift apart**, and the unused one drifts unnoticed.
- **`TriggerEmergencyCutoff` WIRED**, and it is **not** a duplicate of the kill switch: the switch is a **persistent thrown state** that must be cleared before the next opening, while a cutoff **ends this opening, starts the return window, and leaves the gate usable.** That is the safety action a player wants while watching a crew get into trouble - end it now, keep the gate. `EnterEmergency` already had seven automatic callers, so the mechanism was sound and only the **deliberate** version was unreachable. Now a gizmo, shown only while an opening runs and is not already an emergency.
- **The checker's allow-list names its own failure mode.** `CORE_CONSUMED` is short and explicit and the file says a type added there without a reason is a hole in the check - which is the failure mode of every allow-list, and naming it in the file is the only defence available.
- **Fault-planted both ways, 2 of 2:** an action losing its only caller, and a new unreferenced def appearing.
- Build 0.12.32-dev, **179 C# files, 87 package files**, **0 warnings, 0 errors**. Assembly `B86715C2EBD0300B0888F9C613EC3645AD9CEAAEA314FD45ED55230971D848CD`, identical across two clean rebuilds. **ELEVEN checkers** pass, twenty-eight proofs exit zero. **No game was launched** - and wiring is exactly the kind of thing a launch would have found instead.

---

## Completed sessions""")

print('ledger written for 0.12.32-dev')
