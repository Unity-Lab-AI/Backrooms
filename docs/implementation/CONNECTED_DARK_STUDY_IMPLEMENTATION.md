# Studying a contained entity through a gate, and a DLC gate that was never there (0.6.6-dev)

**Baseline:** `6a29238` (0.6.5-dev, 114 C# files, 76 package files).

**This checkpoint — 0.6.6-dev:** **115 C# source files** (one new), **76 approved package files** (unchanged — two work giver defs and two keyed strings added to files that already existed), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `238DA7119BECD99E080312C23FAC129E6996C805AD2A48A1E2405656CF86DEA0`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence: [`evidence/dark-study-2026-09-29/`](evidence/dark-study-2026-09-29/).

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The family

A researcher crosses a gate to study a contained entity on the other side. Thematically it is the most apt thing in the whole work layer: a company that reaches unstable spaces through a machine gate, holds what it finds, and learns from it. A containment facility behind a portal is the premise of the mod, and until now nobody would walk to one.

Twenty-eight families, twenty of them travel-to-work deployments.

## Core hands the candidate half over directly

This is the cleanest split so far, because Core's own scanner already takes an explicit map:

```csharp
public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
    => Find.StudyManager.GetStudiableThingsAndPlatforms(pawn.Map);
```

and `GetStudiableThingsAndPlatforms` is a **pure read of a per-map cache** that returns an empty set for a map it does not know and mutates nothing:

```csharp
public HashSet<Thing> GetStudiableThingsAndPlatforms(Map map)
{
    if (!studiableThingsCache.ContainsKey(map)) { return new HashSet<Thing>(); }
    return studiableThingsCache[map];
}
```

So asking it about a map nobody is standing on is fair, cheap and **exact** — no reimplementation of the search, and no risk of touching Core's scan state from a remote probe, which is the standing prohibition.

`CompStudiable.EverStudiable()` and `CurrentlyStudiable()` were read in source for the same reason and are also safe: between them they consult the studied thing, its parent holder, its own comps, the player-set prisoner interaction mode and the global tick. **Neither takes a pawn and neither reads any worker's map.**

| Rule | Where | Why |
|---|---|---|
| `GetStudiableThingsAndPlatforms(map)` | candidate | takes the map as an argument; pure read |
| `KnowledgeCategory != null` | candidate | a fact about the comp |
| `EverStudiable()` | candidate | holding-platform and imprisonment requirements of the entity itself |
| `CurrentlyStudiable()` | candidate | study enabled, the frequency cooldown, `CanStudy`, and the interaction mode the player set |
| `IsForbidden(Faction)` | candidate | the faction overload; the pawn overload reads the pawn's *current* map |
| `CanReserve(platform)` **and** `CanReserve(heldPawn)` | **arrival only** | Core reserves both; both are pawn-specific |
| `thing == pawn` | **arrival only** | identity against the worker |

### A rotating window over an unindexed collection

The studiable set is a `HashSet<Thing>`, which has no stable index, and the standing rule is that every bounded scan is a rotating window and never a prefix. So the scan enumerates, skips to a per-worker start offset, takes up to twelve, and — if it ran out before twelve — enumerates a second time to pick up the wrap. Re-enumerating a `HashSet` allocates nothing, and the set is small in practice.

The arrival check is unwindowed, as every deployment's arrival check is: a window that missed the one studiable entity would release the deployment while work remained and plan the worker straight back across the gate.

### An empty platform is not work

A holding platform is the *work target*, but the studiable thing is the entity held on it — exactly the substitution Core makes in `HasJobOnThing` before it looks for the comp. `Subject()` does that substitution, and a platform with no `HeldPawn` yields nothing.

Core then dereferences `TryGetComp<CompStudiable>()` **without a null check**, relying on the cache only ever holding studiable things. This provider null-checks anyway: a remote probe that threw would take down an unrelated work scan on the worker's own map.

## Anomaly content, and it degrades rather than claiming support

`WorkTypeDefOf` declares `DarkStudy` as `[MayRequireAnomaly]`, so `GetNamedSilentFail("DarkStudy")` returns null without the expansion and the provider is simply unavailable. Core's own giver agrees — `WorkGiver_DarkStudyInteract.ShouldSkip` is exactly `return !ModsConfig.AnomalyActive;`.

The profile's position, read from the register before writing: row **8 Anomaly** is *"optional native anomaly touchpoints; Rimrooms supplies its own Core threat, evidence, and containment loops"*, so the campaign must stay whole without it — which is precisely what an unavailable provider gives. Rows **138 Move Your Monolith** (a layout utility, explicitly *"not a Rimrooms gate or navigation system"*), **140 Name Your Entities** (display naming only; stable Rimrooms ids stay separate) and **39 Anomaly Research Asteroid** (optional expedition content, no adapter planned) were checked and none of them touches this route.

## The defect: a DLC gate that had never been there

Adding an Anomaly-gated def raised the question of how the mod already handled DLC-only defs — and the answer was that it did not.

```xml
<WorkGiverDef>
  <defName>RR_ConnectedChildcare</defName>
  <workType>Childcare</workType>
```

`Childcare` is a **Biotech** `WorkTypeDef`. With no `MayRequire`, that `<workType>` is an **unresolved cross-reference at load on a Core-only install** — a red error in a mod whose entire stated position is that it needs nothing but base Core. Both childcare giver defs have shipped that way since 0.6.4-dev.

The C# side had always been right: `ChildcareProvider` uses `GetNamedSilentFail` and becomes unavailable without Biotech, and the 0.6.4 record says so accurately. Only the XML half was missing, and nothing was checking it. **This is the same shape as the `Bill_Production` defect found in the previous checkpoint** — careful C# beside a def that quietly contradicts it.

Both childcare defs are now gated `MayRequire="Ludeon.RimWorld.Biotech"`, and both new dark study defs `MayRequire="Ludeon.RimWorld.Anomaly"`.

### Why the existing compliance check could never have caught it

The compliance check looks for DLC **package ids** appearing ungated. It could not have found this, because the def never mentions Biotech at all — it mentions `Childcare`, and knowing that `Childcare` belongs to Biotech requires reading the game's own data.

So `tools/check-dlc-gating.py` now does exactly that. It indexes every `defName` shipped under `RimWorld/Data/*/Defs/**`, marks anything not defined by `Core` as DLC-only, walks every packaged mod XML, and fails on any element whose text is a DLC-only defName inside a def that does not carry the matching `MayRequire`. **6,063 DLC-only defs indexed; 4 references found in the package, all gated.**

Reading the game's data rather than a hand-written list is the point: a list of names would have to be maintained and would rot exactly the way the thing it checks rotted.

Prose is excluded by tag — a keyed string whose English text collides with a defName is not a cross-reference. The live example is the word `Researcher` inside `<RR_Role_research>`, which collides with an Anomaly def and is plainly not a reference to it.

The check was verified by deliberately removing a gate and confirming it reported the failure, then restoring it.

## Priority

Continue **112**, above Core's only `DarkStudy` giver (`StudyInteract`, 110), so a traveller is not turned around. Plan **2**, below everything local. Fifty-six cross-gate numbers now, all player settings, tunable live.

## Saved state

**None added.** The deployment record already carries a provider id and `dark-study` is a new value in an existing field. A 0.6.5-dev save loads unchanged.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and the project fully recompiled **twice**; identical assembly SHA-256 both times.
- All 58 package XML files parse; every `RR_` label and settings key resolves with **0 missing**; every Rimrooms `giverClass` resolves; all **28** priority pairs name real `WorkGiverDef`s with keyed labels.
- `tools/check-dlc-gating.py`: 6,063 DLC-only defs indexed, 4 references, all gated. Verified to fail when a gate is removed.
- Compliance: zero destructive patch operations, no `texPath` outside `RR_`, no `modDependencies`, no non-original package asset. 76 approved package files, 0 missing. Reference manifest recomputed, no drift. No attribution strings.

## Not done, and named

- **Anomaly's other work** — `ExtractBioferrite` and `DoctorTendToEntities` sit in `Doctor`, and `ActivitySuppression`, `ExecuteEntity`, `ReleaseEntity` and `InterrogatePrisoner` sit in `Warden`. Both of those work types already have deployments, so a worker who crosses for tending or wardening will do this work locally on arrival. No separate family is needed and none is claimed.
- **`TakeEntityToHoldingPlatform` and `TransferEntity`** are `Hauling` givers and belong to the hauling upkeep gap, not here.

## For the post-completion test phase

With Anomaly present: a contained entity on a far coordinate attracting a researcher who then studies it; an **empty** holding platform attracting nobody; an entity on its study cooldown attracting nobody until the cooldown passes; a prisoner whose Study interaction the player switched off attracting nobody; and a platform or entity already reserved by somebody on that map attracting nobody. **Without Anomaly:** the mod loads with zero errors, the dark study work giver defs are absent, and the provider is unavailable. **Without Biotech:** the same, for childcare — which is the case that was broken and is the reason this checkpoint exists.
