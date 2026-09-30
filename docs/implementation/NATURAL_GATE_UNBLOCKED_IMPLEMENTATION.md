# A light count took every Backrooms level down for thirty-nine checkpoints — 0.12.48-dev

**The most expensive defect this project has had, and the cheapest to state:** a validator counted
things of one def and required the total to match a formula built from a different def. From
**0.7.8-dev** to **0.12.47-dev**, no Backrooms coordinate could generate. Nothing caught it,
because every proof reads source text and nothing had ever run the generator until a player walked
up to a gate.

## The report, verbatim

> *"okay check it the store and pawns are there now but i dont see a natural gate thats suppose to
> be on the back wall of one of the storage rooms so that they can eneter theri 300x300 gate ie the
> stargate mode that prcedurally generated the backrooms of diffent levels with thir natual gate
> spawns to different levels within"*

> *"kill it again when rimsort is ready for m,e and u are done checking the old runtime test"*

> *"make sure to push to both remotes too i need someone else to work on this in parrellel through
> git hub and i need to make sure they have it all but the temp stuff i told you to git ignore"*

## The door was there. It was never marked.

Read live from the owner's running game before anything was changed:

| Read | Result |
|---|---|
| `get_cell_info` (160, 161) | a **steel `RimWorld.Building_Door`**, walkable, under `RoofConstructed` |
| its gizmos | `Deconstruct`, `Uninstall`, `Reinstall at...`, **`Mark as way home`** — all enabled |
| `get_cell_info` (133, 135) | a **granite-block `Wall`** on Concrete, where 0.12.47-dev's burn removed a Granite formation |
| `get_game_info` | `mapCount: **2**` — the Backrooms level had been created |
| `list_letters` | one letter: *"Room content placement stopped; the existing site is retained."* |

So the physical door existed, in the right cell, carrying the emergence component with its gizmo
live. **What was missing was the marking**, and the reason is a chain:

`SoloGroupOpening.Open` runs in order — coordinate, **site**, mark the door, register the
connection. Step 2 failed, so steps 3 and 4 never ran. The door stayed an ordinary steel door.

And 0.12.47-dev's burn is confirmed working in the same breath: a wall stands where the granite
formation stood.

## Why step 2 failed

`GenStep_BackroomsDestination` threw `RR_Generation_ContentPlacementFailed` out of
`ValidateNativePowerNetwork`, which required:

```
count(things where def == lightDef)  ==  Rooms.Count + Rooms.Count(service_passage or utility_room)
```

The extra lamps in that sum are placed by `RoomContentBuilder`, which spawns a hard-coded
**`StandingLamp`**. The formula was correct while `lightDef` was also `StandingLamp`.
**`BackroomsPalette` switched the fixture to `WallLamp` at 0.7.8-dev** — a deliberate improvement,
recorded and argued for in that file — and from that moment the count of `WallLamp`s could never
include the `StandingLamp`s the formula expected.

`climateRoom` is `FirstOrDefault(utility_room) ?? First(service_passage)`, so **at least one such
room always exists.** The shortfall was not a rare case. It was arithmetic.

There is a comment three hundred lines away that proves the author knew:

> *RoomContentBuilder adds another Core lamp to every service/utility room after this method. Wire
> each such room first so those later loads join the real native network.*

The knowledge was there. The coupling was by **count**, and a count cannot notice that the thing
being counted changed identity.

## The fix: stop predicting, start observing

`ValidateNativePowerNetwork` no longer names a def or predicts a count. It takes the list of lights
the caller **actually spawned**, and its last check sweeps **every `CompPowerTrader` on the map**:

```csharp
foreach (Thing thing in map.listerThings.AllThings)
{
    if (thing == null || !thing.Spawned || thing.Map != map || consumers.Contains(thing)) { continue; }
    if (thing.TryGetComp<CompPowerTrader>() != null) { consumers.Add(thing); }
}
```

That is the invariant a player can actually see — **nothing here is dark or cold** — and it covers
`RoomContentBuilder`'s lamps without naming them, which is what the formula was trying and failing
to do by arithmetic. It cannot go stale when a palette or a furniture list changes.

## And it is reported, never fatal

The second half, and it is the same lesson as the three defects before it.

A coordinate whose heater failed to join the grid is dark, cold and **completely playable**. A
coordinate that does not exist **costs the player the gate that leads to it.** The power check now
returns a fault string and the caller logs a warning naming the coordinate.

`ValidatePlacedLayout` stays fatal, deliberately: entry, return and office cells standable, every
room reachable, one clue per room with a reachable inspection cell. **A coordinate you cannot walk
through really is broken**, and weakening that would trade one silent failure for another.

## The lamp was also in the wrong place, and it is the same root

`WallLamp` is `building.isAttachment` with a `Placeworker_AttachedToWall` and
`drawOffsetNorth (0,0,0.9)` — it draws almost a full cell **into the wall it is mounted on**. It was
being spawned on an open interior cell at `CenterCell + (0,0,2)` with `Rot4.North`, so it drew a
sconce hanging in mid-floor — and that also defeats the reason the palette chose it, which
`BackroomsPalette` states outright: *an endless corridor reads as endless precisely because nothing
is standing in it.*

