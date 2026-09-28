# RimWorld mod review: Change map edge limit

- Steam Workshop URL: https://steamcommunity.com/sharedfiles/filedetails/?id=1546494565
- Public source/release: https://github.com/KapitanOczywisty/ChangeMapEdge/releases
- Workshop ID: `1546494565`
- Package ID: `kapitanoczywisty.changemapedge`
- Exact installed version/date: local 1.6 folder; upstream v1.0.9; review checked 2026-09-27
- RimWorld build and DLC present: 1.6.4871 rev590; local metadata has no semantic modVersion
- Load order: profile row 63; Harmony required and this mod loads after Harmony; no HugsLib requirement in the 1.6 metadata
- Dependencies and incompatibilities stated by publisher: Workshop description still mentions Harmony and HugsLib; its v1.0.9 release says HugsLib was removed for RimWorld 1.6. The publisher says to leave an outer edge tile for visitors and not to use the option for perimeter walls.
- Source/package files reviewed: Workshop page, upstream release/repository and local 1.6 metadata

## Verified source facts

- The mod changes the placement exclusion distance for buildings, blueprints, and zones. The publisher says the default limit is zero and cautions that removing the mod is safest after blueprints near the edge are removed.
- The 1.6 local dependency list matches the upstream release: Harmony only, loaded after Harmony.
- No license declaration was found in the inspected page or repository. Do not copy its code or assets.
- The publisher does not describe this as a map-size, edge-arrival, or perimeter-defense feature.

## Rimrooms integration decision

- **Provisional:** optional configuration convenience; no Rimrooms adapter planned.
- Related systems: `RR-FAC`, `RR-OUT`, `RR-COMPAT`; see the [feature map](../../../FEATURE_TRACEABILITY.md).
- It changes build placement near the edge, not map dimensions or travel. Keep vanilla placement rules as the fallback and do not make perimeter defense depend on it.

## Runtime evidence

- Test profile/order and logs: pending.
- Runtime tests: none.
- Re-test trigger: try near-edge structure, blueprint and zone placement; check visitor/trader entry, raids, caravans and pod arrivals with one boundary tile left open; then run the exact RWT profile.
