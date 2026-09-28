# Physical logistics and hauling baseline test plan

**Status:** post-build acceptance run sheet prepared; no in-game capacity/haul result is claimed. Run these cases only after a Rimrooms build exists, following the owner-operated RimSort launch plan and using RimBridgeServer as a separate test overlay. Read with [`CAMPAIGN_ECONOMY_MODEL.md`](../CAMPAIGN_ECONOMY_MODEL.md), [`CAMPAIGN_ECONOMY_PROGRESSION.md`](../CAMPAIGN_ECONOMY_PROGRESSION.md), the [campaign economy workbook](../../outputs/4b7976f0-1820-4ffa-a191-bf7c7f79b010/Rimrooms_Campaign_Economy_v0.2.xlsx), the [OgreStack review](reviews/mods/1447140290-Ogre.OgreStack.md), the [RWT baseline plan](RWT_BASELINE_TEST_PLAN.md), and the [RimSort plan](RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md).

## Purpose

Prove that company money remains a branch-local USD ledger while goods stay physical and use RimWorld's ordinary stack, carrying, storage, hauling, caravan, and shipment rules. This test is aimed at the user's large-company scale: a million-dollar award must not spawn a million silver, while any actual silver, meals, equipment, samples, or salvage must arrive as bounded physical stock that pawns and facilities can handle.

The current planning comparison is conditional. Core Silver has a 500-item base stack limit; if the installed OgreStack row 157 is active with its published default 30× small-volume multiplier and no per-item override, the expectation is 15,000 silver per stack, or 67 stacks for one million silver. The Core-only comparison is 2,000 stacks. Confirm the current save's setting and each tested item's effective limit rather than treating either example as a universal result.

## Profiles and controls

Use the exact 1.6 game executable/Core hashes and runtime-reported build recorded in [`RWT_AND_FULL_PROFILE_STARTUP_2026-09-27.md`](runtime-evidence/RWT_AND_FULL_PROFILE_STARTUP_2026-09-27.md). Record all DLC, mod IDs/order, mod versions, OgreStack preset and overrides, storage/carry/transport settings, map size, pawn count, and save hash. Test at least:

1. **Core + Rimrooms:** no DLC or optional profile mods; preserve the complete logistics fallback.
2. **Core + Rimrooms + OgreStack:** row 157 enabled at its published default, then repeat with the profile's actual saved preset and any relevant overrides.
3. **Full 295-entry target:** the existing 294-entry order plus Rimrooms, sorted in RimSort. Enable RimBridgeServer only as a separate QA overlay and record the extra loaded entry (normally total 296). Do not infer that every optional mod is required.

Use disposable saves and developer-mode test stock. Never inject these test quantities into a campaign save. Keep worker skill, health, manipulation, movement, equipment, map distance, and assigned work priorities fixed between comparisons.

## Post-build reference cases

| Case | Test input | Record |
| --- | --- | --- |
| Stack baseline | 1,000,000 silver; one Core resource and one non-small-volume item with no known override | Effective stack size, number of stacks, item count after save/reload, and any override/preset that changed the result |
| Ordinary and field-kit hauling | A bounded order of meals, medicine, materials, equipment, then the first-slice crew kit and return cargo | Pawn carry per trip before/after kit, trips, hauling jobs, elapsed game time, interruptions, and unfinished remainder |
| Storage | The silver example and a mixed warehouse of meals, gear, and ordinary stock | Cells/shelves used, filters, access, pathing, overflow behavior, and whether physical contents match UI totals |
| Ordinary cargo transfer | A small and a large ordinary item transfer between two RWT clients, using only supported online trade/gift; offline cargo only if enabled | Both client hashes, item/stack counts, recipient ownership, receipt, reconnect, save recovery, and any per-transfer limit |

The owner launches every profile through RimSort; do not start RimWorld directly or use GABS to launch. For every run, capture a short RimBridgeServer log or screenshot set and record the target profile, separate QA overlay, observed stack lists, total item count, pawn capacity, hauling job count and elapsed game time, storage occupancy, and post-reload totals. Repeat a case after changing only one setting. For a transfer, record source and destination counts before disconnect and after reconnect; do not treat a failed offline option as a supported route.

## Rimrooms-specific cases

After the build exists, load the complete first-slice crew kit and return cargo onto a pawn; test a paid company supply order as bounded physical batches, including delay/loss/recovery, cost and duplicate handling; and exercise Rimrooms-specific transfer/recovery workflows. Run the Core/OgreStack comparison and ordinary RWT cargo cases after the build as well.

## Acceptance rules

- USD balances and contract values create no physical silver; only an explicit procurement action creates goods.
- Every future Rimrooms shipment names its physical manifest, stage size, carrier/storage route, and failure/recovery outcome before dispatch; validate the custom shipment flow after implementation.
- A large order can be staged, stored, hauled, or declined without hiding items in a counter or forcing one pawn to move an impossible load.
- Core-only play works without OgreStack, storage expansions, vehicles, or DLC. Profile-specific settings improve convenience but do not become hidden campaign requirements.
- Save/reload and any tested RWT transfer preserve counts without silently deleting or duplicating physical stock.

## Run record template

For each case, append date, operator, game build plus executable/Core hashes, DLC, ordered package IDs and versions, save/profile hash, relevant mod settings, starting stock, actions, measurements, observed result, logs/screenshots, and pass/fail with a concise reason. Leave the result **Pending** until the run actually occurs; this document is a plan, not evidence.
