# RimPLC rebuilt ladder: complete I/O inventory

Built from 430 rungs in `.local/plc-rebuild/families/*.json` (animals 18, backrooms 25, base-and-fortress 42, configuration 22, economy 44, endgame 21, growth 20, ideology-biotech-anomaly 24, meta 25, research 17, royalty 18, setup 23, space 19, start 21, survival 61, war 30), checked against `RimPLC/Source/RimPLC/Sensors.cs`, `Engine.cs`, `MainTabWindow_RimPLC.cs`, the `sensors` / `tags` / `marks` tables of `docs/playbook.gates.json`, `.local/autopilot/gates.py` and the tool table in `.local/autopilot/tools.py` + `guards.py`. Generated mechanically from the JSON, so every rung id is listed.

**How the RimPLC window shows things** (`MainTabWindow_RimPLC.cs`, tabs Ladder / Tags / Marks / Sensors / Log):

- Ladder tab: one row per rung, one coloured box per TOP-LEVEL `when` key (green true / dark false / amber unmeasured / red unresolved). A nested instruction is ONE box named by its label; its operand keys, timer accumulator and counter value are not shown.
- Sensors tab: every key in the scan state, so every measured sensor and every `mark_<x>` (never-set marks read false). An unmeasured sensor is absent.
- Tags tab: every constant and variable of the playbook tag table with rule and min..max. A tag missing from the table does not appear, and `{TAG}` to it is Unresolved (red).
- Marks tab: only marks set at least once.

## 1. Inputs (sensors): 192 keys, 128 measured, 64 NOT measured

| key | measured? (where) | used by rungs | in window | missing |
|---|---|---|---|---|
| `able_shooters_armed` | yes: Sensors.cs | crew-armed-attack, endgame-defence-check | Sensors tab + rung box | - |
| `adv_components` | yes: Sensors.cs | endgame-materials-check | Sensors tab + rung box | - |
| `alert_food_rot` | yes: Sensors.cs | colony-before-research, rot-alert | Sensors tab + rung box | - |
| `alert_heatstroke` | yes: Sensors.cs | heat | Sensors tab + rung box | - |
| `alert_hunterlacksrangedweapon` | yes: Sensors.cs generic alert_<def> (only while the def is loaded) | animals-hunt-food, animals-hunter-armed, hunter-weapon | Sensors tab + rung box | - |
| `alert_hypotherm` | yes: Sensors.cs | cold | Sensors tab + rung box | - |
| `alert_life_threat` | yes: Sensors.cs | life-threat | Sensors tab + rung box | - |
| `alert_need_research` | yes: Sensors.cs | research-next | Sensors tab + rung box | - |
| `alert_needs_tend` | yes: Sensors.cs | needs-tend | Sensors tab + rung box | - |
| `alert_sickness` | yes: Sensors.cs | disease | Sensors tab + rung box | - |
| `alert_starv` | yes: Sensors.cs | starving, starving-no-game | Sensors tab + rung box | - |
| `alert_warm_clothes` | yes: Sensors.cs | warm-clothes | Sensors tab + rung box | - |
| `away_maps` | yes: Sensors.cs | assault-on-map, assault-retreat-count, settlement-down | Sensors tab + rung box | - |
| `beds` | yes: Sensors.cs | beds-short, growth-spare-bed, hospital, research-bench, start-camp-beds | Sensors tab + rung box | - |
| `best_plants_skill` | NO | growth-healroot-and-cash-crops | amber rung box only | sensor (see TO BUILD) |
| `bill_rows` | yes: Sensors.cs | bills-missing, bills-missing-fallback, bills-raise-target, start-camp-stable | Sensors tab + rung box | - |
| `blueprints` | yes: Sensors.cs | blueprints-but-no-material, camp-wood-wall-fallback, camp-wood-wall-ring, econ-stray-blueprint, finish-before-new, growth-catch-up, research-bench-fallback | Sensors tab + rung box | - |
| `blueprints_against_rock` | NO | mine-before-wall | amber rung box only | sensor (see TO BUILD) |
| `buildings_damaged` | yes: Sensors.cs | defense-0-reset-damage, defense-1-secure, repair-0-reset, repair-1-wait, repair-2-set, repair-after-raid, war-fortification-repair | Sensors tab + rung box | - |
| `camera_on_colonist` | NO | camera-on-crew | amber rung box only | sensor (see TO BUILD) |
| `camp_water_cells` | NO | terraform-water-first | amber rung box only | sensor (see TO BUILD) |
| `chat_asks_mod` | NO | br-chat-mod-links | amber rung box only | sensor (see TO BUILD) |
| `chat_unanswered` | NO | chat-first | amber rung box only | sensor (see TO BUILD) |
| `chemfuel` | yes: Sensors.cs | pod-assault, supply-podfuel-0-reset, supply-podfuel-1-low, supply-shipfuel-0-reset, supply-shipfuel-1-low | Sensors tab + rung box | - |
| `children` | NO | bio-child-care | amber rung box only | sensor (see TO BUILD) |
| `colonist_hurt` | yes: Sensors.cs chain inputs | combat-1-damage-pause, endgame-reactor-start | Sensors tab + rung box | - |
| `colonist_needs_rescue` | NO: key typo, Sensors.cs measures `alert_colonist_needs_rescue` | growth-rescue-and-tend | amber rung box only | sensor (see TO BUILD) |
| `colonists` | yes: Sensors.cs | bio-family-rooms, empire-dominion, growth-family, hospital-setup, ideo-colony-policy, ideo-party-room, ideo-roles, leader-role, recruit-past-three, start-colony-lost, tame-mounts, war-prep, war-prison-workcamp | Sensors tab + rung box | - |
| `colonists_without_armor` | NO | growth-upgrade-everyone | amber rung box only | sensor (see TO BUILD) |
| `colonists_without_bedroom` | NO | bedrooms-owned | amber rung box only | sensor (see TO BUILD) |
| `colony_animals` | yes: Sensors.cs | animal-pen, animals-autumn-cull, animals-haygrass, animals-kibble, train-mounts | Sensors tab + rung box | - |
| `colony_exists` | yes: Sensors.cs | animal-pen, animals-butcher-standing, animals-danger-clear, animals-food-steady, animals-handler, animals-hunt-fallback, animals-hunt-food, animals-hunter-armed, arms-out-fallback, arms-out-first, bills-missing, butcher-table, config-assign-tab, config-drug-policy, config-hospitality-visitors, config-schedule-anything, config-stockpile-priority, config-window-fullscreen, econ-checklist, econ-dump-zone, firebreak, food-rotting-or-no-cold, growth-needs-watch, growth-new-pawn-setup, growth-spare-bed, hospital-setup, ideo-colony-policy, ideo-roles, long-goal-drive, maintenance-sweep, meals-early, new-colony, recruit-past-three, setup-0-new-colony, setup-0-pause-on-land, setup-0-starting-goods, setup-0-unforbid, setup-1-explore, setup-1-explore-fallback, setup-2-pawns, setup-2-pawns-fallback, setup-2b-priorities-after-explore, setup-3-assign, setup-4-stores, setup-4-stores-fallback, setup-4b-shelter, setup-5-stove, setup-6-run, setup-6b-crops, setup-7-camp-defence, setup-8-camp-stable, setup-9-new-pawn, setup-chop, shelter-night-one, start-async, start-camp-beds, start-camp-chop, start-camp-chop-fallback, start-camp-food, start-camp-shelter, start-camp-shelter-fallback, start-camp-stable, start-camp-stores, start-camp-tight, start-colony-lost, start-crashlanded, start-explore-facility, start-kind-unknown, start-lone, start-naked, start-new-colony, start-new-pawn, start-standing-orders, start-store, start-tribal, stream-setup, unforbid-constant, work-grid-set, work-priorities-unset | Sensors tab + rung box | - |
| `comms_console` | yes: Sensors.cs | br-contact-company, combat-2-call-help-comms, comms, config-post-strictness, space-trade-beacon, space-trade-comms, supply-steel-1-buy, supply-weapons-1-sell | Sensors tab + rung box | - |
| `components` | yes: Sensors.cs | br-company-supply, components-low, econ-components-reset, endgame-materials-check, gate-assemble, war-weapons-upgrade | Sensors tab + rung box | - |
| `condition_HeatWave` | NO: mixed case, Sensors.cs writes `condition_heatwave` | br-heat | amber rung box only | sensor (see TO BUILD) |
| `condition_coldsnap` | yes: Sensors.cs generic condition_<def> (only while the def is loaded) | cold-snap | Sensors tab + rung box | - |
| `condition_eclipse` | yes: Sensors.cs generic condition_<def> (only while the def is loaded) | eclipse-battery | Sensors tab + rung box | - |
| `condition_flashstorm` | yes: Sensors.cs generic condition_<def> (only while the def is loaded) | flashstorm | Sensors tab + rung box | - |
| `condition_heatwave` | yes: Sensors.cs generic condition_<def> (only while the def is loaded) | heat-wave | Sensors tab + rung box | - |
| `condition_solarflare` | yes: Sensors.cs generic condition_<def> (only while the def is loaded) | solar-flare | Sensors tab + rung box | - |
| `condition_toxicfallout` | yes: Sensors.cs generic condition_<def> (only while the def is loaded) | toxic-fallout | Sensors tab + rung box | - |
| `condition_volcanicwinter` | yes: Sensors.cs generic condition_<def> (only while the def is loaded) | volcanic-winter | Sensors tab + rung box | - |
| `corpses` | yes: Sensors.cs | animals-butcher-standing, anomaly-dissection, butcher-fast, corpses-buried, econ-corpses-standing, econ-dump-zone, war-manhunter-butcher, war-organ-harvest | Sensors tab + rung box | - |
| `count_Hive` | NO: mixed case, Sensors.cs writes `count_hive` | war-infestation | amber rung box only | sensor (see TO BUILD) |
| `count_TableAutopsy` | NO: mixed case, Sensors.cs writes `count_tableautopsy` | war-organ-harvest | amber rung box only | sensor (see TO BUILD) |
| `count_aipersonacore` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | endgame-persona-core, endgame-persona-core-stuck, endgame-ship-build, space-persona-core | Sensors tab + rung box | - |
| `count_battery` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | power-batteries | Sensors tab + rung box | - |
| `count_blocksmarble` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | econ-marble | Sensors tab + rung box | - |
| `count_componentindustrial` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | space-ship-materials | Sensors tab + rung box | - |
| `count_componentspacer` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | ship-launch, space-ship-materials | Sensors tab + rung box | - |
| `count_cooler` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | power-ac-fridge | Sensors tab + rung box | - |
| `count_drug_lab` | NO: vanilla defName is DrugLab -> count_druglab | econ-druglab | amber rung box only | sensor (see TO BUILD) |
| `count_geneextractor` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | genes | Sensors tab + rung box | - |
| `count_gold` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | space-ship-materials | Sensors tab + rung box | - |
| `count_loudspeaker` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | party-and-statues | Sensors tab + rung box | - |
| `count_mechlink` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | mechanitor | Sensors tab + rung box | - |
| `count_milk` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | bio-milk-pen | Sensors tab + rung box | - |
| `count_orbitaltradebeacon` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | space-trade-beacon | Sensors tab + rung box | - |
| `count_penoxycyline` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | research-antibiotics | Sensors tab + rung box | - |
| `count_plasteel` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | ship-launch, space-ship-materials | Sensors tab + rung box | - |
| `count_solargenerator` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | power-alternate | Sensors tab + rung box | - |
| `count_steel` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | ship-launch, space-ship-materials | Sensors tab + rung box | - |
| `count_tablebutcher` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | econ-butcher | Sensors tab + rung box | - |
| `count_tablesculpting` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | econ-art | Sensors tab + rung box | - |
| `count_uranium` | yes: Sensors.cs generic count_<def> (only while the def is loaded) | ship-launch, space-ship-materials | Sensors tab + rung box | - |
| `danger_animals_near` | yes: Sensors.cs | animals-danger-clear, tame-mounts | Sensors tab + rung box | - |
| `day` | yes: Sensors.cs | dining-room, setup-0-starting-goods, shelter-night-one | Sensors tab + rung box | - |
| `days_of_food` | yes: Sensors.cs | animals-food-steady, animals-hunt-fallback, animals-hunt-food, br-sustainable, camp-wood-wall-ring, colony-before-research, crops-full-set, endgame-defence-check, food-low, gate-open, pawn-starving, research-bench, rung-2-power-and-cold, rung-3-defence, rung-4-production, rung-5-the-mountain-base, rung-5b-the-gate, setup-8-camp-stable, start-camp-food, start-camp-stable, supply-food-0-reset, supply-food-1-low, volcanic-winter, winter-food-stock | Sensors tab + rung box | - |
| `defences_built` | yes: Sensors.cs | br-sustainable, defense-1-secure, defense-2-embrasures, fortress-ring, rung-4-production | Sensors tab + rung box | - |
| `designations_cut` | yes: Sensors.cs | setup-chop | Sensors tab + rung box | - |
| `designations_hunt` | yes: Sensors.cs | animals-hunt-fallback, starving-no-game | Sensors tab + rung box | - |
| `dialog_open` | yes: Sensors.cs | camera-on-crew, config-ui-clear, config-ui-clear-stuck, dialog-open, dialog-stuck, game-paused | Sensors tab + rung box | - |
| `downed_count` | yes: Sensors.cs | assault-retreat-count, downed-pawn | Sensors tab + rung box | - |
| `drafted_count` | yes: Sensors.cs | hostile-on-map, raid-cleanup, raid-posted | Sensors tab + rung box | - |
| `embrasure_gaps` | NO | war-fortification-repair | amber rung box only | sensor (see TO BUILD) |
| `embrasures` | yes: Sensors.cs | defense-0-reset-embrasures, defense-1-secure, defense-2-embrasures, fortress-ring | Sensors tab + rung box | - |
| `empire_letter` | yes: Sensors.cs | empire-quest, endgame-royal-ascent | Sensors tab + rung box | - |
| `explore_done` | yes: Engine.cs (copied from mark_explore_done) | setup-1-explore, setup-1-explore-fallback, setup-2b-priorities-after-explore, setup-4-stores, start-explore-facility | Sensors tab + rung box | - |
| `fields_all_default_crop` | yes: Sensors.cs | fields-wrong, fields-wrong-fallback | Sensors tab + rung box | - |
| `fight_ratio` | yes: Sensors.cs chain inputs (able_shooters / hostiles_on_map) | combat-0-reassess-better, combat-0-reassess-worse, combat-2-call-help-comms, combat-2-call-help-permit, combat-2-fight, combat-2-help-coming, combat-2-kite, combat-2-retreat, war-overwhelmed-indoors | Sensors tab + rung box | - |
| `fire_cells` | yes: Sensors.cs | fire-in-camp | Sensors tab + rung box | - |
| `flee_hostility_count` | NO | war-hostility-attack | amber rung box only | sensor (see TO BUILD) |
| `food_store` | yes: Sensors.cs | setup-4-stores, setup-4-stores-fallback, setup-4b-shelter, setup-5-stove | Sensors tab + rung box | - |
| `forbidden_items` | NO | unforbid-constant | amber rung box only | sensor (see TO BUILD) |
| `game_foreground` | yes: Sensors.cs | window-not-in-front | Sensors tab + rung box | - |
| `gold` | yes: Sensors.cs | endgame-materials-check | Sensors tab + rung box | - |
| `grav_parts` | yes: Sensors.cs | grav-build, grav-ready, supply-shipfuel-1-low | Sensors tab + rung box | - |
| `grid_matches_plan` | yes: Sensors.cs | config-assign-tab, config-priorities-new-pawn, setup-2b-priorities-after-explore, setup-9-new-pawn, work-priorities-fallback, work-priorities-unset | Sensors tab + rung box | - |
| `growing_cells` | yes: Sensors.cs | crops-full-set, growth-healroot-and-cash-crops, setup-6b-crops, setup-8-camp-stable | Sensors tab + rung box | - |
| `has_power` | yes: Sensors.cs | battery-room, br-sustainable, colony-before-research, comms, coolers-and-vents, defense-3-turrets, eclipse-battery, electric-lights, flooring-by-purpose, freezer-cluster, freezer-sorting, gate-power, hitech-bench, hvac-clusters, power-ac-fridge, power-every-consumer, power-fail-cook-meat, power-generation-margin, power-grid-standing, research-equipment-tiers, research-multi-analyzer, rung-3-defence, rung-4-production, space-trade-beacon, space-trade-comms, turret-line | Sensors tab + rung box | - |
| `healroot_plants` | yes: Sensors.cs | growth-healroot-and-cash-crops | Sensors tab + rung box | - |
| `heatstroke` | NO: key typo, Sensors.cs measures `alert_heatstroke` | br-heat | amber rung box only | sensor (see TO BUILD) |
| `hitech_benches` | NO | hitech-bench | amber rung box only | sensor (see TO BUILD) |
| `home_cells` | yes: Sensors.cs | firebreak | Sensors tab + rung box | - |
| `hostile_threat` | yes: Sensors.cs | empire-quest, setup-6-run, war-mobilize | Sensors tab + rung box | - |
| `hostiles_on_map` | yes: Sensors.cs | after-the-kill, animals-butcher-standing, animals-hunt-food, assault-on-map, big-plan, cavalry-tactics, combat-0-reset, combat-1-damage-pause, combat-3-hold-plan, corpses-buried, crew-armed-attack, downed-pawn, empire-hostile, endgame-load-caskets, endgame-reactor-start, game-paused, game-paused-stuck, gate-open, growth-rescue-and-tend, hostile-on-map, ideo-ritual-hold, long-goal-drive, maintenance-sweep, med-1-bleeding-under-fire, med-2-field-tend, med-3-carry-to-hospital, needs-tend, permit-aid, prisoner-bed-before-fight, raid-cleanup, raid-posted, repair-1-wait, repair-2-set, repair-after-raid, rung-5c-the-backrooms, settlement-down, space-launch-load, unforbid-constant, war-after-kill-storage, war-drop-pods-centre, war-fortification-repair, war-manhunter, war-manhunter-butcher, war-mechanoids, war-mobilize, war-overwhelmed-indoors, war-pirate-gunline, war-sapper-breach, war-siege-counter, war-stand-down, war-tribal-swarm | Sensors tab + rung box | - |
| `hud_visible` | NO | config-hud-restore | amber rung box only | sensor (see TO BUILD) |
| `humanlikes_not_ours` | yes: Sensors.cs | space-trade-comms-fallback | Sensors tab + rung box | - |
| `idle` | NO: key typo, Sensors.cs measures `alert_idle` | colony-before-research, endgame-greed | amber rung box only | sensor (see TO BUILD) |
| `items_forbidden` | NO | setup-0-unforbid | amber rung box only | sensor (see TO BUILD) |
| `junk_weapons` | yes: Sensors.cs | econ-wealth-junk | Sensors tab + rung box | - |
| `letter_labels` | yes: Sensors.cs | econ-guest-beds-full | Sensors tab + rung box | - |
| `letter_matches` | yes: Engine.cs special key (a letter label contains the text) | anomaly-entity, bestowing, bio-growth-moment, endgame-journey-offer | Sensors tab + rung box | - |
| `letters` | yes: Sensors.cs | letter-unread | Sensors tab + rung box | - |
| `loose_items_off_shelf` | NO | storage-shelves | amber rung box only | sensor (see TO BUILD) |
| `loose_items_outside_storage` | NO | growth-shelves-everything | amber rung box only | sensor (see TO BUILD) |
| `loose_items_unstored` | NO | config-haul-out-paced | amber rung box only | sensor (see TO BUILD) |
| `loose_weapons` | yes: Sensors.cs | econ-wealth-junk, supply-weapons-0-reset, supply-weapons-1-sell, supply-weapons-2-smelt | Sensors tab + rung box | - |
| `lovers_unmarried` | NO | growth-family | amber rung box only | sensor (see TO BUILD) |
| `low_food` | NO: key typo, Sensors.cs measures `alert_low_food` | rung-5c-the-backrooms | amber rung box only | sensor (see TO BUILD) |
| `low_medicine` | NO: key typo, Sensors.cs measures `alert_low_medicine` | br-sustainable | amber rung box only | sensor (see TO BUILD) |
| `lowest_mood` | yes: Sensors.cs | growth-needs-watch, ideo-ritual-hold, ideo-role-abilities | Sensors tab + rung box | - |
| `map_count` | yes: Sensors.cs | br-close-old-levels | Sensors tab + rung box | - |
| `meals` | yes: Sensors.cs | animals-food-steady, bills-raise-target, pawn-starving | Sensors tab + rung box | - |
| `medicine` | yes: Sensors.cs | endgame-defence-check, medicine-reserve, no-medicine, rung-2-power-and-cold, war-prep | Sensors tab + rung box | - |
| `mental_break` | yes: Sensors.cs | mental-break | Sensors tab + rung box | - |
| `monolith` | NO | anomaly-monolith | amber rung box only | sensor (see TO BUILD) |
| `mount_candidates` | yes: Sensors.cs | animal-pen, tame-mounts | Sensors tab + rung box | - |
| `multi_analyzers` | NO | research-multi-analyzer | amber rung box only | sensor (see TO BUILD) |
| `needs_tend_count` | yes: Sensors.cs | config-medicine-doctor | Sensors tab + rung box | - |
| `new_joiners` | NO | viewer-joined | amber rung box only | sensor (see TO BUILD) |
| `outdoor_temp` | yes: Sensors.cs | br-heat, winter-food-stock | Sensors tab + rung box | - |
| `owner_input_active` | NO | camera-on-crew, owner-at-controls | amber rung box only | sensor (see TO BUILD) |
| `owner_unread` | NO | owner-message | amber rung box only | sensor (see TO BUILD) |
| `paused` | yes: Sensors.cs | config-ui-clear-stuck, setup-0-pause-on-land | Sensors tab + rung box | - |
| `pawn_bleeding` | yes: Sensors.cs chain inputs | med-1-bleeding-under-fire, med-2-field-tend | Sensors tab + rung box | - |
| `pawns_flee` | NO | crew-armed-attack | amber rung box only | sensor (see TO BUILD) |
| `pawns_sharing_bedroom` | NO | growth-private-rooms | amber rung box only | sensor (see TO BUILD) |
| `pawns_unconfigured` | NO | growth-new-pawn-setup, start-new-pawn | amber rung box only | sensor (see TO BUILD) |
| `pawns_without_sidearm` | NO | crew-armed-attack | amber rung box only | sensor (see TO BUILD) |
| `plasteel` | yes: Sensors.cs | endgame-materials-check | Sensors tab + rung box | - |
| `pod_launchers` | yes: Sensors.cs | pod-assault, space-ally-gifts, supply-podfuel-1-low | Sensors tab + rung box | - |
| `power_generators` | yes: Sensors.cs | generators-out, power-alternate, power-generators-fallback, power-generators-outside | Sensors tab + rung box | - |
| `power_margin_pct` | NO | power-generation-margin | amber rung box only | sensor (see TO BUILD) |
| `prisoners` | NO | growth-prisoner-keep | amber rung box only | sensor (see TO BUILD) |
| `prompt_version_changed` | NO | updated-spark | amber rung box only | sensor (see TO BUILD) |
| `quadrum_index` | yes: Sensors.cs | animals-autumn-cull, animals-haygrass | Sensors tab + rung box | - |
| `quest_letter` | yes: Sensors.cs | econ-quests-cash, empire-quest, endgame-archonexus, grav-core, growth-joiner-letter | Sensors tab + rung box | - |
| `raw_food` | yes: Sensors.cs | pawn-starving | Sensors tab + rung box | - |
| `research_AirConditioning` | NO: mixed case, Sensors.cs writes `research_airconditioning` | coolers-and-vents, freezer-cluster | amber rung box only | sensor (see TO BUILD) |
| `research_Battery` | NO: mixed case, Sensors.cs writes `research_batteries` | battery-room | amber rung box only | sensor (see TO BUILD) |
| `research_GunTurrets` | NO: mixed case, Sensors.cs writes `research_gunturrets` | turret-line | amber rung box only | sensor (see TO BUILD) |
| `research_PenoxycylineProduction` | NO: mixed case, Sensors.cs writes `research_penoxycylineproduction` | config-antibiotics | amber rung box only | sensor (see TO BUILD) |
| `research_Stonecutting` | NO: mixed case, Sensors.cs writes `research_stonecutting` | stone-blocks-bench | amber rung box only | sensor (see TO BUILD) |
| `research_airconditioning` | yes: Sensors.cs generic research_<def> (only while the def is loaded) | hvac-clusters, power-ac-fridge | Sensors tab + rung box | - |
| `research_basicmechtech` | yes: Sensors.cs generic research_<def> (only while the def is loaded) | mechanitor | Sensors tab + rung box | - |
| `research_batteries` | yes: Sensors.cs generic research_<def> (only while the def is loaded) | power-batteries | Sensors tab + rung box | - |
| `research_benches` | yes: Sensors.cs | anomaly-dissection, colony-before-research, ideo-research-antibiotics, research-antibiotics-queue, research-bench, research-bench-fallback, research-idle, research-next, research-researcher-balance, research-rush-micro | Sensors tab + rung box | - |
| `research_current` | yes: Sensors.cs | research-queue-multi, research-rush-micro | Sensors tab + rung box | - |
| `research_drugproduction` | yes: Sensors.cs generic research_<def> (only while the def is loaded) | econ-druglab, research-antibiotics-queue | Sensors tab + rung box | - |
| `research_electricity` | yes: Sensors.cs generic research_<def> (only while the def is loaded) | hospital-setup, power-generators-outside, research-rush-micro | Sensors tab + rung box | - |
| `research_microelectronicsbasics` | yes: Sensors.cs generic research_<def> (only while the def is loaded) | comms, hitech-bench, research-production-money, research-queue-multi, research-rush-micro, space-microelectronics, space-trade-beacon | Sensors tab + rung box | - |
| `research_multianalyzer` | yes: Sensors.cs generic research_<def> (only while the def is loaded) | research-multi-analyzer, research-queue-multi, research-ship-tree | Sensors tab + rung box | - |
| `research_only_pawns` | NO: not a research project (no ResearchProjectDef of that name) | research-researcher-balance | amber rung box only | sensor (see TO BUILD) |
| `research_penoxycyline` | NO: vanilla defName is PenoxycylineProduction -> research_penoxycylineproduction | ideo-antibiotics, ideo-research-antibiotics | amber rung box only | sensor (see TO BUILD) |
| `research_penoxycylineproduction` | yes: Sensors.cs generic research_<def> (only while the def is loaded) | research-antibiotics, research-antibiotics-queue | Sensors tab + rung box | - |
| `research_queue_empty` | yes: Sensors.cs | endgame-ship-research, ideo-research-antibiotics, research-idle, research-idle-fallback, research-production-money | Sensors tab + rung box | - |
| `research_room_lit` | NO: not a research project (a room/lighting check) | research-lab-room | amber rung box only | sensor (see TO BUILD) |
| `research_shipreactor` | yes: Sensors.cs generic research_<def> (only while the def is loaded) | endgame-research-refused, endgame-ship-research | Sensors tab + rung box | - |
| `research_solarpanels` | yes: Sensors.cs generic research_<def> (only while the def is loaded) | power-alternate | Sensors tab + rung box | - |
| `research_xenogenetics` | NO: UNVERIFIED Biotech defName (Xenogermination?) -- check DefDatabase | genes | amber rung box only | sensor (see TO BUILD) |
| `room_wall_holes` | NO | walls-halls-roofs | amber rung box only | sensor (see TO BUILD) |
| `rooms_out_of_temp` | NO | coolers-and-vents | amber rung box only | sensor (see TO BUILD) |
| `seconds_since_spoken` | NO | dead-air | amber rung box only | sensor (see TO BUILD) |
| `seconds_since_tool` | NO | idle-watchdog | amber rung box only | sensor (see TO BUILD) |
| `seconds_since_webcam` | NO | webcam-stale | amber rung box only | sensor (see TO BUILD) |
| `ship_parts` | yes: Sensors.cs | ship-launch | Sensors tab + rung box | - |
| `ship_research_done` | yes: Sensors.cs | empire-dominion, endgame-persona-core, endgame-persona-core-stuck, endgame-ship-materials, research-ship-tree | Sensors tab + rung box | - |
| `silver` | yes: Sensors.cs | br-company-supply, econ-money-to-security, econ-silver-company, space-ally-gifts, space-trade-comms, supply-steel-1-buy, trade-run, vault | Sensors tab + rung box | - |
| `simple_benches` | NO | research-upgrade-sweep | amber rung box only | sensor (see TO BUILD) |
| `steel` | yes: Sensors.cs | br-company-supply, endgame-materials-check, gate-assemble, supply-steel-0-reset, supply-steel-1-buy, supply-steel-2-mine, turret-line | Sensors tab + rung box | - |
| `stockpile_cells` | yes: Sensors.cs | config-haul-out-paced, config-stockpile-priority, start-camp-stores, stockpiles-sized, storage-logic | Sensors tab + rung box | - |
| `store_roofed_fraction` | yes: Sensors.cs | food-rotting-or-no-cold, freezer-sorting | Sensors tab + rung box | - |
| `stoves` | yes: Sensors.cs | bills-missing, econ-butcher, econ-freezer-shelves, kitchen-clean, meals-early, setup-8-camp-stable, start-camp-tight | Sensors tab + rung box | - |
| `threat_letter` | yes: Sensors.cs | after-the-kill, anomaly-entity, empire-hostile, hostile-on-map, prisoner-bed-before-fight, war-after-kill-storage, war-letter-classify | Sensors tab + rung box | - |
| `throne` | yes: Sensors.cs | party-and-statues, throne-room, throne-room-layout, throne-room-retry | Sensors tab + rung box | - |
| `ticks_moving` | yes: Sensors.cs | game-paused, game-paused-stuck, maintenance-sweep, setup-6-run | Sensors tab + rung box | - |
| `title_seniority` | yes: Sensors.cs | title-track | Sensors tab + rung box | - |
| `torch_lamps` | NO | electric-lights | amber rung box only | sensor (see TO BUILD) |
| `transport_pods` | yes: Sensors.cs | space-ally-gifts | Sensors tab + rung box | - |
| `turrets` | yes: Sensors.cs | defense-0-reset-turrets, defense-1-secure, defense-3-turrets, endgame-defence-check, turret-line | Sensors tab + rung box | - |
| `unarmed_colonists` | NO | war-arms-fallback, war-arms-sidearms | amber rung box only | sensor (see TO BUILD) |
| `unfloored_room_cells` | NO | flooring-by-purpose | amber rung box only | sensor (see TO BUILD) |
| `unpowered_buildings` | NO | power-grid-standing | amber rung box only | sensor (see TO BUILD) |
| `unpowered_consumers` | NO | power-every-consumer | amber rung box only | sensor (see TO BUILD) |
| `unpowered_embrasures` | NO | war-fortification-repair | amber rung box only | sensor (see TO BUILD) |
| `uranium` | yes: Sensors.cs | endgame-materials-check | Sensors tab + rung box | - |
| `voice_playing` | NO | dead-air, voice-busy | amber rung box only | sensor (see TO BUILD) |
| `wall_gaps` | NO | perimeter-hole | amber rung box only | sensor (see TO BUILD) |
| `wild_game` | yes: Sensors.cs | animals-hunt-food | Sensors tab + rung box | - |
| `window_fullscreen` | NO | config-window-fullscreen | amber rung box only | sensor (see TO BUILD) |
| `wood` | yes: Sensors.cs | blueprints-but-no-material, br-camp-wall, camp-wood-wall-ring, econ-wood-reset, econ-wood-winter, setup-chop, start-camp-chop, start-camp-chop-fallback, start-camp-shelter | Sensors tab + rung box | - |

