# -*- coding: utf-8 -*-
"""0.12.67-dev: the corporate start disabled itself on turn one, from the day it was written."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = u"58D9FD124C6B051ED6798B783DF6D006D87F5A731933DB8C92089F08F5656359"

TODO_ENTRY = u"""
## The corporate start disabled itself on turn one - 2026-10-01 (0.12.67-dev) - DONE

Owner, verbatim:

> **"okay i moved on top the company scenerio start. the gate is not set up.. there should be
> everthing basic needed to operate the gate already align and ready to operate.. and it says :
> Company Records could not be reconsiled blah blah blah.... and none of our buttons work and i
> have no idea how the gate is suppose to work as there doesnt be a toggle option to turn it from
> a normal door to a machine gate door . so it looke like some work is needed on the design of the
> machine gate room and facility. and we probably need to fix the load shit becasue it seems like
> our mod isnt there in the corporate start.. but i could be wrong as corporate start doent have a
> operating gate at first, but it should at least have all its basic components there and
> connected just waiting to be switched on"**

> **"u can check the gasme, but like you said it been busted since scenerio write so might not get
> much"**

- [x] **"it says : Company Records could not be reconsiled blah blah blah"** - `BuildProjectTree`
  set `insightCommitted = done` and never set `insightOperationId`, which
  `ValidateRecordRelationships` requires. Every pre-completed project was a save-integrity fault
- [x] **"and none of our buttons work"** - the fault set `stateFaultKey`, so `CanOperate` went
  false and every company action in the mod refused
- [x] **"i have no idea how the gate is suppose to work as there doesnt be a toggle option to turn
  it from a normal door to a machine gate door"** - `CompGetGizmosExtra` returned early for any
  undesignated door, so an ordinary door offered nothing; the only route was a pane the fault was
  also refusing
- [x] **"it seems like our mod isnt there in the corporate start.. but i could be wrong"** - the
  owner was right to doubt it and wrong about the cause: the mod was there and every component
  was placed. **The controls were unreachable**
- [x] **"it should at least have all its basic components there and connected just waiting to be
  switched on"** - they already are: `CommsConsole` (28,0,29), `Battery` (44,0,26),
  `TableMachining` (17,0,44) and an `Autodoor` (29,0,33). Recorded because the owner doubted it
- [x] **"so it looke like some work is needed on the design of the machine gate room and
  facility"** - the toggle is on the door now, and it commissions with the branch's own equipment

---
"""

ENTRY = u"""
---

## Session 2026-10-01 - the corporate start disabled itself on turn one (0.12.67-dev)

**Verbatim user quotes:** *"okay i moved on top the company scenerio start. the gate is not set
up.. there should be everthing basic needed to operate the gate already align and ready to
operate.. and it says : Company Records could not be reconsiled blah blah blah.... and none of our
buttons work and i have no idea how the gate is suppose to work as there doesnt be a toggle option
to turn it from a normal door to a machine gate door . so it looke like some work is needed on the
design of the machine gate room and facility. and we probably need to fix the load shit becasue it
seems like our mod isnt there in the corporate start.. but i could be wrong as corporate start
doent have a operating gate at first, but it should at least have all its basic components there
and connected just waiting to be switched on"*; *"u can check the gasme, but like you said it been
busted since scenerio write so might not get much"*.

**Files touched:** `Company/CampaignServices.cs`, `Gate/CompRimroomsGate.cs`,
`UI/OperationsGateBinding.cs`, `Keyed/RR_Gate.xml`, `proof-starts.py`,
`plant-startplacement.py`.

**Mod register.** Nothing applied. Both defects are our own records and our own UI.

**Closure notes.** **One missing field disabled an entire scenario on turn one, and it had done so
since the day that scenario was written.**

The log was decisive and it took one line to find:

```
2027  [Rimrooms][Save] Campaign integrity failed; company actions are disabled.
2028  [Rimrooms][Company] Initialized rr-branch-... scenario=async_industries
```

The error is logged **immediately before** the branch reports itself initialised, because
`InitializeBranch` calls `ValidateSavedState()` as its last act -- so the records it has just
seeded are the records that failed.

