# 294-Mod Review Roadmap

**Purpose:** coordinate the source-by-source review of the selected RimWorld profile before implementation. This is a research workflow, not a compatibility certificate. The owner wants the lead agent to check and write the canonical records after research agents report back.

## Review contract

- The complete ordered input is [`rimworld-server-mod-inventory.csv`](rimworld-server-mod-inventory.csv); preserve its row number, display name, and Workshop ID. The companion workbook is the filterable review register.
- RimWorld Core is the solo baseline. Harmony and RimWorld Together are required only for the chosen co-op path. All other profile entries, including DLC and VGE content, remain optional under the [optional-mod policy](OPTIONAL_MOD_SUPPORT_POLICY.md).
- Research each row's exact publisher page and, when relevant, its upstream source or official documentation. Use the installed metadata and declared relationship snapshots as local evidence, not as proof of support.
- Separate publisher claims, local package facts, our design interpretation, and reproduced runtime behavior. A page/source review does not establish compatibility. Do not infer a license or API from a mod name, mirror, removal banner, or another mod's documentation.
- Do not copy, repackage, or suggest vendoring another mod's code or assets. Record the public extension point, dependency, load-order advice, version limits, known interaction, and license statement only as supported by evidence.
- Keep the report readable and proportional to the mod. For a small visual/QoL mod, record what it changes, where that overlaps Rimrooms, its dependency/version/license status, and whether Rimrooms should leave it alone. Reserve code-hook detail for mods where a feature could touch the same game state.
- Every reviewed Workshop row gets one local record at `docs/research/reviews/mods/<workshop_id>-<package_id>.md`; official Core/DLC rows use `docs/research/reviews/mods/official-<load_order>-<package_id>.md`. Record `FeatureTraceIDs`, `ReviewRecord`, `ReviewStatus`, `FinalDisposition`, `EvidenceBuild`, and `AcceptanceEvidence` in both CSV and workbook. Assign `None—verified unrelated` only after checking why it has no meaningful overlap.
- Use only these evidence statuses: `Pending`, `Reviewed—source facts recorded`, or `Runtime tested—profile details recorded`. `Runtime tested` requires a saved reproduction record with exact game/DLC, mod order, relevant RWT versions, save/logs, steps, and observed behavior.
- Keep proposed dispositions provisional until evidence is complete: native feature, configuration only, optional adapter, compatibility patch, verified alongside/no touch, or unsupported/conflict. Do not mark a mod “integrated” merely to make the list appear complete.

## Agent work and lead-agent intake

Research agents work in bounded, non-overlapping batches, use the review template and this project roadmap, and return findings to the lead agent. Agents must not edit the canonical CSV, workbook, source register, or design documents unless the lead explicitly delegates that exact edit. If a design choice changes the review, ask the lead agent; do not contact the owner directly.

For each row, return:

1. Exact inventory row, Workshop title/ID, package ID if verified, and installed version/build if present in the local snapshot.
2. Direct source URLs and date checked; source sections or code paths when useful.
3. What the publisher/source actually says about behavior, dependencies, incompatibilities, supported game versions, load order, and license/redistribution.
4. Public API or patch surface only when examined and relevant; name an inaccessible or unverified source plainly.
5. Likely Rimrooms overlap and a provisional disposition with feature IDs. Mark interpretation as interpretation.
6. A short list of unresolved questions and the exact isolated/full-profile runtime check needed. Never report a test that was not run.

The lead agent checks row identity, source quality, and evidence level; resolves disagreements; writes or edits the canonical review; then updates the CSV and workbook together. It adds confirmed named interactions to the priority-pair record and updates the feature map/TODO only when the evidence changes a design requirement. After each wave, reconcile reviewed/pending counts and verify links and row parity.

## Queue order

Work from the highest player/system overlap to the remaining profile, while ensuring every pending inventory row eventually receives one review or a documented unrelated disposition:

1. **Gate, energy, security, and research:** gate/portal systems, power generation and storage, defenses, research benches and UI, alarms, and communications.
2. **Operations, missions, and economy:** quests, incidents, faction/site/world-map changes, contracts, traders, guests, procurement, shipping, cargo, and selling.
3. **Staff, care, and containment:** pawn/work/job changes, hiring and visitors, medicine, training, prisoner/custody/interrogation, injuries, entities, and anomaly systems.
4. **Space and production:** procedural map/terrain, storage, building/materials, vehicles, caravans, outposts, gravships, and space travel.
5. **Frameworks and shared patches:** Harmony and other libraries, mods that patch the same defs/jobs/UI, declared dependency chains, and interaction clusters.
6. **Remaining quality-of-life, visual, balance, and decoration mods:** record practical role, optionality, dependencies, and known overlap; no adapter is needed when the mod simply coexists.
7. **Core and DLC rows:** map each official game/DLC layer to the campaign and identify the required vanilla fallback; use official 1.6 documentation and local Def/package evidence rather than Workshop pages.

