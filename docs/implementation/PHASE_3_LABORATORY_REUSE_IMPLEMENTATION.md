# Existing research bench laboratory binding

**Task started and source implemented 2026-09-28; lead integration/build pending.** RR-EVD/RR-FAC/RR-UI under [Phase 3 build continuation](PHASE_3_BUILD_RECORD.md), the [content-reuse policy](../CONTENT_REUSE_POLICY.md), [evidence/research actions](../OPERATIONS_ACTION_CONTRACTS.md), [saved ownership](../CAMPAIGN_STATE_DICTIONARY.md) and [first playable](../FIRST_PLAYABLE_CONTRACT.md). Core inventory row **4**, package **Ludeon.RimWorld**, is the only provider in scope.

## Task and ownership

Replace laboratory runtime selection of the superseded custom bench with an explicit player designation of one existing Core `SimpleResearchBench` or `HiTechResearchBench` at this branch's headquarters. Keep evidence analysis and company research, native researcher work, physical evidence custody and native bench identity. No ThingDef, texture, item, recipe or global patch is added.

Exclusive files are listed below and now exist. Lead owns scenario, shared UI hook, company/evidence services, package allowlist, save policy and build.

State owner: independent schema-1 GameComponent with saved branch, headquarters, exact bench reference/load ID and provider/Def identity. No automatic designation during construction, load, scanning or drawing. Player route: Operations designation, actual bench inspection, change/clear binding; jobs revalidate current binding. Missing, moved, destroyed, foreign, forbidden, unpowered or obstructed providers leave progress/evidence intact and report readiness failure.

Acceptance remains planned: explicit opt-in only; Simple and HiTech native power differences; same-object save/load/minify/replace/loss; designation changed during work; analysis/research unchanged; ordinary bench available without company work; no optional-provider assumption. No builds, tests, game launches, profile operations, staging or Git are performed by this task.

## Source basis