## 2. Switches (marks): 203 marks

Every mark shows in the Sensors tab as `mark_<name>` and in the Marks tab once set. "set by" = rungs whose `then` has `ladder_set mark <name>`.

| mark | read by rungs | set by rungs | declared in playbook marks | gap |
|---|---|---|---|---|
| `after_kill_done` | after-the-kill, war-after-kill-storage | after-the-kill, war-after-kill-storage | no | - |
| `aid_cooldown` | - | permit-aid | no | set but no rung reads it |
| `altar_room_done` | altar-room | altar-room | no | - |
| `arms_set` | arms-out-fallback, arms-out-first, setup-2-pawns | arms-out-first | no | - |
| `arms_tried` | arms-out-fallback | - | no | no rung sets it |
| `art_bill_set` | econ-art | econ-art | no | - |
| `assign_set` | leader-moral-guide, setup-0-pause-on-land, setup-1-explore, setup-1-explore-fallback, setup-3-assign, setup-4-stores, setup-4-stores-fallback, setup-chop | - | yes | no rung sets it |
| `base_layout_planned` | br-base-layout | - | no | no rung sets it |
| `bastions_done` | war-bastions-towers, war-wall-tour | war-bastions-towers | no | - |
| `battery_room_done` | battery-room | battery-room | no | - |
| `blueprints_audited` | econ-stray-blueprint | econ-stray-blueprint | no | - |
| `butcher_built` | animals-butcher-standing, animals-kibble, butcher-fast, butcher-table | butcher-table | no | - |
| `butcher_set` | econ-butcher | econ-butcher | no | - |
| `camp_defence` | camp-wood-wall-fallback, camp-wood-wall-ring, growth-healroot-and-cash-crops, growth-look-at-world, growth-shelves-everything, setup-7-camp-defence, setup-8-camp-stable | camp-wood-wall-fallback, camp-wood-wall-ring | no | - |
| `camp_food_steady` | animal-pen, animals-food-steady, animals-handler, tame-mounts | animals-food-steady | no | - |
| `camp_stable` | setup-8-camp-stable | setup-8-camp-stable | no | - |
| `camp_wall_done` | br-base-layout, br-camp-wall | br-camp-wall | no | - |
| `caravan_out` | caravan-raid, settlement-down | assault-retreat-count, caravan-raid, settlement-down | yes | - |
| `caskets_loaded` | endgame-launch, endgame-load-caskets | endgame-load-caskets | no | - |
| `child_care_ready` | bio-child-care | - | no | no rung sets it |
| `chop_refused` | start-camp-chop-fallback | start-camp-chop-fallback | no | - |
| `colonist_hurt` | - | combat-0-reset | yes | set but no rung reads it |
| `colony_policy_set` | ideo-colony-policy | - | no | no rung sets it |
| `colony_sustainable` | br-gate-facility, br-sustainable, rung-5b-the-gate | br-sustainable | no | - |
| `combat_paused` | combat-0-reset, combat-1-damage-pause, combat-2-call-help-comms, combat-2-call-help-permit, combat-2-fight, combat-2-help-coming, combat-2-kite, combat-2-retreat | combat-0-reset, combat-1-damage-pause | yes | - |
| `combat_plan` | combat-0-reassess-better, combat-0-reassess-worse, combat-2-call-help-comms, combat-2-call-help-permit, combat-2-fight, combat-2-help-coming, combat-2-kite, combat-2-retreat, combat-3-hold-plan, med-1-bleeding-under-fire | combat-0-reassess-better, combat-0-reassess-worse, combat-0-reset, combat-2-call-help-comms, combat-2-call-help-permit, combat-2-fight, combat-2-help-coming, combat-2-kite, combat-2-retreat | yes | - |
| `comms_set` | trade-run | comms | no | - |
| `company_contact` | br-company-supply, br-contact-company, br-gate-ops-cash, br-trade-income | br-contact-company | no | - |
| `components_short_set` | components-low, econ-components-reset | components-low, econ-components-reset | no | - |
| `config_antibiotics_set` | - | config-antibiotics | no | set but no rung reads it |
| `config_assign_set` | config-medicine-doctor, config-schedule-anything | config-assign-tab | no | - |
| `config_drug_policy_set` | config-antibiotics, config-hospitality-visitors | config-drug-policy | no | - |
| `config_priorities_audited` | config-priorities-new-pawn | config-priorities-new-pawn | no | - |
| `config_schedule_set` | config-drug-policy | config-schedule-anything | no | - |
| `config_stockpile_priority_set` | - | config-stockpile-priority | no | set but no rung reads it |
| `config_visitors_on` | - | config-hospitality-visitors | no | set but no rung reads it |
| `coordinate_held` | backrooms-mine | - | yes | no rung sets it |
| `corral_set` | econ-corral | econ-corral | no | - |
| `crew_across` | br-close-old-levels, br-return-window | br-return-window, rung-5c-the-backrooms | no | - |
| `crops_attempt` | econ-crops-fallback | crops-full-set | no | - |
| `crops_full` | crops-full-set, econ-crops-fallback, econ-fields-outside, rung-4-production | econ-crops-fallback | no | - |
| `defense_secure` | defense-0-reset-damage, defense-0-reset-embrasures, defense-0-reset-turrets, defense-1-secure, defense-2-embrasures, defense-3-turrets | defense-0-reset-damage, defense-0-reset-embrasures, defense-0-reset-turrets, defense-1-secure | yes | - |
| `dining_done` | dining-room | dining-room | no | - |
| `dining_rec_done` | growth-dining-and-rec | growth-dining-and-rec | no | - |
| `dissection_bill_set` | anomaly-dissection | - | no | no rung sets it |
| `double_rooms_set` | double-bed-rooms | double-bed-rooms | no | - |
| `druglab_set` | econ-druglab | econ-druglab | no | - |
| `dump_zone_set` | econ-corpses-standing, econ-dump-zone | econ-dump-zone | no | - |
| `empire_hostile` | empire-hostile | - | yes | no rung sets it |
| `empire_quest_active` | - | empire-quest | no | set but no rung reads it |
| `ending_archonexus` | endgame-archonexus | - | no | no rung sets it |
| `ending_chosen` | empire-dominion, endgame-greed, endgame-journey-offer | empire-dominion | no | - |
| `ending_gravship` | endgame-gravship-voyage | - | no | no rung sets it |
| `ending_royal` | endgame-royal-ascent | - | no | no rung sets it |
| `ending_ship` | endgame-defence-check, endgame-launch-defence, endgame-materials-check, endgame-persona-core, endgame-persona-core-stuck, endgame-research-refused, endgame-ship-build, endgame-ship-build-refused, endgame-ship-materials, endgame-ship-research, endgame-ship-site | empire-dominion | no | - |
| `explore_refused` | br-out-fallback, br-out-of-the-backrooms | - | no | no rung sets it |
| `explore_skipped` | setup-4-stores | - | no | no rung sets it |
| `facility_build_refused` | br-gate-facility, br-gate-facility-fallback | br-gate-facility-fallback | no | - |
| `family_rooms_built` | bio-family-rooms, bio-milk-pen | - | no | no rung sets it |
| `field_tended` | med-2-field-tend, med-3-carry-to-hospital | med-2-field-tend, med-3-carry-to-hospital | yes | - |
| `fields_outside_set` | econ-fields-outside | econ-fields-outside | no | - |
| `firebreak_cut` | firebreak | firebreak | no | - |
| `firebreak_done` | firebreak-ring | firebreak-ring | no | - |
| `food_short_set` | supply-food-0-reset, supply-food-1-low | supply-food-0-reset, supply-food-1-low | yes | - |
| `freezer_attempt` | econ-freezer-fallback | econ-freezer-shelves | no | - |
| `freezer_shelves_set` | econ-freezer-fallback, econ-freezer-shelves | econ-freezer-fallback | no | - |
| `freezer_sorted` | colony-before-research, freezer-cluster, freezer-sorting, power-fail-cook-meat, storage-logic | freezer-cluster, freezer-sorting | no | - |
| `fuel_short_set` | supply-podfuel-0-reset, supply-podfuel-1-low | supply-podfuel-0-reset, supply-podfuel-1-low | yes | - |
| `gate_designated` | gate-assemble, rung-5b-the-gate | rung-5b-the-gate, start-async | yes | - |
| `gate_facility_built` | br-gate-facility, br-gate-facility-fallback, rung-5b-the-gate | - | no | no rung sets it |
| `gate_online` | gate-open, gate-power | gate-power | yes | - |
| `gate_open` | backrooms-mine, br-gate-ops-cash, gate-open, gate-open-fallback, gate-staffed, rung-5c-the-backrooms | - | yes | no rung sets it |
| `gate_open_refused` | gate-open, gate-open-fallback | gate-open-fallback | no | - |
| `gate_sections_done` | gate-assemble, gate-power | gate-assemble | yes | - |
| `gen_area_done` | generators-out | generators-out | no | - |
| `generator_cancelled` | power-generators-fallback | - | no | no rung sets it |
| `gift_sent` | - | space-ally-gifts | no | set but no rung reads it |
| `got_out` | br-camp-wall, br-contact-company, br-haul-out, br-natural-gate-room | - | no | no rung sets it |
| `gravcore_found` | grav-build, grav-core | grav-core | yes | - |
| `gravship_ready` | empire-dominion, endgame-gravship-voyage, megaship-drop | grav-ready | yes | - |
| `guest_drugs_set` | drugs-econ | drugs-econ | no | - |
| `guests_set` | drugs-econ, econ-guest-beds-full, guest-wing | guest-wing | no | - |
| `handler_set` | animals-handler, animals-milk-herd, tame-mounts, train-mounts | animals-handler | no | - |
| `haygrass` | animals-haygrass | animals-haygrass | no | - |
| `help_coming` | combat-2-call-help-comms, combat-2-call-help-permit, combat-2-help-coming, combat-2-kite, combat-2-retreat | combat-0-reset, combat-2-call-help-comms, combat-2-call-help-permit | yes | - |
| `hitech_bench_done` | hitech-bench, research-multi-analyzer, research-upgrade-sweep | hitech-bench | no | - |
| `hospital_done` | growth-hospital, growth-hospital-fallback, hospital | growth-hospital, growth-hospital-fallback, hospital | no | - |
| `hospital_set` | hospital-setup | hospital-setup | no | - |
| `hospital_try` | growth-hospital-fallback | - | no | no rung sets it |
| `hud_restored` | - | config-hud-restore | no | set but no rung reads it |
| `hvac_done` | hvac-clusters | hvac-clusters | no | - |
| `ideo_altar_built` | ideo-party-room, ideo-ritual, ideo-ritual-hold | - | no | no rung sets it |
| `ideo_content_done` | growth-ideology-content | growth-ideology-content | no | - |
| `ideo_party_room` | ideo-party-room | - | no | no rung sets it |
| `ideo_roles_refused` | ideo-roles-fallback | - | no | no rung sets it |
| `ideo_roles_set` | growth-ideology-content, ideo-ritual, ideo-role-abilities, ideo-roles, ideo-roles-fallback, leader-moral-guide | leader-moral-guide | yes | - |
| `infestation_proofed` | war-infestation-prevent | war-infestation-prevent | no | - |
| `junk_weapons_set` | supply-weapons-0-reset, supply-weapons-1-sell, supply-weapons-2-smelt | supply-weapons-0-reset, supply-weapons-1-sell, supply-weapons-2-smelt | yes | - |
| `killbox_done` | killbox-funnel | killbox-funnel | no | - |
| `kitchen_floored` | kitchen-clean | kitchen-clean | no | - |
| `landing_pad_done` | landing-pad | landing-pad | no | - |
| `launch_defence_ready` | endgame-defence-check, endgame-launch-defence, endgame-reactor-start, endgame-ship-build | endgame-defence-check | no | - |
| `launched` | endgame-gravship-voyage, endgame-greed, endgame-launch, endgame-reactor-hold | endgame-launch | no | - |
| `leader_set` | leader-role | leader-role | no | - |
| `main_base_started` | bio-family-rooms | - | no | no rung sets it |
| `marble_set` | econ-marble | econ-marble | no | - |
| `meal_bill_set` | meals-early | meals-early | no | - |
| `meditation_spot` | psycasts | psycasts | no | - |
| `milk_herd` | animals-milk-herd | - | no | no rung sets it |
| `milk_pen_built` | bio-milk-pen | - | no | no rung sets it |
| `monolith_advanced` | anomaly-monolith | - | no | no rung sets it |
| `mountain_base_done` | br-sustainable, econ-corral, econ-fields-outside, econ-marble, empire-dominion, growth-dining-and-rec, growth-family, growth-ideology-content, growth-private-rooms, guest-wing, infestation-walloff, research-ship-tree, rung-5-the-mountain-base, rung-5b-the-gate, rung-6-off-world, vault, war-infestation-prevent | rung-5-the-mountain-base | yes | - |
| `mountain_base_site` | throne-base-plan | - | no | no rung sets it |
| `mountain_plan_done` | mountain-base-plan, rung-5-the-mountain-base | - | no | no rung sets it |
| `mounted_ready` | cavalry-check, cavalry-tactics | - | yes | no rung sets it |
| `mounts_trained` | armor-mounts, cavalry-check, tame-mounts, train-mounts | train-mounts | yes | - |
| `multi_analyzer_done` | - | research-multi-analyzer | no | set but no rung reads it |
| `natural_gate_found` | br-haul-out, br-out-fallback, br-out-of-the-backrooms | - | no | no rung sets it |
| `operator_on_station` | gate-staffed | gate-staffed | yes | - |
| `organ_bill` | war-organ-harvest | war-organ-harvest | no | - |
| `outdoor_cold` | - | cold | yes | set but no rung reads it |
| `owner_ordered_new_colony` | new-colony, setup-0-new-colony | setup-0-new-colony | no | - |
| `pawns_set` | setup-2-pawns, setup-2-pawns-fallback, setup-3-assign | - | yes | no rung sets it |
| `pawns_tried` | setup-2-pawns-fallback | - | no | no rung sets it |
| `pen_built` | animal-pen, animals-haygrass, animals-milk-herd, animals-pen-soil | animal-pen | no | - |
| `pen_soil` | animals-pen-soil | animals-pen-soil | no | - |
| `peno_policy_set` | ideo-antibiotics | - | no | no rung sets it |
| `persona_core_held` | ship-launch | - | no | no rung sets it |
| `plan_needed` | big-plan | - | no | no rung sets it |
| `power_wired` | power-every-consumer | power-every-consumer | no | - |
| `prison_done` | war-prison-workcamp | war-prison-workcamp | no | - |
| `prison_wing_done` | prison-wing | prison-wing | no | - |
| `prisoner_bed` | prisoner-bed-before-fight, war-prison-workcamp | prisoner-bed-before-fight | no | - |
| `private_rooms_done` | growth-private-rooms, growth-private-rooms-fallback | growth-private-rooms, growth-private-rooms-fallback | no | - |
| `private_rooms_try` | growth-private-rooms-fallback | - | no | no rung sets it |
| `production_running` | drugs-econ, econ-art, econ-druglab | rung-4-production | yes | - |
| `psylink_level` | psycasts | title-track | yes | - |
| `raid_kind` | war-drop-pods-centre, war-infestation, war-manhunter, war-manhunter-butcher, war-mechanoids, war-pirate-gunline, war-sapper-breach, war-siege-counter, war-tribal-swarm | war-manhunter-butcher | no | - |
| `reactor_started` | endgame-load-caskets, endgame-reactor-hold, endgame-reactor-start, space-launch-load, space-reactor-hold, space-reactor-start | endgame-reactor-start, space-reactor-start | no | - |
| `repairs_set` | repair-0-reset, repair-2-set, repair-after-raid | repair-0-reset, repair-2-set, repair-after-raid | yes | - |
| `research_bench_done` | research-bench, research-lab-room | - | no | no rung sets it |
| `research_click_refused` | endgame-research-refused | endgame-research-refused | no | - |
| `research_gunsmithing` | war-weapons-upgrade | - | no | no rung sets it |
| `research_lab_done` | research-lab-room | - | no | no rung sets it |
| `research_ship_basics` | ship-launch, space-persona-core, space-prelaunch-defence, space-ship-materials, space-ship-research | - | no | no rung sets it |
| `research_transport_pod` | caravan-raid, pod-assault | - | no | no rung sets it |
| `royal_rooms_done` | landing-pad, rooms-level-up, royal-rooms | royal-rooms | no | - |
| `rung_3_defence_done` | defense-2-embrasures, firebreak-ring, fortress-ring, growth-hospital, killbox-funnel, war-bastions-towers | - | no | no rung sets it |
| `rung_4_production_done` | growth-upgrade-everyone, mountain-base-plan, rung-5-the-mountain-base | - | no | no rung sets it |
| `rung_5_the_mountain_base_done` | double-bed-rooms, furniture-tight-and-uniform, prison-wing | - | no | no rung sets it |
| `second_colony_started` | growth-second-colony | growth-second-colony | no | - |
| `security_spend_set` | econ-money-to-security | econ-money-to-security | no | - |
| `setup_done` | setup-0-pause-on-land, setup-9-new-pawn | setup-8-camp-stable | no | - |
| `shelter_built` | beds-short, shelter-night-one | shelter-night-one | no | - |
| `shelter_refused` | start-camp-shelter-fallback | - | no | no rung sets it |
| `shelter_set` | setup-4b-shelter, setup-5-stove, setup-8-camp-stable | - | no | no rung sets it |
| `ship_built` | endgame-reactor-start, endgame-ship-build, endgame-ship-build-refused, space-reactor-start | - | no | no rung sets it |
| `ship_defence_ready` | ship-launch, space-prelaunch-defence, space-reactor-start | - | no | no rung sets it |
| `ship_launched` | growth-second-colony | space-launch-load | no | - |
| `ship_materials_ready` | endgame-launch-defence, endgame-materials-check, endgame-ship-materials, endgame-ship-site | endgame-materials-check | no | - |
| `ship_place_refused` | endgame-ship-build-refused | endgame-ship-build-refused | no | - |
| `ship_site_set` | endgame-ship-build, endgame-ship-site | endgame-ship-build-refused, endgame-ship-site | no | - |
| `shipfuel_short_set` | supply-shipfuel-0-reset, supply-shipfuel-1-low | supply-shipfuel-0-reset, supply-shipfuel-1-low | yes | - |
| `siege_attacked` | - | war-siege-counter | no | set but no rung reads it |
| `silver_ordered` | econ-silver-company | econ-silver-company | no | - |
| `space_program_open` | grav-core, rung-6-off-world, space-ally-gifts, space-ask-chat, space-microelectronics, space-ship-research | rung-6-off-world | no | - |
| `start_camp_beds_done` | start-camp-tight | start-camp-beds | no | - |
| `start_camp_shelter_done` | start-camp-beds, start-camp-food, start-camp-shelter-fallback | start-camp-shelter | no | - |
| `start_camp_stable` | start-standing-orders | start-camp-stable | no | - |
| `start_camp_stores_done` | start-camp-shelter | start-camp-stores | no | - |
| `start_camp_tight_done` | start-camp-stable | start-camp-tight | no | - |
| `start_crashlanded_done` | start-camp-chop, start-camp-chop-fallback, start-camp-stores | start-crashlanded, start-naked, start-tribal | no | - |
| `start_goods_checked` | - | setup-0-starting-goods | no | set but no rung reads it |
| `start_in_backrooms` | br-out-fallback, br-out-of-the-backrooms | - | no | no rung sets it |
| `start_kind` | camp-wood-wall-fallback, camp-wood-wall-ring, start-async, start-crashlanded, start-explore-facility, start-kind-unknown, start-lone, start-naked, start-store, start-tribal | start-kind-unknown | yes | - |
| `starve_attempt` | - | starving | no | set but no rung reads it |
| `steel_short_set` | supply-steel-0-reset, supply-steel-1-buy, supply-steel-2-mine | supply-steel-0-reset, supply-steel-1-buy, supply-steel-2-mine | yes | - |
| `stockpiles_sized` | econ-freezer-shelves, stockpiles-sized | stockpiles-sized | no | - |
| `stonecutter_set` | stone-blocks-bench | stone-blocks-bench | no | - |
| `storage_logic` | storage-audit, storage-logic | storage-logic | no | - |
| `store_tried` | setup-4-stores-fallback | setup-4-stores, setup-4-stores-fallback | no | - |
| `stove_set` | butcher-table, setup-5-stove, setup-6-run, setup-6b-crops, setup-7-camp-defence | setup-5-stove | yes | - |
| `stream_titled` | stream-setup | - | no | no rung sets it |
| `survival_basics_done` | research-rush-micro | - | no | no rung sets it |
| `terraform_done` | terraform-water-first | terraform-water-first | no | - |
| `throne_layout_done` | altar-room, royal-rooms, throne-room-layout | throne-room-layout | no | - |
| `throne_plan_done` | generators-out, royal-vault, throne-base-plan, throne-room | throne-base-plan | no | - |
| `throne_room_walls` | throne-room-retry | throne-room | no | - |
| `title_rank` | combat-2-call-help-permit, empire-dominion, endgame-royal-ascent, permit-aid | title-track | yes | - |
| `trade_call_failed` | space-trade-comms-fallback | - | no | no rung sets it |
| `trade_run_done` | econ-trade-reset, econ-wealth-junk, trade-run | econ-trade-reset, trade-run | no | - |
| `traded_recently` | space-trade-comms-fallback | space-trade-comms, space-trade-comms-fallback | no | - |
| `ui_stuck_reported` | - | config-ui-clear-stuck | no | set but no rung reads it |
| `vault_done` | royal-vault | royal-vault | no | - |
| `vault_set` | vault | vault | no | - |
| `voids_walled` | infestation-walloff | infestation-walloff | no | - |
| `wall_build_refused` | br-camp-wall | - | no | no rung sets it |
| `war_mobilized` | war-after-kill-storage, war-overwhelmed-indoors, war-stand-down | war-mobilize, war-stand-down | no | - |
| `war_target_set` | caravan-raid, megaship-drop | - | yes | no rung sets it |
| `weapons_upgraded` | war-weapons-upgrade | war-weapons-upgrade | no | - |
| `wood_short_set` | econ-wood-reset, econ-wood-winter | econ-wood-reset, econ-wood-winter | no | - |
| `work_grid_set` | work-grid-set | work-grid-set | no | - |
| `world_looked` | growth-look-at-world | growth-look-at-world | no | - |

