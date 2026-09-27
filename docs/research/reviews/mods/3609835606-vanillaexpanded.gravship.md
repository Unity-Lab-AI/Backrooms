# RimWorld mod review: Vanilla Gravship Expanded - Chapter 1

- Steam Workshop URL: https://steamcommunity.com/sharedfiles/filedetails/?id=3609835606
- Workshop ID: `3609835606`
- Package ID: `vanillaexpanded.gravship`
- Review date: 2026-09-27; publisher page, local `About.xml`, and `LoadFolders.xml` reviewed
- Installed version: local metadata has no `modVersion`; it lists RimWorld 1.6; `About.xml` SHA-256 `483A2F11DFB86FA060C65DA7184B7D08228C02B34B60CC57C3EDCE5B924A6A1A`
- RimWorld target: `1.6.4871 rev590`
- Load order: profile row 247; local metadata requires Harmony, Odyssey, and Vanilla Expanded Framework
- Dependencies/incompatibilities stated: Workshop page requires Odyssey and Vanilla Expanded Framework. Local metadata additionally records Harmony and declares `Bulldog.VanillaChemfuelExpandedOdysseyPatch` incompatible.
- Source/package files reviewed: current Workshop description and FAQ; local `About.xml` and `LoadFolders.xml`; no VGE code or assets are copied

## Verified source facts

- The publisher describes this as a full gravship overhaul focused on oxygen, fuel, power, heat, and crew systems that support an ongoing orbital gravship.
- The page supports RimWorld 1.6 and was updated 2026-09-17. The page currently displays a Steam Community removal notice; no reason beyond the displayed notice is inferred here.
- The publisher warns that other mods changing gravships are likely incompatible and recommends checking any additional gravship-mod combinations. Its stated license is CC BY-NC-ND 4.0; Rimrooms will not copy its code, text, or assets.
- The local `LoadFolders.xml` references no absent path. Its metadata-declared incompatibility target is not an active entry in the selected 294-mod inventory.

## Rimrooms integration decision

- **Provisional disposition:** optional late-game Odyssey integration only. Keep the Core campaign, company gate, expeditions, and room progression playable without Odyssey, VEF, Harmony, or either gravship chapter.
- Related systems: `RR-OUT`, `RR-SPACEFLIGHT`, `RR-COMPAT`.
- Preserve the native gravship and its progression. Keep the Backrooms gate as an independent system; do not patch Chapter 1's gravship definitions or require orbital travel to use the Backrooms.

## Runtime evidence

- A clean Odyssey + Harmony + VEF + Chapter 1 profile has not been tested for this project. Neither has the complete 294-entry stack or the RWT multiplayer combination.
- After Gate 0, confirm construction, oxygen/pressure, power/fuel, travel, save/load, and the interaction with Chapter 2 and selected vehicle/space mods before claiming this integration works.
