# HEYUNITY — project audit and coding-agent handoff

**Project:** Rimrooms - Async Industries / Backrooms  
**Root:** C:\Users\gfour\Desktop\Backrooms  
**Date:** 2026-10-10  
**Deliverable:** completed inspection report. The issues below have not been repaired.

## 1. Scope and evidence

The owner requested a comprehensive inspection without implementation changes, then specifically requested HEYUNITY.md and a copyable coding-agent handoff. **This report is the only file written by the reviewers.** No source, existing document, asset, profile, setting, save, build artifact or Git ref was changed. No build, project checker, test suite, game launch, staging, service action, network request or publication was performed.

AGENTS1.md and UNITY_MEMORY.md were read. **AGENTS2.md was absent**; existing AGENTS.md was used as the project-guide fallback, with its stale instructions identified below. This is an explicit assumption, not a claim that the missing guide was read.

Inspection began on feature/bug-testing at **aa79267b307a3bbaffa8293774d3ad6f5bc6d238**. Concurrent external work changed .local/qa/stream-host.py and docs/TODO.md. Last reviewed HEAD: **8ec0d29f5235a416aa8c2dab7675d553e7c575a1**. The changed host was reread and affected findings corrected. During final review, an external untracked .local/tw/read-chat.py helper also appeared; its complete short body was inspected without execution. It was preserved, and no independent material defect was established from that read.

Pre-existing untracked files were preserved: .local/obs/_brb_until, .local/qa/_go.request, AGENTS1.md and UNITY_MEMORY.md.

All paths below are relative to the root above unless explicitly absolute. Source line numbers refer to this inspection and must be rechecked against the coding agent's baseline.

### Classification

- **P1:** prioritize before trusting the affected money, physical custody, travel, save or destructive-operation route.
- **P2:** functional correctness, recovery, operational control or materially misleading workflow.
- **P3:** narrower maintenance/navigation issue.
- **Source defect:** a concrete inconsistent execution path, not necessarily reproduced in the game.
- **Conditional:** the named configuration or preceding repair is required.
- **Risk / acceptance gap:** further confirmation or authorized runtime evidence is needed.

This is a broad project review, not a formal proof that no bugs remain or a runtime compatibility certification. Suggested fixes defer to the coding agent.

## 2. Structure and current implementation

### Tracked repository

Baseline: approximately **3,585 tracked files**.

| Area | Files | Purpose |
| --- | ---: | --- |
| .local/ | 1,774 | automation/QA, provider register, source inspections, local rig |
| docs/ | 913 | design, decisions, workflow, implementation and evidence |
| src/ | 266 | solution/project and mod source |
| Mod/ | 199 | tracked copyable game-package content |
| .claude/ | 160 | workflow harness, hooks and runtime tools |
| assets/ | 92 | source assets/masters/provenance |
| tools/ | 66 | build, package, stage, export and research tools |
| outputs/ | 54 | saved research/asset outputs |
| training/ | 33 | tracked training/export/application pipeline |
| stream/ | 3 | service engine/admin/README |
| linux/, windows/ | 4 each | launch/admin/stop wrappers |

There are **263 tracked mod C# files**, 21 namespaces and 19 domain folders:

Company 45; ConnectedWork 37; Generation 27; Gate 25; UI 24; Portals 21; Threats 15; Scenario 12; Investigation 11; Economy 9; Presentation 7; Procurement 7; Expedition 6; Core 5; Personnel 5; Automation 4; Audio 1; Facilities 1; Incidents 1.

The large ignored training/preflight/llama.cpp tree is a vendored dependency. Historical generated/inspection/proof material was inventoried or selectively inspected; it is not all independent current implementation.

### Game package and build

