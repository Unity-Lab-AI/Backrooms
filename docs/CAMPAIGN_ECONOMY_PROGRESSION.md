# Rimrooms - Async Industries: campaign economy and logistics progression

**Current content rule (owner, 2026-09-28):** [Repurpose existing game/mod content](CONTENT_REUSE_POLICY.md). Earlier instructions to create gameplay items, benches, sprites, textures or audio are superseded. Historical implementation facts remain evidence of the older build, not permission to ship those custom objects/assets. Original RimWorld-style Backrooms main-menu images are the approved visual exception; gameplay content must use existing providers.


**Status:** pre-code design, version 0.2. Read with the canonical [economy model](CAMPAIGN_ECONOMY_MODEL.md) and [v0.2 workbook](../outputs/4b7976f0-1820-4ffa-a191-bf7c7f79b010/Rimrooms_Campaign_Economy_v0.2.xlsx). Physical-versus-ledger rules and the Core/OgreStack planning comparison are product rules; all opening amounts, rates, quotes, and milestone targets remain editable hypotheses pending owner approval and playtests. The parent is a multi-trillion-dollar corporation; each scenario controls its own authorized budget and earns growth through play.

## Economy promise

The company account is a branch-local USD ledger. One account unit represents one dollar for company transactions; it never becomes physical silver. Ordinary RimWorld silver and goods remain real items. A company purchase or sale requires a visible quote and a receipt, and physical cargo appears as items only when its shipment is delivered. There is no automatic conversion between the ledger and silver.

Players still build and operate a RimWorld settlement. They grow and cook food, craft equipment and furniture, research, harvest, collect, store, trade, hire, build outposts, and send expeditions. Those activities use ordinary pawn jobs, work, power, maps, bills, stockpiles, and physical items. A harvest becomes company cash only when the player accepts an actual sale or contract that transfers custody.

