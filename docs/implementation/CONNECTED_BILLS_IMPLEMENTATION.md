# Ingredients reach a bill through a gate (0.5.7-dev)

**Baseline:** `8e69929` (0.5.6-dev, 100 C# files, 76 package files).

**This checkpoint — 0.5.7-dev:** **101 C# source files**, **76 approved package files** (unchanged — two work giver defs and three keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `7520EB990C16ACB609A25731D844FF989DB186B5DC4CF933BF4AFB2B1EEC43D2`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/bill-ingredients-2026-09-28/`](evidence/bill-ingredients-2026-09-28/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The fifth family, and what it actually adds

A workbench stalled for want of leather on one side can now be supplied from the other. A colonist picks up the real leather, carries it through the gate, and puts it into storage the bill can use.

**What is new here is the trigger, not the destination.** Storage hauling already moves an object when somewhere else is better storage for it — but it has no opinion about what anyone wants to *make*. This family moves an object because a specific bill on a specific bench is short of it. That is the "physical ingredient logistics" half of the contract, and it is the reason the intent had to learn to record an actual `Bill`.

No bill is ever started from here, and nothing about crafting is reimplemented. The ingredients land in storage and Core's own `WorkGiver_DoBill` on that map finds them, allocates them with its own `TryFindBestBillIngredients`, and runs the recipe.

## The search radius is what makes this more than hauling

Core's ingredient validator, read from `WorkGiver_DoBill.TryFindBestIngredientsHelper`, rejects anything further from the bench than the bill allows:

```
(t.Position - billGiver.Position).LengthHorizontalSquared < radiusSq
```

measured against `bill.ingredientSearchRadius`, from the **giver's `Position`** — not its interaction cell. So the delivery cell is chosen inside that radius, measured from exactly the same place, and the adapter never exceeds the bill's own radius even where its own scan cap is wider.

`ingredientSearchRadius` defaults to `999f`, so for a default bill almost any storage on that map works — which is why a cap of our own (24 cells of radius) exists: without it a single planning pass would sweep a whole map of cells. But for a bill the player has deliberately kept tight, the ingredient has to land *near the bench*, and that case is precisely where ordinary hauling would never have helped.

## The `UnfinishedThing` trap, avoided on purpose

This was the flagged danger at handoff, and Core confirms it twice over:

- `WorkGiver_DoBill.ClosestUnfinishedThingForBill` validates `((UnfinishedThing)t).Creator == pawn`.
- `Bill_ProductionWithUft` additionally binds `BoundUft` to a `BoundWorker`, and only that worker resumes it.

So a half-made thing belongs to one colonist and **no other pawn may ever finish it**. A cross-gate worker that picked one up would be carrying something nobody on either map is allowed to complete.

This family therefore does not touch unfinished things at all. It delivers material and stops. That is not a limitation worked around — it is the correct behaviour, and the reason it is written down here is so a later session does not "improve" the family by adding UFT hauling.

## Bill types supplied, and the ones deliberately not

Only `Bill_Production` and its subclasses. Skipped, each with a reason rather than silently:

| Type | Why not |
|---|---|
| `Bill_Medical` | A surgery needs the patient present. That belongs to the tending family, which still needs its own source review per native route. |
| `Bill_Autonomous` / `Bill_Mech` | State machines with their own gathering phases (`FormingState`, a waste producer, a gestating mech). Supplying one correctly means understanding its phase, which has not been reviewed. |

## `ShouldDoNow()` is safe to ask about a remote bill — verified, not assumed

This is load-bearing, because the whole candidate half depends on it. `Bill_Production.ShouldDoNow()` reads `suspended`, `repeatMode`, `repeatCount`, and for a target-count bill calls `recipe.WorkerCounter.CountProducts(this)` — which counts through `Bill.Map`, and `Bill.Map` resolves to **`billStack.billGiver`'s own map**, falling back to that thing's `MapHeld`. It consults no pawn and never touches the worker's map.

So it is a fair question about a bill on a map nobody is standing on, and it is asked directly rather than reimplemented.

Likewise `BillStack.AnyShouldDoNow` is Core's own first question about a bill giver and is a fact about the giver and its own map.

## Shortage, and the mistake it avoids

Presence is counted across **every** def the ingredient allows, not just the one being considered for carrying.

A recipe that accepts steel *or* plasteel, with plenty of steel by the bench, is not short of anything. Counting only plasteel would have reported a shortage and sent somebody across a gate for nothing — repeatedly, because the situation is stable. Getting this backwards would have produced exactly the kind of quiet, permanent busywork that is hard to notice and hard to attribute.

The required count comes from `IngredientCount.CountRequiredOfFor(def, recipe, bill)`, so a small-volume ingredient and a bill-specific count are both Core's numbers, never ours.

## Saving the bill by reference

The intent gained a `Bill` field, saved with `Scribe_References.Look`.

This is a supported pattern rather than an invention: **Core's own `UnfinishedThing` does exactly this** — `Scribe_References.Look(ref boundBillInt, "bill")` — because `Bill` implements `ILoadReferenceable` with `GetUniqueLoadID() => "Bill_" + recipe.defName + "_" + loadID`.

The alternative considered and rejected was a recipe def plus a stack index. That would silently retarget onto whatever bill occupied that slot after the player reordered the stack, and the worker would deliver leather to a bill that never asked for it.

## Two resolve methods, and why

`RecordResolvedStoreCell` clears `finalTarget`, because plain hauling has no final target and leaving a stale one would make the readout describe a trip to an object that is not involved. But a bill delivery **does** have a final target — the bench — while still delivering to a cell.

So a second method exists, `RecordResolvedCellForTarget`, which sets only the cell. Calling the hauling one here would have erased the bench and left the Operations pane describing a trip to nowhere. Both are documented at the call site so the distinction is not re-discovered by accident.

## Reuse rather than new code

- **No new `JobDef`.** Fetch reuses `RR_ConnectedFetch`; delivery reuses `RR_ConnectedDeliver`.
- The two shared storage-delivery drivers were **generalised, not copied**. `ConnectedWorkJobs.LiveHaulingIntent` was locked to the storage-hauling family; it now accepts any family in a small declared list of families that genuinely finish by placing cargo into storage the destination map's own settings accept. Bills qualify, because that is exactly what a bill delivery does.
- **Cells only**, deliberately. A stockpile and a shelf are both delivered to by cell, and they are where ingredients live. A container such as a grave is not ingredient storage, and routing to one would also collide with the final-target field that here holds the bench.

## Priorities

Both in `Hauling`, alongside the construction supply pair:

| Giver | Priority | Why |
|---|---|---|
| `RR_ConnectedBillContinue` | **11** | Cargo in real hands must not be abandoned, so finishing edges above the starting givers. Sits just under construction's continue (12). |
| `RR_ConnectedBill` | **7** | Just below construction supply's start (8): a stalled build is more urgent than a stalled bill. Both stay well under Core's `HaulGeneral` (15), so ordinary local hauling always wins. |

All ten cross-gate numbers are **player settings** as of 0.5.6-dev, tunable live, so these are starting positions rather than verdicts. The bill family was added to the settings screen in the same change.

## Saved state

| Owner | Key | Rule |
|---|---|---|
| `ConnectedWorkIntent` | `bill` (reference, inside `rr_connectedWorkIntents`) | Additive within the existing deep-saved intent list; no schema bump. Absent from every earlier save, loading as null, which every other family already expects since only this one sets it. A 0.5.6-dev save loads unchanged. |

## A defect in the evidence ritual, found and fixed here

While confirming this checkpoint's hash, the rebuild produced a **different** assembly from the one just recorded, with no source change. That is worth writing down properly, because the cause invalidated a claim this project has been making since 0.4.x.

The .NET SDK appends the git commit to `AssemblyInformationalVersion` by default. The assembly literally contained:

```
0.5.7-dev+74ce5a5594a4e17e67844a450b31f8a853e52341
```

So the assembly hash was a function of the source **and the commit**. Every evidence hash recorded before this checkpoint became unreproducible the instant its own commit was created — creating the commit changed what a rebuild produces. Those hashes were honest measurements and the clean-rebuild comparisons behind them were real, but **they could never be re-verified afterwards**, which is most of the reason to record a hash at all. There is even a tell in the existing source: `RimroomsMod.ResolveModVersion` already strips everything after a `+`, which only matters if the commit is in there.

Fixed by setting `IncludeSourceRevisionInInformationalVersion` to `false`. The informational version is now exactly `0.5.7-dev`, and the hash is a pure function of the source.

Verified two ways rather than asserted:

- `obj/` and `bin/` deleted and the project fully recompiled — same hash;
- **the same source rebuilt at two different HEAD commits** (`74ce5a5` and `efa5060`) — same hash both times. That is the property the ritual actually depends on, and it was the one previously absent.

Earlier evidence folders are left as they are. Their hashes are truthful records of what was built at that commit; they are simply not reproducible now, and this is the note that explains why rather than leaving a future session to conclude the build is broken.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; 537 `RR_` keys referenced from source resolve with 0 missing; every `giverClass` resolves to a real class.
- Compliance checks pass: zero destructive patch operations, no `texPath` outside `RR_`, no ungated DLC id, no `modDependencies`, no non-original package asset.
- 76 approved package files, 0 missing. Reference assemblies recomputed, no drift. No attribution strings.

## Not done, and named

- **Unfinished things are out of scope by design**, per the Core evidence above. Not a gap to close.
- **`Bill_Medical`, `Bill_Autonomous` and `Bill_Mech`** each need their own source review before being supplied.
- **A deep-storage container inside the radius is not used** as a landing place; cells only. A container route would need the final-target field freed up, or a second field.
- **Research** is next, and should reuse the travel-to-work *deployment* shape rather than this one: it is stationary work at a real bench with nothing carried.
- Then tending across a gate (medicine-as-cargo), food, rest, and the remaining families.

## For the post-completion test phase

Opening a gate with a bench on the far side whose bill is short of an ingredient that only exists on this side, and confirming a colonist carries it across and the bill then runs; confirming nothing crosses when the ingredient is already within the bill's radius; confirming a bill whose recipe accepts two materials does **not** trigger a trip when one of them is plentiful by the bench; setting a bill's ingredient radius small and confirming the delivery lands inside it; suspending or deleting the bill mid-carry and confirming the goods are simply set down rather than lost; confirming a half-made unfinished thing is never picked up or carried; saving and reloading mid-carry and confirming the bill reference survives; and reordering the bill stack mid-carry and confirming the delivery still targets the original bill.
