# Phase 2 Def and Core Source Review

Reviewed 2026-09-28 against the 0.2.0 package in `Mod/Rimrooms - Async Industries/1.6` and the locally installed RimWorld 1.6 Core source/data. The pinned `Assembly-CSharp.dll` reports version `1.6.9676.17735` and SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`.

This was a static XML/source review. It did not compile the mod, load Defs in RimWorld, launch the game, or run tests. Decompiler evidence is in ignored `.local/inspection-work/`; it is local audit evidence, not a distributable source dependency.

## Findings

### Corrected during this review: gate damage-override enum

The first read of [`RR_GateJobs.xml`](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/JobDefs/RR_GateJobs.xml) found `true` in `checkOverrideOnDamage` for both `RR_CalibrateGate` and `RR_OperateGate`. Core declares `Verse.JobDef.checkOverrideOnDamage` as `CheckJobOverrideOnDamageMode`, whose accepted values are `Never`, `OnlyIfInstigatorNotJobTarget`, and `Always` (`.local/inspection-work/Verse.JobDef.decompiled.cs:18`; `.local/inspection-work/Verse.CheckJobOverrideOnDamageMode.decompiled.cs:3-8`). The shared file now uses `Always` at lines 10 and 19. That is a valid native value; this Def-loading blocker is closed. C# compilation alone would not have exposed the former XML enum mismatch.

### Corrected after review: disable native launch targeting for Backrooms sites

[`RR_BackroomsSites.xml`](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Defs/WorldObjectDefs/RR_BackroomsSites.xml#L3) defines the machine-linked map site and already disables caravan map incidents, but it does not set `validLaunchTarget`. In the pinned Core assembly, `RimWorld.WorldObjectDef.validLaunchTarget` defaults to `true` (`.local/inspection-work/RimWorld.WorldObjectDef.decompiled.cs:31`); Core's travelling transport objects explicitly set it to `false` (`Core/Defs/WorldObjectDefs/WorldObjects.xml:135,237`). For the documented machine-only access path, set `<validLaunchTarget>false</validLaunchTarget>` on `RR_BackroomsSite`. This is an integration/behavior omission, not a Def-load error. It has been reported to the lead; no package file was changed in this review.

## Checks completed

Lead integration follow-up: `RR_BackroomsSite` now sets `validLaunchTarget=false`. Its map-parent class also disables generic caravan entry, native transporter/shuttle options and normal gravship landing. This closes the reviewed native access omission in source; custom transport adapters still require their own review.

- All 21 package Def XML documents parse as XML. No duplicate `(Def type, defName)` pairs were found; `RR_CalibrateGate` appearing once as a `JobDef` and once as a `WorkGiverDef` is valid because those use separate Def databases.
- Every package `ParentName` resolves to a pinned Core named parent or another package parent. Checked examples include `ScenarioBase`, `BuildingBase`, `BenchBase`, `ResourceBase`, `BasePlayerPawnKind`, `StaticWorldObjectBase`, and the package's `RR_StaffBase`, `RR_FieldItemBase`, and `RR_FieldFabricationBase`.
- Typed native references checked in the package resolve against Core or the package: scenario pawn kinds and skills, ThingDefs and stuff, recipe users/ingredients, work types, job work settings, `RR_GateConsole` bill-giver selection, world/map generator Defs, and the `Fog`/`ScenParts` generation steps. Native WorkTags used by starting staff, including `Shooting`, are present in Core `Verse.WorkTags`.
- Native scenario configuration is consistent with Core: `RR_StaffConfiguration` uses `RimWorld.ScenPart_ConfigPage_ConfigureStartingPawns_KindDefs`; its `kindCounts` entries support `kindDef`, `count`, and `requiredAtStart` through Core `PawnKindCount`/`StartingPawnCount` (`.local/inspection-scenario/RimWorld.ScenPart_ConfigPage_ConfigureStartingPawns_KindDefs.cs:10-18,143`; `.local/inspection-work/RimWorld.PawnKindCount.decompiled.cs`).
- Package-owned fully-qualified `driverClass`, `giverClass`, `workerClass`, `thingClass`, `worldObjectClass`, `genStep`, `scenPartClass`, and UI class references match declarations in `src/RimroomsAsyncIndustries`. The key extension Defs align with their code: `RimroomsProjectDef` fields in `RR_CompanyProjects.xml`, `RimroomsStartDef` fields in `RR_Starts.xml`, and gate/evidence/route-aid comp-property fields in their corresponding ThingDefs. Their base classes match Core extension points (`JobDriver`, `WorkGiver_Scanner`, `RecipeWorker`, `GenStep`, `ScenPart`, `MapParent`, `ThingComp`, and `Def`).
- Core-backed native field routes were checked for recipes, workgivers, jobs, scenarios, map generators, world objects, and building properties. The gate assembly recipe uses Core `RecipeDef.workerClass`, `requiredGiverWorkType`, ingredient/filter/product, and `recipeUsers` routes; the bill giver uses Core `WorkGiver_DoBill` plus `fixedBillGiverDefs`. Generator ambience, `Recipe_Smith`, EMP, work-type/skill, and ThingDef references are present in Core.
- All XML `texPath` targets resolve to package PNGs. All five English `DefInjected` XML files target existing Defs and fields. Every literal `RR_*.Translate()` key found in package C# has an English keyed entry (the package currently has 372 keyed entries). Dynamically composed localization families were not exhaustively enumerated in this pass.

## Remaining acceptance boundary

The `validLaunchTarget` correction is present. Later audio and flooring additions have their own [audio source](PHASE_2_AUDIO_SOURCE_REVIEW.md) and [interior presentation](PHASE_2_INTERIOR_PRESENTATION.md) records. The package still needs an actual Core-only 1.6 Def load and scenario-start acceptance pass. Static checks cannot prove Verse's full XML loading/`ConfigErrors` outcome, page flow, map generation, or runtime behavior. The result is therefore: **no other definite Def-load blocker found in this reviewed snapshot; runtime Def acceptance remains unverified.**