## 3. Setpoints / variables / constants (tags): 87 used, 60 UNDEFINED in the tag table

| tag | class | value (rule, min..max) | used by rungs | in Tags tab | missing |
|---|---|---|---|---|---|
| `ABLE_SHOOTERS` | UNDEFINED | - | crew-armed-attack | no | add to tags.variables |
| `AID_CALL_FOES` | variable | 6 (2 per colonist, 2..100) | permit-aid | yes | - |
| `ART_BILL` | UNDEFINED | - | econ-art | no | add to tags.variables |
| `BEACONS_TARGET` | UNDEFINED | - | space-trade-beacon | no | add to tags.variables |
| `BEDS_NEEDED` | variable | 4 (one per colonist, plus one spare, 2..60) | beds-short, growth-spare-bed, hospital | yes | - |
| `BLUEPRINT_BACKLOG` | UNDEFINED | - | growth-catch-up | no | add to tags.variables |
| `CALL_HELP_RATIO` | variable | 0.5 (fixed setpoint: under this many shooters per hostile it is 'too many' -- call help or retreat, 0.1..2.0) | combat-2-call-help-comms, combat-2-call-help-permit, combat-2-retreat | yes | - |
| `CAMP_STABLE_HOURS` | UNDEFINED | - | start-camp-stable | no | add to tags.variables |
| `CAMP_WOOD` | UNDEFINED | - | start-camp-chop, start-camp-chop-fallback | no | add to tags.variables |
| `CAVALRY_ENABLED` | variable | 1 (1 on, 0 off (cavalry-check sets 0 when no mount gizmo exists), 0..1) | cavalry-check, cavalry-tactics | yes | - |
| `CHAT_DECIDE_S` | UNDEFINED | - | dead-air, long-goal-drive | no | add to tags.variables |
| `COLONIST_TARGET` | UNDEFINED | - | growth-family, recruit-past-three | no | add to tags.variables |
| `COMPONENTS_FLOOR` | UNDEFINED | - | br-company-supply | no | add to tags.variables |
| `COMPONENT_RESERVE` | variable | 8 (5 + colonists, 5..200) | components-low, econ-components-reset, war-weapons-upgrade | yes | - |
| `CORPSE_LIMIT` | variable | 3 (fixed setpoint (mood penalty for seen corpses), 0..20) | corpses-buried, econ-corpses-standing | yes | - |
| `CROP_CELLS` | UNDEFINED | - | setup-6b-crops, setup-8-camp-stable | no | add to tags.variables |
| `DEAD_AIR_MAX_S` | UNDEFINED | - | dead-air | no | add to tags.variables |
| `EMBRASURE_TARGET` | variable | 40 (4 x sqrt(home_cells), 16..200) | defense-0-reset-embrasures, defense-1-secure, defense-2-embrasures, fortress-ring | yes | - |
| `ENDGAME_COLONISTS` | UNDEFINED | - | empire-dominion, endgame-defence-check | no | add to tags.variables |
| `FIELD_CELLS_TOTAL` | UNDEFINED | - | growth-healroot-and-cash-crops | no | add to tags.variables |
| `FIGHT_RATIO_MIN` | variable | 1.0 (fixed setpoint: able shooters per hostile to take the fight, 0.3..5.0) | combat-0-reassess-better, combat-0-reassess-worse, combat-2-fight, combat-2-help-coming, combat-2-kite | yes | - |
| `FOOD_COMFORT_DAYS` | variable | 6.4 (twice FOOD_MIN_DAYS, 5.0..60.0) | animals-food-steady, br-sustainable, crops-full-set, gate-open, rung-4-production, rung-5-the-mountain-base, rung-5b-the-gate, start-camp-food, start-camp-stable, supply-food-0-reset, supply-food-1-low, winter-food-stock | yes | - |
| `FOOD_DAYS_STABLE` | UNDEFINED | - | setup-8-camp-stable | no | add to tags.variables |
| `FOOD_MIN_DAYS` | variable | 3.2 (2 + 0.4 per colonist, 3.0..30.0) | animals-hunt-fallback, animals-hunt-food, camp-wood-wall-ring, colony-before-research, food-low, research-bench, rung-2-power-and-cold, rung-3-defence, start-camp-food | yes | - |
| `FOOD_PANIC_DAYS` | constant | 1.0 | pawn-starving | yes | - |
| `GATE_FIRST_WINDOW_MIN` | UNDEFINED | - | gate-open | no | add to tags.variables |
| `GATE_MAX` | constant | 3 | backrooms-mine, rung-5b-the-gate | yes | - |
| `GRAV_PARTS_TARGET` | variable | 12 (placeholder: set after counting what the console requires (UNVERIFIED), 1..500) | grav-build, grav-ready | yes | - |
| `GUEST_DRUG_STOCK` | UNDEFINED | - | drugs-econ | no | add to tags.variables |
| `HAY_CELLS_PER_ANIMAL` | UNDEFINED | - | animals-haygrass | no | add to tags.variables |
| `IDLE_WATCHDOG_S` | UNDEFINED | - | idle-watchdog | no | add to tags.variables |
| `KIBBLE_FROM_ANIMALS` | UNDEFINED | - | animals-kibble | no | add to tags.variables |
| `KIBBLE_TARGET` | UNDEFINED | - | animals-kibble | no | add to tags.variables |
| `LAUNCH_FOOD_DAYS` | UNDEFINED | - | endgame-defence-check, endgame-launch-defence | no | add to tags.variables |
| `LAUNCH_MEDICINE` | UNDEFINED | - | endgame-defence-check | no | add to tags.variables |
| `LAUNCH_TURRETS` | UNDEFINED | - | endgame-defence-check, endgame-launch-defence | no | add to tags.variables |
| `LEVELS_MAX` | UNDEFINED | - | br-close-old-levels | no | add to tags.variables |
| `LINE_MAX_WORDS` | UNDEFINED | - | always, dead-air | no | add to tags.variables |
| `LOOSE_ITEMS_MAX` | UNDEFINED | - | growth-shelves-everything | no | add to tags.variables |
| `MAX_LINES_QUEUED` | UNDEFINED | - | voice-busy | no | add to tags.variables |
| `MEAL_BILL` | UNDEFINED | - | bills-missing, bills-missing-fallback, bills-raise-target | no | add to tags.variables |
| `MEAL_BILL_TARGET` | variable | 50 (owner: "cook bill maintained at 50 rather than 10", 50..300) | animals-butcher-standing, animals-hunt-food, food-low, growth-needs-watch, meals-early, power-fail-cook-meat, setup-5-stove, start-camp-food, starving, supply-food-1-low | yes | - |
| `MEDICINE_RESERVE` | variable | 6 (2 per colonist, 4..80) | growth-hospital, medicine-reserve, war-prep | yes | - |
| `MOUNT_TARGET` | variable | 3 (one mount per colonist, 1..60) | tame-mounts, train-mounts | yes | - |
| `OWNER_SETTLE_S` | UNDEFINED | - | owner-at-controls | no | add to tags.variables |
| `PENOX_STOCK` | UNDEFINED | - | config-antibiotics | no | add to tags.variables |
| `PEN_CELLS_PER_ANIMAL` | UNDEFINED | - | animal-pen | no | add to tags.variables |
| `PEN_MIN_ANIMALS` | UNDEFINED | - | animal-pen | no | add to tags.variables |
| `PERSONA_CORE_WAIT_HOURS` | UNDEFINED | - | endgame-persona-core-stuck | no | add to tags.variables |
| `POD_FUEL` | variable | 600 (150 x POD_SQUAD (cost per tile UNVERIFIED, generous), 150..10000) | pod-assault, supply-podfuel-0-reset, supply-podfuel-1-low | yes | - |
| `POD_SQUAD` | variable | 4 (fixed setpoint: one pawn per pod, 1..30) | pod-assault | yes | - |
| `POST_STRICTNESS` | UNDEFINED | - | config-post-strictness | no | add to tags.variables |
| `PRODUCT_BILL` | UNDEFINED | - | econ-druglab, rung-4-production | no | add to tags.variables |
| `QUEST_MIN_FIGHT_RATIO` | UNDEFINED | - | empire-quest | no | add to tags.variables |
| `REACTOR_HOURS` | UNDEFINED | - | endgame-load-caskets | no | add to tags.variables |
| `RETURN_HOURS` | UNDEFINED | - | br-return-window | no | add to tags.variables |
| `RUNDOWN_EVERY_S` | UNDEFINED | - | viewer-joined | no | add to tags.variables |
| `SECURITY_SILVER` | UNDEFINED | - | econ-money-to-security | no | add to tags.variables |
| `SHELTER_H` | UNDEFINED | - | start-camp-shelter | no | add to tags.variables |
| `SHELTER_W` | UNDEFINED | - | start-camp-shelter | no | add to tags.variables |
| `SHELTER_WOOD` | UNDEFINED | - | start-camp-chop-fallback, start-camp-shelter | no | add to tags.variables |
| `SHIP_ADV_COMPS` | UNDEFINED | - | endgame-materials-check, endgame-ship-materials, ship-launch, space-ship-materials | no | add to tags.variables |
| `SHIP_COMPS` | UNDEFINED | - | endgame-materials-check, endgame-ship-materials, space-ship-materials | no | add to tags.variables |
| `SHIP_FUEL_RESERVE` | variable | 300 (fixed setpoint (UNVERIFIED: gravship fuel use), 50..10000) | supply-shipfuel-0-reset, supply-shipfuel-1-low | yes | - |
| `SHIP_GOLD` | UNDEFINED | - | endgame-materials-check, space-ship-materials | no | add to tags.variables |
| `SHIP_PARTS_TARGET` | UNDEFINED | - | endgame-ship-build, ship-launch | no | add to tags.variables |
| `SHIP_PLASTEEL` | UNDEFINED | - | endgame-materials-check, ship-launch, space-ship-materials | no | add to tags.variables |
| `SHIP_STEEL` | UNDEFINED | - | endgame-materials-check, ship-launch, space-ship-materials | no | add to tags.variables |
| `SHIP_TURRETS` | UNDEFINED | - | space-prelaunch-defence | no | add to tags.variables |
| `SHIP_URANIUM` | UNDEFINED | - | endgame-materials-check, ship-launch, space-ship-materials | no | add to tags.variables |
| `SILVER_FLOOR` | UNDEFINED | - | br-company-supply | no | add to tags.variables |
| `START_SURVIVAL_MEALS` | UNDEFINED | - | setup-0-starting-goods | no | add to tags.variables |
| `STEEL_FLOOR` | UNDEFINED | - | br-company-supply | no | add to tags.variables |
| `STEEL_RESERVE` | variable | 450 (150 per colonist, 150..20000) | supply-steel-0-reset, supply-steel-1-buy, supply-steel-2-mine, turret-line | yes | - |
| `STOCK_CELLS` | variable | 75 (30 + 15 per colonist, 30..2000) | stockpiles-sized | yes | - |
| `STONE_BLOCK_TARGET` | UNDEFINED | - | econ-marble, rung-4-production | no | add to tags.variables |
| `TARGET_TITLE` | variable | 6 (fixed setpoint: 6 = Baron (rank list after Count UNVERIFIED), 1..9) | empire-dominion, endgame-royal-ascent | yes | - |
| `TRADE_SILVER_MIN` | variable | 500 (fixed setpoint, 100..20000) | econ-silver-company, recruit-past-three, supply-steel-1-buy, trade-run, vault | yes | - |
| `TRY_PRESET` | UNDEFINED | - | start-camp-chop-fallback, start-camp-shelter-fallback | no | add to tags.variables |
| `TURRET_TARGET` | variable | 3 (2 + colonists/3, 2..30) | defense-0-reset-turrets, defense-1-secure, defense-3-turrets, turret-line | yes | - |
| `WAR_MIN_CREW` | variable | 6 (fixed setpoint: raid with 4, leave 2, 3..60) | war-prep | yes | - |
| `WEAPON_KEEP` | variable | 5 (colonists + 2 spare loose weapons, 2..200) | econ-wealth-junk, supply-weapons-0-reset, supply-weapons-1-sell, supply-weapons-2-smelt | yes | - |
| `WEBCAM_MAX_S` | UNDEFINED | - | webcam-stale | no | add to tags.variables |
| `WINTER_ANIMAL_CAP` | UNDEFINED | - | animals-autumn-cull | no | add to tags.variables |
| `WOOD_FLOOR` | UNDEFINED | - | blueprints-but-no-material, setup-chop | no | add to tags.variables |
| `WOOD_RESERVE` | variable | 180 (60 per colonist, 100..2000) | camp-wood-wall-ring, econ-wood-reset, econ-wood-winter | yes | - |
| `WOOD_TARGET` | UNDEFINED | - | setup-chop | no | add to tags.variables |