Pinned Core assembly SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`, local ILSpy **9.1.0.7988**. Existing ignored `.local/inspection-work/` files supply `Building_ResearchBench`, `WorkGiver_Researcher`, `JobDriver_Research`, `ResearchProjectDef` and `CompPowerTrader`. Additional exact-type inspections are stored only under ignored `.local/inspection-laboratory/`. Installed native XML: `Data/Core/Defs/ThingDefs_Buildings/Buildings_Production.xml` and `Data/Core/Defs/Books/BookDefs.xml`.

Reproduce the additional bounded type inspection with PowerShell; keep output in the ignored directory:

```powershell
$managed = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed'
New-Item -ItemType Directory -Force '.local/inspection-laboratory' | Out-Null
foreach ($type in 'Verse.ModContentPack','RimWorld.WorkGiver_Scanner','Verse.Book','RimWorld.CompBook','RimWorld.CompReadable') {
  & '.local/tools/ilspycmd.exe' -t $type -r $managed "$managed/Assembly-CSharp.dll" |
    Set-Content -Encoding utf8 ".local/inspection-laboratory/$type.cs"
}
```

## Implemented files and player route

| Existing source file | Implemented responsibility |
| --- | --- |
| [RimroomsLaboratoryComponent.cs](../../src/RimroomsAsyncIndustries/Investigation/RimroomsLaboratoryComponent.cs) | Saved exact-object binding, branch/HQ ownership, provider identity, revision, designation/clear actions and live readiness |
| [LaboratoryUtility.cs](../../src/RimroomsAsyncIndustries/Investigation/LaboratoryUtility.cs) | Jobs accept only the ready designated bench and a living, free, capable, present player researcher |
| [WorkGiver_CompanyLaboratory.cs](../../src/RimroomsAsyncIndustries/Investigation/WorkGiver_CompanyLaboratory.cs) | Only the designated bench is offered to company job search; existing evidence and project work remain the work source |
| [OperationsLaboratoryBinding.cs](../../src/RimroomsAsyncIndustries/UI/OperationsLaboratoryBinding.cs) | Paginated existing-bench choices, live readiness, designation, clear, and native camera/selection inspection |
| [RR_LaboratoryBinding.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Languages/English/Keyed/RR_LaboratoryBinding.xml) | Player-facing setup, readiness, recovery, provider identity and native-research explanations |

Lead UI hook: call **`DrawLaboratoryBinding(Listing_Standard listing, RimroomsCampaignComponent campaign)`** from the Operations Investigation pane or Facilities. It is a private method on the existing partial Operations class. Add the keyed XML to the package allowlist. The scenario should provide/build an ordinary native research bench; **do not call designation automatically**. The new component has no scenario initializer, tick, spawn, grant or load-time selection effect.

Public service actions: `DesignateBench(Thing)`, `ClearDesignation()`, `CanDesignate(Thing)` and `Readiness()` return `CompanyActionResult`. Read-only identity includes `DesignatedBench`, `BenchLoadId`, `BenchDefName`, `ProviderPackageId`, `LabelAtDesignation`, `HasDesignation`, `Revision`, and `FaultKey`. `AvailableBenches()` provides current supported physical choices; `IsReadyBench(Thing, campaign)` is the job guard.

Designation requires the actual Core definition, `Building_ResearchBench` class, current DefDatabase identity, player faction, visible/spawned/live object and loaded player HQ. Allowed Defs are exactly **SimpleResearchBench** and **HiTechResearchBench**, with `modContentPack.IsCoreMod`. A mod's new bench or similarly named clone is not inferred compatible. Ordinary patches to an existing Core definition still require later full-profile acceptance; the provider check is not a compatibility claim.

Power/interaction availability is checked separately from designation: a player may designate a bench awaiting power/repair, but company jobs refuse until it is usable. The native simple bench has no power comp; it does not acquire an invented electricity requirement. The hi-tech bench must retain its native `CompPowerTrader` and be powered. Any actual power comp also obeys its current power, flick and map electricity-disabled state. Forbidden state, breakdown, obstructed/out-of-bounds/fogged interaction cells and pawn skill/custody/mental/health restrictions block work without changing native objects.

Native `WorkGiver_Researcher` and ResearchManager are unmodified. The company workgiver returns no job when there is no ready company evidence or active company project. Native research may use the bench normally; designation does not interrupt an already-running native job. Reservations decide actual access. Changing/clearing the binding invalidates the existing company job through its preexisting `LaboratoryUtility.CanWork` fail condition; saved evidence/project progress remains in company records, and the original physical evidence follows native job/carry cleanup.

Native source shows `JobDriver_Research` applies the bench's `ResearchSpeedFactor` as well as pawn speed. Simple has factor **0.75**; hi-tech has **1.0**. Follow-up source inspection confirms the lead applied that factor in shared `JobDriver_CompanyLaboratory.cs`, hooked `DrawLaboratoryBinding` in Operations and retained the native simple bench in the start at `(41, 0, 42)`. This task does not change recipes, evidence awards, insight receipts or research unlocks.

## Saved behavior and old development content

Schema **1** saves one branch ID, original HQ reference, exact bench reference/load ID, existing Def/provider identity and monotonic revision. There is no second building owner or deep-held bench. Unknown/corrupt schemas stop actions and display a preserve-original-save warning. Missing or despawned benches keep their identity record and stop work; the player may reinstall the same native object, explicitly choose another valid bench, or clear the role. A new object at the old coordinates is never silently accepted.

An existing company save acquires an empty unbound laboratory component without grants or conversion. This alone needs no campaign schema change. The superseded `RR_FieldAnalysisBench` is never auto-replaced, removed or bound here. **Removing old custom ThingDefs from the package remains a separate lead-owned development-save compatibility decision** under [save policy](../SAVE_MIGRATION_POLICY.md). Preserve the old build/save and document any required fresh start; a successful compiler result cannot establish old-save compatibility.

## Core TextBook: suitability review only

The installed `Data/Core/Defs/Books/BookDefs.xml` confirms `TextBook` is Core content, with no DLC gate on its definition. Its `BookBase` has `stackLimit=1`, `tradeNeverStack`, physical mass **0.50**, quality, hit points, deterioration and haulability. `Verse.Book.CanStackWith(Thing)` returns false, preserving distinct normal merge behavior even if a stack-limit provider raises the Def value. A future evidence service must still validate actual `stackCount=1`, hold the exact object/load ID and preserve its original physical custody.

Source signatures confirmed: `Verse.Book.PostPostMake()`, `PostQualitySet()`, `GenerateBook(Pawn author = null, long? fixedDate = null)`, `CanStackWith(Thing)`, `PawnReadNow(Pawn)`, `OnBookReadTick(Pawn,int,float)`, `ExposeData()`; `Book.Title` is getter-only. `RimWorld.CompBook : CompReadable` owns native book outcomes. `CompReadable.Initialize`, `PostPostMake` and `PostExposeData` create/save the native doers. `Book.ExposeData` saves its native title/description/generation counter and presentation/read state.

This is a suitable candidate for an existing physical document carrier, **not a blank or inert paper item**. TextBook includes native skill experience and a configured quest-reading outcome chance; ordinary reading, sale, damage, destruction and reservation continue to matter. Do not remove those native outcomes globally or generate/rewrite a book on every custody check. `PostPostMake` automatically calls GenerateBook only when no quality comp exists; TextBook has quality and `PostQualitySet` generates its contents. A future creation path must explicitly initialize native quality/content once before registration, and avoid repeating quality/generation calls that reroll outcomes/title. The native title stays native; show Rimrooms case/record labels in its company UI binding rather than accessing private book fields. An ordinary unrelated TextBook must remain unrelated until explicitly bound.

No book creation, quality change, evidence adapter, native patch, document transfer or book gameplay was implemented or run by this task. Optional RWT physical transfer still needs its own validated identity/receipt route.

## Evidence limits and remaining work

Read installed Core XML and the exact pinned decompiled type bodies; manually compared the changed laboratory source and UI with those APIs. No automated checks, compilation, game, tests, staging, Git operation or profile operation was performed. Lead integration/build, native research versus company-work scheduling, selected-bench save/minify/reinstall/loss, physical evidence on interrupted jobs, power/interaction recovery and full-profile behavior remain unverified acceptance cases. The company analysis/research feature is retained; this task replaces its workstation provider only.
