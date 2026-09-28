# Rimrooms - Async Industries: campaign economy model

**Status:** pre-code balance model, version 0.1. Values are tuning hypotheses, not tested play balance. The linked [campaign economy workbook](../outputs/4b7976f0-1820-4ffa-a191-bf7c7f79b010/Rimrooms_Campaign_Economy_v0.1.xlsx) calculates the first 30-day Async Industries example plus editable 30-day planning and downside cases for campaign stages 2–7. Later prices and solvency remain open. Update this note and workbook together when a rule or value changes.

**Feature route:** [RR-ECO](FEATURE_TRACEABILITY.md), [RR-FAC](FEATURE_TRACEABILITY.md), [RR-STA](FEATURE_TRACEABILITY.md), [RR-GATE](FEATURE_TRACEABILITY.md), [RR-EXP](FEATURE_TRACEABILITY.md), [RR-MSN](FEATURE_TRACEABILITY.md), and [RR-OUT](FEATURE_TRACEABILITY.md). Account totals, reputation, and company research belong to the owning local campaign branch as defined in [CAMPAIGN_STATE_DICTIONARY.md](CAMPAIGN_STATE_DICTIONARY.md).

## Money and physical stock

- **Company credits** are a local company ledger for wages, contracts, procurement, leases, and service costs. Each entry records a unique transaction, amount, reason, and owning branch. No credit balance is shared by implication.
- **Silver, materials, food, weapons, furniture, and evidence** are physical RimWorld items. Credits are not a replacement for a physical order: a purchase posts once, then creates a shipment and later physical stock. An item cannot also be claimed as a cash reward.
- **Vanilla trade** uses its normal physical goods and silver. Do not invent an exchange rate between credits and silver. For RWT, only verified item or dossier transfer routes may move supported objects; credits and research stay local.
- Starting inventory is an already-owned resource grant. Its original purchase is outside the new-save cash forecast. Consumed, damaged, sold, lost, or transferred stacks must still be reconciled against their physical manifest.

## Async Industries opening values

| Driver | v0.1 starting value | Rule |
| --- | ---: | --- |
| Company credits | 900 | Starting branch balance. |
| Physical silver | 150 | Petty cash for ordinary vanilla trade; separate from credits. |
| Starting staff | 5 | All staff begin on the company roster. |
| Base pay | 2 credits per staff member per day | Applies to employed staff, including staff not on an expedition. Specialist premiums are not in the first slice. |
| HQ overhead | 4 credits per day | Covers routine company administration and communications. It does not represent RimWorld electrical power or purchased physical goods. |
| Starter food coverage | 5 days for the starting roster | Food and rest use vanilla pawn needs. After the starter stock runs down, model replacement provisions at 1 credit per person-day when ordered. Food still arrives as physical items. |
| First survey payment | 240 credits | One-time payment only after the accepted onboarding survey has a valid extraction and evidence record. |
| Safety/documentation bonus | 60 credits | Optional. Pays if all three first-slice crew return with the route, distortion, and entity-observation records. A recoverable injury does not cancel the bonus. The base forecast assumes it is not earned. |
| Failure/late penalty | Up to 60 credits | Never more than 25% of the original 240-credit reward. Only a named, accepted contract term can create a penalty. |
| New-hire setup | 25 credits per additional hire | Applies only after the start roster, for onboarding, not a transfer of pawn ownership. It is not included in the starting balance forecast. |
| Basic survey-kit restock | 40 credits per order | A quote for a physical replenishment shipment; not charged unless ordered. The starter kit is already stocked. |
| First research project | 1 insight and one staffed workday | Gate Telemetry spends the first contract insight and ordinary researcher time. Existing physical supplies are used first; a paid materials order is a separate ledger transaction. |
| HQ rent | 0 credits per day | The Async Industries headquarters is owned/available in the opening. |
| Leased facility space | 8 credits per active day | Optional later laboratory, warehouse, or protected rental space. No charge before the lease starts. |
| Outpost operation and lease | 17 credits per active outpost day | 5 credits for site/lease and 12 for local service/communications. Staff wages and physical food/supplies remain separate so they are not double counted. |
| Reputation | Starts at 0; bounded from -20 to 100 | Complete a contract: +5. Meet its declared safety/documentation condition: +2. Fail an accepted contract: -2. Deliberately abandon a crew or breach a signed obligation: -5. Reputation can qualify future offers; it never posts cash by itself. |

All prices are provisional and quoted before the player commits. If a generated contract has a different amount, its saved card is the authority for that contract. No random unannounced fee may be added at settlement.

## First-month calculation

For the 30-day example, one successful onboarding survey produces the 240-credit payment. No safety bonus, failure penalty, new hires, restock, research materials order, lease, or outpost is included by default.