`BuildProjectTree` writes a pre-completed project as `completed = done`,
`insightCommitted = done`, `workDone = workRequired` -- and **never sets `insightOperationId`.**
`ValidateRecordRelationships` requires `(!p.insightCommitted || insightOperationId is non-empty)`,
so every pre-completed project is an integrity fault, `stateFaultKey` is set, `CanOperate` goes
false, and **every company action in the mod refuses.** That is *"none of our buttons work"*,
exactly.

**Only the corporate start names completed projects** -- eight of them, from `RR_GateTelemetry` to
`RR_Commerce_NegotiatedTerms`. The store and lone-survivor starts carry an empty list, so `done`
is always false and they start clean. **So this was never a regression; the corporate start has
been unplayable since it was written, and no launch had reached it until now.**

The rule was right and stays: a committed insight with no receipt is the double-payment hole the
check exists for. What changed is the seeding, and the comment beside the field had already stated
the intent -- *"a project that begins finished has had its insight paid for by whoever ran this
branch before you"*. A paid insight has a receipt, in the same format
`InvestigationServices` writes when a player commits one, built from the record's own id.

### The toggle was in the wrong place, and then unreachable

`CompGetGizmosExtra` opened with `if (parent.Faction != Faction.OfPlayer || !IsDesignated)
{ yield break; }`, so **an undesignated door offered nothing at all.** Every control for making a
door a gate lived in an Operations pane -- which the state fault was also refusing. There was no
route from a door to a gate anywhere a player would look, which is the whole of *"i have no idea
how the gate is suppose to work"*.

The door carries the toggle now. It commissions with the **sole** candidate of each kind, which is
every start this mod ships, so *"basic components there and connected just waiting to be switched
on"* is one click; with none or several of a kind it refuses **by name** and the Operations pane
stays for choosing deliberately. Nothing is decided there: `BindNativeInfrastructure` applies
every rule it always did.

**And the owner's doubt about the facility was worth checking and was wrong in a useful way.** The
corporate HQ places every component the binding requires -- `CommsConsole` at (28,0,29), `Battery`
at (44,0,26), `TableMachining` at (17,0,44), an `Autodoor` at (29,0,33). **Nothing was missing from
the facility. The controls were unreachable.**

### Two checkers and two plants caught me

`check-info-cards.py` and `check-retired-content.py` both refused the new strings for saying
*"machine gate"* -- retired at 0.9.0-dev, when a gate became a door and nothing else, and the
shipped vocabulary is *"gate"*. The owner's own phrasing was colloquial and the player-facing text
must not be.

**The scoping trap, fortieth instance.** `RR_GateTelemetry` appears in that file's own **comment**,
explaining that it puts `PortalWindowTier` at 1 -- so a plant deleting it from
`<completedProjects>` left the comment standing and the whole-file claim was satisfied by it. The
claim reads the element now.

**The machinery is not the behaviour, seventh instance this run.** The toggle claim pinned the
three provider scans, the headquarters check and the bind call -- all of which a plant replacing
`if (console == null || battery == null || bench == null)` with `if (false)` leaves untouched. It
pins the refusal branch now.

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`58D9FD124C6B051ED6798B783DF6D006D87F5A731933DB8C92089F08F5656359`, measured after the version
bump, reproduced by two clean recompiles. **Fourteen checkers pass, forty-five proofs hold. 600 of
600** planted faults caught across sixteen suites.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"\n## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)
io.open(TODO, "w", encoding="utf-8", newline="").write(
    todo.replace(ANCHOR, TODO_ENTRY + ANCHOR, 1))
print("TODO row added and closed, owner words verbatim")

now = io.open(NOW, encoding="utf-8").read()
NOW_EDITS = [
    (u"| Published | **0.12.66-dev**.", u"| Published | **0.12.67-dev**."),
    (u"SHA-256 `ACD26DB10102B9055A5C44641A4EC2E99E862BC387414DB757849A8F692D83FB`",
     u"SHA-256 `" + HASH + u"`"),
]
problems = []
for old, _ in NOW_EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in NOW_EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.67-dev")
