# Somebody finally runs the bill on the far side (0.6.5-dev)

**Baseline:** `4af9086` (0.6.4-dev plus the register checkpoint, 112 C# files, 76 package files).

**This checkpoint — 0.6.5-dev:** **114 C# source files** (two new), **76 approved package files** (unchanged — ten work giver defs and ten keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `51D2DB71724A7559FCE6092406040C6660EDCF15817732511D74C3A018D7E8EC`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/bill-work-2026-09-29/`](evidence/bill-work-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The gap, stated plainly

The carry family has delivered ingredients to a remote bill since 0.5.7-dev. **Nobody was ever sent to work the bench.** A coordinate holding a stove, a live bill and a pile of delivered ingredients produced nothing at all unless a colonist happened to be standing there for some other reason. The material arrived and sat.

`CONNECTED_BILLS_IMPLEMENTATION.md` settled the supply half completely and never decided the other half. This is that decision.

## Why a deployment is the *correct* shape here, not a workaround

The carry family's record pinned the rule that makes this work, and it reads at first like an obstacle:

- `WorkGiver_DoBill.ClosestUnfinishedThingForBill` validates `((UnfinishedThing)t).Creator == pawn`.
- `Bill_ProductionWithUft` binds `BoundUft` to a `BoundWorker`, and only that worker resumes it.

A half-made thing belongs to exactly one colonist. That is precisely why the **carry** family must never touch one — it would be hauling something nobody on either map is allowed to finish.

But a **deployed** worker stands on the bill's own map and runs Core's own `WorkGiver_DoBill` locally, creating and finishing its *own* unfinished thing, on one map, exactly as Core intends. The deployment shape sidesteps the trap **by construction** rather than working around it. The same fact that forbids one family enables the other.

## One family per work type, because Core draws that line itself

This is not five copies of one idea. `WorkGiver_DoBill.StartOrResumeBillJob` contains:

```csharp
if (bill.recipe.requiredGiverWorkType != null &&
    bill.recipe.requiredGiverWorkType != def.workType) { continue; }
```

and a bench belongs to a work type **only** through its `WorkGiverDef.fixedBillGiverDefs`. A single "bill work" provider would have to declare one `WorkType`, and a pawn with cooking enabled but smithing disabled would then be pulled across a gate for smithing it cannot do.

So there are five providers — Cooking, Crafting, Smithing, Tailoring, Art — each with its own priority pair and its own row in the player's work settings, which is also where a player already expects to control this.

| Work type | Core's highest giver | Continue | Plan |
|---|---|---|---|
| Cooking | `DoBillsCook` 100 | **102** | 2 |
| Crafting | `DoBillsUseCraftingSpot` 100 | **102** | 2 |
| Smithing | `DoBillsSubcoreEncoder` 220 | **222** | 2 |
| Tailoring | `DoBillsMakeApparel` 110 | **112** | 2 |
| Art | `RemovePaintFloor` 202 | **204** | 2 |

Fifty-four cross-gate numbers now, all player settings, all tunable live.

**One interaction recorded rather than papered over:** Rimrooms' own `RR_DoGateAssembly` sits at 100 in Crafting, so the Crafting continue giver at 102 outranks it. That follows the rule every other family follows — a committed traveller is never turned around — and a player who disagrees can lower it without a restart. Naming it here because it is the one place a new number landed above existing Rimrooms work rather than only above Core's.

## The bench set is read from the defs, never from a list of names

`BenchDefs()` unions the `fixedBillGiverDefs` of **every** loaded `WorkGiverDef` whose `workType` matches and whose `giverClass` is `WorkGiver_DoBill` or a subclass.

That is a capability match against live data, so **a mod that adds a bench to an existing work type is covered with no code here and no mention of its name.** It is the project's standing match-by-capability rule applied one level deeper than usual: not "which things are benches" but "which things does the game itself consider bill work of this type".

Only `fixedBillGiverDefs` is read. The `billGiversAll*` flags exist for pawn and corpse bill givers — surgery — which is Doctor work and belongs to the tending family. `UsableGiver` refuses a pawn or corpse giver outright for the same reason.

## Which Core rules are asked from where

The two-halves split, with what each rule actually reads:

| Rule | Where | Why |
|---|---|---|
| `requiredGiverWorkType` | candidate | a fact about the recipe |
| `nextTickToSearchForIngredients` | candidate, **read only** | Core's own throttle. Writing Core's scan state from a remote probe is forbidden; reading it means a bill that just failed for somebody does not immediately pull somebody else across |
| `PawnAllowedToStartAnew` | candidate | reads the bill's pawn restriction, slaves-only / mechs-only flags, and the pawn's skill against `allowedSkillRange`. **None reads the pawn's map.** Verified in source |
| `FirstSkillRequirementPawnDoesntSatisfy` | candidate | the recipe's skill minimum against the pawn's skills; map-independent |
| `ShouldDoNow()` | candidate | counts products through `Bill.Map`, which resolves to the **giver's** map |
| `UsableForBillsAfterFueling()` | candidate | a fact about the giver's own fuel comp |
| `IsForbidden(Faction)` | candidate | the faction overload; the pawn overload consults the pawn's allowed area in its *current* map |
| `TryFindBestBillIngredients` | **arrival only** | allocates across substitutable defs using the pawn's own reachability |
| `CanReserve`, `CanReserveSittableOrSpot` | **arrival only** | pawn-and-map specific |
| `IsForbidden(Pawn)` | **arrival only** | consults the pawn's allowed area |
| the whole unfinished-thing resolution | **arrival only** | Core's, and correct only on one map |

`PawnAllowedToStartAnew` being safe to ask remotely is the useful find. It is what stops a bill restricted to one named colonist, or to a skill band, or to slaves, from dragging the wrong worker through a gate — and asking it at planning time costs nothing.

## The one approximate test, and why it has to exist

`EveryIngredientPresent` asks whether each ingredient the recipe needs has *something* acceptable standing within the bill's search radius on the giver's own map. It is a **necessary condition, not a sufficient one**, deliberately.

Deciding for certain means running `TryFindBestBillIngredients`, which is exactly the expensive pawn-and-map specific question the candidate half may never ask about a remote map.

What it exists to prevent is a permanent futility. A coordinate holding a bench, a live bill and **no materials at all** would otherwise look like work forever — and Core's own throttle cannot save us, because `nextTickToSearchForIngredients` is only pushed forward when a pawn actually tries and fails, and **on a map with nobody standing on it nobody ever tries.** Without this test the family would walk a cook across a gate, find nothing, release the deployment, and plan the identical trip again, indefinitely.

A false positive costs one wasted walk. A false negative costs one planning delay. That asymmetry is why the test is cheap and approximate rather than exact, and it is written down so a later session does not "improve" it into an exact reimplementation of Core's allocator.

Presence is counted across **every** def the ingredient allows, not just one — a recipe accepting steel *or* plasteel with plenty of steel by the bench is not short of anything — and the required count comes from `IngredientCount.CountRequiredOfFor`, so no quantity is ours.

## A defect in the carry family, found by checking the hierarchy

`ConnectedBillAdapter` has said since 0.5.7-dev that autonomous and mech bills are deliberately out of scope. Its filter was:

```csharp
if (!(bill is Bill_Production)) { return false; }
```

The hierarchy, read in source rather than assumed from the names:

```csharp
public class Bill_Autonomous : Bill_Production
public abstract class Bill_Mech : Bill_Autonomous
```

**Autonomous and mech bills *are* `Bill_Production`**, so that test admitted exactly what it was written to exclude. The carry family has been supplying ingredients to mech gestator and other autonomous bills without review, contrary to its own record, for five checkpoints.

Both families now share one type test in `ConnectedBillScan.OrdinaryProductionBill`, which excludes `Bill_Autonomous` explicitly. `Bill_Medical` is excluded by the same test since it derives from `Bill` directly; `Bill_ProductionWithUft` **is** included, because it is an ordinary production bill whose unfinished thing Core handles on arrival.

## Shared, not duplicated

Both bill families ask about the same bills from opposite directions — *is this bill short of something I could bring it* versus *does this bill have what it needs already*. Those are the same primitives read in opposite senses, so `ConnectedBillScan` now owns them and `ConnectedBillAdapter` delegates. A second copy of the ingredient-counting rule would have been a second place for it to be subtly wrong, and the hierarchy defect above is what that looks like in practice.

## Profile rows read before writing this

Per the standing rule that the prep work is where mod facts live. Each answered a real question, and each answer is recorded back in the register's `CompatibilityWatch` rather than only here.

| Row | What it changed here |
|---|---|
| **260 While You Are Nearby** | Reorders which target a *scanning* giver picks by distance. These are `NonScanJob` givers with a single candidate, so there is nothing to reorder. Its stated effect — prefer near over distant — already matches this family's own rule. |
| **67 Compact Work Tab** | Ten more giver defs, fifty-seven total. Its page states added work *types* work; these are added givers inside existing types, a weaker change. Readability is a runtime check. |
| **53 Big Little Mod Patch** | Links furniture and workbenches across mods. Because the bench set is computed from defs, anything it links is covered with nothing named and nothing patched. |
| **246 Vanilla Furniture Expanded - Factory** | Bill-driven benches, covered automatically **if** their work type is one of the five. A bench under a wholly new modded work type is **not** covered — a named limit, not a claim. |
| **96 Fueled Crematoriums** | Core hands out a *refuel* job instead of the bill when `CompRefuelable.HasFuel` is false, so this family requires `UsableForBillsAfterFueling()` and nobody crosses for a bench that only needs fuel. The fuel carry family owns that route. |

Nothing of any of theirs is copied, patched, replaced or bundled. These are our notes about our own behaviour alongside theirs.

## Saved state

**None added.** The deployment record already carries a provider id, and the five new ids are new values in an existing field. A 0.6.4-dev save loads unchanged.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; every `RR_` label and settings key referenced from source resolves with **0 missing**; every one of the 57 Rimrooms `giverClass` references resolves to a declared class; all 27 priority pairs name real `WorkGiverDef`s with keyed labels.
- Register rebuilt and verified after the five row updates; `audit-gate0.py` `"result": "PASS"`, zero errors.
- Compliance checks pass: zero destructive patch operations, no `texPath` outside `RR_`, no ungated DLC id, no `modDependencies`, no non-original package asset. 76 approved package files, 0 missing. No attribution strings.

## Not done, and named

- **A modded work type with its own bill givers** gets no provider, because the five are fixed and the giver defs are shipped XML. Recorded as a limit rather than a silent gap.
- **`Bill_Autonomous` and `Bill_Mech` remain out of scope for both families** — now actually, rather than only on paper. Each needs its own source review of its gathering phase first.
- **Nothing walks the worker home.** That is the standing rule for all twenty deployments; Core's own think tree brings them back.

## For the post-completion test phase

A coordinate with a stove, a live cooking bill and delivered ingredients attracting a cook who then actually cooks; the same coordinate with **no** ingredients attracting nobody, repeatedly, rather than cycling a worker across the gate; a bill restricted to one named colonist pulling only that colonist; a bill with a skill minimum pulling only a worker who meets it; a fuelled bench that is out of fuel pulling *fuel* rather than a worker, and pulling a worker once refuelled; a smithing bill not pulling a pawn who has smithing disabled; a mech gestator bill pulling neither a worker nor ingredients; and — with the profile loaded — the work tab staying readable with all fifty-seven givers present.
