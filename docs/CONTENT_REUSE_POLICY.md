# Existing-content-only gameplay policy

**Binding owner direction, 2026-09-28:** Rimrooms repurposes content already in RimWorld and the selected installed mods. The owner does not want a new item, equipment, furniture, production-bench or in-game asset production project. This supersedes earlier instructions to create original gameplay art/audio and custom physical item/building content. The full company/procedural campaign scope is retained.

## What implementation must do

- Use existing native `ThingDef`, `TerrainDef`, pawn/race/kind, recipe, furniture, apparel, weapon and sound definitions where their behavior fits the required role. Reference the providing game/mod at runtime; do not copy its assets or source into this package.
- Build the Backrooms atmosphere from arrangements of existing rooms, walls, doors, floors, lighting, furniture and objects, with procedural topology, events, state changes and the company's UI/records. Original algorithms, stories, text, quests and layouts remain Rimrooms work.
- Implement machine operation by assigning company roles to real existing installed objects and connecting power, staffing, research and expedition logic. Do not introduce a new machine/console/bench `ThingDef` merely to attach a copied texture.
- Use actual existing gear and inventory for field-equipment requirements and effects. Track which concrete object has a mission/evidence role through saved references and identifiers. A renamed clone with a new Def is still a new item and does not satisfy this direction.
- Run analysis, research and production through existing workstations and available native/modded work routes. Rimrooms may add scoped jobs, work-giver logic, recipes using existing inputs/outputs, policy/configuration Defs and UI where needed; it must not add a new production bench or fabricate a new physical product.
- Keep currency, contracts, route knowledge, case files and research dossiers as company records where they do not require physical custody. Where physical custody or transfer is required, bind it to an existing suitable object and implement its receipt/save/transfer behavior explicitly. A digital record is not a substitute for promised physical hauling.
- Use existing native/modded pawn or entity presentations for threats and people, with original Rimrooms behavior only where compatible. Do not commission or generate new threat sprites, uniforms, furniture, item icons, floor textures or gameplay audio. Use existing UI graphics/sounds or clear text where no suitable asset exists.
- Preserve native item mass, stack limits, work, building usability, needs and optional-mod behavior. OgreStack remains the runtime stack-limit source through live `ThingDef.stackLimit`; company value does not become impossible silver stacks.

**Explicit door direction:** the owner selected actual existing doors, native recolouring and aura, and the installed door sizes the game already supports. See [the scenario and gate contract](SCENARIO_SETUP_AND_PORTAL_NETWORK.md): power, batteries, control equipment, research and upgrades govern opening duration, aperture and recall of saved sites. No cloned door Def or new gameplay sprite is permitted.

## Content provider and dependency rules

Every repurposed role needs a saved binding: functional role, actual provider package ID, existing Def name, reviewed version/source, prerequisite, Core-only fallback, player assignment/action, save ownership and failure recovery. Use the 294-row register and the exact per-mod review before depending on that mod's behavior. Modded objects should contribute useful function where supported; there is no requirement to replace them with Rimrooms equivalents.

Keep a complete Core-only solo route and optional DLC/profile support under the existing owner decisions. If Core has no literal version of a specialist object, use a clearly explained existing Core mechanism that delivers the same gameplay function; do not pretend a fallback has an unsupported capability. If a faithful function genuinely requires an optional provider, expose that optional route and retain a working Core route to campaign progression. Do not silently make all 294 mods mandatory.

Mappings are opt-in to the company's designated facilities and marked objects. Do not globally rename/rebalance every native workbench, turn ordinary component stacks into evidence, or change an unrelated colony by installing Rimrooms. Distinct object identity, split/merge behavior, loss, sale, recovery and save migration need explicit handling.

## Earlier 0.2.0 content and migration

The historical 0.2.0 development package contains custom gameplay Defs and original PNG/WAV files that predate this instruction. Their build/staging/provenance receipts remain truthful historical evidence, but that content is **superseded for the intended finished mod**. Do not use it as a template for adding further custom items or assets.

Replace those objects and source consumers using the [existing-content replacement map](implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md). Keep old project masters/evidence as historical records; do not delete them to hide the change. Remove obsolete gameplay assets from the active package/allowlist when their runtime references have been replaced. No future release may contain the superseded custom gameplay assets by accident.

Account for earlier development saves before removing Defs: retain inert migration handling when technically necessary, or explicitly declare a development-save break with a preserved old build and owner-visible fresh-save requirement. Do not silently delete pawns/items/maps or falsely mark old saves compatible. Runtime acceptance remains deferred; source/build work continues.

## Menu backgrounds and package presentation

**Owner clarification, 2026-09-28:** original Backrooms-themed, RimWorld-style main-menu background images remain required. This is the visual exception to existing-content-only gameplay. Create/present the slideshow as requested; do not treat it as authorization for custom gameplay items, benches, sprites, textures or audio.

Show **Rimrooms - Async Industries** and the current loaded mod version alongside RimWorld's other version information at the **top left of the main menu**. Derive the version from the running build/package. Draw title/version as interface text rather than baking version text into every background, so updates do not leave stale artwork. Preserve native version information, readability, DLC hover backgrounds, other menu-owner behavior, disable/fallback and reduced-motion settings.

The two existing original menu candidates are available for this use. Record their original source/provenance and actual native resolution; do not claim 4K masters. Later image additions should represent actual implemented mod experiences. The existing package preview is presentation metadata; it does not permit new gameplay art.

## Documentation and completion rule

In older design inventories, names such as field recorder, survey tag, evidence case, gate console and laboratory describe gameplay roles. They no longer authorize a new physical Def/asset. Older original-asset tasks are superseded by provider selection, runtime binding, procedural arrangement, integration and reference cleanup. Source records about another mod's own content remain valid source evidence; do not rewrite their facts.

A reuse task is implemented only when its existing provider object is reachable through the actual player flow and the Rimrooms state/logic uses it. A source mapping alone is preparation. Compilation is build evidence; later owner-launched checks still establish behavior, saves, performance, visual readability and compatibility. Never reduce the full-mod goal to a mapping document or the current first slice.
