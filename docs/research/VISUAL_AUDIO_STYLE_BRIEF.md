# Rimrooms - Async Industries: visual and audio style brief

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** presentation direction using existing Core/DLC/installed-mod content. New gameplay art, audio, items and production benches are excluded by the owner. New procedural arrangements, behavior, UI and story text remain in scope.

## Experience in one sentence

Make the company's spaces feel practical and inspectable, then let familiar rooms become quietly wrong in ways the player can notice, investigate, and survive.

## Reference and originality rules

- Use Kane Pixels' series as the primary source for broad moods and story cues: institutional research, procedural footage, fluorescent interiors, uncertain routes, missing crews, and incomplete returns. The [fan cliff notes](KANE_PIXELS_FAN_CLIFF_NOTES.md) are a quick index, not proof of every visual detail.
- Use the [separate A24 feature review](reviews/a24-feature/feature-review.md) only for its own store/Async branch and production notes. Do not collapse film events into the series timeline.
- Translate these references into original procedural arrangements, story text, observations and behavior using existing RimWorld/mod furniture, objects, pawns, terrain and sounds. Do not create new gameplay graphics or audio, clone item/bench definitions, or copy provider files. Broader community Backrooms designs remain outside the selected story scope.
- Label future entries as **source cue**, **interpretation**, or **original design** in the [provenance register](provenance-register.csv). A reference mention does not establish permission for a specific borrowed asset.

## Visual language

### Company facilities

Show a small organization making an improvised research site work: practical concrete, painted block, steel doors, wired glass, work lights, cable runs, labeled storage, paper notices, and patched equipment. Labs, security, staff rooms, cafeteria, power, loading, and machine spaces should be identifiable by their furniture and work purpose. A room's function must not depend on hidden score values.

Keep the company spaces brighter, more orderly, and more legible than the destinations. As money, equipment, and security improve, the base becomes better organized without turning into a generic futuristic command center.

### The machine gate

Make the gate read as an engineered installation that needs power, operators, clearance, and maintenance. Represent build, calibration, ready, opening, unstable, recall, cooldown and damaged states through designated existing equipment, available native lights and clear interface text. Alarms and animation support those labels; the player must never need to infer a dangerous state from color or a brief flash alone.

### Backrooms destinations

Start with commonplace interiors and let one or two precise changes create unease: a doorway in the wrong place, a repeated corridor, an altered room dimension, a moved object, an exit that no longer matches the route, or a familiar space with a new obstruction. Tie room variations to a readable room family, coordinate clue, equipment tag, or logged anomaly. Avoid random visual clutter without a gameplay or story reason.

Increase variation gradually: institutional rooms and service corridors first; then deeper spaces combine known room families, altered connections, and occasional new rules. Preserve recognizable landmarks, route clues, and a return path. A rare distortion can surprise the player, but the UI and map record should explain what changed after the event.

### Scenarios

- **Async Industries:** a modest, functional research/security compound, an unfinished gate chamber, sparse starter stock, and a small crew with clear needs.
- **Furniture & Knickknack Store:** an ordinary public shop with recognizable retail stock and back-of-house space; the threshold and missing-person case introduce the abnormal layer without turning the whole shop into a horror set.
- **Lone Survivor:** a readable survival space with limited equipment, visible route clues, and immediate needs. The player should understand what can be used, what is unsafe, and what might lead to escape or rescue.

All three use the same icon grammar and status language, but their opening inventory, camera composition, and briefing emphasis can differ.

### Main menu background slideshow

**Approved presentation exception:** a curated slideshow of original Backrooms scenes as the mod's main-menu backgrounds. Use the images to preview the range of play: the Async Industries facility and gate, the furniture-store breach, a field crew moving through a familiar room made wrong, evidence work and a safe return, a remote outpost, and deeper spaces or optional orbital support when those features are represented in the release. Include at least one image for each shipped scenario; add images for other systems as they become real in the build.

Keep each frame faithful to the experience the release actually contains. A concept image for a later feature must not imply that feature is playable. Compose a calm, low-detail area behind the menu controls, check the crop at supported aspect ratios and resolutions, and keep menu text readable over every image. Use slow fades or similarly quiet transitions; the slideshow must not rely on flashes, sudden movement, or audio. Provide a way to disable the mod's backgrounds and honor reduced-motion preferences.

Create the images specifically for Rimrooms. Do not use Kane Pixels or A24 frames, promotional stills, screenshots, or third-party mod assets. Broad mood and story cues may inform original compositions under the source rules above. Record the creator, source, license/permission, edits, and packaged path for every image in `provenance-register.csv`.

Before implementation, inspect RimWorld 1.6's public menu/background extension surface and the exact profile's menu-changing mods. Decide whether Rimrooms can safely add its images to the existing rotation or needs a scoped replacement while enabled. Do not overwrite or redistribute vanilla/DLC background files; preserve a clear fallback when Rimrooms backgrounds are disabled or unavailable.

