# Main-menu background extension audit

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Audit date:** 2026-09-27
**Scope:** RimWorld 1.6 title/menu background selection, available native extension evidence, and menu/UI/audio mods in the captured 294-entry profile. This is a source audit, not an in-game compatibility result. No mod code or assets were created.

## Finding

The installed RimWorld 1.6 assembly contains a plausible self-contained data extension for still menu backgrounds: an `ExpansionDef` with a mod-owned `backgroundPath` and the active Rimrooms package as `linkedMod` is eligible for the native **random background selection**, based on the inspected 1.6 code path. This is an inference from the installed assembly and should be verified with a disposable clean profile before it is treated as a supported integration.

The native random selection chooses one active expansion background when `MainMenuDrawer.Init` runs. The inspected path does not implement a timed slideshow during one menu visit. The requested automatic slideshow therefore remains a design/runtime lead: it needs a tested Rimrooms-owned rotation controller, or an optional integration with a background framework such as Vanilla Backgrounds Expanded. Do not make that framework required based on this audit; it is absent from the captured profile and is not needed to prove the native still-image path.

## Official 1.6 documentation reviewed

- [Ludeon: Announcing Odyssey and update 1.6](https://ludeon.com/blog/2025/06/announcing-odyssey-and-update-1-6/) links the [official 1.6 Modder Primer](https://docs.google.com/document/d/e/2PACX-1vRKE9u5ZW_zG45pxzwNvy4sxvozDeqtxlxpac5jwenOeW6liQCPgmPl9bIbtcMuqL1NPIDHOLFg64M_/pub). The primer documents 1.6 technical changes and asset formats, but does not document a timed title-screen background API or a menu slideshow contract. That absence is a documentation gap, not proof that no extension is possible.
- The installed official file `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\ModUpdating.txt` documents the supported mod folder structure and `Textures/` content. It does not describe a title-screen slideshow API.
- No official 1.6 publication found in this audit promises that arbitrary third-party expansion definitions are a stable public menu API. The native behavior below was checked against the installed game files and CLR metadata/IL, not inferred from the primer.

## Installed game and native evidence

### Version and profile identifiers

The installed `Version.txt` and the global `ModsConfig.xml` both report **RimWorld 1.6.4871 rev590**. The captured `ModsConfig.xml` contains **294 active entries**. The installed `Assembly-CSharp.dll` has CLR assembly version **1.6.9676.17735**; treat that as a separate assembly identifier, not a replacement for the public game build number.

Two disposable startup-smoke logs captured on 2026-09-27 report **RimWorld 1.6.4871 rev591**, while the installed `Version.txt` and global `ModsConfig.xml` report rev590. Their hashes, profiles, and limits are recorded in the [runtime-smoke report](runtime-evidence/RWT_AND_FULL_PROFILE_STARTUP_2026-09-27.md). Rev590 versus rev591 remains unresolved as a test-record question. Do not infer an installation fault from these identifiers alone.

### What the installed 1.6 files show

The inspected files are from the local Windows installation. `Assembly-CSharp.dll` metadata reports version 1.6.9676.17735.

| Local source | Observed evidence | Evidence type |
|---|---|---|
| `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\Misc\ExpansionDefs\ExpansionDefs.xml` | Core and each installed DLC `ExpansionDef` declares a `backgroundPath` such as `UI/HeroArt/BGPlanet`, `MenuBG_Royalty`, `MenuBG_Ideology`, `MenuBG_Biotech`, `MenuBG_Anomaly`, and `MenuBG_Odyssey`. | Installed official XML |
| `...\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`, type `RimWorld.ExpansionDef` | Reflection reports public fields `backgroundPath` and `linkedMod`, plus public `BackgroundImage`. Its getter loads the texture through `ContentFinder<Texture2D>.Get(backgroundPath, true)`. `Status` returns Active when `ModLister.IsActive(linkedMod)` succeeds. | Installed assembly reflection/IL |
| Same assembly, `RimWorld.MainMenuDrawer.Init` | When `Prefs.RandomBackgroundImage` is true, it filters the expansion list to `Status.Active`, chooses one random `ExpansionDef`, and assigns its `BackgroundImage` to `UI_BackgroundMain.overrideBGImage`. Otherwise it uses `Prefs.BackgroundImageExpansion`. It then initializes the background fade data. | Installed assembly IL |
| Same assembly, `RimWorld.UI_BackgroundMain.SetupExpansionFadeData` | Initializes an entry for each expansion definition. `BackgroundOnGUI` draws the override image, or the private static readonly `BGPlanet` fallback, then the menu overlay. | Installed assembly reflection/IL |
| Same assembly, `RimWorld.MainMenuDrawer.DoExpansionIcons` | Iterates expansion definitions and omits entries marked `isCore` from the expansion-icon row. Hovering an icon calls `UI_BackgroundMain.Notify_Hovered` for that definition. | Installed assembly IL |
| `C:\Users\gfour\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Prefs.xml` | Current saved preferences are 3840×2160, UI scale 2, `randomBackground=False`, and `backgroundExpansionId IsNull=True`. This records the current preference state, not a test result. | Installed preference file |
| `...\Data\Core\Languages\English\Keyed\Menu_Options.xml` | Contains the vanilla `SetBackgroundImage` label, displayed as “Menu background.” | Installed official keyed text |

**Implementation inference:** a Rimrooms `ExpansionDef` that points `linkedMod` to `UnityLabAI.RimroomsAsyncIndustries` and points `backgroundPath` to a unique, Rimrooms-owned texture should be eligible for vanilla's random background picker while Rimrooms is active. If it is not marked `isCore`, the inspected menu code will also consider it for an expansion icon. That extra icon may be useful branding, but its icon, hover state, details panel, and `isCore` behavior need an in-game decision and test. Do not mark the definition as Core merely to hide its icon without testing the side effects.

The native picker is not itself a timed slideshow: it selects during menu initialization, while the visible expansion icons provide a hover-driven background change. A timer-driven rotation, transition timing, and disable/fallback setting remain unverified work. The private vanilla `BGPlanet` should remain a fallback; no vanilla or DLC file needs to be replaced or redistributed.

## Exact profile menu, UI, and audio review

The captured profile is `C:\Users\gfour\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`; the repository snapshot is `docs/research/installed-mod-metadata-2026-09-27.csv`. Row numbers below refer to that CSV. Local copies are under `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\<Workshop ID>\`.

| Row / mod | Captured local version | Menu-related evidence and boundary |
|---|---|---|
| 3 — Loading Progress | 0.16.0; has a `1.6` folder | Its `About.xml` describes a detailed startup-progress window. Its installed DLL contains `MainMenuDrawer` references, but this string-level scan does not establish a background-provider feature. Test startup/menu transition with it present and absent. |
| 13 — HugsLib | About description says 12.0.0; has a `v1.6` folder | Installed `v1.6/Assemblies/HugsLib.xml` documents `MainMenuDrawer_Quickstart_Patch` as rewiring the developer quicktest button. This is a menu-control interaction, not a background source. |
| 64 — Character Editor | About metadata says 1.6.1; description text says v1.6.3 build for game 1.6.4523; has a `v1.6` folder | Its installed 1.6 assembly contains `MainMenuDrawer` and `MainMenuOnGUI` references. The exact overlay behavior was not reverse-engineered; confirm button placement and text/image layering in the runtime profile. |
| 74 — Ding On Game Loaded | 1.6.1 | The local `About.xml` says it plays a ding when loading reaches the main menu, with alternate sounds for loading warnings/errors. Its 1.6 assembly references `MainMenuDrawer.MainMenuOnGUI`. It is an audio/timing interaction, not a background provider. Test with muted/no-audio settings and on loading errors. |
| 81 — Dubs Mint Menus | 1.3.1247 | Its local `About.xml` describes recipe, health, plant, architect, research, and designator list UIs. No title-background provider is documented or identified in the targeted file scan. |
| 196 — RimWorld Together | local metadata has a `v1.6` folder | The installed `1.6/Assemblies/RTClient.dll` contains main-menu references. Exact UI surface was not decompiled in this audit. Test connection/menu controls with the slideshow and verify solo fallback; this audit does not assert RWT compatibility. |
| 203 — Shit Rimworld Says (Continued) | 1.6.1 | The installed 1.6 assembly contains a `MainMenuDrawer.MainMenuOnGui` patch name and a `TipsOnMainMenu` setting. Its About page focuses on loading-screen tips. Treat main-menu text overlay as a legibility test lead, not a proven conflict. |
| 204 — Show Me Your Hands | 1.6.10; has a `1.6` folder | Its installed 1.6 assembly contains a `MainMenuDrawer.MainMenuOnGUI` reference. The exact effect on the main menu was not established; include it in the overlay pass. |

The profile inventory has no active `Vanilla Backgrounds Expanded` (`vanillaexpanded.backgrounds`) or `RimThemes` provider. These mods are not established dependencies of the current 294-entry profile. Dubs Mint Menus, Loading Progress, HugsLib, and the other UI/audio leads above do not by themselves prove that a third-party slideshow exists in this profile.

## External extension example (not installed)

[Vanilla Backgrounds Expanded, Workshop item 2775017012](https://steamcommunity.com/sharedfiles/filedetails/?id=2775017012) advertises 1.6 support, adjustable background cycling/duration, and automatic inclusion of mod-authored `BackgroundDef` entries in its options. Its public [1.6 repository folder](https://github.com/Vanilla-Expanded/VanillaBackgroundsExpanded/tree/main/1.6) contains separate 1.6 definitions and source. This is a useful compatibility research lead, not an official RimWorld API and not part of the exact profile. The Workshop page states that its background images are CC BY-NC-ND 4.0; do not reuse or redistribute those images. If supported optionally later, test the publisher's current implementation rather than assuming this contract is stable.

## Tests still required before closing this lead

Use one reconciled 1.6 build identity and a disposable copy of the exact 294-entry list. Capture the launched game version/log and resolve the rev590/rev591 difference as a test-record question.

1. With all DLC disabled, load Core + Harmony + RimWorld Together and the candidate Rimrooms menu background path. Confirm the authored background loads, fallback works, and the title menu remains usable. Repeat with each DLC profile as selected by the support matrix.
2. Test both vanilla preference branches: fixed background and random background. Prove whether a Rimrooms `ExpansionDef` appears in random selection with Rimrooms active and is absent/falls back cleanly when disabled or missing its image.
3. Confirm whether the custom `ExpansionDef` adds an expansion icon/details surface, and determine a supported icon strategy. Test mouse-hover fades, menu transitions, returning from a save, and restart persistence.
4. Exercise the actual rotation the player asked for. If one image is selected per menu initialization, implement/test a timed transition before calling it a slideshow. Verify disable setting and missing-asset fallback.
5. Repeat with Loading Progress, HugsLib, Character Editor, Ding On Game Loaded, Dubs Mint Menus, RimWorld Together, Shit Rimworld Says, and Show Me Your Hands present/absent as applicable. Check 3840×2160 at UI scale 2, narrower/wider ratios, crops, title/menu readability, reduced motion, and no-audio operation.
6. Keep one original, release-accurate scene per shipped scenario and add more only when those systems ship. Follow [the visual/audio style brief](VISUAL_AUDIO_STYLE_BRIEF.md): original art, safe control-area composition, quiet fades, no sound dependency, reduced-motion support, and no implication that unreleased features are playable.

## Status safe to record

The pre-code **source inspection** lead is complete with this report as evidence: the local 1.6 data/assembly path has been traced, exact-profile menu/UI/audio leads have been enumerated, and a bounded native/optional-framework direction is documented. Keep **runtime integration, the timed-slideshow implementation choice, version-log pin, visual fallback/accessibility, and profile-interaction checks** for later implementation and acceptance. This report alone does not establish compatibility or finish any art; its assigned source-review work is included in the completed Gate 0 documentation/source pass.
