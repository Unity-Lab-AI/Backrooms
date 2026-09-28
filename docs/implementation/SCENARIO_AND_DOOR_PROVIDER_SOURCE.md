# Scenario setup and existing-door provider source review

**Date:** 2026-09-28. **Status:** installed-source research and proposed implementation route, not implemented compatibility. No game, gameplay tests, build, staging or Git operation was performed. Only this tracked document was written; decompiled inspection text remains ignored under `.local/inspection-scenario-door/`.

## Task and authority

This bounded assignment supports the [scenario setup and physical portal contract](../SCENARIO_SETUP_AND_PORTAL_NETWORK.md), [existing-content policy](../CONTENT_REUSE_POLICY.md), [scenario cards](../SCENARIOS.md), [procedural-space contract](../PROCEDURAL_SPACE_CONTRACT.md), [state dictionary](../CAMPAIGN_STATE_DICTIONARY.md), [action contracts](../OPERATIONS_ACTION_CONTRACTS.md) and [master TODO](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md). Feature IDs: **RR-SCEN, RR-STA, RR-FAC, RR-GATE, RR-EXP, RR-SPACE, RR-STYLE, RR-COMPAT**.

The owner requires custom setup for all three starts, optional EdB Prepare Carefully, normal company tile selection, and actual existing doors of supported sizes as portal endpoints. Connected native power, batteries, controls and research facilities must govern capability and duration. Stargates! supplies mechanics context, not permission to copy its implementation or make its planetary network Rimrooms' authority. The inside start's party default and first-exit destination choice remain the lead's two pending owner questions at the time of this review.

## Evidence pins and reproducible inspections

- Native game: **RimWorld 1.6.4871 rev590**, profile row **4**, package `Ludeon.RimWorld`.
- Game assembly: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`; SHA-256 **`5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`**.
- Tool: local **ilspycmd 9.1.0.7988**. No provider code or assets were copied into tracked implementation.
- Read-only `tools/research/audit-pinned-targets.ps1` returned **307 checked hashes, 294 metadata rows, one reviewed delta, no issues**. This is a metadata/source-pin check, not a mod or gameplay test.
- Workshop root below: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100`. Core XML root: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs`.

| Inspected installed assembly, relative to Workshop root | SHA-256 |
| --- | --- |
| `735106432/1.6/Assemblies/EdBPrepareCarefully.dll` | `4A511455894D22C104AB6F07CC70A7AAF256DA8B980208EEE251603391A6276E` |
| `2831698056/1.6/Assemblies/Stargates.dll` | `1BFB4744738765F9AE9D571C820FEA59B9E90A1EDAE6A1946D4F80D9F58A0F25` |
| `3532342422/1.6/Assemblies/DoorsExpanded.dll` | `2B8639002BD9D7D0208A9DD023B072A265C7EEF55881B5D676B6A27AEFA49080` |

Exact type inspection pattern, with output restricted to the ignored folder:

```powershell
$managedDir = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed'
$providerRoot = 'C:\Program Files (x86)\Steam\steamapps\workshop\content\294100'
$reviewType = 'EdB.PrepareCarefully.ControllerPage'
$providerAssembly = Join-Path $providerRoot '735106432/1.6/Assemblies/EdBPrepareCarefully.dll'
& .local/tools/ilspycmd.exe -r $managedDir -t $reviewType $providerAssembly |
  Set-Content -Encoding utf8 ".local/inspection-scenario-door/$reviewType.cs"
