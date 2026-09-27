# RimWorld Together and gravship feasibility audit

**Checked:** 2026-09-27  
**Scope:** local server/client profile comparison plus publisher/repository metadata. This is a research audit, not an in-game compatibility test.

## Local profile comparison

The local server file `C:\Users\gfour\Desktop\RimWorld Server\Server-win-x64-new\Configs\ModConfig.json` contains **294** mod records. The local client file `C:\Users\gfour\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml` contains **294** active package IDs.

All **288** Workshop-backed entries in the active client list were mapped through the locally installed Workshop `About/About.xml` files. The other six entries are RimWorld Core and the five DLCs. Comparing mapped Workshop IDs plus Core/DLC records produced **294/294 matching IDs, zero missing entries, zero client-only entries, and zero load-order position differences** against the server profile export on this date.

That establishes that the current client and server profile snapshots agree. It does not establish that Rimrooms works in the profile, that a second client will stay aligned, or that RWT is enforcing the profile.

The server config reports `AllowAllMods=true`, `EnforceSettings=false`, and a null `ModOrder`. Its `ModConfigs` array has 294 records. Therefore the profile is currently installed consistently by observation, but the server configuration does not force the settings or order; an administrator can still allow drift. The current client does have RWT active as package ID `nova.rimworldtogether`, Workshop ID `3005289691`, with local `About.xml` supporting RimWorld 1.5 and 1.6.

## RWT build identity and documented boundary

The local server executable reports product version `1.0.0+a7bc029472d727faec4e99b7f02614c370f4771a`. The official upstream release listing identifies **26.8.31.1**, commit `bbd981f`, as the latest published release in this audit. The local build hash does not match that release commit, and the installed client `About.xml` contains no RWT release tag. Do not label the local stack as 26.8.31.1 or infer its feature/API surface from that release until the server build is identified.

The RWT Workshop description says players share a planet while keeping separate colonies and pacing, and lists visiting, raiding, spying, trading, faction/guild creation, roads, and site building. The 26.8.31.1 release notes add full planet river synchronization and Odyssey asteroid compatibility. Release 26.8.9.1 introduced server-side mod-config and mod-order enforcement, but those controls are not enabled in this local server configuration.

**Design boundary:** each Rimrooms branch owns its own company ledger, research state, discovered coordinates, and local facility/maps. Use supported RWT world actions and transfers as the cross-branch boundary. A transferable Research Dossier is a design proposal only; custom Thing transfer, reliable receipts, multiplayer save behavior, and any server-side extension point still need code inspection and a disposable-save test. Do not build a shared research ledger against an undocumented API.

RWT's public wiki endpoints returned HTTP 403 during this audit. Use the linked official Steam page and upstream GitHub release/source as available evidence, then verify detailed visit, aid, item-transfer, and configuration behavior in the pinned build. The user-facing co-op goal does not imply live shared-map pawn control; explicitly test whether each desired visit is a snapshot activity, remote activity, or any form of live interaction before designing around it.

## Gravship chapters in the exact profile

The profile contains both selected chapters, with Odyssey and Vanilla Expanded Framework earlier in the recorded order:

| Load order | Mod | Workshop ID | Verified dependency / feature note |
| ---: | --- | --- | --- |
| 247 | Vanilla Gravship Expanded - Chapter 1 | `3609835606` | Workshop page requires Odyssey and Vanilla Expanded Framework. It overhauls gravships around oxygen, fuel, power, heat, crew, and self-sustaining orbital operations. |
| 281 | Vanilla Gravship Expanded - Chapter 2 | `3799737423` | Workshop page requires Odyssey, Vanilla Expanded Framework, and Chapter 1. It adds orbital threat detection, ship combat/defenses, salvage, and hostile orbital sites. |

Both Workshop pages warn that other mods altering gravships are likely incompatible. Both list CC BY-NC-ND 4.0; use these installed mods as optional integrations and do not redistribute their code, assets, or copied content.

The profile has a broad vehicle/space set that still needs individual page/source inspection: Vehicle Framework; Carryalls; More Crashed Ship Parts; Trade Ships Drop Spot; Trade Ships No Matter What; Vanilla Vehicles Expanded and its Tier 3/Upgrades modules; Various Space Ship Chunk; Alpha Vehicles - Age of Sail; Vehicles Wrecks Expanded and Revisited; and both gravship chapters. The exact known conflict FriendFlyTogether is **not** in the current 294-entry profile. Its absence does not certify the remaining vehicle/space mods as compatible.

## Recommended integration shape

1. Keep the Backrooms gate, room graph, coordinate persistence, expeditions, and company progression native to Rimrooms. VGE is not the foundation of the gate.
2. Add an Odyssey-guarded, optional bridge that turns the gravship chapters into late-game off-world logistics, orbital reconnaissance, or defense content only where a specific public extension point permits it.
3. Make every integration fail safely when either VGE chapter, Odyssey, VEF, or another optional dependency is absent. Do not hard-reference VGE defs/types from the base assembly.
4. First test Core + Harmony + VEF + Odyssey + VGE Chapter 1 + Chapter 2; then add the profile's vehicle/space mods one family at a time. Record any confirmed incompatibility and keep it visible in the compatibility report.
5. For multiplayer, join with two clients, transfer vanilla and custom cargo, visit/raid where enabled, reconnect during/after transfers, and confirm duplicate or failed transactions cannot create/loss-duplicate items. This remains a required future test, not a completed result.

## Source links

- [RimWorld Together Workshop page](https://steamcommunity.com/sharedfiles/filedetails/?id=3005289691)
- [RimWorld Together upstream repository](https://github.com/RimWorld-Together/Rimworld-Together)
- [RimWorld Together latest release](https://github.com/RimWorld-Together/Rimworld-Together/releases/tag/26.8.31.1)
- [Vanilla Gravship Expanded - Chapter 1](https://steamcommunity.com/sharedfiles/filedetails/?id=3609835606)
- [Vanilla Gravship Expanded - Chapter 2](https://steamcommunity.com/sharedfiles/filedetails/?id=3799737423)
- [Vanilla Expanded Framework](https://steamcommunity.com/sharedfiles/filedetails/?id=2023507013)
