# You are already in — 0.12.0-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

> ## ONE CLAIM IN THIS RECORD WAS CORRECTED THE SAME DAY
>
> Below, under *"Three things it deliberately does not do"*, this record says: **"There is no way
> home and finding one is the whole opening."**
>
> **That is wrong.** Owner direction, 2026-09-29, verbatim: *"and remember the solo/group start in
> a backroom needs to 100% have a exit to map natural portal on their first backrroms level with
> natural portals deeper to an extent till they would need to buidl theri own gate"*.
>
> The first level must hold a **guaranteed** natural portal out - not a discovered one, not a
> rarity draw. The body below is **left exactly as written**, because it is what the checkpoint
> shipped and the evidence trail depends on that. The correction is in `TODO.md`, in
> `FINALIZED.md`, and in the record for the checkpoint that fixes it.
>
> **Half of it was fixed immediately**, in the same session: natural portals now reach through
> depth 3 and no further, which is the *"to an extent"* half. The guaranteed exit itself is its
> own piece, because its destination is a world tile that does not exist yet.

---

## What this is

**The third and last of the chart's starts.** The mod now ships all three, and this one is unlike
the other two: **the map itself is a Backrooms coordinate**, wall to wall.

> *"remember the other one is solo/group start.. group have been known to end up together inside
> so leets use the in backrooms start to be 1-5 pawns player settable with normal set up or edb
> prepare carefully mod and or character editor"*

The stable scenario ID stays `lone_survivor`, because saves depend on it. **The name is
solo/group**, because the owner is right that groups go in together.

---

## The register, checked first

`Interface, scenario setup, and quality of life`, and the two rows that matter are named in the
owner's own direction: **[85] EdB Prepare Carefully** and Character Editor.

Both are answered by the shape the other two starts already use and this one repeats: the native
`ScenPart_ConfigPage_ConfigureStartingPawns` goes **first**, every starting item is a native
`ScenPart_StartingThing_Defined`, and the mod's own scen parts are `visible=false` and carry only
the start def. Those tools see an ordinary scenario. **`pawnCount` 1 with `pawnChoiceCount` 5** is
the 1–5 the owner asked for, through Core's own page, with no custom UI to go stale.

---

## No Harmony, and no trick

The hard part looked like forcing the *starting* map to be something other than a colony map.
It turned out Core already allows it, and this mod already used the hook.

```csharp
// Verse.Game.InitNewGame, decompiled
Map currentMap = MapGenerator.GenerateMap(intVec,
    settlement, initData.mapGeneratorDef ?? settlement.MapGeneratorDef, ...);
```

`GameInitData.mapGeneratorDef` is a **public field Core consults first**, and
`ScenPart_RimroomsStart.PreMapGenerate` has assigned it from the start def since the Async
headquarters was built:

```csharp
Find.GameInitData.mapSize = startDef.mapSize;
Find.GameInitData.mapGeneratorDef = startDef.mapGenerator;
```

So a start that wants to open inside the Backrooms **names a different generator**, and Core does
the rest. Map size comes from the same place, which is why the coordinate fills the map to every
edge instead of sitting as an island in open ground.

**Nothing was patched, nothing was reflected, and no other mod's defs were touched.**

---

## The shell is shared; the furniture is not

`GenStep_BackroomsDestination` is 768 lines and most of it is about a place reached **through a
gate**: a gate anchor in the threshold room, a return cell beside it, an evidence lead in the
office copy, a chemfuel generator and a conduit run. **None of that applies to people who are
simply already there.**

But underneath it is the part that must never differ, and it is now `BuildShell`:

- void terrain and **`RoofRockThick` over every cell**
- solid mineable rock filling everything that is not a room
- rooms **carved out of** the rock, keeping the thick roof
- corridors, walls, a centre support, and the doors

