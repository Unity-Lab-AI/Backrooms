# You cannot brick your own gate — 0.12.27-dev, 2026-09-29

**Dated record.** Never rewritten. Closes the last open row of the gate-placement direction, on an
owner answer given at the fork.

---

## The question, and the answer

Row 113 had been open since the gate-placement direction was recorded, because **both readings were
defensible** and invariant 134 says ask rather than guess:

> *"whether the approach cell should be re-derived when the local geometry changes, or whether the
> rule should be that a portal door's approach cell simply cannot be built on — and if the latter,
> how the player is told."*

Asked at the fork. The owner's answer, verbatim:

> **"option 2 but flooring is fine"**

That is sharper than either option I offered. Option 2 was *"the approach cell cannot be built on"*;
the owner's addition carves terrain out of "built on", which is the distinction that makes the rule
feel like a rule rather than a restriction.

**It also is not either/or.** Re-derivation already shipped at 0.12.3-dev — the approach cell used
to be frozen at registration, and a wall on the saved cell would have made a permanently open gate
refuse. That fix is the *guarantee*. This checkpoint is the *protection*: you are stopped before you
brick your own gate, and told why.

---

## Flooring is free by construction, not by a special case

A floor is a **`TerrainDef`**, and terrain placement never consults a `PlaceWorker` at all.

So implementing this as a place worker means the owner's carve-out is **structural**. Had I
implemented it as a map component cancelling blueprints — the other obvious no-Harmony route — the
exception would have had to be written by hand, and then remembered by whoever touched it next.

**The shape of the mechanism made the owner's exception free.** That is worth recording, because the
map-component version was my first instinct.

---

## What counts as "built on" is Core's rule, not a list of ours

`GenGrid.Standable`, decompiled rather than remembered:

```csharp
public static bool Standable(this IntVec3 c, Map map)
{
    if (!c.Walkable(map)) return false;
    List<Thing> list = map.thingGrid.ThingsListAt(c);
    for (int i = 0; i < list.Count; i++)
        if (list[i].def.passability != Traversability.Standable) return false;
    return true;
}
```

So the test is exactly `passability != Traversability.Standable`:

| | |
|---|---|
| a wall (`Impassable`) | **refused** |
| a barricade, a sandbag, a door (`PassThroughOnly`) | **refused** — Core itself says you cannot stand in a door |
| a power conduit, a floor-level fitting (`Standable`) | **allowed** |
| a floor, a carpet (`TerrainDef`) | **allowed**, and never even asked |
| another mod's building this project has never heard of | **decided by its own passability** |

**A list of def names would have been wrong for the 294 mods the moment one of them shipped a new
wall.** Deriving the rule from Core's own predicate is the only version that stays true.

---

## The patch reaches other mods' buildings without touching a single one of their files

A place worker only exists on a def, and the set of things that could block an approach cell is
every wall, barricade and door in Core, in five DLC and in 294 other mods.

Core's abstract **`BuildingBase`** is the parent of nearly all of them — including other mods'
buildings, because `ParentName="BuildingBase"` is the conventional way to define one — and
**RimWorld merges an inherited list node with a child's own**. One addition there reaches
everything that descends from it.

**Two stages, deliberately.** `BuildingBase` declares no `placeWorkers` today and might one day.
Adding the element when absent and appending to it when present are different operations, and doing
only the first would append a **second** `placeWorkers` element the day Core or a load-order
predecessor adds one — which is malformed and would take the whole list with it.

Nothing is replaced or removed, so another mod's place worker on the same parent survives this.

### The register was consulted and it bears on this directly

`use RR-GATE`. Two rows applied, both from the construction family:

