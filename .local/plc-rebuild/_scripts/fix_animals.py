import json, re, os
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
src = json.load(open(os.path.join(B, "families", "animals.json"), encoding="utf-8"))
old = {r["id"]: r for r in src["rungs"]}

def latch_name(rid):
    return re.sub(r"[^a-z0-9]+", "_", str(rid).lower()).strip("_")[:35] + "_done"

STEADY = "mark_" + latch_name("animals-food-steady")
HANDLER = "mark_" + latch_name("animals-handler")
PEN = "mark_" + latch_name("animal-pen")
CAMP = {"mark_camp_stable": True}

Q_TERRA = "dont forget terriforming for soil plots"
Q_TEND = "remmebr always field tnde directly brefopre cpature and haul"

def rung(rid, prio, when, then, latch, why=None, never=None, note=None, extra_why=""):
    o = old.get(rid, {})
    r = {"id": rid, "priority": prio, "family": "animals", "when": when, "then": then}
    nv = never if never is not None else o.get("never")
    if nv: r["never"] = nv
    r["latch"] = latch
    r["why"] = (why if why is not None else o.get("why", "")) + extra_why
    if note or o.get("note"): r["note"] = note or o.get("note")
    r["owner_rules"] = sorted(set(q for q in re.findall(r'\\?"([^"]{12,})\\?"', r["why"]) if not q.startswith("walkthrough")))
    return r

R = []
# ---- food band 10.00-10.09 (explicit in decisions.json)
R.append(rung("animals-hunt-food", 10.0, {
    "colony_exists": True,
    "days_of_food": "<{FOOD_MIN_DAYS}",
    "wild_game": ">0",
    "alert_hunterlacksrangedweapon": False,
    "hostiles_on_map": 0,
    "hunt_ok": {"not": {"hunt_fails": {"ctu": {"mark_hunt_tried": True}, "preset": 3,
                                       "reset": {"days_of_food": ">={FOOD_MIN_DAYS}"}}}},
}, [
    "game_set cmd hunt -- designates every safe wild animal (skips NEVER_HUNT); read the count it returns",
    "designations_hunt still 0: game_select_architect_designator Orders/Hunt then game_apply_architect_designator on each wild_game animal's cell (game_get_cells_info finds them)",
    "both refused / designations_hunt still 0: ladder_set mark hunt_tried true, then ladder_set mark hunt_tried false (one count toward the gathering fallback)",
    "mark_butcher_built not true: survival:butcher-table first (butcher table before the first hunt)",
    "game_set cmd add_bill recipe CookMealSimple count {MEAL_BILL_TARGET}",
], False))
R.append(rung("animals-hunt-fallback", 10.01, {
    "colony_exists": True,
    "days_of_food": "<{FOOD_MIN_DAYS}",
    "hostiles_on_map": 0,
    "hunt_fails": {"ctu": {"mark_hunt_tried": True}, "preset": 3,
                   "reset": {"days_of_food": ">={FOOD_MIN_DAYS}"}},
}, [
    "say on stream: no safe game to hunt -- switching to gathering",
    "berry_bushes>0: game_select_architect_designator Orders/Harvest and game_apply_architect_designator on every berry bush",
    "growing_cells = 0: game_set cmd crops plant Plant_Rice; else check every field is harvesting",
    "colony_animals>1: Orders/Slaughter the least useful colony animal, never a trained mount or milk animal",
    "nothing to gather and nothing designated: ladder_set mark hunt_tried true, then ladder_set mark hunt_tried false",
], False))
R.append(rung("animals-danger-clear", 10.02, {
    "colony_exists": True,
    "danger_animals_near": ">0",
}, [
    "game_list_colonists -- anyone working near the dangerous animal?",
    "game_set cmd set_area pawn <each colonist> area Home",
    "it attacks / goes manhunter: game_set_draft the shooters, kill it at range before it closes",
    "a colonist goes down: field tend directly (order_pawn <doctor> tend <downed>) before anyone hauls them to a bed",
], False, extra_why=' / "%s"' % Q_TEND))
R.append(rung("animals-food-steady", 10.03, {
    "colony_exists": True,
    "food_held": {"ton": {"days_of_food": ">={FOOD_COMFORT_DAYS}", "meals": ">0"}, "hours": 24},
}, [
    "game_state -- read days_of_food, meals, raw_food once more",
    "ladder_set mark %s true" % latch_name("animals-food-steady"),
], True))

