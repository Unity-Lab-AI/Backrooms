# Technical architecture proposal

**Latest owner requirement — connected colony portals (2026-09-28):** [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, materials, portal lifetime, coordinate persistence and procedural inhabitants. Open portals unify local-branch labor and physical job/material access across both sides; ordinary crossing must not require expedition dispatch. Natural portals remain permanently open. Existing dispatch-only descriptions below are superseded where they conflict. The current source does not yet implement this unified work network.


**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


Most of this document is the full-campaign design target. The [0.3.0-dev company wave](implementation/PHASE_3_BUILD_RECORD.md) adds independent schema-1 personnel, procurement, laboratory-binding and evidence-creation owners, all linked to the existing branch; the campaign component remains the only USD/payroll owner. Facilities are transient observations, and the menu owns settings/presentation only. The [0.2.0 build record](implementation/PHASE_2_BUILD_RECORD.md) maps the implemented company/scenario/gate/destination/expedition/investigation/threat/UI subset and its source reviews. [BUILDING.md](BUILDING.md) records the compiler/reference/package setup; [SAVE_MIGRATION_POLICY.md](SAVE_MIGRATION_POLICY.md) records actual saved owners. First-slice company research uses a custom insight-gated `RimroomsProjectDef` with native Research work, preserving Core research. Expedition transfer moves the same native objects and journals interruptions. Other proposed types and optional integrations still require their own source review and implementation.

**Gate 0 decisions recorded:** private RWT prototype first; exact displayed title `Rimrooms - Async Industries`; author/publisher value `Operator`; package ID `UnityLabAI.RimroomsAsyncIndustries`; internal namespace `RimroomsAsyncIndustries`; semantic versions; Core-only solo path; optional support for all five DLC; other 294-profile mods optional; indirect adaptation of Kane Pixels/A24 references, with wider community canon excluded from shipped content; dossier transfer plus shared research ledger only if supported and safely tested; English-first localization-ready; MIT for original source code; and supplemental S1/B, which freezes broad later threat families and defers named sketches. Gate 0 documentation/source preparation passed; the foundation compile/staging evidence is linked above, while all in-game/runtime checks remain pending.

**Native door/network work:** use [SCENARIO_SETUP_AND_PORTAL_NETWORK.md](SCENARIO_SETUP_AND_PORTAL_NETWORK.md) for setup-page compatibility, preserved customized pawn instances, saved door/endpoint/provider bindings, physical electrical connections, explicit control links, duration/aperture upgrades and deterministic map recall. This implementation replaces the historical custom gate owners through an explicit migration boundary.

## Runtime and package boundaries

- Target RimWorld **1.6** and its Core APIs first.
- Keep Royalty, Ideology, Biotech, Anomaly, and Odyssey as optional conditional integrations; the Core campaign remains complete.
- Use the exact 294-entry profile as the full research/test target. Require only Core plus Harmony/RWT for the co-op path; all other profile mods remain optional.
- Ship one main mod package initially. Keep content and code organized so future optional extension packages can be split out without changing saved identifiers.
- Keep repository source under `src/` and make `Mod/Rimrooms - Async Industries/` the only loadable, copyable package root. Documentation, research, workbook, source files, build utilities, and evidence stay outside this folder; the packaging/staging script must copy only this root to RimSort's configured Local Mods directory.
- The product target is the existing 294 entries plus Rimrooms (295). RimSort owns the load order and profile; the owner launches each session through RimSort. RimBridgeServer is a separate QA overlay, normally making the attached test profile 296 entries; it does not replace any target mod. GABS must not start or rewrite this project's test profile.
- Reference existing building/item/pawn/terrain/sound definitions. Rimrooms may define role bindings, policy/configuration, jobs, recipes using existing products, research, quests, incidents, world objects and language strings. Use C# for company state, generation, integration and UI. Do not introduce cloned or custom physical item/bench definitions to bypass the reuse rule.

## Source and package layout

```text
Backrooms/
  docs/                              research and design; not packaged
  outputs/                           planning workbooks; not packaged
  src/RimroomsAsyncIndustries.sln    source project; not packaged
    Core/ Company/ Gate/ Expedition/ Generation/ Investigation/
    Personnel/ Procurement/ Facilities/ Presentation/ UI/
    Compatibility/RimWorldTogether/
  tools/                             build and Rimsort staging scripts; not packaged
  Mod/
    Rimrooms - Async Industries/     only copyable/loadable mod package
      About/About.xml
      LoadFolders.xml
      1.6/Assemblies/                 built RimroomsAsyncIndustries.dll
      1.6/Defs/                       buildings, items, work, research, quests, maps
      1.6/Languages/English/Keyed/
      1.6/Patches/                    narrow, package-guarded patches
      1.6/Textures/  1.6/Sounds/     no new gameplay assets; historical files awaiting replacement
```

The identity, load folders, MainButtonDef and English localization now exist in the foundation package. The other feature folders in this target layout are created only with implemented content. `About/About.xml` uses the accepted title/package ID and `Operator`. Keep C# source outside the package; copy only Rimrooms build/definition/text output and any separately approved presentation output into the package root; existing provider assets stay with their provider. Use [BUILDING.md](BUILDING.md), the [RimSort package/launch plan](research/RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md) and [RimBridgeServer harness](research/RIMBRIDGE_TEST_HARNESS.md) for staging and post-build checks.

## State ownership and persistence

Keep each value in one authoritative owner and serialize it through RimWorld's save system. The full campaign record list, branch boundaries, stable IDs, idempotency rules, and recovery expectations are in the [campaign state dictionary](CAMPAIGN_STATE_DICTIONARY.md). Those rules describe the data contract; the component types below remain API candidates.

- **Campaign/company state:** funds/ledger, research clues, unlocked coordinates, open contracts, company reputation, and global progression. Candidate: one campaign `GameComponent`.
- **World state:** coordinate records, discovered routes, outposts, signal sources, and active distortion incidents. Candidate: one `WorldComponent` plus normal `WorldObject` instances.
- **Map state:** local expedition flags, active gate/relay information, room graph identifiers, exploration data not already represented by vanilla fog-of-war, and map-local event stages. Candidate: `MapComponent` or dedicated saved world objects.
- **Building state:** gate condition, configuration, calibration, and local job status. Candidate: a gate `ThingComp` with stable references rather than duplicated global fields.
- **Pawn state:** training credentials, expedition history, exposure or case metadata. Use pawn components only for state that belongs to that pawn and survives travel.

Persist numeric IDs, stable seeds, Def references, and explicit stage values. Avoid saving direct references to temporary UI objects or relying on list order to identify a room, site, or crew.

## Destination and map generation model

Represent a destination as a stable company coordinate with a deterministic generation seed and a normal RimWorld world object that can own a saved local map. The world object should record its room graph seed, generator version, visit count, first-seen state, known exits, and return equipment. Returning to a destination loads its previous save; a deliberate anomaly modifier may alter only documented state. The full player-facing generation, discovery, propagation, recovery, and migration contract is in [PROCEDURAL_SPACE_CONTRACT.md](PROCEDURAL_SPACE_CONTRACT.md).

Generate a local map in stages:

1. Select a room-graph recipe from the coordinate seed and mission constraints.
2. Place room/corridor templates from tagged definitions.
3. Validate that doors, paths, exits, and required workspaces are reachable.
4. Apply a small set of seeded spatial modifiers.
5. Place evidence, equipment, hazards, and entity events.
6. Register the map to its coordinate and save through normal world/map persistence.

The engine should generate only maps that the player visits. Infinite expansion is a stable generator plus coordinates and continued discovery, not a single gigantic map. Add a generator version to records so later releases can preserve old destinations or intentionally migrate them.

RimWorld 1.6's official [Modder Primer](https://docs.google.com/document/d/e/2PACX-1vRKE9u5ZW_zG45pxzwNvy4sxvozDeqtxlxpac5jwenOeW6liQCPgmPl9bIbtcMuqL1NPIDHOLFg64M_/pub) documents room layouts, room parts, prefabs, and map-generation stages that may support reusable generated rooms. Treat these as candidate building blocks only: exact type names, signatures, placement constraints, persistence behavior, and deterministic replay still need a small prototype against the pinned assemblies after Gate 0. See [RimWorld 1.6 package and generation findings](research/RIMWORLD_1_6_PACKAGE_AND_GENERATION.md) for the research path.

## Gate and expedition simulation

The gate is a normal buildable `Thing` with a component that reads power, machine condition, operator readiness, and installed modules. One transition system should own its states, for example: unbuilt, assembly, calibration, ready, opening, open, unstable, recall, cooldown, and damaged. All timers should use game ticks and deterministic inputs.

An expedition owns an explicit crew list, destination ID, opening tick, close/recall criteria, cargo rules, and event state. Avoid creating hidden parallel copies of pawn ownership, inventory, or quest progress already represented by vanilla objects. A hard time limit should trigger clear warning stages and a player-facing recall decision before catastrophic failure.

## Company UI

Begin with one compact Operations window and inspectable objects (gate, console, lab, contracts) that open focused dialogs. Use the [Operations action contracts](OPERATIONS_ACTION_CONTRACTS.md) for every pane's preconditions, success result, refusal state, recovery route, and owner. UI actions that change funds, assign crews, consume stock, create sites, or advance a project mutate and save the owning branch's state. Cross-branch transfer actions must route through the RWT adapter and record a transfer receipt; RWT does not make every local action a shared-state mutation. Read-only panels can stay local.

Store state independently from the screen implementation. That makes the company board replaceable without migrating every campaign record. Use keyed translations from the first content pass; avoid hard-coded visible English in C#.

## RimWorld Together requirements

The local profile confirms workshop ID `3005289691` (`RimWorld Together`) and a dedicated server package. The client and server currently have the same 294 mapped mod IDs in the same order, but the server config does not enforce that profile. The local Windows server archive and installed `RTClient.dll`, `RTNetwork.dll`, and `RTShared.dll` match the official RWT 26.8.31.1 release assets by SHA-256/byte comparison. See the [local RWT and gravship audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) for exact artifact hashes and the RimWorld, Harmony, DLC, and profile snapshot. Runtime behavior and save compatibility remain untested and must be verified before adapter work.

Design around RWT's advertised separate-colony model, not a presumed shared simulation. The official Workshop listing describes a shared planet and advertises several world/co-op activities, but exact visit, transfer, and setting semantics need verification against the pinned build:

- Each player's local company ledger, gate, expedition maps, research completion, contracts, pawns, and case records are authoritative in that branch's save.
- Use RWT guilds, sites, roads, events, item trading/gifting, pawn aid, and configured visits where enabled. Inspect server settings before showing actions; disabled features must have a clear unavailable state.
- Treat trade, gifting, visits, aid, and other world activities as unavailable until the exact client/server release and relevant server settings are reproduced. The official RWT wiki's activity and server-configuration descriptions are setup guidance, not runtime proof; see the linked official sources and the [baseline test plan](research/RWT_BASELINE_TEST_PLAN.md).
- No documented supported RWT client extension API was identified in the 2026-09-27 source review. Public implementation classes such as `RTClient.Hooks.*` and `RTClient.Patches.*` are not stable extension hooks. Wiki-configurable JSON events and sites are a narrow server-configuration candidate only; verify their schema against a disposable copy of the pinned server. They do not establish a client API or shared research/ledger support.
- Direct trade and gifts require both players online according to the official RWT trading guide. The guide also describes vanilla drop-pod transfers to another settlement, but does not establish whether an offline recipient receives the cargo; test this route before designing asynchronous supply shipments around it.
- Treat physical Research Dossier transfer with local study as a conditional feature: after a Rimrooms build exists, the owner launches the disposable profile through RimSort and attaches RimBridgeServer for the ordinary RWT item-transfer check; then test the custom dossier and receipt idempotency after that item exists. Keep shared research-ledger synchronization out of the first build unless a supported RWT extension and nonduplicating sync are demonstrated.
- Record transaction IDs and sender/receiver branch IDs to prevent duplicate company-account postings for a shipment. Use configured transfer spots and show failed/unrecognized cargo for recovery instead of deleting or duplicating it.
- Seed a destination from its saved coordinate ID, generator version, and explicit mission inputs. Never make the two players independently recreate what is supposed to be one shared map; RWT visits and Backrooms expedition maps are distinct features.
- Do not make outcomes depend on client-only UI, local wall-clock time, external web requests, or unsaved random draws.
- Keep compatibility code behind one small adapter layer. Do not scatter multiplayer-specific checks throughout XML defs and gameplay systems.
- Keep a Core-only solo path. The multiplayer path requires RimWorld Together and Harmony; the remaining 294-profile entries are optional.
- Treat the scenario presets as alternate starting conditions over one data model, as specified in [`SCENARIOS.md`](SCENARIOS.md). After a Rimrooms build exists, the owner launches disposable vanilla-started RWT branches through RimSort and attaches RimBridgeServer for evidence capture; test Rimrooms scenario creation and mixed starts after those scenarios exist. Do not promise that clients can independently choose different Rimrooms starts until the pinned build demonstrates it.

The older `rwmt/Multiplayer` compatibility wiki is for a distinct multiplayer project and should not be treated as proof of RimWorld Together behavior. Implement against a documented, supported RWT client extension API only if one is identified in future source review; none was identified in the 2026-09-27 audit.

The local RWT snapshot has Aid and Trade enabled, but no Visit/Activity setting was found; the server enforces Crashlanded. The official RWT trading guide says direct trades and gifts require both players online. Treat item exchange and offline visits as different workflows, and test pawn aid with identity, faction, health, equipment, destination, and reconnect checks in light of [upstream issue #296](https://github.com/RimWorld-Together/Rimworld-Together/issues/296). Use a disposable server configuration copy for mixed-start experiments.

## DLC strategy

Build the base game loop without DLC-only types or content. Add conditional integrations by expansion:

- **Royalty:** honor existing quest, title, psycast, and faction systems when present; avoid requiring them for gate progress.
- **Ideology:** allow ideoligions and rituals to affect staff needs, cohesion, or company policies only after the baseline system is stable.
- **Biotech:** use genes, children, mechanoids, and pollution through optional content rather than making any of them required staff or resources.
- **Anomaly:** complement containment and study loops with optional integration; the Backrooms threat catalog remains its own system.
- **Odyssey:** complement vehicle/gravship and off-world travel systems while retaining gate-based progression as the defining campaign loop.

Test each DLC combination actually advertised as supported. `supportedVersions` in `About.xml` should list only RimWorld builds explicitly verified for release.

## Performance and failure handling

- Keep the active map's entity count, room graph size, and pathing work bounded.
- Prefer a small set of reusable room templates and composable rules to one enormous generated grid.
- Cap event and coordinate record growth with compact data and optional archival; do not remove player-built or player-visited maps silently.
- Log seed, coordinate, generator version, and failing stage when generation fails. Provide a safe fallback site rather than corrupting the campaign.
- Keep custom component Scribe keys stable and add migration code before renaming or changing saved fields.