```

Other exact inspected types: EdB `HarmonyPatches.PrepareCarefullyButtonPatch`, `HarmonyPatches.ReplaceScenarioPatch`, `PagePrepareCarefully`, `Mod`, `ManagerEquipment`; StargatesMod `CompStargate`, `CompDialHomeDevice`, `WorldComp_StargateAddresses`; DoorsExpanded `Building_DoorExpanded`; Core `RimWorld.FleckMaker`, `Verse.FleckCreationData`, `Verse.Building`, `RimWorld.Building_MultiTileDoor`, `RimWorld.MainButtonWorker_ToggleWorld`, `RimWorld.Planet.WorldRendererUtility`, `RimWorld.Planet.WorldRenderer`. Existing ignored scenario/door/power inspections and the [scenario source review](PHASE_2_SCENARIO_SOURCE_REVIEW.md) were read again. Preliminary guesses `Verse.FleckMaker` and `RimWorld.MainButtonWorker_World` do not exist in this assembly; the verified names above supersede them.

## Exact profile routes

Rows and package IDs come from the [294-row inventory](../research/rimworld-server-mod-inventory.csv) and [installed metadata](../research/installed-mod-metadata-2026-09-27.csv). Linked reviews retain their historical dispositions; new provider binding remains work under the latest owner contract.

| Row | Provider and package | Role and limits |
| --- | --- | --- |
| 4 | [Core](../research/reviews/mods/official-4-Ludeon.RimWorld.md), `Ludeon.RimWorld` | Native scenario pages, final pawn list, doors, painting, effects and connected power; mandatory baseline. |
| 85 | [EdB Prepare Carefully](../research/reviews/mods/735106432-EdB.PrepareCarefully.md), `EdB.PrepareCarefully` | Starting people/equipment only. 1.6 loads `Common` plus `1.6`; optional. Historical local Harmony load-after ID mismatch remains a profile concern. |
| 218 | [Stargates!](../research/reviews/mods/2831698056-ccyt.stargatesmod.md), `ccyt.stargatesmod` | Mechanics reference; source has Harmony/VEF dependencies and GPL-3.0 provenance. Keep native Stargate objects/network independent. |
| 77 | [Doors Expanded](../research/reviews/mods/3532342422-jecrell.doorsexpanded.md), `jecrell.doorsexpanded` | Actual 2-, 3-cell and thick door candidates; depends on Harmony. Installed DLL inheritance inspected. |
| 185 | [ReBuild: Doors and Corners](../research/reviews/mods/3262718980-ReBuild.COTR.DoorsAndCorners.md), `ReBuild.COTR.DoorsAndCorners` | Actual glass/double/ornate door candidates and broad rendering patches; VEF dependency. Reference subscribed content, do not redistribute it. |
| 187 | [Remote Doors](../research/reviews/mods/2243274070-Mlie.RemoteDoors.md), `Mlie.RemoteDoors` | Existing remote door/controller/switch; keep its access and remote-control behavior. Specific class adapter needs source review. |
| 201 | [Secret Passage Doors](../research/reviews/mods/2412682633-Mlie.SecretPassageDoors.md), `Mlie.SecretPassageDoors` | Optional disguised-door candidate; its concealment is not secure containment. Not promoted to a supported portal provider by this review. |
| 249 / 11 | [Vanilla Vehicles Expanded](../research/reviews/mods/3014906877-OskarPotocki.VanillaVehiclesExpanded.md), `OskarPotocki.VanillaVehiclesExpanded`; [Vehicle Framework](../research/reviews/mods/3014915404-SmashPhil.VehicleFramework.md), `SmashPhil.VehicleFramework` | Real 4-/5-cell garage doors, with separate open/closed definitions. Dedicated transition/vehicle path review needed. |
| 265 | [AirtightGarageDoors](../research/reviews/mods/3534740420-Endy.Airtightgarage.md), `Endy.Airtightgarage` | Patch of VVE garage-base airtight behavior, not a standalone door provider. Odyssey boundary remains relevant. |
| 252 | [Vault Walls and Doors](../research/reviews/mods/2000708343-SickBoyWi.Vault.OnePointOne.md), `SickBoyWi.Vault.OnePointOne` | Additional reviewed architecture row; exact native-door inheritance and usable sizes not inspected here. |
| 273 / 175 | [Locks](../research/reviews/mods/1157085076-avius.locks.md), `avius.locks`; [Prisoners Dont Have Keys](../research/reviews/mods/2595360307-Mlie.PrisonersDontHaveKeys.md), `Mlie.PrisonersDontHaveKeys` | Access/path behavior must remain authoritative; a portal must not bypass locked/native forbidden approach by teleporting remotely. |
| 86 | [Efficient batteries](../research/reviews/mods/865497369-efficient.batteries.md), `efficient.batteries` | Existing native CompPowerBattery storage candidates; exact XML below. |
| 19 / 49 | [Automatic Power Switch](../research/reviews/mods/3031634496-Og.AutomaticPowerSwitch.md), `Og.AutomaticPowerSwitch`; [Better Electronics](../research/reviews/mods/1555743957-AdamBucior.BetterElectronics.md), `AdamBucior.BetterElectronics` | Switching / electrical incident configuration; neither supplies free energy or guarantees stable gate power. |
| 83 / 194 | [Rimatomics](../research/reviews/mods/1127530465-Dubwise.Rimatomics.md), `Dubwise.Rimatomics`; [Rimefeller](../research/reviews/mods/1321849735-Dubwise.Rimefeller.md), `Dubwise.Rimefeller` | Existing generation/industry feeding the native grid; do not require either or rewrite their machines. |
| 110 / 167 | [Human Power Generator](../research/reviews/mods/1706030487-FLASHPOINT55.HumanPowerGeneratorMod.md), `FLASHPOINT55.HumanPowerGeneratorMod`; [Power Poles](../research/reviews/mods/2507086460-co.uk.epicguru.rimforgepoles.md), `co.uk.epicguru.rimforgepoles` | Optional real power production and wiring. Physical connectivity must be read from native networks after their provider logic runs. |

## Prepare Carefully: concrete startup behavior

### Verified source facts

1. EdB patches **`Page_ConfigureStartingPawns.DoWindowContents(Rect)`** with a postfix button, then calls **`Mod.Start(Page_ConfigureStartingPawns)`**. Preserve that native page or a subclass using its draw method. Replacing it with an unrelated custom page loses this known entry point.
2. **`ControllerPage.StartGame()`** calls `PreparePawns()`, `PrepareRelationships()`, `PrepareEquipment()`, then reads the original page's **`next` and `nextAct`**, opens `next` and invokes `nextAct`. It does **not** call the original page's `CanDoNext()`.
3. `PreparePawns()` sets `Find.GameInitData.startingPawnCount` to the customized colony count, replaces `startingAndOptionalPawns` with the prepared actual pawn instances, and updates `startingPossessions`. It disposes unused original candidates as part of its own flow. Rimrooms must not hold pre-customization roster references as its final crew or run another generation pass.
4. `ManagerEquipment.InitializeStateFromScenarioAndStartingPawns()` recognizes native starting/scattered thing parts, starting animals/mechs and pawn possessions. `PrepareEquipment()` preserves parts not marked replaced and appends customized equipment parts. Stock privately created by `GenStep_Headquarters` is outside that editable equipment route.
5. EdB's `Game.InitNewGame` postfix restores original scenario parts and clears its singleton state. Capture accepted setup/stock/role choices into Rimrooms' own saved startup receipt during startup; do not reconstruct actual grants later by rereading restored scenario parts.

### Required implementation route

- Keep one native pawn configuration part/page for each scenario. Use actual native PawnKinds, with scenario default count; do not require the five old Rimrooms staff PawnKinds.
- Append a **final Rimrooms setup/role/manifest review page after the native pawn page** through a custom `ScenPart.GetConfigPages()`. Both normal Next and EdB's direct next-page route reach it. Keep the final `PageUtility.InitGameStart` callback on this last page, as native page stitching normally does.
- That page rereads the final selected list and count, shows genuine capability gaps, assigns company roles by pawn reference, and preserves health, traits, skills, relationships, equipment and accepted count edits. It must handle Back/reopen/EdB cancel without stale references. `PreMapGenerate()` remains a last defensive check, not the player's first notification through an exception.
- Put editable startup supplies into native scenario starting-thing parts/possessions or a specifically reviewed adapter. Give fixed prebuilt structures and their exact remaining stock a separate visible facility manifest. Never grant edited supplies through native arrival and again through HQ stock generation. Current custom startup stock is not automatically editable in EdB.
- Keep scenario ID/version, roster references/load IDs, role assignment, final stock manifest, chosen tile or inside coordinate, and physical/setup receipts in game/map-owned saved state. One native arrival owner spawns the selected people and native supplies exactly once.

**Existing-source mismatch:** [ScenPart_RimroomsStart.cs](../../src/RimroomsAsyncIndustries/Scenario/ScenPart_RimroomsStart.cs) currently takes five candidates, demands five distinct custom kinds, enables role priorities, and overrides `Page_ConfigureRimroomsStaff.CanDoNext`. That is the earlier fixed-company implementation, not completion of the new three-start/customization contract. It must change without silently overriding player customization.

## Three native starting flows and the hidden surface

Native `Scenario.GetFirstConfigPage()` stitches storyteller → world generation → surface site selection unless any part is `ScenPart_ForcedMap` → ideology when enabled → part config pages. `GameInitData.PrepForMapGen()` trims optional candidates and sets native faction/work state before `Scenario.PreMapGenerate()`. `GenerateIntoMap(Map)` and native standing arrival run during generation; `PostGameStart()` follows map creation. See the [earlier full ordering evidence](PHASE_2_SCENARIO_SOURCE_REVIEW.md#selectable-scenario-and-exact-lifecycle).

| Start | Proposed source route | Important boundary |
| --- | --- | --- |
| `async_industries` | Ordinary selected tile; no ForcedMap part. Assign the reviewed generator/size in PreMapGenerate, then initialize the company from the actual final roster and physical setup receipt. | Honor the selected tile. A custom map generator does not require randomizing or skipping site choice. |
| `furniture_knickknack_store` | Ordinary selected tile and own native pawn/stock defaults, then store-specific final setup and map receipt. | Must not invoke company grants or require the company's operator/three-person crew template. Preserve this canonical scenario ID. |
| `lone_survivor` | Conditional on owner answer: a ForcedMap-compatible part can suppress surface-site selection and assign a backed tile/generator after world creation; final pawn customization still runs. Generate the saved Backrooms opening directly and use the same actual selected people. | No disposable surface colony or duplicate pawn batch. A new-game map-parent/faction path still needs a narrow adapter: native player-faction PreMapGenerate creates a surface settlement, and the current destination service assumes an initialized company/HQ. Neither may be reused unchanged for an inside-only survivor. |

A hidden surface still needs a valid native world for factions, time, seed and later exit. **`MainButtonWorker_ToggleWorld.Activate()`** sets `Find.World.renderer.wantedMode`; **`WorldRendererUtility.CurrentWorldRenderMode`** also forces `Planet` when playing with no current map, and can use a map generator's `renderWorld` flag. Therefore hiding one button or setting `wantedMode=None` once does not enforce the proposed rule. A saved inside-start access state must guard applicable world UI activation, map-edge/caravan/transport escape and alternate mod entry points while an actual inside map remains current. This needs narrowly scoped source/patch work; no blanket global world suppression is implemented or certified here. Do not show a fake hidden world while another ordinary route exposes it.

For the first real exit, save the endpoint/destination once before crossing, use the selected owner policy, then expose normal world access only after the stable exit receipt. Preserve the original site, exact pawns, corpses, equipment and map modifications. A portal discovery must not reroll its established destination on reload or create a company budget for the survivor/store.

## Existing physical door candidates

Read these installed XML paths directly; a candidate is not a supported adapter yet.

| Provider | Actual Defs, footprint and source |
| --- | --- |
| Core | `Door`, `Autodoor`, default **1×1**, `ThingDefs_Buildings/Buildings_Structure.xml:7–107`. `DoorBase` uses `Building_Door`, native `paintable=true`, ordinary roof/room/access behavior. Autodoor's native power is separate from portal operation energy. |
| Doors Expanded | `3532342422/1.6/Defs/ThingDef_Building/Heron_Doors.xml`: `PH_DoorDouble` **2×1** (13/21), `PH_DoorTriple` **3×1** (48/56), `PH_AutodoorDouble` **2×1 /100 W** (83/95/118), `PH_AutodoorTriple` **3×1 /150 W** (132/144/167), `PH_DoorThickBlastDoor` **3×2 /200 W** (578/592/654). `Heron_Base.xml:46` identifies `DoorsExpanded.Building_DoorExpanded`, whose inspected DLL inherits Core `Building_MultiTileDoor`. Remote variants are in `Heron_RemoteDoorsAndButtons.xml`. Curtains are not automatically valid gate frames. |
| ReBuild | `3262718980/1.6/Defs/ThingDefs_Buildings/Buildings_Structure_Doors.xml`: `RB_DoubleDoor` **2×1**, native `Building_MultiTileDoor` (127/130/139); `RB_DoubleAutodoor` **2×1**, provider `Building_MultiTileDoorStuffColor` (173/176/185); `RB_LargeOrnateDoor` **3×1**, native multi-tile class (233/236/252); `RB_GlassAutodoor`, `RB_ReinforcedGlassAutodoor` are additional native-provider candidates. Provider graphic/paint overrides still need acceptance. |
| Remote Doors | `2243274070/1.6/Defs/ThingDefs/Buildings_RemoteDoors.xml`: `RemoteDoor`, `RemoteDoors.Building_RemoteDoor`, base draw **25 W**. Its controller and power-switch files are in the same folder. Do not replace its controller/access behavior with a forced-open command. |
| VVE garage | `3014906877/1.6/Defs/ThingDefs_Buildings/Buildings_Structure.xml`: `VVE_GarageDoor` **4×1**, `VVE_GarageDoorLarge` **5×1**, respective `...Opened` definitions; `VVE_GarageAutoDoor` **4×1 /150 W** and provider classes `GarageDoor`/`GarageAutoDoor`. XML establishes separate states, not whether their runtime transition preserves the same Thing. Inspect that exact lifecycle before binding by load ID. `3534740420/Patches/Garage.xml` adds `isAirtight=true` to `VVE_GarageDoorAbstract`; it creates no doorway. |

Core `Building_Door` exposes **`Open`**, **`HoldOpen`**, **`PawnCanOpen(Pawn)`**, **`StartManualOpenBy(Pawn)`**; its protected `DoorOpen(int)` is not a public portal hook. Respect native pawn approach/reservation/opening/access and the entire rotated occupied rectangle. Never teleport merely because a pawn walks through an ordinary door. Explicit Enter/Dispatch jobs must reach the bound door's valid threshold and verify the same endpoint/active route before transferring the original pawn.

Provider adapter records should store package/Def/class family, actual load ID, map ID, rotation, occupied dimensions, approach/arrival sides and counterpart coordinate. Loss/minification/replacement of a bound door pauses the route and exposes a deliberate rebind/recovery action; it must not bind whichever unrelated door appears at that cell. Multiple doors sharing one grid need separate saved identities and mutually accounted power budgets. Unknown providers remain ordinary usable buildings until their portal adapter is reviewed.

## Native recoloring and aura without new art

**Source facts:** `Verse.Building.PaintColorDef` is readable and saved; **`ChangePaint(ColorDef)`** updates the instance and calls `Notify_ColorChanged()`. `Building.DrawColor` prioritizes paint over base color. `CompColorable.SetColor(Color)`/`Disable()` are also native, but not every door has that comp and setting it does not override a building's existing paint. Core doors already have `paintable=true`. Do not edit the shared ThingDef/graphic color to tint one portal.

**Proposed route:** use an existing native structure ColorDef for the bound doorway, save its original paint Def (including null), and restore it through `ChangePaint` when the role ends. Respect a deliberate player repaint rather than blindly restoring stale paint. For provider-specific rendering that ignores native paint, retain a visible aura and report the tint limitation until a supported adapter exists; do not clone its graphics or claim full recoloring.

Core `RimWorld.FleckMaker.GetDataStatic(Vector3, Map, FleckDef, float=1)` returns `Verse.FleckCreationData`; set its public **`instanceColor`**, **`exactScale`**, **`rotation`**, and optional **`solidTimeOverride`**, then call **`map.flecks.CreateFleck(data)`**. `Effects/Fleck_Visual.xml:185` defines native **`HeatGlow`**, using native FireGlow/MoteGlow with slow fades (2.6 s in, 1.5 s solid, 3.3 s out). It is a reasonable quiet aura candidate, not a native portal simulation. No new FleckDef/texture is required. Avoid rapid `LightningGlow` flashes as a continuous aura. Bound emission rate/size; render only valid visible current-map endpoints, preserve fog, provide status text and reduced-motion/disable behavior. The appearance and acceptable alpha/scale still require owner-launched viewing.

## Physical power and equipment bindings

Verified native APIs from ignored `.local/inspection-work/` and scenario inspections:

| API | Meaning / constraint |
| --- | --- |
| `CompPower.PowerNet` | Actual native connected network; null/disconnected must refuse powered operation. Never use geographic distance as proof of electrical connection. |
| `PowerNet.powerComps`, `batteryComps` | Actual traders and storage on that network. De-duplicate actual objects, require same map, live spawned state and valid provider. Native switches/poles determine topology. |
| `CompPowerTrader.PowerOn`, `PowerOutput`, `EnergyOutputPerTick` | Current native operating state; positive output generates, negative consumes. Other provider logic may recalculate output; do not overwrite it globally to manufacture portal power. |
| `PowerNet.CurrentEnergyGainRate()` | **Net watt-days per tick**, not gross watts or an independently available portal allowance. Convert with `CompPower.WattsToWattDaysPerTick` (=1/60000) for display. |
| `PowerNet.CurrentStoredEnergy()` | Sum of non-EMP-stunned native batteries. Shared consumers can spend it; a UI estimate is not reserved energy. |
| `CompPowerBattery.StoredEnergy`, `Props.storedEnergyMax`, `StunnedByEMP`, `DrawPower(float)` | Real stored watt-days and withdrawal. Prevalidate finite positive amount and sufficient observed total; DrawPower does not return a transactional success and clamps below zero. Bound receipts and actual before/after amounts are required. |
| `CompPowerBattery.AddEnergy(float)` / `SetStoredEnergyPct(float)` | AddEnergy applies native efficiency; setting percentage directly is a grant, not evidence of delivered power. Do not refill on open/load/rebind. |

Row 86 `865497369/1.2/Defs/ThingDefs/Batteries.xml` supplies native `Building_Battery` / `CompProperties_Battery`: **`SmallEfficientBattery` 1000 Wd /0.60 efficiency**, **`SmallHyperEfficentBattery` 1250 Wd /0.85**, **`SmallUltraEfficientBattery` 1500 Wd /0.98**, all **1×2**. The middle Def's spelling is intentional. There is no LoadFolders.xml; the installed versioned XML exists at 1.2, as noted here, not an invented 1.6 subfolder. Runtime final Defs can still be patched; read actual loaded capacities rather than hard-coding these snapshot numbers.

A safe first implementation can require a designated existing powered **CommsConsole**, actual native door, physically connected charged batteries and appropriate connected operating equipment. Read actual battery withdrawal for portal energy while ordinary generators refill through their native network. A manual Door can be the threshold without inventing a power comp for it: its linked control's network supplies portal energy, while the explicit physical endpoint/control association is shown to the player. A HiTechResearchBench can prove connected lab support; a SimpleResearchBench is a physical non-electric lab capability and must not be described as electrically connected.

Choose one accounting route per energy cost; do not charge the native network through both an added demand and battery withdrawal for the same operation. A protected return reserve cannot be an unlimited virtual capacitor. Show the actual designated reserve batteries/network; shared loads, switching, EMP and destruction can invalidate availability. New code needs one installation-wide allocator and stable debit receipts before several portals share batteries. Opening estimates combine measured grid/storage with data-defined aperture, stability, control and research limits; numeric balance is original game design, not a fact learned from Stargates.

## Stargates: useful reference and boundaries

Installed `CompDialHomeDevice.IsConnectedToStargate` and **`GetLinkedStargateComp()`** use native **`CompFacility.LinkedBuildings`** (unless self-dialing). This demonstrates a physical linked controller route rather than selecting a random console on any map. Rimrooms may use its own saved role links with native grid validation; do not copy this provider's implementation.

`CompStargate.OpenStargateDelayed(PlanetTile,int,DialMode)` starts its own dial state; its private opening path uses map parents and `GetOrGenerateMapUtility`. World/pocket addresses belong to `WorldComp_StargateAddresses`; pocket addresses in this build use map indices. **Do not adopt those indices as stable Rimrooms coordinates.** Preserve Rimrooms' saved coordinate, generator version, map-parent/map identity and discovery records; recall the existing saved map without regeneration.

Installed gate XML has three variants: 5×1 ordinary/advanced gates and a 3×1 Orlin gate. The Orlin variant has native 2000 W power plus `requiresPower=true` and `explodeOnUse=true`; this is not a general duration-by-battery system to copy. `CompStargate.CompTick()` handles its transporter/buffers, native effects and receiving-gate idle closure after 2500 ticks without traffic. Its iris/vortex content disposal and paired gate rules differ from Rimrooms' preservation/recovery contract. Rimrooms must own its crossing receipts, emergency timing and persistent map retention; do not put its crew or unique evidence into another mod's disposal buffers.

The new mysterious/company door origins can share a Rimrooms endpoint model while retaining different discovery/control requirements. Stargate controls must not silently acquire authority over these doors, and ordinary Stargate travel must not become an unreviewed bypass into otherwise gate-only sites. Coexistence remains a future full-profile check.

## Implementation sequence and unresolved decisions

**Planned paths only, not created by this review:** scenario setup record/page/service under `Scenario/`; provider adapters and saved endpoint/installation/energy receipts under `Gate/`; native aura utility under `Presentation/`; a start-world-access policy and inside-start initializer; scenario/Operations keyed text and data-only setup/provider policies. Reuse existing `Generation/`, `Expedition/`, laboratory and company services after separating their current company-only assumptions. No new ThingDefs/PawnKind art or copied provider resources.

1. Preserve native/EdB final roster and stock, insert final setup page, replace kind locks, and keep company tile selection. Add one startup receipt per distinct scenario.
2. Bind Core Door/Autodoor and actual control/storage/lab roles; move legacy gate state out of the custom building with an explicit migration boundary. Implement actual native withdrawal and recovery before increasing door sizes.
3. Add reviewed 2-/3-cell provider adapters and paint/aura fallback; honor locks, forbidden state, rotation and complete doorway pathing. Review VVE's state transition before larger garages.
4. Implement inside start under the lead's recorded provisional defaults until the owner answers, including direct initial map ownership/arrival and narrowly guarded surface access. Keep its unique exit and original people/site saved.
5. Preserve dispatch, emergency return, stranded/rescue/abandonment, evidence custody and saved-site recall; do not discard these existing systems during provider replacement.

**Provisional lead defaults:** configurable solo/group with automatic Backrooms placement and a fixed discovered exit; these are reversible working assumptions, not owner selections. The questions remain available while independent implementation continues.

**Pending owner direction, already grouped by lead:** (a) configurable solo/group versus strictly one survivor; (b) fixed discovered surface exit versus player-chosen settlement after escape. No additional design questionnaire is required for routine provider selection. Technical follow-up remains: initial inside map-parent creation without temporary settlement; full world-entry guard coverage; VVE open/closed Thing identity; third-party paint/render behavior; final loaded battery/door metadata; preserving native research and multi-installation energy accounting. These are engineering tasks, not grounds to claim compatibility now.

**Acceptance still future:** three starts × native/EdB setup, Back/cancel/presets/count/relationships/gear retention; tile fidelity; one physical stock grant; direct inside arrival and stable exit; all rotations/footprints and provider absence; actual battery/grid drain; disconnection/EMP/operator loss; safe same-item/same-pawn crossing and interrupted recovery; saved endpoint recall without reroll; old development-save migration; reduced motion/fog; locks/door interactions; separately pinned RWT branch/visit/transfer cases. The owner alone launches through RimSort.
