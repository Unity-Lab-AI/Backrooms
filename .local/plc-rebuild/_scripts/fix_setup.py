import json, re, copy, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = json.load(open(os.path.join(B, "families", "setup.json"), encoding="utf-8"))
R = {r["id"]: copy.deepcopy(r) for r in src["rungs"]}
P = dict(src["prompts"])
def latch_name(rid): return re.sub(r"[^a-z0-9]+", "_", str(rid).lower()).strip("_")[:35] + "_done"
Q = lambda s: 'owner: "%s"' % s

q_stores = "you need to set stockpile and get everyone hueling stuff out without exahusting them letting them relax and starting up you facitly small first massive later get ur needs food security and shit settled / you should have a maintaince list of thinge proprigating what all you need to do / make sure u arm up and set everyones setting attack, heal self, schedule, priorities, drugs to no drugs, all of it pause and do it and set control shift carry but becasre full sending them on 50 runs without a break"
q_terra = "use teriform to remove mud and shit like water inside camp perimeter"
q_terra2 = "dont forget terriforming for soil plots"
q_shelves = "ur dry storage needs more shleves / add another shelfe N side of existing ones directly / and missing ones"
q_spam = "something is wrong u are clicking a million times in a row and it looked weird on steeam / sounds spammy, warn viewers for shit before like that"
q_click = "some time u click twice it selects all firelds be werry"
q_three = "three peopel are there its selecting them but no pawn options apear like draft major bug the model cant haddle"
q_wood = "make it of wood just exterior make 3wide terrriom stone smooth marble for fire break"
q_water = "all those walls over top of water need to be cancled and use terraform to change it to dirt first"
q_doorsw = "hold some places you put walls where doors are to be opn outer wall"
q_rev = "tell reve its one the list Rev character(ask if any requests when u get to making him, as an extra hand will be helpopfull just have to always set up everything for new pawns"
q_prio = "stop ur fucking up the priorities i told you how to set them"
q_prio2 = "set up all priorities this is the last time i telling you set it how ive told you every day weve played all of them for every one using coopy paste ..."
q_ops1 = "and your operations manual script or .md obviousliy isnt good becasue it doesnt have everything ive fucking ever told you as you arent even reading messages and clearing them"
q_ops2 = "make sure u maintain everything in totality ive ever tyold you about the game play in totality has to ber maintained not a one and done"
q_ops3 = "you are suppose tho be checking off todo items of the tests stuff while playing the full game to do so"
q_ops4 = "how are we gonna do the fucking tests if u dont play the game?"
q_nowood = "there is no wood no trees on this map, thats why in advanced setting on world gen setup you set 300x300 mapo and spring, and then when choosing a map tile u pic on that has mountains(the rock areas on map) in forest area and jungle areas the light green and green, terrain tab on left tells u all this when u highlight via select the tiles"
q_camp = "camp fridege all of it workshop every thing u need in the camp tight and no blocked paths"
q_unforbid = "and a big issue its it never auto unforbid all the starting materials and never copped wood to build starting structures rooms"
def addwhy(r, *qs):
    for q in qs:
        if ('"%s"' % q) not in r["why"]:
            r["why"] += " / " + Q(q)

r = R["setup-0-pause-on-land"]
r["then"].append("pawns selected but no pawn options/draft show: game_close_window, then select ONE pawn (click once) and read game_get_ui_layout")
addwhy(r, q_three)

r = R["setup-0-starting-goods"]
r["then"][0] = "read count_mealsurvivalpack (survival meals) and meals: the scenario must start with about 100 survival meals plus the Prepare Carefully items"

r = R["arms-out-first"]; r["latch"] = False
r["when"] = {"colony_exists": True, "mark_start_opening_done": True, "mark_arms_set": False}
r["then"] = ["empire_pass",
             "empire_pass refused, or its ARMS line still shows someone unarmed: ladder_set mark arms_tried true, then ladder_set mark arms_tried false (each refusal counts once; 2 -> arms-out-fallback)",
             "read its ARMS line: nobody unarmed (able_shooters_armed == able_shooters); a gun as primary, the melee weapon/pain baton as sidearm, helmet on, skip flak vest/pants early",
             "game_set cmd assign hostility Attack",
             "loose_weapons 0 and everyone armed: ladder_set mark arms_set true"]
