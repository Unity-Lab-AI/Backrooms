# The warren, the map budget, and a doorway you can carry — 0.12.50-dev

Stages two through four of the coordinate rebuild, all of them answers to direction given inside a
single session.

## The direction, verbatim

> *"dont let them go more than 5 remember the games mechanics and limits built in if they find a
> gate to a world map tile or a deeper backrroms and they have 5 mpas they should gett a warning
> this gate is blocked your holding open too many gates, but per scerio styled"*

> *"5 is the limit of other colonies available so a backrooms level should be one colonly bacskicly
> in my thinking"*

> *"and everything doesnt have to be square rooms and rectangle halways"*

> *"yeah so if the player discovers and goes through a natural gate how do they turn them off to use
> the machine gates for more controll and aiming deeper?"* / *"get 5 natural gates u cant use a
> machine gate"*

> *"so we need a way to deconstruct natural gates too i think"* / *"and then u lose them forever but
> maybe allow minify move"* / *"they are just doors too right that dont need the mechine gate
> systems"*

> *"make sure u are using prep and mod registry as needed"*

## The register found something none of our own code could have

That last instruction paid for itself immediately, and it is the reason this record leads with it.

Register row **[188] Removable Mt.Rock Roof Patch** (Workshop `1541438898`,
`Proxyer.RemovableMtRockRoofPatche`, *Facilities and spatial construction*, Optional, Provisional)
is **installed in this profile**, and its patch is:

```xml
<xpath>*/RoofDef[defName = "RoofRockThick"]/isThickRoof</xpath>
<value><isThickRoof>false</isThickRoof></value>
```

**So in this player's game, Core's overhead mountain is not thick.** And
`RoofDef.VanishOnCollapse => !isThickRoof`, which means it **vanishes on collapse and leaves open
sky.**

That breaks invariant 13 — *a Backrooms coordinate has no outside* — and **it was already broken
before this session's work.** `BackroomsContainment` argued that thick roof "never vanishes", which
is true of unpatched Core and false here. A coordinate roofed with `RoofRockThick` in this profile
could be mined into a hole in the world.

Two consequences. **The non-collapsing roof def introduced for the cave-in direction also repairs
that breach**, because it carries its own `isThickRoof` that nothing patches. And it is a second,
independent reason patching `RoofRockThick` would have been wrong: two mods editing one def at
startup, resolved by load order, with that mod asking to be loaded last.

Also checked and clear: **[69] Craftable Mountains** only *sets* `RoofDefOf.RoofRockThick` from its
own assembly, so it consumes the def rather than redefining it; **[63] Change map edge limit**
affects player map sizing, and a coordinate is a fixed size this mod creates.

## The map budget: five places, and the number comes from Core

`RimroomsDestinationMapParent.ShouldRemoveMapNow` returns **false, always** — a coordinate is a
place you go back to, so its map is never unloaded. Free at 3,600 cells; not free at **90,000 with
~70,000 mineables**, against a `MaximumCoordinates` of **512**.

The owner's first answer was eviction. They replaced it with a hard cap, and it is better on every
count: **nothing the player looted or built ever resets**, memory is bounded by construction rather
than by a policy that runs later, and the limit is **diegetic** — *you are holding open too many
gates* is a fact about the fiction, not an apology about memory.

**And the number is read, not written.** `Prefs.MaxNumberOfPlayerSettlements` is a player slider
from **1 to 5**, which Core enforces in `SettleUtility` as
`count >= Prefs.MaxNumberOfPlayerSettlements`. That is the *"limits built in"* the direction points
at. Core's own count is `map.IsPlayerHome && map.Parent is Settlement` plus gravship landings, and
**it cannot see a coordinate map** — so `OpenMapBudget.Held` counts both. *"A backrooms level should
be one colonly bacskicly."* A scenario may override the budget, which is *"per scerio styled"*.

**A floor of 2 is load-bearing.** The slider can be set to **1**, and the solo/group start opens a
coordinate during `PostGameStart` when the surface map already counts as one held place. Without the
floor that scenario would refuse its own opening on a clean new game.