Every contract is valued for its deliverables and circumstances. It names the buyer, scope, evidence or cargo, ownership, staff time, equipment, risk, amount, advance, optional milestone/bonus, partial outcome, penalty cap, cancellation, logistics, and **two or more routes to success**. **It names no deadline** - see [the campaign chart](CAMPAIGN_CHART.md#11-the-only-clock-is-the-gate). A room discovery, combat event, or entity sighting alone pays nothing. A recovered or studied finding can command millions when evidence, condition, buyer demand, risk, and rights make it valuable. Players may sell/license it, keep it for research, archive it, or use it in company production.

## Seven campaign stages

Stages describe expanding work and capacity, not a locked mission ladder. The amounts below are broad target bands, not guaranteed drops or final canon; contract cards store the chosen amount before the player commits.

| Stage | Income and work | Costs, capacity, and new choices |
| --- | --- | --- |
| **1. First safe survey** | Opening branch allocation; one accepted mapping/recording contract, target payment $5,000,000 plus an optional $1,000,000 records bonus. | Five-staff wages, company overhead, existing physical food/stock, gate power, first repairs and visible shipment invoices. |
| **2. Repeat access** | Verified routes, returned equipment, ordinary salvage sales, repeat surveys; planning cases use roughly $250,000–$5,000,000 per routine contract. | More field kits, replacement costs, delivery windows, safer receiving/storage, and short-haul labor. |
| **3. Specialist services** | Sample analysis, commissioned research, equipment recovery, missing-person leads; planning cases range roughly $1,000,000–$25,000,000. | Specialist premiums, controlled/quarantine storage, lab space, medical supplies, and trained handling jobs. |
| **4. Leases and remote sites** | Monitoring, relay installation, local services, site leases, resupply, and return contracts; scope-dependent millions or tens of millions. | Outpost wages, communications, defense, stock, cold/secure storage, and evacuation reserves. |
| **5. Large recovery and network work** | Multi-team surveys, town response, rescue, high-value retrieval, and defended-site work; larger contracts may reach $5,000,000–$100,000,000. | More crews, relief shifts, shipment handling, recovery/medical capacity, damaged goods, and deep warehouse upgrades. |
| **6. Vehicle and optional orbital support** | Transport, reconnaissance, security, cargo, salvage, and service contracts; late logistics can reach tens or hundreds of millions. | Native vehicle/gravship costs, cargo holds, route support, acquisition/maintenance, and tested optional integrations. |
| **7. Deep-site operations** | Exceptional study, containment, route network, or site rights; $25,000,000–$500,000,000+ is a provisional range for rare, buyer-specific outcomes. | Extended provisions, stabilizers, multiple safe storage sites, replacement teams, threat response, and rescue/closure reserves. |

The workbook's planning and downside cases use a single average core contract value per stage to make cashflow editable, then layer separate accepted service receipts and earned lease receipts onto the monthly bridge. Its `Extended Cases` sheet also models capped penalties, cargo/crew response costs, delayed/lost contract receipts and accepted claims, optional VGE vehicle/gravship acquisition and operating quotes, itemized outpost costs (additional hires/setup, security/defense, physical resupply shipments, extra communications, evacuation), and expedition extensions beyond 30 days (crew pay, specialist premium, provisions, transport, replacement gear, rescue). `Recovery & Capital` carries a 30-day no-contract close and a recovery close for each stage; the recovery block includes still-owed penalties, response and replacement obligations, optional transport/outpost/expedition commitments, and only receipts actually realized. Milestone targets remain editable and release no funds unless completion and explicit approval are both set. The recovery inputs represent adaptive cuts through retained staffing and stoppable/optional work choices; they are not an automatic austerity system. All values remain unapproved hypotheses, not tested balance or proof that later stages are balanced. Actual offer generation must use scope, deliverables, costs, risk, time, buyer demand, and rights.

Workbook data path: stage receipt/penalty/incident inputs and calculations are in `Extended Cases!B7:R13`; optional VGE/outpost values and total are in `B18:K24`; long-expedition extension values and total are in `B29:L35`; recovery obligations and realized cash inputs/totals are in `B40:T46`. `Recovery & Capital!I7:I13` adds monthly scenario costs; `C39:C45` reports planned receipts, `E39:E45` no-contract closes, and `F39:G45` recovery costs and closes. Stage 2–7 scenario outputs remain linked in `Campaign Scenarios`. These ranges describe the current workbook layout and must be revised alongside formula changes.

## Company capital, costs, and receipts

- Keep the parent-company valuation separate from branch cash. The $50,000,000 starting allocation and the workbook's illustrative $25 million to $1 billion later-stage request targets are editable scenario amounts, not final approvals. Larger allocations require a visible milestone request/approval and a one-time branch receipt.
- Record wages and account-funded orders once. The first five staff and HQ overhead use provisional values from the economy model; additional hires, specialist pay, service contracts, leases, repairs, transport, and physical procurement have separate quoted lines.
- Food and crafted goods are physical stock. Pawns consume food in the ordinary simulation; do not subtract an automatic cash amount per meal. Growing or cooking creates physical stock; a food shipment charges only its accepted order price.
- Client payments and salvage/research sales attach to actual deliverables and custody receipts. Partial results, bonuses, deductions, damage, and penalties must appear on the accepted contract or incident choice before work.
- A credit advance reduces the remaining contract amount. Milestones do not duplicate a full payment. No random event grants a flat payout, debt, or bailout.
- Failure still has a visible cost: wages during delay, used supplies, equipment loss, missed receipt, or a named penalty. Injury follows RimWorld treatment/recovery; an injured employee is not an automatic cash payout.

## Cargo and warehouse progression

Cash, carried load, stored stock, and hauling throughput have separate limits. The implementation plan and tests must preserve the following behavior:

| Layer | Rule | What progression improves |
| --- | --- | --- |
| **Account** | Dollar totals remain ledger entries. They never spawn as silver or require hauling. | Larger approved branch allocations and contract authorizations; not larger item piles. |
| **Carry** | Actual pawn carry/inventory limits apply after mandatory kits, food, and tools. Dispatch previews cargo still available. | Better kits, more crew/relief, dedicated carriers, and verified vehicle holds. |
| **Storage** | Physical inventory occupies real bounded storage, with item stack, capacity, access, security, and preservation limits. | Receiving bays, stockpile capacity, warehouses, cold/quarantine rooms, and containers with tested contents and limits. |
| **Throughput** | Loading/unloading, sorting, and hauling use time, pathing, labor, and available job capacity. | More staff, better routes, staged schedules, compatible material handling, and optional transport automation. |
| **Shipment** | A manifest lists actual quantity, estimated stacks, size/weight where available, destination, batches, delivery window, and loss risk. | Larger batches only when the destination and staff can accept them; pause, redirect, or split shipments when full. |

The Core Silver definition has a 500-item base limit and is tagged `smallVolume`. The active profile includes row 157, **OgreStack** (`Ogre.OgreStack`); its published default multiplies small-volume resource stacks by 30. That gives 15,000 silver per stack, or 67 stacks for one million silver, when that preset is active and no item override applies. Core-only fallback is 2,000 stacks. See the [OgreStack review](research/reviews/mods/1447140290-Ogre.OgreStack.md) and [profile interaction map](research/PRIORITY_PROFILE_INTERACTIONS.md#stack-size-cargo-and-shared-item-exchange-row-157--rows-122259--rwt). The current saved preset still needs runtime inspection. Do not represent company account balances as physical silver. For any physical quantity, calculate `ceil(quantity / effective in-save stack limit)` and show the expected stacks before dispatch or order acceptance. Bulk cargo must arrive in bounded stages or a tested container/warehouse route; never silently spawn an enormous delivery or store real inventory only as a hidden number.

Do not alter vanilla stack limits just to reduce the hauling burden. Review the exact storage/stack/carry mods in the 294 profile and prove the chosen treatment on disposable saves. Optional mods may ease routine logistics, but the Core-only path must remain playable. If receiving capacity, pawn load, or hauling time is inadequate, explain the constraint and offer hold, split, reroute, sell, or decline choices.

## Multiplayer boundary

Each player's company account, facility, contracts, research, stock, and maps remain branch-local. RWT cargo exchange moves supported physical items with a receipt; it does not move account balances. A received shipment is counted at the recipient only after delivery succeeds. The exact vanilla silver, resource, large-stack, dossier, and container transfer cases require separate testing.

## Freeze and balance evidence still required

The code-free category model is complete for the requested seven-stage monthly cases; the full economy and logistics contract is not frozen. Implement and test priced contract/partial-delivery/sale/claim cases, adaptive cost-cut choices, milestone funding, storage and haul limits, batch/delivery policies, physical inventory reconciliation, and cargo recovery. On disposable builds, test ordinary carry/storage and both the active-profile OgreStack settings and Core-only 2,000-stack one-million-silver example. Capture item stacks, mass/space, hauling jobs and time, stockpile capacity, shipment receipts, and save/reload behavior. Record build, DLC, exact mod order, and observed result; owner review and actual playtest balance remain pending.