R["arms-out-fallback"]["then"] = [
    "empire_pass refused twice: for each loose weapon order_pawn pawn_id <unarmed pawn> x z of the weapon option 'Equip'",
    "an Equip order refused: ladder_set mark arms_tried true, then ladder_set mark arms_tried false, and order the next pawn",
    "then ladder_set mark arms_set true"]

r = R["setup-2-pawns"]; r["latch"] = False
r["then"].insert(2, "pawn_priorities refused: ladder_set mark pawns_tried true, then ladder_set mark pawns_tried false (3 refusals -> setup-2-pawns-fallback)")
addwhy(r, q_prio2, q_prio)
R["setup-2-pawns-fallback"]["then"].insert(1, "a set_work_priority refused: ladder_set mark pawns_tried true, then ladder_set mark pawns_tried false; read the reason, next cell")

r = R["setup-3-assign"]
r["then"][2] = "schedule: Anything at all hours for every pawn, sleep and recreation kept (no 50 carry runs without a break) [missing tool: game_set cmd schedule -> game_open_main_tab Schedule, game_get_ui_layout, click once each]"
r["then"][3] = "drug policy: No drugs for colonists except Penicillin every 5 days, carry 2 [missing tool: game_set cmd drug_policy -> game_open_main_tab Assign, game_get_ui_layout, click once each]"
addwhy(r, q_stores)

r = R["leader-moral-guide"]
r["when"] = {"colony_exists": True, "mark_assign_set": True, "mark_ideo_roles_set": False}
r["then"].insert(1, "a click selected everything (all fields/pawns): game_close_window and read game_get_ui_layout again -- exactly one thing selected before acting")
addwhy(r, q_click)

r = R["setup-1-explore"]; r["latch"] = False
r["then"][3] = "explore answers 'nothing left' -> ladder_set mark explore_done true (explore_done mirrors it); this rung clears"
R["setup-1-explore-fallback"]["then"][1] = "Crashlanded open ground: no rooms exist -- ladder_set mark explore_done true and go on to stores"

r = R["setup-chop"]
r["when"] = {"colony_exists": True, "mark_assign_set": True, "wood": "<{WOOD_RESERVE}", "designations_cut": "<20"}
r["then"] = ["game_set cmd chop count 300 (nearest trees to the crew; trees on the site first); unpause so it is cut",
             "chop refused or 0 trees: game_set cmd explore for trees beyond reach, then game_get_cells_info on the wooded cells and game_apply_architect_designator Chop wood once",
             "no trees on the whole map: reply_owner with the chop reply (the tile was picked wrong); never loop"]
addwhy(r, q_nowood)

r = R["setup-4-stores"]; r["latch"] = False
r["when"] = {"colony_exists": True, "mark_assign_set": True, "food_store": False}
r["then"][4] = "a refused try: ladder_set mark store_tried true, then ladder_set mark store_tried false (each refusal counts once; 2 -> setup-4-stores-fallback)"
r["then"].append("haul in short batches; the schedule keeps sleep and recreation -- never 50 carry runs without a break [missing tool: haul limit / rest setting]")
old = Q("you need to set stockpile and get everyone hueling stuff out without exahusting them / set control shift carry but becasre full sending them on 50 runs without a break")
assert old in r["why"]
r["why"] = r["why"].replace(old, Q(q_stores))
r["never"].append("haul everything across the map -- settle near the landing spot")

r = R["setup-4b-shelter"]; r["latch"] = False
r["then"] = ["game_set cmd shelter w 7 h 7 (wood room + door + roof beside the crew; 9x9 if wood allows); doors mid-side or near a corner, never the corner cell",
             "shelter refused: ladder_set mark shelter_tried true, then ladder_set mark shelter_tried false; next try w 6 h 8 (2 refusals -> setup-4b-shelter-fallback)",
             "game_set cmd beds (one per colonist), then game_set cmd shelves -- enough shelves for the dry store, more directly on the N side of the existing ones",
             "fridge (roofed food store), workshop (crafting spot / butcher), 1x2 table + stool, torch lamp, a campfire in the middle -- all inside or touching the camp (game_apply_architect_designator Campfire / TorchLamp) [missing tool: game_set cmd campfire/torch]",
             "store everything under a roof except steel and stone blocks",
             "mud/marsh/water inside the camp perimeter -> soil before building on it [missing tool: game_set cmd terraform -> game_apply_architect_designator terrain designator, once per drag]",
             "unpause to build; when beds >= colonists and store_roofed_fraction >= 0.75: ladder_set mark shelter_set true"]