## 4. Instructions (ton / tof / ctu / ons / any / not): 112 instances, 17 malformed

Window: the label is one box on the Ladder row; accumulated ticks and the counter value are not displayed anywhere.

| rung | label | op | params | well-formed? |
|---|---|---|---|---|
| animals-food-steady | `food_held` | ton | {"hours": 24} | yes |
| animals-hunt-food | `hunt_ok` | not | - | NO: operator/parameter "reset" written as a plain key inside the operand (needs a label object around it) |
| animals-hunt-fallback | `hunt_ok` | ctu | {"preset": 3} | yes |
| tame-mounts | `tame_ok` | not | - | NO: operator/parameter "reset" written as a plain key inside the operand (needs a label object around it) |
| animal-pen | `has_stock` | any | - | yes |
| animals-autumn-cull | `autumn` | ons | - | yes |
| br-out-fallback | `explore_fails` | ctu | {"preset": 3} | yes |
| br-heat | `heat` | any | - | yes |
| br-camp-wall | `wall_fails` | ctu | {"preset": 3} | yes |
| br-company-supply | `short` | any | - | yes |
| br-company-supply | `order_fails` | not | - | NO: operator/parameter "reset" written as a plain key inside the operand (needs a label object around it) |
| br-sustainable | `held` | ton | {"hours": 72} | yes |
| br-gate-facility-fallback | `fac_fails` | ctu | {"preset": 3} | yes |
| gate-open-fallback | `open_fails` | ctu | {"preset": 2} | yes |
| br-return-window | `over` | ton | {"hours": "{RETURN_HOURS}"} | yes |
| camp-wood-wall-ring | `build_tries` | ctu | {"preset": 3} | yes |
| camp-wood-wall-fallback | `build_tries` | ctu | {"preset": 3} | yes |
| finish-before-new | `unfinished_hold` | ton | {"hours": 24} | yes |
| config-ui-clear-stuck | `stuck` | ctu | {"preset": 3} | yes |
| work-priorities-fallback | `held` | ton | {"hours": 3} | yes |
| config-priorities-new-pawn | `rejoined` | ctu | {"preset": 2} | yes |
| bills-missing-fallback | `tries` | ctu | {"preset": 3} | yes |
| fields-wrong-fallback | `held` | ton | {"hours": 4} | yes |
| econ-corpses-standing | `held` | ton | {"hours": 12} | yes |
| econ-freezer-shelves | `tries` | not | - | NO: operator/parameter "reset" written as a plain key inside the operand (needs a label object around it) |
| econ-freezer-fallback | `tries` | ctu | {"preset": 3} | yes |
| crops-full-set | `tries` | not | - | NO: operator/parameter "reset" written as a plain key inside the operand (needs a label object around it) |
| econ-crops-fallback | `tries` | ctu | {"preset": 3} | yes |
| econ-trader-arrived | `arrival` | ons | - | NO: operator/parameter "any" written as a plain key inside the operand (needs a label object around it) |
| econ-trade-reset | `held` | ton | {"hours": 72} | yes |
| econ-quests-cash | `offer` | ons | - | yes |
| econ-guest-beds-full | `full` | ons | - | yes |
| econ-checklist | `held` | ton | {"hours": 24} | yes |
| empire-dominion | `ready` | any | - | yes |
| endgame-research-refused | `stuck` | ctu | {"preset": 3} | yes |
| endgame-persona-core-stuck | `waited` | ton | {"hours": "{PERSONA_CORE_WAIT_HOURS}"} | yes |
| endgame-ship-build-refused | `stuck` | ctu | {"preset": 3} | yes |
| endgame-load-caskets | `held` | ton | {"hours": "{REACTOR_HOURS}"} | yes |
| endgame-royal-ascent | `royal_letter` | ons | - | yes |
| endgame-archonexus | `arch_letter` | ons | - | yes |
| endgame-journey-offer | `journey` | ons | - | yes |
| growth-catch-up | `backlog` | ton | {"hours": 2} | yes |
| growth-joiner-letter | `joiner` | ons | - | yes |
| growth-hospital-fallback | `hospital_tries` | ctu | {"preset": 3} | yes |
| growth-private-rooms-fallback | `private_rooms_tries` | ctu | {"preset": 3} | yes |
| ideo-roles | `roles_refused` | not | - | NO: operator/parameter "reset" written as a plain key inside the operand (needs a label object around it) |
| ideo-roles-fallback | `roles_refused` | ctu | {"preset": 3} | yes |
| ideo-role-abilities | `held` | ton | {"hours": 24} | yes |
| ideo-ritual-hold | `gap` | ton | {"hours": 120} | yes |
| bio-growth-moment | `growth` | ons | - | yes |
| power-generators-outside | `cancelled` | not | - | NO: operator/parameter "reset" written as a plain key inside the operand (needs a label object around it) |
| power-generators-fallback | `cancelled` | ctu | {"preset": 2} | yes |
| dialog-stuck | `dialog_tries` | ctu | {"preset": 3} | yes |
| threat-moment | `threat_onset` | ons | - | NO: operator/parameter "any" written as a plain key inside the operand (needs a label object around it) |
| updated-spark | `spark` | ons | - | yes |
| unforbid-constant | `unforbid_due` | any | - | yes |
| unforbid-constant | `landed` | ons | - | yes |
| unforbid-constant | `raid_over` | ons | - | yes |
| unforbid-constant | `drop` | ons | - | yes |
| crew-armed-attack | `crew_unready` | any | - | yes |
| game-paused-stuck | `pause_tries` | ctu | {"preset": 3} | yes |
| research-bench-fallback | `bench_tries` | ctu | {"preset": 3} | yes |
| research-idle | `idle_held` | ton | {"hours": 1} | yes |
| research-idle-fallback | `stall` | ctu | {"preset": 3} | NO: operator/parameter "ons" written as a plain key inside the operand (needs a label object around it) |
| research-rush-micro | `not_rushing` | not | - | yes |
| research-queue-multi | `not_queued` | not | - | yes |
| research-equipment-tiers | `tier_day` | ton | {"hours": 24} | yes |
| research-researcher-balance | `hogging` | ton | {"hours": 6} | yes |
| research-production-money | `money_day` | ton | {"hours": 48} | yes |
| title-track | `title_changed` | ons | - | yes |
| empire-quest | `quest_new` | ons | - | yes |
| bestowing | `bestow` | ons | - | yes |
| throne-room-retry | `throne_fail` | ctu | {"preset": 3} | yes |
| rooms-level-up | `lvl` | ton | {"hours": 48} | yes |
| setup-0-starting-goods | `landed` | ons | - | yes |
| arms-out-fallback | `arms_tries` | ctu | {"preset": 2} | yes |
| setup-2-pawns-fallback | `prio_tries` | ctu | {"preset": 3} | yes |
| setup-1-explore-fallback | `explore_stuck` | ton | {"hours": 6} | yes |
| setup-4-stores | `explored` | any | - | yes |
| setup-4-stores-fallback | `store_fail` | any | - | yes |
| setup-4-stores-fallback | `store_tries` | ctu | {"preset": 2} | yes |
| setup-4-stores-fallback | `store_slow` | ton | {"hours": 3} | yes |
| setup-8-camp-stable | `stable_held` | ton | {"hours": 24} | yes |
| setup-9-new-pawn | `new_pawn` | ons | - | yes |
| space-trade-comms | `t_trade_cooldown` | not | - | NO: operator/parameter "hours" written as a plain key inside the operand (needs a label object around it) |
| space-trade-comms | `c_trade_fail` | not | - | NO: operator/parameter "reset" written as a plain key inside the operand (needs a label object around it) |
| space-trade-comms-fallback | `c_trade_fail` | ctu | {"preset": 3} | yes |
| space-ally-gifts | `t_gift` | not | - | NO: operator/parameter "hours" written as a plain key inside the operand (needs a label object around it) |
| space-ship-materials | `any_short` | any | - | yes |
| space-reactor-hold | `t_reactor` | not | - | NO: operator/parameter "hours" written as a plain key inside the operand (needs a label object around it) |
| space-launch-load | `t_reactor_done` | ton | {"hours": 360} | yes |
| space-ask-chat | `t_ask` | ton | {"hours": 24} | yes |
| start-colony-lost | `lost` | ons | - | yes |
| start-camp-chop | `chop_fail` | not | - | NO: operator/parameter "reset" written as a plain key inside the operand (needs a label object around it) |
| start-camp-chop-fallback | `chop_fail` | ctu | {"preset": "{TRY_PRESET}"} | yes |
| start-camp-shelter | `shelter_fail` | not | - | NO: operator/parameter "preset" written as a plain key inside the operand (needs a label object around it) |
| start-camp-shelter-fallback | `shelter_fail` | ctu | {"preset": "{TRY_PRESET}"} | yes |
| start-explore-facility | `explore_fail` | not | - | NO: operator/parameter "preset" written as a plain key inside the operand (needs a label object around it) |
| start-camp-stable | `food_held` | ton | {"hours": "{CAMP_STABLE_HOURS}"} | yes |
| starving-no-game | `starve_retry` | ctu | {"preset": 2} | yes |
| butcher-fast | `corpse_age` | ton | {"hours": 24} | yes |
| storage-audit | `audit` | ton | {"hours": 24} | yes |
| medicine-reserve | `medicine_low` | ton | {"hours": 48} | yes |
| colony-before-research | `any_urgent` | any | - | yes |
| after-the-kill | `kill_over` | ons | - | yes |
| war-letter-classify | `new_threat` | ons | - | yes |
| war-siege-counter | `siege_held` | ton | {"hours": 6} | yes |
| war-stand-down | `clear` | ton | {"hours": 1} | yes |
| war-arms-fallback | `equip_fail` | ctu | {"preset": 3} | yes |
| war-fortification-repair | `damage` | any | - | yes |
| war-wall-tour | `tour` | ons | - | yes |
| assault-retreat-count | `downs` | ctu | {"preset": 3} | yes |

### 4b. Broken `when` entries (40): the rung is Unresolved (red) or the branch can never hold

| rung | key | problem |
|---|---|---|
| animals-hunt-food | `ctu` | object is not exactly one instruction: {"designations_hunt": 0} |
| animals-hunt-food | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| animals-hunt-food | `reset` | object is not exactly one instruction: {"days_of_food": ">={FOOD_MIN_DAYS}"} |
| tame-mounts | `ctu` | object is not exactly one instruction: {"designations_tame": 0} |
| tame-mounts | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| tame-mounts | `reset` | object is not exactly one instruction: {"colony_animals": ">0"} |
| br-company-supply | `ctu` | object is not exactly one instruction: {"mark_company_order_refused": true} |
| br-company-supply | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| br-company-supply | `reset` | object is not exactly one instruction: {"mark_company_order_refused": false} |
| econ-freezer-shelves | `ctu` | object is not exactly one instruction: {"mark_freezer_attempt": true} |
| econ-freezer-shelves | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| econ-freezer-shelves | `reset` | object is not exactly one instruction: {"mark_freezer_shelves_set": true} |
| crops-full-set | `ctu` | object is not exactly one instruction: {"mark_crops_attempt": true} |
| crops-full-set | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| crops-full-set | `reset` | object is not exactly one instruction: {"mark_crops_full": true} |
| econ-trader-arrived | `any` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| ideo-roles | `ctu` | object is not exactly one instruction: {"mark_ideo_roles_refused": true} |
| ideo-roles | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| ideo-roles | `reset` | object is not exactly one instruction: {"mark_ideo_roles_set": true} |
| power-generators-outside | `ctu` | object is not exactly one instruction: {"mark_generator_cancelled": true} |
| power-generators-outside | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| power-generators-outside | `reset` | object is not exactly one instruction: {"power_generators": ">=2"} |
| threat-moment | `any` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| research-idle-fallback | `ons` | object is not exactly one instruction: {"research_queue_empty": true} |
| space-trade-comms | `ton` | object is not exactly one instruction: {"mark_traded_recently": true} |
| space-trade-comms | `hours` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| space-trade-comms | `ctu` | object is not exactly one instruction: {"mark_trade_call_failed": true} |
| space-trade-comms | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| space-trade-comms | `reset` | object is not exactly one instruction: {"mark_traded_recently": true} |
| space-ally-gifts | `ton` | object is not exactly one instruction: {"mark_gift_sent": true} |
| space-ally-gifts | `hours` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| space-reactor-hold | `ton` | object is not exactly one instruction: {"mark_reactor_started": true} |
| space-reactor-hold | `hours` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| start-camp-chop | `ctu` | object is not exactly one instruction: {"mark_chop_refused": true} |
| start-camp-chop | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| start-camp-chop | `reset` | object is not exactly one instruction: {"wood": ">={CAMP_WOOD}"} |
| start-camp-shelter | `ctu` | object is not exactly one instruction: {"mark_shelter_refused": true} |
| start-camp-shelter | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |
| start-explore-facility | `ctu` | object is not exactly one instruction: {"mark_explore_refused": true} |
| start-explore-facility | `preset` | instruction word used as a plain when key: read as an unmeasured sensor, the branch never holds |

## 5. Outputs (tools a rung step drives): 64 tools named

Steps whose first word is not a tool are prose orders to her (736 steps) and are not counted.

