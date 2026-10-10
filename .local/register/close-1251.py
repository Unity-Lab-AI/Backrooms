# -*- coding: utf-8 -*-
"""0.12.51-dev closure: the release list, and a correction owed to the previous record."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODO = os.path.join(REPO, "docs", "TODO.md")
FINAL = os.path.join(REPO, "docs", "FINALIZED.md")
NOW = os.path.join(REPO, "docs", "NOW.md")
PRIOR = os.path.join(REPO, "docs", "implementation", "WARREN_AND_DOORWAYS_IMPLEMENTATION.md")

# ---------------------------------------------------------------- the correction, annotated
prior = io.open(PRIOR, encoding="utf-8").read()
OLD_CLAIM = """### And discovering is free

Worth stating because it changes the mental model: `Discover` mints a coordinate *record* and
registers an address. **No map is generated until somebody crosses.** So a player may find many
natural gates at no cost; what costs a slot is a place left open."""
NEW_CLAIM = """### And discovering is free — **WRONG, corrected at 0.12.51-dev**

> **This section was wrong and is annotated rather than rewritten**, per invariant 135.
>
> `Discover` calls `PortalAddressService.RegisterNaturalAddress`, which calls
> `DestinationService.EnsureSite` **immediately** — because a natural edge is registered against
> the far side's own `ReturnAnchor`, and that `Thing` does not exist until the map does. **A
> discovery costs a slot the moment it is made.**
>
> Two things follow. The budget check in `Discover` is **load-bearing rather than over-eager**, as
> this record wrongly implied. And the owner's trap — *"get 5 natural gates u cant use a machine
> gate"* — is real exactly as they described it, not a late-game edge case. That is why the
> release list moved from "next checkpoint" to done at 0.12.51-dev.

The original text, preserved: *Worth stating because it changes the mental model: `Discover` mints
a coordinate record and registers an address. No map is generated until somebody crosses. So a
player may find many natural gates at no cost; what costs a slot is a place left open.*"""
if prior.count(OLD_CLAIM) != 1:
    print("PRIOR ANCHOR PROBLEM: %d" % prior.count(OLD_CLAIM))
    raise SystemExit(1)

OLD_HELD = """## The one piece deliberately not shipped, and exactly what it needs"""
NEW_HELD = """## The one piece deliberately not shipped — **SHIPPED at 0.12.51-dev**

> The three things named below were built exactly as described: the save-schema field on
> `CoordinateRecord` (`releasedByPlayer`), teardown ordered so nothing is ever orphaned, and the
> refusal set. See `RELEASE_A_PLACE_IMPLEMENTATION.md`.

## The one piece deliberately not shipped, and exactly what it needs"""
if prior.count(OLD_HELD) != 1:
    print("PRIOR HELD ANCHOR PROBLEM: %d" % prior.count(OLD_HELD))
    raise SystemExit(1)

prior = prior.replace(OLD_CLAIM, NEW_CLAIM, 1).replace(OLD_HELD, NEW_HELD, 1)
io.open(PRIOR, "w", encoding="utf-8", newline="").write(prior)
print("prior record annotated, not rewritten")

# ---------------------------------------------------------------- TODO
ROW = u"""## Releasing a place — 2026-09-30 (0.12.51-dev)

- [x] **"yeah so if the player discovers and goes through a natural gate how do they turn them off to use the machine gates for more controll and aiming deeper?"** and **"get 5 natural gates u cant use a machine gate"** — **DONE, as the Operations held-places list the owner chose.**

  **And the trap was worse than the previous record said.** That record claimed discovering a gate was free because no map existed until somebody crossed. **It was wrong:** `Discover` calls `RegisterNaturalAddress`, which calls `EnsureSite` **immediately**, because a natural edge is registered against the far side's own `ReturnAnchor` and that `Thing` does not exist until the map does. **A discovery costs a slot at the moment it is made**, so the budget check in `Discover` is load-bearing rather than over-eager, and five discoveries really do lock a player out of their machine gates. The previous record is **annotated, not rewritten**, per invariant 135.

  A natural gate is permanently open (invariant 12) and is never closed. What is released is **the space behind it**. The door stays, still marked, and **remembers which place it led to** on its own comp — written at release while the edge still says so, because the edge has to be removed and is the only other record of the pairing.

  **The teardown order is the whole of the safety, and it is asserted as an ordering:** the doors are told where they led **before** the edges are removed, and the edges are removed **before** the map is torn down. Reverse either pair and a record points at something that no longer exists, which is this project's most expensive defect class.

  **`releasedByPlayer` is the only thing that can tell a deliberate release from a broken reference** — both look identical from outside, no site and surveyed rooms — and `EnsureSite`'s explored-graph guard exempts exactly that and nothing else. It still refuses a competing owner or a live map, and the exemption is **spent the moment the place exists again**, because an exemption that outlives its reason is a hole.

  Refusals name themselves: the headquarters, crew inside (**a prisoner or an animal counts**), a crossing in flight, or a place with no live map. Re-opening goes through the same `RegisterNaturalAddress` path that first created it, is **disabled rather than hidden** at the budget, and **only forgets the shelved place on success** — forgetting on failure would strand it for ever over a transient refusal.

  Record `implementation/RELEASE_A_PLACE_IMPLEMENTATION.md`. **88 of 88** planted faults caught.

- [ ] **still open from the same direction** — the wild variation of materials across items, equipment, walls, floors, lights, furniture and benches, with the events, layouts and loot deeper in.

---

"""

