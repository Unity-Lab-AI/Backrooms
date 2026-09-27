# Compatibility and local multiplayer profile

## Support target

**Selected support target:** RimWorld **1.6**. Core-only solo play is supported by design; Royalty, Ideology, Biotech, Anomaly, and Odyssey are optional integrations. Co-op requires RimWorld Together and Harmony. All other entries in the 294-entry server profile are optional, while the complete ordered list is the required research/test target. No profile entry is assumed compatible until exact review and combined-profile testing.

## Local server snapshot

On 2026-09-27, `C:\Users\gfour\Desktop\RimWorld Server\Server-win-x64-new\Configs\ModConfig.json` contained 294 ordered mod records. The exported inventory is [here](research/rimworld-server-mod-inventory.csv). Its entries are names, workshop/package IDs, load order, and the server config's type number; it deliberately excludes mod settings and private server values.

The separate client `C:\Users\gfour\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml` was also inspected. Its 294 active package IDs map through the installed Workshop `About/About.xml` files to the exact same 294 IDs and load order as the server export: **zero set differences and zero order-position differences** on this snapshot. This confirms local profile agreement, not RWT synchronization or Rimrooms compatibility. The mapping and its limits are recorded in the [RWT and gravship feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md).

The server reports `AllowAllMods=true`, `EnforceSettings=false`, and no configured `ModOrder`, so it does not force the currently matching profile/settings. The RWT client package is `nova.rimworldtogether` (Workshop ID `3005289691`) and its local `About.xml` declares support for RimWorld 1.5 and 1.6, but does not pin a client release tag.

## Pinned pre-build test baseline

The installed game reads **RimWorld 1.6.4871 rev590** from `Version.txt`; Steam's local app manifest build ID is `23969874`. The game assembly reports `1.6.9676.17735`. The current client/server profile files and their hashes are recorded in the [RWT feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md). This is the exact local baseline for the first compatibility run, not a claim that other users have the same build.

The local Windows RWT server archive SHA-256 matches the `Server-win-x64.zip` asset published for upstream release **26.8.31.1**. The installed client assembly is separately pinned by its `RTClient.dll` product version and SHA-256 in that audit; matching version strings do not establish byte-for-byte release identity. Record the two exact artifacts for every run. No Rimrooms profile/runtime compatibility run has been completed.

The profile contained:

- RimWorld Together, workshop ID `3005289691`.
- Core and all five DLC entries: Royalty, Ideology, Biotech, Anomaly, and Odyssey.
- Common frameworks: Harmony, XML Extensions, HugsLib, Vanilla Expanded Framework, Adaptive Storage Framework, and Vehicle Framework.
- Relevant example systems for later comparison: Hospitality, Gastronomy, Prison Commons, Prison Labor, prisoner interactions, ResearchTree, Rimatomics, Rimefeller, vehicles, storage frameworks, communications, and expanded furniture.
- Vanilla Gravship Expanded Chapters 1 and 2. Chapter 1 requires Odyssey and Vanilla Expanded Framework; Chapter 2 also requires Chapter 1. The publishers describe Chapter 1 as a gravship systems overhaul and warn other gravship-changing mods may conflict; Chapter 2 adds orbital threats and ship defense. These are optional integrations, not Backrooms core requirements.

The server configuration is a useful real-world profile, but `AllowAllMods=true`, `EnforceSettings=false`, and an unset order mean the server does not guarantee that every future client keeps the same list. The current exact local match is a dated observation; a co-op release still needs a pinned/enforced join profile and an in-game run. RWT's official wiki describes configurable offline visits/raids and item/pawn exchange, while direct real-time play on shared world tiles remains a future feature. The exact local feature switches and in-game behavior are unverified. Rimrooms keeps company maps, research, gate state, and ledgers separate. See the [source register](SOURCE_REGISTER.md), [per-mod RWT review](research/reviews/mods/3005289691-nova.rimworldtogether.md), and [RWT feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md).

## Mod-interaction shortlist

Treat these as **examples to study**, not dependencies or guaranteed integrations:

| Need in Rimrooms - Async Industries | Existing profile examples | Design use |
| --- | --- | --- |
| Guests, recruitment, and stays | Hospitality (Continued), Hospitality: Invite to Stay, Real Faction Guest | Compare visit and recruitment flows; keep company hiring native to the mod. |
| Detention and prisoner workflows | Prison Commons, Prison Labor, PrisonerRansom, Custom Prisoner Interactions, Restraints | Reuse vanilla prisoner model where possible; add case files and investigation decisions in the mod. |
| Research and complex projects | ResearchTree, Research Whatever, Do Your F****** Research | Study visual organization and project cadence; do not require an alternative research system. |
| Storage, power, and engineering | Adaptive Storage Framework, Warehouse Storage, RimFridge, Rimatomics, Better Electronics | Check for patch collisions and learn from logistics presentation; define our own gate machinery. |
| Travel, transport, and remote operations | RimWorld Together, Vanilla Vehicles Expanded, Carryalls, Vanilla Gravship Expanded | Compare world-object, vehicle, and remote supply behavior; do not make vehicles necessary to enter the Backrooms. |
| Rooms, food, and staff comfort | Gastronomy, Hospitality, Realistic Rooms Rewritten, expanded furniture | Map company functions onto ordinary room, food, and recreation systems. |

The local list also contains a large set of combat, medical, pawn, and quality-of-life changes. Each is assigned a use and risk note in the [294-mod integration register](../outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx); actual page/API review and combined-profile compatibility work are still pending. Do not preemptively patch a mod solely from its title.

## Compatibility rules

1. Keep the main package independent from optional DLC/profile content and preserve a complete Core path; require Harmony/RWT only for the co-op path.
2. Detect DLC and optional user mods by their stable package IDs; place each integration in isolated XML patches or adapter code.
3. Avoid overwriting another mod's Def. Prefer targeted `PatchOperation` changes only when there is a concrete interaction to solve.
4. Keep a minimal recommended load-order note after the 1.6 folder and metadata rules are checked against the final package.
5. Record RimWorld build, DLC set, RimWorld Together client version, server release, ordered mod IDs, and the save used for each compatibility report.
6. Review errors and desynchronization evidence on a clean baseline first, then add the exact local profile. Do not describe the entire 294-entry profile as supported until that profile has been exercised.

## Current open compatibility questions

- Does this pinned game build and exact RWT client/server artifact pair support the required co-op campaign behavior in a disposable save?
- Which individual profile mods need explicit synchronization patches for actions or custom interfaces used by this campaign?
- Should unsupported optional mods be warned about, or should the first release publish a smaller recommended list?
- Does the pinned RWT build transfer the Backrooms research dossier and expedition cargo reliably, and which server features will be enabled for visits, guilds, sites, roads, aid, and trading?
- Can one RWT server/world support players choosing different Rimrooms start scenarios, or must each co-op session select one common scenario?
- Which active profile mods modify gravships and therefore conflict with the selected Gravship Expanded chapters?

See the [complete systems and 294-mod integration plan](MOD_INTEGRATION_PLAN.md) and its linked workbook for the per-row role/status. Most profile rows have design-level mappings only; do not represent the profile as tested.