### Where it is enforced, and the one place it deliberately is not

`NaturalFrontierService.Discover` refuses before `CreateDiscoveredCoordinate`, so a blocked gate
leaves no half-minted coordinate recorded against the branch. `DestinationService.EnsureSite` is the
backstop, and only when `coordinate.Site == null` — recalling a place that already has its map must
never be refused.

**The budget is checked after the way-out attempt, on purpose.** A doorway may lead *out* instead of
deeper, and a way home **costs no map**: it records a world tile rather than minting a place.
Checking the budget first would strand a crew that is deep and full up with nothing but the route
they walked in by — the same trap the depth cap is explicitly ordered to avoid. **The budget stops
the mod opening another place; it never closes the last door home.**

### And discovering is free — **WRONG, corrected at 0.12.51-dev**

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
player may find many natural gates at no cost; what costs a slot is a place left open.*

## Ways onward now scale with the size of the place

Two was right for a six-room 60×60 coordinate. `FrontiersFor` gives **4 to 6**, one more per 20
rooms, read from the coordinate's own room count rather than its depth so it stays correct if the
planner's depth profile moves again. `MaximumNaturalDepth` is **6**, up from 3.

**What made that safe is the budget, not a change of mind about finiteness.** The old cap's own
summary said raising it was a design decision because the cap was the only thing keeping the chain
finite. It no longer is.

**Two proofs correctly objected** to these changes, because they encoded the previous owner
decisions. What those restraints were ever protecting is kept and asserted **harder**: no research
capability may buy more ways onward or reach further, now checked by reading `FrontiersFor`'s own
body rather than by inspecting the shape of an assignment.

## Rooms are not rectangles and hallways are not one width

A room's `Bounds` stays a rect, because the validator, the doors, the corridors and the pillar
lattice all read it. What changed is **which cells get carved out of the rock.**

`RockIntrusionCells` leaves rock standing **only in the corners**, as quarter-ellipses so the edge
presented to the room is curved, **never on the centre cross and never at an edge midpoint.** That
one restriction buys four things at once:

- every doorway opens onto clear floor;
- a straight walk from any doorway to any other stays clear, so **no shape can disconnect a room**
  and no candidate is ever rejected for having one;
- the pillar lattice needs no special case, because rock already holds roof;
- the intrusions are `Mineable`, so a player who wants the rectangle can dig for it.

**Proved rather than argued:** the proof fills every corner at the deepest reach and flood-fills
from the room centre to all four edge midpoints, at every depth. Depth 1 gets no deformation at all,
for the same reason `Derange` leaves it alone — the yellow rooms read as a place because they are
monotonous, and the wrongness is travelled toward.

Corridor width comes from `CorridorHalfWidthBetween` — three cells or five — and **the planner reads
the same function the generator carves from**, so the reachability proved is the reachability built.

## A natural gate is an object you own

The owner asked whether they are just doors. **They are, and that was measured rather than
inferred**: the natural gate in their running game was a plain `RimWorld.Building_Door` in steel,
already offering Deconstruct, Uninstall, Reinstall and the emergence gizmo, with no power, console,
calibration or assembly.

**Destroying one already ended its route**, and the player was already warned with informed consent
— `PortalDoorWarningMapComponent`, written to the owner's earlier words. Nothing had to change.

**Carrying one did not work, and now does.** `RimroomsPortalNetwork.EndpointPresent` requires
`Anchor.Position == AnchorCell`, and `PortalEndpointRecord` says outright that the cell is a
deliberate snapshot so *"moving a door cannot silently redirect a saved route"*. Correct under the
old rule that naturals could not be moved; wrong under *"maybe allow minify move"*.

`TryFollowMovedAnchor` is not a refresh, it is a **move**, and it keeps the three properties the
snapshot was protecting:

- it only ever follows the **same `Thing` instance**, so a route cannot be captured by rebuilding a
  lookalike door in the same cell;
