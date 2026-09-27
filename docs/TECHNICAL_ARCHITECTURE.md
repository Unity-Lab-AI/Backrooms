# Technical architecture proposal

This is a design target, not a claim that these types or APIs have already been implemented. Verify exact names and signatures against the installed RimWorld 1.6 assemblies and the chosen RimWorld Together client release before writing production code.

**Gate 0 decisions recorded:** private RWT prototype first; exact displayed title `Rimrooms - Async Industries`; author/publisher metadata intentionally blank; package ID `UnityLabAI.RimroomsAsyncIndustries`; internal namespace `RimroomsAsyncIndustries`; semantic versions; Core-only solo path; optional support for all five DLC; other 294-profile mods optional; indirect adaptation of Kane Pixels/A24 references, with wider community canon excluded from shipped content; dossier transfer plus shared research ledger only if supported and safely tested; English-first localization-ready; MIT for original source code. The remaining Gate 0 work is research, design, and runtime feasibility—not unresolved owner direction.

## Runtime and package boundaries

- Target RimWorld **1.6** and its Core APIs first.
- Keep Royalty, Ideology, Biotech, Anomaly, and Odyssey as optional conditional integrations; the Core campaign remains complete.
- Use the exact 294-entry profile as the full research/test target. Require only Core plus Harmony/RWT for the co-op path; all other profile mods remain optional.
- Ship one main mod package initially. Keep content and code organized so future optional extension packages can be split out without changing saved identifiers.
- Use XML Defs for buildings, items, recipes, work types, research, quests, incidents, world objects, and language strings. Use C# only for systems that genuinely need custom state, generation, UI, or simulation.

## Suggested source layout once implementation begins

```text
About/
  About.xml
  Preview.png
Assemblies/
  RimroomsAsyncIndustries.dll
Defs/
  Buildings/  Items/  Recipes/  WorkTypes/  Research/  Quests/
  WorldObjects/  Incidents/  Pawns/  Areas/
Languages/English/Keyed/
Patches/
Textures/  Sounds/
Source/RimroomsAsyncIndustries.sln
  Core/  Company/  Gate/  Expedition/  Generation/  Investigation/
  Compatibility/RimWorldTogether/
```

The repository can include `Source/` and the mod's loadable `Assemblies/` output. Create `About/About.xml` with the selected title, package ID, version policy, and license when packaging begins. Leave its author/publisher value blank or omit it if the format permits; do not insert a placeholder. The owner may assign an author later.

## State ownership and persistence

Keep each value in one authoritative owner and serialize it through RimWorld's save system.

- **Campaign/company state:** funds/ledger, research clues, unlocked coordinates, open contracts, company reputation, and global progression. Candidate: one campaign `GameComponent`.
- **World state:** coordinate records, discovered routes, outposts, signal sources, and active distortion incidents. Candidate: one `WorldComponent` plus normal `WorldObject` instances.
- **Map state:** local expedition flags, active gate/relay information, room graph identifiers, exploration data not already represented by vanilla fog-of-war, and map-local event stages. Candidate: `MapComponent` or dedicated saved world objects.
- **Building state:** gate condition, configuration, calibration, and local job status. Candidate: a gate `ThingComp` with stable references rather than duplicated global fields.
- **Pawn state:** training credentials, expedition history, exposure or case metadata. Use pawn components only for state that belongs to that pawn and survives travel.

Persist numeric IDs, stable seeds, Def references, and explicit stage values. Avoid saving direct references to temporary UI objects or relying on list order to identify a room, site, or crew.

## Destination and map generation model

Represent a destination as a stable company coordinate with a deterministic generation seed and a normal RimWorld world object that can own a saved local map. The world object should record its room graph seed, generator version, visit count, first-seen state, known exits, and return equipment. Returning to a destination loads its previous save; a deliberate anomaly modifier may alter only documented state.

Generate a local map in stages:

1. Select a room-graph recipe from the coordinate seed and mission constraints.
2. Place room/corridor templates from tagged definitions.
3. Validate that doors, paths, exits, and required workspaces are reachable.
4. Apply a small set of seeded spatial modifiers.
5. Place evidence, equipment, hazards, and entity events.
6. Register the map to its coordinate and save through normal world/map persistence.

