# RimWorld mod review: Vanilla Expanded Framework

- Steam Workshop URL: https://steamcommunity.com/sharedfiles/filedetails/?id=2023507013
- Workshop ID: `2023507013`
- Package ID: `OskarPotocki.VanillaFactionsExpanded.Core`
- Review date: 2026-09-27; Workshop description and installed `About.xml` reviewed
- Installed version: `About.xml` does not state a mod version; it lists RimWorld 1.6 support.
- RimWorld target: `1.6.4871 rev590`
- Load order: profile row 14; local metadata requires Harmony and loads after the game and DLCs
- Dependencies/incompatibilities stated: Harmony required; local metadata lists `hatena.RangeAnimalFramework` as incompatible
- Source/package files reviewed: official Workshop description; installed `About.xml`

## Verified source facts

- VEF is a shared framework for Vanilla Expanded and other mods; the Workshop page says it is not a standalone content mod and is required by many related mods.
- The local selected Gravship Expanded chapters depend on VEF; their relationship and version requirements are tracked separately in the [gravship feasibility audit](../../RWT_AND_GRAVSHIP_FEASIBILITY.md).
- The exact services Rimrooms might call have not been selected or source-reviewed. No VEF code or assets are copied into Rimrooms.

## Rimrooms integration decision

- **Provisional disposition:** retain as a dependency of the selected Gravship Expanded chain; optional to the Core-only solo campaign. Do not add VEF as a separate Rimrooms dependency unless a concrete, tested feature needs it.
- Related systems: `RR-SPACEFLIGHT`, `RR-COMPAT`.
- Keep gravship content behind the chosen DLC/mod boundary and preserve a working gate-based campaign without it.

## Runtime evidence

- Clean VGE-only and full-profile Rimrooms tests: pending.
- Check the listed incompatibility against the selected profile during the complete dependency/conflict review.