r["never"] += ["a massive camp", "grow the camp beyond what three pawns need"]
addwhy(r, q_terra, q_shelves)
R["setup-4b-shelter-fallback"] = {
    "id": "setup-4b-shelter-fallback", "family": "setup", "latch": False,
    "when": {"colony_exists": True, "food_store": True, "mark_shelter_set": False,
             "shelter_tries": {"ctu": {"mark_shelter_tried": True}, "preset": 2, "reset": {"mark_shelter_set": True}}},
    "then": ["shelter tool refused twice: game_list_architect_designators Structure, then game_apply_architect_designator wood Wall as a 7x7 ring by the crew, one Door mid-side, roof over it",
             "a designator refused: ladder_set mark shelter_tried true, then ladder_set mark shelter_tried false; reply_owner with the refusal text",
             "room closed and roofed, beds >= colonists: ladder_set mark shelter_set true"],
    "never": ["a door on the extreme corner cell", "a third try on the same cells"],
    "why": Q("you retarn u put doors the the extreem corners thats not gonna work") + " / " + Q(q_camp)}

r = R["setup-5-stove"]; r["latch"] = False
r["then"][2] = "stoves >= 1 and the bill is placed: ladder_set mark stove_set true"

r = R["setup-6-run"]
r["when"] = {"colony_exists": True, "mark_stove_set": True, "ticks_moving": False, "hostiles_on_map": 0}
r["then"] += ["letters first: read every letter (game_state), act, dismiss",
              "run_list -- the propagating maintenance list; the first FIX is the goal; check off test TODO items while playing (note append)"]
addwhy(r, q_ops1, q_ops2, q_ops3, q_ops4)

r = R["setup-6b-crops"]
r["when"] = {"colony_exists": True, "mark_stove_set": True, "growing_cells": "<75"}
r["then"].insert(0, "sand/gravel/rock under a planned field: terraform it to soil first [missing tool: game_set cmd terraform -> game_apply_architect_designator terrain designator]")
r["never"].append("plant on sand/gravel/rock without terraforming to soil")
addwhy(r, q_terra2)

r = R["setup-7-camp-defence"]; r["latch"] = False
r["then"] = ["unity_say a clean line first: what the build is and that it takes a minute (bulk jobs are announced, never silent; paced, not a million clicks)",
             "the STARTING CAMP comes before the main base: one entrance in use, everything else closed",
             "wood wall ring round the camp (game_select_architect_designator Wall wood, ONE game_drag_cell per side); only the EXTERIOR is wood; doors in every other gap (corners and mid-side)",
             "water under the line: terraform it to dirt first [missing tool: game_set cmd terraform]",
             "wood barricades (or sandbags) either side of that entrance, inside, staggered (game_apply_architect_designator Barricade)  [missing tool: game_set cmd barricades]",
             "game_set cmd set_area area Home over the whole ring so pawns stay inside",
             "a fallback point behind the barricades where all three gather when drafted",
             "everyone armed: rifle primary, melee sidearm (empire_pass if anyone is not)",
             "a mini-turret covering the entrance once steel and components allow",
             "a drag or designator refused: ladder_set mark camp_wall_tried true, then ladder_set mark camp_wall_tried false (3 -> setup-7-camp-defence-fallback)",
             "when defences_built >= 2: ladder_set mark camp_defence true; the full embrasure wall and killbox are rung-3-defence, after power"]
r["never"] += ["wall over water (terraform first)", "a wall cell where a door is meant to be"]
addwhy(r, q_wood, q_water, q_doorsw, q_spam)
R["setup-7-camp-defence-fallback"] = {
    "id": "setup-7-camp-defence-fallback", "family": "setup", "latch": False,
    "when": {"colony_exists": True, "mark_stove_set": True, "mark_camp_defence": False,
             "build_tries": {"ctu": {"mark_camp_wall_tried": True}, "preset": 3, "reset": {"mark_camp_defence": True}}},
    "then": ["the wall ring was refused three times: game_set cmd shelter (a small closed wood room the crew can fight from)",
             "wood barricades on the threat side, shooters behind them; a refusal: ladder_set mark camp_wall_tried true, then ladder_set mark camp_wall_tried false",
             "ladder_set mark camp_defence true"],
    "never": ["a third try on the same cells"],
    "why": Q(q_wood)}

