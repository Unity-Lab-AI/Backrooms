# Official game-layer review: RimWorld Core

- Official sources: https://rimworldgame.com/ and https://store.steampowered.com/app/294100/RimWorld/
- Review date: 2026-09-27; profile row 4
- Local package: `Ludeon.RimWorld`; pinned game build `1.6.4871 rev590`; no separate package version recorded
- Local metadata SHA-256: `62C5B721F0A562075A0109BA558AF22791D2B20B7A5E677592C1E7C138A21336`

## Official scope and Rimrooms use

Ludeon describes RimWorld as a colony/story simulation with pawn needs and psychology, construction, combat, trade, quests, factions and generated worlds. Ludeon's 1.6 release announcement describes 1.6 as a free base-game update, with Odyssey sold separately. Core is the solo campaign baseline and must support the complete facility, gate, expedition, evidence, contract and company loop. No third-party code or assets are being reused.

**Disposition:** required base-game target. Related features: `RR-SCEN`, `RR-FAC`, `RR-STA`, `RR-GATE`, `RR-EXP`, `RR-SPACE`, `RR-EVD`, `RR-MSN`, `RR-ECO`, `RR-OUT`, `RR-UI`, `RR-COMPAT`.

## Acceptance follow-up

No Rimrooms runtime implementation exists. Build and verify the full Core-only solo path before adding DLC-specific features. Every optional DLC route must have a working Core fallback and a clean absent-DLC save/start path.