| tool | exists? | used by rungs |
|---|---|---|
| `call_trader` | NO | supply-steel-1-buy, supply-weapons-1-sell, trade-run |
| `company_order` | NO | econ-silver-company |
| `designate_gate` | NO | rung-5b-the-gate |
| `door_lock` | NO | guest-wing |
| `edit_drug_policy` | NO | config-antibiotics |
| `empire_pass` | yes | arms-out-fallback, arms-out-first, crew-armed-attack, econ-silver-company, endgame-greed, endgame-launch-defence, endgame-reactor-hold, endgame-ship-materials, growth-new-pawn-setup, growth-upgrade-everyone, maintenance-sweep, start-crashlanded, start-new-pawn, war-arms-sidearms |
| `game_apply_architect_designator` | yes | br-camp-wall, br-heat, cold-snap, comms, econ-butcher, econ-corral, econ-druglab, econ-guest-beds-full, econ-money-to-security, endgame-ship-build, fire-in-camp, firebreak, food-rotting-or-no-cold, guest-wing, pawn-starving, repair-2-set, rung-5b-the-gate, ship-launch, starving, supply-steel-2-mine |
| `game_click_cell` | yes | combat-2-fight, endgame-launch, endgame-reactor-start, fields-wrong-fallback, ideo-ritual-hold |
| `game_click_ui_target` | yes | br-contact-company, dialog-open |
| `game_close_main_tab` | yes | camera-on-crew, config-schedule-anything, config-ui-clear, config-ui-clear-stuck, work-priorities-fallback |
| `game_close_window` | yes | config-ui-clear |
| `game_dismiss_letter` | yes | letter-unread |
| `game_execute_gizmo` | yes | ideo-role-abilities, raid-posted |
| `game_get_cell_info` | yes | econ-crops-fallback |
| `game_get_cells_info` | yes | animals-milk-herd, animals-pen-soil, br-camp-wall, br-out-of-the-backrooms, endgame-ship-site, food-rotting-or-no-cold, power-every-consumer, start-camp-chop-fallback, tame-mounts |
| `game_get_context_menu_options` | yes | fields-wrong-fallback, space-trade-comms |
| `game_get_ui_layout` | yes | config-ui-clear-stuck, dialog-open, dialog-stuck, game-paused-stuck |
| `game_jump_camera_to_cell` | yes | bills-missing-fallback, camera-on-crew |
| `game_list_alerts` | yes | rot-alert |
| `game_list_architect_designators` | yes | animal-pen, br-gate-facility-fallback, butcher-table, endgame-launch-defence, endgame-ship-build, grav-build, ship-launch, start-camp-shelter-fallback |
| `game_list_colonists` | yes | animals-danger-clear, animals-handler, animals-hunter-armed, bio-family-rooms, camera-on-crew, config-ui-clear, downed-pawn, empire-hostile, endgame-load-caskets, ideo-colony-policy, life-threat, mental-break, work-priorities-unset |
| `game_list_letters` | yes | empire-quest, endgame-persona-core, grav-core, letter-unread |
| `game_list_selected_gizmos` | yes | cavalry-check |
| `game_list_zones` | yes | br-natural-gate-room, config-stockpile-priority, fields-wrong, space-trade-beacon |
| `game_open_letter` | yes | anomaly-entity, bestowing, bio-growth-moment, empire-quest, endgame-archonexus, endgame-journey-offer, endgame-royal-ascent |
| `game_open_main_tab` | yes | animals-autumn-cull, br-contact-company, growth-look-at-world, ideo-ritual, ideo-roles, leader-moral-guide, leader-role, train-mounts, work-priorities-fallback |
| `game_pause_game` | yes | combat-2-fight, config-hud-restore, empire-hostile, fire-in-camp, game-paused-stuck, hostile-on-map, setup-0-pause-on-land, war-stand-down, work-priorities-unset |
| `game_press_accept` | yes | bio-growth-moment |
| `game_select_architect_designator` | yes | animals-milk-herd, camp-wood-wall-ring, power-alternate, power-batteries, power-every-consumer, power-generators-outside, setup-4-stores-fallback, space-trade-beacon, tame-mounts, throne-base-plan |
| `game_select_pawn` | yes | ideo-role-abilities |
| `game_set` | yes | after-the-kill, animals-butcher-standing, animals-danger-clear, animals-haygrass, animals-hunt-food, animals-hunter-armed, animals-kibble, anomaly-dissection, armor-mounts, arms-out-first, bedrooms-owned, beds-short, bills-missing, bio-child-care, bio-family-rooms, blueprints-but-no-material, br-haul-out, br-out-fallback, br-out-of-the-backrooms, br-trade-income, butcher-fast, camp-wood-wall-fallback, camp-wood-wall-ring, cold, cold-snap, components-low, config-antibiotics, config-assign-tab, corpses-buried, crew-armed-attack, crops-full-set, disease, downed-pawn, drugs-econ, econ-art, econ-butcher, econ-corpses-standing, econ-corral, econ-crops-fallback, econ-druglab, econ-dump-zone, econ-fields-outside, econ-freezer-fallback, econ-freezer-shelves, econ-marble, econ-wealth-junk, econ-wood-winter, endgame-launch-defence, endgame-reactor-hold, endgame-ship-materials, endgame-ship-site, fire-in-camp, food-low, freezer-cluster, freezer-sorting, gate-assemble, growth-family, growth-healroot-and-cash-crops, growth-hospital, growth-hospital-fallback, growth-new-pawn-setup, growth-prisoner-keep, growth-private-rooms, growth-private-rooms-fallback, growth-shelves-everything, growth-spare-bed, hospital-setup, ideo-antibiotics, ideo-colony-policy, ideo-party-room, ideo-ritual, meals-early, medicine-reserve, no-medicine, pawn-starving, power-ac-fridge, prisoner-bed-before-fight, repair-after-raid, research-bench, research-bench-fallback, royal-rooms, royal-vault, rung-4-production, rung-5c-the-backrooms, setup-0-unforbid, setup-1-explore, setup-3-assign, setup-4-stores, setup-4b-shelter, setup-5-stove, setup-6b-crops, setup-9-new-pawn, setup-chop, shelter-night-one, space-ship-materials, start-camp-beds, start-camp-chop, start-camp-chop-fallback, start-camp-food, start-camp-shelter, start-camp-stores, start-crashlanded, start-explore-facility, start-naked, start-new-pawn, start-tribal, starving, stockpiles-sized, stone-blocks-bench, storage-logic, storage-shelves, supply-food-1-low, supply-podfuel-1-low, supply-shipfuel-1-low, supply-weapons-2-smelt, train-mounts, unforbid-constant, vault, war-after-kill-storage, war-hostility-attack, war-manhunter, war-manhunter-butcher, war-mobilize, war-organ-harvest, war-weapons-upgrade, warm-clothes, work-priorities-unset |
| `game_set_draft` | yes | cavalry-check, combat-2-fight, hostile-on-map, raid-cleanup |
| `game_set_time_speed` | yes | empire-hostile, game-paused, hostile-on-map |
| `game_state` | yes | animals-food-steady, econ-stray-blueprint, empire-dominion, endgame-launch-defence, endgame-ship-materials, endgame-ship-research, growth-new-pawn-setup, growth-rescue-and-tend, new-colony, research-bench, start-kind-unknown, unforbid-constant |
| `game_take_screenshot` | yes | br-base-layout, br-out-fallback, config-ui-clear-stuck, endgame-ship-build-refused, throne-room-layout, throne-room-retry |
| `hospitality_sell_zone` | NO | guest-wing |
| `ladder` | yes | idle-watchdog |
| `ladder_set` | yes | after-the-kill, altar-room, animal-pen, animals-food-steady, animals-handler, animals-haygrass, animals-pen-soil, anomaly-dissection, arms-out-first, assault-retreat-count, battery-room, big-plan, bio-child-care, bio-family-rooms, bio-milk-pen, br-camp-wall, br-contact-company, br-gate-facility-fallback, br-return-window, br-sustainable, butcher-table, camp-wood-wall-fallback, camp-wood-wall-ring, caravan-raid, cold, combat-0-reassess-better, combat-0-reassess-worse, combat-0-reset, combat-1-damage-pause, combat-2-call-help-comms, combat-2-call-help-permit, combat-2-fight, combat-2-help-coming, combat-2-kite, combat-2-retreat, comms, components-low, config-antibiotics, config-assign-tab, config-drug-policy, config-hospitality-visitors, config-hud-restore, config-priorities-new-pawn, config-schedule-anything, config-stockpile-priority, config-ui-clear-stuck, crops-full-set, defense-0-reset-damage, defense-0-reset-embrasures, defense-0-reset-turrets, defense-1-secure, dining-room, double-bed-rooms, drugs-econ, econ-art, econ-butcher, econ-components-reset, econ-corral, econ-crops-fallback, econ-druglab, econ-dump-zone, econ-fields-outside, econ-freezer-fallback, econ-freezer-shelves, econ-marble, econ-money-to-security, econ-silver-company, econ-stray-blueprint, econ-trade-reset, econ-wood-reset, econ-wood-winter, empire-dominion, empire-quest, endgame-defence-check, endgame-launch, endgame-load-caskets, endgame-materials-check, endgame-reactor-start, endgame-research-refused, endgame-ship-build-refused, endgame-ship-site, firebreak, firebreak-ring, freezer-cluster, freezer-sorting, gate-assemble, gate-open-fallback, gate-power, gate-staffed, generators-out, grav-core, grav-ready, growth-dining-and-rec, growth-hospital, growth-hospital-fallback, growth-ideology-content, growth-look-at-world, growth-private-rooms, growth-private-rooms-fallback, growth-second-colony, guest-wing, hitech-bench, hospital, hospital-setup, hvac-clusters, ideo-antibiotics, ideo-colony-policy, ideo-party-room, ideo-ritual, ideo-roles, ideo-roles-fallback, infestation-walloff, killbox-funnel, kitchen-clean, landing-pad, leader-moral-guide, leader-role, meals-early, med-2-field-tend, med-3-carry-to-hospital, new-colony, permit-aid, power-every-consumer, power-generators-outside, prison-wing, prisoner-bed-before-fight, psycasts, repair-0-reset, repair-2-set, repair-after-raid, research-multi-analyzer, royal-rooms, royal-vault, rung-4-production, rung-5-the-mountain-base, rung-5b-the-gate, rung-5c-the-backrooms, rung-6-off-world, settlement-down, setup-0-new-colony, setup-0-starting-goods, setup-4-stores, setup-4-stores-fallback, setup-5-stove, setup-8-camp-stable, shelter-night-one, space-ally-gifts, space-launch-load, space-reactor-start, space-trade-comms, space-trade-comms-fallback, start-async, start-camp-beds, start-camp-chop-fallback, start-camp-shelter, start-camp-stable, start-camp-stores, start-camp-tight, start-crashlanded, start-kind-unknown, start-naked, start-tribal, starving, stockpiles-sized, stone-blocks-bench, storage-logic, stream-setup, supply-food-0-reset, supply-food-1-low, supply-podfuel-0-reset, supply-podfuel-1-low, supply-shipfuel-0-reset, supply-shipfuel-1-low, supply-steel-0-reset, supply-steel-1-buy, supply-steel-2-mine, supply-weapons-0-reset, supply-weapons-1-sell, supply-weapons-2-smelt, terraform-water-first, throne-base-plan, throne-room, throne-room-layout, title-track, trade-run, train-mounts, vault, war-after-kill-storage, war-bastions-towers, war-infestation-prevent, war-manhunter-butcher, war-mobilize, war-organ-harvest, war-prison-workcamp, war-siege-counter, war-stand-down, war-weapons-upgrade, work-grid-set |
| `look` | yes | research-idle-fallback, start-kind-unknown |
| `new_colony` | yes | growth-second-colony, new-colony, setup-0-new-colony, start-colony-lost, start-new-colony |
| `note` | yes | growth-look-at-world, mountain-base-plan, start-camp-stable |
| `order_pawn` | yes | animals-hunter-armed, bestowing, br-haul-out, br-out-fallback, br-return-window, config-haul-out-paced, disease, downed-pawn, econ-corpses-standing, econ-trader-arrived, empire-hostile, empire-quest, gate-open, gate-staffed, growth-rescue-and-tend, hostile-on-map, med-2-field-tend, med-3-carry-to-hospital, needs-tend, pawn-starving, war-arms-sidearms, war-drop-pods-centre, war-mobilize, war-stand-down |
| `pawn_check` | yes | crew-armed-attack, growth-needs-watch |
| `pawn_priorities` | yes | animals-handler, animals-hunter-armed, bio-milk-pen, butcher-fast, cold-snap, colony-before-research, disease, fire-in-camp, growth-new-pawn-setup, ideo-colony-policy, repair-2-set, research-researcher-balance, setup-2-pawns, setup-2-pawns-fallback, setup-2b-priorities-after-explore, ship-launch, space-microelectronics, start-crashlanded, start-new-pawn, starving, war-hostility-attack, work-grid-set, work-priorities-unset |
| `plan` | yes | big-plan, start-camp-stable, throne-base-plan |
| `play_slices` | yes | endgame-ship-build, game-paused-stuck, growth-catch-up, long-goal-drive |
| `reply_chat` | yes | chat-first, viewer-joined |
| `reply_owner` | yes | endgame-persona-core-stuck, endgame-research-refused, endgame-ship-build-refused, ideo-roles-fallback, owner-at-controls, owner-message, power-generators-fallback, start-camp-shelter-fallback |
| `run_list` | yes | endgame-greed, growth-catch-up, maintenance-sweep, start-standing-orders |
| `save_game` | NO | config-hud-restore |
| `say` | yes | animals-hunt-fallback, big-plan, colony-before-research, dead-air, dialog-stuck, empire-dominion, endgame-journey-offer, endgame-launch, endgame-persona-core-stuck, endgame-reactor-start, endgame-ship-research, game-paused, growth-needs-watch, growth-rescue-and-tend, idle-watchdog, letter-unread, maintenance-sweep, mental-break, new-colony, owner-at-controls, start-colony-lost, stream-setup, threat-moment, updated-spark, war-mobilize, window-not-in-front |
| `set_bed_price` | NO | econ-guest-beds-full, guest-wing |
| `set_bill_count` | NO | bills-raise-target |
| `set_drug_policy` | NO | config-drug-policy |
| `set_hospitality_accept` | NO | config-hospitality-visitors |
| `set_post_strictness` | NO | config-post-strictness |
| `set_schedule` | NO | config-schedule-anything |
| `set_window_mode` | NO | config-window-fullscreen |
| `snap` | yes | threat-moment |
| `toggle_hud` | NO | config-hud-restore |
| `trade_dialog` | NO | econ-trader-arrived, trade-run |
| `twitch_chat` | yes | br-chat-mod-links, research-bench-fallback, space-ask-chat, start-new-colony, stream-setup |
| `webcam` | yes | endgame-launch, threat-moment, webcam-stale |
| `zone_create` | NO | econ-dump-zone, econ-fields-outside |

### 5b. game_set commands: 19 named

| cmd | in tools.py enum? | used by rungs |
|---|---|---|
| `add_bill` | yes | animals-butcher-standing, animals-hunt-food, animals-kibble, anomaly-dissection, armor-mounts, bills-missing, bio-child-care, butcher-fast, cold, cold-snap, components-low, config-antibiotics, corpses-buried, drugs-econ, econ-art, econ-butcher, econ-druglab, econ-marble, econ-wealth-junk, endgame-launch-defence, endgame-reactor-hold, endgame-ship-materials, food-low, gate-assemble, ideo-antibiotics, meals-early, pawn-starving, rung-4-production, space-ship-materials, stone-blocks-bench, supply-food-1-low, supply-podfuel-1-low, supply-shipfuel-1-low, supply-weapons-2-smelt, war-manhunter-butcher, war-organ-harvest, war-weapons-upgrade, warm-clothes |
| `assign` | yes | arms-out-first, config-assign-tab, crew-armed-attack, disease, growth-new-pawn-setup, ideo-colony-policy, setup-3-assign, setup-9-new-pawn, start-crashlanded, start-new-pawn, start-tribal, war-hostility-attack, war-mobilize |
| `beds` | yes | bedrooms-owned, beds-short, growth-hospital-fallback, growth-spare-bed, prisoner-bed-before-fight, setup-4b-shelter, shelter-night-one, start-camp-beds, start-new-pawn |
| `chop` | yes | blueprints-but-no-material, econ-wood-winter, research-bench-fallback, setup-chop, shelter-night-one, start-camp-chop |
| `crops` | yes | animals-haygrass, crops-full-set, growth-healroot-and-cash-crops, medicine-reserve, no-medicine, setup-6b-crops, start-camp-food, supply-food-1-low |
| `explore` | yes | br-out-fallback, br-out-of-the-backrooms, rung-5c-the-backrooms, setup-1-explore, start-camp-chop-fallback, start-explore-facility |
| `hunt` | yes | animals-hunt-food, food-low, pawn-starving, setup-6b-crops, start-camp-food, start-tribal, starving, supply-food-1-low |
| `rooms` | yes | bedrooms-owned, bio-family-rooms, br-out-of-the-backrooms, econ-freezer-shelves, growth-hospital, growth-private-rooms, ideo-party-room, ideo-ritual, setup-4-stores, start-explore-facility, vault |
| `set_area` | yes | animals-danger-clear, camp-wood-wall-ring, endgame-ship-site, fire-in-camp, growth-new-pawn-setup, repair-after-raid, train-mounts, war-manhunter |
| `set_bed_owner` | yes | bedrooms-owned, beds-short, bio-family-rooms, downed-pawn, growth-family, growth-new-pawn-setup, growth-private-rooms, growth-private-rooms-fallback, growth-spare-bed, hospital-setup, prisoner-bed-before-fight, royal-rooms, start-camp-beds |
| `set_work_priority` | yes | econ-art, econ-corpses-standing, econ-corral, endgame-ship-materials, growth-hospital, growth-prisoner-keep, growth-shelves-everything, repair-after-raid, research-bench, rung-4-production, space-ship-materials, work-priorities-unset |
| `set_zone_plant` | yes | br-trade-income, crops-full-set, econ-crops-fallback, econ-fields-outside |
| `shelter` | yes | camp-wood-wall-fallback, growth-private-rooms-fallback, research-bench-fallback, setup-4b-shelter, shelter-night-one, start-camp-shelter, start-naked |
| `shelves` | yes | after-the-kill, growth-shelves-everything, royal-vault, stockpiles-sized, storage-shelves, war-after-kill-storage |
| `stockpile_camp` | yes | econ-freezer-fallback, start-camp-stores |
| `stockpile_filter` | yes | animals-butcher-standing, anomaly-dissection, drugs-econ, econ-dump-zone, econ-freezer-fallback, econ-freezer-shelves, freezer-sorting, growth-shelves-everything, royal-vault, setup-4-stores, storage-logic |
| `stockpile_room` | yes | econ-freezer-shelves, freezer-cluster, power-ac-fridge, vault |
| `stove` | yes | setup-5-stove, start-camp-food, start-tribal |
| `unforbid` | yes | after-the-kill, animals-butcher-standing, animals-hunter-armed, br-haul-out, setup-0-unforbid, shelter-night-one, start-crashlanded, start-tribal, unforbid-constant, war-after-kill-storage, war-manhunter-butcher |

Existing game_set commands no rebuilt rung drives: day_one, set_zone_sowing


## 6. Undefined tags: proposed rows for the tag table (from the families' variables_needed)

