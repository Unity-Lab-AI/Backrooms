# RimWorld mod review: [FSF] FrozenSnowFox Tweaks

- Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=2893432492
- Row 284; local package `FrozenSnowFox.FrozenSnowFoxTweaks`.
- Version blank; supports RimWorld 1.4–1.6; XML Extensions required. Local metadata has 124 LoadAfter declarations, 17 for selected packages (including Adaptive Primitive Storage, Common Sense, Medical IVs Fork, Dubs Rimkit, Animals Logic, Vanilla Vehicles Expanded, ReBuild: Doors and Corners, Oops All Gene Banks, Vehicle Framework, Packs Are Not Belts, Vanilla Apparel Expanded packages, and VWE Non-Lethal). Fourteen declared conflicts are FrozenSnowFox standalone packages, none selected.
- Reviewed 2026-09-27 using the dated local metadata snapshot for RimWorld 1.6.4871 rev590. No in-game or multiplayer test was run.

## Source facts

Publisher describes a configurable XML Extensions tweak collection, disabled by default, and advises loading near the end and checking duplicates. Examples include turret rearming, bed rest, utility layers, learning speed, improvised weapons, and fleeing; examples are not proof each is active.

**License and reuse:** CC BY 3.0 applies to the icon only; no general code/content license verified.

No public API or code hook is assumed from this source review. See the publisher/package sources before any future patch work.

## Rimrooms use

- **Disposition:** Provisional: optional configurable tweaks; no Rimrooms dependency.
- **Provisional feature mapping:** `RR-STA; RR-THREAT; RR-FAC; RR-COMPAT`.
- **Follow-up check:** Check only enabled overlaps against Rimrooms systems, especially turrets/security, bed rest, utility apparel, training, weapons/salvage and fleeing.
- Keep this profile mod optional; preserve the Core-only campaign path. Do not copy or bundle third-party code or assets.

## Evidence status

Publisher page and local metadata recorded; disabled-by-default is a publisher claim; no runtime test.

Source review records publisher/local facts and design implications only. It does not certify compatibility with the full profile, RimWorld Together, DLC, or other mods.
