# Priority power, gate, and turret source audit

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](../CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Checked:** 2026-09-27
**Scope:** installed payloads for priority rows 29, 49, 83, 86, 110, 167, 194, 217, and 218 in the 294-mod profile. This is a source/metadata inspection, not a runtime compatibility result.

## Local metadata and payloads

All nine Workshop payloads are present under `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\<WorkshopID>`. Each installed `About\About.xml` SHA-256 matches its corresponding record in [installed-mod-metadata-2026-09-27.csv](installed-mod-metadata-2026-09-27.csv). The package IDs and version evidence are:

| Row | Package ID | Local version evidence | Workshop ID |
| ---: | --- | --- | ---: |
| 29 | `Mlie.AllTurretsCanSetForcedTarget` | About 1.6.0; assembly identity version 0.0.0.0 | 3256513109 |
| 49 | `AdamBucior.BetterElectronics` | No About `modVersion` | 1555743957 |
| 83 | `Dubwise.Rimatomics` | About 1.7.3551; assembly product version 1.7.7368 | 1127530465 |
| 86 | `efficient.batteries` | No About `modVersion`; only a `1.2` content folder is installed although metadata lists RimWorld 1.6 | 865497369 |
| 110 | `FLASHPOINT55.HumanPowerGeneratorMod` | No About `modVersion`; assembly 1.0.0.0 | 1706030487 |
| 167 | `co.uk.epicguru.rimforgepoles` | No About `modVersion`; assembly 1.0.0.0 | 2507086460 |
| 194 | `Dubwise.Rimefeller` | About 1.2.2061; assembly product version 1.2.7364 | 1321849735 |
| 217 | `Mlie.SSLightningRod` | No About `modVersion`; assembly identity version 0.0.0.0 | 2358261479 |
| 218 | `ccyt.stargatesmod` | No About `modVersion`; local 1.6 assembly and definitions are present | 2831698056 |

The dated metadata CSV has exact `About.xml` hashes. Version differences between About metadata and assembly product version are recorded observations; their effect is unknown. Absence of a `modVersion` does not establish an outdated payload.

## Shared power and incident surfaces

- **Better Electronics, row 49:** its installed `Patches\BetterElectronics.xml` conditionally sets vanilla `ShortCircuit` and `SolarFlare` incident base chances to zero. This affects the incident environment around the proposed gate; it does not establish what will happen with Rimrooms or another incident mod.
- **Rimatomics, row 83:** local 1.6 definitions use vanilla power-plant/trader components alongside custom steam, water, cooling, and high-voltage pipe systems. Its research uses a separate Rimatomics tab. Relevant installed folders include `1.6\Defs\ThingDefs_Buildings`, `Defs\ResearchProjectDefs`, and `Patches`.
- **Efficient Batteries, row 86:** local battery definitions are in `1.2\Defs\ThingDefs\Batteries.xml`; they define 1,000/1,250/1,500 capacity and 0.60/0.85/0.98 efficiency values. The installed middle efficiency is 85%, while the indexed publisher description used for its review says 75%. Whether the `1.2` definitions load in the selected 1.6 profile remains unverified.
- **Human Power Generator, row 110:** installed 1.6 source derives its generator component from `CompPowerPlant`; output depends on pawn movement speed while its `Cycle` work/job runs. The source is in `1.6\Source\Humanpowergeneratormod`; its work type and job-giver definitions are in `1.6\Defs`.
- **Power Poles, row 167:** the two installed 1.6 definitions use `CompPowerTransmitter`; custom pole and wall-connector classes add connection behavior. Definitions are in `1.6\Defs\Buildings`.
- **Rimefeller, row 194:** installed definitions add powered oil/refining equipment and its own pipe buildings/jobs. The selected load order also contains a distinct `Multiplayer.API.dll` from Rimatomics with the same assembly name but a different version (0.5.0.0 versus 0.3.0.0) and hash. This is an assembly-resolution and multiplayer test lead, not proof of a collision or RWT compatibility.
- **Advanced Lightning Rod, row 217:** the installed 1.6 definition uses a custom component, consumes 750 W, and includes power-transmission/discharge settings.

Together these systems touch vanilla map power, incident chances, generation, storage, wiring, custom material networks, and work. The findings identify what to inspect in a test. They do not prove conflicts, interoperability, or a supported Rimrooms extension API.

## Turret controls and the separate gate system

- **All Turrets Can Set Forced Target, row 29:** the reviewed source patches `Building_TurretGun.get_CanSetForcedTarget` and conditionally covers a Combat Extended class. The exact profile turret classes covered at runtime are not established. Rimatomics adds its own turret/defense content, so forced-target controls need an in-game class-by-class check.
- **Stargates!, row 218:** the installed 1.6 XML defines transporter-based sites, a custom powered/explosive gate component, and a world component saving addresses. Source patches map-removal checks, caravan gizmos, carrying-pawn transport options, and raid arrival. The inspected source license is GPL-3.0. This is a separate portal system, not a Rimrooms dependency or an approved code/asset source; optional coexistence is a distinct test.

## Post-build acceptance checks

**Status:** test cases prepared; no game run is planned before the Rimrooms build exists. The owner stages/sorts the full 295-entry product target in RimSort and launches the first test; RimBridgeServer is a separately recorded QA overlay attached afterward. See the [RimSort plan](RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md) and [bridge plan](RIMBRIDGE_TEST_HARNESS.md) for setup/evidence.

1. Use representative vanilla power consumers on Core alone to record startup, cutoff, power-loss response, and recovery; then test the built Rimrooms gate against its specified power budget and failure behavior.
2. Add each power/storage mod separately, then test the selected combinations with incident settings on and off, including construction, deconstruction, and save/load.
3. Check whether Efficient Batteries definitions actually load in the pinned 1.6 profile and record their in-game values.
4. Record Rimatomics/Rimefeller assembly resolution and startup logs before testing any RWT action with that pair.
5. Test forced-target controls on vanilla and selected-profile turrets, including Rimatomics turrets where they are available.
6. If optional Stargates! coexistence remains in scope, test site/map creation and removal, pawns/cargo, raid arrivals, save/load, and a separate two-client RWT profile.

No runtime case above has been run. Keep the Rimrooms gate native and independent. Preserve a Core-only path and treat every profile mod as optional until its exact behavior has test evidence.
