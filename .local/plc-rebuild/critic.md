# RimPLC rebuild: completeness critic

Scope: `families/*.json` (430 rungs, 16 families), `inventory.md`, `owner-rules-{a,b,c}.jsonl` (880 rules), `walkthrough-*.md`, checked against `.local/autopilot/gates.py` (latch naming = `latch_name()`, 35-char cut + `_done`; nested instruction shapes per the "Nested instructions" block). Mechanical checks were done by script; the progression walk was done by reading the rungs. Owner quotes below are copied verbatim.

Verdict: **not complete.** The ladder can't be walked from a 3-pawn Crashlanded start to a ship launch without a stall. There are 27 marks that rungs read but no rung ever sets, 64 sensors that rungs use but nothing measures, and 70 owner quotes the families themselves list as unplaced that appear in no rung or prompt. Two separate ship chains build the same ship. Two separate camp chains build the same camp.

## 1. Progression walk: the first rung that stalls at each stage

| Stage | First stall | Why |
|---|---|---|
| Boot -> 3 pawns | `start-new-colony` (3.3) vs `setup-0-new-colony` (3.05) / `new-colony` (0) | `start-new-colony` fires whenever `colony_exists` is false. The other two require `mark_owner_ordered_new_colony`. One family starts colonies on its own; the other says "only on his order". These rules contradict each other. |
| Landing -> camp | `start-crashlanded` (3.4) collides with `setup-2-pawns` (3.4), then two camp chains interleave | `start-camp-stores` 3.47 / `setup-4-stores` 3.54, `start-camp-shelter` 3.48 / `setup-4b-shelter` 3.55, `start-camp-stable` 3.55 / `setup-8-camp-stable` 3.59. Each pair drives the same build twice. `setup-4-stores` also waits on `explore_done` (every door on the map) before the first food store goes down on day 1. |
| Camp -> mountain base | `stone-blocks-bench` (20.8) and `turret-line` (21.5) | Both read mixed-case keys `research_Stonecutting` / `research_GunTurrets`. Sensors.cs writes lowercase keys, so these are never measured and never fire. Without the stonecutter the stone wall never goes up, so `defences_built` never turns true. That blocks `rung-4-production` (needs `defences_built` + `mark_crops_full`), which blocks `mountain-base-plan` and `rung-5-the-mountain-base`. Separately, no base rung reads `mark_camp_stable`. `rung-2-power-and-cold` (20) and `rung-3-defence` (21) can start base work before the camp is stable, which contradicts the setup family's own interlock ("the mountain base family may now dig"). |
| Main base -> empire | `double-bed-rooms`, `prison-wing`, `furniture-tight-and-uniform` | They read `mark_rung_5_the_mountain_base_done`. `rung-5-the-mountain-base` has `latch: false`, so that mark is never set and the rest of the base layout never builds. `bio-family-rooms` reads `mark_main_base_started`, which is also never set. |
| Empire -> ship | `space-ship-research` (24.5, latched) | The latch writes `space_ship_research_done` after the first pass. The step that sets `mark_research_ship_basics` ("when ... all true") only runs inside that first pass, so it is never re-checked. `space-persona-core` has the same bug for `mark_persona_core_held`: its `when` needs `count_aipersonacore <1`, so the step "when >= 1 set persona_core_held" can never be true. `ship-launch` (64) needs both marks, so it never fires. |
| Launch | `endgame-*` (95-96) duplicates `space-*` (24-65) | Two chains each set `mark_ship_built` and each launch: `space-launch-load` launches directly; `endgame-launch` needs `mark_caskets_loaded`. The endgame chain can't start until `empire-dominion` sets `mark_ending_ship`. One of its `ready` branches is `ship_research_done`, which the space chain has to finish first. |

## 2. Marks read but never set (27). The rung never fires.

`start_in_backrooms`, `coordinate_held`, `rung_5_the_mountain_base_done`, `main_base_started`, `family_rooms_built`, `milk_pen_built`, `child_care_ready`, `ending_gravship`, `ending_royal`, `ending_archonexus` (`empire-dominion` only says "or ..." in prose), `colony_policy_set`, `ideo_roles_refused`, `peno_policy_set`, `ideo_altar_built`, `ideo_party_room`, `generator_cancelled`, `dissection_bill_set`, `monolith_advanced`, `stream_titled`, `plan_needed`, `survival_basics_done`, `empire_hostile`, `mountain_base_site`, `arms_tried`, `pawns_tried`, `research_gunsmithing`, `research_transport_pod`.

The last two are research keys written as marks. They should be the sensors `research_gunsmithing` / `research_transportpod`. The `*_tried` marks feed CTU fallbacks that therefore never count.

## 3. Unmeasured inputs (inventory section 1: 64 keys)

Keys that block the main progression:
- Case typos: `research_Stonecutting`, `research_GunTurrets`, `research_Battery`, `research_AirConditioning`, `research_PenoxycylineProduction`, `count_Hive`, `count_TableAutopsy`, `condition_HeatWave`.
- Wrong names: `low_food` (measured as `alert_low_food`), `colonist_needs_rescue` (measured as `alert_colonist_needs_rescue`).
- Measured nowhere: `idle`, `forbidden_items` / `items_forbidden` (two names for one thing), `unpowered_consumers`, `wall_gaps`, `pawns_unconfigured`, `colonists_without_bedroom`, `unarmed_colonists`, `low_medicine`.
- `br-sustainable` reads `low_medicine`, so `mark_colony_sustainable` is never set and the whole gate chain (`rung-5b-the-gate`) is dead.
- Inconsistent types: `hostiles_on_map` is compared as `"0"` (string), `0` and `false` in different rungs.

