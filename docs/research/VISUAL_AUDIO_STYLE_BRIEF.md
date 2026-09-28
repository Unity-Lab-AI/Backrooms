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

### Main menu background slideshow

Ship a curated slideshow of original Backrooms scenes as the mod's main-menu backgrounds. Use the images to preview the range of play: the Async Industries facility and gate, the furniture-store breach, a field crew moving through a familiar room made wrong, evidence work and a safe return, a remote outpost, and deeper spaces or optional orbital support when those features are represented in the release. Include at least one image for each shipped scenario; add images for other systems as they become real in the build.

Keep each frame faithful to the experience the release actually contains. A concept image for a later feature must not imply that feature is playable. Compose a calm, low-detail area behind the menu controls, check the crop at supported aspect ratios and resolutions, and keep menu text readable over every image. Use slow fades or similarly quiet transitions; the slideshow must not rely on flashes, sudden movement, or audio. Provide a way to disable the mod's backgrounds and honor reduced-motion preferences.

Create the images specifically for Rimrooms. Do not use Kane Pixels or A24 frames, promotional stills, screenshots, or third-party mod assets. Broad mood and story cues may inform original compositions under the source rules above. Record the creator, source, license/permission, edits, and packaged path for every image in `provenance-register.csv`.

Before implementation, inspect RimWorld 1.6's public menu/background extension surface and the exact profile's menu-changing mods. Decide whether Rimrooms can safely add its images to the existing rotation or needs a scoped replacement while enabled. Do not overwrite or redistribute vanilla/DLC background files; preserve a clear fallback when Rimrooms backgrounds are disabled or unavailable.

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

## Production file specification

These are original-art production defaults for the planned campaign. The [0.2.0 build record](../implementation/PHASE_2_BUILD_RECORD.md) links the actual original equipment/entity sprites, carpet material, short audio cues and provenance. Their native-resolution development exports have not yet passed in-game presentation acceptance. Change a default when the actual game view demonstrates a better result, and record the reason with the asset.

| Asset family | Working/export specification | Readability and ownership |
| --- | --- | --- |
| Package preview | 960 × 540 opaque PNG, sRGB; original title/identity composition | Title readable at a 320-pixel-wide thumbnail; identify foundation builds as such; no implied gameplay screenshot |
| Menu backgrounds | 3840 × 2160 original master, 1920 × 1080 shipped PNG initially; no embedded menu text | Reserve a quiet middle-left area for the actual native menu; check 16:9, 16:10 and 21:9 crops and 1280 × 720 minimum before release; exact safe area follows source inspection and overlay evidence |
| UI icons | 64 × 64 RGBA PNG on a 64-pixel grid; detail within a 52-pixel safe region; retain 256 × 256 source | Recognizable at 24–32 displayed pixels; distinct outline and paired text, never color alone |
| Items and equipment | 128 × 128 RGBA export, up to 256 × 256 for detailed/large items | Match native item scale, silhouette and ground shadow; equipment must read at normal map zoom |
| Buildings and room props | Start at 128 pixels per occupied tile; cap a single initial texture at 1024 × 1024 | Author needed facing variants deliberately; match footprint/interaction cells and avoid baking UI labels into sprites |
| Pawns/entities | Original 256 × 256 directional masters with RimWorld-scale export chosen per body/overlay use | Distinct threat silhouette; fair pose/animation tells linked to the threat contract |
| Short sound effects | 48 kHz WAV masters, mono PCM 16-bit exports unless spatial design needs stereo | Aim for peaks at or below −3 dBFS; trim clicks and use short edge fades; calibrate Def volume in game |
| Ambient loops/music | 48 kHz stereo masters; OGG exports, restrained dynamics, seamless loops where needed | Initial ambience mix target around −24 LUFS integrated; radio around −20 LUFS; true peaks below −3 dBTP; production targets, not measured game loudness |

Use source names such as `RR_<Family>_<Purpose>_<FacingOrVariant>` and stable extensionless runtime paths. Editable source and mix masters stay outside `Mod/`. Each shipped output has its own provenance entry and a source-generation/edit trail. Do not add unused assets just to fill directories.

The foundation identity palette is charcoal `#141A1D`, deep shadow `#080D10`, steel `#263135`, warm paper `#EEE8D5`, muted grey `#A8B0AD`, and amber `#D3B46C`. Later status colors add red/green only with text, shape and an icon. UI text should meet a 4.5:1 contrast target and essential large symbols 3:1 against their actual backgrounds; check screenshots after game lighting/overlays. Use native UI fonts for game controls. The preview uses system Arial during rendering and bundles no font.

Start the menu rotation at 30 seconds per image with a 2-second quiet crossfade. Reduced motion holds one image until user selection; disabling Rimrooms backgrounds restores the game's normal path. No flashes, sudden camera travel or menu audio stingers. These settings are planned behavior, pending the menu API/profile review, not features of the package preview. Gate/anomaly animation must retain static status labels when motion is reduced. Limit repeated alarms and allow ambience/stingers to be muted independently where the inspected sound API permits; native volume controls remain functional.

Record export dimensions, format, measured audio peak/loudness where applicable, creator/license, packaged path and actual visual/audio review per asset. Readability, UI scaling, directional rendering, sound balance and menu crops remain owner-launched acceptance after those assets are implemented.

## Production and acceptance notes

- Create original assets at the scale and contrast RimWorld needs; test them at normal zoom, not only in an enlarged editor view.
- Keep each asset's source, creator, license/permission, edits, and included-file path in `provenance-register.csv` before it enters a release build. Third-party mods remain dependencies or optional references; do not copy their files.
- Use keyed/localizable text from the first production pass. Check a long-string language, color-vision-safe status cues, keyboard navigation, reduced effects, and no-sound completion of the first expedition.
- Review every room family and threat against its gameplay contract: the player can recognize a clue, read a warning, identify an action, and find the recovery path.
- Final acceptance uses the [pre-production quality bar](PREPRODUCTION_ACCEPTANCE_STANDARD.md) and [content/accessibility brief](CONTENT_ACCESSIBILITY_BRIEF.md). This brief does not claim production assets exist or that their provenance has been cleared.
- The main-menu slideshow is part of the release asset set. Test every image with the actual menu overlay at supported sizes, with reduced motion and no audio, and verify the chosen integration against menu-related mods in the pinned profile before advertising it as compatible.
