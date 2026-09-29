# Continuous portal topology: what already worked, and the first real gap closed (0.6.3-dev)

**Baseline:** `d50b90c` (0.6.2-dev, 110 C# files, 76 package files).

**This checkpoint — 0.6.3-dev:** **110 C# source files** (no new file), **76 approved package files** (unchanged — two keyed strings added), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `F7ADAE761CE5AF98925DBA0EEA5A5ED5C0CC8BAB14B0163D1CD8236FEE90C89C`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/world-frontiers-2026-09-29/`](evidence/world-frontiers-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The owner's direction, and what was actually missing

> so that any one backrooms portal corroridanet weither from a lab portal or a natural portal can lead to other places and other backroom instance seeds, and or pop out any where in the game world on a tile map

> there can be portals with in portals and portals found on world maps

Before writing anything, the existing portal layer was read to establish what already satisfied this. **Two of the four requirements already worked**, and saying so is more useful than quietly rebuilding them.

| Requirement | State before this checkpoint |
|---|---|
| Portals within portals, unbounded nesting | **Already worked.** `RimroomsPortalNetwork` stores a graph and `PortalRouteSearch` is multi-hop, so coordinate A's frontier reaching B, whose frontier reaches C, is just another edge. Depth is unbounded; breadth is capped at two frontiers per coordinate and by the campaign's own coordinate cap. |
| A portal to another Backrooms instance seed / a deeper level | **Already worked.** `NaturalFrontierService.Discover` calls `campaign.CreateDiscoveredCoordinate`, which mints a **new coordinate with its own derived seed**. A frontier has always led to a genuinely new space, not a link between known ones. |
| The link kind never restricts where you can go next | **Already true.** Routing does not discriminate by `PortalConnectionKind`, and `Availability` consults the gate window only for `Laboratory` edges, so a natural edge is always open regardless of how you arrived. |
| **Portals found on world maps** | **Gap.** `Evaluate` refused any door outside a `RimroomsDestinationMapParent`, with the stated reason "Only deeper in." That was a design assumption the owner has now overridden. **Closed here.** |
| **A portal that emerges out in the world** | **Gap.** Still open — see below. |

## The gap closed: a way onward can be found on an ordinary map

`NaturalFrontierService.Evaluate` now has two origin branches instead of one refusal.

| | Inside the Backrooms | On an ordinary map |
|---|---|---|
| Seed for the draw | that coordinate's own `Seed` | the branch seed, newly exposed as `BranchSeed` |
| Origin id | the coordinate id | `"map:" + map.uniqueID` |
| Seed key prefix | `frontier:` | `worldfrontier:` |
| Rarity | 1 in 12 doorways | 1 in 40 |
| Cap per map | 2 | **1** |
| Player-built doors | n/a | **never eligible** |

### The player-built rule is the important one

**A door the player built is never a frontier.** Turning somebody's own wall door into a permanent way into the Backrooms would change an existing colony just by installing this mod — which `CONTENT_REUSE_POLICY.md` forbids outright — and it would be exactly the kind of surprise nobody asked for.

So a way onward is found in **something that was already standing there**: `door.Faction != Faction.OfPlayer`. That single check is what makes the feature safe to ship, and it is also the better fiction. A designated laboratory gate is excluded too, because it already has a machine on it.

The cap of one and the 1-in-40 rarity carry the same intent: in the Backrooms a doorway leading elsewhere is ordinary, and out in the world it should be a rare and notable event.

### Save compatibility is exact, deliberately

A Backrooms origin still produces **byte-for-byte the same discovered-coordinate id and the same seed key** it produced before ordinary maps were allowed — `record.Id + ":frontier:" + x + "," + z`. So every coordinate already discovered in an existing save resolves to exactly the same space with exactly the same seed. The ordinary-map case uses the distinct `worldfrontier:` key so the two can never collide even if a seed and a position coincided.

That was a constraint on the refactor, not an accident: restructuring the id would have silently relocated every space a player had already found.

## Two defects caught before the build

**A null dereference in the case the change exists to support.** `Discover` recorded its event with `source.Id` — the `CoordinateRecord`. An ordinary map has no `CoordinateRecord` at all, so the first successful world-map discovery would have thrown. Now it records `origin.OriginId`.

**A shadowed type.** Exposing the branch seed as `CampaignSeed` collided with the static `CampaignSeed` derivation helper in the same namespace, so four existing call sites in `CampaignServices` and `FailedSiteRecovery` silently resolved `CampaignSeed.Derive(...)` against an `int` property and failed to compile. Renamed to `BranchSeed`, which is clearer regardless. Worth recording because a property that shadows a type is a failure mode that produces baffling errors far from its cause.

## Still open: emerging out in the world

The remaining requirement — *"pop out any where in the game world on a tile map"* — is genuinely unbuilt, and it is the larger half.

Everything today assumes the far side of a natural edge is a **branch-owned coordinate**: `RegisterNaturalAddress` takes a `CoordinateRecord`, and `DestinationService.EnsureSite` produces a generated Backrooms map for it. To emerge in the ordinary world the far endpoint has to be something else:

- **The cheap version, and genuinely useful:** the far side is an **already-owned ordinary map** — the colony, or a world site the branch holds. A Backrooms door that opens onto your own base is a real shortcut and a real "portal to another normal world's map". It needs a far-side threshold chosen on that map, which is the same kind of work `RegisterLaboratoryAddress` already does for a site.
- **The full version:** the far side is a **world tile the branch does not yet hold**, which means a new world object and a generated map. That touches world generation and map lifecycle, so it wants its own checkpoint and its own review — not the tail end of a long session.

Both are recorded in `DEFERRED.md` with this note. The order is the cheap version first, because it is bounded and it exercises the endpoint plumbing that the full version then reuses.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; every `RR_` key referenced from source resolves with 0 missing, including the two added here; every `giverClass` resolves.
- Compliance checks pass: zero destructive patch operations, no `texPath` outside `RR_`, no ungated DLC id, no `modDependencies`, no non-original package asset.
- 76 approved package files, 0 missing. Reference assemblies recomputed, no drift. No attribution strings.

## Saved state

**None added.** `BranchSeed` exposes an existing saved field read-only. Discovered coordinates continue to use the existing derived-id path, so a 0.6.2-dev save loads unchanged and every already-discovered space resolves identically.

## For the post-completion test phase

Surveying a doorway in the Backrooms and confirming it still records a new coordinate with a stable seed across save and reload; confirming the *same* doorway always gives the same answer and a revisit never rerolls it; confirming a coordinate gives up at most two ways onward and an ordinary map at most one; confirming a door the player built is **never** offered as a survey target on any map; confirming a designated laboratory gate is never offered either; confirming an already-discovered coordinate in a pre-0.6.3 save still resolves to the same space; and confirming a chain of three or more spaces routes end to end.
