# RimWorld mod review: Vehicles Wrecks Expanded - Revisited

- Steam Workshop URL: https://steamcommunity.com/sharedfiles/filedetails/?id=3348827283
- Workshop ID: `3348827283`
- Package ID: `VehiclesWrecksExpanded.Revisited`
- Exact installed version/date: no local version declared; review checked 2026-09-27
- RimWorld build and DLC present: 1.6.4871 rev590; local supports 1.5–1.6; SHA-256 `59B45A39559C85824356760944F3FF2CD0E14B0A9682CF6901CC5D36F7F518BE`
- Load order: profile row 294; requires row 290 Vehicles Wrecks Expanded and loads after it
- Dependencies and incompatibilities stated by publisher: the page describes texture replacements and says it was made with the original author's permission. The page carries a removal notice without a reason.
- Source/package files reviewed: Workshop page and local package (matching wreck textures; no DLL or defs)

## Verified source facts

- This package retextures, recolors, converts or upscales row 290's wreck images; it does not implement new mechanics in the inspected local package.
- Permission to create the retexture is not, by itself, a redistribution license for Rimrooms. No explicit license was found.

## Rimrooms integration decision

- **Provisional:** optional appearance-only support; no direct integration and no bundling of these textures.
- Related systems: `RR-STYLE`, `RR-COMPAT`; see the [feature map](../../../FEATURE_TRACEABILITY.md).
- Keep row 290's mechanics independent of the appearance patch and preserve a vanilla visual fallback.

## Runtime evidence

- Runtime tests: pending; none run.
- Check texture precedence and readability with the selected load order, and verify the underlying wreck mechanics when this texture package is absent.
