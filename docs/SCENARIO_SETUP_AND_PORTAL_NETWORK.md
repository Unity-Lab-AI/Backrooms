# Scenario setup and physical door portals

**Latest owner requirement — connected colony portals (2026-09-28):** [CONNECTED_COLONY_PORTALS.md](CONNECTED_COLONY_PORTALS.md) governs travel, work, materials, portal lifetime, coordinate persistence and procedural inhabitants. Open portals unify local-branch labor and physical job/material access across both sides; ordinary crossing must not require expedition dispatch. Natural portals remain permanently open. Existing dispatch-only descriptions below are superseded where they conflict. The current source does not yet implement this unified work network.


**Owner direction, 2026-09-28:** retain three distinct starts with their own setup. Allow EdB Prepare Carefully for starting people in each scenario. The company start chooses its real-world site. Portals are existing doors with recoloring and a readable native aura; existing power, batteries, control equipment and research infrastructure enable larger supported doorways, longer openings and recall of saved Backrooms destinations. This refines the existing-content policy without adding custom items or door assets.

**Status:** implementation contract. The current development build does not implement these setup or door-network changes. Read the [installed-provider and setup source review](implementation/SCENARIO_AND_DOOR_PROVIDER_SOURCE.md) before implementation. Prepare Carefully and Stargates! are already in the 294-row profile; their source review is not runtime clearance.

## Three starting flows

| Start | Player setup | Initial location and objective | Shared-system boundary |
| --- | --- | --- | --- |
| Async Industries | Configure the actual starting people, skills, relationships and allowed supplies through native setup or optional Prepare Carefully. Pick a real-world settlement tile through the normal world flow. Review company role assignments after customization. | Build the company facility at the selected tile, establish its connected door/control/power infrastructure, research and prepare the first survey. | The company receives its scenario-authorized budget once. Gate power and field gear remain physical. Never replace customized pawns with a generated fixed roster. |
| Furniture & Knickknack Store | A distinct store opening, configurable owners/staff and starting stock through native setup or optional Prepare Carefully. Keep the ordinary surface-world site-selection route unless the owner changes it. | Operate and secure the shop, discover its anomalous doorway and investigate the missing-person lead. | No automatic company headquarters, corporate grants or machine technology. A later accepted investigation creates the company relationship through saved receipts. |
| Inside start (`lone_survivor`, stable internal ID) | Keep pawn customization before entry. The owner's proposed direction is a lone survivor **or group**, starting automatically inside; party-size choice is awaiting the grouped owner answer. | Proposed flow skips surface tile selection and begins in a bounded generated Backrooms site. Shelter, clues and a genuine discoverable exit replace the company's construction tutorial. | No fabricated surface headquarters or free company balance. A supported underlying world must still exist for a future exit; hiding the initial surface-selection page does not mean deleting world state. |

The third start's automatic placement and solo/group default were posed as a proposal. Two compact choices are pending: configurable party versus strictly lone start, and whether the first reliable exit reveals a fixed discovered surface destination or lets the player choose a settlement. After allowing time for an answer, the lead is using **configurable solo/group, automatic Backrooms entry and a fixed discovered surface destination** as a provisional implementation assumption, not an owner-approved final selection. Continue independent company setup work; the pending answers can revise this assumption. Do not create a fourth scenario just to support a party-size option, and do not rename an existing saved scenario ID.

### Customization must survive setup

- Use the player's actual final starting pawn instances, names, relationships, health, traits, skills and inventory. Prepare Carefully is optional; Core setup remains functional when it is absent.
- Company roles are assignments to those pawns, not custom PawnKind locks. Show unmet work capabilities and allow the player to resolve them in setup. Do not silently reroll, overwrite skills, reset priorities or replace edited people.
- Treat starting quantities and roster sizes as scenario defaults. Preserve accepted user edits; validate only genuine operational prerequisites with a specific reason and a visible correction route.
- Store the selected scenario, setup version, chosen world tile or inside coordinate, actual pawn identities and grant receipts. Loading never repeats generation or setup grants.
- The inside start must finish customization without first spawning a disposable colony or discarding a temporary group. Stage the final native people directly into the initial saved Backrooms map through the reviewed game-init path.
- Finding an exit reveals a real paired destination. Transfer the same living pawns and physical cargo through the normal expedition/custody rules; do not create copies on the surface or discard their original site.

## Existing doors are the portals

There are two useful portal origins: company-controlled doorways and mysterious/anomalous doorways discovered in ordinary settlements or generated spaces. Both use a real existing installed door and the shared saved endpoint model. Their discovery, reliability, access and control rules differ.