The sole copyable mod is **Mod/Rimrooms - Async Industries/**.

Current About.xml: Rimrooms - Async Industries; Operator; Rimrooms.AsyncIndustries; RimWorld 1.6; **0.13.0-dev**; **zero hard modDependencies**, approximately 294 loadAfter entries. This matches the later October 3 dependency-removal direction. Older mandatory-DLC/collection instructions are stale.

The project targets net472/C#7.3, local Core/Unity references, SDK 9.0.308, pinned Core, strict package allowlist and warnings-as-errors. AssemblyVersion 0.8.8.0 and FileVersion 0.7.1.0 differ from package/project0.13.0-dev; not inherently a runtime defect, but diagnostics must distinguish them.

### Substantial source implementation

The project already includes:

- Three scenario families, company/inside-start setup, first-exit logic, starting-pawn preservation and automated new-game setup.
- Native door designation, laboratory/permanent natural portals, saved coordinates, connection graphs, crossing receipts and recovery.
- Seven physical work adapters, 28 worker-deployment providers, materials/native jobs and food/rest routing.
- Seeded room layouts, archetypes/palettes/motifs, furnishings/resources, fog exploration, fixture changes and revisits.
- Pressure, native-state inhabitants, unusual encounters, containment and gate danger.
- Hiring, salary/payroll, role recommendations and native work controls.
- Branch USD ledger, bearer bonds, goods exchange, supply tiers, physical procurement and delivery recovery.
- 25 request definitions: seven tutorial and 18 generated families; bound quest journals and settlement.
- Evidence custody/analysis, witness disagreements, dispositions and 44 company projects.
- Facility observations and remote-site registration/operating costs, with 8-to-12 registered-site capacity.
- Legacy expedition crew/cargo/return/recovery.
- Fourteen Operations panes, keyed text, alerts, gate audio and shared menu/loading/generation slides.
- Separate local Unity player/stream rig: service engine/panel, gameplay ladder, bridge/OBS/Twitch/voice/avatar and training tools.

**Breadth is substantial; the connections are not reliably complete.** The findings below are failures within implemented routes, alongside genuine missing integration/acceptance work.

## 3. Static observations and build identity

Plain reads, metadata/hash comparisons and inline standard-library parsing were used. Project tests/checkers were not executed.

| Inspection | Observation | Limit |
| --- | --- | --- |
| Allowlist/disk | 200 allowed and 200 actual files; no missing/unexpected paths | Not gameplay evidence |
| XML | All 98 package XML files parse | No semantic/runtime guarantee |
| Def names | 426 distinct names | Same name in different Def types is valid |
| Keyed translations | 2,117 keys; no duplicates found | Not full localization acceptance |
| Literal translation calls | 900 literal RR_ uses found Keyed entries | Dynamic/DefInjected cases excluded |
| Audio | 17 WAVs, 48 kHz mono PCM16, 0.4–4 seconds | No listening/loop/loudness verification |
| Textures | 83 PNGs:12 menu, 70 gameplay, 1 preview | No in-game visual verification |
| Graphic_Multi | North/east/south present for9 unique paths / 10 appearances inspected | Does not prove rotation readability |
| Python syntax | All 1,150 tracked .py files AST-parse | No imports/dependencies/execution |
| Limited secret-shape scan | No candidates for inspected private-key/token patterns | Not security clearance |

Package:98XML,83PNG,17WAV,1DLL,1License.txt =200 files. **199 are tracked; DLL is deliberately ignored and built locally.**

### B01 — P1: three different DLL identities

**Repository:** Mod/Rimrooms - Async Industries/1.6/Assemblies/RimroomsAsyncIndustries.dll

- SHA256 **B7ED4A0AD0513B1690CBA51F8A6224CA78A615CD51E49C21395F27DE03FB89B6**
- 1,181,184 bytes

**Staged:** C:\Program Files (x86)\Steam\steamapps\common\Rimworld\Mods\Rimrooms - Async Industries\1.6\Assemblies\RimroomsAsyncIndustries.dll

- SHA256 **8B3072D6E9E5EE798E0E1F24E4B844B315D2153F689E632CCEFB3B6B65A34AFD**
- 1,181,184 bytes

**Both saved receipts:** artifacts/build/package-manifest.json and artifacts/build/staging-receipt.json

- SHA256 **2655C2B333606CD4DDDC072026A1A7A6D097D9BADEDE55F7DC5CF25A1C61C7A4**
- 1,147,904 bytes; version 0.13.0-dev;200 files

Other receipt entries matched. Current source-to-DLL equivalence is **unestablished**. NOW's byte-identical/tracked-DLL statement is false for this state. Normal staging/export guards should refuse mismatched receipts.

**Suggestion:** establish an explicit source baseline, then produce matched build/package/staging receipts when authorized. Do not rewrite hashes to bless unknown binaries or use the version label as proof.

## 4. Company, economy, evidence and requests

Source paths below are relative to the project root.

### E01 — P1: paused withdrawal duplicates bonds for one debit

**Sources:** src/RimroomsAsyncIndustries/Company/BondTreasury.cs:191–198; src/RimroomsAsyncIndustries/Company/CampaignServices.cs:311–325; src/RimroomsAsyncIndustries/Procurement/CreditWithdrawalGizmo.cs:57–73.

Issuance identity uses map/cell/TicksGame. Repeating the same withdrawal while paused returns Existing from PostTransaction but issues fresh paper again, provided the preliminary balance check passes.  
**Suggestion:** saved issuance sequence/custody receipt; AlreadyApplied resumes original issuance, never creates a second batch.

### E02 — P1: payment refusal occurs after goods are destroyed

**Sources:** src/RimroomsAsyncIndustries/Company/ValuablesExchange.cs:104–115; src/RimroomsAsyncIndustries/Company/BondTreasury.cs:62–67,96–101,133–138; src/RimroomsAsyncIndustries/Economy/CompRimroomsCreditBeacon.cs:139–153; src/RimroomsAsyncIndustries/Company/CampaignServices.cs:306–319.

Exchange/banking destroys goods before posting credit. Inactive/faulted companies, mismatched receipts or overflow can refuse. Beacon eligibility requires a component rather than CanOperate, so ordinary non-company saves can offer the command.  
**Suggestion:** eligibility/value preflight, held custody and idempotent consumption/payment commit. Existing payment must not consume a different batch.

### E03 — P1: generated salvage becomes Outside before odd-origin marking

**Sources:** src/RimroomsAsyncIndustries/Economy/CompRimroomsOddOrigin.cs:132–138; src/RimroomsAsyncIndustries/Economy/OddOriginService.cs:100–110,134–138; src/RimroomsAsyncIndustries/Generation/GenStep_BackroomsDestination.cs:359–363; src/RimroomsAsyncIndustries/Generation/RoomContentBuilder.cs:326,600; src/RimroomsAsyncIndustries/Threats/BackroomsPressure.cs:198–220.

Ordinary furnishings/stock spawn with LayoutReady=false, receive Outside origin, and cannot be overwritten by the finishing pass. The produced-goods catalog can be empty/incomplete; odd contracts and shelter bonuses become wrong. Specially marked/contained objects may differ.  
**Suggestion:** distinguish generating Backrooms maps from ordinary maps; establish correct birth provenance and actual content catalog.

### E04 — P1: free portal exploration misses the evidence pipeline

**Sources:** src/RimroomsAsyncIndustries/Company/EvidenceSettlement.cs:73–79; src/RimroomsAsyncIndustries/Company/InvestigationServices.cs:195onward; src/RimroomsAsyncIndustries/Investigation/WorkGiver_CompanyLaboratory.cs; src/RimroomsAsyncIndustries/Expedition/RimroomsExpeditionComponent.cs:84; src/RimroomsAsyncIndustries/UI/OperationsEvidenceRecovery.cs:37.

For new coordinates explored solely through ordinary portal visits, settlement skips records without a legacy expedition source while analysis requires secured evidence. Recording creation is tied to dispatch/recovery. Historical coordinates may already have recordings and legacy ownership. Return/debrief/exposure ownership also remains legacy-dependent.  
**Suggestion:** saved portal-visit/field-recording/custody/return ownership; preserve historical expedition recovery without requiring dispatch.

### E05 — P1: crossing drops the journal required for survey

**Sources:** src/RimroomsAsyncIndustries/Portals/CrossingInventoryPolicy.cs:108–129; src/RimroomsAsyncIndustries/Threats/FirstSliceSiteComponent.cs:315–318; src/RimroomsAsyncIndustries/Generation/JobDriver_ExploreRoom.cs:91; src/RimroomsAsyncIndustries/Generation/ExplorationMapComponent.cs:91; src/RimroomsAsyncIndustries/Expedition/ExpeditionCargo.cs:117,186.

Crossing drains FirstUnloadableThing, but survey requires a supported book in inventory. Journals loaded by the Rimrooms pickup/loadout route are treated as unloadable freight unless a native/provider inventoryStock rule retains them. Carrying in hands also fails the survey predicate.  
**Suggestion:** explicit retained field equipment and shared survey/custody rules across valid carried states.

### E06 — P2: cancelling an old request targets the newest family instance

**Sources:** src/RimroomsAsyncIndustries/UI/OperationsRequests.cs:225–226; src/RimroomsAsyncIndustries/Company/RequestLine.cs:368–376,614–623; src/RimroomsAsyncIndustries/Company/RequestGeneration.cs:193–227.

Cards pass Def name, while RequestFor picks the newest record. Repeated accepted families therefore make card cancellation target the wrong job.  
**Suggestion:** RequestRecord.Id for every instance action.

### E07 — P2: dynamically displayed routes cannot settle

**Sources:** src/RimroomsAsyncIndustries/Company/RequestRoutes.cs:41–105; src/RimroomsAsyncIndustries/UI/OperationsRequests.cs:198–210; src/RimroomsAsyncIndustries/Company/RequestLine.cs:663–710; src/RimroomsAsyncIndustries/Company/QuestBookCollection.cs.

UI adds Purchase/Testify routes, while baselines/completion/collection use only definition.successRoutes.  
**Suggestion:** one effective-route model for display, saved baselines and settlement.

### E08 — P2: abandoned quotes can exhaust procurement permanently

**Sources:** src/RimroomsAsyncIndustries/Procurement/RimroomsProcurementComponent.cs:19,245–247,1365–1370; src/RimroomsAsyncIndustries/UI/OperationsProcurement.cs:105–106.

100-quote cap; only latest 8 shown; no discard API/UI; invalid receiving-zone/provider quotes cannot be accepted yet retain slots.  
**Suggestion:** player cancellation/discard and pagination, without quest deadlines.

### E09 — P2: journal resupply repeats before pods arrive

**Sources:** src/RimroomsAsyncIndustries/Company/RecordBookDelivery.cs:106–130,138–150,183–187; src/RimroomsAsyncIndustries/Company/CampaignServices.cs.

Presence search ignores incoming pods and carrying hands. Checks every 60 ticks precede110-tick delivery; saved delivery timestamp is not a pending guard.  
**Suggestion:** recursive custody lookup and pending-shipment receipt. src/RimroomsAsyncIndustries/Company/QuestPaperwork.cs:394–435 already solves an analogous recursive lookup.

### E10 — P2: contained evidence can be sold while fees continue

**Sources:** src/RimroomsAsyncIndustries/Company/EvidenceDispositionService.cs:65–85,120–121; src/RimroomsAsyncIndustries/Company/ValuablesExchange.cs:166–181; Mod/Rimrooms - Async Industries/1.6/Defs/ThingDefs_Items/RR_CompanyJournal.xml.

Exchange ignores disposition; tradeable journal is destroyed while Contained record remains billable.  
**Suggestion:** protect bound/contained evidence and reconcile destruction/disposition/custody.

### E11 — P2: supply settlement destroys installed/reserved furniture

**Source:** src/RimroomsAsyncIndustries/Company/OddSupplyContracts.cs:217–244,255–270.

AllThings matching accepts installed buildings and ignores reservations/in-use state. An accepted furniture order can consume an operating stove/bench, unlike the owner's uninstalled-furniture example.  
**Suggestion:** explicit eligible delivery custody/minified furniture and reservation protections.

### E12 — P2: integration diagnostics confuse Workshop and package IDs

**Source:** src/RimroomsAsyncIndustries/Core/InstalledIntegrations.cs:97,104,111,118,125,150–152.

ModsConfig.IsActive receives numeric Workshop IDs. Correct identities: SmashPhil.VehicleFramework; nova.rimworldtogether; vanillaexpanded.gravship; OskarPotocki.VanillaVehiclesExpanded; vanillaexpanded.gravship2.  
**Suggestion:** separate package identity from source/Workshop ID. Correct diagnostics are not completed adapters.

### E13 — P2: prices shown differ from charged totals

**Sources:** src/RimroomsAsyncIndustries/Procurement/CorporateSupplyGizmos.cs:109–110,115–117; src/RimroomsAsyncIndustries/Company/CorporateSupply.cs:96–127; src/RimroomsAsyncIndustries/UI/OperationsProcurement.cs:70–83; src/RimroomsAsyncIndustries/Procurement/RimroomsProcurementComponent.cs:222 onward,266–267.

Labels use base unlock/catalog prices while payment applies settings/research discounts; quoted unit and total can disagree.  
**Suggestion:** shared actual pricing for preview, quote, affordability and settlement.

## 5. Gates, scenarios, threats and connected work

Source paths below are relative to the project root.

### P01 — P1: original gate equipment binds but readiness rejects it

**Sources:** src/RimroomsAsyncIndustries/Gate/GateProviders.cs:42,45,66–106; src/RimroomsAsyncIndustries/Gate/NativeGateBinding.cs:373–376,601–605; src/RimroomsAsyncIndustries/Scenario/GateReadinessReview.cs:120.

RR_GateConsole/RR_FieldAnalysisBench are supported by binding, but readiness requires exact CommsConsole/Battery/TableMachining and reports LinkMissing. Setup warnings retain similar assumptions.  
**Suggestion:** common provider predicates across assignment/readiness/jobs/warnings.

### P02 — P1: relief workers/consoles cannot execute the advertised job

**Sources:** src/RimroomsAsyncIndustries/Gate/WorkGiver_RimroomsGate.cs:133–190; src/RimroomsAsyncIndustries/Gate/JobDriver_RimroomsGate.cs:141–143,156; src/RimroomsAsyncIndustries/Gate/GateOperatorRelief.cs:183–202.

WorkGiver/relief accept qualified staff and BoundConsoles, but driver resolves the primary direct console and fails unless already the assigned operator.  
**Suggestion:** consistent console resolution and safe operator handover; distinguish maintenance from startup.

### P03 — P1: reload replays occupant arrival effects

**Sources:** src/RimroomsAsyncIndustries/Threats/BackroomsPressureComponent.cs:142–164,212; src/RimroomsAsyncIndustries/Threats/InhabitantService.cs:473–478.

Unsaved occupiedLastSweep makes existing occupants fresh arrivals on first post-load sweep, replaying population/anomaly/fixture changes.  
**Suggestion:** saved arrival generation or initialization without entry effects.

### P04 — P1/P2: inhabitant cap resets per entry

**Sources:** src/RimroomsAsyncIndustries/Threats/CoordinatePressureLadder.cs:76,185–205; src/RimroomsAsyncIndustries/Threats/InhabitantService.cs:59–75.

hostilesPlaced starts at 0 each call and does not count existing population. Entries/reloads can accumulate inhabitants beyond the intended concurrent cap.  
**Suggestion:** surviving tagged-population counts and separate event/concurrent budgets.

### P05 — P1: release misses outgoing edges and transfer guards

**Source:** src/RimroomsAsyncIndustries/Generation/CoordinateRelease.cs:73–76,118–139.

Filtering by edge.CoordinateId misses A-to-B edges identified by B when releasing A; map removal can leave dead anchors/in-flight ownership and regeneration conflicts.  
**Suggestion:** enumerate every edge/receipt touching the released map, preserve reconnect memory and settle custody first.

### P06 — P1/P2: NPC egress omits physical/access checks

**Sources:** src/RimroomsAsyncIndustries/Threats/GateEgress.cs:99–120,171–180; src/RimroomsAsyncIndustries/Portals/PortalTraversalPolicy.cs:407–455.

Proximity/state checks bypass normal Availability, allowed area, forbidden status, PawnCanOpen and physical passage. Latest direction permits zoned/permitted NPC crossing.  
**Suggestion:** shared native access/traversal guard. Do not revive obsolete blanket NPC prohibition.

### P07 — P2: incursion runs before cutoff handling

**Sources:** src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs:435,460; src/RimroomsAsyncIndustries/Threats/GateIncursion.cs:80; src/RimroomsAsyncIndustries/Portals/PortalTraversalPolicy.cs:346–347.

TickIncursion precedes KillSwitch and omits cutoff eligibility, allowing a same-tick arrival before emergency closure.  
**Suggestion:** cutoff-first and shared physical availability.

### P08 — P2: terminal crossing receipts block approach repair

**Sources:** src/RimroomsAsyncIndustries/Portals/RimroomsPortalNetwork.cs:193–197,215–220; src/RimroomsAsyncIndustries/Portals/PortalCrossingService.cs:57–61.

Availability repair uses an in-flight test that includes completed history. A terminal-aware helper exists elsewhere.  
**Suggestion:** one active-receipt predicate.

### P09 — P2: Walk Through selects first remembered address

**Sources:** src/RimroomsAsyncIndustries/Portals/DoorCrossingGizmo.cs:35–43,54–67,108–109; src/RimroomsAsyncIndustries/Portals/PortalTravelService.cs:77–91.

Remembered closed A can be chosen while B is open, causing refusal.  
**Suggestion:** actual active connection identity, explicit choice if multiple usable edges.

### P10 — P2: emergency retry reuses old failed opening identity

**Sources:** src/RimroomsAsyncIndustries/Portals/PortalTravelService.cs:190–197; src/RimroomsAsyncIndustries/Gate/PortalGateOpening.cs:276–280,294–299.

Existing receipt returns before reset; retry can replay failure rather than begin a recovery attempt.  
**Suggestion:** saved per-attempt sequence with idempotency within each attempt.

### P11 — P2: reveal sweep clears later player forbids

**Source:** src/RimroomsAsyncIndustries/Generation/UnexploredRoomsAreQuiet.cs:137–147.

Repeated clearing affects deliberate player forbids after revelation.  
**Suggestion:** release only mod-installed initial flags, once.

### P12 — P2: autonomous exploration issues orders to busy/drafted pawns

**Source:** src/RimroomsAsyncIndustries/Generation/ExplorationMapComponent.cs:85–98,160–161.

Periodic ordered exploration lacks drafted/manual/urgent-needs guards and can replace manual or needs jobs. The native outcome for a drafted pawn was not observed.  
**Suggestion:** explicit autonomous/idle eligibility and cancellable resumable plans.

### P13 — P1/P2: inside start commits before arrival succeeds

**Source:** src/RimroomsAsyncIndustries/Scenario/ScenPart_RimroomsStart.cs:140,170,175–179.

branchInitialized is set before SoloGroupOpening.Open; failure leaves surface crew with retry blocked by Existing.  
**Suggestion:** separate branch initialization from saved arrival completion/recovery.

### P14 — P2: needs routing excludes natural/multi-hop routes

**Source:** src/RimroomsAsyncIndustries/ConnectedWork/CrossForNeed.cs:243–286.

Direct active-laboratory requirement excludes permanent natural gates/chains.  
**Suggestion:** shared graph routing, permanent expiry and tightest temporary route window; later verify diet/bed/access reachability.

### P15 — P2: standing recall targets global legacy trip

**Sources:** src/RimroomsAsyncIndustries/Gate/GateStandingRecall.cs:118–135; src/RimroomsAsyncIndustries/Expedition/RimroomsExpeditionComponent.cs:26,117–125; src/RimroomsAsyncIndustries/Gate/CompRimroomsGate.cs:488–489.

Gate B warning can recall first active legacy trip A; free portal travelers lack matching recall.  
**Suggestion:** gate/session-owned traveler routes, separate legacy handling.

### P16 — P2: failed first exit leaves surface claims behind

**Source:** src/RimroomsAsyncIndustries/Portals/WorldExit.cs:352,377–405.

Settlement/home/map state mutates before arrival succeeds; retry can leave duplicate/orphan claims.  
**Suggestion:** durable claim/arrival receipt, reuse and visible recovery.

### P17 — P2, conditional: recipe ingredients counted in incompatible units

**Source:** src/RimroomsAsyncIndustries/ConnectedWork/ConnectedBillScan.cs:120,147,176–190.

Required units use one basis Def; stock sums raw counts across allowed Defs with different nutrition/value. Can falsely show supplied or over-import.  
**Suggestion:** common recipe contribution units or verified native ingredient selection, preserving budgets.

### P18 — P2, conditional: fixed-prefix scans starve later remote work

**Sources:** src/RimroomsAsyncIndustries/ConnectedWork/Providers/RoofWorkProvider.cs:134–142,162–169; src/RimroomsAsyncIndustries/ConnectedWork/Providers/FieldworkProviders.cs:288–338; src/RimroomsAsyncIndustries/ConnectedWork/Providers/PaintingProvider.cs:289,311; src/RimroomsAsyncIndustries/ConnectedWork/Providers/BillWorkProvider.cs:207–210.

First 24 roof cells / 40 growing cells are rescanned without rotating. Complete cells remain in areas/zones, so later work stays invisible. Blocked paint/suspended bill prefixes similarly hide later entries. The budgets themselves are sensible.  
**Suggestion:** fair rotating inner cursors/windows rather than simply raising limits.

### P19 — P2, conditional: partial energy debit can be charged again

**Source:** src/RimroomsAsyncIndustries/Gate/NativeGateBinding.cs:174–209,763–766.

taken starts at 0; an exception after partial DrawFromNativeCircuit debit is recorded as zero rather than observed before/after delta. Acknowledged retry can charge the paid portion again. No actual provider throw was reproduced.  
**Suggestion:** explicit partial-debit measurement/receipt on exception.

### P20 — P2: fixture warnings disappear when a marked stack splits

**Sources:** src/RimroomsAsyncIndustries/Generation/CompRimroomsFixtureTell.cs:46,51,94–102; .local/decomp/roofscan/Verse/Thing.cs:1620–1635; .local/decomp/roofscan/Verse/ThingWithComps.cs:532–540; .local/decomp/roofscan/Verse/ThingComp.cs:100–102.

Core creates a fresh split item and calls PostSplitOff; its default hook copies no custom state. FixtureTell saves its tell and prevents incompatible merges, but has no split hook. A partial haul/split therefore loses the warning on the new piece, which can merge with ordinary stock. Source remainder retains its tell. No game reproduction was performed.  
**Suggestion:** copy the exact tell in PostSplitOff, following src/RimroomsAsyncIndustries/Economy/CompRimroomsOddOrigin.cs:173–178.

## 6. Mod automation channel

Source paths below are relative to the project root.

### A01 — P2: commands after 32 are discarded

**Source:** src/RimroomsAsyncIndustries/Automation/RimroomsAutomationComponent.cs:90–100.

ReadAllLines, Delete, then Take(32) loses remainder and reads unbounded input. Producer append/read/delete races also lose commands.  
**Suggestion:** atomic bounded spool with retained remainder/IDs/acknowledgements; coordinate RT-11.

### A02 — P2: selected map and selected pawn can disagree

**Source:** src/RimroomsAsyncIndustries/Automation/RimroomsAutomationComponent.cs:169,179,approximately 391,486–503.

Coordinates use CurrentMap; pawn lookup searches all maps. set_area can assign displayed-map area to another-map pawn.  
**Suggestion:** explicit validated map/stable pawn IDs and matching ownership.

### A03 — P2: parser mishandles escaping; guest command is unsupported

**Source:** src/RimroomsAsyncIndustries/Automation/RimroomsAutomationComponent.cs:128–165,36,437–453.

Flat parser lacks JSON quote/backslash escape handling. Header advertises guest bed ownership; execution accepts only colonist/prisoner/slave.  
**Suggestion:** real versioned command protocol and accurate capability list. Review recipe availability/research guards; bypass not established here.

### A04 — P2: setup Explore orders busy/drafted colonists

**Source:** src/RimroomsAsyncIndustries/Automation/SetupTools.cs:94–113.

Despite idle description, downed/mental exclusions still allow busy/drafted/urgent-needs pawns; ordered jobs and additional destinations are queued. Distinct from P12's controller.  
**Suggestion:** shared owner-preserving autonomy eligibility.

### A05 — risk: refused new-game step is still marked handled

**Source:** src/RimroomsAsyncIndustries/Automation/WorldSetupDriver.cs:127,approximately135–147 and handlers.

Void page actions can ignore Advance refusal, then handled.Add prevents retry. Reflection setters can silently fail while progress claims success. Same-window-ID retry behavior needs Core lifecycle confirmation.  
**Suggestion:** verified step result, pending/retry state and read-back before marking done.

### A06 — risk: repeated bed setup ignores pending capacity

**Source:** src/RimroomsAsyncIndustries/Automation/SetupTools.cs:231onward.

Missing owned bed accounting can repeat blueprints before construction completes.  
**Suggestion:** idempotent finished/planned sleeping-capacity accounting.

## 7. Unity player, stream and training rig

### RT-01 — P1/P2: unauthenticated local mutation endpoints

**Sources:** stream/admin.py:257–291; .claude/tools/persona-studio.cjs:315–432.

GO/colony/service/orders/credential/audio/shutdown mutations lack session token and strict Host/Origin/CSRF guards. Local callers can invoke; browser exploitation depends on localhost policies and was not attempted.  
**Suggestion:** session authorization, owner capabilities, Host/Origin/body validation.

### RT-02 — P2 risk: whole-rig stop kills before graceful close

**Source:** stream/services.py:103,327–345.

Name sweep includes game/OBS/Ollama before graceful OBS close. **Owner explicitly requested name-based kills**; consequences include unsaved/unrelated same-name processes, not unauthorized design.  
**Suggestion:** reconcile requested semantics and consider owned-PID graceful-first/explicit force fallback.

### RT-03 — P1/P2: persisted GO breaks fresh startup

**Sources:** .local/qa/keep-playing.py:197–235; stream/services.py:452–472; stream/admin.py:265,278–280.

existing_go skips asked initialization needed by later launch flow.  
**Suggestion:** startup generation, consumed-once owner request, honest panel state.

### RT-04 — P2: continuing turns omit fresh owner orders

**Source:** .local/autopilot/autopilot.py:127–134,247–253,279–284.

Only fresh with_orders=True turns attach directives; continuations pass False despite binding-next-turn promise.  
**Suggestion:** versioned deltas at every turn boundary.

### RT-05 — P1: new-colony tool has no enforced owner grant

**Source:** .local/autopilot/tools.py:311–314,598–609.

Description says ONLY owner but any model call writes forced restart. Viewer influence/mistaken decisions are conditional triggers.  
**Suggestion:** separate consumable owner authorization and preserved-colony/save boundary.

### RT-06 — P2: read-only ladder rewrites canonical tracked rules

**Sources:** .local/autopilot/gates.py:19–21,172–179; .local/autopilot/tools.py:495–498; .local/autopilot/guards.py:9,28–64.

Queries write computed state into docs/playbook.gates.json, contradicting scratch-only/read-only claims.  
**Suggestion:** immutable canonical rules, atomic machine-local measured state.

### RT-07 — P2: symbolic guard thresholds silently ignored

**Sources:** .local/autopilot/gates.py:152–170; docs/playbook.gates.json:75,122,263,282,301,317,350.

Numeric parser fails on symbols/expressions and continues instead of enforcing guard.  
**Suggestion:** safe symbol resolution; visibly reject unresolved conditions.

### RT-08 — P2: ladder inputs are absent/hard-coded

**Source:** .local/autopilot/gates.py:40–102; docs/playbook.gates.json.

Missing measurements include grid_matches_plan, fields_all_default_crop, bill_rows, research_queue_empty, wants_click, has_power, defences_built, production_running, mountain_base_done, gate_online, ship_research_done; wall_gaps fixed at 0.  
**Suggestion:** verified measurements or explicitly disabled unfinished rungs.

### RT-09 — P1/P2: time helpers bypass the setup-pause guard

**Sources:** .local/autopilot/tools.py:231–244,417–422; .local/autopilot/guards.py:109; .local/qa/play.py:116,151,162; training/check_player.py:87–90.

After exploration, pause/set_time_speed enforce pawns_set and assign_set marks before time runs. play_slices forces Superfast/Normal through another route; play_for/play_until_letter remain allowed.  
**Suggestion:** central guarded time-advance capability, enforcing the current setup sequence on every route.

### RT-10 — P2: global mouse loan disables interruption protection

**Sources:** stream/services.py:257; .local/qa/keep-playing.py:399–402; .local/qa/real-click.py:15–20.

OWNER_LENT_MOUSE=1 bypasses movement abort during ordinary runtime.  
**Suggestion:** scoped loan with immediate owner interruption/release.

### RT-11 — P2: automation replies cannot be correlated

**Sources:** .local/qa/automate.py:35–56; .local/autopilot/tools.py:546–563; .local/qa/keep-playing.py:354–361; A01/A02.

Shared append/inbox disappearance/outbox offsets/keywords can acknowledge another caller or incomplete work.  
**Suggestion:** common client/mod protocol: IDs/map IDs/atomic queue/per-command outcomes/retries.

### RT-12 — P2: duplicated service engines diverge

**Sources:** stream/services.py; .local/qa/services.py:40–47,160; .local/qa/admin.py:45; stream/README.md:10–12.

Copied engine uses undefined QA on cold voice path and lacks same model/GPU setup; old admin still invokes it.  
**Suggestion:** wrappers over one implementation, inventory every caller.

### RT-13 — P2: Linux/macOS wrappers call Windows-only rig

**Sources:** linux/*.sh; stream/services.py:72–98; .local/qa/cursor-jobs.py:17; .local/qa/bridge.py:20; .claude/tools/unity-speak.py:65.

Windows paths/executables/WinDLL/winsound remain.  
**Suggestion:** declare actual platform support or complete platform adapters/prerequisites.

### RT-14 — P2: panel/ladder reads alter selection

**Sources:** stream/admin.py:72–76,211; .local/autopilot/gates.py:57–62.

Polling selects pawns to measure state, stealing player selection.  
**Suggestion:** identity-based reads without UI mutation.

### RT-15 — P2: camp/map/geometry assumptions are hard-coded

**Sources:** .local/autopilot/gates.py:22,57–75,83–86; .local/qa/heat-guard.py:34,45–49; stream/admin.py:74–80; .local/qa/cursor-jobs.py:88,94–95,383.

Map_0/names/rectangles/coordinates/screensize and label-based hostility do not survive new colonies/multiple maps.  
**Suggestion:** live stable identity/state discovery; preferences as configuration.

### RT-16 — P2: camera averages crew across maps

**Source:** .local/qa/follow-crew.py:26–31.

All colonist coordinates are averaged against displayed map.  
**Suggestion:** map-grouped crew focus.

### RT-17 — P2: heat rescue is logged before verified crossing

**Source:** .local/qa/heat-guard.py:38–50.

seen flag precedes fixed gate/menu action; crewSent without confirmation; retry suppressed.  
**Suggestion:** dynamic gate, saved per-pawn outcome and resumable retry.

### RT-18 — P2: public chat bypasses privacy/owner filters

**Sources:** .claude/tools/persona-studio.cjs:248–264; .claude/tools/stream-overlay.html:148–160; .local/qa/stream-host.py:256–263.

Raw names/text reach public API/UI. textContent avoids HTML injection, but does not provide owner/privacy filtering.  
**Suggestion:** separate private directives/public chat and filter on server.

### RT-19 — P2: parallel speech overwrites shared WAV

**Source:** .claude/tools/unity-speak.py:35–41,49–52,59 and callers.

Shared unity-voice.wav/OBS playback races.  
**Suggestion:** serialized speech queue, unique outputs and playback acknowledgement.

### RT-20 — P2: diffusion initialization is outside lock

**Source:** .claude/tools/unity-face-sd.py:38–53,56–64.

Concurrent requests initialize shared GPU pipelines before lock.  
**Suggestion:** serialize lazy initialization/rendering; bound resources/queue.

### RT-21 — P2: failed replies consume chat permanently

**Sources:** .local/qa/stream-host.py:252–298; .local/autopilot/autopilot.py:327–338.

Inbox offset/greeted state advances before successful reply/speech.  
**Suggestion:** pending queue, acknowledged delivery, bounded retry.

### RT-22 — P2: EOF exits host; swallowed failures retain dead socket

**Sources:** .local/qa/bridge.py:55,59; .local/qa/stream-host.py:60–65,179–184,299–300,320–323.

Current host DOES recover ordinary uncaught exceptions. But SystemExit on EOF/deadline bypasses Exception handlers; locally swallowed failures leave non-null dead socket and block reconnect.  
**Suggestion:** controlled exceptions, close/reset and bounded session reconciliation.

### RT-23 — P2: word regex contains actual backspace

**Source:** .local/qa/stream-host.py:112,115.

U+0008 replaces intended regex word boundaries; still present after concurrent edits.  
**Suggestion:** correct raw boundary expressions.

### RT-24 — P2: broad process matching/racy start

**Source:** stream/services.py:64,193–233,310–325.

admin.py-like fragments can identify another project; scan/start not serialized.  
**Suggestion:** canonical path/owned PID/start identity and process-control mutex.

### RT-25 — P2: legacy launcher bypasses single engine

**Sources:** Unity Plays RimWorld.cmd:4; .claude/tools/unity-plays-rimworld.py:44–64; stream/README.md.

Independent game/chat flow can announce live before OBS verified.  
**Suggestion:** delegate or explicitly retire with owner-visible replacement.

### RT-26 — P2: training markers not bound to inputs

**Sources:** training/pod/bootstrap.sh:14–18; training/pod/run.sh:8–9,41,50–56.

stage.done can reuse old outputs after changed data/config/code.  
**Suggestion:** hash-bound run manifest/model/data/config/converter/output identity.

### RT-27 — P2: no resumable training checkpoints

**Source:** training/pod/train.py:89–97.

save_strategy=no/final-only loses interrupted progress.  
**Suggestion:** bounded resume checkpoints chosen by coding agent.

### RT-28 — P2: failed fetch can train stale workspace

**Source:** training/pod/bootstrap.sh:6,15–22.

set-u alone permits clone/copy failures to continue.  
**Suggestion:** fail closed and verify/promote acquired inputs atomically.

### RT-29 — P2 risk: serving pod sleeps indefinitely

**Source:** training/pod/bootstrap.sh:24.

No terminal retention/deadline/budget policy. Billing/current pod not inspected.  
**Suggestion:** owner-approved bounded retrieval/retention policy.

### RT-30 — P2: environment/converter unpinned, options silently dropped

**Sources:** training/pod/run.sh:12–19,28–32; training/pod/train.py:73–81.

Latest dependencies/current converter and degraded unsupported options undermine repeatability.  
**Suggestion:** pinned required capabilities and explicit recorded fallback.

### RT-31 — P2 risk: artifact access/expected checksum unverified

**Sources:** training/pod/bootstrap.sh:11; training/pod/run.sh:45; training/apply.py:35–60.

HTTP lacks application auth; platform proxy not inspected. Apply stamps arrived hash instead of checking trusted expected hash.  
**Suggestion:** restricted artifact access/trusted expected digest.

### RT-32 — P2: model apply returns success after failure

**Sources:** training/apply.py:41–45,56–69; stream/services.py:171–182.

Caught failures exit0; no-op identity lacks full target digest/template validation.  
**Suggestion:** meaningful failure status and verified applied-model readiness.

### RT-33 — P2: model prerequisite chain incomplete

**Sources:** stream/services.py:113,141–149; training/apply.py:16–18,43–45.

Required qwen3:8b omitted; custom unity-local pulled instead of constructed; readiness not awaited.  
**Suggestion:** exact base/custom manifest, local construction and readiness.

### RT-34 — P2: harvested examples never join training inputs

**Sources:** .local/train/harvest.py:83–102; training/pod/train.py:14–18.

Local harvested voice/tool/rule data differs from fixed training/data consumed by pod. No reviewed ingestion/promotion mapping.  
**Suggestion:** provenance/dedup/outcome-grounded dataset promotion; harvesting alone is not continual learning.

### RT-35 — P1: updater can discard its only recovery backup

**Sources:** .claude/scripts/unity-install.ps1:127–148,154–168,258–264; .claude/scripts/unity-install.sh:98–100,125–147,153–163.

Fixed-file preservation, delete/replace, failed restore and unconditional cleanup can lose backup/custom files.  
**Suggestion:** validated sibling staging/atomic promotion, durable backup and explicit conflict/preservation policy. Do not reproduce against owner's workspace.

### RT-36 — P1: Stargates zero-delay never activates in supplied source

**Rimrooms:** src/RimroomsAsyncIndustries/Portals/CompRimroomsEmergence.cs:298; src/RimroomsAsyncIndustries/Portals/StargateBridge.cs:366–367.  
**Provider:** CompStargate.cs:76–82,389–396,518–519.

delay 0 never enters positive countdown tick; bridge returns true after void invocation.  
**Suggestion:** supported activation then verify active state/exact peer.

### RT-37 — P1: provider excludes attached ordinary-door endpoints

**Rimrooms:** src/RimroomsAsyncIndustries/Portals/StargateBridge.cs:159–174,354–366.  
**Provider:** SgUtilities.cs:45–46; CompStargate.cs:92–94,159–177.

Provider lookup requires exact Building_Stargate, not ordinary doors with added comp. Far door missing; after RT-36 repair a native destination Stargate can be selected instead.  
**Suggestion:** exact supported adapter or provider presentation only/Rimrooms travel.

### RT-38 — P1: dynamic provider/transporter state cannot restore on load

**Rimrooms:** src/RimroomsAsyncIndustries/Portals/StargateBridge.cs:169,339; src/RimroomsAsyncIndustries/Portals/CompRimroomsEmergence.cs:606–614,625–630; Mod/Rimrooms - Async Industries/1.6/Patches/RR_NativeGateProviders.xml:16–58.  
**Core inspection:** .local/decomp/roofscan/Verse/ThingWithComps.cs:237–249; .local/decomp/roofscan/RimWorld/CompTransporter.cs:238–266.  
**Provider:** CompStargate.cs:849–871.

LoadingVars rebuilds def.comps, omitting dynamic comps. Later fresh attachment cannot read prior peer/iris/loading/held contents. Actual loss severity needs disposable-save evidence.  
**Suggestion:** supported pre-load reconstruction/serialization/custody; no silent empty reattachment.

### RT-39 — P1, conditional: provider has independent unsafe transit

**Provider:** FloatMenuOptionProvider_Stargate.cs:25–28,46–55; JobDriver_EnterStargate.cs:16–19,48–50; JobDriver_BringToStargate.cs:24–25,35–37; CompStargate.cs:447–470,548–599.  
**Rimrooms:** src/RimroomsAsyncIndustries/Portals/CompRimroomsEmergence.cs:266.

Once active, provider menus bypass Rimrooms receipts/ownership/availability. Receiving-end entry may feed disintegration disposal. Returning when not live does not close provider session.  
**Suggestion:** reconcile every menu/loading/transit/closure route, or disable provider transit on host doors and retain presentation only.

**RT-36–39 evidence boundary:** supplied installed source at C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2831698056\Source\Stargates\. Installed1.6 DLL exists; source-to-DLL equivalence not established. Recheck actual loaded provider before runtime attribution.

## 8. Documents, repository and authority

### D01 — P2: active instructions contradict later decisions

**Files:** AGENTS.md, CONTRIBUTING.md, README.md:31, docs/CONTENT_REUSE_POLICY.md, docs/ARCHITECTURE.md, docs/GATE_0_DECISIONS.md, docs/TODO.md, docs/NOW.md.

Original-content prohibition vsOctober 6 reversal; mandatory DLC/profile vsOctober 3 removal; old 0.4 checkpoint vs 0.13; owner-only launch vslater local-player permission; old no-NPC traversal vspermitted native access. CONTENT_REUSE_POLICY contains both current reversal and unretired contradictory rules; README claims no new items/buildings while package includes them.  
**Suggestion:** one current decision index, explicit historical labels, synchronized guides/contracts/queue/acceptance. Preserve history; do not invent new scope.

### D02 — P2: ledger completion/counts/decomposition stale

**Files:** docs/ROADMAP.md:21–26,58; docs/DECOMPOSED.md; docs/TODO.md; docs/TEST.md; docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md.

No-game-ever-launched/TODO-empty/source-package-art counts contradict current records. DECOMPOSED remains template. Master had190 checked / 66 open; initial TODO 38 top-level open, concurrent faction task makes 39. Fixed TEST labels are not computed receipts.  
**Suggestion:** reconcile bounded feature IDs/implementation vsacceptance, preserve owner quotes and archive; counts alone do not close features.

### D03 — P2: old consignment catastrophe is already repaired in source

**Files:** docs/TODO.md:28–44; src/RimroomsAsyncIndustries/Company/RimroomsCampaignComponent.cs:436–453.

Current validator distinguishes IsOddConsignment/named coordinate from ordinary IsOddSupply.  
**Suggestion:** historical diagnosis/fix record plus outstanding save acceptance, not repeated source repair.

### D04 — P2: publication authority disagrees on repositories/ref case

**Files:** docs/PUBLISHING.md, docs/HOWTO.md, AGENTS.md, docs/NOW.md; local refs.

Four repositories/twelve refs, then a Forgejo hold/six refs/capitalized Prep/Develop/Main conflict with newer lowercase PR cascade/no separatemodrepo. Local case variants remain; remote state not queried.  
**Suggestion:** later authorized publication must inspect actual refs/latest direction and replace stale instructions. Keep hold unless lifted; no force-push/browser-auth assumption. No push authorized here.

### D05 — P2: tracked/build/staged identities are conflated

**Files:** docs/NOW.md; .gitignore; artifacts/build/*.json; B01.

DLL is ignored, not tracked; current staged bytes differ. Clean source clone intentionally needs build; public export not inspected.  
**Suggestion:** separate source/build/stage/export receipts and exact verified identities.

### D06 — P2: tracked third-party inspection material contradicts provenance rules

**Files:** .local/inspection-*; AGENTS.md; docs/ARCHITECTURE.md; docs/CONTENT_REUSE_POLICY.md; .gitignore.

Approximately 412 tracked inspection C# files,414 .local C# total, including provider/Core supplied/decompiled material. Descriptions call these ignored/local or forbid copying source. They are outside the200-file mod package; no claim that game package bundles them and no legal ruling.  
**Suggestion:** evidence-preserving provenance/public-private boundary review; do not blindly delete.

### D07 — P2: local control triggers escape ignore policy

**Files:** .gitignore; .local/obs/_brb_until; .local/qa/_go.request.

Trigger files appear untracked; blanket staging can publish stale controls.  
**Suggestion:** explicit runtime-state root/ignores, preserving intentional tracked scripts/rules and owner data.

### D08 — P3: broken navigation

- docs/implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md:40 -> removed 1.6/Defs/ThingDefs_Items/RR_FieldEquipment.xml.
- docs/implementation/PHASE_2_THREAT_IMPLEMENTATION.md:10 -> removed Threats/Thing_QuietPursuer.cs.
- docs/implementation/evidence/authored-rotations-2026-10-06/prior-handoff-before-artwork.md:200 -> wrong archive-relative docs/TEST.md.
- docs/ASSET_REQUESTS.md:160 -> absent docs/TODO.md#active-portal-artwork-and-code-handoff-2026-10-06.

Scan covered626 root/docs Markdown/3,589 relative candidates. Explicit HTML anchors create false positives; do not call every candidate broken. TWITCH_PANELS example url is placeholder.  
**Suggestion:** archive-aware paths and current integration-record links, real anchor parsing.

## 9. Incomplete work and qualified risks

### G01 — permanent coordinate ceiling conflicts with open-ended exploration

src/RimroomsAsyncIndustries/Company/RimroomsCampaignComponent.cs:16 / src/RimroomsAsyncIndustries/Company/CampaignServices.cs:233 cap saved coordinates512. Release keeps history, so it is a lifetime discovery ceiling, not just loaded-map budget.  
**Suggestion:** durable discovered/retained/active identity model with bounded working set; don't erase revisits or remove all safety bounds.

Procurement512 orders compact terminal verified history (not512-purchase ceiling); delivery receipts compact at 64; site slots recycle; terminal applicant history trims.

### G02 — large histories/network performance unmeasured

Requests/ledger/obligations/evidence/contracts grow and repeat scans. Generation does synchronous 90,000-cell work and repeated power-route searches.  
**Suggestion:** measured authorized large-save/network benchmarks and preservation-safe indexing/compaction. No FPS failure measured.

### G03 — dedicated async RWT campaign integration incomplete

Custom dossier transfer/local study/reconnect/replay/facility-visit adapter was not established. Native provider coexistence and installed-mod display are not that implementation.  
**Suggestion:** exact provider route, branch ownership, physical comp/receipt transfer and both-client recovery; keep distinct from live shared control.  
**Built (2026-10-10, unverified in play):** `Company/BranchDossierExchange.cs` — signed (per-branch RSA-SHA256, key pinned per source branch on first import) dossier files in `<SaveData>/RimroomsDossiers`, sequence+nonce replay refusal, kept outbound payloads rewritable byte-for-byte, on-disk sequence floor for rolled-back senders, signed receipts that acknowledge on the sender. Read-only on arrival. **Missing provider piece:** RWT 26.8.31.1 exposes no third-party payload path (`PM_Transfers` only carries its Thing/pawn manifest; packet handlers are attribute-registered inside RTClient), so the RWT route is refused with a Keyed reason. Physical comp transfer through the RWT manifest remains unbuilt.

### G04 — company vehicle/gravship layer incomplete

Dedicated company mission/spaceflight/Vehicle Framework/VGE adapter not established.  
**Suggestion:** map promised actions to native behavior or narrow adapters with DLC/provider boundaries and evidence.  
**Built (2026-10-10, unverified in play):** `Company/CompanyVehicles.cs` (reflection, no reference) — VF `Dialog_LoadCargo` per company vehicle, vanilla `Dialog_FormCaravan` (VF patches it for vehicles) from company surface maps, Odyssey grav-engine select for native launch. **Refused:** vehicles through the gate (VF has no MapPortal path), gravship from a pocket map, every action with provider/DLC absent. VVE and VGE 1/2 expose no launch/cargo/mission API, so no adapter beyond the native systems.

### G05 — broad descriptions exceed current abstraction

Roles largely recommend native duties; eviction unregisters company site rather than deleting map/pawns; some delivery/purchase request routes measure stock rather than consume shipment; interviews/review are immediate UI actions rather than scheduled pawn jobs.  
**Suggestion:** describe intended abstractions accurately or finish promised routes.

### G06 — conditional procurement origin / consignment wording

Procurement creates unstamped cargo (src/RimroomsAsyncIndustries/Procurement/RimroomsProcurementComponent.cs:1209–1229), but normal RemoteSites destinations exclude Backrooms (src/RimroomsAsyncIndustries/Company/RemoteSites.cs:198–199,268–299,366–376). Purchased goods become odd only if inside-start HQ remains inside when contact/procurement activates; src/RimroomsAsyncIndustries/Company/CorporateContact.cs:38–53 lacks explicit surface restriction. Not a universal exploit.

src/RimroomsAsyncIndustries/Company/OddConsignmentMissions.cs:223–255 deliberately permits any sufficiently deep coordinate; origin lacks exact coordinate. Older wording names goods from one specific site.  
**Suggestion:** confirm scenario HQ rebinding and approved semantics.

### G07 — remaining fault/provider risks

Further confirmation is required for:

- Direct scenario/world-exit/NPC despawn/spawn without common held-custody exception boundary.
- Cancelled connected-work references causing broader controller faults.
- HQ assumptions/multiple facilities/multiple gates to one coordinate.
- GateAura static glow when PortalAuraEnabled is disabled: clarify setting semantics.
- Board-up stock/resource accounting after pickup.
- Cursor process-liveness/lock races and live OBS/Ollama/CDP access/readiness.
- Relief/clear-squad delivery without durable payload receipt: src/RimroomsAsyncIndustries/Company/CompanyClearSquad.cs:245–253 charges/increments before DropThingsNear; src/RimroomsAsyncIndustries/Company/FacilityRelief.cs:175–179 records attempt before delivery. Native throw may leave partial effects/fresh retry.

These are not additional reproduced failures.

### G08 — current build/play/acceptance queue unfinished

Existing TODO/TEST include scenario wording/buttons and first-exit preview; unsupported bridge calls; thread/resource observations with unestablished causation; machining-table bill-menu NRE/explosion bounds; generated approach/retry/half-address; repeated-request payment; original artwork/rotations/gate overlays/audio acceptance; food/freezer/butcher/bills; defence/drafting/towers; layout/firebreaks/conduits; trade/research/power; player training/voice/stream countdown; resource efficiency; newest faction rule pending install/restart; full profile/DLC/RWT/save/performance/balance/release work.

These are prior records/queued work, not results of this audit. Newest TODO says voice trained/applied and player still training; voice GGUF exists, completed player GGUF was not found at inspected location. Live use/completion requires its own trusted receipt.

## 10. Preserve existing repairs and foundations

- Consignment relationship-validator distinction already exists.
- Quest paperwork searches recursive custody; field-journal resupply is the separate remaining defect.
- Gate projection draws aggregate circuit battery energy; old single-battery criticism is stale.
- Gate audio has sustained start/stop handling; old asset-request loop warning is historical.
- Menu/loading/generation share one slide pool; directional asset paths exist.
- Procurement physical custody/recovery and terminal compaction already exist.
- Host ordinary outer exception recovery exists; RT-22 is narrower.
- Native fallback bindings, work/generation budgets, saved identities/receipts are useful foundations.
- Build/stage utilities have allowlists/hash/destination/reparse/backups/rollback guards. Fix stale evidence, do not remove guards.

## 11. Suggested sequence — defer implementation to coding agent

This sequence is triage, not permission to edit/run/deploy:

### File reading order for the repair agent

These entry points exist. Read the report first, then the current context and applicable domain contracts. Old guides contain the D01 conflicts; compare their dates and exact owner decisions rather than treating every historical sentence as current.

| Purpose | Files, relative to the project root |
| --- | --- |
| Requested Unity context | AGENTS1.md; UNITY_MEMORY.md; AGENTS.md, with D01 caveat. AGENTS2.md is absent |
| Current work and historical decisions | docs/NOW.md; docs/TODO.md; docs/FINALIZED.md; docs/GATE_0_DECISIONS.md |
| Complete backlog and implementation map | docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md; docs/FEATURE_TRACEABILITY.md; docs/ARCHITECTURE.md; docs/ROADMAP.md; docs/DECOMPOSED.md |
| Regression and persistent ownership | docs/REGRESSION_CONTAINMENT.md; docs/SAVE_MIGRATION_POLICY.md; docs/CAMPAIGN_STATE_DICTIONARY.md |
| Travel, jobs, scenarios | docs/CONNECTED_COLONY_PORTALS.md; docs/SCENARIO_SETUP_AND_PORTAL_NETWORK.md; linked implementation/source records and the exact source paths in section5 |
| Money and company actions | docs/CAMPAIGN_ECONOMY_MODEL.md; docs/CAMPAIGN_ECONOMY_PROGRESSION.md; docs/OPERATIONS_ACTION_CONTRACTS.md; section4 source paths |
| Provider/RWT/DLC work | docs/MOD_INTEGRATION_PLAN.md; docs/COMPATIBILITY.md; docs/SOURCE_REGISTER.md; applicable dated per-mod review. A historical294-row inventory is not current compatibility proof |
| Assets/presentation | docs/CONTENT_REUSE_POLICY.md, with D01 caveat; docs/ASSET_REQUESTS.md, with historical loop warning and D08 caveats; docs/research/VISUAL_AUDIO_STYLE_BRIEF.md; docs/research/CONTENT_ACCESSIBILITY_BRIEF.md |
| Build identity and package boundaries | docs/BUILDING.md; tools/build.ps1; tools/stage-mod.ps1; tools/BuildCommon.ps1; tools/package-files.json; artifacts/build/package-manifest.json; artifacts/build/staging-receipt.json |
| Local rig and training | stream/services.py; stream/admin.py; .local/autopilot/; .local/qa/; .claude/tools/; training/; docs/playbook.gates.json; docs/playbook.rules.json; section7 exact paths |
| Acceptance/publication | docs/TEST.md and relevant acceptance plans; docs/PUBLISHING.md, after resolving D04 against latest decisions. Follow current authorization before execution |

### Repair order

1. **Truth:** B01, D01–D05. Current source/build/stage baseline, current owner decisions and accurate handoff/queue.
2. **Value/custody:** E01/E02/E10/E11, RT-35/38/39. Duplicate issuance, destructive refused payment, evidence/provider/save loss.
3. **Travel/recovery:** P01/P02/P05/P08–P10/P13/P16, RT-36–39. Exact endpoints and attempt ownership.
4. **Campaign loop:** E03–E05/E09, P03/P04/P06/P07/P15. Provenance, field equipment, free-travel evidence and bounded population.
5. **Native work/protocol:** P11/P12/P14/P17–P20, A01–A06, RT-11. Treat client/mod command fixes together.
6. **Requests/economy/UI:** E06–E08/E12/E13, G01/G02/G06.
7. **Local control:** RT-01–25, especially owner grant/GO/time/cursor/process/message/voice recovery.
8. **Training:** RT-26–34, reproducible inputs/outputs, interruption/checksum/application.
9. **Completion:** G03–G08, D06–D08, full backlog, presentation, optional integrations and authorized acceptance/release.

For each bounded change record baseline, affected callers, saved IDs/fields, providers/fallbacks, preserved behavior, migration/recovery, changed paths/evidence and remaining acceptance. Avoid broad rewrites that discard existing features.

### Future acceptance cases, proposed only

- Repeated paused withdrawals/receipt replay; refused payment leaves exact goods/custody unchanged.
- Generated provenance/journals/occupants and in-flight portal/provider cargo across reload.
- Two gates/remembered vsactive addresses; source-map release with outgoing edges.
- Failed inside start/first exit retry without duplicate surface claims.
- NPC permissions/cutoff ordering; needs/material/work through natural/multi-hop routes.
- Mixed-value recipes; actionable cell/bill beyond each scan prefix; partial-energy interruption and marked-stack splitting.
- Same-family requests/derived routes/old quotes/protected furniture/evidence.
- More than 32/concurrent automation commands/escaped labels/wrong-map pawns.
- GO restart/mid-turn orders/unauthorized restart/owner cursor/bridge EOF/service duplication.
- Failed training fetch/interruption/old markers/checksum/apply failure.
- Long campaigns, DLC/provider cases and RWT independent-client custom custody transfer.

None was executed or newly authorized by this audit.

## 12. Review coverage and delivery

Lead inspection covered context, current package/build/stage tools, metadata/assets, Automation/Core/Presentation/Audio/Incidents and document/repository consistency.

Connected reviewer plus company follow-up covered executable bodies of all 143 Gate/Portals/ConnectedWork/Generation/Threats/Scenario/Expedition files, approximately 44,546 lines. Many comments were filtered. Company review inventoried 109 Company/Economy/Investigation/Personnel/Procurement/Facilities/UI/Expedition files, approximately 23,900 lines, then completed identified records/hiring/relief/clear-squad/legacy-closure gaps. These scope totals overlap; do not add them as unique counts.

Runtime reviewer inspected first-party service/stream/player/training/installer paths and selectively traced installed Stargates/Core inspection source. Historical proofs/corpora/vendor content were inventoried/sampled, not all executed or line-reviewed.

All 263 first-party mod C# files were inventoried; executable source review focused on money/custody, persistence, endpoint eligibility, jobs/materials, failure recovery and owner control. Not every comment, historical document or large corpus received equal scrutiny.

**This completes the requested inspection deliverable. It does not rectify the issues or declare the full mod/rig finished.** Coding agent: use stable IDs/paths, recheck current source, select repairs, and defer to latest owner decisions over obsolete guide text.