- Starting balance: 900 credits
- Successful first survey: +240 credits
- Payroll: 5 staff × 2 credits × 30 days: −300 credits
- HQ overhead: 4 credits × 30 days: −120 credits
- Food resupply: 5 staff × 25 uncovered days × 1 credit: −125 credits
- End of day 30: 595 credits

The five starter food days cover the first 25 person-days of the forecast, so only the remaining 25 days require a provision order. Without the survey payment, the same model ends at 355 credits. This prevents the first contract from being the only way to avoid immediate bankruptcy, while making continued operations depend on completing work or cutting costs. The steady-state daily cash outflow after starter food runs out is 19 credits for the five-person, no-outpost HQ. The workbook exposes the assumptions and formula rows for editing.

The company does not debit a flat expedition fee on top of consumed equipment. Gear use is reflected by physical loss, wear, replacement orders, or a contractually quoted service cost. Keep the cash ledger and item manifest separate, then reconcile them in the expedition report.

## Later-stage workbook cases

The workbook's `Campaign Scenarios` sheet rolls a 30-day planning case and a downside case through repeat access, specialist services, remote sites, large recovery work, optional vehicle/orbital support, and deep-site operations. The planning case starts from the existing 595-credit successful opening. The downside starts from the 355-credit opening with no survey payment, then assumes fewer completed and paid contracts while keeping the planned staffing and operating costs. Every later contract count, average payment, roster size, and nonzero support-cost placeholder is editable and marked as an estimate.

The cases carry forward the first-slice base payroll, food, overhead, onboarding, restock, material, outpost, and facility rates. They do not include specialist pay premiums, itemized maintenance/medical/transport quotes, client-lease income as a separate line, contract penalties, partial-result terms, item sales, changing costs in response to shortfalls, or a tested vehicle/gravship budget. A negative closing value is a funding gap in the proposed spending plan; it does not define an account that can borrow or carry debt. Company credits remain separate from silver and physical inventory.

## Contract, procurement, and recovery rules

- The contract card shows client, requested result, payment, advance, deadline, bonus, penalty cap, and cancellation rule. A 300-credit advance proposed for the Furniture & Knickknack Store start counts against that contract's total payment; it is not extra revenue.
- Research and survey contracts pay for documented deliverables. A crew returning safely with useful evidence is a valid outcome; killing or capturing an entity is not the default objective.
- A partial result can pay only when the contract listed a partial-delivery amount before dispatch. Otherwise, an incomplete result posts no payment and no surprise penalty.
- An order shows price, quantity, supplier, arrival window, receiving location, and risk. Payment is recorded once at acceptance. Delays or losses remain visible in the order record; retrying cannot debit twice.
- Loss or damage to company equipment reduces physical stock. A replacement costs the quoted order amount and arrives as a shipment. A pawn injury uses ordinary medicine, work, rest, and recovery; any compensation payment must appear in an accepted contract or explicit incident choice.
- Sale, study, archive, contain, release, hire, detain, or transfer choices are exclusive where the same object cannot logically serve two outcomes. The player sees the resulting value and custody change before committing.

## Progression and operating limits

The first gate opening is 20 in-game minutes. A provisional access ladder is 2 hours, 1 day, 7 days, then 30 days. Each increase needs explicit technology, power reserve, maintenance, communication, staffing, and a return plan. Longer durations increase payroll, food, field wear, and resupply exposure; they do not automatically increase revenue.

For first-slice balancing, use a 500 W draw while the gate is on standby and a 2,000 W total draw while it is open. Reserve 50% above the active open-gate draw, for a 3,000 W capacity target. These are machine-building balance hypotheses, not claims about RimWorld power APIs or verified electrical costs. Fuel or materials used by optional generator mods are physical inventory and must remain optional.

First-slice dispatch allows three pawns plus carried kits, requires a qualified operator to remain at the facility, and caps optional bulk salvage at 30 kg. Crew must be able to work, have at least 60% rest, and have no untreated condition that prevents the assigned role. RimWorld continues to own pawn food, rest, health, movement, and carrying behavior; the company layer gives a readable readiness explanation.

Research uses named evidence/insight plus ordinary staffed research work. One insight is awarded for the first valid survey. It cannot be sold or transferred as a hidden number. A physical dossier may be transferred only through a tested RWT item route; the receiving branch must analyze its own copy. Research costs no extra credits unless it creates an explicit procurement order for physical materials.

## Economy not yet balanced

The workbook is a planning scaffold, not a full simulation or tested balance. Threat capture/sale, specialist salary, long expeditions, vehicle or gravship operations, insurance/compensation, tax, auction prices, rival companies, changing plans after a shortfall, and complete outpost logistics still need design, itemized estimates, and later playtesting. The selected 294-mod profile may affect ordinary trade and production; it never changes the standalone Core-only ledger rules without a verified integration decision.