| tag | proposed value | rule | used by rungs |
|---|---|---|---|
| `ABLE_SHOOTERS` | = able_shooters (measured) | every able shooter armed | crew-armed-attack |
| `ART_BILL` | 2 * colonists | better sucurity and flooring and beutification of rooms | econ-art |
| `BEACONS_TARGET` | 2 | one per storage room (freezer + main store); raise as rooms are added | space-trade-beacon |
| `BLUEPRINT_BACKLOG` | 19 | 10 + 3 per colonist | growth-catch-up |
| `CAMP_STABLE_HOURS` | 24 | ton hold for setup-8-camp-stable | start-camp-stable |
| `CAMP_WOOD` | 300 | wood wanted for the first camp (the existing chop count 300) | start-camp-chop, start-camp-chop-fallback |
| `CHAT_DECIDE_S` | 20 | owner: "if i dont answer in 20second u make the call..." | dead-air, long-goal-drive |
| `COLONIST_TARGET` | 7 | walkthrough W Ship: 6-8 colonists by year 1, 10-15 by ship time; 7 until mark_mountain_base_done, then 12 (min 3, max 25) | growth-family, recruit-past-three |
| `COMPONENTS_FLOOR` | 10 | you have no components | br-company-supply |
| `CROP_CELLS` | 75 | 25 tiles per pawn on normal soil (walkthrough B) | setup-6b-crops, setup-8-camp-stable |
| `DEAD_AIR_MAX_S` | 30 | owner: "and we need to fix her 30 sec max time without speaking every like 30s -1m she needs to talk as she is suppose to and enguage the audiance and put on a show" | dead-air |
| `ENDGAME_COLONISTS` | 10 | W: 10-15 colonists by ship time | empire-dominion, endgame-defence-check |
| `FIELD_CELLS_TOTAL` | 75 | 25 per colonist on normal soil (walkthrough B: 75 tiles for 3) | growth-healroot-and-cash-crops |
| `FOOD_DAYS_STABLE` | 5 | camp stable before the mountain base | setup-8-camp-stable |
| `GATE_FIRST_WINDOW_MIN` | 30 | first opening be like 30 minutes of real time | gate-open |
| `GUEST_DRUG_STOCK` | 5 * guest_beds | drugs are for hospitality guests | drugs-econ |
| `HAY_CELLS_PER_ANIMAL` | 15 | walkthrough F: 1 haygrass field per 2-3 large animals; min 8 max 60 | animals-haygrass |
| `IDLE_WATCHDOG_S` | 60 | owner: "wtf keep fucking playing and set a watch dog so if u stop thinking idel for 1 minute we get woken with \"get the tests all completed\"" | idle-watchdog |
| `KIBBLE_FROM_ANIMALS` | 3 | start kibble at this many colony animals; min 1 max 20 | animals-kibble |
| `KIBBLE_TARGET` | 75 | walkthrough W Kibble: one batch = 75; 25 per animal, min 75 max 2000 | animals-kibble |
| `LAUNCH_FOOD_DAYS` | 30 | W Before reactor | endgame-defence-check, endgame-launch-defence |
| `LAUNCH_MEDICINE` | 20 | W Before reactor | endgame-defence-check |
| `LAUNCH_TURRETS` | 8 | judgement: W says turrets + kill box + mortars | endgame-defence-check, endgame-launch-defence |
| `LEVELS_MAX` | 4 | you already have 5 colonies builds of colonies open u have too close old ones if u want to open new ones | br-close-old-levels |
| `LINE_MAX_WORDS` | 18 | existing always rung: one spoken line, at most 18 words | always, dead-air |
| `LOOSE_ITEMS_MAX` | 14 | 5 + 3 per colonist | growth-shelves-everything |
| `MAX_LINES_QUEUED` | 1 | owner: "she is still sending like 3-4 messages at once" | voice-busy |
| `MEAL_BILL` | 50 | max(50, 10 x colonists); raised as the colony grows | bills-missing, bills-missing-fallback, bills-raise-target |
| `OWNER_SETTLE_S` | 10 | setpoint (owner may move it): "deffers instantly before attempting recontol once settles d mouse" | owner-at-controls |
| `PENOX_STOCK` | 6 | 2 x colonists (each carries 2) | config-antibiotics |
| `PEN_CELLS_PER_ANIMAL` | 30 | grazing area per animal; min 15 max 200 | animal-pen |
| `PEN_MIN_ANIMALS` | 1 | walkthrough says pen at Animals >= 5; owner wants a pen for milk animals from the first tame, so 1 | animal-pen |
| `PERSONA_CORE_WAIT_HOURS` | 480 | 20 days without a core -> ask chat and the owner | endgame-persona-core-stuck |
| `POST_STRICTNESS` | default | strict / default / mild; default lets pawns eat and seek safety | config-post-strictness |
| `PRODUCT_BILL` | 10 * colonists | set amounts higher and higher as your base grows | econ-druglab, rung-4-production |
| `QUEST_MIN_FIGHT_RATIO` | 1.5 | accept honor quests only when survivable | empire-quest |
| `REACTOR_HOURS` | 360 | 15 days x 24 h (W Reactor startup) | endgame-load-caskets |
| `RETURN_HOURS` | 6 | come back before the scout's needs bottom out | br-return-window |
| `RUNDOWN_EVERY_S` | 900 | owner: "she has three viewers and hasnet given a full run donwn catch up once and hasnt mentioned anyone by name watching yet" -- one catch-up per ~15 min | viewer-joined |
| `SECURITY_SILVER` | 3 * TRADE_SILVER_MIN | the money pays for security, floors, beauty | econ-money-to-security |
| `SHELTER_H` | 7 | walkthrough: 7x7 minimum | start-camp-shelter |
| `SHELTER_W` | 7 | walkthrough: 7x7 minimum, 9x9 better | start-camp-shelter |
| `SHELTER_WOOD` | 200 | minimum wood before the shelter cmd: 7x7 ring walls + door | start-camp-chop-fallback, start-camp-shelter |
| `SHIP_ADV_COMPS` | 40 | W Ship | endgame-materials-check, endgame-ship-materials, ship-launch, space-ship-materials |
| `SHIP_COMPS` | 12 | W Ship | endgame-materials-check, endgame-ship-materials, space-ship-materials |
| `SHIP_GOLD` | 74 | W Ship | endgame-materials-check, space-ship-materials |
| `SHIP_PARTS_TARGET` | 16 | 1 reactor + 3 engines + 1 core + 1 sensor + 10 caskets (beams excluded if ship_parts counts them; replace with ship_launchable once measured) | endgame-ship-build, ship-launch |
| `SHIP_PLASTEEL` | 740 | W Ship | endgame-materials-check, ship-launch, space-ship-materials |
| `SHIP_STEEL` | 1740 | W Ship | endgame-materials-check, ship-launch, space-ship-materials |
| `SHIP_TURRETS` | 6 | pre-reactor defence setpoint (UNVERIFIED, tune) | space-prelaunch-defence |
| `SHIP_URANIUM` | 294 | W Ship | endgame-materials-check, ship-launch, space-ship-materials |
| `SILVER_FLOOR` | 500 | and order some silver from the company | br-company-supply |
| `START_SURVIVAL_MEALS` | 100 | owner: survival meals "should be like 100 to start" | setup-0-starting-goods |
| `STEEL_FLOOR` | 200 | and use steel and order steel from the company | br-company-supply |
| `STONE_BLOCK_TARGET` | 200 | walkthrough: Stonecutter keep >= 200 stone blocks | econ-marble, rung-4-production |
| `TRY_PRESET` | 3 | ctu preset for refusals before the fallback rung | start-camp-chop-fallback, start-camp-shelter-fallback |
| `WEBCAM_MAX_S` | 120 | owner: "dont forget to update yout profile pic like every couple minutes" | webcam-stale |
| `WINTER_ANIMAL_CAP` | 6 | 2 per colonist until animal_food_days is measured; min 2 max 60 | animals-autumn-cull |
| `WOOD_FLOOR` | 100 | cost of queued blueprints, min 100 | blueprints-but-no-material, setup-chop |
| `WOOD_TARGET` | 300 | chop count per order | setup-chop |

## 7. Every sensor the family passes asked for (sensors_needed), with today's status

