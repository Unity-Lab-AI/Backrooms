# Phase 2: physical evidence and company research

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** implemented source in progress, 2026-09-28. Compiler evidence is separate from owner-launched gameplay acceptance. No game has been started by this work.

## Task and source route

- TODO: [Phase 2 vertical slice](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md#phase-2--code-architecture-and-safe-vertical-slice); features RR-EVD, RR-MSN, RR-ECO, RR-UI.
- Player contracts: [first playable](../FIRST_PLAYABLE_CONTRACT.md), [inventory](../FIRST_SLICE_CONTENT_INVENTORY.md), [actions](../OPERATIONS_ACTION_CONTRACTS.md), [state dictionary](../CAMPAIGN_STATE_DICTIONARY.md), [style](../research/VISUAL_AUDIO_STYLE_BRIEF.md).
- Exact source: Core row 4, `Ludeon.RimWorld`, Assembly-CSharp SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`; [review](../research/reviews/mods/official-4-Ludeon.RimWorld.md). No optional mod/DLC assembly is referenced.
- Pinned implementation surfaces inspected locally: `WorkGiver_Researcher`, `JobDriver_Research`, `Toils_Goto`, `Toils_Haul.StartCarryThing` and `DropCarriedThing`, `Scribe_References`, `Scribe_Collections`, and the Core ResourceBase/BuildingBase/WorkGiver/recipe definitions. Private reference decompilations remain in ignored `.local/`; none is distributed.

## Implemented player route and ownership

1. A coordinate can create one unique physical `RR_RouteRecording`. The branch links it to a case with a stable evidence ID. A retry finds an already spawned recording and registers it rather than spawning another. Existing missing/destroyed evidence is preserved as a loss; the site can still be reopened.
2. Expedition recovery establishes custody through the actual recording and case in the same expedition manifest at headquarters. The case and recording remain separate physical items. Both are rechecked during analysis; moving the case away pauses further work. A located field item cannot be analyzed remotely.
3. `WorkGiver_CompanyLaboratory` uses the native Research work priority. A researcher with Intellectual 4 reserves the bench, interaction spot and recording, walks to the item, picks it up through the native haul toil, carries it to the powered bench and performs work. Interruptions preserve work on the evidence record. The item remains a normal physical object.
4. Completed analysis records its researcher and tick and awards one branch insight. The analyzed status is the receipt preventing repeated awards. The initial survey posts its separate $5m receipt after required room/mismatch observations and analysis. The $1m bonus uses a separate receipt and requires the original three-person crew alive at headquarters plus the entity observation; a later physical rescue can satisfy that condition without paying the base reward again. These are implemented conditions, with runtime evidence pending.
5. The Operations investigation panel commits the insight to Gate Telemetry. A further staffed laboratory job advances a saved company project. The project is a custom `RimroomsProjectDef`, because the inspected Core research selector does not provide a safe Core-only insight prerequisite hook. Colony research stays on its native path.
6. Completed Gate Telemetry reveals the player's surveyed room records and known connections in the atlas before repeat entry. It reveals no unexplored room or additional coordinate. This is the concrete first-slice interpretation of “better repeat-site planning”; it does not alter the opening duration.

The campaign component owns evidence, insight receipts and project progress. The map/native inventories own the physical recording. Jobs own transient targets/reservations and the active project ID. View code invokes services and owns no simulation state.

## Durable field observations

`RecordFieldObservation` ([source](../../src/RimroomsAsyncIndustries/Company/EvidenceObservations.cs)) stores a typed observation only when the linked physical route recording is present at the saved destination, a matching expedition is active there, the witness is a live member of that expedition and is physically in the observed room, and another live member of that same expedition carries the physical field recorder on-site. The saved row includes a stable deduplication ID, observation kind, actual room indices/tag number where relevant, witness identity and room, recorder identity/carrier, and game tick. It accepts room surveys, a witnessed displaced survey tag, a follow-up recorder-gap observation for that same tag, and a live entity sighting; it does not accept a spawn attempt or remote/HQ facts.

The route checklist is derived from one stored `room_survey` observation in each of the six required room families (`threshold_room`, `survey_lobby`, `office_copy`, `service_passage`, `borrowed_corridor`, `return_gallery`). It does not infer recorded coverage from the map's `surveyed` flags. The sole compatibility exception is a prior true route boolean on an older save, captured as `legacyRouteRecorded`; old booleans are not converted into fabricated observation rows. Campaign relationship validation rejects malformed or duplicate observation rows and invalid analyzed-report snapshots.

When analysis completes, the record freezes a copy of the available observations with analyst and completion tick. An older analyzed record without typed observations keeps an explicit “legacy details unavailable” report; a new empty report says its details are unavailable rather than inventing them. The snapshot and observation rows are saved additively. Save/load, custody changes, event authenticity, and report display still require in-game verification.

## Files

- [Investigation service](../../src/RimroomsAsyncIndustries/Company/InvestigationServices.cs), [saved records](../../src/RimroomsAsyncIndustries/Company/CampaignRecords.cs), [field observations and frozen report](../../src/RimroomsAsyncIndustries/Company/EvidenceObservations.cs).
- [Project Def](../../src/RimroomsAsyncIndustries/Investigation/RimroomsProjectDef.cs), [physical evidence component](../../src/RimroomsAsyncIndustries/Investigation/CompRouteEvidence.cs), [work checks](../../src/RimroomsAsyncIndustries/Investigation/LaboratoryUtility.cs), [work giver](../../src/RimroomsAsyncIndustries/Investigation/WorkGiver_CompanyLaboratory.cs), [job driver](../../src/RimroomsAsyncIndustries/Investigation/JobDriver_CompanyLaboratory.cs).
- Package XML: `1.6/Defs/RimroomsProjectDefs/RR_CompanyProjects.xml`, `ThingDefs_Buildings/RR_InvestigationBuildings.xml`, `ThingDefs_Items/RR_FieldEquipment.xml`, `ThingCategoryDefs/RR_FieldCategories.xml`, `JobDefs/RR_InvestigationJobs.xml`, `WorkGiverDefs/RR_InvestigationWork.xml`, `RecipeDefs/RR_FieldEquipmentRecipes.xml` beneath the [mod root](../../Mod/Rimrooms%20-%20Async%20Industries/).
- English: [RR_Investigation.xml](../../Mod/Rimrooms%20-%20Async%20Industries/1.6/Languages/English/Keyed/RR_Investigation.xml).

## Physical equipment and provisional tuning

The recorder, tags, beacon, case and recording have ordinary mass, health, hauling and storage behavior. Replacement equipment is manufactured by native bills at the electric smithy or machining table from real steel/components. A replacement recorder carries no observations; there is no recipe for the unique evidence. Shared kit and recording remain separate physical items, with the evidence case acting as a custody requirement rather than granting invisible extra inventory capacity.

Initial analysis work is 3,000 units; Gate Telemetry needs one insight and 6,000 work units. Pawn ResearchSpeed scales progress. The company lab work giver is priority 110 within Research, ahead of the native research giver's 100, while active company work exists. Native work priorities still determine whether a pawn researches. All these values require balance observations.

## Failure/recovery and acceptance still needed

- Power off/breakdown, pawn interruption, blocked item/bench, forbidden item, missing skill/capacity, and save/load during carrying/work must preserve the object and saved progress. Verify that cleanup drops carried evidence safely and reservations release.
- A successful analysis must award exactly one insight through interrupted work, reload and repeated jobs. Starting/reloading a project must spend exactly its recorded insight cost once.
- Verify the six required room survey rows, displaced-tag room pair, recorder-gap follow-up, and actual spawned-entity observation are accepted once each; confirm remote facts, missing recorder, nonmember witnesses, and failed entity spawns are refused. Save/load before and after analysis and confirm the frozen report remains unchanged after later events.
- Verify settled survey/bonus receipts separately from analysis, with partial return, injury, stranded crew, missing case, destroyed recording and repeat trips.
- Validate stockpile filters, actual modded stack settings, replacement bills, item art, bench interaction cell and Research-work ordering in the owner-launched full profile, then focused Core-only cases. Static XML and successful compilation do not establish these results.
- Confirm the atlas exposes only surveyed connections and that the benefit is useful in normal play.

The inspected API route is implemented; runtime results and full campaign research remain outstanding.