- it refuses unless the door is spawned, player-owned and on ground the branch owns — the same test
  registration had to pass;
- **it is refused outright while a crossing is in flight**, which is invariant 55. The route is left
  broken and visible rather than re-pointed under a traveller.

Loading a save is **not** a move: `respawningAfterLoad` returns early, or every load would re-anchor
every route.

And uninstall and deconstruct **stop saying the same thing**. Telling a player the same sentence for
both would be telling them something false about one of them, and the red destructive confirmation
is reserved for the one that is.

## Verification

**Two proof files were extended and one plant suite was written.** Totals: **thirteen checkers,
forty-one proofs**, and in this checkpoint **62 of 62** planted faults in
`plant-coordinate-layout.py` and **15 of 15** in `plant-gate-links-carry.py`.

**Eight of my own claims were too loose and plants found every one.** They are worth listing,
because they are all one family and the family keeps recurring:

| What the claim read | Why the plant walked past it |
|---|---|
| `"Prefs.MaxNumberOfPlayerSettlements" in budget` | the name is also in the **doc comment** above the code |
| `"RR_Frontier_TooManyGatesHeld" in keyed` | it is a **prefix** of `…HeldUnused` |
| `"MaximumFrontiersPerCoordinate" in frontier` | the **declaration** survived while the *use* was deleted |
| `"return false;" in parent` | that shape appears **four times** in the file |
| `"if (x == center.x …)" in planner` | stage three added the **same line** to a second function, and the harness replaces only the first |
| `genstep.count("RockIntrusionCells") == 1` | a **comment** mentioning the name counted |
| `find(a) < find(b)` across a file | `SetRoof(cell, overheadRoof)` appears **twice**, so the wrong pair was compared |
| `"!receipt.IsTerminal" in crossing` | it appears **seven times** in that file |

Every one is now scoped to the method body, the exact tag, or the call site. **A claim about code
must never be satisfiable by a comment, a prefix, a declaration, or a duplicate.**

**And the heredoc rule earned its place twice more.** A bash heredoc mangled escapes in two
separate register scripts this checkpoint — the seventh and eighth times in two days. Both were
rewritten as files.

## Build

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`0B307BD06299AE6EA7028267A1663D5D15315F540FEBDD8898432E60F1150599`, reproduced by two clean
recompiles. Staged to Local Mods and hash-verified; the game was not running.

## The one piece deliberately not shipped — **SHIPPED at 0.12.51-dev**

> The three things named below were built exactly as described: the save-schema field on
> `CoordinateRecord` (`releasedByPlayer`), teardown ordered so nothing is ever orphaned, and the
> refusal set. See `RELEASE_A_PLACE_IMPLEMENTATION.md`.

## The one piece deliberately not shipped, and exactly what it needs

The owner chose **an Operations "held places" list with a Release button** as the way to free a slot
so a machine gate can aim deeper. **It is not in this build, and it is not half-built either.**

Releasing a place is not a UI problem. It needs three things this checkpoint could not give the care
they deserve:

1. **A save-schema field on `CoordinateRecord`.** `EnsureSite` deliberately refuses to regenerate a
   coordinate whose rooms have been surveyed — *"a broken reference must not create a competing
   owner or replace an already explored graph"*. After a **deliberate** release, regenerating that
   same graph is exactly what is wanted, and the only honest way to distinguish the two is a flag
   that says the player let it go.
2. **Map teardown that cannot orphan anything** — the world object, the coordinate's `Site`
   reference, and any portal edge pointing into it.
3. **A refusal set**: crew on the map, a crossing in flight, or the headquarters itself.

Get any of those wrong and the result is an unreachable place or a dead record, which is the exact
defect class that cost this project thirty-nine checkpoints. **It is the next checkpoint, first
thing.**

Until then the practical position is unchanged for a fresh game: **discovering gates is free**, and
a player only meets the cap after holding five places open, which is many hours in.

## Still open from the same direction

The **wild variation of materials** across items, equipment, walls, floors, lights, furniture and
benches, with the events, layouts and loot that go with it deeper in.
