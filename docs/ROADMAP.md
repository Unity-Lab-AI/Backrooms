# Development roadmap

The work is sequenced so that later content depends on a tested company loop rather than a pile of disconnected buildings and monsters. These are planning stages; none of the gameplay systems is implemented yet. Gate 0 is a strict pre-build gate: complete all owner decisions, source reviews, and the 294-mod feature map before creating the code project. See [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md).

## Stage 0 — decisions and research

- Use the selected title, package ID, namespace, distribution target, and MIT source-code license. Set author/publisher metadata to `Operator`; track art/audio provenance and licensing separately.
- Capture the exact RimWorld 1.6 build, DLC set, RimWorld Together client version, server release, and client load order.
- Maintain the completed 23-entry Kane fan-summary notes and separate A24 fan-summary story note; check official sources only for design-critical gaps, and assess supplemental Kane-related material without folding broader community canon into shipped content.
- Establish folder layout, build setup, language-key conventions, save ownership rules, and multiplayer synchronization approach.

**Exit condition:** a concrete versioned target profile and a documented content-provenance rule exist.

## Stage 1 — facility start and company shell

- Use [`SCENARIOS.md`](SCENARIOS.md) as the data-driven scenario setup contract and implement the first new-game scenario: Async Industries with a small facility, a roster, starter resources, a disabled gate, and a first project.
- Add the basic machine building, calibration/assembly project, operator and power requirements, and clear gate status feedback.
- Add the first company console and minimal operations record: funds, staff, active projects, and incidents.
- Preserve normal pawn management, work priorities, needs, health, storage, and construction.

**Exit condition:** a save starts and plays as a facility-management campaign before any endless destination system exists.

The Furniture & Knickknack Store breach and Lone Survivor starts are planned scenarios, not part of the first playable acceptance target. Their starting-state contracts are documented in [`SCENARIOS.md`](SCENARIOS.md); implement them after the facility-to-expedition vertical slice has stable save and return behavior. Add outpost, town-distortion, and company-crisis openings only after their acceptance criteria and procedural variation are designed.

## Stage 2 — first expedition vertical slice

- Add one stable seeded coordinate that creates a single local site from a small room set.
- Send a named crew and equipment loadout through a time-limited opening.
- Add one return method, one environmental risk, one entity encounter, one recoverable evidence chain, and one payment/research outcome.
- Reopen the coordinate and preserve meaningful prior exploration and recovered state.
- Serialize campaign, coordinate, gate, quest, crew, and site state.

**Exit condition:** the full prepare → enter → investigate → extract → analyze → reward loop works in a save and can be repeated.

## Stage 3 — co-op and DLC foundation

- Add a narrow RimWorld Together adapter using only supported extension points; keep branch-local campaign state authoritative.
- Verify guilds, sites/roads/events, item trade/gifts, pawn aid, configured facility visits, transfer spots, and reconnect/save behavior against a pinned client/server release.
- Implement physical dossier exchange only after the exact RWT build reliably transfers the Backrooms dossier; research completion remains local to each branch.
- Add optional DLC content for Royalty, Ideology, Biotech, Anomaly, and Odyssey; keep the complete Core-only campaign path playable.
- Run the mod in a clean baseline and then the exact recorded local server profile; keep an explicit list of known interactions.

**Exit condition:** a second client can operate a separate company branch, exchange verified supplies/dossiers, use supported RWT world activities, and reconnect without duplicating or corrupting either branch. Direct shared research is enabled only if the selected supported ledger extension passes synchronization tests; otherwise dossiers remain the technology-transfer path. No live shared-map control is assumed.

## Stage 4 — management breadth

- Expand hiring, role assignments, training, staff records, labs, cafeterias, dormitories, medical/quarantine, evidence storage, contracts, procurement, and shipment schedules.
- Add two-way company economy with operating costs, salvage valuation, wages or contract labor, penalties, and equipment loss.
- Add the Operations interface for finance, projects, staff, research clues, contracts, destinations, and incidents.
- Grow the Operations panes into the Company Command navigation layout, retaining direct access to vanilla pawn/work/research/world controls.

**Exit condition:** the company has meaningful operating choices between expeditions, not only construction chores.

## Stage 5 — world network and spatial variation

- Expand room templates, map themes, coordinate selection, radio reports, return navigation, remote supply, relay stations, and outposts.
- Add rescue, survey, retrieval, containment, and town-distortion quest families.
- Add stable map archival and generator-version migration rules.
- Introduce vehicle/space travel as a later logistics layer that supports the company's reach without replacing gate exploration.

**Exit condition:** an established company can run parallel sites and revisit saved spaces without save corruption or runaway map growth.

## Stage 6 — long-form progression and release

- Expand threat catalog, countermeasures, deeper research branches, long-duration openings, multi-team operations, advanced transport, and endgame phenomena.
- Add remaining original narratives, art, sounds, translations, accessibility options, settings, tutorials, and Workshop packaging.
- Maintain a published compatibility table for RimWorld 1.6 builds, DLC combinations, RimWorld Together versions, and explicitly supported optional mods.

**Exit condition:** release notes, credits, licensing records, installation guidance, save/migration policy, and compatibility statements match what was actually verified.

## Non-goals for the first playable build

- A literal infinite map loaded at once.
- Replacing every vanilla tab and menu before the simulation loop works.
- Requiring the local 294-mod profile as a dependency set.
- Promising compatibility with every mod simply because the server has `AllowAllMods` enabled.
- Reusing film footage, screenshots, transcripts, distinctive named entities, or unverified community assets as shipped content.
