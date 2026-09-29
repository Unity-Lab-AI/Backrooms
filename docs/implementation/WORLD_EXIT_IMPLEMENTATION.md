# A way out into the world — 0.12.21-dev, 2026-09-29

**Dated record.** Never rewritten. Closes the last genuinely unbuilt piece of the portal topology,
and narrows one guarantee by owner decision.

---

## The owner overruled my caution, and was right to

I had parked this because it moves pawns between maps — the one bug class that can *lose* a
colonist — and cannot be verified without launching the game.

> *"okay and remember test cases arnt being worried about right now we are trying to get the build
> complete so we can test"*

Unverifiable-without-a-launch is not a reason to slow the build. It is built.

---

## The gap was worse than the row said

The row described a missing feature. The reality was a **dead end.**

`TryRecordWayOut` required a **marked anchor on a map the branch already owned**. With nothing
marked it returned null — so the draw that said *"this door leads out"* silently produced a way
**deeper** instead. **A branch with no marked door could never find a way out at all**, which is
worst for exactly the player least equipped to deal with it: somebody who started inside with no
company.

---

## A caravan, not a new world object — and the `trace` column settled it

The register's **`RR-OUT`** trace groups the rows that bear on *"a way out into the world"*. Querying
it returned the four Settled transport mods that actually matter here:

| Row | Mod |
|---|---|
| 61 | Carryalls \| Intercontinental Transport |
| 98 | Giddy-Up 2 |
| 159 | Pack Mules Extended |
| 266 | Alpha Vehicles – Age of Sail |

**All four already integrate with caravans. None integrates with a bespoke world object of ours.**
Nothing in the `family` column would have grouped those four together — that is what the trace
column is for.

And Core already has *"people standing on a world tile you do not own"*: a caravan. A new
`WorldObjectDef` plus generated map would duplicate it and touch world generation, the most
compatibility-sensitive surface there is with 294 mods. **Acquisition stays RimWorld's; recognition
is ours** — the same rule arc 5 settled for remote sites.

---

## The guarantee conflict was real, and was the owner's to settle

Forming *any* caravan calls `PassToWorld`. The stranded-crew guarantee says **no gate source ever
may**, because *"a pawn in the world pool is alive and no longer the player's."*

I stopped and asked rather than deciding — and said plainly that `proof-stranded-crew.py` only
watches `Gate/*.cs`, so shipping this in `Portals/` would have **passed on a directory
technicality.** That would have been evading the guarantee, not honouring it.

> **Owner decision: build it — a player caravan is still yours.**

The narrowing is exact, and the forbidden paths are asserted **by name** rather than by location:

| Path | May reach `PassToWorld` |
|---|---|
| a gate **closing** on a crew | **never** |
| a return **window expiring** | **never** |
| any **traversal** or crossing | **never** |
| walking out, **on a player's click** | yes — into something they control |

### In the event, our source gained no new call at all

The only route is inside Core's own `ExitMapAndCreateCaravan`. Our one direct `PassToWorld` is
**pre-existing** and releases a **declined job applicant** — somebody who was never the player's.
The proof asserts that this is the only caller in our source, that the world exit never calls it
directly, and that gate sources and traversal still never do.

---

## The five-map cap improved the design rather than constraining it

> *"lets have that 5 map count be universal max for back rooms main map and claiming maps where u
> pop out and anything over 5 maps defaults to caravans"*

Two outcomes:

| Maps held | What happens | Touches `PassToWorld` |
|---|---|---|
| **under** the cap | the tile is **claimed** via Core's `SettleUtility.AddNewHome` and the crew walks onto a new map | **no** |
| **at or over** it | the crew forms a **caravan** they control | yes |

**The common case never touches the narrowed guarantee at all.** It is not reached until somebody
already holds five maps.

### The stricter of two caps wins

- **Ours**: five, counting the Backrooms coordinate the crew is standing in — the owner's cap is on
  maps *held*, and a coordinate is a map held.
- **The player's**: `Prefs.MaxNumberOfPlayerSettlements`, read through Core's own
  `PlayerSettlementsCountLimitReached`.

**Somebody who set that to one meant it.** This mod does not get to overrule a setting the player
chose.

---

## Nobody can be lost

- **The claimed map is generated before any pawn is despawned.** If settling or generation fails,
  nothing has moved and the way out is still there. That ordering is the whole safety property.
- **A failed spawn puts that pawn back** where it stood.
- **Prisoners, slaves and the downed are never taken** — invariant 17, and somebody unconscious on
  the floor is not walking anywhere.
- **Only the player's own pawns leave.**
- A claim that moves nobody is reported as a **refusal**, not a success.

Invariant 55: a transfer that can lose a pawn is a corruption, not a threat.

---

## The destination is Core's choice

`TileFinder.TryFindNewSiteTile` already refuses water, space and impassable terrain, and already
honours every mod that patches tile validity. Our own test would be a second opinion that disagrees
with the game the first time somebody installs a biome mod.

The roll is wrapped in a **seeded `Rand` state** derived from the coordinate's seed and the door's
position — an unseeded roll would be a different world on every load.

**`PlanetTile` is a readonly struct and not `IExposable`**, with a private `layerId`. Both halves are
saved and the tile rebuilt: losing the layer would put a crew on the wrong planet layer, which reads
as a teleport bug rather than a save bug.

---

## Fault-planted seven ways

| Planted fault | Exit | Caught |
|---|---|---|
| a direct `PassToWorld` added to the world exit | 1 | ✓ |
| our five-map cap removed | 1 | ✓ |
| the player's own settlement limit ignored | 1 | ✓ |
| a prisoner made takeable | 1 | ✓ |
| a failed spawn no longer puts the pawn back | 1 | ✓ |
| the map no longer generated before despawn | 1 | ✓ |
| **the no-anchor dead end restored** | 1 | ✓ |
| *restored* | **0** | — |

---

## Receipts

| | |
|---|---|
| Version | 0.12.21-dev |
| Build | **174 C# files**, 91 package files, **0 warnings, 0 errors** |
| New `PassToWorld` calls in our source | **zero** |
| Callers of the leave routine | **one**, a player command |
| Map cap | **5**, or the player's own limit if stricter |
| Owner topology rows closed | **5** |
| Checkers | **nine**, all passing |
| Proofs | **twenty-one**, all exiting zero |
| Planted faults caught | **7 of 7** |
| Game launched | **no** — this moves pawns between maps and **nobody has watched it happen** |
