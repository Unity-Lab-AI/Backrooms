# The fourth launch: the site had to be prepared, not refused — 0.12.47-dev

**Two defects, and the second one is why the game was unplayable rather than merely wrong.** Both
came out of 0.12.46-dev handing map generation back to Core, which was the right fix and had a
consequence nobody paid for until a real launch.

## The report, verbatim

> *"i did a store start the map loaded correctly but i had pop up company could not finish startup
> company placement stopped... so wtf is up with this??? also the starting store structure was not
> built and i have no pawns on the map to control"*

> *"you can use the api mod you have that we installed last so u can see wtf rimworld is doing"*

> *"i think the issue was there was shit where it planned on putting the store and pawns so it
> errored it needs a like a burn into place functiions to carve everyhting out and cut everything
> down and fill in with soil where water is unmder where the store needs to propigate before game
> start"*

> *"and the store facilities walls floors and all of it have to be reconfigureable deconstructable
> and minifyable(the minify mod) just like the game with the mods allows"*

**The owner's diagnosis was right before any code was read**, and the fix is theirs by name.

## Measured, not inferred

This is the first checkpoint where the evidence came from the running game. RimBridgeServer
2.1.1 in direct mode, port and token read from the owner's own live log, read-only calls against
the owner-launched process. The log named the cause and the bridge confirmed it at the cell:

| Read | Result |
|---|---|
| `Player.log` | `Headquarters wall intersects generated structure at (133, 0, 135)` out of `HeadquartersBuilder.Build`, then `Error in GenStep: [Rimrooms] Native arrival requires the prepared headquarters receipt.` |
| `rimworld/get_cell_info` at (133, 135) | a **`Granite` `RimWorld.Mineable`, 900 hit points**, natural `RoofRockThin` above it |
| `rimworld/get_cell_info` across all **1020** footprint cells | **164 Marble** and **70 Granite** formations, **177** cells of natural rock roof, ~440 plant cells, 34 cells of rubble and chunks, **2 monkeys** |
| `rimworld/list_colonists` | **0** |
| `rimworld/list_letters` | exactly one letter, ours |
| `rimworld/get_game_info` | `game_loaded`, 1 map, tick 714 |

The footprint resolving to x 133 / z 135 is only consistent with a **300×300** map, so the owner's
*"the map loaded correctly"* is confirmed arithmetically as well as visually: 0.12.46-dev's map fix
held.

**234 of 1020 cells held natural rock.** The build did not hit a rare collision; it had no chance,
and it threw on the footprint's very first cell.

## Defect one: the facility refused ground it did not own

`Build` threw `Headquarters wall intersects generated structure` at the first occupied cell. That
was survivable while a generator of ours handed it flat, empty Soil. It is indefensible now that
Core generates the tile — and refusing was the wrong instinct in the first place. **Every vanilla
structure gen step clears what is under it.**

The fix is in two halves, and the first is the one that keeps the map looking like a map.

### Prevention: the rock is never generated

`GenStep_RocksFromGrid` spawns a formation in every cell whose `MapGenerator.Elevation` exceeds
**0.7**, and natural rock roof above 0.728 and 0.798. It runs at **order 200**. Core's
`ElevationFertility` builds that grid at **order 10**.

`RR_HeadquartersTerrain` moved from **order 5 to order 100** — between the two — and lowers
elevation across the site to **0.55**. No formation, no natural roof, nothing to demolish. At its
old order of 5 the grid did not exist yet, and any terrain it wrote was overwritten by Core's
`Terrain` step at order 210, so that step was doing nothing useful at all.

That is the difference between a building on open ground and a building at the bottom of a
234-cell hole carved out of a mountain.

### The burn: everything else

`HeadquartersBuilder.BurnIntoPlace` runs **before a single wall is placed**, in one pass over the
site:

- **carves everything out and cuts everything down** — every thing in the cell destroyed with
  `DestroyMode.Vanish`, the thing list copied first because destroying mutates it
- **clears the natural rock roof** a formation leaves behind, which outlives the rock under it and
  would leave the facility in permanent darkness
- **fills in with soil where water is**, and where terrain is impassable, using the start's own
  `outdoorTerrain`

Ordered before placement deliberately: a site that cannot be prepared now fails **before** the map
has a half-built building on it.

**What it does not touch.** Nothing living: pawns are skipped by category. And a `Building` with a
faction is destroyed only after being **named in a warning** — that would mean another mod's gen
step placed a structure inside the footprint despite the `UsedRects` reservation, and the standing
rule is that a silent failure is the bug.

The `UsedRects` reservation is worth stating, because it is why the burn stays small:
`GenStep_ScatterRuinsSimple` and `GenStep_ScatterShrines` both read `UsedRects` at order 750 and
will not place on top of the facility. Registering the rooms at order 100 is what buys that.

## Defect two: the arrival killed Core's scenario step

**This is the one that made the launch unplayable, and it is the eight-defect pattern again.**

`ScenPart_RimroomsArrival.GenerateIntoMap` **threw** when the headquarters receipt was incomplete.
That method is called from Core's `GenStep_ScenParts`, and `MapGenerator.GenerateContentsIntoMap`
abandons a gen step at its first exception. So Core's **entire** scenario step died: no colonists,
no starting supplies. `list_colonists` returned zero on the live map.

