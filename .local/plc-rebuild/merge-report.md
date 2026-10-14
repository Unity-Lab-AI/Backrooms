# Merge round 1 report

Build: `python .local/plc-rebuild/build.py` then `python .local/plc-rebuild/check.py`.

```
live rungs dropped by family pointers: hostile-on-map, raid-posted, raid-cleanup, ship-launch
tags added 61: PEN_CELLS_PER_ANIMAL, HAY_CELLS_PER_ANIMAL, KIBBLE_FROM_ANIMALS, KIBBLE_TARGET, WINTER_ANIMAL_CAP, PEN_MIN_ANIMALS, GATE_FIRST_WINDOW_MIN, BUILD_RETRY_PRESET, FREEZER_TARGET_C, POWER_MARGIN_MIN_PCT, PILLAR_EVERY, STONE_BLOCK_TARGET, SECURITY_SILVER, EMPIRE_SILVER, ENDGAME_COLONISTS, SHIP_STEEL, SHIP_PLASTEEL, SHIP_URANIUM, SHIP_ADV_COMPS, SHIP_COMPS, SHIP_GOLD, SHIP_PARTS_TARGET, LAUNCH_FOOD_DAYS, LAUNCH_MEDICINE, LAUNCH_TURRETS, LAUNCH_SHOOTERS, REACTOR_HOURS, PERSONA_CORE_WAIT_HOURS, COLONIST_TARGET, BLUEPRINT_BACKLOG, FIELD_CELLS_TOTAL, DEAD_AIR_MAX_S, WEBCAM_MAX_S, CHAT_DECIDE_S, IDLE_WATCHDOG_S, OWNER_SETTLE_S, MAX_LINES_QUEUED, LINE_MAX_WORDS, REPEAT_WINDOW, RUNDOWN_EVERY_S, RESEARCHERS_DEDICATED, LAB_LIGHTS_MIN, BENCH_TRIES, PENOXY_DAYS, PENOXY_STOCK, QUEST_MIN_FIGHT_RATIO, BEACONS_TARGET, ROOM_TARGET_C, COOLER_CELLS, VENT_MAX_PER_UNIT, CLUSTER_CELLS_MAX, MEDICINE_PER_PAWN, WINTER_MEALS_PER_PAWN, TOXIC_PULL_IN, SPREAD_CELLS, SIEGE_WAIT_HOURS, OVERWHELM_RATIO, ASSAULT_DOWN_LIMIT, BASTION_SPACING, BASTION_EMBRASURE_ROW, EQUIP_RETRY; rungs with sidecar fields 210
rungs 378 (family 377, live kept 1), prompts 378, sensors added 57: forbidden_items, unpowered_consumers, unpowered_embrasures, power_margin_pct, embrasure_gaps, unarmed_colonists, pawns_without_sidearm, flee_hostility_count, colonists_without_bedroom, pawns_sharing_bedroom, colonists_without_armor, children, lovers_unmarried, best_plants_skill, researchers_only_research, pawns_unconfigured, prisoners, simple_benches, hitech_benches, multi_analyzers, torch_lamps, monolith, empire_hostile, rooms_out_of_temp, room_wall_holes, unfloored_room_cells, lab_lit, loose_items_unstored, camp_water_cells, blueprints_against_rock, hud_visible, window_fullscreen, camera_on_colonist, owner_input_active, owner_unread, chat_unanswered, chat_asks_mod, new_joiners, seconds_since_spoken, voice_playing, seconds_since_webcam, seconds_since_tool, prompt_version_changed, able_shooters_armed, needs_tend_count, hostile_threat, outdoor_temp, lowest_mood, title_seniority, monolith_level, condition_heatwave, condition_coldsnap, condition_solarflare, condition_toxicfallout, condition_flashstorm, condition_eclipse, condition_volcanicwinter
```

## Fixes applied in families-fixed
- space.json: prompts was a list of [id, prompt] pairs, now an {id: prompt} map.
- endgame.json: 20 rungs had why as a list; joined with ' / ' (quotes unchanged).
- base-and-fortress.json rung-2-power-and-cold and ideology-biotech-anomaly.json ideo-roles: {not: {ctu..., preset, reset}} was malformed; now {not: {<label>_count: {ctu, preset, reset}}}.

## Build rules
- Live rungs that a family names in notes/pointers were deleted into a survivor (hostile-on-map, raid-posted, raid-cleanup, ship-launch); rung-6b-orbit-and-beyond (disabled in live) is kept as is with a prompt made from its own text.
- Rung fields outside rung.schema.json (owner_rules, done_mark, merged_from, moved_from, ...) go untouched into rung-extras.candidate.json.
- Sensors added: decisions.json TO_BUILD/TO_BUILD_HOST keys (status not-measured), monolith_level, Sensors.cs keys missing from the catalogue, and each condition_* key a rung reads.
- Tags added: numeric variables_needed entries missing from the live table; SECURITY_SILVER = 3 * TRADE_SILVER_MIN (formula kept in rule).

## Checker output
```
== 1 rimplc-check: 0
== 2 duplicate ids: 0
== 3 priority ties: 0
== 4 marks read, never set: 0
== 5 unknown when keys: 0
== 6 mixed-case generic keys: 0
== 7 rungs without a prompt: 0
rungs 378, prompts 378, sensors 143, tags 105
CLEAN
```
