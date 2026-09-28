# Phase 2: final bounded source findings

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Reviewed 2026-09-28.** Read-only review of Generation, Audio/settings, root Operations clue/salvage/report routes, and gate/threat cue call sites. Features: RR-SPACE, RR-EXP, RR-EVD, RR-GATE, RR-THREAT, RR-STYLE, RR-UI. No code fixes, tests, build, game launch or audio playback were performed by this reviewer. In-progress failed-site recovery work and its possible planner wrapper are excluded; this is not their final review.

Sources remain pinned Core row 4, `Ludeon.RimWorld`, assembly SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`, local ILSpy 9.1.0.7988. Read the [destination implementation](PHASE_2_DESTINATION_IMPLEMENTATION.md), [audio source review](PHASE_2_AUDIO_SOURCE_REVIEW.md), [audio implementation](PHASE_2_AUDIO_IMPLEMENTATION.md), [procedural discovery contract](../PROCEDURAL_SPACE_CONTRACT.md#discovery-and-fog-of-war), and [first threat sheets](../THREAT_DESIGN_SHEETS.md).

## Finding resolved during review

**Fogged recording exposed by Operations.** The recording is registered before initial entry, but its Locate button and expedition Recover Evidence list originally checked only the actual Thing's presence. They could expose its position/action before Office Copy discovery, unlike the guarded clue/salvage controls. The lead added actual `Position.Fogged(Map)` checks to both routes. Follow-up source reads confirmed the guards in [MainTabWindow_Operations.cs](../../src/RimroomsAsyncIndustries/UI/MainTabWindow_Operations.cs) and [OperationsExpeditions.cs](../../src/RimroomsAsyncIndustries/UI/OperationsExpeditions.cs). **Resolved in source; engine behavior remains unverified.**

## Clarification, not a defect

The initial concern that the displaced survey tag must physically return to its old junction was withdrawn after comparing the exact RR-D-001 contract. Counterplay explicitly compares the displaced numbered tag and places the beacon at the known junction. Requiring the tag itself back there would add an unapproved restriction. The current distinction between the beacon's actual junction and the tag's recorded junction is intentional; this review makes no additional counterplay requirement.

## No further concrete mismatch found in this scope

| Area | Source evidence and limit |
| --- | --- |
| Floor and layout | Current content uses the original `RR_FadedInstitutionalCarpet` with native paved/metal accents. Props avoid the reserved route cross, anchor and objective cells. Placed room and landmark-adjacency route checks fail closed before entry. Current template geometry remains bounded; no source-provable corridor obstruction was identified. |
| Roof support | Steel perimeter walls, native roof-holding doors and center support walls bound the room roofs; corridors have side walls. Native `RoofCollapseCellsFinder` bases collapse on roof-holder range/connectivity. No missing-support defect was identified in these authored footprints; actual collapse behavior after damage remains runtime work. |
| Doors and fog | Closed native doors plus threshold-only fog roots preserve discovery; the native hold-open command does not forcibly open doors. Route checks explicitly admit native accessible doors. Optional mods can replace native behavior, which remains a stated runtime limitation. |
| Physical salvage | The Operations button requires an observed clue and an actual unfogged item on the worker's map. `ExpeditionCargo.QueuePickup` applies native capacity/reservation/reach checks, queues `TakeInventory`, and adds carried-item mass to its preflight. Native TakeInventory rechecks encumbrance, target presence and forbiddance during the job. No copy, virtual credit or teleport is introduced by this route. |
| Clue labels | Map labels require a spawned physical landmark on that map and an unfogged position. Atlas uses saved observed clues. Missing/moved-off-map objects stop map labels while the historical clue remains available. The corresponding eight label/text pairs exist in English keyed XML. |
| Evidence report UI | Report display uses the saved analysis snapshot when present, handles explicitly unavailable legacy details, and otherwise shows current field observations. The viewed paths do not mutate rewards or analysis state. |
| Audio view and failure | Helper requires main thread, playing state, live/current map, map view and valid cell. Settings/Def/clip problems skip playback; presentation exceptions cannot escape through the helper. Native game/master volume remains intact and warning storage is bounded to eight keys. |
| Cue call sites | Gate cues follow actual opening/emergency/warning transitions; warning flags are saved. Threat cues follow persisted events and select an actual field crew position. These custom cue events use SilentInput messages to avoid the normal accompanying neutral-event sound. No cue call was found in save exposure or GUI drawing. |
| Pursuit route | Lead's start logic waits for a valid two-graph-room position with a real no-closed-door route to live crew, retrying later if unavailable. This avoids the earlier unopened-room immediate-withdrawal path. Full encounter timing/fairness remains owner-launched acceptance. |

These are bounded source conclusions, not proof that every possible modified Def, damaged map or optional integration works.

## Asset and XML references observed

- All four SoundDefs point to their matching extensionless `Rimrooms/RR_*` names. The four shipped WAV hashes were read and **match** [phase2-original-audio.json](assets/phase2-original-audio.json): `RR_GatePowerRise`, `RR_GateWarning`, `RR_FieldRadio`, `RR_SpatialTell`. This confirms file/manifest correspondence, not audio playback or mix quality.
- `RR_FadedInstitutionalCarpet` resolves by declared path to the present packaged PNG. Its SHA-256 is `77D0F53A0A12AD1947180A72067253ED73A0079DD7C87134AFFE00BCC82B0ED6`, matching [phase2-interior-art.json](assets/phase2-interior-art.json).
- Fixture XML points to the present original fluorescent sprite and the existing original gate-console sprite reused for the climate fixture; their entries are in [phase2-original-art.json](assets/phase2-original-art.json). This source pass did not perform a new visual inspection.
- The six settings text keys are present in `RR_Audio.xml`; new generation/clue text is present in `RR_Generation.xml`. No missing referenced key or file was identified in the reviewed additions.

Local observations came from reads/searches and file hashes only. Extra roof inspection is ignored at `.local/inspection-generation-final/Verse.RoofCollapseCellsFinder.decompiled.cs`; existing audio/generation/job inspections remain in their documented ignored directories. The lead owns the integrated compilation and subsequent source changes. Gate 2, runtime acceptance and full-profile/co-op compatibility remain pending.
