# The Backrooms has no outside, and the last three work families (0.6.4-dev)

**Baseline:** `562fc01` (0.6.3-dev, 110 C# files, 76 package files).

**This checkpoint — 0.6.4-dev:** **112 C# source files**, **76 approved package files** (unchanged — six work giver defs and six keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `4057EFD15AAB4B1C609732AB18A02F025C9A98A8D951374CE7333A80C9780728`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/containment-and-care-2026-09-29/`](evidence/containment-and-care-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## Part one: the Backrooms has no outside

Three owner directions arrived in sequence and together they define the strongest world rule in the project. Verbatim text is in `TODO.md`; the rule is:

1. A Backrooms environment can **never have an outside**. The whole seed map is inside mountain roof, and **no roof in it may ever be removed**. The only way out into a world map area is a portal found inside the Backrooms.
2. But **everything inside is fully strippable** — walls and doors deconstructable, areas mineable in a variety of materials, carpet and tile liftable.
3. And **ordinary world maps keep every vanilla tool**: build roof, remove mountain roof, build mountain wall.

### Two direct violations in the existing generator

`GenStep_BackroomsDestination` did two things that broke rule 1 outright:

- the base pass set **`SetRoof(cell, null)` on every cell**, so every cell outside a room or corridor was *unroofed* — open sky, an outside, across most of the map;
- rooms and corridors were roofed with **`RoofConstructed`**, which is removable.

### The Core fact that makes rules 1 and 2 compatible

Read in source rather than assumed:

```csharp
public bool VanishOnCollapse => !isThickRoof;
```

**Thick rock roof never vanishes when it collapses.** Mining out the rock that supports it produces rubble and a collapse exactly as under any mountain, and the cell stays roofed afterwards.

That is the whole reconciliation. My first instinct had been that mining inside a coordinate would have to be *refused* to protect the ceiling, and I wrote that into the register as a conflict — **the owner's refinement corrected it and the Core fact proves the refinement right.** A player may mine a coordinate to nothing and still never open a hole in the world, so containment needs **no restriction on the player at all**. That is a much better answer than forbidding the pickaxe, and the wrong guess is marked superseded in `TODO.md` rather than quietly deleted.

### What generation does now

- **Every cell gets `RoofRockThick`.** Not `RoofConstructed` anywhere, including rooms and corridors, because constructed roof is removable and no roof here ever may be.
- **The space between rooms is filled with solid natural rock**, drawn from the map tile's own rock types via `Find.World.NaturalRockTypesIn`, varied per cell by a draw from the **coordinate's own saved seed**. So a coordinate is always made of the same stone in the same places, and revisiting never reshuffles it — the same determinism rule every other generated property follows. The rock does two jobs at once: it supports the thick ceiling so Core's collapse check never sees a vast unsupported span, and it is material the player can mine, which rule 2 explicitly asks for.
- **Rooms and corridors are carved back out** of that fill.

### Two breakages the rock fill caused, caught before publishing

Filling every cell with rock interacted badly with code that predated it, and both would have been serious:

- **Corridors would have been impassable.** `SetWalkableRoofedCell` set terrain and roof but never removed an edifice, so every corridor would have stayed solid rock and each coordinate would have been cut into disconnected rooms. Now it carves.
- **Generation would have failed outright.** `PlaceWall` **throws** `RR_Generation_WallOverlap` on any existing edifice, and after the fill every wall cell had rock in it. Now it clears natural rock first and still throws for anything else — because a non-rock overlap means two generated structures collided, which is a real generator fault that must not be silently tolerated.

### The roof guard, and why a guard was needed at all

Vanilla alone can strip the ceiling. `WorkGiver_RemoveRoof` is driven by `map.areaManager.NoRoof` and contains **no** check for natural or thick roof — it asks only whether the cell is in the area and is roofed. A player could paint a no-roof area across a coordinate and colonists would obediently remove a mountain ceiling. That is precisely the hole the owner named when they said mods that remove roof or mountain "need something in our mod".

`BackroomsContainmentMapComponent` closes it two ways, with public API only and no Harmony:

1. **The no-roof area is kept empty** on a Backrooms map. With no active cells, `WorkGiver_RemoveRoof.ShouldSkip` returns true and the job is never offered — and any mod driving removal through the same area is neutralised by the same stroke, because the area is the shared mechanism rather than a vanilla detail.
2. **Any cell that somehow loses its roof is re-roofed** with thick rock. This is the belt to that brace, and it does not care *how* the roof went — so a mod removing roof by a route nobody has seen is still corrected. It is a repair rather than a prohibition, which is why it can be honest about mods it has never been tested against.

Both passes are bounded: the re-roof sweep walks a **rotating window** of 400 cells per interval, so cost is fixed regardless of map size and no region can be starved — the same rotating-window rule the work layer uses. A full pass runs once on load, where a partial sweep would leave a visible hole until the rotation came round.

### Rule 3 is satisfied by construction, not by a special case

The component tests one thing before doing anything: whether the map is a `RimroomsDestinationMapParent` with a ready layout. On a colony map, a quest site or any other ordinary world map that test fails and it **returns immediately** — it never clears a no-roof area and never re-roofs a cell there. So build roof, remove mountain roof and build mountain wall all behave exactly as they always did outside the Backrooms, and the guard cannot regress an existing colony.

## Part two: the last three work families

Wardening, childcare and animal handling, all deployments. Twenty-two families now, fourteen of them travel-to-work deployments.

All three lean on the rule that **a provider answers one question, not one Core work giver**. Core has fourteen warden givers, six childcare givers and eight handling givers; asking once whether that kind of work exists over there, and letting Core pick which giver applies on arrival, is both correct and the only sane amount of code.

| Family | The one question | Notes |
|---|---|---|
| **Warden** | Does that map hold a prisoner or slave of ours? | Every warden giver is driven by the interaction mode **the player set** on that prisoner, so the deployment justifies the crossing and Core decides what happens. |
| **Childcare** | Is there a baby of ours on that map? | Biotech content: `GetNamedSilentFail("Childcare")` returns null without the expansion, so the provider is simply unavailable — never an exception, never a claim the install cannot honour. |
| **Animal handling** | Has the player designated slaughter, taming or release to the wild there? | **Designation-driven only**, deliberately. |

### Prisoner food already reaches them, and nothing had to be added

The food carry family excluded prisoners from *feeding*, because `WardenFeedUtility` owns that route. But its eater test accepts any pawn whose `HostFaction` is the player — which is exactly what a prisoner is. So food is already carried to a map holding prisoners, and this provider sends the warden who hands it over. **The two halves already fit without either knowing about the other**, which is what the shapes were for.

### Animal handling is narrowed on purpose

Core's `Handling` type has eight givers, but penning, milking, shearing, training and feeding patient animals describe *continuous states* rather than something the player asked for. A handler crossing a gate because a far-side alpaca could theoretically be sheared would be constant, pointless traffic. So this family fires only on an explicit mark — slaughter, tame, release — which puts it with the fieldwork families where nothing is inferred. Once a handler is there, Core's own givers do whatever else that map needs, including the continuous work the provider would not have crossed for.

### Priorities

Each continue giver sits just above the highest Core giver in its own work type so a traveller is not turned around: Warden **112** above `ExecuteSlave` (110), Childcare **202** above `BringBabyToSafety` (200), Handling **152** above `HandlingFeedPatientAnimals` (150). Each plan giver sits at **2**, below everything local in that type. Forty-four cross-gate numbers now, all player settings, tunable live.

## Saved state

One transient scan cursor, `rr_containmentCursor`, on the new map component. Nothing else. A 0.6.3-dev save loads unchanged — and on load the containment component immediately roofs any cell an older save left open, so an existing coordinate is brought up to the rule rather than left broken.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; every `RR_` key resolves with 0 missing; every new `giverClass` resolves.
- Compliance checks pass: zero destructive patch operations, no `texPath` outside `RR_`, no ungated DLC id, no `modDependencies`, no non-original package asset.
- 76 approved package files, 0 missing. Reference assemblies recomputed, no drift. No attribution strings.

## Not done, and named

- **Floors being recovered.** Vanilla returns no materials when a floor is removed, so *"uninstalled, moved, resued, sold"* for carpet and tile is a content feature rather than a setting. It needs its own decision under `CONTENT_REUSE_POLICY.md` and is recorded in `TODO.md` rather than assumed.
- **Joy and rituals** remain, and the needs-are-not-work answer is expected to apply to joy. Decide both explicitly rather than leaving rows open.
- **The three hauling providers** — Pick Up And Haul (164), Haul To Stack (107), Prison Labor (288) — are mod-review rows rather than families.
- **A portal whose far side is an ordinary map or a world tile**, which is the remaining half of the topology direction and needs a player designation flow.
- **The three starting sites**, including the two starts that begin with a way out of the Backrooms.

## For the post-completion test phase

Generating a fresh coordinate and confirming **no cell anywhere on it is unroofed**, that every roof is thick rock, and that the space between rooms is solid mineable rock in more than one material; confirming rooms and corridors are all connected and walkable; mining out a large area and confirming the roof collapses to rubble but **never leaves an open cell**; painting a no-roof area across a coordinate and confirming no colonist ever removes roof; loading a pre-0.6.4 save of an existing coordinate and confirming its open cells are roofed on load; and — on an ordinary colony map — confirming build roof, remove mountain roof and build mountain wall all still work exactly as they do without this mod. Then the three care families: a prisoner held on a far map attracting a warden and receiving carried food, a baby attracting a carer only with Biotech present, and a designated slaughter, tame or release pulling a handler while an undesignated animal pulls nobody.