`FindWallAttachmentCell` returns an interior cell with one of the room's **own wall def** behind it
and the `Rot4` that faces it. Not a door: a door holds up roof too, and a lamp mounted on a door is
mounted on nothing the moment it opens.

**It branches on `lightDef.building.isAttachment`, never on the string `WallLamp`** — the palette
still falls back to `StandingLamp`, which stands on the floor and must keep doing so. Naming the def
here would recreate the exact coupling that caused the outage.

**And it returns `IntVec3.Invalid` rather than throwing.** The threshold room holds the gate anchor,
the entry cell, the return cell and the anchor's whole expanded rect, so its wall-adjacent cells can
all be reserved. A lamp standing on the floor is a cosmetic compromise; a coordinate that does not
generate is not. This method exists *because* a light-placement rule took the whole map down.

## A correction, stated plainly

Mid-investigation this record's author reported `NaturalFrontierService` as orphaned — all three
public methods with zero callers. **That was wrong, and the mistake was in the search, not the
code:** the grep excluded the file that holds the caller, and the caller is a `JobDriver` in that
same file. The chain is whole and was verified end to end:

```
WorkGiverDef RR_SurveyFrontier  ->  WorkGiver_SurveyFrontier
  ->  JobDef RR_SurveyFrontier  ->  JobDriver  ->  NaturalFrontierService.Discover
```

`check-wiring.py` was right and this reader was not. The onward-gate machinery — ways deeper, ways
out to a world tile — exists and is reachable. **The only thing blocking it was that no level could
ever generate.**

## What the collaborator gets

Owner direction: *"i need someone else to work on this in parrellel through git hub and i need to
make sure they have it all but the temp stuff i told you to git ignore"*.

**`.local/` was hiding the verification suite.** A clone could run the 13 checkers in `tools/` and
**none of the 40 proofs or 11 plant suites**, because they live under `.local/register/`. Those are
neither machine-local nor temp — they are this project's primary instrument.

`.gitignore` now admits exactly two globs and nothing else:

```
.local/*
!.local/register/
.local/register/*
!.local/register/proof-*.py
!.local/register/plant-*.py
```

Git will not descend into an ignored directory, so the parent has to be re-admitted a level at a
time before a negation inside it can match — the same pattern as the existing `!.claude/bin/`.
Measured result: **51 files newly tracked, being exactly 40 proofs and 11 plants.** Still excluded:
a 132 MB nuget cache, 19 MB of decompiler binaries, the per-subsystem source inspections, the
scratch bridge client, and the hundreds of one-shot record/ship/fix scripts.

**A collaborator needs the same RimWorld install**: `tools/build.ps1` refuses to build unless the
Core assembly hashes to `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`.

## The proof, and the plant that walked past it

`proof-generation-batch.py` gained **nine claims**, `plant-generation.py` gained **fourteen plants**.

**One plant was missed on the first run, and it was the important one.** *"A POWER FAULT BECOMES
FATAL AGAIN"* inserted a `throw` inside the `if (powerFault != null)` block, and the claim passed —
because it asserted that `Log.Warning` and `if (powerFault != null)` were both **present**, which a
`throw` does not disturb. **A claim that a warning exists is not a claim that a throw does not.**

That is the sixth time this exact shape has defeated a claim in this project. The fix is the same
one that worked for the facility's `catch` block: read the block body on its own and assert `throw`
is absent from it. Sweep is now **28 of 28**.

## Build

**199 C# files, 90 package files**, zero warnings, zero errors. Assembly SHA-256
`D0441DC4DA5D1255362FA5D81865561A50C134984519E69E26739FB00508BEA4`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty proofs hold.** 28 of 28 planted faults caught in the
generation suite; 56 of 56 in the start-placement suite.

Staged to Local Mods and hash-verified. The game was closed on owner instruction, and **every read
in this record came from a process the owner started**.

## What launch six should settle

- the door in the Store's back room is a **natural gate**, not an ordinary steel door — its
  inspect string and the `RR_Event_NaturalGateOpening` event, not just the `Mark as way home` gizmo
- going through it reaches a **Backrooms level that exists**, lit and heated
- the lamps are **on the walls**, not floating in the corridors
- surveying doorways finds ways **deeper** and ways **out to a world tile**

## Queued next, decided by the owner this checkpoint

**300×300 Backrooms levels as a dense warren**, answered through four questions:

| Decision | Answer |
|---|---|
| level size | **300×300**, up from 60×60 |
| room count | **60–100**, a dense warren on a 10×10 planning grid at the existing 19-cell spacing |
| families | threshold / office_copy / return_gallery stay **unique**; the other five **repeat**; **new structural families** are authored (flooded_room, stairwell, dead_end, pillar_hall) — layout and dressing only, **no new ThingDefs** |
| onward gates | **4–6 per level**, one per ~15 rooms, and `MaximumNaturalDepth` **3 → 6** |
| saves | **fresh save, the 60×60 path is dropped** — one shape, simplest code, cleanest proofs |
