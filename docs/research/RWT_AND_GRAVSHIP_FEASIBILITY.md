# RimWorld Together and gravship feasibility audit

**Checked:** 2026-09-27  
**Scope:** local server/client profile comparison plus publisher/repository metadata. This is a research audit, not an in-game compatibility test.

## Local profile comparison

The local server file `C:\Users\gfour\Desktop\RimWorld Server\Server-win-x64-new\Configs\ModConfig.json` contains **294** mod records. The local client file `C:\Users\gfour\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml` contains **294** active package IDs.

All **288** Workshop-backed entries in the active client list were mapped through the locally installed Workshop `About/About.xml` files. The other six entries are RimWorld Core and the five DLCs. Comparing mapped Workshop IDs plus Core/DLC records produced **294/294 matching IDs, zero missing entries, zero client-only entries, and zero load-order position differences** against the server profile export on this date.

That establishes that the current client and server profile snapshots agree. It does not establish that Rimrooms works in the profile, that a second client will stay aligned, or that RWT is enforcing the profile.

The server config reports `AllowAllMods=true`, `EnforceSettings=false`, and a null `ModOrder`. Its `ModConfigs` array has 294 records. Therefore the profile is currently installed consistently by observation, but the server configuration does not force the settings or order; an administrator can still allow drift. The current client does have RWT active as package ID `nova.rimworldtogether`, Workshop ID `3005289691`, with local `About.xml` supporting RimWorld 1.5 and 1.6.

## Pinned local RimWorld test target

The installed game's `Version.txt` reads **1.6.4871 rev590** and Steam's local app manifest records build ID `23969874`. The managed `Assembly-CSharp.dll` reports version `1.6.9676.17735`. These identify the local pre-build test target; they do not claim every player's game is on this build. The local client `ModsConfig.xml` and server `ModConfig.json` SHA-256 digests are recorded below so the exact 294-entry profile snapshot can be reproduced without publishing its settings.

| Target artifact | Observed identity | SHA-256 / evidence |
| --- | --- | --- |
| RimWorld game version file | `1.6.4871 rev590` | `0EC56B267649FAA48E8CD6BD767B14BAFE3D1359AF44434711105DBDC4597BE3` |
| Steam RimWorld app manifest | Build ID `23969874` | Local `appmanifest_294100.acf` |
| Core game assembly | `Assembly-CSharp.dll`, version `1.6.9676.17735` | `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A` |
| Harmony mod metadata | `2.4.2.0`, package `brrainz.harmony`, Workshop ID `2009463077` | Local `About.xml`; declares RimWorld 1.6 support |
| Harmony active assembly | `0Harmony.dll`, product `2.4.1.0+789df191bbaf6610232d50e7ef7dddc0d2812549` | `353DAAFEC180BB8E7BBE4DA78F2A7CDC78067392E3A4E79DC8E7AF295F2371E6` |
| Client mod profile | `ModsConfig.xml` | `D80C797B6DC41B0D8C44F5E0BAA28E9670656E36637D7E16885680DDDA0F38B1` |
| Server mod profile | `ModConfig.json` | `1C1139569B469789B8586902FBDC99DEFE8DF91249A391B615F6198A990FA0CE` |
| RWT client assembly | `RTClient.dll`, product `1.0.0+a7bc029472d727faec4e99b7f02614c370f4771a` | `CDCEC1060B7EBC9181B2457E3C1220AFB224EC755351C44C61851B8FF1BB9919` |
| RWT server archive | `26.8.31.1` Windows x64 release asset | `F16C703F1E3E4E6DE0F4877D8AE502A817C85482681956AA01E8A4B619BAB68C`; exact match to official release-page digest |
| RWT server executable | `RTServer.exe`, product `1.0.0+a7bc029472d727faec4e99b7f02614c370f4771a` | `939FE9A83434D31C543B3C486ED3398C6498AE9A9A609F8296E73C84CD5B7CC6` |

## RWT build identity and documented boundary

The local `Server-win-x64-new.zip` SHA-256 is `F16C703F1E3E4E6DE0F4877D8AE502A817C85482681956AA01E8A4B619BAB68C`. This exactly matches the `Server-win-x64.zip` digest published on the official **26.8.31.1** release page, so the Windows server artifact is pinned to that release. Its `RTServer.exe` reports product version `1.0.0+a7bc029472d727faec4e99b7f02614c370f4771a` and SHA-256 `939FE9A83434D31C543B3C486ED3398C6498AE9A9A609F8296E73C84CD5B7CC6`.

The installed Workshop client `RTClient.dll` reports the same product-version string and has SHA-256 `CDCEC1060B7EBC9181B2457E3C1220AFB224EC755351C44C61851B8FF1BB9919`. The installed client `About.xml` supports RimWorld 1.5 and 1.6 but does not declare a release tag. The local client DLL is pinned by its exact hash; matching product-version text alone does not prove the client is byte-for-byte the release's distributed client. Keep this exact local artifact pair as the first test target and record any client/server update as a new target.

The official upstream page currently marks **26.8.31.1** as latest, gives tag commit `bbd981f`, and publishes the matching Windows server archive hash. Its release notes cover full planet-river synchronization and Odyssey asteroid compatibility. The local executable's embedded product-version hash differs from the release tag commit, so cite the published archive digest as the evidence for the server release identity rather than treating those two identifiers as interchangeable. No Rimrooms multiplayer behavior has been tested yet.

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
