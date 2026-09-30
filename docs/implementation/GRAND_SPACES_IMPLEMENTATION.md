# Grand spaces, pillars, and the Backrooms stop caving in — 0.12.49-dev

**Stage one of the coordinate rebuild.** A Backrooms level was 60×60 with a hard-coded 3×3 grid of
eight slots at 19-cell spacing, producing 6 to 8 rooms of 10 to 16 cells. Every one of those
numbers was a constant. It is now a function of depth, and **depth 1 is six halls eighty cells
across.**

## The direction, verbatim

> *"and everything doesnt have to be square rooms and rectangle halways and u can use walls as
> pillars making the 0 level rooms be grand large spaces and leas than 60-100 romms and this can
> propigate depper with the wild variatiosn of material typeds in all items equaipment walls floors
> lights furnature and benches that are found everywher deeper in with wild random events and
> layouts and spawns to find and loot!!!!!!"*

> *"and remember backrooms can not and shall not have cave ins so removing walls floors columns
> shall not cause mountain overhead to column collapse"*

> *"tgis is only for backrooms"*

The first of those **revised** an answer given an hour earlier — a 60-to-100-room dense warren —
and it is the better call. A hall eighty cells across cannot fit in a 19-cell slot, so the room
count going *down* is what pays for the rooms getting grand.

## What scales with depth now

| depth | slots | spacing | room span | rooms | pillars/room |
|---|---|---|---|---|---|
| 1 | 3×3 | 90 | **80** | **6** | 144 |
| 2 | 4×4 | 68 | 58 | 10 | 64 |
| 3 | 5×5 | 54 | 44 | 16 | 36 |
| 4 | 6×6 | 45 | 34 | 24 | 16 |
| 5 | 7×7 | 38 | 28 | 32 | 9 |
| 6 | 8×8 | 34 | 24 | 42 | 4 |

Verified at every depth: no room lands off the map, every span is even so `CellRect.CenterCell`
stays on the slot centre where doors and corridors are aimed, and there are always **10 cells of
rock between neighbours** for a corridor to carve through.

The shape is a **serpentine chain** through the slot grid — row-major with alternating direction —
so consecutive rooms are always grid neighbours and the chain is connected without a search. Dead
ends hang off it from slots the chain walked past. `threshold_room`, `office_copy` and
`return_gallery` stay unique because something depends on there being exactly one: the gate anchor,
the evidence book, and the way out. The rest repeat.

## The pillars, and what they are actually for

The owner named them, and they are what makes an eighty-cell room a hall rather than a field.
`RoofCollapseUtility.RoofMaxSupportDistance` is **6.9**, so the lattice sits at **6**.

**The lattice is decided in `RoomLayoutPlanner.PillarCells` and nowhere else.** The generator
spawns from it and `CandidateIsSafe` proves the room is still walkable with them in it — before any
map exists. Two places deriving the same lattice independently is *precisely* the defect that
stopped every coordinate generating for thirty-nine checkpoints, one checkpoint ago.

**Never on the centre cross.** Doors and corridors meet a room at the midpoint of each wall, so the
centre row and column are left completely clear: a straight walk from any doorway to any other
cannot be blocked, whatever the room's size. The narrowest free run between pillars is **5 cells**
at every depth.

This replaced a single wall at the room's centre cell — right for a 14-cell room, pointless in an
80-cell one, and it sat on the centre cross the lattice now deliberately keeps clear.

## The Backrooms do not cave in, and only the Backrooms

**The existing code was wrong about this, and its comment hid how wrong.** `BackroomsContainment`
reasoned from `RoofDef.VanishOnCollapse => !isThickRoof` and concluded a coordinate "can be mined to
nothing and still never open a hole in the world", treating the collapse itself as acceptable.

Half right. No *hole* opens — but Core gates every cave-in on **`RoofDef.canCollapse`**, which
**defaults to `true`** and which Core sets false on **none of its three roofs**. So `RoofRockThick`
still drops `CollapsedRocks` and **crushes whatever stands underneath.** Verified in
`RoofCollapseCellsFinder.ProcessRoofHolderDespawned`:

```csharp
... && roofGrid.RoofAt(intVec).canCollapse && !RoofCollapseUtility.WithinRangeOfRoofHolder(intVec, map)
```

**Patching `RoofRockThick` was considered and refused.** It would stop mountains collapsing in
every colony, for this player and every other mod in the profile. The owner drew that line
themselves, in the same minute: *"tgis is only for backrooms"*.

So there is a **roof def of our own**, `RR_RoofBackroomsOverhead`, with `canCollapse false`. It is
the right unit for this:

- a `RoofDef` is a `Def`, not a `ThingDef`, and it carries **no texture, graphic or audio we
  author** — roofs are drawn from the map mesh. This stays inside the existing-content-only rule.
- `isThickRoof true` is what makes it behave as overhead mountain everywhere that matters:
  `DropPodUtility`, `DropCellFinder`, `Projectile`, `Bombardment`, `RoomTempTracker`, `Fire`,
  `Building_TurretGun`, `SectionLayer_IndoorMask`, `SectionLayer_LightingOverlay` and
  `Designator_AreaNoRoof` **all read the flag, not the def's identity.** Invariant 13 needs that: a
  Backrooms coordinate has no outside.

**What is knowingly given up.** Two places in Core compare the def itself. `RoofGrid.GetCellExtraColor`
tints `RoofRockThick` gray in the roof-overlay view, so ours draws white there — cosmetic, inside
one toggle. And `MechClusterUtility` avoids cells whose roof *is* `RoofRockThick`; mech clusters are
a colony-map incident and do not target coordinate maps.

