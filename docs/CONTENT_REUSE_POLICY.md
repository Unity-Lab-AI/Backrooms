# Content reuse and original-content policy

> Current owner decisions across the project: [DECISIONS_CURRENT.md](DECISIONS_CURRENT.md).

## ⛔ SUPERSEDED IN PART, 2026-10-06. READ THIS BEFORE THE RULES BELOW ⛔

**Binding owner direction, 2026-10-06, verbatim:** *"are we making our own items and benches and gates? becasue if so i fucking love it!"*, and, asked which way to take it, the owner chose **full reversal — our own items and benches** over sound-only, over gate-identity-only, and over leaving the 0.2.0 content archived. With it: *"remember things rotate"*.

**So Rimrooms ships original gameplay art and audio again, and may declare its own items, production benches, gate equipment and terrain.** The 2026-09-28 direction below is the reason every such object was retired across 0.9.0-dev, 0.9.9-dev and 0.12.22-dev. It is kept word for word because it was true on the day, because invariant 105 forbids making a removal look like progress, and because a reader who finds those retirement records must be able to see what overruled them.

**What is NOT reversed, and inferring otherwise would break the mod.** Reuse remains the default and the gate remains a **designation on an existing Core `Door`/`Autodoor`**. That binding is what the 294-mod profile integrates against — register rows 273 Locks, 77 Doors Expanded, 185 ReBuild: Doors and Corners, 252 Vault Walls and Doors, 201 Secret Passage Doors, 265 AirtightGarageDoors — and it is what a prisoner crossing rides on, since *"if zoned to and door are allowed access"* is door permissions and nothing else. **Original content is added beside the reuse bindings, never in place of them.** Both routes stay reachable; a player without a named mod still has a working object.

**Three conditions on original content, derived from the rules the reversal did not touch:**

1. **Reuse first where reuse already works.** A new Def is justified by a role no existing object fills, not by a wish to attach a texture. The records desk is the worked example: its own Def, Core's `Table1x2` texture, because the role was new and the look was not.
2. **Never copy another package's assets or source.** Unchanged from the original policy, and the reversal does not weaken it. Original means ours.
3. **Things rotate.** `Graphic_Multi` requires `_north`, `_east` and `_south`; RimWorld mirrors `_west` from `_east` and nothing else is free. A rotatable building shipping one frame four times is a defect, and a master that has no authored rotation is named rather than faked.

---

## The 2026-09-28 direction, kept verbatim

**Binding owner direction, 2026-09-28:** Rimrooms repurposes content already in RimWorld and the selected installed mods. The owner does not want a new item, equipment, furniture, production-bench or in-game asset production project. This supersedes earlier instructions to create original gameplay art/audio and custom physical item/building content. The full company/procedural campaign scope is retained.

**That paragraph is history as of 2026-10-06, not instruction.** The rules it produced follow, each marked where the reversal reaches it.

## What implementation must do