A subclass of `ScenPart_PlayerPawnsArriveMethod` is an **addition** to Core's arrival, not a
replacement for it. When our own part of the work is not ready, Core's still has to happen. The
incomplete-receipt branch now logs the fault and calls `base.GenerateIntoMap(map)` — and still
records `arrivalStarted`, so a retry cannot re-enumerate the native starting-thing factories and
grant supplies twice.

Two smaller pieces of the same shape:

- the facility step's `catch` no longer re-throws. Re-throwing only reached
  `GenerateContentsIntoMap`, which logs and carries on, so it bought nothing — and it left the
  player standing on an arrival cell inside a building that does not exist. It now sets
  `MapGenerator.PlayerStartSpot = IntVec3.Invalid`, and Core's `GenStep_FindPlayerStartSpot` at
  order 850 picks a real one, because it only chooses when none is valid.
- the wall placement no longer checks for a generated edifice at all. The burn cleared it, and
  `GenSpawn.Spawn` wipes with `WipeMode.Vanish` by default.

## Reconfigurable, deconstructable, minifiable

The owner's fourth message. **It already held; the work was turning an assumption into a check.**

**Minifiable.** Register row **[128] MinifyEverything** (Workshop `872762753`, family *Facility
construction and material access*, Optional, Settled, traces RR-FAC / RR-OUT / RR-SPACEFLIGHT /
RR-COMPAT). Its installed assembly was read rather than its card: it mutates
`ThingDef.minifiedDef` and `building.alwaysUninstallable` for every qualifying def at startup,
skipping natural rock, zero-work defs, mineables and `Smooth*`. **It operates on defs, not
instances.** The facility is built from `ThingDefOf.Wall`, `ThingDefOf.Door` and the authored
furniture list — all Core defs — so whatever it does to a wall applies to ours identically. **A
ThingDef of our own would be outside its reach entirely**, which is the existing-content-only rule
paying for itself.

**Deconstructable.** Every placement is given `Faction.OfPlayer` before it is spawned, which is
all `Designator_Deconstruct` and `Designator_Uninstall` require, and nothing in the facility path
touches `designationManager`.

**Floors removable.** `TerrainGrid.SetTerrain` records the displaced terrain in `underGrid`
whenever the new terrain is `layerable`, and `CanRemoveTopLayerAt` needs exactly that. Concrete is
layerable. The burn's water fill is deliberately ordered first, so the under-terrain is Soil rather
than water.

**Reconfigurable — the one that needed measuring.** Deconstructing a wall under an unsupported
roof collapses it. `RoofCollapseUtility.RoofMaxSupportDistance` is **6.9**, and support is a flood
fill over roofed cells within that distance looking for a `holdsRoof` edifice. Replicating that
rule against all three layouts:

| Layout | Roofed cells | Wall cells | Unsupported |
|---|---|---|---|
| `RR_AsyncIndustriesStart` | 884 | 540 | **0** |
| `RR_FurnitureStoreStart` | 686 | 334 | **0** |
| `RR_SoloGroupStart` | 25 | 24 | **0** |

**Not one unsupported roof cell.** The Store's outer room is 34×30, far wider than a 6.9 span, and
it holds up only because the inner rooms' walls stand inside it. That was luck rather than design,
so it is a proof claim now — and the plant that deletes the Store's largest inner room is caught,
which is the measurement proving itself.

## The proof, and what the plants found

`proof-startplacement.py` gained **20 claims** and `plant-startplacement.py` gained **21 plants**,
plus one retarget: the old *"THE TERRAIN STEP FLATTENS THE WHOLE MAP AGAIN"* plant anchored on a
room-rect loop that no longer exists in the terrain step. A plant whose anchor has rotted away
**reports zero matches and aborts the suite**, which is the harness refusing to score a fault it
never planted.

The sweep is **56 of 56**.

**The interpreter caught one real mistake.** The new claims read
`ScenPart_RimroomsArrival.cs` into a variable named `arrival`, which the reachability section
already used for an `re.search` match object 200 lines later. `TypeError: argument of type
're.Match' is not iterable` — a name collision that would have silently passed had the two types
been compatible.

Claims worth naming because they assert an **inequality or an ordering**, not the presence of a
string:

- the terrain step's order is parsed as a **number** and checked as `10 < order < 200`. A test for
  the literal `100` would pass against `1000`; a test for the def name would pass against any
  order at all. Both plants — order 5 and order 300 — are caught.
- the burn's call site index must be **less than** the room loop's. A burn that ran after the walls
  were up would destroy the facility it had just built, and that plant is caught.
- the `catch` block is read on its own, because a `throw;` planted inside it changes nothing about
  the surrounding code.

## Build

**199 C# files, 90 package files**, zero warnings, zero errors. Assembly SHA-256
`85B6769552B8D94641A5DA8B93BB9514715FE90AE9087BC0106C528F60ECE540`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty proofs hold.** 56 of 56 planted faults caught.

Staged to the owner's Local Mods folder. **No game was launched by this work** — the running
process was the owner's, it was read from only, and the owner closes it themselves.

## What launch five should settle

- the Store stands on the tile and the map size the owner picked, on **open ground** with no rock
  crater around it, and the rest of the tile keeps its biome character
- **colonists and starting supplies are present** — the thing that was zero
- select a wall: **Deconstruct and Uninstall are both offered**, and Remove Floor works on the
  concrete
- deconstruct an interior wall and **no roof collapses**
- the back-room door nobody built, and the ways deeper or out to a world tile behind it