The inventory CSV is the exact queue and source of row identity. Batch boundaries can cross load-order ranges to keep related systems together, but do not assign a row twice. Add newly discovered high-risk pairs to the priority list with an explicit evidence level.

## Current wave

The authoritative tracker now lists 291 accepted source reviews and 3 pending rows. All three pending rows (96, 237, and 278) have linked partial notes that record the evidence gap and the next source check. Each accepted row has a linked source note, feature mapping, and provisional disposition in the CSV and workbook. No combined-profile compatibility is established by these source notes.

The first and second waves completed source review and lead intake on 2026-09-27:

| Batch | Assigned rows | Focus |
| --- | --- | --- |
| Facility / power — complete | 39, 49, 84, 86, 110, 167, 194, 217 | Gate-adjacent energy, lab and industrial operation |
| Economy / quests — complete | 59, 62, 100, 132, 148, 183, 229, 231, 232 | Contracts, exploration, factions, trade, cargo and selling |
| Custody / staff — complete | 151, 169, 170, 171, 173, 175, 176, 192 | Prisoner, restraint, recruitment and custody interactions |
| Gate / world batch — complete | 58, 63, 124, 163, 218 | Terrain, map controls, and Stargates |
| Staff / custody batch — complete | 109, 172, 174, 177, 182, 236, 270, 285, 287, 292 | Hospital, prisoner options, containment-adjacent systems, and guests |
| Space / trade batch — complete | 131, 154, 249, 251, 255, 282, 283, 290, 294 | Ship parts, orbital trade, vehicle expansion, and salvage |
| Security / research — complete | 20, 191, 211, 234, 279 | Faction incidents, research trees, turrets and research controls |
| Staff / medical / work — complete | 34, 67, 99, 126, 146, 209 | Animal care, work UI, medicine, IVs and alerts |
| Storage / transport — complete | 46, 61, 82, 91, 98, 122, 259, 266 | Caravans, vehicles, map display, storage and freight |
| Weapons / scanner / mechanoid — complete | 21, 42, 223, 250, 291 | Weapon sales, asteroid mining, surrogate mechanoid, and vehicle weapons |
| Facility doors / power — complete | 77, 185, 187, 201, 252, 265, 276 | Door systems, access, vault structures, and power poles |
| Health / facility / hospitality — partial | 44, 47, 88, 96, 274, 286 | Five accepted; row 96 partial note pending direct page review |
| Animals Logic supplemental — complete | 38 | Publisher-documented overlap with predator-targeting row 234 |
| Medical / containment follow-up — accepted | 105, 108, 120, 166, 168, 178, 179, 193 | Post-mortem, medicine, surgery, prosthetics, and tending |
| Materials / logistics follow-up — accepted | 101, 107, 113, 116, 125, 128, 144 | Materials, hauling, food delivery, and production |
| Resource / caravan follow-up — accepted | 115, 127, 143, 152, 157, 159, 160 | Strategic weapons, mining, manufacturing inputs, storage stacks, and pack animals |
| Animal care / pawns — accepted | 23, 27, 28, 31, 32, 33, 35, 36, 37, 48 | Animal equipment, care, memories, prosthetics, and recreation |
| Combat / equipment / defense — accepted | 50, 54, 80, 90, 104, 137, 139, 161, 162, 198 | Combat presentation and pawn/weapon control; record only verified overlap |
| Operations / furniture / source follow-up — accepted with one partial | 30, 40, 41, 43, 55, 57, 64, 65, 66, 75, 96, 127 | Utility/build planning, player UI, work QoL, recreation; row 96 remains pending after direct-page retry |
| Facility / production — accepted | 189, 195, 212, 219, 226, 246, 253, 254, 256, 257 | Construction, storage, heat/cooling, production and facility care |
| Staff / visitors / custody — accepted | 213, 214, 215, 225, 227, 258, 269, 272, 273, 275 | Visitor behavior, recovery, medicine, life support, locks, and non-lethal custody |
| Core, DLC and room systems — accepted | 4, 5, 6, 7, 8, 9, 184, 186, 188, 190 | Official base/DLC source review plus room, recipe UI, roof and plant support |
| Staff health / pawn care — accepted | 22, 45, 52, 68, 70, 71, 72, 78, 87, 93 | Apparel, body condition, death/health, animal handling, incubators, and food-poisoning recovery |
| Genes / training / entity names — accepted | 51, 94, 112, 114, 117, 121, 129, 138, 140, 141 | Biotech gene workflows, research/crafting, training, anomaly entity controls, and name systems |
| Work UI / materials / utility — accepted | 69, 73, 74, 79, 81, 85, 89, 92, 95, 97 | Terrain recipes, item control, alerts, selection/menus, pawn setup, implants, floors, performance and resources |
| Misc audio utility — accepted | 74 | Startup warning/error sound utility; unrelated to Rimrooms systems; no runtime test |
| Staff / social / needs — accepted | 102, 103, 111, 118, 119, 123, 130, 142, 197, 238 | Appearance, traits, needs, romance, skill growth, and staff recreation |
| Animals / terrain / maps — accepted | 127, 133, 134, 135, 136, 145, 147, 150, 153, 155 | Mining discovery, pen filters, linkables, animal products, biomes, hazards, flares, error handling, and pawn readouts |
| Work / logistics / gear — accepted | 156, 158, 164, 165, 180, 181, 199, 200, 204, 205 | Gene inheritance/banks, hauling/plant work, quality controls, combat jobs, hand visuals, and sidearms |
| Production / materials / events — accepted | 53, 69, 73, 92, 97, 106, 127, 149, 202, 207, 208, 216, 221, 222, 230, 267, 271, 293 | Source-reviewed construction/materials, item disposal, events, apparel, furniture and salvage |
| Interface / staff / social — accepted with one partial | 79, 81, 85, 95, 96, 203, 210, 233, 235, 237, 239, 240, 242, 243, 244, 245, 248, 260 | Source-reviewed selection, menus, scenario setup, performance, apparel/traits, recreation, animal care and haul workflows; row 237 remains pending direct source review |
| Combat / medicine / mobility — accepted with one partial | 89, 206, 220, 224, 228, 241, 261, 262, 263, 264, 268, 277, 278, 280, 284, 289 | Source-reviewed implants, custody apparel, fire response, cover, harvesting, weapons, vehicles, scheduling, defenses and materials; row 278 remains pending direct source review |
| Publisher-source refresh — four accepted, three partials remain | 96, 127, 237, 262, 268, 278, 280 | Fresh primary Steam descriptions/author statements confirmed rows 127, 262, 268, and 280; rows 96, 237, and 278 remain pending |

