# Rimrooms - Async Industries: campaign economy model

> **Superseded 2026-10-01 — dependencies.** This document predates the owner's decision that the
> package has hard dependencies. `About.xml` now declares all five expansions and the whole
> collection as requirements, so anything here describing a Core-only route is history rather than
> a current claim. Recorded as a change to D3 and D4 in
> [Gate 0 decisions](GATE_0_DECISIONS.md#decision-log).

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** pre-code economy model, version 0.2. Currency/physical-stock separation, ordinary RimWorld hauling, no automatic flat event cash, and the published OgreStack 67-stack planning example versus Core's 2,000-stack case are product rules. Opening costs, later prices, quotes, milestone targets, and recoveries in the linked [campaign economy workbook](../outputs/4b7976f0-1820-4ffa-a191-bf7c7f79b010/Rimrooms_Campaign_Economy_v0.2.xlsx) are editable design hypotheses, not tested balance or final owner approvals. The workbook models seven 30-day stage cases, separate service and lease receipts, penalties and cargo incidents, delayed/lost receipts and claims, optional VGE vehicle/gravship costs, itemized outpost costs, long expedition extensions, no-contract months, recovery, gated milestone releases, and the one-million-silver stack example. The pre-code category map is covered; owner approval, in-game balance, and mod/runtime validation remain open. Revise this note and workbook together.

**Feature route:** [RR-ECO](FEATURE_TRACEABILITY.md), [RR-FAC](FEATURE_TRACEABILITY.md), [RR-STA](FEATURE_TRACEABILITY.md), [RR-GATE](FEATURE_TRACEABILITY.md), [RR-EXP](FEATURE_TRACEABILITY.md), [RR-MSN](FEATURE_TRACEABILITY.md), and [RR-OUT](FEATURE_TRACEABILITY.md). Account totals and physical stock have different owners and records as defined in [CAMPAIGN_STATE_DICTIONARY.md](CAMPAIGN_STATE_DICTIONARY.md).

## Account scale and physical money

**Current procurement source:** [0.3.0-dev procurement](implementation/PHASE_3_PROCUREMENT_IMPLEMENTATION.md) adds an explicit provisional supplier catalog. Physical Silver is quoted at $1,000 per unit, so a one-million-unit order costs $1 billion before its real stack/storage/hauling constraints. This avoids the earlier draft's $1 silver shortcut around industrial goods prices. It is a supplier quote, not an automatic exchange rate or a tested balance result. The v0.2 workbook remains a historical planning model; reconcile its broader supplier/economy assumptions in the balance work before claiming calibrated progression.

- **The parent company is worth multiple trillions of dollars in the setting.** That valuation is corporate scale and story context; it is not a pile of spendable silver and does not make every division purchase free.
- **Company Account is a branch-local USD ledger.** For accounting, one displayed account unit equals one US dollar. The initial Async Industries division receives a provisional **$50,000,000 authorized project allocation**. This is a material operating budget with visible limits, not the parent company's full treasury. An approved funding release must be an explicit, recorded decision; no event silently refills the account.
- **Company cash is never a RimWorld item.** A $1,000,000,000 ledger balance is one account amount, not one billion silver, not stacks, and not pawn cargo. It can be saved, shared in UI summaries, and reconciled without hauling objects.
- **Silver remains physical stock.** In installed Core, Silver has a base stack limit of 500 and is tagged `smallVolume` (`Data/Core/Defs/ThingDefs_Items/Items_Resource_Stuff.xml`, `Silver`). The active 294-profile includes row 157, **OgreStack** (`Ogre.OgreStack`). Its published defaults apply a ×30 scalar to small-volume resources, so the planning example is 15,000 silver per stack and 67 stacks for one million silver, assuming the default preset and no per-item override. OgreStack settings can change this, so the effective limit must be read from the active save/profile at runtime. The Core-only fallback remains 500 per stack, or 2,000 stacks. See its [source review](research/reviews/mods/1447140290-Ogre.OgreStack.md) and [cross-mod interaction record](research/PRIORITY_PROFILE_INTERACTIONS.md#stack-size-cargo-and-shared-item-exchange-row-157--rows-122259--rwt). Do not represent the Company's cash balance with silver stacks.
- **No silent conversion:** normal RimWorld trade continues to exchange physical goods and silver. A company procurement or client sale uses an explicit company order/contract with a quoted USD amount, transaction ID, and physical shipment/custody change. If a vanilla trader transaction remains physical, its silver stays physical. A conversion between the two requires a separately visible, quoted, tested finance action.
- Each company transaction belongs to one player's branch. RWT does not imply shared balances; cross-branch movement remains a separately tested physical transfer with receipts.

## Async Industries opening targets

| Driver | v0.2 planning target | Rule |
| --- | ---: | --- |
| Parent-company scale | Multi-trillion-dollar valuation | Setting context only; not the player's available balance. |
| Authorized opening account | $50,000,000 | Local operating allocation for the Async Industries branch. |
| Physical silver | 150 silver | Small physical trade stock, separate from the Company Account. |
| Starting staff | 5 | All begin on the company roster. |
| Base staff pay | $5,000 per staff member per day | Editable target; specialist premiums and contracts are quoted separately. |
| HQ administration/comms | $25,000 per day | Does not stand in for electrical power or item purchases. |
| Food | Starter physical stock plus ordinary growing/cooking | Pawns eat physical meals. There is no automatic per-meal cash debit; an ordered food shipment has its own quoted invoice and physical delivery. |
| First survey payment | $5,000,000 | Paid once when the accepted AI-01 deliverables are accepted. It is a named opening contract, not a universal event payout. |
| Safety/documentation bonus | Up to $1,000,000 | Optional contract term, shown before dispatch; requires the listed returned records and crew. |
| Failure/late penalty | Up to $1,250,000 | Only if named on the accepted contract; hard-capped at 25% of the base payment. |
| New-hire setup | $100,000 per additional hire | One-time onboarding target; wages remain a separate visible cost. |
| Survey-kit replenishment | $750,000 per order | Editable quote for a physical shipment; no payment until ordered. |
| Research-material shipment | $2,000,000 per order | Physical supplies only; research itself uses evidence and staffed work. |
| HQ rent | $0 per day | The opening headquarters is already available. |
| Leased facility space | $100,000 per active day | Optional lab, warehouse, or protected rental space. |
| Outpost lease and service | $250,000 per active outpost day | A planning allowance for site/service/communications. Staff, physical stock, security, and shipment costs remain separate. |
| First opening window | 108,000 ticks (~30 real minutes at normal speed) | **Superseded the provisional 20 in-game minutes on 2026-09-28** by owner direction. Operational window, independent of dollar amounts. |
| First field team | Up to 3 pawns | A qualified operator remains at headquarters. Cargo capacity is further limited by actual carried kits, pawn capacity, return transfer capacity, receiving space, and time. |

These figures are balance targets for pre-code modeling. A player sees the full contract/order quote and consequences before accepting. No flat payment is generated merely because an event occurred, an entity appeared, or a room was discovered.

## First-month account example

The 30-day example begins with the five-person opening roster, starter physical supplies, no new hire, no outpost, no extra lease, no restock order, no bonus, and no penalty.

- Opening Company Account: **$50,000,000**
- One accepted AI-01 survey payment: **+$5,000,000**
- Payroll: 5 staff × $5,000 × 30 days: **−$750,000**
- HQ overhead: $25,000 × 30 days: **−$750,000**
- Food: **$0 automatic cash debit**; the colony grows/cooks from physical stock. Any purchased shipment would be itemized separately.
- Day-30 account: **$53,500,000**
- Without the survey receipt: **$48,500,000**
- Steady HQ payroll plus overhead: **$50,000 per day**, before optional orders, repairs, rent, outposts, or other contracts.

The margin protects the opening from an immediate softlock while making salaries, procurement, security, repairs, and expanding facilities matter. The workbook's figures remain hypotheses until run through actual campaign playtests.

## Work, discovery, sales, and the company scale

The player should operate a real RimWorld company settlement: build rooms, grow/cook food, craft gear and furniture, research, harvest, collect, store, trade, recruit, and dispatch. Physical production is governed by pawns, jobs, bills, power, stock, storage, and map space. A farm harvest or crafted component creates physical inventory; it does not create company cash until a sale/contract explicitly changes custody and posts a receipt.

Company revenue can come from accepted investigation/recovery contracts, commissioned research, analysis or licensing deliverables, facility services, leases, physical harvest/salvage sales, rescue work, and later transport/outpost operations. Each contract card names requested evidence or cargo, who owns it, base payment, advance, milestone/partial payments, optional bonus, **two or more routes to success**, penalty cap, and cancellation terms. **No card carries a deadline, ever** - see [the campaign chart](CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate). An advance counts toward the total. Settlement requires the matching delivered result and posts once.

Use these broad, editable balance bands as a starting point for generated offers, not a guaranteed payout table:

| Work scale | Early planning band | Examples of what earns it |
| --- | ---: | --- |
| Routine repeat survey or local service | $250,000–$5,000,000 | Verified route map, monitoring, ordinary equipment retrieval, or documented short survey. |
| Specialist study or controlled recovery | $1,000,000–$25,000,000 | Usable sample analysis, missing-person lead, staffed lab service, or requested recovery with custody and risk documented. |
| Town-scale response, major rescue, or defended site | $5,000,000–$100,000,000 | Several teams, high-value cargo, or a secured temporary facility. |
| Exceptional entity/site discovery or deep-network operation | $25,000,000–$500,000,000+ | Rare findings, high exposure, large logistics, sustained containment, or buyer-specific study/licensing rights. |

The actual quote is generated from scope, risk, staff time, required equipment and transport, buyer demand, deliverable quality, and ownership terms. Loot value comes from actual items, recovered people or equipment, research services, or a buyer who wants the evidence. A clue, kill, capture, or random event alone does not mint money. Rare discoveries can be worth millions to the right buyer, but players must recover, secure, document, analyze, and sell/license them to realize that value. A finding can also be retained for research or company use instead of sold.

Parent-company funding is a separate progression route: milestone requests can make larger approved budgets available, with a stated amount, requirement, and ledger receipt. This represents corporate authorization and does not replace player-run income, ordinary colony production, or trade.

## Bulk cash, carry, storage, and throughput

The money scale must not turn into a pawn-hauling tax. Keep these four limits separate:

1. **Cash capacity:** account totals are ledger values. Millions or billions never spawn as item stacks and have no pawn carrying cost.
2. **Pawn carry capacity:** expedition kits and physical finds use the game's actual item weights and pawn limits. Show mandatory kit weight first, then remaining cargo allowance. Do not promise capacity using only a fixed salvage number.
3. **Storage capacity:** real goods occupy real storage, with limits from item stacks, mass/volume, room capacity, climate/security, and permitted item types. Warehouses and later cargo facilities can expand these limits but must not become infinite hidden inventories.
4. **Handling throughput:** receiving, sorting, stacking, loading, and hauling consume time and labor. Show expected stack count, mass/space where available, available destination capacity, batch count, staffing/time, and risk before a large shipment is accepted.

For a physical commodity, planned stack count is `ceil(quantity / that item's effective stack limit)`. The one-million-silver illustration is **67 stacks with the active profile's published OgreStack default**, versus **2,000 stacks under Core's 500-item limit**. The generated estimate must use the effective in-save item limit; never assume a universal value or encode OgreStack's preset into Rimrooms. Never send physical silver as the default form of a million-dollar discovery payment. For actual bulk resources, offer a bounded shipment manifest with phased deliveries or a player-selected accept/reject/hold option. On arrival, reconcile the manifest to real items in receiving space; don't grant stock directly to a hidden counter or drop thousands of unannounced stacks onto the map.

Use physical containers, warehouses, pallets, vehicle holds, or automation only when the exact system has a bounded capacity, inspectable contents, workable load/unload jobs, and a tested path through the selected profile. Do not override vanilla stack sizes merely to hide a logistics problem. If space or staff throughput is insufficient, block or stage the order with a clear explanation and a recovery choice. Optional logistics mods can improve QoL but are not required to complete Core-only play.

Expedition dispatch likewise checks the complete kit, carry capacity remaining after mandatory equipment, route/exit transfer limit, receiving/storage room, and available time. The 30 kg optional first-slice salvage figure is only a test envelope; it cannot override a lower real capacity or strand the crew. Rebalance after measuring actual pawn loadouts and return behavior.

## Transactions and settlement

- The contract card and order show client/supplier, requested work or goods, amount in USD, advance, bonus, capped penalty, cancellation rule, shipment quantity, receiving site, expected arrival, and item ownership. **No deadline.** An expected arrival is the supplier's estimate of when goods turn up, not a clock the player is measured against.
- A generated amount is saved on that contract/order and is never rerolled at settlement. Partial credit is paid only if the contract listed a partial-delivery amount before dispatch.
- Physical goods remain items. A company purchase debits the ledger once, then creates a physical shipment. A sale/lease/service receipt records the accepted goods or service and posts once.
- Loss/damage removes only the physical item actually lost; replacement requires an explicit quote/order. Food, medicine, construction supplies, and power inputs must not be charged twice as both automatic fees and physical purchases.
- Every transaction is branch-owned and idempotent. A failed shipment remains visible and recoverable; retrying cannot debit twice.
- Research insight is not cash and does not transfer as an invisible number. A dossier can be sent only through a tested physical item route; its recipient performs local analysis. Research income requires an accepted research/analysis/licensing deliverable.
- Sale, study, archive, contain, release, hire, detain, interrogate, and transfer choices preview resulting value, ownership, custody, and risk before committing.

## Progression and operating limits

The first gate opening is **108,000 ticks, about thirty real minutes at normal speed** — this **supersedes** the provisional 20 in-game minutes recorded here before 2026-09-28, by owner direction, because a colonist cannot cross a gate, collect something, return and deliver in a shorter window. The access ladder is now **multiplicative: each earned tier multiplies the duration by three, and at the indefinite tier the countdown stops entirely while power, the operator and the energy supply all hold.** Tier is the count of completed company projects, never spendable insight. The earlier 2 hours / 1 day / 7 days / 30 days sketch is superseded as a duration schedule, though its operating requirements below still apply. Each increase needs explicit power reserve, maintenance, staffing, communication, supply, cargo, storage, security, and return planning. Longer openings increase operating and recovery exposure; they do not automatically pay more.

The implemented development machine uses provisional 250 W standby draw, 3,500 W opening draw and 250 W projected network headroom. A separate 2 Wd gate-owned capacitor charges through an accounted 1,000 W load; emergency return and a recovery activation each spend 1 Wd. These untested values replace the earlier 500 W / 2,000 W / 3,000 W draft and distinguish power from stored energy. See the [gate implementation](implementation/PHASE_2_GATE_IMPLEMENTATION.md). Power must not be converted into company dollars without an explicit fuel/material purchase. The first expedition allows three pawns and requires a qualified operator at the facility; physical cargo is then checked against the actual limits above. Pawn food, rest, health, movement, carrying, and ordinary work stay in RimWorld's simulation.

## Workbook case definitions and assumption ownership

The `Recovery & Capital` sheet gives every campaign stage an operating bridge: base-path opening balance, planned receipts, planned costs with any added quotes, no-contract close, recovery-case costs, recovery close before funding, explicitly approved milestone release, and recovery close after funding. The `Campaign Scenarios` sheet links the no-contract and recovery closes beside its planning and downside cases. `Extended Cases` adds editable per-stage inputs for distinct accepted service deliveries and earned lease days; a 25%-of-average-contract-value penalty cap; incident response/rescue costs; delayed or lost contract cash and accepted claim receipts; optional vehicle/gravship acquisition and operations; additional outpost hires/setup, defense, physical resupply invoices, communications, and evacuation; and cost extensions for expeditions beyond the 30-day case, including crew/day payroll, specialist premium, physical provisions, transport, replacement equipment, and rescue. The recovery block carries still-owed penalties and costs, committed replacement/vehicle/outpost/expedition obligations, and only service, lease, or claim receipts actually collected. These are cashflow cases and category coverage, not proof of balanced gameplay.

For traceable workbook entry points, `Extended Cases!B7:P13` holds receipt, penalty, incident, delay, and accepted-claim assumptions by stage; calculated outputs are in D/G/K/N/R. `B18:J24` contains the optional VGE and outpost inputs with total K; `B29:K35` contains expedition-extension inputs with total L; and `B40:R46` contains recovery commitments/realized-receipt inputs with totals S:T. These feed `Recovery & Capital!I7:I13` for added monthly costs, `C39:C45` for planned receipts, `E39:E45` for no-contract closes, and `F39:G45` for recovery costs/closes. Stage 2–7 base and downside results are linked in `Campaign Scenarios`; stage 1 inputs still use the existing `Economy` controls where indicated. Changing workbook layout requires updating these references and this map together.

Inputs shaded for editing are scenarios, not settled prices. Service and lease rates, specialist premiums, penalties, incident response, claims, transport, equipment/cargo replacement, VGE, outpost operation, long expedition extension, milestone request amounts, retained recovery staffing, site days, and orders have no owner-approved quote unless separately decided. A zero quote means “not supplied,” not “free.” Milestone release stays zero unless both completion and explicit approval are switched on. A no-contract case removes that month's core contract receipts and delayed contract cash while retaining only service/lease work earned and claims accepted/collected in its corresponding inputs. Recovery models adaptive cuts by allowing unstarted hires, optional orders and dispatches, and stoppable lease/outpost days to be omitted, while entered non-cancellable payroll, penalties, replacement, vehicle, site, expedition, and response obligations remain; enter binding commitments before relying on its projected close. Recovery hires, if any, add to retained payroll and food costs. All amounts remain unapproved planning hypotheses until owner review and playtesting.

Fixed product rules are the branch-local USD ledger, physical goods as physical inventory, actual pawn hauling and storage, no forced OgreStack dependency, and a Core-only solo campaign. OgreStack's default is a comparison assumption only; actual stack capacity must come from the active save.

## Balance work still open

The v0.2 workbook now covers the code-free cashflow categories listed above, but it is not a tested balance result and does not close the broader economy/logistics gate. Still required are owner review of the assumptions, implementation of quote and contract generation, contract/item-sale and accepted-claim cases, cost-cut/recovery choices, storage/haul capacity, delayed/lost physical shipments, marketplace interactions, and staged cargo handling. Validate ordinary play and a deliberately oversized one-million-silver case on disposable saves with and without OgreStack. Record game build, DLC, exact mod order, observed cargo and account results, and save/reload behavior. Keep company cash and physical inventory reconciled separately.