# ---- animals band 36.00-37.99 (all gated on mark_camp_stable per decisions.json progression)
p = [36.0]
def nxt():
    v = round(p[0], 2); p[0] += 0.1; return v

R.append(rung("animals-handler", nxt(), dict(CAMP, colony_exists=True, **{STEADY: True}), [
    "game_list_colonists -- the best Animals skill",
    "pawn_priorities <that pawn> custom {Handling:2}",
    "everyone else Handling 3 (never blank)",
    "refused: game_set cmd set_work_priority pawn <p> work Handling level 2",
    "ladder_set mark mounts_trained 0",
    "ladder_set mark %s true" % latch_name("animals-handler"),
], True))
R.append(rung("tame-mounts", nxt(), dict(CAMP, **{
    "mount_candidates": ">0",
    "mark_mounts_trained": "<{MOUNT_TARGET}",
    "colonists": ">3",
    STEADY: True,
    HANDLER: True,
    "danger_animals_near": 0,
    "tame_ok": {"not": {"tame_fails": {"ctu": {"mark_tame_tried": True}, "preset": 3,
                                       "reset": {"designations_tame": ">0"}}}},
}), [
    "game_get_cells_info: the best MOUNT_DEFS animal in sight (Horse, Dromedary, Muffalo first; Elephant/Thrumbo only with RIFLES_FOR_BIG_GAME armed shooters drafted)",
    "game_select_architect_designator Orders/Tame then game_apply_architect_designator on its cell",
    "read designations_tame back",
    "designations_tame still 0: ladder_set mark tame_tried true, then ladder_set mark tame_tried false",
], False, note="UNVERIFIED: which MOUNT_DEFS species Giddy-up can ride; after 3 refused tames the rung drops out until a tame designation appears -- buy mounts from a trader"))
R.append(rung("animal-pen", nxt(), dict(CAMP, colony_exists=True, **{
    STEADY: True,
    "has_stock": {"any": [{"colony_animals": ">=1"}, {"mount_candidates": ">0"}]},
}), [
    "pick open soil inside the defended camp beside the fields (game_get_cells_info: not marsh/water)",
    "game_list_architect_designators Structure: Fence -- game_drag_cell a closed ring of 30 cells per animal; a fence gate; a pen marker inside",
    "anything roofed it: Orders/Remove roof over the whole pen",
    "animal sleeping spots inside; game_set cmd stockpile_filter x z (pen corner) mode all for hay/kibble",
    "ladder_set mark milk_herd false",
    "ladder_set mark %s true" % latch_name("animal-pen"),
], True))
R.append(rung("animals-pen-soil", nxt(), dict(CAMP, **{PEN: True}), [
    "game_get_cells_info over the pen: every marsh/mud/sand/water cell",
    "terraform those cells to Soil (designator name UNVERIFIED: find it in game_list_architect_designators)",
    "refused: smaller drags; report which cells stayed bad",
    "ladder_set mark %s true" % latch_name("animals-pen-soil"),
], True, extra_why=' / "%s"' % Q_TERRA))
R.append(rung("animals-milk-herd", nxt(), dict(CAMP, **{PEN: True, HANDLER: True, "mark_milk_herd": False}), [
    "game_get_cells_info / game_take_screenshot: wild cows, goats, muffalo, dromedaries, chickens",
    "game_select_architect_designator Orders/Tame then game_apply_architect_designator on each (not NEVER_HUNT)",
    "a trader with cows and silver >= TRADE_SILVER_MIN: buy them",
    "count_cow + count_muffalo + count_goat + count_dromedary tamed (Animals tab) >= 2: ladder_set mark milk_herd true",
], False, note="mark milk_herd is initialised false by animal-pen; count_<def> also counts wild animals, so the Animals tab confirms the tame count"))
R.append(rung("animals-haygrass", nxt(), dict(CAMP, **{PEN: True, "colony_animals": ">=3", "quadrum_index": "<3"}), [
    "game_set cmd crops plant Plant_Haygrass -- 15 cells per colony animal next to the pen",
    "crops reused the rice field: game_set cmd set_zone_plant x z Plant_Haygrass on the new field",
    "ladder_set mark %s true" % latch_name("animals-haygrass"),
], True))
R.append(rung("animals-kibble", nxt(), dict(CAMP, **{"colony_animals": ">=3", "mark_butcher_built": True, "count_kibble": "<75"}), [
    "read the bench bill list first: Make_Kibble already there -> nothing to add",
    "game_set cmd add_bill recipe Make_Kibble count 75 (bench UNVERIFIED in this mod list)",
    "animals eat kibble/hay, never meals (Animals tab food restriction -- see missing_tools)",
], False))
R.append(rung("train-mounts", nxt(), dict(CAMP, **{
    "colony_animals": ">0",
    "mark_mounts_trained": "<{MOUNT_TARGET}",
    HANDLER: True,
    "train_ok": {"not": {"train_fails": {"ctu": {"mark_train_tried": True}, "preset": 3,
                                         "reset": {"designations_tame": ">0"}}}},
}), [
    "game_open_main_tab Animals: training Obedience, then Release, for each mount (one box per click, read back)",
    "game_set cmd set_area pawn <animal> area <pen>",
    "ladder_set mark mounts_trained <n trained>",
    "no mount to train / box refused: ladder_set mark train_tried true, then ladder_set mark train_tried false",
], False))
R.append(rung("armor-mounts", nxt(), dict(CAMP, **{"mark_mounts_trained": ">2"}), [
    "game_set cmd add_bill recipe <animal armor recipe> count 1 per mount -- only if the bench offers it",
    "not offered: say so on stream and skip",
    "ladder_set mark %s true" % latch_name("armor-mounts"),
], True))
R.append(rung("animals-autumn-cull", nxt(), dict(CAMP, **{
    "quadrum_index": 2,
    "colony_animals": ">6",
    "cull_ok": {"not": {"cull_fails": {"ctu": {"mark_cull_tried": True}, "preset": 3,
                                       "reset": {"quadrum_index": "!=2"}}}},
}), [
    "game_open_main_tab Animals -- pick the oldest/least useful, never a trained mount or a milk animal",
    "Orders/Slaughter designator on each until colony_animals <= 6",
    "slaughter refused: ladder_set mark cull_tried true, then ladder_set mark cull_tried false",
    "the meat: survival:butcher-fast takes it",
], False))
R.append(rung("cavalry-check", nxt(), dict(CAMP, **{"mark_mounts_trained": ">0", "CAVALRY_ENABLED": ">0"}), [
    "game_set_draft one rider",
    "game_list_selected_gizmos",
    "mount gizmo there: game_execute_gizmo mount, then ladder_set mark mounted_ready true",
    "no gizmo: ladder_set tag CAVALRY_ENABLED 0 -- war rungs fall back to infantry with animals on Release",
    "ladder_set mark %s true" % latch_name("cavalry-check"),
], True))
R.append(rung("cavalry-tactics", nxt(), dict(CAMP, **{"hostiles_on_map": ">0", "mark_mounted_ready": True, "CAVALRY_ENABLED": ">0"}), [
    "mounted riders flank on open ground, Run and Gun shooting on the move (memegoddess.runandgun)",
    "elephants front-line on Release",
    "retreat behind embrasures when hurt",
], False))