That block carries **invariant 13** — *a Backrooms coordinate has no outside, and its roof is
never removable*. The roof is `RoofRockThick` and deliberately never `RoofConstructed`, because
constructed roof can be taken off. **A second copy of this would drift, and what would drift out
of it is the promise that you cannot dig your way into open sky.**

Same reasoning as the `AnomalyEventService` re-scoping in 0.11.8: share the half that carries the
promises, and let each caller furnish its own.

---

## Three things it deliberately does not do

**No power and no lights.** The destination generator wires a generator and conduits because a
branch arrives with a gate behind it and a reason to light the place. **Nobody wired this one.**
The survivors have three glow pods and whatever else they were carrying, and the dark is the
point.

**No gate anchor and no return cell.** Those exist at a destination because something opened onto
it. Nothing opened onto this. **There is no way home and finding one is the whole opening.**

**The coordinate is not registered in the branch atlas.** It is the map the colony lives on, saved
whole like any colony map, so a reload cannot silently produce a different place — the
`SCENARIOS.md` requirement is met by the save rather than by a world object. Turning *where you
were trapped* into *a coordinate you can dial back to* is a **convergence** feature and belongs
with the escape route, not with the opening.

Each of those is an absence a player will notice, and each is cheaper and more honest than a
half-built version of the thing.

---

## Zero funding, zero wages, zero overhead

Async runs on a $50,000,000 allocation. The Store has 200 silver in the till. **This start has
nothing, and its wage and overhead are zero.**

Not as a balance decision — **there is no company here.** Nobody is being paid because nobody is
employing anybody, and nothing is being billed because there is no one to bill. The campaign's
payroll runs over a roster that costs nothing, which is exactly right until contact turns this
into a branch.

---

## The proof learned a second shape

`proof-starts.py` validates surface layouts by rebuilding them cell by cell. **An inside start has
no layout**, so every one of those claims is about a facility that does not exist. It now branches,
and asserts what is true instead:

| Claim | Why it matters |
|---|---|
| declares **no** rooms, doors, buildings or conduits | a facility would be built on top of a coordinate that is already wall to wall |
| uses the coordinate map size, **60** | `GenStep_InsideStart` refuses any other, so the start would fail at new game |
| names a map generator **the mod ships** | otherwise Core silently falls back to an ordinary colony map and the player opens on a hillside |
| each genstep resolves to a **real class** | a class named in XML and defined nowhere makes the step do nothing, with no error a player sees |

That third one is the nastiest: **the failure is not a crash, it is an ordinary RimWorld colony**,
and the scenario description would still promise the Backrooms.

### Fault-planted four ways

| Fault planted | Caught by |
|---|---|
| a room added to the inside start | *"declares no rooms, doors, buildings or conduits"* |
| map size changed to 50 | *"uses the coordinate map size (60)"* |
| `RR_InsideStarts` as the generator | *"names a map generator the mod ships"* |
| `GenStep_InsideStartt` as the class | *"genstep resolves to a real class"* |

All restored, and the proof holds over **all three** starts.

---

## Receipts

| | |
|---|---|
| Version | 0.12.0-dev |
| Build | 168 C# files, 86 package files, **0 warnings, 0 errors** |
| Starts | **3 of 3** — the chart's full set |
| New defs | 1 `RimroomsStartDef`, 1 `ScenarioDef`, 1 `MapGeneratorDef`, 1 `GenStepDef` |
| New art, audio or texture | **none** |
| Harmony | **none** — `GameInitData.mapGeneratorDef` is a public field Core reads first |
| Checkers | **eight**, all passing |
| Proofs | **seven**, all holding; the starts proof fault-planted four more ways |
| Game launched | **no** |

Exactly one start begins in corporation contact, and it is asserted. The other two earn it, and
until they do there is **no clean-up team and no courier** — which as of 0.11.7 and 0.11.8 is a
real mechanical difference rather than a line in a design document.

Next, in the chart's order: research tiers 3 and 4, then generated requests after the hinge.