Waves 1–9 completed lead intake with two partial records (rows 96 and 127). Wave 10 received three non-overlapping agent reports; the lead accepted 45 additional rows. A fresh source refresh accepted row 262 from its English-language publisher page, and this final primary-source lookup also accepted rows 127, 268, and 280, bringing the new intake to 49 rows. Partial notes remain for rows 96, 237, and 278. The tracker now has 291 accepted rows and 3 pending rows, all linked to an accepted or partial review record. Rows 96, 237, and 278 remain pending because current publisher-source access or sufficient source detail is missing; do not promote a title, indexed fragment, or secondary reference into a confirmed feature/license claim. Some accepted notes rely on exact-ID publisher-page text or upstream repositories and state that limit. None establishes full-profile compatibility. Agents report findings and questions to the lead; the lead writes canonical notes, decides interaction-map entries, and reconciles CSV/workbook counts. No agent asked for design guidance. Continue assigning newly pending source tasks in non-overlapping batches. Earlier reviews preserve unresolved rights/version boundaries for selected forks (notably rows 71, 78, 81, 89, 92, 112, 114, 117, 129, 140, and 141), local/publisher DLC mismatches on rows 72 and 140, and untested medical, gene, RWT, and DLC behavior. Medical Dissection (274) has the publisher multiplayer warning and is awaiting owner direction on co-op scope; do not claim RWT support. Rows 17 and 288 have existing review records useful for interaction cross-checks. Questionable Ethics Enhanced (182) is also awaiting owner direction on its multiplayer-warning scope. Keep both optional under D3.

## Completion check

Before Gate 0 can pass, all 294 inventory rows need a reviewed source/ownership decision and feature mapping; each actual mod needs the relevant publisher/package/version/dependency/license facts recorded; plausible overlapping mods need a complete interaction graph; named behavior that the design depends on must have exact-profile runtime evidence; and every remaining uncertainty must be either resolved or explicitly excluded from the support promise. Source review alone never satisfies runtime acceptance. See the [master TODO](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md), [feature traceability map](../FEATURE_TRACEABILITY.md), [review procedure](reviews/README.md), and [RWT/gravship feasibility audit](RWT_AND_GRAVSHIP_FEASIBILITY.md).
