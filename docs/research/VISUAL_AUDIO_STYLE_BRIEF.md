# Rimrooms - Async Industries: visual and audio style brief

**Status:** pre-production direction for original Rimrooms content. This is a style contract, not finished art, sound, or a license clearance.

## Experience in one sentence

Make the company's spaces feel practical and inspectable, then let familiar rooms become quietly wrong in ways the player can notice, investigate, and survive.

## Reference and originality rules

- Use Kane Pixels' series as the primary source for broad moods and story cues: institutional research, procedural footage, fluorescent interiors, uncertain routes, missing crews, and incomplete returns. The [fan cliff notes](KANE_PIXELS_FAN_CLIFF_NOTES.md) are a quick index, not proof of every visual detail.
- Use the [separate A24 feature review](reviews/a24-feature/feature-review.md) only for its own store/Async branch and production notes. Do not collapse film events into the series timeline.
- Translate these references into original RimWorld-scale rooms, icons, dialogue, music/sound, props, and entities. Do not trace a frame, recreate a named character, or lift a third-party mod's asset. Broader community Backrooms designs are outside the current shipped-content scope.
- Label future entries as **source cue**, **interpretation**, or **original design** in the [provenance register](provenance-register.csv). A reference mention does not establish permission for a specific borrowed asset.

## Visual language

### Company facilities

Show a small organization making an improvised research site work: practical concrete, painted block, steel doors, wired glass, work lights, cable runs, labeled storage, paper notices, and patched equipment. Labs, security, staff rooms, cafeteria, power, loading, and machine spaces should be identifiable by their furniture and work purpose. A room's function must not depend on hidden score values.

Keep the company spaces brighter, more orderly, and more legible than the destinations. As money, equipment, and security improve, the base becomes better organized without turning into a generic futuristic command center.

### The machine gate

Make the gate read as an engineered installation that needs power, operators, clearance, and maintenance. Give its build, calibration, ready, opening, unstable, recall, cooldown, and damaged states distinct silhouettes, labels, lights, and interface text. Alarms and animation support those labels; the player must never need to infer a dangerous state from color or a brief flash alone.

### Backrooms destinations

Start with commonplace interiors and let one or two precise changes create unease: a doorway in the wrong place, a repeated corridor, an altered room dimension, a moved object, an exit that no longer matches the route, or a familiar space with a new obstruction. Tie room variations to a readable room family, coordinate clue, equipment tag, or logged anomaly. Avoid random visual clutter without a gameplay or story reason.

Increase variation gradually: institutional rooms and service corridors first; then deeper spaces combine known room families, altered connections, and occasional new rules. Preserve recognizable landmarks, route clues, and a return path. A rare distortion can surprise the player, but the UI and map record should explain what changed after the event.

### Scenarios

- **Async Industries:** a modest, functional research/security compound, an unfinished gate chamber, sparse starter stock, and a small crew with clear needs.
- **Furniture & Knickknack Store:** an ordinary public shop with recognizable retail stock and back-of-house space; the threshold and missing-person case introduce the abnormal layer without turning the whole shop into a horror set.
- **Lone Survivor:** a readable survival space with limited equipment, visible route clues, and immediate needs. The player should understand what can be used, what is unsafe, and what might lead to escape or rescue.

All three use the same icon grammar and status language, but their opening inventory, camera composition, and briefing emphasis can differ.

### Staff, evidence, equipment, and entities

- Staff remain readable as RimWorld pawns first. Uniforms, protective gear, badges, radios, and work tools distinguish roles; do not make job eligibility depend on appearance.
- Evidence has a clear physical form or named record: tape, transcript, sample, photograph, route sketch, instrument reading, or case file. Mark ownership, condition, risk, and analysis status in text or symbols.
- Equipment should look like a repurposed company tool, salvage, or a named specialist device. Reuse visual grammar consistently so players can identify function and carry weight at normal game scale.
- Threats and anomalies need original, distinguishable silhouettes and fair tells. Convey detection, danger, and counterplay through more than color or audio; keep specific movement and attack details in their own gameplay contracts.

## Color, light, and readability

Use restrained industrial neutrals for the facility and a slightly sickly warm fluorescent range for early Backrooms interiors. Save stronger colors for alarms, rare phenomena, and clearly labeled interactive equipment. Keep text, icons, outlines, and shape changes as redundant signals; never encode ownership, danger, or availability by color alone.

Fluorescent hum, dim patches, reflections, and isolated pools of light can carry mood. Avoid rapid full-screen flashes, essential strobe cues, or unannounced camera shake. Any intense effect needs a reduced-effect option that preserves the warning and gameplay consequence.

## Interface and text

Keep the vanilla RimWorld vocabulary and navigation recognizable. Add one company Operations view that connects people, facility, gate, expedition, evidence, contracts, and outposts; retain familiar vanilla tabs in the first playable version. Use concise labels, stable icons, plain-language states, and clear action/result/recovery text.

Critical alerts, radio traffic, mission objectives, gate states, route clues, and failures must remain in a readable log after temporary notifications disappear. Pair icons with names where an unfamiliar symbol could block a decision. Show missing prerequisites and consequences before commitment. Preserve keyboard navigation and hotkeys; validate multiple UI scales and long strings before release.

## Audio direction

Use a sparse sound bed: steady facility power, ventilation, distant machinery, intermittent radio static, footsteps, and carefully placed environmental changes. The gate can build a recognizable sequence from machine start to stable opening and recall. Use silence and changes in the room's ordinary hum more often than loud stingers.

Alarms, radio messages, and entity cues need a text or icon equivalent in the log or status panel. Let players lower or mute repeated ambience and reduce startling effects without losing objective, threat, or failure information. Do not require headphones or rapid sound recognition to complete an action.

## Production and acceptance notes

- Create original assets at the scale and contrast RimWorld needs; test them at normal zoom, not only in an enlarged editor view.
- Keep each asset's source, creator, license/permission, edits, and included-file path in `provenance-register.csv` before it enters a release build. Third-party mods remain dependencies or optional references; do not copy their files.
- Use keyed/localizable text from the first production pass. Check a long-string language, color-vision-safe status cues, keyboard navigation, reduced effects, and no-sound completion of the first expedition.
- Review every room family and threat against its gameplay contract: the player can recognize a clue, read a warning, identify an action, and find the recovery path.
- Final acceptance uses the [pre-production quality bar](PREPRODUCTION_ACCEPTANCE_STANDARD.md) and [content/accessibility brief](CONTENT_ACCESSIBILITY_BRIEF.md). This brief does not claim production assets exist or that their provenance has been cleared.