todo = io.open(TODO, encoding="utf-8").read()
ANCHOR = u"## TOMBSTONES"
if todo.count(ANCHOR) != 1:
    print("TODO ANCHOR PROBLEM: %d" % todo.count(ANCHOR))
    raise SystemExit(1)

ENTRY = u"""
---

## Session 2026-09-30 - letting a place go (0.12.51-dev)

**Verbatim user quote:** *"yeah so if the player discovers and goes through a natural gate how do
they turn them off to use the machine gates for more controll and aiming deeper?"*

**Verbatim user quote:** *"get 5 natural gates u cant use a machine gate"*

**Verbatim user quote:** *"get to work"*

**Files touched:** `Generation/CoordinateRelease.cs` (new), `UI/OperationsHeldPlaces.cs` (new),
`Company/CampaignRecords.cs`, `Generation/DestinationService.cs`,
`Portals/RimroomsPortalNetwork.cs`, `Portals/CompRimroomsEmergence.cs`,
`UI/MainTabWindow_Operations.cs`, `Keyed/RR_Portals.xml`, About/csproj/README,
`docs/implementation/RELEASE_A_PLACE_IMPLEMENTATION.md`, and
`WARREN_AND_DOORWAYS_IMPLEMENTATION.md` **annotated with a correction**.

**Closure notes.** **A correction is owed and is the first thing in this entry.** The previous
checkpoint's record said discovering a natural gate was free because no map was generated until
somebody crossed. That is wrong. `NaturalFrontierService.Discover` calls
`PortalAddressService.RegisterNaturalAddress`, which calls `DestinationService.EnsureSite`
**immediately**, because a natural edge is registered against the far side's own `ReturnAnchor` and
that `Thing` does not exist until the map does. **A discovery costs a slot the moment it is made.**
The budget check in `Discover` is therefore load-bearing rather than over-eager, and the owner's
trap is real exactly as they described it - which is why this shipped now instead of being deferred.
The prior record is annotated rather than rewritten, per invariant 135.

**A natural gate is permanently open and is never closed.** What a release lets go of is the space
behind it. The door stays, still marked, and remembers which place it led to on its own comp -
written at release **while the edge still says so**, because the edge must be removed and is the
only other record of the pairing.

**The teardown order is the whole of the safety**, and the proof asserts it as an ordering rather
than as the presence of three calls: doors told **before** edges removed, edges removed **before**
the map is torn down. Reverse either pair and a record points at something that no longer exists.

**`releasedByPlayer` exists because one question cannot otherwise be answered.** `EnsureSite`
rightly refuses to rebuild a coordinate with no site whose rooms were surveyed - a broken reference
must not replace an explored graph - and a deliberate release is indistinguishable from that unless
it says so. The exemption covers nothing else: a competing owner or a live map still refuses, and
it is cleared the moment the place exists again.

**Refusals name themselves**, and a prisoner or an animal counts as somebody inside, because a
released map takes its contents with it. Re-opening reuses `RegisterNaturalAddress` rather than a
second implementation, is disabled rather than hidden at the budget, and only forgets the shelved
place on success.

**Two plants found two more loose claims of mine**, both the duplicate-string trap: the
`EnsureSite` call appears **twice** in `PortalAddressService`, so a presence test survived deleting
one, and `connections.Remove(` did not match a planted `connections.RemoveAll(`. Counted and
widened. That trap is now the single most recurrent failure mode in this project's proofs.

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`378493F20F4B7CD8BB932608073434CC00315C00EE94567C50FE995CCADF1A79`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-one proofs hold.** **88 of 88** planted faults caught.
"""

final = io.open(FINAL, encoding="utf-8").read()
io.open(FINAL, "w", encoding="utf-8", newline="").write(final + ENTRY)
if ENTRY not in io.open(FINAL, encoding="utf-8").read():
    print("FINALIZED WRITE NOT VERIFIED -- nothing else touched")
    raise SystemExit(1)
print("FINALIZED written and verified")

io.open(TODO, "w", encoding="utf-8", newline="").write(todo.replace(ANCHOR, ROW + ANCHOR, 1))
print("release rows recorded")

now = io.open(NOW, encoding="utf-8").read()
EDITS = [
    (u"| Published | **0.12.50-dev**.", u"| Published | **0.12.51-dev**."),
    (u"SHA-256 `0B307BD06299AE6EA7028267A1663D5D15315F540FEBDD8898432E60F1150599`",
     u"SHA-256 `378493F20F4B7CD8BB932608073434CC00315C00EE94567C50FE995CCADF1A79`"),
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
print("NOW.md updated for 0.12.51-dev")
