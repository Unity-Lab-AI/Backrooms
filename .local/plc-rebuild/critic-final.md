# RimPLC rebuild: final critic (playbook.candidate.json + prompts.candidate.json)

Method: `_scripts/final_critic.py` (mechanical: every `when` key against Sensors.cs + gates.py `derive()` keys + generic prefixes; every `mark_*` read against every `ladder_set mark X` in then/prompts and every latch_name(); 25 owner quotes sampled with seed 13), then the progression walked by hand in priority order (lower number wins the turn; one rung per scan).

## Stall table
| Stage | First stall | Kind |
|---|---|---|
| Crashlanded, 3 pawns | `setup-1-explore` (3.57) / `setup-2b-priorities-after-explore` (3.6): `explore_done` is only set when the bridge reply carries it (gates.py derive); Sensors.cs does not publish it | unmeasured key (soft; stores/shelter/stove chain does not depend on it) |
| Camp | none hard. `setup-8-camp-stable` (latched) needs a 24 h ton on food/stove/bill_rows/75 crop cells, all measured. Silent rungs: `storage-audit` 7.2 (`loose_items_unstored`), `config-window-fullscreen` 1.08 latched on unmeasured `window_fullscreen` | unmeasured (never fire) |
| Mountain base + defences | `econ-checklist` (24.8, not latched, `when` = ton colony_exists 24 h) is TRUE FOREVER from day 2. Rungs below it (16-18 base/fortress) still run; silent: `perimeter-hole` (`wall_gaps`), `mine-before-wall`, `war-fortification-repair`, `power-every-consumer`, `coolers-and-vents`, `walls-halls-roofs` | unmeasured |
| Production / empire | `econ-checklist` 24.8 takes every idle turn: every rung > 24.8 (growth 25.x, animals 37, ideology/biotech 33-34, space 41-42, endgame 43-44, big-plan 45) never gets the turn | priority starvation by a never-latching rung |
| Ship research | `research-ship-tree` (14.6) needs `mark_ending_ship`, set ONLY by `empire-dominion` (43.0) -> starved by econ-checklist | never-set mark (via starvation) |
| Ship built | `endgame-ship-materials` 43.2 / `endgame-ship-build` 43.9: same starvation; ending never chosen | starvation |
| Launch | `endgame-reactor-hold` (44.2, not latched, true for the whole reactor countdown) outranks `endgame-load-caskets` (44.3) -> `mark_caskets_loaded` never set -> `endgame-launch` (44.4) never fires | priority starvation |

Fixes: latch econ-checklist or give it a ctu/ton-reset cycle (or move it to 47.x below endgame); give reactor-hold a lower priority than load-caskets (e.g. 44.35) or gate it on `mark_caskets_loaded: true`; publish `explore_done` from Sensors.cs.

## Other mechanical results
- Rungs with an unmeasured `when` key (never fire): 41. Keys: owner_input_active, seconds_since_tool, owner_unread, hud_visible, window_fullscreen, empire_hostile, chat_unanswered, new_joiners, chat_asks_mod, voice_playing, seconds_since_spoken, seconds_since_webcam, camera_on_colonist, prompt_version_changed, loose_items_unstored, unarmed_colonists, flee_hostility_count, embrasure_gaps, unpowered_embrasures, forbidden_items, lab_lit, researchers_only_research, blueprints_against_rock, wall_gaps, camp_water_cells, unpowered_consumers, power_margin_pct, rooms_out_of_temp, torch_lamps, colonists_without_bedroom, room_wall_holes, unfloored_room_cells, prisoners, best_plants_skill, lovers_unmarried, colonists_without_armor, monolith_level, children. `CAVALRY_ENABLED` (cavalry-check / cavalry-tactics) is used as a key but is not in `tags`.
  The candidate's `sensors` table declares 57 of these but RimPLC Sensors.cs does not measure them yet. Several of them are meta and stream keys (owner-at-controls, dead-air, chat-first) and may be filled in by the autopilot. Check that before treating them as dead.
- Marks read but never set: 0. (Every latched rung's done-mark only gates itself; no other rung reads research_lab_room_done, terraform_water_first_done, bio_child_care_done, cavalry_check_done or config_window_fullscreen_done.)
- Owner quotes: 25 sampled, 0 missing. One compound quote ("your freezer has holes in the walls!! ... / are you writing this all down and maintinaing it") is present as its two halves.