R["setup-8-camp-stable"]["when"] = {
    "colony_exists": True, "mark_camp_defence": True, "mark_camp_stable": False,
    "stable_held": {"ton": {"days_of_food": ">={FOOD_COMFORT_DAYS}", "stoves": ">=1", "bill_rows": ">0",
                            "mark_shelter_set": True, "growing_cells": ">=75"}, "hours": 24}}
addwhy(R["setup-8-camp-stable"], "and try to get to where everything is stable and food supply is handled production  so that things can settle down and u can start mining out the base, but lots before then")

r = R["setup-9-new-pawn"]
r["when"] = {"colony_exists": True, "mark_assign_set": True, "new_pawn": {"ons": {"grid_matches_plan": False}}}
r["then"] = ["a new colonist (or a drifted grid): game_state -> the pawn with a default grid / no area, and their best skills",
             "pawn_priorities for that pawn (one call per pawn, the same plan as everyone, passion cells changed only); read it back with pawn_check Work tab; a wrong cell: game_set cmd set_work_priority pawn work level, one cell, read back",
             "game_set cmd assign pawn <name> (food Fine, medicine Best, hostility Attack)",
             "empire_pass: gun primary, melee sidearm, self-tend on; read its ARMS line",
             "game_set cmd beds if none free, then game_set cmd set_bed_owner x z owner <name>; game_set cmd set_area pawn <name> area Home",
             "a new pawn made at the start (e.g. Rev): ask chat once for requests, then set everything up the same day"]
r["never"] = ["leave a new pawn without priorities or a bed", "batch-click priorities across pawns", "leave a new colonist unarmed"]
addwhy(r, q_rev, q_prio, q_prio2)

order = ["setup-0-pause-on-land", "setup-0-starting-goods", "arms-out-fallback", "arms-out-first",
         "setup-2-pawns-fallback", "setup-2-pawns", "setup-3-assign", "leader-moral-guide",
         "setup-1-explore-fallback", "setup-1-explore", "setup-2b-priorities-after-explore", "setup-chop",
         "setup-4-stores-fallback", "setup-4-stores", "setup-4b-shelter-fallback", "setup-4b-shelter",
         "setup-5-stove", "setup-6-run", "setup-6b-crops", "setup-7-camp-defence-fallback",
         "setup-7-camp-defence", "setup-8-camp-stable", "setup-9-new-pawn"]
rungs = []
for i, rid in enumerate(order):
    g = R[rid]
    o = {"id": rid, "priority": round(3.30 + 0.03 * i, 2), "family": "setup", "latch": bool(g.get("latch")),
         "when": g["when"], "then": g["then"], "never": g.get("never", []), "why": g["why"]}
    if o["latch"]:
        o["done_mark"] = latch_name(rid)
    o["owner_rules"] = re.findall(r'owner: "(.*?)"(?= / owner:|\s*--|\s*$)', g["why"])
    rungs.append(o)

def lk(k, v): P[k] = P[k].replace(*v) if isinstance(v, tuple) else v
P.pop("setup-0-new-colony"); P.pop("setup-0-unforbid")
P["setup-0-pause-on-land"] = P["setup-0-pause-on-land"].replace("No other order first.", "Pawns selected but no options/draft: game_close_window, click ONE pawn once.\nNo other order first.")
P["setup-0-starting-goods"] = P["setup-0-starting-goods"].replace("count_MealSurvivalPack", "count_mealsurvivalpack").replace("{START_SURVIVAL_MEALS}", "100").replace(
    "Done: ladder_set mark start_goods_checked true.", "Done: ladder_set mark start_goods_checked true (latch writes %s)." % latch_name("setup-0-starting-goods"))