The engine should generate only maps that the player visits. Infinite expansion is a stable generator plus coordinates and continued discovery, not a single gigantic map. Add a generator version to records so later releases can preserve old destinations or intentionally migrate them.

## Gate and expedition simulation

The gate is a normal buildable `Thing` with a component that reads power, machine condition, operator readiness, and installed modules. One transition system should own its states, for example: unbuilt, assembly, calibration, ready, opening, open, unstable, recall, cooldown, and damaged. All timers should use game ticks and deterministic inputs.

An expedition owns an explicit crew list, destination ID, opening tick, close/recall criteria, cargo rules, and event state. Avoid creating hidden parallel copies of pawn ownership, inventory, or quest progress already represented by vanilla objects. A hard time limit should trigger clear warning stages and a player-facing recall decision before catastrophic failure.

## Company UI

Begin with one compact Operations window and inspectable objects (gate, console, lab, contracts) that open focused dialogs. UI actions that change funds, assign crews, consume stock, create sites, or advance a project mutate and save the owning branch's state. Cross-branch transfer actions must route through the RWT adapter and record a transfer receipt; RWT does not make every local action a shared-state mutation. Read-only panels can stay local.

Store state independently from the screen implementation. That makes the company board replaceable without migrating every campaign record. Use keyed translations from the first content pass; avoid hard-coded visible English in C#.

## RimWorld Together requirements

The local profile confirms workshop ID `3005289691` (`RimWorld Together`) and a dedicated server package. The client and server currently have the same 294 mapped mod IDs in the same order, but the server config does not enforce that profile. The server executable reports product hash `a7bc029472d727faec4e99b7f02614c370f4771a`; its published release identity is still unresolved. See the [local RWT and gravship audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md) and pin the exact client/server/game/DLC versions before adapter or save compatibility work.

Design around RWT's advertised separate-colony model, not a presumed shared simulation. The official Workshop listing describes a shared planet and advertises several world/co-op activities, but exact visit, transfer, and setting semantics need verification against the pinned build:

- Each player's local company ledger, gate, expedition maps, research completion, contracts, pawns, and case records are authoritative in that branch's save.
- Use RWT guilds, sites, roads, events, item trading/gifting, pawn aid, and configured visits where enabled. Inspect server settings before showing actions; disabled features must have a clear unavailable state.
- Treat trade, gifting, visits, aid, and other world activities as unavailable until the exact client/server release and relevant server settings are pinned and reproduced. Do not copy older wiki claims into the API contract; those wiki pages could not be retrieved for the 2026-09-27 audit.
- Support physical Research Dossier transfer with local study. Also add shared research-ledger synchronization only if the pinned RWT build provides a supported extension and tests prove safe, nonduplicating updates.
- Record transaction IDs and sender/receiver branch IDs to avoid duplicate shipment credits. Use configured transfer spots and show failed/unrecognized cargo for recovery instead of deleting or duplicating it.
- Seed a destination from its saved coordinate ID, generator version, and explicit mission inputs. Never make the two players independently recreate what is supposed to be one shared map; RWT visits and Backrooms expedition maps are distinct features.
- Do not make outcomes depend on client-only UI, local wall-clock time, external web requests, or unsaved random draws.
- Keep compatibility code behind one small adapter layer. Do not scatter multiplayer-specific checks throughout XML defs and gameplay systems.
- Keep a Core-only solo path. The multiplayer path requires RimWorld Together and Harmony; the remaining 294-profile entries are optional.
- Treat the scenario presets as alternate starting conditions over one data model, as specified in [`SCENARIOS.md`](SCENARIOS.md). Test how new-game scenario creation maps onto RWT's shared world; do not assume separate clients can independently create different world starts until that behavior is demonstrated.

The older `rwmt/Multiplayer` compatibility wiki is for a distinct multiplayer project and should not be treated as proof of RimWorld Together behavior. Use the chosen RWT source, version, and client APIs for implementation.

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
