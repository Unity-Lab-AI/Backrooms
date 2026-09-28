# Compatibility and local multiplayer profile

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


## Support target

**Selected support target:** RimWorld **1.6**. Core-only solo play is supported by design; Royalty, Ideology, Biotech, Anomaly, and Odyssey are optional integrations. Co-op requires RimWorld Together and Harmony. All other entries in the 294-entry server profile are optional, while the complete ordered list is the required research/test target. All 294 entries have source-fact reviews; no profile entry is treated as runtime-compatible until the relevant exact-profile test is recorded.

## Local server snapshot

On 2026-09-27, `C:\Users\gfour\Desktop\RimWorld Server\Server-win-x64-new\Configs\ModConfig.json` contained 294 ordered mod records. The exported inventory is [here](research/rimworld-server-mod-inventory.csv). Its entries are names, workshop/package IDs, load order, and the server config's type number; it deliberately excludes mod settings and private server values.

The separate client `C:\Users\gfour\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml` was also inspected. Its 294 active package IDs map through the installed Workshop `About/About.xml` files to the exact same 294 IDs and load order as the server export: **zero set differences and zero order-position differences** on this snapshot. This confirms local profile agreement, not RWT synchronization or Rimrooms compatibility. The mapping and its limits are recorded in the [RWT and gravship feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md).

The server reports `AllowAllMods=true`, `EnforceSettings=false`, and no configured `ModOrder`, so it does not force the currently matching profile/settings. The RWT client package is `nova.rimworldtogether` (Workshop ID `3005289691`) and its local `About.xml` declares support for RimWorld 1.5 and 1.6, but does not pin a client release tag. The installed `RTClient.dll`, `RTNetwork.dll`, and `RTShared.dll` have each been verified as byte-for-byte matches to the official 26.8.31.1 client asset; this pins source artifacts, not runtime compatibility.

The local server's action files are in `Configs\Actions\*.json`: Aid and Trade are enabled with cooldown 250. There is no separate local Visit/Activity action file, and `ServerConfig.json` has no `EnableActivities` field, so offline-visit availability remains unknown from this snapshot. `ScenarioConfig.json` enforces `Crashlanded`; use a disposable configuration copy when testing mixed starts. File hashes and config details are recorded in the [RWT feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md).

## Pinned pre-build test baseline

The pre-build test target is the exact installed binary set whose two disposable `-batchmode -quicktest` logs report **RimWorld 1.6.4871 rev591**: Steam build ID `23969874`, `RimWorldWin64.exe` SHA-256 `4C30E2105B49F2D0130F5D861947FBE82B866042299DA48EF1C8CF6979A8564D`, and `Assembly-CSharp.dll` SHA-256 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`. `Version.txt` and the profile snapshot text say **rev590**; the reason for that mismatch is unknown and both observations remain recorded. The [startup-smoke report](research/runtime-evidence/RWT_AND_FULL_PROFILE_STARTUP_2026-09-27.md) records the logs, hashes, and limitations. Match both hashes and record the reported build on each client before multiplayer cases. Client/server profile hashes remain in the [RWT feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md).

The local Windows RWT server archive SHA-256 matches the `Server-win-x64.zip` asset published for upstream release **26.8.31.1**. The installed client release archive digest and all three client DLL hashes also match the official 26.8.31.1 client asset, as recorded in that audit. This verifies artifact identity only. Record the exact artifacts for every run. No Rimrooms profile/runtime compatibility run has been completed.

The profile contained:

- RimWorld Together, workshop ID `3005289691`.
- Core and all five DLC entries: Royalty, Ideology, Biotech, Anomaly, and Odyssey.
- Common frameworks: Harmony, XML Extensions, HugsLib, Vanilla Expanded Framework, Adaptive Storage Framework, and Vehicle Framework.
- Relevant example systems for later comparison: Hospitality, Gastronomy, Prison Commons, Prison Labor, prisoner interactions, ResearchTree, Rimatomics, Rimefeller, vehicles, storage frameworks, communications, and expanded furniture.
- Vanilla Gravship Expanded Chapters 1 and 2. Chapter 1 requires Odyssey and Vanilla Expanded Framework; Chapter 2 also requires Chapter 1. The publishers describe Chapter 1 as a gravship systems overhaul and warn other gravship-changing mods may conflict; Chapter 2 adds orbital threats and ship defense. These are optional integrations, not Backrooms core requirements.

The server configuration is a useful real-world profile, but `AllowAllMods=true`, `EnforceSettings=false`, and an unset order mean the server does not guarantee that every future client keeps the same list. The current exact local match is a dated observation; a co-op release still needs a pinned/enforced join profile and an in-game run. RWT's official wiki describes configurable offline visits/raids; its trading guide says direct trades and gifts require both players online. Local Aid and Trade actions are enabled, while offline-visit availability is not established. Test visits, aid, direct trade, and reconnect as separate workflows. Keep company maps, research, gate state, and ledgers separate. See the [source register](SOURCE_REGISTER.md), [per-mod RWT review](research/reviews/mods/3005289691-nova.rimworldtogether.md), and [RWT feasibility audit](research/RWT_AND_GRAVSHIP_FEASIBILITY.md).

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

The local list also contains a large set of combat, medical, pawn, and quality-of-life changes. Each is assigned a use and risk note in the [294-mod integration register](../outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx); linked source-fact review is complete, while extension-point inspection and combined-profile compatibility work remain open. Do not preemptively patch a mod solely from its title.

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
- What happens in the pinned two-client candidate profile with Questionable Ethics Enhanced (row 182) and Medical Dissection (row 274), which the owner directed us to include despite publisher multiplayer warnings?
- Which active profile mods modify gravships and therefore conflict with the selected Gravship Expanded chapters?

See the [complete systems and 294-mod integration plan](MOD_INTEGRATION_PLAN.md) and its linked workbook for the per-row role/status. Every row has source review, but that does not establish runtime behavior; do not represent the profile as tested.