P["arms-out-first"] = P["arms-out-first"].replace("Refused: ladder_set mark arms_tried true", "Refused: ladder_set mark arms_tried true then false")
P["arms-out-fallback"] += "\nAn Equip refused: ladder_set mark arms_tried true then false; next pawn."
P["setup-2-pawns"] = P["setup-2-pawns"].replace("Refused: ladder_set mark pawns_tried true", "Refused: ladder_set mark pawns_tried true then false")
P["setup-2-pawns-fallback"] = ("pawn_priorities refused 3 times. game_set cmd set_work_priority pawn work level for each missing cell, read each back.\n"
    "A cell refused: ladder_set mark pawns_tried true then false.\nCheck grid_matches_plan, then ladder_set mark pawns_set true.\n"
    "Owner: \"she is bnot to skip priorities that is what she must to after exploring wtf am i talking to a wall all week\"")
P["setup-3-assign"] = P["setup-3-assign"].replace("Done: ladder_set mark assign_set true",
    "Keep sleep and recreation: never 50 carry runs without a break.\nDone: ladder_set mark assign_set true (latch writes %s)" % latch_name("setup-3-assign"))
P["leader-moral-guide"] = P["leader-moral-guide"].replace("Done: ladder_set mark ideo_roles_set true.",
    "Done: ladder_set mark ideo_roles_set true (latch writes %s)." % latch_name("leader-moral-guide")) + " / \"%s\"" % q_click
P["setup-1-explore"] = P["setup-1-explore"].replace("Done: explore_done true (the rung clears).", "Done: 'nothing left' -> ladder_set mark explore_done true (the rung clears).")
P["setup-1-explore-fallback"] = P["setup-1-explore-fallback"].replace("ladder_set mark explore_skipped true", "ladder_set mark explore_done true")
P["setup-chop"] = ("wood below {WOOD_RESERVE}: game_set cmd chop count 300. One call; trees on the site first; unpause.\n"
    "Refused / 0 trees: game_set cmd explore, game_get_cells_info, game_apply_architect_designator Chop wood once.\n"
    "No trees on the map: reply_owner, never loop. PlantCutting on one or two pawns, not all.\n"
    "Done: designations_cut >= 20 (rung clears).\nOwner: \"set your priorities, dont need everyone choopping wood, multitask\" / \"%s\"" % q_unforbid)
P["setup-4-stores"] = P["setup-4-stores"].replace("A refusal: ladder_set mark store_tried true, never retry that spot.",
    "A refusal: ladder_set mark store_tried true then false, never retry that spot (2 -> fallback).\nHaul in short batches; let them rest -- no 50 runs without a break.").replace(
    "Done: food_store true (latched).", "Done: food_store true.") + " / \"you need to set stockpile and get everyone hueling stuff out without exahusting them letting them relax\""
P["setup-4b-shelter"] = ("game_set cmd shelter w 7 h 7 (9x9 if wood allows), then game_set cmd beds, game_set cmd shelves (enough for dry storage).\n"
    "Doors mid-side or near a corner -- never the corner cell. 2-wide walkways. Fridge, workshop, table+stool, campfire, torch lamp inside.\n"
    "Mud/water inside the perimeter: terraform to soil first (no terraform tool: game_apply_architect_designator once per drag).\n"
    "Refused: ladder_set mark shelter_tried true then false; next w 6 h 8 (2 -> setup-4b-shelter-fallback).\n"
    "Done: beds >= colonists, roofed >= 0.75: ladder_set mark shelter_set true.\n"
    "Owner: \"%s\" / \"%s\" / \"ur dry storage needs more shleves\"" % (q_camp, q_terra))
P["setup-4b-shelter-fallback"] = ("Shelter tool refused twice.\nTools: game_list_architect_designators Structure -> game_apply_architect_designator wood Wall, 7x7 ring by the crew, Door mid-side, roof.\n"
    "Refused: ladder_set mark shelter_tried true then false; reply_owner with the refusal text.\nNever the corner cell for a door.\n"
    "Done: roofed, beds >= colonists -> ladder_set mark shelter_set true.\nOwner: \"you retarn u put doors the the extreem corners thats not gonna work\"")
P["setup-5-stove"] = P["setup-5-stove"].replace("Done: ladder_set mark stove_set true.", "Done: stoves >= 1 and the bill placed: ladder_set mark stove_set true.")
P["setup-6-run"] = ("Setup is in place and time is stopped. game_pause_game pause false. pawn_priorities custom Research 3.\n"
    "Every turn after: letters first (read, act, dismiss), then run_list; the first FIX is the goal; check off test TODO items while playing.\n"
    "Done: ticks_moving true.\nOwner: \"okay is it ever going to play the game?(set up cololnist, zones, and shit)\" / \"%s\"" % q_ops2)