## 4. Priority collisions and duplicates

- Duplicate id `power-every-consumer`: base-and-fortress (22.0) and survival (6.6). `gates.py` keeps one silently.
- 40+ shared priorities. The ones that matter: 3.4 (`start-crashlanded` / `setup-2-pawns`), 3.5 (`setup-1-explore`, `start-camp-food`, `work-grid-set`, `threat-moment`, `br-out-of-the-backrooms`), 2.0 (`hostile-on-map` / `chat-first`: a combat rung tied with chat), 2.3 (`raid-posted` / `life-threat`), 4.3 (`cold` / `animals-danger-clear`). Ties leave the order undefined.
- `endgame-ship-build` (95.6) and `ship-launch` (64) both place the ship. `endgame-ship-site` and `ship-launch` choose different sites ("inside/adjacent to the fortified mountain base" vs a site mark).

## 5. Inventory section 4b is itself wrong

It reports 40 "broken" CTU/TON entries (`{"ctu": when, "preset": N, "reset": when}`). That is exactly the legal shape in `gates.py` (`expr_op` sees one instruction; `preset`/`reset`/`hours` are operands). Those rungs are fine. The audit is a false alarm, and acting on it would break working rungs.

## 6. Owner rules placed nowhere (70 the families list as unplaced, absent from every rung and prompt)

Representative quotes, verbatim:
- "TALK TO THE VIEWEREWS YOU ARE FUCKING IGNORING THEM / its quiet becasue you arent entrertaining enough"
- "comeone told me it too quiet too much dead air"
- "you need to be testing all three scenerios trying to get a gate built in all three"
- "dont forget terriforming for soil plots"
- "you need to put horse shoes up against wide wall so action area isnt clicked need at minimum one action area unblocked"
- "nmake that sotrage room a prison hold toss in a spot and put the storage where the table and chairs are might have to move benches, compelte evertthing ive sdaid"
- "u need to move those two cooler on the morgue freezer to east side of that narro room so they ppush outside correctly"
- "not peace full you cheap skat community buiilder go back"
- "you are dsoing test items right you keep getting lost in the game play, set fucking goals foo"
- "set base goals first; halls 3 wide, never 1; ..." / "adult couples get private double-bed rooms; milk, cribs and toys before births; raise soldiers (combat traits)". Both are filed under war and never placed in base/growth.

Some quotes are not even in an `unplaced_rules` list (they are missing from both the rungs and the unplaced lists):
- "talk come on NEVER FUCKING IGNORE CHAT TELL THEM IF U HAVE TO PROCESS SOMETHING GIVE TO BARE WITH YOU"
- "something is wrong u are clicking a million times in a row and it looked weird on steeam / sounds spammy, warn viewers for shit before like that"
- "ur dry storage needs more shleves / add another shelfe N side of existing ones directly / and missing ones"
- "and you need make a straight wall north of edge wall of the alter room"
- "start growing cash crops / what can u doi to make the next visitors happier with their stay beauty better food sales of goods have to set a sell zone"

The endgame family states that no owner rule carries family `endgame`. 409 of 430 rungs have an empty `owner_rules` field, so owner-rule traceability exists only in the `why` prose.

## 7. Walkthrough essentials with no rung

- Blight: 0 rungs. The walkthrough says "cut blighted plants at once".
- Surgery / operating room light 50% / bionics / prosthetics: 0 rungs.
- Mental breaks and psychic drone: none of the 2 mentions is a rung with a sensor.
- Sapper/breacher interior fallback ring: mentioned, but no rung reads a breach.
- Nutrient paste: 1 mention, no rung.
- Walkthrough meta lines 67-73 (draft within 1 tick, day>=3 stone walls / day>=5 killbox, 2 mini-turrets at GunTurrets+steel>=140+components>=3, unused mountain room above -17C -> light/freezer for infestations, rescue/tend within a day, attack sieges before mortars, manhunters -> indoors) are listed as unplaced in meta and are not in the target families.

## 8. Meta prompts

- Every rung has a prompt (430/430). 60 are under 90 characters, and many of those are only `UNVERIFIED: ...` notes (`animal-pen`, `train-mounts`, `cavalry-check`, ...). They tell the model nothing to do.
- Some prompts contradict their rung:
  - `rung-5-the-mountain-base`: the prompt says "Done = mark mountain_base_done" while its `latch: false` leaves the dependants' `rung_5_..._done` unset.
  - `space-persona-core` / `space-ship-research`: the "Done:" lines in the prompts can't run under the latch.
  - `start-camp-stable` plans "the mountain base, re-sited around the started entrance near the north-most farms" while the setup family says the camp is "a staging camp, not a colony".
- 28 rungs drive a `MISSING TOOL` (research_queue, pod_load_and_launch, enter_casket, designate_gate, barricades ...). They depend on screenshot fallbacks the 9B model handles badly.