| Row | Instruction | How it landed |
|---|---|---|
| **[43] Auto links** | *"retain native build costs and link rules. Confirm generated and prefabricated rooms remain reachable"* | **No cost and no link rule changes.** One cell refuses a blocking building, and the rule exists precisely to keep a gate reachable |
| **[43] Auto links** | *"test pathing, room reachability, doors, and map generation with the profile's construction tools"* | Construction-reach mods place through `GenConstruct.CanPlaceBlueprintAt`, which is where place workers run, so they are covered by the same chokepoint rather than needing their own adapter |

---

## Every uncertainty allows the placement

This runs on **every placement check for every building in the game**, while a player drags a
blueprint, in a profile with 294 other mods.

The asymmetry is not close:

- a **refusal** this gets wrong is a player who cannot build, with no explanation that makes sense
- an **allowance** it gets wrong is a gate re-deriving its approach cell exactly as it already does

So: a thrown exception returns accepted. No game, no portal network, no connections, a despawned
door, an off-map door, an invalid approach cell — all accepted. The only path to a refusal is a
live registered connection whose door is on this map and whose currently-derived approach cell is
inside the footprint being placed.

**And the protected cell is re-derived, never read from the save.** The saved endpoint cell is a
snapshot that exists so moving a door cannot silently redirect a route; the cell a pawn will
actually use is whatever the geometry says now. Protecting the snapshot while the pawn uses a
different cell would be the worst of both.

---

## The checker could not verify this, so the checker was taught

`check-package-integrity.py` refused the patch outright:

```
has an xpath selecting no named def, so what it patches cannot be verified:
Defs/ThingDef[@Name="BuildingBase"]
```

It only understood `defName="X"`. **So every patch on an abstract inheritance parent was
unverifiable and therefore refused** — which did not check the technique, it ruled it out.

It now indexes the `Name` attribute of defs that declare `Abstract="True"`, and accepts `@Name="X"`
as a patch target. **The verification is real, not a waiver**: a `Name` on a *concrete* def is an
alias and is deliberately not indexed, and fault-planting a patch at `@Name="NoSuchAbstractParent"`
fails with *"exists neither in the game's Data nor in this package"*.

That matters beyond this checkpoint: patching an abstract parent is the only way to reach a property
of every building at once, and the toolchain had been quietly forbidding it.

---

## The proof, fault-planted seven ways

`.local/register/proof-gate-approach.py` — the **twenty-fourth** — asserts **22 claims** across
five groups, including that Core's `BuildingBase` really is abstract in the installed game, so a
rename cannot leave the patch silently reaching nothing.

| Planted fault | Exit | Caught |
|---|---|---|
| a conduit-class passable thing stops being allowed | 1 | ✓ |
| **the saved snapshot cell is protected instead of the live one** | 1 | ✓ |
| only the centre cell is tested, not the footprint | 1 | ✓ |
| **a thrown exception stops allowing the placement** | 1 | ✓ |
| an invalid approach cell starts reserving anyway | 1 | ✓ |
| the patch replaces the list instead of appending | 1 | ✓ |
| the refusal stops mentioning that flooring is allowed | 1 | ✓ |
| *restored* | **0** | — |

The last one is not cosmetic: a carve-out nobody is told about is a carve-out that does not exist as
far as the player is concerned.

---

## Receipts

| | |
|---|---|
| Version | 0.12.27-dev |
| Build | **175 C# files, 87 package files**, **0 warnings, 0 errors** |
| Assembly | `977BC6016FDF88FEADA0E7DA032BD5F8074DCB2C81E5078478B269D2E5B6CF2C`, identical across two clean rebuilds |
| Owner questions open | **zero** — this closed the one that was |
| Other mods' files touched | **none.** One addition to a Core abstract parent |
| Register | `use RR-GATE`; two construction-family instructions applied |
| Checkers | **ten**, all passing, one of them extended to make this verifiable |
| Proofs | **twenty-four**, all exiting zero |
| Planted faults caught | **7 of 7**, plus 1 of 1 on the checker extension |
| Game launched | **no.** Nobody has tried to wall a gate shut |
