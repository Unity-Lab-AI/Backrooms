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

## Rules for the next implementation

1. Keep stable class/Def/Scribe/record identifiers. Separate package, schema and generator versions. Record first introduction and required migrations alongside each field.
2. Implement explicit, ordered migrations before changing stored meanings. A migration checks its source version, runs once, preserves branch/coordinate/transaction identities, and advances version only after a complete result. Never infer “new game” from a missing field in an old save.
3. Scenario activation is a deliberate one-time initializer, with a recorded scenario ID and transaction/initialization receipt. Constructors, load hooks and UI drawing never award starter stock or cash.
4. Validate collections, owner references and old optional-mod records after loading. Missing optional content produces a visible recovery route; never silently delete cargo, evidence, research or transfer receipts.
5. Future unsupported versions remain read-only at the campaign layer and receive a clear warning against re-saving. Before supporting cross-version loads, inspect the full save lifecycle and implement a reliable refusal/recovery path. A warning alone is not preservation of unknown fields.
6. Retain pre-migration backups and record source/destination package and schema versions. Owner-launched cases cover new start, existing non-Rimrooms save, same-version reload, repeat reload, each supported migration, interrupted/invalid records and removed optional dependencies.

The [state dictionary](CAMPAIGN_STATE_DICTIONARY.md) owns full campaign fields and transfer rules; the [procedural contract](PROCEDURAL_SPACE_CONTRACT.md) owns coordinate/generator persistence. Those planned records are not implemented by the three foundation fields above.
