# Phase 2: company records and accounting source review

**Date:** 2026-09-28. **Scope:** Core row 4, `Ludeon.RimWorld`, same Assembly-CSharp SHA-256 as the [vertical-slice task](PHASE_2_VERTICAL_SLICE_TASK.md). No game was launched. The [foundation lifecycle review](PHASE_1_CORE_SOURCE_REVIEW.md) still controls component construction and bootstrap.

## Inspected source

ILSpy 9.1.0.7988 inspected `Verse.Scribe_Collections`, `Verse.Scribe_References`, `Verse.Scribe_Values`, `Verse.Scribe_Defs`, `Verse.GameComponent`, `RimWorld.GenDate`, `Verse.TickManager` and `Verse.CameraJumper`. Private decompiled text is held only in ignored `.local/inspection-company/`; no Core method body is redistributed.

- `Scribe_Collections.Look<T>(ref List<T>, string, LookMode, params object[])` supports explicit `LookMode.Deep` for company-owned records and `LookMode.Value` for scalar lists. Deep records implement `IExposable`; their physical pawn/item/map references use reference serialization.
- `Scribe_References.Look<T>(ref T, string, bool saveDestroyedThings = false)` requires `ILoadReferenceable`. It writes load IDs, registers XML IDs during `LoadingVars`, and resolves objects during `ResolvingCrossRefs`. Default behavior clears references to destroyed things; retain separate stable load-ID/history fields for missing people/items. It does not clone physical things.
- `PostLoadInit` follows reference resolution. Normalize new optional collections and rebuild derived lookup caches there. Do not assign branch funds or physical stock during loading.
- `Scribe_Values.Look<T>` accepts scalar long/int/bool/string/enum values; explicit defaults preserve historical meanings. Schema 1 is the historical fallback, while every saved schema version remains forced into XML.
- `RimWorld.GenDate.TicksPerDay` is 60,000 and `TicksPerHour` is 2,500. TickManager's normal-speed interval is 1/60 second. Thus the earlier 20 **game-minute** window is roughly 833 ticks / 14 real seconds; the lead asked the owner to clarify this before selecting a changed expedition duration. Pause stops game ticks.
- `CameraJumper.TryJumpAndSelect(GlobalTargetInfo, MovementMode)` and `TryJump(IntVec3, Map, MovementMode)` provide the native navigation route. They are used to inspect staff and headquarters, not to move those pawns between maps.
- Drawing `Widgets.ButtonText` directly exposes the `UnityEngine.TextRenderingModule` `TextAnchor` type. The compiler reported this missing reference; adding that local assembly with `Private=false` resolved it. It is recorded with other references and is not packaged.

## Implemented ownership and guarantees from code inspection

The company component accepts a complete `BranchStartRequest` after physical scenario setup. It validates staff/map identity and quoted amounts, builds records, then commits one branch/init receipt. It does not create pawns, silver or equipment. Branch identity is random once and persisted; the first coordinate's saved seed is derived deterministically from the campaign seed, stable coordinate ordinal and generator version using an explicit hash algorithm.

USD uses whole-dollar `long` values and checked arithmetic. The single ledger posting method requires a unique operation key; replay with the same amount/reason/owner returns the existing result, while reuse with a different payload refuses. Negative available balance is refused. Payroll/overhead first create saved obligations; an unaffordable payment remains visibly unpaid, rather than pretending staff were paid or silently minting cash. Daily processing is bounded to four catch-up days per scheduled update. The initial target is five $5,000 daily wages plus $25,000 overhead; food remains physical stock with no automatic meal debit.

Schema 2 adds actual branch/staff/ledger/obligation/coordinate/case/evidence/contract/project records. Migration from schema 1 keeps old scalar IDs and leaves foundation/ordinary saves inactive; it does not start a company. A ledger sequence mismatch, duplicate operation/record ID or invalid record disables company actions and preserves the data for diagnosis. Recent activity is capped at 256 entries; authoritative ledger, obligations, cases and contracts are not truncated by that display cap.

The Operations panes are views of these owners and call services for payment. They do not award money or initialize branches. All visible company text is keyed English. UI map/pawn navigation remains native.

## Remaining proof

Successful compilation establishes signatures and references only. Owner-launched cases must cover actual new-game registration, missing references, same-version save/load, schema-1 migration, repeat initialization/payment, insufficient funds, daily charges, long saves, multi-map navigation, UI scale and profile interactions. The scenario, gate and destination assignments have their own source records; no co-op transfer or compatibility claim follows from these accounting classes.