- Core `Door` / `Autodoor` are initial provider candidates. Larger sizes come from actual installed door providers after source review; do not rescale a one-cell door's footprint or invent another ThingDef to claim a larger portal.
- Recolor only the explicitly bound doorway using supported native drawing/color behavior. Add a restrained native effect/overlay for its active aura. Preserve the original door identity, ownership, health, access and provider behavior, and restore the original appearance when a role is removed. Unrelated doors stay ordinary.
- Provide a deliberate **enter/dispatch**, **return**, **recall**, **dial saved site**, **close** and **emergency shutdown** route where appropriate. Ordinary walking, hauling or opening the physical door must not accidentally teleport a pawn.
- Save doorway load ID, provider package/Def, physical footprint, source map, destination coordinate ID, paired endpoint, discovered/controlled state, opening state and transition receipt. A saved destination recalls its existing generated map/discoveries; reopening never regenerates it from scratch.
- An unknown portal shows uncertainty honestly. Resolving its destination assigns and saves a coordinate once. Random-looking portal events may vary by saved event seed, but reloading cannot silently change an already established endpoint.

## Infrastructure, upgrades and opening duration

The player must be able to see and manage the actual connections. Bind existing control/communications equipment, a real doorway, native generators and batteries, and relevant analysis/engineering stations into a local gate installation. Native power networks determine electrical connection; explicit Rimrooms role links determine which equipment controls which doorway. A bench on another unlinked map is not gate support.

Show connected equipment, live generation/demand, stored energy, power loss, missing operators, researched upgrades, supported portal size, estimated opening duration and available saved destinations. Upgrades improve specific capabilities—stability, duration, destination recall, aperture support, efficiency or recovery—using real materials, work and unlocked equipment.

Consume native power/energy through reviewed APIs. Do not count the same battery twice, replace the physical grid with an unlimited virtual reserve, or silently operate after a connection breaks. Additional batteries increase usable reserve only when connected and charged. More generation supports sustained operation subject to control/stability limits. Larger openings require their own supported door provider and higher demonstrated infrastructure capability; numeric tuning remains provisional until measured.

Research remains at designated existing benches. Portal operation uses connected control equipment and staff. These roles can share an installation but are distinct jobs and saved bindings. Preserve ordinary research, power and building behavior outside an active company job.

## Failure, migration and acceptance

Handle destroyed/uninstalled doors, missing providers, power failure, disconnected equipment, operator loss, expired windows, a moved endpoint, interrupted crossing, blocked arrival cells and unavailable destination maps. Keep the original map, endpoint, people, cargo and records recoverable; never substitute a new map or duplicate crew to repair an uncertain transfer. Mysterious doors need discoverable retreat/rescue routes consistent with their scenario.

The older custom machine gate, console and cutoff need a documented state migration into native-door/network bindings or an explicit preserved development-save boundary. Keep old saves/builds available. Existing source compilation does not verify this migration.

Acceptance remains owner-launched through RimSort: all three starts with native setup and with Prepare Carefully; customized rosters/relationships/items preserved; company tile honored; inside start bypasses surface selection without an extra colony; initial exit identity survives reload; door sizes/provider absence; native grid/battery drain; equipment unlink/relink; power loss and recovery; once-only crossing with physical cargo; deterministic generation and saved-map recall. RWT adds separate branch/visit/transfer cases and never grants live shared-map control.

## Canonical routes

- [Scenario contract](SCENARIOS.md), [game design](GAME_DESIGN.md), [procedural-space contract](PROCEDURAL_SPACE_CONTRACT.md).
- [Existing-content policy](CONTENT_REUSE_POLICY.md), [replacement map](implementation/EXISTING_CONTENT_REPLACEMENT_MAP.md), [technical architecture](TECHNICAL_ARCHITECTURE.md).
- [Operations actions](OPERATIONS_ACTION_CONTRACTS.md), [saved state](CAMPAIGN_STATE_DICTIONARY.md), [master TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md).
- Prepare Carefully: [row 85 source review](research/reviews/mods/735106432-EdB.PrepareCarefully.md), package `EdB.PrepareCarefully`, Workshop `735106432`.
- Stargates!: [row 218 source review](research/reviews/mods/2831698056-ccyt.stargatesmod.md), package `ccyt.stargatesmod`, Workshop `2831698056`. Use its gate/site mechanics as a source reference; no direct dependency or copied implementation is authorized by that comparison.