- Use existing native `ThingDef`, `TerrainDef`, pawn/race/kind, recipe, furniture, apparel, weapon and sound definitions where their behavior fits the required role. Reference the providing game/mod at runtime; do not copy its assets or source into this package.
- Build the Backrooms atmosphere from arrangements of existing rooms, walls, doors, floors, lighting, furniture and objects, with procedural topology, events, state changes and the company's UI/records. Original algorithms, stories, text, quests and layouts remain Rimrooms work.
- Implement machine operation by assigning company roles to real existing installed objects and connecting power, staffing, research and expedition logic. Do not introduce a new machine/console/bench `ThingDef` merely to attach a copied texture. **Reversed in part, 2026-10-06:** a new `ThingDef` carrying **our own original art** is now permitted where the role warrants an object of our own. The clause that stands is *copied* — another package's texture never justifies a Def, and never travels into this one.
- Use actual existing gear and inventory for field-equipment requirements and effects. Track which concrete object has a mission/evidence role through saved references and identifiers. A renamed clone with a new Def is still a new item and does not satisfy this direction.
- Run analysis, research and production through existing workstations and available native/modded work routes. Rimrooms may add scoped jobs, work-giver logic, recipes using existing inputs/outputs, policy/configuration Defs and UI where needed. **Reversed, 2026-10-06:** Rimrooms **may** add its own production benches and its own physical products, on the owner's words *"our own items and benches and gates"*. The existing-workstation routes stay reachable beside them, so a colony that never builds our bench is never stuck.
- Keep currency, contracts, route knowledge, case files and research dossiers as company records where they do not require physical custody. Where physical custody or transfer is required, bind it to an existing suitable object and implement its receipt/save/transfer behavior explicitly. A digital record is not a substitute for promised physical hauling.
- Use existing native/modded pawn or entity presentations for threats and people, with original Rimrooms behavior only where compatible. **Reversed, 2026-10-06:** original threat sprites, item icons, furniture, floor textures and gameplay audio are permitted again, on the owner's words *"a audio folder! sounds dope!!!"* and the full-reversal decision. **The fairness rule in [`THREAT_DESIGN_SHEETS.md`](THREAT_DESIGN_SHEETS.md) is untouched and now matters more**: *"Do not use color or sound as the only way to notice a tell."* Our own art and our own cue may carry an encounter's character; neither may carry its warning. Clear text still does that.
- Preserve native item mass, stack limits, work, building usability, needs and optional-mod behavior. OgreStack remains the runtime stack-limit source through live `ThingDef.stackLimit`; company value does not become impossible silver stacks.

**Explicit door direction, and it survives the reversal intact:** the owner selected actual existing doors, native recolouring and aura, and the installed door sizes the game already supports. See [the scenario and gate contract](SCENARIO_SETUP_AND_PORTAL_NETWORK.md): power, batteries, control equipment, research and upgrades govern opening duration, aperture and recall of saved sites. **No cloned door Def.** This is the one clause the 2026-10-06 reversal deliberately leaves standing, because a cloned door is exactly what would cut the gate off from Locks, Doors Expanded, ReBuild and every prisoner-access mod in the profile. Our own gate **equipment** may be our own Defs with our own art; the door the gate is designated on stays the player's real door.

## Content provider and dependency rules

Every repurposed role needs a saved binding: functional role, actual provider package ID, existing Def name, reviewed version/source, prerequisite, a fallback built from Core content alone, player assignment/action, save ownership and failure recovery. Use the 294-row register and the exact per-mod review before depending on that mod's behavior. Modded objects should contribute useful function where supported; there is no requirement to replace them with Rimrooms equivalents.

**Superseded on 2026-10-03 by the owner's no-hard-dependency decision** ([D3/D4 rows](GATE_0_DECISIONS.md#decision-log)): the package declares no `modDependencies`; the fallbacks below are now the supported path, not only the broken-promise path. Kept as history: **The collection is mandatory now, and the fallbacks still have to exist.** Those sound contradictory and are not, because the owner chose both halves on 2026-10-01: declare every member of the collection in `About.xml` so a mod manager names anything missing, *and* keep looking content up by name so a player who ignored that warning degrades instead of crashing. The declaration is the promise; the fallback is what happens when the promise is broken anyway.

So the rule that used to read *"retain a working Core route to campaign progression"* is retained — not as a supported way to play, but as the behaviour when a declared provider is absent at runtime. If Core has no literal version of a specialist object, use a clearly explained Core mechanism that delivers the same gameplay function, and never pretend a fallback has a capability it lacks.

*(Superseded on 2026-10-03 with the paragraph above: nothing is mandatory, so the retired instruction is moot rather than overruled.)* **What is retired is the old sentence's closing instruction, *"do not silently make all 294 mods mandatory."*** Nothing is silent about it: every requirement carries a display name and a way to obtain it, which is the opposite of the failure that line was written to prevent.

