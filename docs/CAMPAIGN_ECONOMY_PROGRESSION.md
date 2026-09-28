# Rimrooms - Async Industries: campaign economy progression

**Status:** pre-code economy design, version 0.1. This fills in the campaign-level money and logistics rules around the first-month example. It is not a full price list, tested balance, or implementation. The linked [campaign economy model](CAMPAIGN_ECONOMY_MODEL.md) and [workbook](../outputs/4b7976f0-1820-4ffa-a191-bf7c7f79b010/Rimrooms_Campaign_Economy_v0.1.xlsx) remain the authority for the current Async Industries opening values.

**Feature route:** [RR-ECO](FEATURE_TRACEABILITY.md), [RR-FAC](FEATURE_TRACEABILITY.md), [RR-GATE](FEATURE_TRACEABILITY.md), [RR-EXP](FEATURE_TRACEABILITY.md), [RR-MSN](FEATURE_TRACEABILITY.md), [RR-OUT](FEATURE_TRACEABILITY.md), and [RR-MP](FEATURE_TRACEABILITY.md).

## Economy promise

The company earns money by doing work it can document: survey a route, recover requested goods, analyze evidence, rescue a crew, secure a site, or provide a client with a monitored space. Growth should come from better planning and wider reach, while payroll, power, consumables, repairs, leases, and supply runs create costs the player can understand before accepting them.

Credits and RimWorld items are separate. Credits pay company bills and quoted services. Steel, components, food, weapons, furniture, samples, and dossiers remain physical stock. Buying with credits creates an order and later a shipment; selling an item changes its physical custody and adds a separately recorded payment. Do not silently convert between company credits and silver.

All branch accounts remain local. A tested RWT item transfer may move physical resources or a dossier with a receipt; it does not merge company balances, completed research, contracts, or case authority.

## Campaign income and cost stages

These stages describe how the kinds of work and expense broaden. They do not promise fixed rewards or force one linear route. All later prices and quantities are **open balance inputs** until estimated, modeled, and playtested.

| Stage | Work that can earn income | Costs that begin to matter |
| --- | --- | --- |
| **1. First safe survey** | Accepted mapping or recording contract; its stated one-time payment and any documented safety bonus. | Five-staff payroll, headquarters overhead, food after the starter grant, gate power, repair materials, and field-kit replacement. Use the values in the first-month model. |
| **2. Repeat access** | Repeat surveys, route verification, evidence delivery, small retrieval jobs, and approved salvage sales. | More research and field time, gear wear, replacement shipments, extended openings, and higher-capacity storage. A longer gate window does not create automatic revenue. |
| **3. Specialist services** | Instrument readings, sample analysis, rescue searches, equipment recovery, and client-funded research deliverables. | Specialist pay premiums, secure sample handling, medical/quarantine supplies, client-specific equipment, and scheduled deliveries. A research insight is not cash unless a contract explicitly buys a physical or documented deliverable. |
| **4. Leases and remote sites** | Monitored-space leases, relay installation, site surveys, outpost services, resupply, and return contracts. | Lease terms, outpost upkeep, staff travel and wages, food, radio service, defense, storage, and evacuation reserve. The current provisional outpost operating/lease value is 17 credits per active day before separate wages and physical provisions. |
| **5. Large recovery and network work** | Multi-team surveys, time-limited town response, missing-crew recovery, high-value retrieval, and defended site contracts. | Larger crews, more exposure days, insurance/compensation candidates, damaged shipments, security upgrades, medical care, and opportunity cost when a specialist is away from headquarters. |
| **6. Vehicle and optional orbital support** | Cargo, reconnaissance, security, and salvage work linked to company transport; optional gravship operations only where the native system and verified bridge permit them. | Vehicle acquisition and maintenance, crew, fuel/material inputs where the selected system uses them, cargo handling, and off-world support. Native gravship finances and ship systems remain with their owning content unless an explicit, tested transaction is defined. |
| **7. Deep-site operations** | Exceptional survey or recovery contracts with declared scope and risk; sale of eligible findings; and longer-term access agreements. | Stabilization, specialized gear, relief crews, long-duration food and medical supply, outpost security, and possible route closure or rescue costs. A rare discovery is not a guaranteed windfall. |

The first-slice gate-duration ladder remains provisional: 20 minutes, then 2 hours, 1 day, 7 days, and 30 days. Every increase must account for staffing, food, maintenance, communication, power reserve, cargo, and a return/recovery plan. The paid survey is not required to prevent immediate bankruptcy under the opening forecast.

## What a quote includes

Before accepting a contract, lease, or order, show the player:

- client or supplier, requested work, deliverable, due date, access rights, and who owns the result;
- base payment or price, any advance, bonus, maximum penalty, cancellation rule, and partial-result payment if one exists;
- expected staff time, required equipment/materials, expected physical shipments, and which items can be lost or consumed;
- travel, gate-window, lease, communications, security, and outpost costs that begin because of the commitment;
- the stated risk conditions and what the company loses if it declines, delays, withdraws, or fails.

