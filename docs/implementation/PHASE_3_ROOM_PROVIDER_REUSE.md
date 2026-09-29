# Native room provider replacement: review handoff

**Status: planned, unimplemented.** The 0.3.1 checkpoint changes no Generation source. The lead froze this assignment before source editing so the complete current project batch could be published together. Continue implementation under [the scoped task](PHASE_3_SCENARIO_GATE_REUSE_TASK.md), [content policy](../CONTENT_REUSE_POLICY.md) and [regression containment](../REGRESSION_CONTAINMENT.md).

## Candidate route and required source confirmation

The assigned source reviewer reported a Core-only candidate: `ChemfuelPoweredGenerator` with real initial Chemfuel, existing `StandingLamp`, `Heater` and `HiddenConduit`. Its reviewed nominal budget was a 1,000 W generator, nine 30 W lamps and one 175 W heater (445 W maximum named demand), with 30 actual Chemfuel initially supplied. Treat those values as review findings to confirm against loaded Defs when implementing, not observed operating performance. Fuel depletion must have native consequences and cannot be replaced with an unlimited virtual supply.

The reviewer identified spawn ordering as material: `CompPowerTrader.PostSpawnSetup` can leave a consumer off when its native network does not exist yet. Establish the native network in the proper generation order and preserve native power/flick behavior; do not force `PowerOn` or invent a second electrical store. Verify footprint availability, native fuel API and network rebuilding from the pinned Core source before writing the implementation.

## Owned changes for the next milestone

- `Generation/GenStep_BackroomsDestination.cs`: replace newly generated custom lighting/climate with actual Core providers and physical power. Keep corridors, clear routes, fog, evidence cells, return anchor and graph identity intact.
- `Generation/FailedSiteRecovery.cs`: update readiness/allowed original objects for the native providers while retaining old-map recognition. Never replace an occupied, modified or evidence-bearing site.
- `Generation/RoomContentBuilder.cs`: planned content version 3 for the new provider arrangement. Existing generated version-2 maps must remain unchanged. Explicitly account for saved but ungenerated graphs before introducing a version check.
- New-layout-only floor normalization to actual Core `PavedTile` is a candidate for the custom carpet. Confirm the provider and preserve path/floor semantics; do not repaint existing saved maps. Retain legacy Def resolution until a separately documented migration/removal boundary is implemented.

Do not clear/rebuild a saved site merely to obtain the new look. Existing furniture, salvage, evidence custody and reward receipts survive revisits. Construction source, compilation and owner-launched visual/power/save checks are separate evidence. The room replacement and its master TODO remain open; this handoff does not claim implementation or runtime compatibility.
