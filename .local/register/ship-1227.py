# -*- coding: utf-8 -*-
"""Ledger for 0.12.27-dev: you cannot brick your own gate."""
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


sub('CHANGELOG.md', u'## 0.12.26-dev', u"""## 0.12.27-dev - 2026-09-29 - you cannot brick your own gate

- **Nothing can be built on the cell your crew has to stand on to use a gate.** The game refuses the placement and says which gate it is protecting, instead of letting you wall your own way in and find out later.
- **Laying a floor there is fine.** Carpet it, tile it, do what you like with the ground.
- **A power conduit or anything else you can walk over is fine too.** The rule is only about things that would stop somebody standing there.
- **It works with buildings from other mods** without any of those mods being changed.
- **Your existing gates already could not break this way** - that was fixed earlier. This stops you doing it by accident in the first place.

Full record: [you cannot brick your own gate](docs/implementation/GATE_APPROACH_CELL_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.12.26-dev""")

sub('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - you cannot brick your own gate (0.12.27-dev)

**Verbatim user quote:** *"hold up im not starting nothing till the todo items are completed are all build items comnplete and mod 100% but bug testing?"*

**Owner answer at the fork, verbatim:** *"option 2 but flooring is fine"*

### What shipped

Row 113 closed - the last open row of the gate-placement direction, open since it was recorded because both readings were defensible. Plus the integrity checker taught to verify a patch on an abstract inheritance parent.

### Files touched

`src/.../Portals/PlaceWorker_GateApproach.cs` **new**, `1.6/Patches/RR_GateApproachPlacement.xml` **new**, `1.6/Languages/English/Keyed/RR_Portals.xml`, `tools/package-files.json`, `tools/check-package-integrity.py`, `.local/register/proof-gate-approach.py` **new**, `.local/register/fault-plant-1227.py` **new**, `docs/implementation/GATE_APPROACH_CELL_IMPLEMENTATION.md` **new**, `CHANGELOG.md`, `README.md`, `About.xml`, the csproj, `NOW.md`, `TODO.md`.

### Closure notes

- **THE OWNER'S ANSWER WAS SHARPER THAN EITHER OPTION OFFERED.** Option 2 was *"the approach cell cannot be built on"*; *"but flooring is fine"* carves terrain out of "built on", which is the distinction that makes the rule feel like a rule rather than a restriction.
- **IT IS NOT EITHER/OR.** Re-derivation already shipped at 0.12.3-dev - the approach cell used to be frozen at registration and a wall on the saved cell would have made a permanently open gate refuse. That fix is the **guarantee**; this is the **protection**, which stops a player bricking their own gate and tells them why.
- **FLOORING IS FREE BY CONSTRUCTION, NOT BY A SPECIAL CASE.** A floor is a `TerrainDef` and terrain placement never consults a `PlaceWorker` at all. **The shape of the mechanism made the owner's exception free** - and my first instinct was a map component cancelling blueprints, where the exception would have had to be written by hand and then remembered.
- **What counts as "built on" is CORE'S rule, decompiled rather than remembered.** `GenGrid.Standable` is walkable plus every thing in the cell having `Traversability.Standable`, so the test is `passability != Traversability.Standable`: a wall refused, a barricade or door refused (Core itself says you cannot stand in a door), a power conduit allowed, another mod's unknown building decided by its own passability. **A list of def names would have been wrong for the 294 mods the moment one shipped a new wall.**
- **The patch reaches other mods' buildings without touching one of their files.** Core's abstract `BuildingBase` is the parent of nearly all of them - `ParentName="BuildingBase"` is the conventional way to define a building - and RimWorld merges an inherited list node with a child's own. **Two stages, deliberately:** adding the element when absent and appending when present are different operations, and doing only the first would append a **second** `placeWorkers` element the day Core adds one, which is malformed and would take the whole list with it. Nothing is replaced or removed, so another mod's place worker on the same parent survives.
- **Every uncertainty allows the placement.** This runs on every placement check for every building while a player drags a blueprint in a 294-mod profile. A refusal it gets wrong is a player who cannot build; an allowance it gets wrong is a gate re-deriving its approach cell exactly as it already does. So a thrown exception, no game, no network, no connections, a despawned or off-map door, an invalid approach cell - all accepted.
- **The protected cell is re-derived, never read from the save.** The saved endpoint cell is a snapshot that exists so moving a door cannot silently redirect a route. Protecting the snapshot while the pawn uses a different cell would be the worst of both.
- **THE CHECKER COULD NOT VERIFY THIS, SO THE CHECKER WAS TAUGHT.** `check-package-integrity.py` refused the patch with *"an xpath selecting no named def"* because it only understood `defName="X"` - so **every patch on an abstract inheritance parent was unverifiable and therefore refused**, which did not check the technique, it ruled it out. It now indexes the `Name` attribute of defs declaring `Abstract="True"`. **The verification is real, not a waiver:** a `Name` on a concrete def is an alias and is deliberately not indexed, and a planted patch at `@Name="NoSuchAbstractParent"` fails.
- **Register guidance applied, two rows from the construction family.** [43] Auto links: *"retain native build costs and link rules. Confirm generated and prefabricated rooms remain reachable"* - no cost or link rule changes, and the rule exists precisely to keep a gate reachable. *"test pathing, room reachability, doors, and map generation with the profile's construction tools"* - construction-reach mods place through `GenConstruct.CanPlaceBlueprintAt`, which is where place workers run, so they share the chokepoint rather than needing an adapter.
- **Twenty-fourth proof, 22 claims, fault-planted seven ways and caught 7 of 7**, including that Core's `BuildingBase` really is abstract in the installed game so a rename cannot leave the patch silently reaching nothing. The checker extension was fault-planted separately, 1 of 1.
- Build 0.12.27-dev, **175 C# files, 87 package files**, **0 warnings, 0 errors**. Assembly `977BC6016FDF88FEADA0E7DA032BD5F8074DCB2C81E5078478B269D2E5B6CF2C`, identical across two clean rebuilds. Ten checkers pass, **twenty-four** proofs exit zero. **Zero open owner questions.** **No game was launched, so nobody has tried to wall a gate shut.**

---

## Completed sessions""")

print('ledger written for 0.12.27-dev')
