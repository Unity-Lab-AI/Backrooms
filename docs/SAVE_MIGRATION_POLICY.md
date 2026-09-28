# Save schema and migration policy

## Foundation schema 1

The concrete class `RimroomsAsyncIndustries.Company.RimroomsCampaignComponent` is attached by Core's normal GameComponent discovery. Its public `(Game)` constructor is inert. [Source review](implementation/PHASE_1_CORE_SOURCE_REVIEW.md) confirms creation for ordinary new games and the missing-component path during loading. Runtime acceptance remains pending.

| Persisted key | Type / initial value | Meaning |
| --- | --- | --- |
| `rr_schemaVersion` | integer / 1, always serialized | Format version, independent of the package version |
| `rr_branchId` | string / null | No company has been started when absent |
| `rr_scenarioId` | string / null | No Rimrooms scenario has been initialized when absent |

Foundation 0.1.0 has no scenario initializer and cannot create a branch. It grants no money/items/research and does not alter the player's scenario. The UI reads the current game's component each draw. It shows an unavailable message for an unsupported schema; no campaign mutations exist in this build.

**Do not open and re-save a newer Rimrooms save in an older build.** The status message is not a whole-save forward-compatibility mechanism: unknown future fields cannot be preserved by a serializer that does not know them. Keep the original save and use the matching/newer supported build. No migration, mod-removal safety or downgrade guarantee has been demonstrated for 0.1.0. Use disposable saves for owner-launched acceptance.

## Development 0.2.0 saved state

The [current build record](implementation/PHASE_2_BUILD_RECORD.md) links actual source. These migrations are implemented source, with owner-launched load/reload acceptance pending.

| Owner | Version and persisted state | Missing / interrupted behavior |
| --- | --- | --- |
| `RimroomsCampaignComponent` | Schema 2. `rr_schemaVersion`, branch/scenario/version/seed, initialization receipt, HQ reference, funding/balance, daily costs and next due tick, insight count; deep lists for ledger, staff, obligations, contracts, coordinates, cases, evidence, projects and recent events | Historical schema 1 advances to 2 without granting funds, staff, items, projects or an active branch. Unsupported schema disables company actions. Duplicate IDs, invalid ledger totals, negative amounts, nonfinite work and broken logical relationships disable mutations with a visible integrity message. Lost physical references remain recovery cases. |
| `HeadquartersSetupComponent` | Scenario/start-def receipt, completed physical setup, native staff references/roles, branch initialization receipt and failure | Retrying company registration uses the existing physical setup; it cannot rerun the physical grants. |
| `CompRimroomsGate` | Assembly/calibration, assigned operator, calibration work, stored reserve, opening/failure timers, active/latest-closed expedition IDs, recovery/time-cost receipts and warning flags | Power/operator loss moves to a bounded emergency window. Stranding closes the active opening but preserves its latest ID for a paid reopening. Repeated operation IDs cannot refill time or spend costs twice. |
| Coordinate and destination parent | Stable coordinate ID/seed, generator/room-library version, saved room graph and survey flags, map reference, fingerprint, completed-layout receipt, entry/return/evidence cells and anchor | Previously opened maps are reused; missing/invalid saved sites refuse, retaining records. They are never silently replaced. Generator format changes need an explicit version/migration. |
| `RimroomsExpeditionComponent` | Schema 2. Monotonic expedition IDs, original crew, live returns, relief/recovered passengers, maps/gate/thresholds, phase/ticks, recovery attempt IDs, cargo manifests, closure history; transfer journals plus deep-held interrupted pawn owner | Schema 1 keeps all records and appends old cargo declarations as unverified historical entries needing review. Abandoned journals remain saved and recover only to their original source; only explicitly abandoned journals cease blocking unrelated new dispatch. Orphaned/active transfers still block. |
| Evidence/project records and physical comps | Evidence/item/case/coordinate IDs, observations, source expedition, analyst, work and completion tick; project ID, Def, committed insight receipt, work and completion; physical recording comp ID | Missing evidence is never reminted. Completed analysis remains completed after later item loss. The physical case is rechecked during work. Separate payment/bonus receipts allow a later crew rescue without paying the base reward twice. |
| `FirstSliceSiteComponent`, route-aid comps | Expedition ID, individual previous rooms, marker numbers and recorded coordinate/room, mismatch, warning tick/target, approach/strike counters, pending time-cost receipt, native crew/entity references, deep-held deployment recovery items | Same-expedition reopening preserves encounter limits. New expedition resets bounded encounters while visited-room records and physical site changes persist. Picked-up tags lose deployment metadata; distortion relocation preserves it. |

Stable source fields and Scribe keys are discoverable in the linked source folders. Enum additions append values; existing values are not renumbered. UI selection/scroll/dialog text are transient and never authoritative. `GameComponentTick` applies simulation work; drawing does not grant money or insights. Explicit buttons call services that recheck state.

Keep a pre-upgrade save. No downgrade, removal, corruption-repair, modded pawn transfer or migration compatibility claim follows from compilation. Native object references and deep holders still require interrupted-transfer and save/reload evidence.

### Explicit first-survey replacement

The [initial generation recovery](implementation/PHASE_2_GENERATION_RECOVERY.md) uses a stable child coordinate ID (`<failed ID>:fallback:1`) as its receipt. It preserves the failed parent/map, creates a separately owned preflighted graph, and rebinds only the untouched initial case and unpaid contract. No schema change or resave-time grant is involved. Repeat calls require the same graph and links. Any prior survey, evidence, pawn, corpse or linked expedition/transfer prevents replacement; missing content and unknown failures require source/package diagnosis. No third retained destination is allowed in this slice. A save/reload result for this path remains pending.

## Rules for subsequent implementation

1. Keep stable class/Def/Scribe/record identifiers. Separate package, schema and generator versions. Record first introduction and required migrations alongside each field.
2. Implement explicit, ordered migrations before changing stored meanings. A migration checks its source version, runs once, preserves branch/coordinate/transaction identities, and advances version only after a complete result. Never infer “new game” from a missing field in an old save.
3. Scenario activation is a deliberate one-time initializer, with a recorded scenario ID and transaction/initialization receipt. Constructors, load hooks and UI drawing never award starter stock or cash.
4. Validate collections, owner references and old optional-mod records after loading. Missing optional content produces a visible recovery route; never silently delete cargo, evidence, research or transfer receipts.
5. Future unsupported versions remain read-only at the campaign layer and receive a clear warning against re-saving. Before supporting cross-version loads, inspect the full save lifecycle and implement a reliable refusal/recovery path. A warning alone is not preservation of unknown fields.
6. Retain pre-migration backups and record source/destination package and schema versions. Owner-launched cases cover new start, existing non-Rimrooms save, same-version reload, repeat reload, each supported migration, interrupted/invalid records and removed optional dependencies.

The [state dictionary](CAMPAIGN_STATE_DICTIONARY.md) owns full campaign fields and transfer rules; the [procedural contract](PROCEDURAL_SPACE_CONTRACT.md) owns coordinate/generator persistence. The current build implements the subset above. Later hiring, training, shipments, lease/outpost, expanded research and co-op records remain planned until their own source and migration evidence exists.