An advance counts against the contract's total payment. A bonus or penalty is paid only when the written condition is met. Penalties are capped in the accepted card. A partial result has a listed payment or it earns none; the settlement screen cannot invent a new amount.

For later tuning, a contract quote may be estimated from **work scope + expected staff time + required consumables and transport + disclosed risk and deadline premium + agreed access/service value**. This is a pricing guide, not a locked formula. The player sees the final amount before accepting, and every generated value is saved on that contract card.

## Cost and inventory rules

- **Payroll:** base pay applies to all employed staff. Any specialist premium is shown on the hire offer and roster. A pawn's company role does not remove ordinary RimWorld food, sleep, recreation, medical, or work needs.
- **Physical provisions:** food, ammunition, medicine, parts, protective gear, and replacement tools are items. A purchase charges credits once, creates a named order, and adds stock only on delivery. Starter grants are already owned stock and do not spend the account again.
- **Power and machine operation:** the base game power network determines available electricity. Credit costs apply only to a displayed purchase, service, or physical fuel order; never add an invisible fee merely because a gate draws power.
- **Maintenance:** track wear or a repair requirement on the item/building; quote the parts and labor before repair. Do not charge both a hidden flat expedition fee and full replacement for the same use.
- **Leases:** state the space, boundary, access/security conditions, start/end dates, upkeep, renewal, eviction, and abandonment effects. Rent starts on the accepted start date. Leaving a lease does not erase evidence, route records, or the company's claim history.
- **Outposts:** track local stock, staffing, signal, upkeep, defense, relief date, and exit. The current 17-credit daily provisional charge covers the site/lease and local service/communications only; wages, food, purchased supplies, and repairs remain separate.
- **Cargo loss:** every shipment records owner, contents, value basis, route, dispatch/delivery status, and receipt. A delayed or missing load is an incident with a recovery choice, not a debit-and-delete shortcut.
- **Research:** staff time and existing materials are used first. A purchased supply order is a separate cost. A knowledge unlock is not automatically saleable or transferable; physical dossiers follow the branch-local receipt rules.
- **Salvage and evidence:** show whether an object is eligible for sale, research, a client handoff, retention, or disposal. The same object cannot be paid as both a sale and a deliverable, and research value does not mint duplicate stock or cash.

## Loss, failure, and recovery

Failure must cost something the player was warned about, but it should not add surprise debt. Possible documented costs include wages during a delayed return, consumed field provisions, equipment wear, lost optional cargo, missed contract payment, or an accepted penalty. Injury uses ordinary treatment and recovery. Death, missing staff, or a failed delivery opens a case and may start a rescue, claim, or replacement decision; none grants a payment automatically.

The player may decline work, recall a crew, renegotiate before accepting a changed scope, or close an unprofitable lease under its stated terms. If a generated site or transfer fails before the player commits, do not charge for undelivered work or erase stock. If a shipment is lost after dispatch, preserve its receipt and offer only the recovery routes the game actually supports.

## Multiplayer and optional content

Keep ledgers, research completion, contracts, reputation, leases, and case records branch-local. Trade only physical goods through a verified RWT transfer path. A Research Dossier is a physical item that the receiving branch analyzes locally. Direct shared research remains disabled unless a documented supported RWT extension and duplicate-safe synchronization are established. Facility visits, trades, gifts, aid, and offline cargo each need their own pinned-build test; do not imply one works because another does.

Every DLC and profile mod remains optional except Core plus Harmony/RWT for co-op. External mods may supply useful systems or comparisons, but Rimrooms must preserve its Core-only economic route. An optional trade, hospitality, guest, or gravship mod cannot be the only way to purchase, sell, host, contain, or move required campaign content.

## Balance evidence still needed

The first-month workbook covers only the opening Async Industries account forecast. Before the campaign economy is considered frozen, create an editable model for at least:

1. the first 30-day opening with and without the survey payment and optional bonus;
2. repeat-access work over several months, including contract delays, gear replacement, hiring, and failed/abandoned expeditions;
3. a staffed lease and at least one outpost with wages, provisions, communications, repair, and evacuation reserve shown separately;
4. a long expedition at each provisional gate-duration tier, with provisions and relief timing;
5. a town-response or missing-crew contract with a disclosed deadline, partial outcome, rescue cost, and penalty cap;
6. vehicle/gravship logistics as a separate optional profile, not a required revenue shortcut;
7. a no-contract or lost-shipment case that remains recoverable without hidden credit generation.

Each balance pass records workbook/model version, assumptions, cash and physical stock separately, successful and failed outcomes, and the target RimWorld/DLC/mod profile. Until those cases are modeled and later playtested, the campaign price bands and late-game solvency remain open.
