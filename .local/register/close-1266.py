# -*- coding: utf-8 -*-
"""0.12.66-dev: a gate where a normal door should have been, and a string that capped the depth."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")

HASH = u"ACD26DB10102B9055A5C44641A4EC2E99E862BC387414DB757849A8F692D83FB"

ENTRY = u"""
---

## Session 2026-10-01 - a gate where a normal door should have been (0.12.66-dev)

**Verbatim user quotes:** *"okay i got into the backrooms but i found a door that was a gate, but
it was where a normal door should of been(gates natural need to not also be used and needed as
normal doors, becasue on the other side was the rest of the backrooms map) and when i went to send
my pawn through that door with a click, it said somthing like : this address is already being
used, and anoother door said somthing like you cant doo that, request is not valid for this
branch, and a differnet sdave address alread uses one of these doorsso it must be something about
generationg the next world map or deeper backrroms idk for sure"*; *"chack the game if you u need
to"*.

**Files touched:** `Portals/NaturalFrontierService.cs`, `Portals/GuaranteedFrontiers.cs`,
`Portals/CompRimroomsEmergence.cs`, `Company/CampaignServices.cs`, three proofs, one plant suite.

**Mod register.** Nothing applied. All four defects are our own rules about our own doors.

**The owner's closing guess was right.** *"it must be something about generationg the next world
map or deeper backrroms"* -- it was both, and they are two different recordings. **Four defects,
and each of the three messages they read was a true report of a different one.**

### A gate must not be a door somebody needs

`GuaranteedFrontiers` collected **every** `Building_Door` on the coordinate and picked two, and
`Evaluate` accepted any of them. So a door between two rooms -- a door the player walks through to
get around the level -- became a permanently open one-way gate and took an ordinary route away.

A way onward is now only ever a **dead-end door**: walkable on exactly one side, rock behind it.
Those already existed and the owner asked for them one checkpoint ago -- `FalseOpening` puts
*"doors to now where"* a third of the way along a blank wall and `PlaceNativeDoors` builds a real
door in each. **So the door that should not be there is the door that leads somewhere else**,
which is the setting written in geometry at no content cost. Checked inside `Evaluate`, so the
glow, the menu and the discovery agree, and inside the guarantee, so the pair cannot be chosen
from doors the service would refuse.

### A string length capped the Backrooms at two levels, and this is the big one

A coordinate's id **embeds its parent's entire id.** Measured against the owner's own branch:

```
branch id                                           42
coordinate A = branch + ":coordinate:discovery:opening"            71
discoveryId  = A + ":frontier:169,178"                             88   fits
coordinate B = branch + ":coordinate:discovery:" + discoveryId    152
discoveryId  = B + ":frontier:120,95"                             168   REFUSED
```

`CreateDiscoveredCoordinate` refuses a discovery id over 128 with `RR_Company_InvalidRequest` --
*"that request is not valid for this branch"*, exactly what the owner read. **The first step
inward worked and the second never could.** `MaximumNaturalDepth` was unreachable from the day it
was written, and *"have more natural portals guaranteeed so the backrooms never ends persay"* was
capped at two by a string.

The limit is a named constant now, read by the composer that has to stay under it -- a validator
and its caller carrying separate copies of one number is the defect this project has paid for
three times in a week. The long form is kept **byte-for-byte whenever it fits**, so every
coordinate in an existing save resolves to the same place; only an id that would be refused is
shortened, and such an id never existed in a save. **Two hashes, not one**, because a single
31-bit FNV value shared by two parents would merge two different places into one coordinate,
which is worse than any refusal.

### A way out is not a way deeper, and I had wired one of them

A deeper find registers a portal **edge**. A way out saves a `WorldExitRecord` with a planet tile
and **registers no edge at all**, because leaving the Backrooms for the world map is a caravan.
The float menu asked `EdgeFor()` in both cases, so a world exit recorded correctly and then
reported *"surveying doors is unavailable until this branch is operating"* -- neither true nor
useful. It offers the caravan walk-out now.

**And a proof refused that, correctly.** `proof-world-exit.py` requires **exactly one caller** of
the leave routine, because *"more than one caller means one of them might not be a player
command"*. Both of mine were player clicks, so the guarantee's intent held -- but *"every caller
is a player command"* is not something source text can decide and *"there is one caller"* is. **A
weaker claim that can be checked beats a stronger one that cannot**, so the code changed: one
private `WalkOutToWorld`, reached from the gizmo and from the menu, and the only thing in the
package that can reach Core's caravan formation.

### And a discovered gate went dark and dead

`IsLiveGate` is `IsDesignated` **and** an edge, and `IsDesignated` means *the player marked this
door as a way home* -- it also demands the player's faction and an ordinary branch map, none of
which is ever true of a door generated inside a coordinate.

So after a successful discovery the edge existed, was correct, and was unusable: no crossing
option, no glow, and asking again returned `RR_Frontier_AlreadyRecorded` -- *"that door is already
a remembered address"*, which the owner read as *"this address is already being used"*. **A way
onward worked exactly once and then went dark.** `IsLiveGate` keeps its meaning because the
address service depends on it; a weaker `IsRecordedGate` was added and the appearance and the
crossing menu ask that instead. **Sixth instance in this run of a path built, registered, correct
and gated off by a condition meant for something else.**

### The trap, a sixth and seventh time

**The machinery is not the behaviour.** The depth claim asserted that `DiscoveryIdFor` *exists*; a
plant reverting the call site to the inline composition left the method defined and the claim
passing while the id grew unbounded again. It pins the call site now, and the absence of the
inline form.

**204 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`ACD26DB10102B9055A5C44641A4EC2E99E862BC387414DB757849A8F692D83FB`, measured after the version
bump, reproduced by two clean recompiles. **Fourteen checkers pass, forty-five proofs hold. 593 of
593** planted faults caught across sixteen suites.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED")
    raise SystemExit(1)
print("FINALIZED written and verified")

todo = io.open(TODO, encoding="utf-8").read()
HEAD_OLD = u"## IN PROGRESS - a gate where a normal door should have been - 2026-10-01 (0.12.66-dev)"
HEAD_NEW = u"## A gate where a normal door should have been - 2026-10-01 (0.12.66-dev) - DONE"
if todo.count(HEAD_OLD) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(HEAD_OLD))
    raise SystemExit(1)
todo = todo.replace(HEAD_OLD, HEAD_NEW, 1)
# Status only. Every description keeps every word.
start = todo.index(HEAD_NEW)
end = todo.index(u"\n---", start)
block = todo[start:end].replace(u"- [~] **", u"- [x] **")
todo = todo[:start] + block + todo[end:]
io.open(TODO, "w", encoding="utf-8", newline="").write(todo)
print("TODO marked done, every description kept")

now = io.open(NOW, encoding="utf-8").read()
NOW_EDITS = [
    (u"| Published | **0.12.65-dev**.", u"| Published | **0.12.66-dev**."),
    (u"SHA-256 `4C1C043BCD3F11D320D459091F4FB1D1D8FE595CADB5B89F3D67A0F67AADC5DF`",
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
print("NOW.md updated for 0.12.66-dev")
