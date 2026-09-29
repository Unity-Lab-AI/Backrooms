# Changelog

## 0.4.2-dev — 2026-09-28 — remembered portal addresses and ordinary crossing

- Added explicit portal addresses: a designated native gate can remember a laboratory connection to a saved coordinate, and any actual doorway can hold a permanently open natural connection. Addresses are derived from the branch, coordinate and threshold object, so remembering the same address twice changes nothing.
- Added an explicit repair for sites generated before their return threshold was an actual door. It replaces that one object with a Core door under a saved receipt and keeps the site's map, room graph, construction, recovered items and discoveries.
- Added a deterministic record for newly discovered coordinates so an address can never invent a coordinate identity or seed. Visited coordinates are never removed to make room.
- Added ordinary crossing: order one colonist and they walk to the saved threshold and cross carrying what they already carry. No crew list, manifest or dispatch. Opening a doorway normally still moves nobody.
- Added laboratory session controls, a reconcile action for every unresolved crossing, and an emergency-return route that pays the physical recovery cost once and teleports nobody.
- Added player-facing text for every portal address, travel and crossing result.

Source and compiler evidence is in the [connected-travel record](docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md). Cross-map work, materials, hauling, bills, research and needs are not implemented by this version; they remain the next steps in the [deferment register](docs/DEFERRED.md). No gameplay, save-migration or compatibility result is claimed.

## 0.3.0-dev — 2026-09-28 — company operations and content reuse

- Added voluntary native-pawn applicants, inspection, hiring, recovery, staff role assignments and payroll registration. Offers retain the original pawn through interrupted arrivals; unavailable offers have an explicit safe dismissal route.
- Added quoted procurement of existing Core goods, saved physical cargo, ledger-backed payment/refund records, receiving stockpiles, partial deliveries, redirection and bounded history.
- Added an HQ Facilities pane for actual buildings, rooms, power, bed ownership and staff care needs, with native inspection and assignment routes.
- Moved company laboratory work to an explicitly designated native research bench. New field evidence uses a real Core TextBook, with saved creation/custody records and retry of the same original object.
- Replaced the four custom gameplay audio files with references to existing Core sounds. Preserved old files outside the loadable package as historical evidence.
- Added two original painted Backrooms menu images, a quiet slideshow, reduced-motion/disable settings and the exact mod title/current build version beside native top-left version information.
- Recorded the owner's existing-content-only rule throughout the build documents and mapped the remaining older custom content for replacement.

This is an implementation checkpoint toward the full mod TODO. The [company build record](docs/implementation/PHASE_3_BUILD_RECORD.md) owns compiler/package evidence and limitations. Custom gameplay content from 0.2.0 still awaits replacement; gameplay, balance, save migration, optional integrations and release acceptance remain open.

## 0.2.0 — 2026-09-28 — first-expedition development slice

- Added the Async Industries facility start, five staff, physical supplies and one-time branch funding.
- Added the USD ledger, wages/overhead, arrears, initial survey contract, case/evidence records and company projects.
- Added physical machine assembly, staffed calibration/operation, power reserve, warnings and recovery openings.
- Added a saved finite first destination, real inventory/crew transfer, recall, relief/casualty recovery, abandonment history and auditable cargo declarations.
- Added deployable numbered tags/beacon, corridor mismatch, bounded Quiet Pursuer, physical evidence analysis, once-only settlement and insight-gated Gate Telemetry.
- Added actionable Operations panes, next objectives and original equipment/encounter sprites with provenance and source masters.
- Added bounded layout candidates/fallback, furnished room families, fog-preserving native doors, observed clues, physical salvage, original carpet and native wall paint.
- Added frozen evidence reports, explicit AI-01 resurvey preparation, persistent gate warnings and development identity/performance logging.
- Added four original quiet audio cues with native game/master volume, independent gate/field mute and a mod volume control.

The [build record](docs/implementation/PHASE_2_BUILD_RECORD.md) records exact implementation, source and evidence boundaries. Gate 2, runtime/presentation acceptance, full campaign systems, optional integrations, co-op and release remain in progress. This is a private development checkpoint.

## 0.1.0 — 2026-09-28 — private foundation

- Added the Core-referenced C# library, logging entry point and inactive save-local campaign component with explicit schema version.
- Added the localized Operations main tab, with foundation status and guarded links to native Work and Research tabs.
- Added exact mod identity, original package preview and the separate copyable 1.6 package.
- Added pinned build references, locked dependency restore, package manifests and scoped RimSort Local Mods staging with backups.
- Added contributor/build/migration guidance, production asset specifications and implementation evidence linked to the existing design contracts.

The company scenario, economy, machine gate, expeditions, generation, analysis, threats, main-menu slideshow and optional integrations are not implemented in this version. Compilation and package/staging evidence do not establish in-game behavior or profile compatibility. No public release or save-support promise is made.

## Preparation — 2026-09-28

Gate 0 documentation/source preparation completed, including owner decisions, 294-mod source review, design contracts, feature traceability, source registers and future acceptance plans. See the [closure audit](docs/research/GATE_0_COMPLETION_AUDIT.md).