P["setup-6b-crops"] = ("growing_cells below 75: sand/gravel/rock under a field -> terraform to soil first.\ngame_set cmd crops plant Plant_Rice near camp.\n"
    "fields_all_default_crop true: set_zone_plant other fields to Plant_Potato / strawberry / healroot.\n"
    "Then game_set cmd hunt (never boomrats, boomalopes, predators). Done: growing_cells >= 75.\n"
    "Owner: \"you are going nothing but potatoes everywhere wtf!\" / \"%s\"" % q_terra2)
P["setup-7-camp-defence"] = ("Say it first on stream (clean): what you build, that it takes a minute -- no silent click spam.\n"
    "One entrance in use. Wood wall ring, ONE game_drag_cell per side, doors in the other gaps; water under it: terraform first.\n"
    "Barricades either side inside, staggered (game_apply_architect_designator Barricade); Home area over the ring; fallback point; everyone armed.\n"
    "Refused: ladder_set mark camp_wall_tried true then false (3 -> setup-7-camp-defence-fallback).\n"
    "Done: defences_built >= 2, ladder_set mark camp_defence true.\n"
    "Owner: \"%s\" / \"sounds spammy, warn viewers for shit before like that\"" % q_wood)
P["setup-7-camp-defence-fallback"] = ("The wall ring was refused three times.\nSequence: game_set cmd shelter -> wood barricades on the threat side, shooters behind -> ladder_set mark camp_defence true.\n"
    "Refused: ladder_set mark camp_wall_tried true then false.\nThe stone wall comes with rung-3-defence.\nOwner: \"%s\"" % q_wood)
P["setup-8-camp-stable"] = ("Food days >= {FOOD_COMFORT_DAYS}, a stove with a bill, shelter and 75 crop cells have held 24 hours. Stop growing the camp: a staging camp, not a colony.\n"
    "ladder_set mark camp_stable true, then ladder_set mark setup_done true (latch writes %s). The mountain base may start now.\n"
    "Owner: \"dont go building a massive camp just get telled and start on the mountain base.\" / \"let your people get good on food and set up camp before moving into the base like u said itll tak a while\"" % latch_name("setup-8-camp-stable"))
P["setup-9-new-pawn"] = ("A new pawn or a drifted grid. game_state: who is new, best skills.\n"
    "pawn_priorities for that pawn (one call), read back with pawn_check; game_set cmd assign pawn <name>; empire_pass for arms; beds + set_bed_owner; set_area Home.\n"
    "Refused: game_set cmd set_work_priority one cell at a time, read each back.\nSame day. Done: grid_matches_plan true.\n"
    "Owner: \"just have to always set up everything for new pawns\" / \"%s\"" % q_prio)
assert set(P) == set(order), set(P) ^ set(order)
for k, v in P.items():
    assert len(v.split("\n")) <= 12, k
    assert "START_SURVIVAL" not in v and "WOOD_FLOOR" not in v and "CROP_CELLS" not in v, k