**What this does not claim.** `canCollapse` closes the reachable path. It does not gate
`CheckCollapseFlyingRoofAtAndAdjInternal`, which marks a roofed region carrying *no* roof holder
anywhere in it — and in a coordinate every cell is roofed and the space between rooms is solid rock,
so that region holds tens of thousands of holders. Emptying it would mean mining the entire map and
deconstructing every wall.

A single accessor, `BackroomsContainmentMapComponent.OverheadRoof`, resolves it by name with a
fallback to Core's thick roof, so a package missing the def degrades to vanilla behaviour rather
than generating a coordinate with a sky. The fallback *can* cave in, which is strictly worse and
still better than a hole in the world.

## Ninety thousand cells of rock

`FillWithRock` now suspends `map.regionAndRoomUpdater` for the duration, which is what Core's own
`GenStep_RocksFromGrid` does and for the same reason: every spawn would otherwise ask the region
grid to re-partition the map. At 60×60 that was 3,600 cells and nobody noticed; at 300×300 it is up
to 90,000. The flag is restored in a `finally`, so a throw mid-fill cannot leave the map with region
updates switched off.

## The forty-first proof, and the blind spot that made it necessary

**A coordinate's geometry had no proof coverage at all.** That is measurable rather than asserted:
**every constant in `RoomLayoutPlanner` was changed and all forty existing proofs still passed.**
Not the map size, not the room count, not the room dimensions, not the spacing, not the graph's
connectivity. The most complex generated artefact in the mod was unwatched — which is exactly how a
light count stopped every level generating for thirty-nine checkpoints.

`proof-coordinate-layout.py` **parses the constants out of the C# and recomputes from them.** It
hard-codes no number. Change `Margin` and it recomputes with the new margin and still asserts rooms
land inside the map.

**And a plant found a hole in that design.** Because the proof copies the *formulas* while parsing
the *constants*, deleting a step from the algorithm is invisible to it: a plant that removed
`if (span % 2 != 0) { span--; }` walked straight past the computed evenness claim, since the model
was still doing the subtraction itself. **Every modelled formula is now paired with a source claim**
that the step still exists in the C# — the model asserts the property, the source claim asserts the
code still computes it. One without the other is the mention-versus-assertion defect again.

`plant-coordinate-layout.py` is the **twelfth plant suite**: **34 of 34 caught**, including two of
my own plants that were wrong rather than the proof being wrong — `Margin = 1` does not push rooms
off the map, because the spacing grows as the margin shrinks and the arithmetic self-corrects.

`proof-interior-resource.py` **also caught this change and objected correctly** — it asserted
`RoofDefOf.RoofRockThick` by name. The property worth asserting was never "it uses that particular
def"; it is that the roof is thick, so no sky, and non-collapsing, so no cave-in. It asserts both
now.

## Build

**199 C# files, 91 package files** (the new `RoofDef`), zero warnings, zero errors. Assembly SHA-256
`A17D99ED025EAAA975011D05F588BBB735793165EFF9E8E4881E2A18B26EEB13`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-one proofs hold.** 34 of 34 planted faults caught in the
new suite.

## This needs a fresh save, by owner decision

Owner answer, when asked: **fresh save, drop the 60×60 path.** One shape, simplest code, cleanest
proofs. `PlannerVersion` is 3 and every layout fingerprint changes, so an existing coordinate will
refuse to generate rather than silently becoming a different place.

## What is deliberately NOT in this stage, and why

The owner chose **4–6 onward gates per level and `MaximumNaturalDepth` 3 → 6**. Those are **held
back on purpose**, because of something measured while implementing this:

**`RimroomsDestinationMapParent.ShouldRemoveMapNow` always returns false — a coordinate map is never
unloaded.** Harmless at 3,600 cells. At 90,000 cells and ~70,000 mineables per level, with 4–6 gates
and depth 6 making hundreds of levels reachable against a `MaximumCoordinates` of **512**, raising
the fan-out *without* eviction is what would kill the game.

The owner's first answer was to cap loaded maps and evict the least recently used. **They then
superseded it with a better one**, verbatim:

> *"dont let them go more than 5 remember the games mechanics and limits built in if they find a
> gate to a world map tile or a deeper backrroms and they have 5 mpas they should gett a warning
> this gate is blocked your holding open too many gates, but per scerio styled"*

**A hard cap of five maps and no eviction at all.** That is strictly better than evicting, on three
counts: nothing the player looted or built ever resets; memory is bounded by construction rather
than by a policy that runs later; and the limit is **diegetic** — *you are holding open too many
gates* is a fact about the fiction, not an apology about memory. It is also what *"remember the
games mechanics and limits built in"* points at, because many loaded maps is a RimWorld constraint
before it is ours.

**"per scerio styled"** means the budget belongs to the scenario, so a start can be given a
different one rather than every game sharing a constant.

**That and the raised gate count ship together as stage two**, because either alone is wrong: the
cap without the gates is pointless, and the gates without the cap is what kills the game. Gates
stay at 2 and depth at 3 here, which keeps reachable levels at about seven and is safe with nothing
bounding them.

Still open from the same direction, for later stages: non-rectangular rooms and corridors, and the
wild variation of materials across items, equipment, walls, floors, lights, furniture and benches
with the events, layouts and loot that go with it.
