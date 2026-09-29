# Changelog

## 0.5.6-dev - 2026-09-28 - tune how eagerly colonists cross a gate, while the game runs

- You can now set how eagerly colonists cross a gate to work, for all four kinds of cross-gate errand, in the mod settings. Changes take effect the moment you close the window: no restart, no reload.
- Starting a trip is always kept below finishing one, and the settings screen tells you when it has done that. Otherwise a colonist standing on the far side holding something could be sent on a fresh errand instead of finishing the delivery.
- The shipped numbers stay the shipped numbers. Only values you actually change are saved, and there is a reset button.
- Checked the whole package against RimWorld and Steam requirements and wrote the position down with the evidence behind it: no game or expansion file is included, nothing of the base game is overwritten or deleted, no expansion is required, no third-party mod is required, and the mod targets official RimWorld and official expansions only. Those checks now run automatically on every build, so the position cannot quietly rot.
- Nothing in this project is waiting on anybody. Every item that can only be confirmed by playing is now marked as belonging to the single test pass that happens once the mod is finished, and none of them holds up any work.

Full record: [tunable priorities and the test phase](docs/implementation/TUNABLE_PRIORITIES_AND_TEST_PHASE.md) and the [compliance position](docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.5-dev - 2026-09-28 - a builder crosses a gate to finish the job

- A frame on the other side of a gate that already has all its material can now be finished. A builder walks through and builds it. Nothing is carried, because nothing needs carrying — this is the other half of last build's material delivery.
- The building itself is entirely the game's own. Your colonist finishes the frame with the game's normal construction job, its normal reservation and its normal speed. All this mod does is decide that walking over there is worth it.
- A builder will not cross a gate while there is any construction work left on this side — not even smoothing a wall. Local work always comes first.
- A builder already on the way is not turned around by a frame that appears at home while it walks, so it does not get stuck oscillating at a doorway.
- Nobody is ever dragged home. When the work over there runs out, the colonist is simply free where it stands, with its own needs and whatever local work it finds, exactly like anyone else who walked through a gate.
- A colonist can only ever owe one cross-gate errand at a time. It cannot be promised a haul and a building job at once and then abandon one of them.
- Respects your work assignments as always: a colonist with construction switched off is never sent, and nothing here is ever a forced order.
- Operations lists people working across a gate separately from people carrying things across one, because reading the first as hauling would be misleading.

Also captured this build: the campaign opens in the 1990s, and the world's factions are the universe's own — the US government, rival corporations after proprietary technology, disgruntled ex-employees, high-tech thieves, corporate espionage and sabotage, and concerned citizens — default-set per scenario and tailored to each. They begin neutral and earn their hostility from what your company actually does. That layer is authored after the remaining cross-gate work families. Source and compiler evidence: [travel-to-work record](docs/implementation/CONNECTED_TRAVEL_TO_WORK_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.4-dev - 2026-09-28 - a gate you can actually work through, and a company you name

- A laboratory gate's first opening now lasts about thirty real minutes instead of about fourteen real seconds. The old value could not support a single round trip, which would have made every cross-gate work family unusable on a laboratory gate. Each research advance multiplies the duration, and at the top of the ladder a supported opening has no countdown at all.
- "No countdown" still means "while supported". Power, the operator on station and the energy supply are all checked every tick exactly as before, so running the supply dry ends the opening the same way cutting power does. A sustained draw needs real sustained generation behind it, not just batteries.
- Duration advances on *completed* research, never on spendable insight. Gating it on the currency would have meant spending research to advance shrank your gate.
- Natural gates are untouched and still permanently open, with no timer, operator, power or close command of any kind. Confirmed in the source rather than assumed.
- Every scenario researches the same tree and can build a full company, so nothing about duration or research is tied to which start you chose.
- You name your own company. A field at setup on every start, the name shown throughout Operations, and renaming any time through the game's own rename dialog. The old fixed identity survives only as a suggested default.

Two questions open since the earliest planning are now answered: the inside start has a configurable party, and its first exit lets the player choose the destination settlement rather than revealing a fixed one. Note one honest gap: only one company project exists so far, so the top of the duration ladder cannot be reached until the research tree lands. Source and compiler evidence: [gate duration and naming record](docs/implementation/GATE_DURATION_AND_COMPANY_NAMING.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.3-dev - 2026-09-28 - material reaches a build site through a gate, and the dependency position is audited

- A half-built structure stalled for want of steel can now be supplied from the other side of a gate. A colonist picks up the real material, carries it through, and puts it into the build site. Blueprints work as well as part-built frames, because the game's own delivery step turns a blueprint into a frame on the first material that arrives.
- Nothing about building is reimplemented. The site's own material requirement, the frame's own resource store and the work of building all stay the game's; only the carrying is ours.
- Audited what this mod actually requires and confirmed it needs nothing but the base game. Every game definition it uses was traced to base Core: no DLC, no Harmony, no other mod. The mod description now says so precisely instead of just claiming it.
- Fixed four places where a missing definition would have thrown an error at you instead of quietly reporting the action as unavailable. A definition can go missing because of another mod or a load-order clash, and that should never be a crash. There are now none of those left.
- Confirmed two compatibility claims are real rather than intended: stack-size mods are respected automatically because no stack size is ever hardcoded, and modded doors work as gate thresholds because doors are recognised by what they are rather than by name.
- Corrected a recorded blocker that was simply wrong: the gate's power draw was said to exceed every single generator in the game, while the same sentence named one that exceeds it. A draw is supplied by a power network in any case.

Recorded the method behind the above as binding: decide what to build a feature on by the capability it needs, never by a name. Because this mod adds behaviour to existing game objects rather than inventing objects, every piece of custom gear still awaiting replacement now has an existing-content answer, which unblocks that work on content grounds. See the [dependency and capability record](docs/implementation/DEPENDENCIES_AND_CAPABILITY_MATCHING.md) and the [construction record](docs/implementation/CONNECTED_CONSTRUCTION_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.2-dev - 2026-09-28 - our own people and our dead come home

- A colonist who goes down on the far side of a gate can now be fetched. Another of our people crosses, picks them up, carries them back and puts them in a bed. If no bed is free on arrival they are set down on this side and ordinary rescue takes over from there, because being home is what the trip was for.
- Our dead come back too, to a grave or to storage. This needed no new machinery: the game already treats carrying a corpse as ordinary hauling, and a grave is reached the same way any other container is.
- Fixed a real gap that would have made that silently not work: the planner only looked for open floor space, and a grave is not floor space. A corpse whose only home was a grave would never have been planned for, and the container delivery route added last build would have sat unreachable for exactly the case it was built for.
- Capture stays a player order, not automatic work, which is both how the game does it and what the gate rule says: people and monstrosities come back because you directed it.

This is the casualties-and-remains work family, built ahead of construction because carrying people back through an opening is something the gate rule names explicitly and no route reached it at all. Tending someone across a gate is a different capability and is not implemented. Source and compiler evidence: [casualties record](docs/implementation/CONNECTED_CASUALTIES_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.1-dev - 2026-09-28 - nine deferments closed, and doorways that lead onward

- Doorways deeper in can now be found. One of our own people walks up to a doorway in the Backrooms, studies it, and records that it leads somewhere else: a permanently open way through to a further space. A doorway's answer comes from its own position under that space's saved seed, so it is always the same answer and revisiting never rerolls it. At most two ways onward per space, so a chain of spaces stays finite.
- Storage containers are now valid delivery destinations for cross-gate hauling, not just open stockpile cells. This follows the game's own rule for which destinations take which route, which is also what makes the storage-framework mods work here without special handling for each one.
- A worker no longer plans a trip whose arrival its allowed area forbids. The game offers no way to ask about a zone on a map a pawn is not standing on, so instead we write down what we saw while we were standing there, and an unseen map is treated as unrestricted exactly as the game itself treats it. A destination that turns someone away is left alone for a while afterwards.
- Finished crossing records are now bounded. Automatic hauling made these an everyday event rather than a rare order, so they would otherwise have grown in the save forever. Unresolved records are never touched, because those hold real people and real cargo.
- Fixed four pieces of missing text that would have shown the player a raw internal name, including the Procurement tab label.
- Internal: one implementation each for branch map ownership and for choosing a threshold's approach cell, instead of two and three.

Nine deferred items closed, seven of which turned out to be blocked on nothing and three of which had already shipped and were still listed as outstanding. The deferment register now carries the four audit questions that caught them, so it gets checked rather than only added to. Source and compiler evidence: [audit and closures record](docs/implementation/DEFERMENT_AUDIT_AND_CLOSURES.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.5.0-dev - 2026-09-28 - colonists work across a gate

- Added cross-gate work as ordinary work. A colonist can now haul an actual object from the map that holds it, carry it through a gate in real hands under native mass and stack limits, and put it into storage the other side's own settings accept. Both directions. No dispatch, no crew list, no cargo manifest.
- Added the saved work intent that makes a trip survive its job boundaries, a save and a reload: it remembers the worker, the one real object, the destination, and the gate the plan was made against. The next physical step is always worked out from the worker's actual current position, so an interruption or an unexpected location resolves by itself.
- Added the planning lease, which stops two of our own planners promising the same stack and does nothing else. It is not a reservation, it excludes nobody, and it expires.
- Work reaches people through ordinary work priorities, within-type order, schedules, disabled work types and required capacities, because it is an ordinary work giver rather than something that pushes errands. Hunger, sleep, danger, drafting and mental states keep winning. Nothing is ever marked as a forced player order.
- Nothing is counted, cloned, teleported or consumed at a distance. The object that arrives is the object that left, or the honest split of a stack that a partial pickup produced. A delivery that merges into an existing stack is a finished delivery, not a lost item.
- Added a list of the work trips currently crossing a gate, because saved state that moves people and goods must never be invisible.

Storage hauling is the first of the work families and the only one in this version. Construction, bills, research, medical care, food and rest are specified with named owner steps in the [deferment register](docs/DEFERRED.md) and are not claimed here. Also recorded permanently in the [pinned Core API reference](docs/implementation/CONNECTED_WORK_CORE_API.md): RimWorld 1.6 does ship its own map-portal system, and it cannot serve this design, because its hauling does nothing without a player-filled loading manifest and its crossing drops carried cargo on arrival. Source and compiler evidence: [connected-work record](docs/implementation/CONNECTED_WORK_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

## 0.4.3-dev — 2026-09-28 — inhabitants stay in the Backrooms

- Added the rule that people and monstrosities on the far side do not cross a gate. Nothing but this company's own people walks through, an open gate is never an objective, lure, spawn target, raid route or attack trigger, and no setting, research or upgrade changes that.
- Everything else comes back because one of our own people carried it: materials, tools, equipment, resources, minified furniture and production benches, corpses, and people or monstrosities that are genuinely downed, dead or held prisoner. Anyone still on their own feet cannot be taken through.
- One chokepoint enforces it for every gate at once, so no future work adapter, scheduler, generator or threat can reintroduce the behaviour by accident.
- Added player-facing text for each refusal.

Gate, machine door and portal mean the same thing; every start can eventually run several gates, and nothing assumes one gate per branch, map or coordinate. The gradual-escalation half of the same rule — how much pressure a space presents and how it grows — is specified but not yet implemented; it is owned by the procedural-inhabitants work in the [deferment register](docs/DEFERRED.md). Source and compiler evidence: [connected-travel record](docs/implementation/CONNECTED_TRAVEL_IMPLEMENTATION.md). No gameplay result is claimed.

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