out = {"family": "setup", "rungs": rungs, "prompts": {k: P[k] for k in order},
  "sensors_needed": [
    {"key": "pawns_unconfigured", "status": "TO_BUILD (decisions.json sensors)",
     "used_by": "no rung reads it yet: setup-9-new-pawn uses grid_matches_plan (measured) until it exists, then may add an any-branch on it",
     "csharp": "// RimPLCGameComponent: HashSet<int> configuredPawns; ExposeData: Scribe_Collections.Look(ref configuredPawns, \"configuredPawns\", LookMode.Value); the Inbox adds p.thingIDNumber when assign / set_work_priority / pawn_priorities is applied.\nif (configuredPawns != null) st[\"pawns_unconfigured\"] = (double)home.mapPawns.FreeColonistsSpawned.Count(p => !configuredPawns.Contains(p.thingIDNumber));"}],
  "variables_needed": [
    {"name": "MEAL_BILL_TARGET", "value": "existing gates.py tag (10 x colonists)", "rule": "Do until you have X, raise X"},
    {"name": "WOOD_RESERVE", "value": "existing gates.py tag (60 x colonists)", "rule": "chop below this (replaces the unknown WOOD_FLOOR)"},
    {"name": "FOOD_COMFORT_DAYS", "value": "existing gates.py tag", "rule": "camp stable before the mountain base (replaces the unknown FOOD_DAYS_STABLE)"},
    {"name": "(literals)", "value": "100 survival meals; chop 300; 75 crop cells (25/pawn x 3); ton 24 h stable, 6 h explore, 3 h store; ctu 2 arms, 3 priorities, 2 store, 2 shelter, 3 camp wall",
     "rule": "gates.py has no tag for these (START_SURVIVAL_MEALS, WOOD_TARGET, CROP_CELLS were never tags); ctu preset / ton hours must be literal"}],
  "missing_tools": src["missing_tools"],
  "unplaced_rules": [
    "Twitch staging/panels before the first colony (from the fresh-colony quote: \"1. no use a fresh crash landed scenrio all the world sat up and forest moutain tile pic world settup 300x300 in adv settings ect ect and all of that you already know, but before wee can start we need to stage and deploy and do the twitch setup for the RimPLC mod and its links and such for the infor in twitch streams and stuff with all the image like text and chain emoji things for the mods and wiki links ewe need to do for Rim PLC , im not really trusting the model to do that just yet\") -- JUSTIFIED: the new-colony half belongs to meta:new-colony (setup-0-new-colony is a pointer) and the Twitch half is configuration; the owner says he does not trust the model with it, so no setup rung drives it."],
  "notes": [
    "see meta:new-colony (setup-0-new-colony deleted per decisions.chains 'new colony'). Its owner quotes move VERBATIM into meta:new-colony owner_rules: " + json.dumps(re.findall(r'owner: "(.*?)"(?= / owner:|\s*$)', src["rungs"][0]["why"]), ensure_ascii=False),
    "see meta:unforbid-constant (setup-0-unforbid deleted; it read the ALIAS items_forbidden -> forbidden_items). Quote moves VERBATIM: \"%s\" (also kept in setup-chop's prompt)." % q_unforbid,
    "merged in from pointer rungs of other families: start-camp-chop/-fallback -> setup-chop; start-camp-stores -> setup-4-stores; start-camp-shelter/-fallback and start-camp-tight -> setup-4b-shelter + new setup-4b-shelter-fallback (CTU on mark_shelter_tried); start-camp-stable -> setup-8-camp-stable (bill_rows added to the hold; its mountain-base siting text NOT carried); start-standing-orders -> setup-6-run; start-new-pawn, growth-new-pawn-setup, config-priorities-new-pawn -> setup-9-new-pawn; camp-wood-wall-ring/-fallback -> setup-7-camp-defence + new setup-7-camp-defence-fallback (its CTU input moved from the sensor blueprints to mark camp_wall_tried, set on refusal).",
    "fallback rungs rank just ABOVE their main rung: gates.py hands back one chain, the top eligible rung, and a main rung stays eligible while its guard mark is false, so a fallback ranked below it could never fire. Each fallback is gated by its CTU/TON so it only wins after the strikes. All other rungs keep their relative order; band 3.30-3.96, step 0.03, no ties.",
    "latch false on rungs that take several passes (arms-out-first, setup-2-pawns, setup-1-explore, setup-4-stores, setup-4b-shelter, setup-5-stove, setup-7-camp-defence): a latch writes its done-mark after the FIRST pass and would retire the rung before its own guard mark is set (the critic's space-ship-research bug). Each clears on its own guard mark instead. Latched (single pass, guard set unconditionally): setup-0-starting-goods, setup-3-assign, leader-moral-guide, setup-8-camp-stable; done_mark = latch_name(id). No rung in any family reads these done-marks.",
    "explore_done is measured: RimPLC Engine.cs mirrors mark_explore_done into it. mark_explore_skipped retired; setup-4-stores no longer waits on exploring (decisions fixes_to_survivors).",
    "stage marks: arms-out-first reads mark_start_opening_done (set by start:*); setup-8-camp-stable is the only setter of camp_stable and setup_done; setup-7-camp-defence(-fallback) set camp_defence (backrooms:br-camp-wall for start_kind 7)."]}
json.dump(out, open(os.path.join(B, "families-fixed", "setup.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(rungs), len(out["prompts"]))
