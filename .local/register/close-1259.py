# -*- coding: utf-8 -*-
"""0.12.59-dev: a natural gate is always open, closes once, and never re-opens."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

ROW = u"""## Natural gates are one-way, and that is the 5 limit — 2026-09-30 (0.12.59-dev)

Owner, verbatim:

**"hold up tho im doing the store run scenerio.. the gate is a natural one and shouuld always be
open.... so whats this mean? i understand the machine gate opening and closing and will kill
anyone standing near in front on start up. but the natural portals are open always right? except
if minified and put elsewhere or in storage like a building in storage"**

**"but remember we do need to be able to close natural portals u just can not re open them"**

**"thats the whole 5 limit issue"**

**"so deconstructing the door ie braeaks the connection, but uninstaslling the door and storing it
or placing it else where does not"**

- [x] **"the natural portals are open always right?"** — **YES, AND ASKING IT CAUGHT A DEFECT BEFORE IT SHIPPED.** Their unstable vortex fires inside `OpenStargate`, once per open, and their wormhole closes itself after roughly forty seconds idle — `IsReceivingGate && _ticksSinceBufferUnloaded > 2500 && !GateIsLoadingTransporter && _sendBuffer.Empty()` calls `CloseStargate(true)`. A natural gate held permanently open is therefore **re-dialled every time their timeout closes it**, so the door-sized vortex shipped at 0.12.58-dev **would have detonated its own doorway roughly every forty seconds, for ever.**

  **A natural gate now carries no vortex at all**, which is also the honest fiction: it never opens, because it was always there. **The machine gate keeps its kawoosh** — a player dialled that, and the owner named the behaviour exactly: *"will kill anyone standing near in front on start up"*. The event horizon stays on both, because that is what an open way through looks like.

  The two kinds **cannot share a cached result**, because caching on the def alone would hand whichever was asked for first to the other — which is precisely how a natural gate would quietly inherit a machine gate's kawoosh.

- [x] **"we do need to be able to close natural portals u just can not re open them"** and **"thats the whole 5 limit issue"** — **DONE, and it reversed something this package had shipped.** Releasing a place used to be undoable: the door remembered where it led and could open it again, and both the Operations copy and the confirmation promised exactly that. **That is now wrong.** The gizmo, the method and the three strings that promised it are gone, and the copy says what is true — *the way in closes and does not re-open, and this frees one of your held places.*

  **A decision that can be undone is not a decision**, and that is what makes the limit bite.

  **The door still remembers where it led** — as a record, never an offer. A player standing in front of a spent door needs to know it was a way through; losing the memory would make a released place indistinguishable from a door that never led anywhere.

- [x] **"deconstructing the door ie braeaks the connection, but uninstaslling the door and storing it or placing it else where does not"** — **already true, and verified rather than rebuilt.** `proof-gate-links.py` holds *"A DESTROYED GATE STILL ENDS ITS ROUTE"*, *"A CARRIED GATE TAKES ITS ROUTE WITH IT"* and *"uninstalling and deconstructing no longer say the same thing"*. **Moving a gate keeps it; closing its place spends it.**

- [x] **running every suite found a dead method and three plants guarding a feature that no longer exists** — `Reopen()` survived the gizmo's removal as unreachable code, and **three proof claims still held because the method they inspected was the dead one.** A proof that passes by reading unreachable code is worse than no proof: it reports a feature that cannot happen. The method is deleted, and the claims and plants are **inverted rather than removed** — each plant now restores a way to re-open and requires refusal, so the count stays honest instead of quietly shrinking.

- [x] **and the accessor trap again** — a plant renamed `ShelvedCoordinateId` to `…Unused` and the claim stayed satisfied because it tested the backing **field**. The exact accessor signature is required now. **522 of 522** planted faults caught across sixteen suites.

---

"""

ENTRY = u"""
---

## Session 2026-09-30 - natural gates are one-way (0.12.59-dev)

**Verbatim user quotes:** *"the gate is a natural one and shouuld always be open"*, *"but
remember we do need to be able to close natural portals u just can not re open them"*, *"thats the
whole 5 limit issue"*, *"so deconstructing the door ie braeaks the connection, but uninstaslling
the door and storing it or placing it else where does not"*.

**Files touched:** `Portals/StargateBridge.cs`, `Portals/CompRimroomsEmergence.cs`,
`Keyed/RR_Portals.xml`, About/csproj/README, `docs/TODO.md`, `docs/NOW.md`.

**Closure notes.** **One question caught a defect that every proof had passed.**

Their vortex fires inside `OpenStargate`, once per open, and their wormhole closes itself after
about forty seconds idle. A permanently-open natural gate is therefore re-dialled every time that
timeout fires - so the door-sized vortex shipped one checkpoint earlier **would have detonated its
own doorway every forty seconds, for ever.** A natural gate now carries no vortex at all, which is
also the honest fiction: it never opens, because it was always there. The machine gate keeps its
kawoosh, because a player dialled that. The two kinds cannot share a cached result, since caching
on the def alone would hand whichever was asked for first to the other.

**And releasing a place reversed.** It used to be undoable - the door remembered where it led and
could open it again, and the copy promised it. By owner direction that is now one-way: the gizmo,
the method and the three strings are gone, and the confirmation says the gate will not open again
and that this frees one of the held places. A decision that can be undone is not a decision, and
that is what makes the five-map limit bite. The door still remembers, as a record and not an
offer.

**Deconstruct versus uninstall was already right** and was verified rather than rebuilt: a
destroyed gate ends its route, a carried gate takes its route with it, and the two commands no
longer say the same thing.

**Running every suite found a dead method and three plants guarding a feature that no longer
exists.** `Reopen()` outlived its gizmo as unreachable code, and three claims still held because
the method they inspected was the dead one - **a proof passing by reading unreachable code, which
reports a feature that cannot happen.** The claims and plants were inverted rather than deleted,
so each now restores a way to re-open and requires refusal. And a plant renamed an accessor to
`...Unused` while the claim tested the backing field, which is the prefix trap once more.

**181 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`F267F664D0DB8B70E147FC035614F033BA8546BE12983824622089B260F4F1E9`, measured **after** the version
bump this time, reproduced by two clean recompiles. **Thirteen checkers pass, forty-five proofs
hold. 522 of 522** planted faults caught across sixteen suites.
"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED -- nothing else touched")
    raise SystemExit(1)
print("FINALIZED written and verified")

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("one-way rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.58-dev**.", u"| Published | **0.12.59-dev**."),
    (u"SHA-256 `F513B9D2B17ABF1B10DF36CED4B7DFE868B2FB423712338F1780F3BA2A5EEDA3`",
     u"SHA-256 `F267F664D0DB8B70E147FC035614F033BA8546BE12983824622089B260F4F1E9`"),
]
problems = []
for old, _ in EDITS:
    if now.count(old) != 1:
        problems.append("%d of %r" % (now.count(old), old[:56]))
if problems:
    for problem in problems:
        print("NOW ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in EDITS:
    now = now.replace(old, new, 1)
io.open(NOW, "w", encoding="utf-8", newline="").write(now)
print("NOW.md updated for 0.12.59-dev")