P = {
 "animals-hunt-food": "Look first: days_of_food, wild_game, hostiles_on_map.\n1) game_set cmd hunt -- read the count.  2) count 0: Orders/Hunt designator by hand on each safe animal cell.\n3) still 0: ladder_set mark hunt_tried true, then false (3 of those hand over to the fallback).\n4) no butcher table yet (mark_butcher_built): survival:butcher-table first.  5) add_bill CookMealSimple count MEAL_BILL_TARGET.\nNever NEVER_HUNT, never packs/predators, never during a raid.\nDone: designations_hunt > 0, then days_of_food back above FOOD_MIN_DAYS (resets the count).\nOwner: \"you have no food!! emergency no frefrisgeration hunt make food bills come one your perople WILL DIE!\" / \"cook bill maintained at 50 rather than 10\"",
 "animals-hunt-fallback": "Hunting failed 3 times (mark hunt_tried counted). Say it on stream, then gather.\n1) Orders/Harvest on every berry bush.  2) no field: game_set cmd crops plant Plant_Rice; check fields are harvesting.\n3) last resort: Orders/Slaughter the least useful animal, never a mount or milk animal.\nNothing worked: ladder_set mark hunt_tried true, then false.\nDone: days_of_food >= FOOD_MIN_DAYS (the counter resets). No done-mark: standing rung.\nOwner: \"IS AUTO HARVETS NOT WORKING? CROPS NEED HARVET\" / \"collecting resources planting crops and setting bills for food\"",
 "animals-danger-clear": "Look first: where the dangerous animal is vs your pawns.\n1) set_area every colonist to Home.  2) it charges: game_set_draft the shooters, kill it at range.\n3) someone downed: field tend first (order_pawn tend), then haul to a bed.\nNever hunt or tame it.\nDone: danger_animals_near 0 or it is dead. No done-mark: standing alarm.\nOwner: \"never letting someone melle person or animal get close to your pawns kill them with range at all costs\" / \"remmebr always field tnde directly brefopre cpature and haul\"",
 "animals-food-steady": "Look first: game_state days_of_food, meals, raw_food.\nFires only after days_of_food >= FOOD_COMFORT_DAYS and meals > 0 held for a full game day (ton 24h).\nTool: ladder_set mark animals_food_steady_done true. Nothing else.\nFallback: food dropped meanwhile -- do nothing, the timer restarts.\nDone: mark animals_food_steady_done = true. Until then: no pens, no taming, no mounts.\nOwner: \"let your people get good on food and set up camp before moving into the base like u said itll tak a while\"",
 "animals-handler": "Look first: game_list_colonists Animals skill.\n1) pawn_priorities <best> {Handling:2}  2) everyone else Handling 3, never blank.\nRefused: game_set cmd set_work_priority pawn <p> work Handling level 2.\nThen: ladder_set mark mounts_trained 0 (starts the mount count).\nDone: ladder_set mark animals_handler_done true.\nOwner: \"you only put 2s on the teask u want each colonist doing spliting theri work up\"",
 "tame-mounts": "Look first: mount_candidates on the map; danger_animals_near must be 0.\n1) Orders/Tame on the best MOUNT_DEFS animal (horse/dromedary/muffalo first).\nElephant/thrumbo: draft armed guards first.\nRefused / designations_tame still 0: ladder_set mark tame_tried true, then false.\n3 refusals: stop taming, buy mounts from a trader.\nDone: designations_tame > 0, then mark mounts_trained reaches MOUNT_TARGET (train-mounts).\nOwner: \"from elephant riding armies drop poding down from your megaship\"",
 "animal-pen": "Look first: open soil inside the defences next to the fields.\n1) Fence ring (Structure/Fence, game_drag_cell, 30 cells per animal) + fence gate + pen marker.\n2) No roof over it -- remove roof if any.  3) sleeping spots, a hay/kibble stockpile in a corner.\n4) ladder_set mark milk_herd false (starts the milk herd rung).\nRefused drag: one side at a time, read each back.\nDone: ladder_set mark animal_pen_done true.\nOwner: \"need milk right look for milk makers tame some build a fences in field to put them\" / \"dont put roof over you pen\"",
 "animals-pen-soil": "Look first: game_get_cells_info across the pen -- marsh, mud, sand, water.\n1) Terrain designator to Soil on each bad cell (find it in game_list_architect_designators).\nRefused: small drags; report which cells stayed bad.\nDone: ladder_set mark animals_pen_soil_done true.\nOwner: \"put soil under ur famrs and feilds and animal areas so they have grass grow\" / \"terriform u pen\" / \"dont forget terriforming for soil plots\"",
 "animals-milk-herd": "Look first: tameable milk makers on the map (cow, goat, muffalo, dromedary) and any trader.\n1) Orders/Tame on each.  2) a trader with cows and silver >= TRADE_SILVER_MIN: buy them.\nNone on map: wait for a trader; the rung stays live.\nDone: 2+ tamed milk animals (Animals tab), ladder_set mark milk_herd true.\nOwner: \"need milk right look for milk makers tame some build a fences in field to put them\" / \"have to trade, make a corral for cows and such, buy cows, get a silver supply like cash\" / \"kids need milk and cribs and toys\"",
 "animals-haygrass": "Look first: colony_animals, season (quadrum_index < 3).\n1) game_set cmd crops plant Plant_Haygrass beside the pen, 15 cells per animal.\nRefused: set_zone_plant x z Plant_Haygrass on an existing zone.\nDone: ladder_set mark animals_haygrass_done true.\nWalkthrough: one haygrass field per 2-3 large animals.\nOwner: \"put soil under ur famrs and feilds and animal areas so they have grass grow\"",
 "animals-kibble": "Look first: count_kibble and the bench bills.\n1) Bill already there: nothing.  2) add_bill Make_Kibble count 75.\nRefused (no bench offers it): say so, keep hay stocked instead.\nAnimals eat kibble or hay, never meals.\nDone: count_kibble >= 75. No done-mark: standing order.\nOwner: \"set amounts higher and higher as your base grows\"",
 "train-mounts": "Look first: Animals tab, trained skills of each mount.\n1) Obedience, then Release, for each (one box per click, read back).  2) set_area the animal to the pen.\n3) ladder_set mark mounts_trained <n trained>.\nRefused / nothing to train: ladder_set mark train_tried true, then false (3 = stop until a new tame).\nDone: mark mounts_trained >= MOUNT_TARGET.\nOwner: \"from elephant riding armies drop poding down from your megaship\"",
 "armor-mounts": "Look first: the bench bill picker for animal armor.\n1) add_bill <recipe> count 1 per mount.\nNot offered: skip and say so.\nDone: ladder_set mark armor_mounts_done true (latched, once).\nOwner: \"from elephant riding armies drop poding down from your megaship\"",
 "animals-autumn-cull": "Autumn (quadrum_index 2): more animals than winter can feed (cap 6).\n1) Animals tab: oldest/least useful, never mounts or milk animals.  2) Orders/Slaughter each until colony_animals <= 6.\nRefused: ladder_set mark cull_tried true, then false (3 = stop until next autumn).\nThe meat goes to survival:butcher-fast.\nDone: colony_animals <= 6. No done-mark: standing in autumn.",
 "cavalry-check": "1) game_set_draft one rider  2) game_list_selected_gizmos.\nMount gizmo: game_execute_gizmo it, ladder_set mark mounted_ready true.\nNo gizmo: ladder_set tag CAVALRY_ENABLED 0 -- infantry with animals on Release.\nDone: ladder_set mark cavalry_check_done true (latched).\nOwner: \"from elephant riding armies drop poding down from your megaship\"",
 "cavalry-tactics": "Raid on the map with mounted riders (mark mounted_ready).\n1) riders flank on open ground, shooting on the move.  2) elephants front line on Release.  3) hurt: back behind embrasures.\nNever charge turrets or mortars; never let melee close.\nFallback: no mount gizmo answers -- dismount, fight as infantry.\nDone: hostiles_on_map 0. No done-mark: standing combat rung.\nOwner: \"kill them with range at all costs\"",
}
for k, v in P.items():
    assert len(v.split("\n")) <= 12, k