### Staff, evidence, equipment, and entities

- Staff remain readable as RimWorld pawns first. Uniforms, protective gear, badges, radios, and work tools distinguish roles; do not make job eligibility depend on appearance.
- Evidence has a clear physical form or named record: tape, transcript, sample, photograph, route sketch, instrument reading, or case file. Mark ownership, condition, risk, and analysis status in text or symbols.
- Equipment should look like a repurposed company tool, salvage, or a named specialist device. Reuse visual grammar consistently so players can identify function and carry weight at normal game scale.
- Threats and anomalies use existing pawn/entity presentations and fair, distinguishable behavioral tells. Convey detection, danger, and counterplay through more than color or audio; keep specific movement and attack details in their own gameplay contracts.

## Color, light, and readability

Use restrained industrial neutrals for the facility and a slightly sickly warm fluorescent range for early Backrooms interiors. Save stronger colors for alarms, rare phenomena, and clearly labeled interactive equipment. Keep text, icons, outlines, and shape changes as redundant signals; never encode ownership, danger, or availability by color alone.

Fluorescent hum, dim patches, reflections, and isolated pools of light can carry mood. Avoid rapid full-screen flashes, essential strobe cues, or unannounced camera shake. Any intense effect needs a reduced-effect option that preserves the warning and gameplay consequence.

## Interface and text

Keep the vanilla RimWorld vocabulary and navigation recognizable. Add one company Operations view that connects people, facility, gate, expedition, evidence, contracts, and outposts; retain familiar vanilla tabs in the first playable version. Use concise labels, stable icons, plain-language states, and clear action/result/recovery text.

Critical alerts, radio traffic, mission objectives, gate states, route clues, and failures must remain in a readable log after temporary notifications disappear. Pair icons with names where an unfamiliar symbol could block a decision. Show missing prerequisites and consequences before commitment. Preserve keyboard navigation and hotkeys; validate multiple UI scales and long strings before release.

## Audio direction

Use a sparse sound bed: steady facility power, ventilation, distant machinery, intermittent radio static, footsteps, and carefully placed environmental changes. The gate can build a recognizable sequence from machine start to stable opening and recall. Use silence and changes in the room's ordinary hum more often than loud stingers.

Alarms, radio messages, and entity cues need a text or icon equivalent in the log or status panel. Let players lower or mute repeated ambience and reduce startling effects without losing objective, threat, or failure information. Do not require headphones or rapid sound recognition to complete an action.

## Existing-content bindings and presentation

There is no gameplay sprite, texture, item-icon or sound-production pipeline. For every role, record the provider package, exact existing Def, optional dependency, Core fallback and runtime use. Use native fonts, icons, graphics, lighting and sounds; text is the fallback when a suitable cue is unavailable. Preserve owner controls, native volume and optional mod presentation behavior.

Room families are arrangements of existing floors, walls, doors, furniture and lighting. Item identity and appearance stay with the original definition; Rimrooms associates functional/evidence roles through saved records. Production and analysis use existing installed benches. New recipes/jobs must consume and produce existing content and preserve native bills and Work priorities.

The historical 0.2.0 original PNG/WAV files are superseded for the finished gameplay package. Follow the [replacement map](../implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md) before removing them and their runtime references; preserve old source/provenance as history.

The owner confirmed original RimWorld-style Backrooms menu images as the visual exception. Keep 30-second dwell, two-second quiet fades, a reduced-motion still, native fallback, no audio and readability over the actual menu. Show the exact mod title and current build version beside native top-left version information using interface text, not baked image lettering. This exception does not permit new gameplay assets.

Use the company UI palette through existing interface drawing primitives and native fonts. Preserve redundant text and readable contrast. Inspect eventual in-game results at the owner's resolution and UI scale; source or compilation results do not establish presentation quality.

## Production and acceptance notes

- Select suitable existing provider content and inspect its actual behavior/readability at normal zoom after owner-launched testing is resumed.
- Record each provider/Def/version and fallback. Existing files remain in their owning game/mod packages; do not copy or rebundle them. Historical generated-asset provenance remains a historical record.
- Use keyed/localizable text from the first production pass. Check a long-string language, color-vision-safe status cues, keyboard navigation, reduced effects, and no-sound completion of the first expedition.
- Review every room family and threat against its gameplay contract: the player can recognize a clue, read a warning, identify an action, and find the recovery path.
- Final acceptance uses the [pre-production quality bar](PREPRODUCTION_ACCEPTANCE_STANDARD.md) and [content/accessibility brief](CONTENT_ACCESSIBILITY_BRIEF.md). This brief does not claim production assets exist or that their provenance has been cleared.
- The original main-menu slideshow is the approved visual exception. Test every image with the actual menu overlay at supported sizes, with reduced motion and no audio, and verify the chosen integration against menu-related mods in the pinned profile before advertising it as compatible.