| family | key | how (as the family pass wrote it) | measured now? |
|---|---|---|---|
| animals | `alert_hunterlacksrangedweapon` | generic AlertKey of Alert_HunterLacksRangedWeapon -- confirm the class is in AlertClasses so the key is always written (missing key never fires) | yes: Sensors.cs generic alert_<def> (only while the def is loaded) |
| animals | `milk_animals` | home.mapPawns.SpawnedColonyAnimals.Count(p => p.GetComp<CompMilkable>() != null) | NO |
| animals | `tame_candidates` | wild animals (Faction == null, RaceProps.Animal) where !NeverHuntDefs.Contains(def) && !RaceProps.predator && p.RaceProps.wildness < 0.75 | NO |
| animals | `pen_markers` | home.listerBuildings.AllBuildingsColonistOfDef(ThingDefOf.PenMarker).Count() | NO |
| animals | `pen_roofed_cells` | for each pen marker: CompAnimalPenMarker.PenState enclosed cells where home.roofGrid.Roofed(c) | NO |
| animals | `pen_bad_soil_cells` | pen cells where home.terrainGrid.TerrainAt(c).fertility < 1.0f | NO |
| animals | `fresh_corpses` | ThingRequestGroup.Corpse where ((Corpse)t).GetRotStage() == RotStage.Fresh && InnerPawn.RaceProps.Animal | NO |
| animals | `animals_hungry` | SpawnedColonyAnimals.Count(p => p.needs.food != null && p.needs.food.CurCategory >= HungerCategory.Hungry) | NO |
| animals | `animal_food_days` | (hay + kibble nutrition from resourceCounter) / sum over colony animals of needs.food.FoodFallPerTick * 60000 | NO |
| animals | `trained_mounts` | SpawnedColonyAnimals.Count(p => MountDefs.Contains(p.def.defName) && p.training.HasLearned(TrainableDefOf.Obedience)) -- replaces hand-set mark mounts_trained | NO |
| animals | `handler_priority_set` | any free colonist with workSettings.GetPriority(WorkTypeDefOf.Handling) == 2 -- replaces mark handler_set | NO |
| animals | `designations_slaughter` | add {"Slaughter", "designations_slaughter"} to DesignationKeys | NO |
| backrooms | `chat_asks_mod` | not game-side: the chat reader sets it when a Twitch message mentions mod/repo/workshop | NO |
| backrooms | `start_in_backrooms` | Find.Maps.Any(m => m.Parent is the Rimrooms backrooms MapParent && m.mapPawns.FreeColonistsSpawnedCount > 0) at first scan | NO |
| backrooms | `natural_gate_cell` | map.listerThings.AllThings.FirstOrDefault(t => t.def is a Rimrooms natural gate/portal def)?.Position | NO |
| backrooms | `gate_open / gate_online / gate_sections_done` | the Rimrooms gate comp on the designated door (connection state, sections built) read via the mod's types | NO |
| backrooms | `crew_across` | Find.Maps.Where(backrooms parent).Sum(m => m.mapPawns.FreeColonistsSpawnedCount) > 0 | NO |
| backrooms | `operator_on_station` | PawnsFinder.AllMaps_FreeColonistsSpawned.Any(p => p.CurJobDef is the Rimrooms operate-console job) | NO |
| backrooms | `count_RawSilver (generic count_ covers it; listed for SILVER_FLOOR)` | map.resourceCounter.GetCount(ThingDefOf.Silver) | NO: mixed case, Sensors.cs writes `count_rawsilver` |
| base-and-fortress | `wall_gaps` | for each Building with def.building.isWall... flood the perimeter: count cells on the Home-area boundary where !c.Impassable(map) && no Building_Door && c.Roofed==false inside a wall line; simpler: Region/Room.OpenRoofCount + Room.TouchesMapEdge for colony roo | NO |
| base-and-fortress | `unpowered_consumers` | map.listerBuildings.allBuildingsColonist.Count(b => b.TryGetComp<CompPowerTrader>() is {} p && p.PowerNet == null) | NO |
| base-and-fortress | `power_margin_pct` | sum PowerNet.CurrentEnergyGainRate() over map.powerNetManager.AllNetsListForReading / sum of consumer PowerOutput (negative) * 100 | NO |
| base-and-fortress | `torch_lamps` | map.listerThings.ThingsOfDef(ThingDefOf.TorchLamp).Count(t => t.Faction == Faction.OfPlayer) | NO |
| base-and-fortress | `colonists_without_bedroom` | map.mapPawns.FreeColonists.Count(p => p.ownership.OwnedBed == null // p.ownership.OwnedRoom == null // p.ownership.OwnedBed.ForPrisoners) | NO |
| base-and-fortress | `rooms_out_of_temp` | map.regionGrid.allRooms.Count(r => !r.PsychologicallyOutdoors && r.ProperRoom && r.Role != null && (r.Temperature < 10 // r.Temperature > 35)) | NO |
| base-and-fortress | `loose_items_off_shelf` | map.listerHaulables.ThingsPotentiallyNeedingHauling().Count + things in stockpile zones not on a Building_Storage (StoreUtility.CurrentStoragePriorityOf < Normal) | NO |
| base-and-fortress | `unfloored_room_cells` | colony ProperRooms (Role bedroom/hospital/kitchen/dining): count cells where !c.GetTerrain(map).layerable && !terrain.IsFloor | NO |
| base-and-fortress | `room_wall_holes` | rooms with Role != null whose Room.TouchesMapEdge==false but Room.OpenRoofCount>0 or Room.IsDoorway count; or roofed cells whose District.Room.PsychologicallyOutdoors while c.Roofed | NO |
| base-and-fortress | `camp_water_cells` | Home area cells where map.terrainGrid.TerrainAt(c).IsWater // c.GetTerrain(map) == TerrainDefOf.Mud/Marsh | NO |
| base-and-fortress | `blueprints_against_rock` | map.listerThings.ThingsInGroup(ThingRequestGroup.Blueprint) where entity def isWall and a cardinal neighbour is Mineable (Building.def.mineable) and fogged | NO |
| configuration | `hud_visible` | !Find.UIRoot (UIRoot_Play).screenshotMode.Active | NO |
| configuration | `window_fullscreen` | UnityEngine.Screen.fullScreenMode == FullScreenMode.ExclusiveFullScreen | NO |
| configuration | `manual_priorities` | Current.Game.playSettings.useWorkPriorities | NO |
| configuration | `schedule_all_anything` | all free colonists: pawn.timetable.times.All(t => t == TimeAssignmentDefOf.Anything) | NO |
| configuration | `drug_policy_no_hard` | all colonists: pawn.drugs.CurrentPolicy entries with drug.IsHardDrug have allowedForJoy/allowedForAddiction/allowScheduled all false | NO |
| configuration | `penox_policy_set` | all colonists: CurrentPolicy[ThingDef Penoxycyline].allowScheduled && daysFrequency==5 && takeToInventory==2 | NO |
| configuration | `hostility_all_attack` | all colonists: pawn.playerSettings.hostilityResponse == HostilityResponseMode.Attack | NO |
| configuration | `self_tend_all` | all colonists capable of Doctor: pawn.playerSettings.selfTend | NO |
| configuration | `meal_bill_target` | max Bill_Production.targetCount over stoves' BillStack where recipe produces a meal and repeatMode == BillRepeatModeDefOf.TargetCount | NO |
| configuration | `room_count` | map.regionGrid.AllRooms.Count(r => r.ProperRoom && !r.PsychologicallyOutdoors && !r.IsDoorway) | NO |
| configuration | `loose_items_unstored` | map.listerHaulables.ThingsPotentiallyNeedingHauling().Count | NO |
| configuration | `stockpile_priorities_set` | map.zoneManager.AllZones.OfType<Zone_Stockpile>() Select(settings.Priority).Distinct().Count() > 1 when 2+ stockpiles | NO |
| configuration | `visitors_accepted` | Hospitality mod world component accept-visitors flag via reflection | NO |
| configuration | `cleaning_assigned` | any colonist workSettings.GetPriority(WorkTypeDefOf.Cleaning) in 1..2 | NO |
| economy | `freezer_temp` | rooms containing a Building_Cooler: room.Temperature, min over rooms whose stockpile allows food | NO |
| economy | `food_outside_freezer` | rottable food stacks (CompRottable) on cells whose GetRoom().Temperature > 0 | NO |
| economy | `guest_beds` | Hospitality: Building_GuestBed instances (reflection on type name) count | NO |
| economy | `guest_beds_priced` | Hospitality Building_GuestBed rentalFee field > 0 via reflection | NO |
| economy | `sell_zone_set` | Hospitality guest shopping area (reflection on MapComponent_GuestAreas / Area label) | NO |
| economy | `vault_set` | a room (roofed, 1 door, not PsychologicallyOutdoors) whose Zone_Stockpile filter allows Silver/Gold and nothing food | NO |
| economy | `fields_outside_walls` | Zone_Growing cells where cell.GetRoom(map).PsychologicallyOutdoors and outside the home-wall enclosure | NO |
| economy | `pen_cells` | CompAnimalPenMarker on map.listerBuildings: PenState.ConnectedRegions cell count | NO |
| economy | `trader_on_map` | map.mapPawns.AllPawnsSpawned any p.trader?.traderKind != null && !p.HostileTo(Faction.OfPlayer); plus map.passingShipManager.passingShips.Count | NO |
| economy | `dump_zone_set` | Zone_Stockpile whose settings.filter allows ThingCategoryDefOf.Corpses, unroofed, outside the walls | NO |
| economy | `colonist_drug_policy_none` | all colonists p.drugs.CurrentPolicy == Current.Game.drugPolicyDatabase default No drugs | NO |
| economy | `defnames_to_verify` | generic count_ keys used: count_tablebutcher, count_drug_lab, count_tablesculpting, count_blocksmarble, count_beer, count_smokeleafjoint, count_psychitetea; research_drugproduction, research_microelectronicsbasics, research_brewing, research_fabrication, resea | NO |
| endgame | `count_aipersonacore` | generic count_ already; verify ThingByKey resolves AIPersonaCore and counts it in storage | yes: Sensors.cs generic count_<def> (only while the def is loaded) |
| endgame | `research_shipreactor (and shipcryptosleep, shipengine, shipcomputercore, shipsensorcluster)` | generic research_<defName>; UNVERIFIED that 1.7 keeps these defNames (DefDatabase<ResearchProjectDef>.GetNamedSilentFail) | yes: Sensors.cs generic research_<def> (only while the def is loaded) |
| endgame | `ship_reactor / ship_engines / ship_caskets / ship_computer_core / ship_sensor_cluster / ship_beams` | map.listerBuildings.allBuildingsColonist grouped by def.defName (Ship_Reactor, Ship_Engine, Ship_CryptosleepCasket, Ship_ComputerCore, Ship_SensorCluster, Ship_Beam) | NO |
| endgame | `ship_launchable` | reactor = first Building_ShipReactor; ShipUtility.LaunchFailReasons(reactor).Any() == false | NO |
| endgame | `ship_launch_fail_reason` | first string of ShipUtility.LaunchFailReasons(reactor) | NO |
| endgame | `reactor_started` | reactor.TryGetComp<CompHibernatable>().State != HibernatableStateDefOf.Hibernating | NO |
| endgame | `caskets_empty` | Building_CryptosleepCasket in ShipUtility.ShipBuildingsAttachedTo(reactor) with !HasAnyContents | NO |
| endgame | `letter_matches` | used by existing rungs but not emitted in Sensors.cs: Find.LetterStack.LettersListForReading.Any(l => l.Label contains value, case-insensitive) | yes: Engine.cs special key (a letter label contains the text) |
| growth | `pawns_unconfigured` | count of map.mapPawns.FreeColonistsSpawned whose thingIDNumber is not in a HashSet<int> the mod fills when automate assign / pawn_priorities runs for that pawn (saved via ExposeData) | NO |
| growth | `prisoners` | map.mapPawns.PrisonersOfColonySpawnedCount | NO |
| growth | `pawns_sharing_bedroom` | FreeColonistsSpawned.Count(p => p.ownership.OwnedRoom != null && p.ownership.OwnedRoom.Role == RoomRoleDefOf.Barracks) | NO |
| growth | `loose_items_outside_storage` | map.listerHaulables.ThingsPotentiallyNeedingHauling().Count | NO |
| growth | `lovers_unmarried` | colonists p with p.relations.GetFirstDirectRelationPawn(PawnRelationDefOf.Lover) != null, halved | NO |
| growth | `colonists_without_armor` | FreeColonistsSpawned.Count(p => p.GetStatValue(StatDefOf.ArmorRating_Sharp) < 0.3f) | NO |
| growth | `best_plants_skill` | FreeColonistsSpawned.Max(p => p.skills.GetSkill(SkillDefOf.Plants).Level) | NO |
| ideology-biotech-anomaly | `unpowered_buildings` | home.listerBuildings.allBuildingsColonist.Count(b => b.TryGetComp<CompPowerTrader>() is CompPowerTrader c && (c.PowerNet == null // !c.PowerNet.HasActivePowerSource)) | NO |
| ideology-biotech-anomaly | `power_islands` | home.powerNetManager.AllNetsListForReading.Count(n => !n.HasActivePowerSource && n.powerComps.Count > 0) | NO |
| ideology-biotech-anomaly | `power_surplus_ratio` | sum of CompPowerPlant.PowerOutput / -sum of negative CompPowerTrader.PowerOutput across home nets | NO |
| ideology-biotech-anomaly | `battery_stored_hours` | sum CompPowerBattery.StoredEnergy / (consumption W / 1000 * hours scale) per net | NO |
| ideology-biotech-anomaly | `generators_roofed` | count CompPowerPlant buildings with a CompRefuelable where b.Position.Roofed(home) | NO |
| ideology-biotech-anomaly | `power_outside_home` | power buildings where !home.areaManager.Home[b.Position] | NO |
| ideology-biotech-anomaly | `ideo_role_leader_filled` | Faction.OfPlayer.ideos.PrimaryIdeo.RolesListForReading.FirstOrDefault(r => r.def.defName == "IdeoRole_Leader")?.ChosenPawnSingle() != null | NO |
| ideology-biotech-anomaly | `ideo_role_moralguide_filled` | same, defName "IdeoRole_Moralist" | NO |
| ideology-biotech-anomaly | `role_ability_ready` | role pawn.abilities.abilities.Any(a => a.CanCast) | NO |
| ideology-biotech-anomaly | `children` | home.mapPawns.FreeColonists.Count(p => p.DevelopmentalStage.Juvenile()) | NO |
| ideology-biotech-anomaly | `adults` | home.mapPawns.FreeColonists.Count(p => p.ageTracker.AgeBiologicalYears >= 18) | NO |
| ideology-biotech-anomaly | `couples_without_double_bed` | adult pairs from LovePartnerRelationUtility.ExistingLovePartner with no shared Building_Bed (SleepingSlotsCount >= 2) in OwnersForReading | NO |
| ideology-biotech-anomaly | `schedule_all_anything` | FreeColonists.All(p => Enumerable.Range(0, 24).All(h => p.timetable.GetAssignment(h) == TimeAssignmentDefOf.Anything)) | NO |
| ideology-biotech-anomaly | `drug_policy_peno` | FreeColonists.All(p => p.drugs.CurrentPolicy[ThingDef.Named("Penoxycyline")].allowScheduled) | NO |
| ideology-biotech-anomaly | `pen_roofed_cells` | for each CompAnimalPenMarker: PenState enclosed cells where home.roofGrid.Roofed(c) | NO |
| ideology-biotech-anomaly | `ritual_obligation_due` | PrimaryIdeo.PreceptsListForReading.OfType<Precept_Ritual>().Any(r => r.activeObligations?.Count > 0) | NO |
| ideology-biotech-anomaly | `growth_moment_pending` | Find.LetterStack.LettersListForReading.OfType<ChoiceLetter_GrowthMoment>().Any() | NO |
| ideology-biotech-anomaly | `mech_bandwidth_free` | mechanitor.mechanitor.TotalBandwidth - mechanitor.mechanitor.UsedBandwidth | NO |
| ideology-biotech-anomaly | `entities_held` | home.listerBuildings.allBuildingsColonist.Count(b => b.TryGetComp<CompEntityHolder>()?.HeldPawn != null) | NO |
| meta | `owner_input_active` | host-side (gates.py), not C#: Win32 GetLastInputInfo delta, minus Unity's own injected input; true while the owner touched mouse/keys in the last OWNER_SETTLE_S s | NO |
| meta | `owner_unread` | host-side: admin-channel messages with id > last replied id (tools.read_owner) | NO |
| meta | `chat_unanswered` | host-side: chat lines from tools.read_chat with no reply_chat yet | NO |
| meta | `new_joiners` | host-side: Twitch JOIN / first-message names not yet greeted this stream | NO |
| meta | `viewer_count` | host-side: Twitch Helix streams.viewer_count | NO |
| meta | `seconds_since_spoken` | host-side: now - timestamp of the last unity-speak.py line | NO |
| meta | `voice_playing` | host-side: true while the current obs-voice wav is still within its duration | NO |
| meta | `seconds_since_webcam` | host-side: now - mtime of the newest unity-cam / snap frame | NO |
| meta | `seconds_since_tool` | host-side: now - last tools.dispatch call | NO |
| meta | `prompt_version_changed` | host-side: hash of prompt.md + playbook.gates.json differs from the previous scan | NO |
| meta | `camera_on_colonist` | CellRect v = Find.CameraDriver.CurrentViewRect; Find.MainTabsRoot.OpenTab == null && Find.CurrentMap.mapPawns.FreeColonistsSpawned.Any(p => v.Contains(p.Position)) | NO |
| meta | `camera_zoom` | Find.CameraDriver.RootSize (small = zoomed in) | NO |
| meta | `forbidden_items` | home.listerThings.AllThings.Count(t => t.def.EverHaulable && t.IsForbidden(Faction.OfPlayer) && home.areaManager.Home[t.Position]) | NO |
| meta | `pawns_flee` | home.mapPawns.FreeColonistsSpawned.Count(p => p.playerSettings != null && p.playerSettings.hostilityResponse == HostilityResponseMode.Flee) | NO |
| meta | `pawns_without_sidearm` | home.mapPawns.FreeColonistsSpawned.Count(p => !p.WorkTagIsDisabled(WorkTags.Violent) && !p.equipment.AllEquipmentListForReading.Any(e => e.def.IsMeleeWeapon) && !p.inventory.innerContainer.Any(t => t.def.IsMeleeWeapon)) | NO |
| research | `hitech_benches` | home.listerBuildings.AllBuildingsColonistOfDef(ThingDefOf.HiTechResearchBench).Count() | NO |
| research | `simple_benches` | home.listerBuildings.AllBuildingsColonistOfDef(ThingDefOf.SimpleResearchBench).Count() | NO |
| research | `multi_analyzers` | home.listerBuildings.AllBuildingsColonistOfDef(DefDatabase<ThingDef>.GetNamedSilentFail("MultiAnalyzer")).Count() | NO |
| research | `research_room_lit` | every bench b: home.glowGrid.GroundGlowAt(b.InteractionCell) >= 0.5f | NO: not a research project (a room/lighting check) |
| research | `research_room_clean` | every bench b: !b.GetRoom().PsychologicallyOutdoors && b.GetRoom().GetStat(RoomStatDefOf.Cleanliness) >= 0 | yes: Sensors.cs generic research_<def> (only while the def is loaded) |
| research | `research_room_temp_ok` | every bench b: b.GetRoom().Temperature in [15,24] | yes: Sensors.cs generic research_<def> (only while the def is loaded) |
| research | `research_only_pawns` | PawnsFinder.AllMaps_FreeColonistsSpawned.Count(p => p.workSettings != null && p.workSettings.GetPriority(WorkTypeDefOf.Research) == 1) | NO: not a research project (no ResearchProjectDef of that name) |
| research | `count_penoxycyline` | generic count_<thingdef> (Sensors.CountKey) -- confirm Penoxycyline is in the counted set | yes: Sensors.cs generic count_<def> (only while the def is loaded) |
| research | `research_benches (fix)` | count any Building_ResearchBench subclass (modded benches) -- currently also d == names; class check should use 'is Building_ResearchBench' | yes: Sensors.cs |
| royalty | `count_loudspeaker` | map.listerThings.ThingsOfDef(DefDatabase<ThingDef>.GetNamedSilentFail("Loudspeaker")) filtered to t.GetRoom()==throne.GetRoom() | yes: Sensors.cs generic count_<def> (only while the def is loaded) |
| royalty | `throne_room_impressiveness` | throne.GetRoom().GetStat(RoomStatDefOf.Impressiveness) | NO |
| royalty | `title_room_ok` | pawn.royalty.MostSeniorTitle.def.throneRoomRequirements.All(r=>r.MetOrDisabled(room,pawn)) | NO |
| royalty | `leader_set` | Faction.OfPlayer.ideos.PrimaryIdeo leader-role precept: ChosenPawnSingle()!=null | NO |
| royalty | `empire_hostile` | Faction.OfEmpire.HostileTo(Faction.OfPlayer) | NO |
| setup | `items_forbidden` | read by gates.py from sensors.json; confirm Sensors.cs writes it: map.listerThings.AllThings.Count(t => t.def.EverHaulable && t.IsForbidden(Faction.OfPlayer)) | NO |
| setup | `debug_menu_open` | Find.WindowStack.Windows.Any(w => w.GetType().Name.StartsWith("Dialog_Debug") // w is EditWindow_Log) (works at the main menu too) | NO |
| setup | `schedule_all_anything` | PawnsFinder.AllMaps_FreeColonists.All(p => p.timetable.times.All(a => a == TimeAssignmentDefOf.Anything)) | NO |
| setup | `drug_policy_set` | all free colonists: p.drugs.CurrentPolicy matches the owner's policy (only Penicillin scheduled every 5 days, take-to-inventory 2) | NO |
| setup | `self_tend_all` | all free colonists: p.playerSettings.selfTend | NO |
| setup | `hostility_attack_all` | all free colonists: p.playerSettings.hostilityResponse == HostilityResponseMode.Attack | NO |
| setup | `food_policy_fine_all` | all free colonists: p.foodRestriction.CurrentFoodPolicy.label contains "Fine" | NO |
| setup | `beds_short` | map.listerBuildings.allBuildingsColonist.OfType<Building_Bed>().Count(b => !b.ForPrisoners && !b.Medical) < map.mapPawns.FreeColonistsCount | NO |
| setup | `campfires` | map.listerBuildings.AllBuildingsColonistOfDef(ThingDefOf.Campfire).Count() | NO |
| setup | `helmet_worn_all` | free colonists: p.apparel.WornApparel.Any(a => a.def.apparel.bodyPartGroups.Contains(BodyPartGroupDefOf.UpperHead) // .Contains(BodyPartGroupDefOf.FullHead)) | NO |
| setup | `ideo_roles_filled` | Faction.OfPlayer.ideos.PrimaryIdeo: leader and moralist precept roles each ChosenPawnSingle() != null | NO |
| setup | `entrance_count` | home-area perimeter cells that are doors or passable and reachable from the map edge (map.reachability.CanReachMapEdge from each) | NO |
| space | `count_orbitaltradebeacon` | covered by generic count_ (buildings counted); verify defName OrbitalTradeBeacon | yes: Sensors.cs generic count_<def> (only while the def is loaded) |
| space | `beacon_uncovered_store_cells` | for every Zone_Stockpile cell and Building_Storage cell on the home map: count cells where !Building_OrbitalTradeBeacon.AllPowered(map).Any(b => b.TradeableCells.Contains(c)) | NO |
| space | `caskets_empty` | map.listerBuildings.AllBuildingsColonistOfClass<Building_CryptosleepCasket>().Count(c => c.def.defName == "Ship_CryptosleepCasket" && !c.HasAnyContents) | NO |
| space | `ship_reactor_started` | map.listerThings.ThingsOfDef(Ship_Reactor def).Any(r => r.TryGetComp<CompHibernatable>()?.State == HibernatableStateDefOf.Starting) | NO |
| space | `trader_ship_in_orbit` | map.passingShipManager.passingShips.Any() | NO |
| space | `visiting_trader` | map.mapPawns.AllPawnsSpawned.Any(p => p.trader?.traderKind != null && !p.HostileTo(Faction.OfPlayer)) | NO |
| start | `pawns_unconfigured` | map.mapPawns.FreeColonistsSpawned.Count(p => p.ownership.OwnedBed == null // p.playerSettings.hostilityResponse != HostilityResponseMode.Attack // p.drugs.CurrentPolicy != NoDrugs) | NO |
| start | `forbidden_items` | map.listerThings.AllThings.Count(t => t.def.EverHaulable && t.IsForbidden(Faction.OfPlayer) && !map.fogGrid.IsFogged(t.Position)) | NO |
| start | `explore_done` | now a .local/qa flag in gates.py; in C#: no Building_Door reachable by a colonist that touches a fogged cell (map.fogGrid.IsFogged) -- move into Sensors.cs | yes: Engine.cs (copied from mark_explore_done) |
| start | `camp_marsh_cells` | map.areaManager.Home.ActiveCells.Count(c => map.terrainGrid.TerrainAt(c) is Marsh/Mud/water (def.IsWater // defName contains Marsh/Mud)) | NO |
| start | `doors_on_corners` | Building_Door count whose cell has wall neighbours on two perpendicular sides and none opposite (a room corner) | NO |
| survival | `unconditioned_rooms` | foreach Room r in map.regionGrid.allRooms where !r.PsychologicallyOutdoors && !r.IsDoorway && r.ProperRoom: count rooms with no CompTempControl building in r.ContainedAndAdjacentThings and no Building_Vent in adjacent walls | NO |
| survival | `freezer_temp` | the room of the stockpile whose filter allows FoodRaw only (or largest food store): room.Temperature | NO |
| survival | `perishables_outside_freezer` | sum over map.listerHaulables/zoneManager stockpiles: things with CompRottable where room.Temperature > 0 and not in the freezer room | NO |
| survival | `coolers_misrotated` | foreach Building_Cooler b: IntVec3 cold = b.Position + IntVec3.South.RotatedBy(b.Rotation); hot = b.Position + IntVec3.North.RotatedBy(b.Rotation); misrotated if hot.GetRoom(map) is enclosed (!PsychologicallyOutdoors) or cold.UsesOutdoorTemperature(map) | NO |
| survival | `unpowered_consumers` | count CompPowerTrader c on map.listerBuildings.allBuildingsColonist where c.PowerNet == null // !c.PowerOn | NO |
| survival | `battery_days_stored` | sum CompPowerBattery.StoredEnergy over nets / (sum of consumers' PowerOutput * -1 * 24 / 1000-equivalent Wd per day) | NO |
| survival | `worst_disease_margin` | foreach colonist hediffs with HediffComp_Immunizable: min(immunity - severity); infection_count = count of hediffs with def.makesSickThought or defName Infection | NO |
| survival | `toxic_buildup_max` | max over colonists of pawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.ToxicBuildup)?.Severity | NO |
| survival | `pawns_unroofed_night` | count colonists not in bed whose Position.Roofed(map) is false while GenLocalDate.HourOfDay in 22..6 | NO |
| survival | `blank_work_cells` | sum over colonists of WorkTypeDefs where !pawn.WorkTypeIsDisabled(w) && pawn.workSettings.GetPriority(w)==0 | NO |
| survival | `hospital_beds_for_prisoners` | count Building_Bed with Medical==true && ForPrisoners==true | NO |
| survival | `kitchen_floored` | room of the first stove: fraction of cells whose TerrainAt has a Cleanliness >= 0 and is a built floor (terrain.layerable/IsFloor) | NO |
| survival | `corpse_age_max_hours` | max over Corpse c in map.listerThings ThingRequestGroup.Corpse of c.Age / 2500 | NO |
| survival | `alert_hunterlacksrangedweapon` | already generic via alert_<class>; verify the class name Alert_HunterLacksRangedWeapon live | yes: Sensors.cs generic alert_<def> (only while the def is loaded) |
| survival | `condition_heatwave / coldsnap / solarflare / eclipse / toxicfallout / volcanicwinter / flashstorm` | already generic condition_<defName lowercased>; verify defNames live | yes: Sensors.cs generic condition_<def> (only while the def is loaded) |
| war | `unarmed_colonists` | free colonists capable of Violent with p.equipment?.Primary == null, or (Simple Sidearms present) no melee in CompSidearmMemory/inventory | NO |
| war | `flee_hostility_count` | colonists where p.playerSettings.hostilityResponse != HostilityResponseMode.Attack | NO |
| war | `embrasure_gaps` | edge cells of rooms that touch an embrasure whose edifice is null / not wall, door or embrasure (Room.BorderCells) | NO |
| war | `unpowered_embrasures` | buildings with defName containing Embrasure and CompPowerTrader where !PowerOn | NO |
| war | `downed_hostiles` | map.mapPawns.AllPawnsSpawned.Count(p => p.Downed && p.HostileTo(Faction.OfPlayer) && p.RaceProps.Humanlike) | NO |
| war | `raid_kind` | auto-classify instead of the hand mark: active Lord jobs (LordJob_Siege=4), raid strategy (ImmediateAttackSappers / ImmediateAttackBreaching=5), PawnsArrivalModeDef CenterDrop=3 / EdgeDrop=2, ManhunterPack mental state=6, Faction.OfMechanoids=7, Hive spawned=8 | NO |
| war | `count_Hive` | generic count_ on ThingDefOf.Hive (verify count_ includes buildings/pawns-spawners) | NO: mixed case, Sensors.cs writes `count_hive` |
| war | `count_TableAutopsy` | generic count_ on the autopsy table def (verify defName in the mod list) | NO: mixed case, Sensors.cs writes `count_tableautopsy` |

---

# TO BUILD

Order of work: (A) fix the rung JSON that can never fire, (B) add the 60 tag rows, (C) add the sensors, (D) add the game_set commands / tools, (E) the window displays. A–B cost nothing; until they land, the rungs listed above sit red (Unresolved) or amber (unmeasured) in the RimPLC window and never fire.

## A. Rung JSON fixes (no code, wrong keys or wrong instruction shape)

### A1. Wrong instruction shape (section 4b)
The engine (`Engine.Expr` / `gates._expr`) needs every instruction object to sit under a **label key**. The rebuild wrote the inner instruction straight into the operand, e.g.

```json
"hunt_ok": {"not": {"ctu": {"designations_hunt": 0}, "preset": 3, "reset": {...}}}
```

`ctu`, `preset` and `reset` are then read as three plain sensor keys (never measured), so the branch never holds. Correct form:

```json
"hunt_ok": {"not": {"hunt_tries": {"ctu": {"designations_hunt": 0}, "preset": 3, "reset": {"days_of_food": ">={FOOD_MIN_DAYS}"}}}}
```

Same fix for every row in 4b: animals-hunt-food, tame-mounts, br-company-supply, econ-freezer-shelves, crops-full-set, ideo-roles, power-generators-outside, space-trade-comms (ton + ctu), space-ally-gifts (ton), space-reactor-hold (ton), start-camp-chop, start-camp-shelter, start-explore-facility, research-idle-fallback (`{"ctu": {"edge": {"ons": {...}}}, "preset": 3, ...}`), econ-trader-arrived and threat-moment (`{"ons": {"any": [...]}}` → `{"ons": {"arrived": {"any": [...]}}}`).

### A2. Sensor key typos (Sensors.cs already measures the right key)
| rung key (wrong) | correct key | rungs |
|---|---|---|
| `condition_HeatWave` | `condition_heatwave` | br-heat |
| `heatstroke` | `alert_heatstroke` | br-heat |
| `low_food` | `alert_low_food` | rung-5c-the-backrooms |
| `low_medicine` | `alert_low_medicine` | br-sustainable |
| `idle` | `alert_idle` | colony-before-research, endgame-greed |
| `colonist_needs_rescue` | `alert_colonist_needs_rescue` | growth-rescue-and-tend |
| `research_AirConditioning` | `research_airconditioning` | coolers-and-vents, freezer-cluster |
| `research_Battery` | `research_batteries` | battery-room |
| `research_GunTurrets` | `research_gunturrets` | turret-line |
| `research_Stonecutting` | `research_stonecutting` | stone-blocks-bench |
| `research_PenoxycylineProduction` / `research_penoxycyline` | `research_penoxycylineproduction` | config-antibiotics, ideo-antibiotics, ideo-research-antibiotics |
| `research_xenogenetics` | verify in DefDatabase (Biotech gene extractor research is most likely `Xenogermination` → `research_xenogermination`) | genes |
| `count_drug_lab` | `count_druglab` | econ-druglab |
| `count_Hive` | `count_hive` | war-infestation |
| `count_TableAutopsy` | `count_tableautopsy` (defName comes from a mod: verify in the loaded defs) | war-organ-harvest |
| `items_forbidden` | `forbidden_items` (one sensor, two names) | setup-0-unforbid |
| `loose_items_off_shelf`, `loose_items_outside_storage` | `loose_items_unstored` (one sensor, three names) | storage-shelves, growth-shelves-everything |
| `research_only_pawns` | `research_only_pawns` is not a research project: rename `researchers_only_research` (sensor C below) — the `research_` prefix makes the generic reader shadow it | research-researcher-balance |
| `research_room_lit` | rename `lab_lit` (sensor C below), same reason | research-lab-room |

### A3. Substring match that does not exist
`letter_labels: "~trader"` (economy, 3 uses): neither Engine.cs nor gates.py knows a `~` operator; a list compared to a string is false. Use the special key `letter_matches: "trader"` (Engine.cs line 262), which is measured.

## B. Tag table rows
Add the 60 UNDEFINED tags of section 6 to `docs/playbook.gates.json` `tags.variables` (value, rule, min, max). Rows with "no proposal" need a value from the owner's walkthrough quotes before the rung can run. Until then each `{TAG}` is Unresolved (red).

## C. Sensors to add to `RimPLC/Source/RimPLC/Sensors.cs`

New method on the **normal** cadence (call it from where `ReadNormal` is called in `RimPLCGameComponent`). Every API is RimWorld 1.6 Assembly-CSharp (1.7 keeps them unless noted UNVERIFIED). Keys that cannot be read are left out, as the file's rule says.

```csharp
// ------------------------------------------------------------------------------------------------ build (rebuilt-ladder inputs)

private static readonly string[] EmbrasureHint = { "Embrasure" };

/// <summary>Inputs the rebuilt ladder reads: crew setup, rooms, power, storage, defence. Normal cadence.</summary>
public static void ReadBuild(Dictionary<string, object> st, Map home, HashSet<int> configuredPawns)
{
    List<Pawn> crew = home.mapPawns.FreeColonistsSpawned;

    // ---- crew
    int armorless = 0, flee = 0, noSidearm = 0, unarmed = 0, sharing = 0, noBedroom = 0, kids = 0, lovers = 0, resOnly = 0, unconfigured = 0;
    int bestPlants = 0;
    foreach (Pawn p in crew)
    {
        bool violent = !p.WorkTagIsDisabled(WorkTags.Violent);
        if (p.GetStatValue(StatDefOf.ArmorRating_Sharp) < 0.3f) armorless++;
        if (p.playerSettings != null && p.playerSettings.hostilityResponse != HostilityResponseMode.Attack) flee++;
        bool meleeCarried = p.equipment.AllEquipmentListForReading.Any(e => e.def.IsMeleeWeapon) ||
                            p.inventory.innerContainer.Any(t => t.def.IsMeleeWeapon);
        if (violent && !meleeCarried) noSidearm++;
        if (violent && p.equipment.Primary == null) unarmed++;
        Room own = p.ownership?.OwnedRoom;
        Building_Bed bed = p.ownership?.OwnedBed;
        if (bed == null || bed.ForPrisoners || own == null) noBedroom++;
        else if (own.Role == RoomRoleDefOf.Barracks) sharing++;
        if (p.DevelopmentalStage.Juvenile()) kids++;
        Pawn partner = LovePartnerRelationUtility.ExistingLovePartner(p);
        if (partner != null && !p.relations.DirectRelationExists(PawnRelationDefOf.Spouse, partner)) lovers++;
        if (p.skills != null) bestPlants = Math.Max(bestPlants, p.skills.GetSkill(SkillDefOf.Plants).Level);
        if (p.workSettings != null && p.workSettings.EverWork && p.workSettings.GetPriority(WorkTypeDefOf.Research) == 1 &&
            DefDatabase<WorkTypeDef>.AllDefsListForReading.Where(w => w != WorkTypeDefOf.Research && !p.WorkTypeIsDisabled(w))
                                                          .All(w => p.workSettings.GetPriority(w) == 0)) resOnly++;
        if (configuredPawns != null && !configuredPawns.Contains(p.thingIDNumber)) unconfigured++;
    }
    st["colonists_without_armor"] = (double)armorless;
    st["flee_hostility_count"] = (double)flee;
    st["pawns_flee"] = (double)flee;                       // same reading, the meta rung's name
    st["pawns_without_sidearm"] = (double)noSidearm;
    st["unarmed_colonists"] = (double)unarmed;
    st["pawns_sharing_bedroom"] = (double)sharing;
    st["colonists_without_bedroom"] = (double)noBedroom;
    st["children"] = (double)kids;
    st["lovers_unmarried"] = (double)(lovers / 2);           // each couple is seen from both sides
    if (crew.Count > 0) st["best_plants_skill"] = (double)bestPlants;
    st["researchers_only_research"] = (double)resOnly;
    if (configuredPawns != null) st["pawns_unconfigured"] = (double)unconfigured;
    st["prisoners"] = (double)home.mapPawns.PrisonersOfColonySpawnedCount;

    // ---- buildings by def (null-safe: a def that is not loaded leaves its key out)
    st["simple_benches"] = (double)CountBuilt(home, "SimpleResearchBench");
    st["hitech_benches"] = (double)CountBuilt(home, "HiTechResearchBench");
    st["multi_analyzers"] = (double)CountBuilt(home, "MultiAnalyzer");
    st["torch_lamps"] = (double)CountBuilt(home, "TorchLamp");
    if (ModsConfig.AnomalyActive)
    {
        // Anomaly: the void monolith is on the map and not yet past its first stage (UNVERIFIED on 1.7: Find.Anomaly.Level)
        bool mono = home.listerThings.ThingsOfDef(ThingDefOf.VoidMonolith).Count > 0;
        st["monolith"] = mono;
        st["monolith_level"] = (double)Find.Anomaly.Level;
    }

    // ---- power
    int unpoweredConsumers = 0, unpoweredBuildings = 0, unpoweredEmbr = 0;
    double produced = 0, consumed = 0;
    foreach (Building b in home.listerBuildings.allBuildingsColonist)
    {
        CompPowerTrader pt = b.TryGetComp<CompPowerTrader>();
        if (pt == null) continue;
        if (pt.PowerOutput > 0) { produced += pt.PowerOutput; continue; }
        consumed += -pt.PowerOutput;
        if (pt.PowerNet == null) unpoweredConsumers++;
        if (pt.PowerNet == null || !pt.PowerNet.HasActivePowerSource || !pt.PowerOn) unpoweredBuildings++;
        if (!pt.PowerOn && b.def.defName.Contains("Embrasure")) unpoweredEmbr++;
    }
    st["unpowered_consumers"] = (double)unpoweredConsumers;
    st["unpowered_buildings"] = (double)unpoweredBuildings;
    st["unpowered_embrasures"] = (double)unpoweredEmbr;
    if (consumed > 0) st["power_margin_pct"] = Math.Round(produced / consumed * 100.0, 0);

    // ---- rooms
    int outOfTemp = 0, unfloored = 0, holes = 0;
    bool labLit = true;
    foreach (Room r in home.regionGrid.AllRooms)
    {
        if (r.PsychologicallyOutdoors || r.IsDoorway || !r.ProperRoom || r.Role == null || r.Role == RoomRoleDefOf.None) continue;
        float t = r.Temperature;
        if (t < 10f || t > 35f) outOfTemp++;
        if (r.OpenRoofCount > 0) holes++;
        foreach (IntVec3 c in r.Cells)
        {
            TerrainDef td = c.GetTerrain(home);
            if (!td.IsFloor || td.natural) unfloored++;        // natural rock floor counts as unfloored until smoothed
        }
    }
    foreach (Building b in home.listerBuildings.allBuildingsColonist.Where(x => x is Building_ResearchBench))
    {
        if (home.glowGrid.GroundGlowAt(b.InteractionCell) < 0.5f) labLit = false;
    }
    st["rooms_out_of_temp"] = (double)outOfTemp;
    st["unfloored_room_cells"] = (double)unfloored;
    st["room_wall_holes"] = (double)holes;
    st["lab_lit"] = labLit;

    // ---- storage / forbidden
    st["loose_items_unstored"] = (double)home.listerHaulables.ThingsPotentiallyNeedingHauling().Count;
    Area homeArea = home.areaManager.Home;
    st["forbidden_items"] = (double)home.listerThings.AllThings.Count(t =>
        t.def.EverHaulable && t.IsForbidden(Faction.OfPlayer) && !home.fogGrid.IsFogged(t.Position) &&
        (homeArea == null || homeArea[t.Position] || t.Position.InHorDistOf(CrewCentre(crew), 30f)));

    // ---- terrain inside the camp
    if (homeArea != null)
    {
        st["camp_water_cells"] = (double)homeArea.ActiveCells.Count(c =>
        {
            TerrainDef td = home.terrainGrid.TerrainAt(c);
            return td.IsWater || td.defName.Contains("Marsh") || td.defName.Contains("Mud");
        });
    }

    // ---- blueprints of walls next to fogged rock (mine first)
    st["blueprints_against_rock"] = (double)home.listerThings.ThingsInGroup(ThingRequestGroup.Blueprint).Count(bp =>
        bp.def.entityDefToBuild is ThingDef ed && IsWallDef(ed) &&
        GenAdj.CardinalDirections.Any(d => { IntVec3 n = bp.Position + d; return n.InBounds(home) && n.GetEdifice(home)?.def.mineable == true; }));

    // ---- perimeter: wall_gaps and embrasure_gaps
    ReadPerimeter(st, home);
}

// no single IsWall flag is relied on: vanilla Wall plus any modded def named *Wall* (smoothed rock walls are not edifices of this kind)
private static bool IsWallDef(ThingDef d) => d != null && (d == ThingDefOf.Wall || d.defName.IndexOf("Wall", StringComparison.OrdinalIgnoreCase) >= 0);

private static int CountBuilt(Map map, string defName)
{
    ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
    return d == null ? 0 : map.listerBuildings.AllBuildingsColonistOfDef(d).Count();
}

private static IntVec3 CrewCentre(List<Pawn> crew)
{
    if (crew.Count == 0) return IntVec3.Invalid;
    return new IntVec3((int)crew.Average(p => p.Position.x), 0, (int)crew.Average(p => p.Position.z));
}

/// <summary>
/// Gaps in the defended ring. The ring is the outer boundary of the Home area: a boundary cell that is passable, holds no
/// door, and can reach the map edge without crossing another wall is a gap. embrasure_gaps counts boundary cells next to an
/// embrasure whose edifice is not a wall, door or embrasure. Costs one reachability query per boundary cell: slow cadence
/// if it shows in the profiler.
/// </summary>
private static void ReadPerimeter(Dictionary<string, object> st, Map home)
{
    Area ha = home.areaManager.Home;
    if (ha == null || ha.TrueCount == 0) return;
    int gaps = 0, embGaps = 0;
    foreach (IntVec3 c in ha.ActiveCells)
    {
        bool edge = GenAdj.CardinalDirections.Any(d => { IntVec3 n = c + d; return !n.InBounds(home) || !ha[n]; });
        if (!edge) continue;
        Building ed = c.GetEdifice(home);
        bool closed = ed != null && (IsWallDef(ed.def) || ed is Building_Door || ed.def.defName.Contains("Embrasure"));
        if (!closed && c.Walkable(home)) gaps++;
        if (!closed && GenAdj.CellsAdjacent8Way(new TargetInfo(c, home)).Any(n =>
                n.InBounds(home) && n.GetEdifice(home)?.def.defName.Contains("Embrasure") == true)) embGaps++;
    }
    st["wall_gaps"] = (double)gaps;
    st["embrasure_gaps"] = (double)embGaps;
}
```

UI / window state (fast cadence, add to `ReadFast`):

```csharp
st["hud_visible"] = !(Find.UIRoot is UIRoot_Play up && up.screenshotMode.Active);
st["window_fullscreen"] = Screen.fullScreenMode == FullScreenMode.ExclusiveFullScreen || Screen.fullScreen;
CellRect view = Find.CameraDriver.CurrentViewRect;
st["camera_on_colonist"] = Find.CurrentMap == home && Find.MainTabsRoot.OpenTab == null &&
                           home.mapPawns.FreeColonistsSpawned.Any(p => view.Contains(p.Position));
```

`pawns_unconfigured` needs a `HashSet<int> configuredPawns` saved on `RimPLCGameComponent` (`Scribe_Collections.Look(ref configuredPawns, "configuredPawns", LookMode.Value)`) and filled by the Inbox handler whenever `assign`, `set_work_priority` or `pawn_priorities` is applied to a pawn (all pawns for `assign`). Without it the key stays out (rung idle) — never a fake 0.

`alert_hunterlacksrangedweapon`: measured only when a rung asks (ReadDemand). Add `{ "hunter_no_gun", "Alert_HunterLacksRangedWeapon" }` to `AlertClasses` if the key should be in the Sensors tab every scan; the key itself stays `alert_hunterlacksrangedweapon` via the demand path.

### C2. Host-side sensors (not C#: gates.py / the autopilot writes them, the RimPLC window never sees them)
| key | where it must be written | rungs |
|---|---|---|
| `owner_input_active` | gates.py: Win32 `GetLastInputInfo` age < `{OWNER_SETTLE_S}` minus Unity's own injected input | owner-at-controls, camera-on-crew |
| `owner_unread` | gates.py: admin-channel messages with id > last replied id (tools.read_owner) | owner-message |
| `chat_unanswered` | gates.py: chat lines from tools.read_chat with no reply_chat | chat-first |
| `chat_asks_mod` | gates.py: an unanswered chat line matches mod/repo/workshop/download | br-chat-mod-links |
| `new_joiners` | gates.py: Twitch first-message names not greeted this stream | viewer-joined |
| `seconds_since_spoken` | gates.py: now − time of the last unity-speak line | dead-air |
| `voice_playing` | gates.py: the current voice wav is still inside its duration | voice-busy, dead-air |
| `seconds_since_webcam` | gates.py: now − mtime of the newest webcam/snap frame | webcam-stale |
| `seconds_since_tool` | gates.py: now − last tools.dispatch call | idle-watchdog |
| `prompt_version_changed` | gates.py: hash of prompt.md + playbook.gates.json differs from the previous scan | updated-spark |

To make them show in the in-game window too, have gates.py write them into the RimPLC inbox (`set_mark`-style `host_<key>`), or accept that the meta family is host-only and say so in the window (E4).

## D. game_set commands / tools to build (deduplicated from every rung step and every family's missing_tools)

Each is a new entry in the tools.py `game_set` enum plus a handler in the Rimrooms command reader (the same path as `rooms` / `beds`), returning a read-back the model can check.

| command | what it must do | rungs waiting on it |
|---|---|---|
| `build` (def, x, z, rot, stuff) | place any architect def as a blueprint with a validity check (`GenConstruct.CanPlaceBlueprintAt`), returning placed/refused per cell; the general fix for "build tool missing" | hitech-bench, research-multi-analyzer, start-naked, power-ac-fridge, bastions, ring repair, campfire, torch, barricades, cooler, battery, landing pad |
| `build_room` / `build_bedroom` (x, z, w, h, stuff) | walls + one door + roof area for a rect | growth-private-rooms, bio-family-rooms, throne/guest/prison rooms |
| `deconstruct` (def or x,z) | designate Deconstruct on matching colony buildings | research-upgrade-sweep, crafting spot replacement |
| `terraform_soil` (x, z, w, h) | Rimrooms terraform designator over water/mud/marsh cells | terraform-water-first, animals-pen-soil |
| `harvest` (defs or food) | designate HarvestPlant on every berry bush / healroot / agave | starving, no-medicine, cold-snap |
| `tame` (def or id) | designate Tame on safe candidates (never NEVER_HUNT) | tame-mounts |
| `slaughter` (def, count) | designate Slaughter, never mounts or milk animals | starving-no-game, animals-autumn-cull |
| `train` (animal, skill) | set training wanted for Obedience / Release / Rescue / Haul | mounts |
| `animal_food` (animal or all, policy) | set food restriction (Kibble + Hay) | animals-kibble |
| `pen` (x, z, w, h) | fence ring + gate + pen marker, no roof | animal-pen, bio-milk-pen |
| `self_tend` (pawn or all, on) | `playerSettings.selfTend` | config, no-medicine, war |
| `hostility` (pawn, attack/flee/ignore) | per pawn (assign only does everyone) | start-new-pawn, war-hostility-attack |
| `schedule` (pawn or all, hours, assignment) | write `timetable.SetAssignment` | config-schedule-anything, setup |
| `drug_policy` (pawn or all, policy) and `edit_drug_policy` (drug, every_days, carry) | assign / edit `DrugPolicy` entries | config-drug-policy, config-antibiotics, ideo-antibiotics |
| `food_policy` (pawn or all, policy) | `foodRestriction.CurrentFoodPolicy` | setup |
| `medical_care` (colonists/prisoners/animals, level) | default medical care | config |
| `bill_count` (bench, recipe, target, mode) | edit an existing bill's target (no duplicate bills) | bills-raise-target |
| `research` (defName) | `Find.ResearchManager.SetCurrentProject` | research rungs, space-ship-research, ideo-research-antibiotics |
| `ideo_role` (role, pawn) | assign Leader / MoralGuide / specialist precept roles | ideo-roles, leader rungs |
| `ritual` (ritual, altar, organiser) | start a ritual / party | ideo-ritual, royalty |
| `growth_choice` (child, trait, passion) | answer a growth moment letter | bio-growth-moment |
| `prisoner_interaction` (pawn, mode) | reduce resistance / recruit / enslave | growth-prisoner-keep |
| `bed_medical` / `bed_prisoner` (x, z, on) | toggle Medical / For prisoners | hospital, prison |
| `bed_price` (x, z, silver) | Hospitality guest bed fee (reflection) | guest-wing, econ-guest-beds-full |
| `hospitality_accept` (on) / `sell_zone` (area) | Hospitality settings (reflection) | config-hospitality-visitors, guest-wing |
| `post_strictness` (strict/default/mild) | Rimrooms post setting | config-post-strictness |
| `door_lock` / `door_policy` (x, z, who, hold_open) | Locks mod / door access | guest-wing, prison, killbox |
| `cooler_temp` (x, z, celsius) | `CompTempControl.TargetTemperature` | freezer, hvac |
| `copy_storage` (from x,z → room/all) | copy one storage's settings to the rest | freezer-sorting, storage-logic |
| `stockpile_filter` new modes `medicine`, `valuables`, `dump`, `drugs` | extra filter presets | hospital, vault, econ-dump-zone, drugs-econ |
| `zone_create` (kind, x1, z1, x2, z2, priority) | stockpile / growing zone by rect with priority | econ-dump-zone, econ-fields-outside |
| `roof_area` (x, z, w, h, roof/noroof) | build-roof / no-roof areas | courtyards, generator yard |
| `firebreak` (width) | PlantsCut ring around Home | firebreak |
| `bury` | grave + bury bill | corpses-buried |
| `conduit_link` | route hidden conduit from unpowered buildings to the main grid (port of .local/qa/conduit-link.py) | power-grid-standing, power-every-consumer |
| `equip` (pawn, thing, sidearm) | job Equip on a named weapon/apparel | animals-hunter-armed, war-arms-*, growth-upgrade-everyone |
| `capture` (pawn) | capture a downed enemy | after-the-kill |
| `force_target` (turret, target) | all-turrets-can-set-forced-target mod | war |
| `call_trader` / `trade_call` (kind) | comms console call by option label | supply-steel-1-buy, supply-weapons-1-sell, trade-run |
| `trade` (buy/sell defName count) | drive the open trade window | econ-trader-arrived, trade-run |
| `company_order` (item, count) / `company_branch` | Rimrooms Company Procurement / found branch | econ-silver-company, br-company-supply |
| `quest_accept` (id, yes/no) | accept/decline a quest letter | econ-quests-cash, empire-quest |
| `designate_gate` (x, z) / `gate_link` (kind, x, z) | Rimrooms gate designate / Machine-pane links | rung-5b-the-gate |
| `abandon_site` (map) | abandon a finished backrooms level | br-close-old-levels |
| `form_caravan` (pawns, food_days, tile) | form + send a caravan | endgame-archonexus, cavalry |
| `load_pods` / `launch_pods` (things, tile) | load + launch transport pods | space-ally-gifts, space-launch-load |
| `enter_casket` (pawn) | order into a cryptosleep casket | endgame-launch |
| `world_tile` (tile) | pick a world tile for a flight/launch | gravship, pods |
| `dismiss_letter` (id) | remove a letter | war |
| `camera_to` (cell or pawn) / camera zoom | frame the action without play_slices | camera-on-crew, threat-moment |
| `save_game` (name), `toggle_hud`, `set_window_mode fullscreen` | config tools | config-hud-restore, config-window-fullscreen |
| `allow_area` (x, z, w, h) | unforbid a rect | unforbid-constant |
| `shelter` material arg; `stockpile_camp` priority arg | extend existing commands | start-camp-shelter, setup |

All 19 game_set commands the rebuilt rungs already drive exist in the tools.py enum (section 5b).

## E. RimPLC window displays to build (MainTabWindow_RimPLC.cs)

1. **Instruction memory**: the Ladder row shows a nested instruction as one box. Add to the tooltip / detail pane the live `ctx.Memory[rungId/label]` (TON/TOF accumulated ticks vs preset in game hours, CTU count vs preset, ONS last state), so a timer or counter can be read without the Log.
2. **Operand contacts**: the detail pane (DrawDetail) lists then/never only. Add one line per leaf inside each instruction (`any` branch, `not`, timer operand) with its own green/dark/amber/red state, so it is visible WHY a nested contact is false.
3. **Unresolved reasons**: `ScanResult.Unresolved` strings (bad instruction shape, missing tag) are collected but not shown; show them in the detail pane in red. Every rung in section 4b and every rung using an UNDEFINED tag would then say what is wrong.
4. **Unmeasured inputs list**: a Sensors-tab section "asked for but not measured" = every leaf key of every rung not in `r.State` (the amber set). Today an unmeasured sensor is only visible as an amber box on its rung; it does not appear in the Sensors tab at all. Mark host-only keys (C2) as "host".
5. **Marks tab defaults**: show every mark any rung reads (with its default from the playbook) even before it is first set; today the Marks tab lists set marks only.
6. **Outputs column**: the detail pane prints steps as text. Flag steps whose tool does not exist (section 5 NO rows, section D) so the owner sees which rungs need a missing command.
7. **Family filter**: 430 rungs in one list; a family dropdown (the `family` field is already on the Rung) next to "Live rungs only".

