# RimWorld mod review: Vanilla Gravship Expanded - Chapter 2

- Steam Workshop URL: https://steamcommunity.com/sharedfiles/filedetails/?id=3799737423
- Workshop ID: `3799737423`
- Package ID: `vanillaexpanded.gravship2`
- Review date: 2026-09-27; publisher page, local `About.xml`, and `LoadFolders.xml` reviewed
- Installed version: local metadata has no `modVersion`; it lists RimWorld 1.6; `About.xml` SHA-256 `559658DC04E2891347122853990B48EACDD5E654A37AB2CE4D405B94F42560FA`
- RimWorld target: `1.6.4871 rev590`
- Load order: profile row 281; local metadata requires Harmony, Odyssey, Vanilla Expanded Framework, and Chapter 1
- Dependencies/incompatibilities stated: Workshop page requires Odyssey, Vanilla Expanded Framework, and Chapter 1. Local metadata declares `Bulldog.VanillaChemfuelExpandedOdysseyPatch` incompatible.
- Source/package files reviewed: current Workshop description and FAQ; local `About.xml` and `LoadFolders.xml`; no VGE code or assets are copied

## Verified source facts

- The publisher describes Chapter 2 as adding orbital threats and gravship defense/combat progression, including hostile gravships, bombardment, orbital clusters, weapons, armor, and salvage opportunities.
- The page supports RimWorld 1.6 and was updated 2026-09-20. It currently displays a Steam Community removal notice; no reason beyond the displayed notice is inferred here.
- The publisher says the chapter builds on its previous gravship overhaul and warns that mods changing gravships are likely incompatible unless specifically confirmed. Its stated license is CC BY-NC-ND 4.0; Rimrooms will not copy its code, text, or assets.
- The local `LoadFolders.xml` references no absent path. Its metadata-declared incompatibility target is not an active entry in the selected 294-mod inventory.

## Rimrooms integration decision

- **Provisional disposition:** optional Odyssey endgame integration, with Chapter 1 as a required dependency. Retain the base campaign without this combat expansion and without a gravship.
- Related systems: `RR-OUT`, `RR-SPACEFLIGHT`, `RR-THREAT`, `RR-COMPAT`.
- Keep Backrooms entities, gate states, and expeditions out of VGE's native gravship combat definitions. A later mission may use orbital travel as a separate company opportunity only after the selected profile and multiplayer behavior are tested.

## Runtime evidence

- The selected Chapter 1/Chapter 2 pair has not been tested in a clean profile, the complete 294-entry stack, or the RWT co-op profile.
- After Gate 0, confirm dependency order, orbital combat, ship damage/repair, salvage, save/load, interactions with selected vehicle/space mods, and any RWT visit/trade interactions before claiming compatibility.