out = {
 "family": "animals",
 "rungs": R,
 "prompts": P,
 "notes": [
  "see survival:hunter-weapon (animals-hunter-armed deleted per decisions.json chains 'hunting / butchering'); its owner quotes move VERBATIM to that survivor's owner_rules: \"Missing 0.5x raw food / No hunter has a valid hunting weapon\" / \"you havent set up your work tab manual priorities, everything from firefighting to cooking should be hieghest 1s and you only put 2s on the teask u want each colonist doing spliting theri work up so u have like on guy cutting and planting and one crafting and constructing and one hunting and everyhting else\"",
  "see survival:butcher-fast (animals-butcher-standing deleted per decisions.json chains 'hunting / butchering'); its owner quotes move VERBATIM to that survivor's owner_rules: \"how u plan on cutting up them animals?\" / \"u need to make meals sooner than later and get your shellves organized so like i already told you. so wtf are you not making a guide of everything ive told you becasue im not fucking around you are gonna die if u dont take care of them\" / \"cook bill maintained at 50 rather than 10\" / \"your freezer is completely empty\" / \"set amounts higher and higher as your base grows\" / \"make sure u set it right ur clicking the options twice\"; useful steps to merge: butcher fresh corpses only, ButcherCorpseFlesh bill only if missing, raw meat to the freezer stockpile",
  "mark camp_food_steady retired: readers use mark_animals_food_steady_done (latch_name of animals-food-steady). pen_built -> animal_pen_done, pen_soil -> animals_pen_soil_done, handler_set -> animals_handler_done, haygrass -> animals_haygrass_done, mounted_ready kept (set by cavalry-check).",
  "marks this family initialises so 'false'/'<' readers are measured: mounts_trained 0 (animals-handler), milk_herd false (animal-pen). ctu inputs hunt_tried / tame_tried / train_tried / cull_tried are set true-then-false by their own rung on refusal.",
  "tags not known to gates.py (PEN_CELLS_PER_ANIMAL, HAY_CELLS_PER_ANIMAL, KIBBLE_FROM_ANIMALS, KIBBLE_TARGET, WINTER_ANIMAL_CAP, PEN_MIN_ANIMALS) are written as literal numbers (30, 15, 3, 75, 6, 1) until added to tags.variables; see variables_needed."
 ],
 "sensors_needed": [dict(s, status="PROPOSED (not in decisions.json; no rung reads it)") for s in src["sensors_needed"] if s["key"] != "alert_hunterlacksrangedweapon"],
 "variables_needed": src["variables_needed"],
 "missing_tools": src["missing_tools"],
 "unplaced_rules": [
  {"quote": "u need to move those two cooler on the morgue freezer to east side of that narro room so they ppush outside correctly",
   "why": "cooler placement on the morgue freezer -- survival/temperature family, no animals rung builds coolers"},
  {"quote": "update the peeps watching... update your profile pic u arnt doing that oftern enough it should be comon place / basicly update your pic more in rimchat / still havnet update your pics yet you are suppose to be doing that,, you can even post game screenshots highlighted things that happen with your hand writting drawn o",
   "why": "stream/profile-pic rule mis-tagged animals; belongs to meta (stream band)"},
  {"quote": "open up your rim chat and get to planning and buildingf rimchat shall allways be overlayed",
   "why": "owner-rules-b tags it animals, but it is a RimChat overlay/planning rule; belongs to meta"}
 ]
}
json.dump(out, open(os.path.join(B, "families-fixed", "animals.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(R), len(P))
