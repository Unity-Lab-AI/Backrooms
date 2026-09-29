# Connected-colony construction supply — real material into a real build site (0.5.3-dev)

**TODO / feature IDs:** master TODO §Native-provider foundation, resume step 4. RR-GATE, RR-SPACE, RR-FAC, RR-COMPAT.

**Baseline:** `13dcc26` (0.5.2-dev, 91 C# files, 76 package files).

**This checkpoint — 0.5.3-dev:** **93 C# source files**, **76 approved package files**, zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `F2A854438700F68E419533028C6E523A0FD8FAFBDB72B936B87F78C0138FF8AE`. Evidence: [`evidence/connected-construction-2026-09-28/`](evidence/connected-construction-2026-09-28/), reference manifests recomputed, no drift.

**No game was launched, no test was run, no RimSort mod list was changed.**

**Owned paths.** New: `ConnectedWork/Adapters/ConnectedConstructionAdapter.cs`, `ConnectedWork/JobDriver_ConnectedConstruction.cs`. Modified: `ConnectedWork/ConnectedWorkAdapter.cs` (registry), `ConnectedWork/WorkGiver_ConnectedWork.cs` (two subclasses), `Defs/JobDefs/RR_ConnectedWorkJobs.xml`, `Defs/WorkGiverDefs/RR_ConnectedWork.xml`, `Languages/English/Keyed/RR_ConnectedWork.xml`.

Shipped alongside the dependency audit and capability-matching resolution in [`DEPENDENCIES_AND_CAPABILITY_MATCHING.md`](DEPENDENCIES_AND_CAPABILITY_MATCHING.md).

---

## What this adds

A structure part-built on one side of a gate and stalled for want of material can be supplied from the other side. A colonist picks up the actual resource stack, carries it through under native mass and stack limits, and deposits it into the build site's own resource container.

This is the third work family and the first whose destination is a native **work object** rather than storage or a bed — so the first real use of the intent's `finalTarget` field for what schema 1 reserved it for. It is also the first family where the destination is known at **planning** time rather than resolved on arrival.

## Nothing about construction is reimplemented

The temptation the pinned review warns about is inflating `pawn.Map.itemAvailability` so native construction believes a remote stack is local. That is not done. What travels is the material.

Everything construction-specific is Core's:

| Concern | Core API used |
|---|---|
| What the site still needs | `IConstructible.ThingCountNeeded(ThingDef)`, `TotalMaterialCost()`, `IsCompleted()` |
| How much more it can take | `IHaulEnroute.SpaceRemainingFor(ThingDef)` |
| Where material physically goes | the frame's own `resourceContainer`, via `Toils_Haul.DepositHauledThingInContainer` |
| Getting there with it | `Toils_Haul.CarryHauledThingToContainer`, `Toils_Goto.MoveOffTargetBlueprint` |
| Blueprint becoming a frame | `Toils_Construct.MakeSolidThingFromBlueprintIfNecessary` |
| Building the thing | unchanged: Core's own local construction work |

`Frame` was confirmed from source to be `Building, IThingHolder, IConstructible, IStorageGroupMember, IStoreSettingsParent, IHaulEnroute, ILoadReferenceable` with a public `resourceContainer`. That is why the container delivery route built in 0.5.1-dev already reaches it, and why the driver's existing rule of *not* exclusively reserving an `IHaulEnroute` destination is exactly right here: a frame coordinates several haulers itself.

## Blueprints were not excluded, and that mattered

The easy scope cut would have been "frames only", on the grounds that a blueprint holds no resources. That would have broken the main case: a blueprint with no local material would never become a frame, so cross-gate supply would only have worked for builds that were already under way.

Core solves it in one public toil. `Toils_Construct.MakeSolidThingFromBlueprintIfNecessary` replaces the blueprint with a frame at the moment of delivery, and Core's own container driver uses it in exactly this position. Including it means a first delivery to an untouched blueprint works, and no scope was cut.

The candidate pass looks at frames before blueprints, because a frame is a build already under way and stalled, which is the situation this family exists for.

## Bounded, in the same shape as every other family

Four connected maps, sixteen build sites per map, twenty-four resource stacks per material — every one a rotating window via `ConnectedWorkScan`, not a prefix, so a long build queue cannot starve its own tail. Direction follows the same cost rule as hauling: collect where the worker already stands before crossing to collect, because one crossing beats two.

The quantity is clamped three ways: what the stack has after leases, what the worker can physically carry, and **what the site still needs**. Carrying eighty steel to a frame that wants twelve would be a real waste of a trip.

## Revalidation at both ends

The site is checked on the **fetch** side too, before the pickup, not only on arrival: a build finished or cancelled while the worker walked to the stack means the trip ends before anyone lifts anything. On arrival the site is rechecked for existence, completion, remaining need of that exact def, forbidden state and reachability.

`RR_ConnectedWork_SiteSatisfied` is a **Completed** outcome rather than a failure. If the site no longer wants the material, the material is physically here in real hands and ordinary hauling will put it away. Nothing is lost and nothing is duplicated.

## Work-giver placement

| Def | `priorityInType` | Neighbours in Core's `Hauling` |
|---|---|---|
| `RR_ConnectedConstructionContinue` | 12 | above `DeliverResourcesToFrames` (10) and `ToBlueprints` (9) |
| `RR_ConnectedConstruction` | 8 | below both |

Finishing a delivery already in hand edges above Core's local delivery; starting one sits below, so material already on this side is always delivered first. Both carry `prioritizeSustains` to match Core's own construction givers. Balance decisions, recorded as such.

## Saved state

**No new key and no schema change.** The family reuses the intent shape: the resource stack is `SourceThing` then `Cargo`, and the build site is `FinalTarget`, set at planning time. A 0.5.2-dev save loads unchanged.

## What this does not do

**Construction *finishing* is not here, and it is not another adapter.** A worker crossing to do build work with nothing carried is a different shape from fetch → carry → deliver: the worker crosses because work exists over there, and Core's own local givers take over on arrival. Without an intent to bound it that shape thrashes — cross, find nothing, cross back.

The design is recorded rather than hand-waved: a saved **deployment intent** naming the destination map and the work type that justified crossing, bounded by the same lease, released when no qualifying work remains there. It is a new intent shape, so building it inside this family would have put it in the wrong place. Tracked with that description in [`../DEFERRED.md`](../DEFERRED.md).

Also not claimed: terrain work, removing blockers, installing minified furniture, and roof work, each of which the pinned review lists as its own case.

## Owner-launched acceptance, deferred

A frame on a site short of steel with steel only at headquarters, and the reverse; an untouched blueprint receiving its first material from across a gate and becoming a frame; a site finished by someone else while the worker is mid-trip, confirming the material is set down rather than lost; a site whose remaining need is smaller than a carried stack; two workers supplying the same site, confirming the enroute accounting is Core's and not duplicated; a site forbidden or outside the worker's observed allowed area on the far side; save and reload at each of the four segments; and a branch with more than four connected maps, confirming the rotating window reaches all of them.