Mappings are opt-in to the company's designated facilities and marked objects. Do not globally rename/rebalance every native workbench, turn ordinary component stacks into evidence, or change an unrelated colony by installing Rimrooms. Distinct object identity, split/merge behavior, loss, sale, recovery and save migration need explicit handling.

## Earlier 0.2.0 content and migration — **REINSTATED 2026-10-06**

The historical 0.2.0 development package contains custom gameplay Defs and original PNG/WAV files. **They are no longer superseded.** The owner's reversal names them directly — *"i just saw the pngs in ... assets/source/phase2"* — and they are the starting material for the original content this policy now permits. The archive under `implementation/historical-content/0.2.0/` stays exactly where it is; **it is a record of what was retired and why, and reinstating content does not license deleting the record of its retirement.**

**Reinstated does not mean copied back.** Measured against the game, the thirteen masters are not loadable as they stand: 1254×1254 is non-power-of-two and roughly ten times RimWorld's ~128 px per tile, the institutional carpet has a seam error of **18.3 / 17.8** where anything over 6 shows a grid across every floor, ink coverage runs as low as **15.3%**, several are drawn as front elevations rather than a tilted top-down, and **none has a rotation**. Each one is re-cut by tool from its master, never hand-copied, so the derivation can be re-run when a master changes.

The [existing-content replacement map](implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md) stays accurate as the record of what each role was bound to while the 2026-09-28 direction held, and stays the **fallback** map: an original object and its reuse binding both remain reachable. Keep old project masters and evidence as historical records; do not delete them to hide a change in either direction.

Account for earlier development saves before removing Defs: retain inert migration handling when technically necessary, or explicitly declare a development-save break with a preserved old build and owner-visible fresh-save requirement. Do not silently delete pawns/items/maps or falsely mark old saves compatible. Runtime acceptance remains deferred; source/build work continues.

## Menu backgrounds and package presentation

**Owner clarification, 2026-09-28:** original Backrooms-themed, RimWorld-style main-menu background images remain required. This is the visual exception to existing-content-only gameplay. Create/present the slideshow as requested; do not treat it as authorization for custom gameplay items, benches, sprites, textures or audio.

**The menu images stopped being an exception on 2026-10-06** — they are now simply the first original art this mod shipped, and the sentence above is kept because every retirement record cites it. What the clarification still governs is unchanged: menu artwork is presentation, and no amount of it decides what gameplay content exists.

Show **Rimrooms - Async Industries** and the current loaded mod version alongside RimWorld's other version information at the **top left of the main menu**. Derive the version from the running build/package. Draw title/version as interface text rather than baking version text into every background, so updates do not leave stale artwork. Preserve native version information, readability, DLC hover backgrounds, other menu-owner behavior, disable/fallback and reduced-motion settings.

The two existing original menu candidates are available for this use. Record their original source/provenance and actual native resolution; do not claim 4K masters. Later image additions should represent actual implemented mod experiences. The existing package preview is presentation metadata; it does not permit new gameplay art.

## Documentation and completion rule

In older design inventories, names such as field recorder, survey tag, evidence case, gate console and laboratory describe gameplay roles. They no longer authorize a new physical Def/asset. *(Superseded in part on 2026-10-06: a new Def with our own original art is permitted where the role warrants it, under the three conditions at the top of this file.)* *(Superseded on 2026-10-06 for original assets of our own.)* Older original-asset tasks are superseded by provider selection, runtime binding, procedural arrangement, integration and reference cleanup. Source records about another mod's own content remain valid source evidence; do not rewrite their facts.

A reuse task is implemented only when its existing provider object is reachable through the actual player flow and the Rimrooms state/logic uses it. A source mapping alone is preparation. Compilation is build evidence; later owner-launched checks still establish behavior, saves, performance, visual readability and compatibility. Never reduce the full-mod goal to a mapping document or the current first slice.
