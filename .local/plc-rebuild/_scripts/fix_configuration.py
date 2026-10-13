import json, re, os
B = r"C:\Users\gfour\Desktop\Backrooms\.local\plc-rebuild"
src = json.load(open(os.path.join(B, "families", "configuration.json"), encoding="utf-8"))
R = {r["id"]: r for r in src["rungs"]}
def ln(i): return re.sub(r"[^a-z0-9]+", "_", i.lower()).strip("_")[:35] + "_done"
TIMER = "sleep, wait or set a timer of any length (owner: \"stop setting timeres all timers are forbidden aCT NOW!\")"
Q_TEST = "\"quit mentioning the mod test count until u actually mark one off or atleast get something completed be chaekcing them all what can be marked offf, work towrdas the others\""
Q_REPEAT = "\"shes just repeating same things not living in the momnet and she still hasent set all the priorties scheduled drug use attakck heal and all that on assign\""
Q_FOOL = "\"set up priorities u fool / pawns have none set / your prioties for work are all fucked come on fix it for next time u know how to do it fix why u didnt do it and do it\""
rungs, prompts = [], {}
def add(id_, pr, when, then, never, latch, why, prompt, disabled=None):
    g = {"id": id_, "priority": pr, "family": "configuration"}
    if disabled: g["disabled"] = disabled
    g.update({"when": when, "then": then, "never": never, "latch": latch, "why": why})
    rungs.append(g); prompts[id_] = prompt

# ---- UI-clear band 1.05-1.08 (explicit in decisions.json) ----
add("config-hud-restore", 1.05, {"hud_visible": False},
    ["game_pause_game",
     "toggle the HUD (toggle_hud missing tool, F11); else game_get_ui_layout -> Menu -> Save as rimbridge_save_hudfix, then Load that save",
     "read hud_visible again",
     "ladder_set mark hud_restored true"],
    ["take more than one screenshot per look"], False, R["config-hud-restore"]["why"],
    "HUD is gone (hud_visible false).\n1. game_pause_game.\n2. Toggle HUD (F11, toggle_hud missing); else game_get_ui_layout -> Menu -> Save rimbridge_save_hudfix, then Load it.\n3. Read hud_visible again; one screenshot per look at most.\nDone: hud_visible true, ladder_set mark hud_restored true.\nOwner: \"save your peopel fix the game hud relaod it if its fucking busted wtf... we cant paly with no hud\".")
STUCK = {"stuck": {"ctu": {"mark_ui_close_tried": True}, "preset": 3, "reset": {"dialog_open": False}}}
add("config-ui-clear-stuck", 1.06, dict(STUCK),
    ["game_take_screenshot once and read which window is on top",
     "game_get_ui_layout, then game_click_ui_target on its Close / X / Cancel button",
     "game_close_main_tab",
     "ladder_set mark ui_stuck_reported true and say in chat (clean) that a window is stuck"],
    ["burst game_take_screenshot (owner: \"i lost the hud in my game here on the system i see no hud ui of the game when u where mass clicking shit it disappeared fix it\")",
     "mention the mod test count in that chat line (owner: " + Q_TEST + ")"],
    False, R["config-ui-clear-stuck"]["why"].replace("after 3 re-opens", "after 3 refused closes (mark_ui_close_tried, set by config-ui-clear)"),
    "config-ui-clear failed 3 times (mark_ui_close_tried counted).\n1. ONE game_take_screenshot, name the top window.\n2. game_get_ui_layout, game_click_ui_target its Close/X/Cancel.\n3. game_close_main_tab.\nDone: dialog_open false; ladder_set mark ui_stuck_reported true, one clean chat line.\nNo test-count talk: \"quit mentioning the mod test count until u actually mark one off\".\nOwner: \"i lost the hud in my game here on the system i see no hud ui of the game when u where mass clicking shit it disappeared fix it\".")
add("config-ui-clear", 1.07, {"dialog_open": True, "go": {"not": dict(STUCK)}},
    ["game_close_window (the top window: operations / bills / any menu)",
     "game_close_main_tab",
     "game_list_colonists, then game_select_pawn on ONE pawn and game_list_selected_gizmos: the Draft gizmo must be listed",
     "if no gizmo is listed: game_press_accept once, then game_close_window again",
     "still no Draft gizmo / dialog_open still true: ladder_set mark ui_close_tried true, then ladder_set mark ui_close_tried false (one count toward config-ui-clear-stuck)"],
    R["config-ui-clear"]["never"], False, R["config-ui-clear"]["why"],
    "A window is open and pawns cannot be ordered.\n1. game_close_window, then game_close_main_tab.\n2. game_list_colonists, game_select_pawn ONE pawn, game_list_selected_gizmos.\n3. Draft not listed: game_press_accept once, close again.\nStill stuck: ladder_set mark ui_close_tried true, then false; 3 counts hand over to config-ui-clear-stuck.\nDone: dialog_open false, Draft listed.\nNever burst screenshots, never a timer. Owner: \"i think it doesnt know how to click off the operation menu to use the pawns\".")
add("config-window-fullscreen", 1.08, {"window_fullscreen": False, "colony_exists": True},
    ["set_window_mode fullscreen (missing tool); until it exists: game_get_ui_layout -> Menu -> Options -> Video, pick Fullscreen (not Borderless), apply, read back",
     "read window_fullscreen again"],
    ["leave the game borderless"], True, R["config-window-fullscreen"]["why"],
    "Game should be fullscreen, not borderless (window_fullscreen false).\n1. game_get_ui_layout -> Menu -> Options -> Video.\n2. game_click_ui_target Fullscreen (not Borderless), apply, read back.\nNo set_window_mode tool yet: that UI path is the fallback.\nDone: window_fullscreen true; latch " + ln("config-window-fullscreen") + ".\nOwner: \"and change the game back to fullscreen not boarderless so i can tab in and out\".")

# ---- standing band 11.00-12.99 ----
add("blueprints-but-no-material", 11.00, {"blueprints": ">0", "wood": "<{WOOD_RESERVE}"},
    ["game_set cmd chop (count {WOOD_RESERVE}) -- nearest trees to the crew",
     "count wood lying at stumps too: game_set cmd unforbid",
     "if two build queues compete, cancel the lower one (cancel_blueprint missing tool; else select its blueprint and game_execute_gizmo Cancel)"],
    ["call pawns idle while blueprints wait on wood", TIMER], False, R["blueprints-but-no-material"]["why"],
    "Blueprints wait on wood.\n1. game_set cmd chop (count {WOOD_RESERVE}).\n2. game_set cmd unforbid for wood at the stumps.\n3. Two queues competing: cancel the lower one (select blueprint, game_execute_gizmo Cancel).\nRefused chop: game_select_architect_designator Orders/Chop on the nearest trees.\nDone: wood >= {WOOD_RESERVE}.\nOwner: \"keep building what you need to\".")
WPHELD = {"held": {"ton": {"grid_matches_plan": False}, "hours": 3}}
add("work-priorities-fallback", 11.10, dict(WPHELD),
    R["work-priorities-fallback"]["then"], R["work-priorities-fallback"]["never"] + [TIMER], False,
    R["work-priorities-fallback"]["why"],
    "pawn_priorities did not fix the grid in 3 hours.\n1. game_open_main_tab Work, game_get_ui_layout.\n2. game_set cmd set_work_priority one wrong cell at a time; read each digit back.\n3. game_close_main_tab.\nDone: grid_matches_plan true.\nOwner: \"you have to use the mouse to change the work priorities come on get it done\" / \"you did it iagin you set it correct then set it wrong and the n pasted wrongly to all\".")
wp = R["work-priorities-unset"]
add("work-priorities-unset", 11.20, {"colony_exists": True, "grid_matches_plan": False, "go": {"not": dict(WPHELD)}},
    wp["then"] + ["a new pawn or drift breaks the grid: same plan for EVERY pawn again (setup:setup-9-new-pawn owns the newcomer)"],
    wp["never"], False, wp["why"] + " / " + Q_FOOL,
    "The work grid does not match the plan.\n1. game_pause_game, game_list_colonists (skills, passions, incapables).\n2. pawn_priorities once per pawn: Firefighter..Cooking = 1 is the paste.\n3. Custom after Cooking: specialty 2, all else 3, 0 only if incapable. Split: one cuts/plants, one crafts/constructs, one hunts.\n4. Fix single cells with game_set cmd set_work_priority, re-read grid_matches_plan.\nNot fixed in 3 game hours: work-priorities-fallback does it cell by cell.\nDone: grid_matches_plan true.\nOwner: \"keep all the 1s firsefiring through cooking\" / \"dint leave a bunch blankk\" / \"set up priorities u fool\".")
FHELD = {"held": {"ton": {"fields_all_default_crop": True}, "hours": 4}}
add("fields-wrong-fallback", 11.30, dict(FHELD),
    R["fields-wrong-fallback"]["then"], ["click a field twice", TIMER], False, R["fields-wrong-fallback"]["why"],
    "set_zone_plant has not landed in 4 hours.\n1. game_click_cell the zone; if a plant got selected, click once more to reach the zone.\n2. Exactly ONE zone selected? game_get_context_menu_options / game_execute_gizmo the crop by its real label.\nDone: fields_all_default_crop false.\nOwner: \"some time u click twice it selects all firelds be werry\" / \"click the option s one not twice\".")
fw = R["fields-wrong"]
add("fields-wrong", 11.40, {"fields_all_default_crop": True, "go": {"not": dict(FHELD)}},
    fw["then"], fw["never"], False, fw["why"],
    "Every field grows the default crop.\n1. game_list_zones: growing zones near camp.\n2. game_set cmd set_zone_plant (x,z,plant) per field, each its own crop (rice, corn, healroot, cotton).\n3. Far main-base fields: game_set cmd set_zone_sowing allow false.\nNever click a field twice. Not changed in 4 hours: fields-wrong-fallback.\nDone: fields_all_default_crop false.\nOwner: \"you are going nothing but potatoes everywhere wtf!\" / \"get rid of all the base base fields and just keep the ones close to camp for now\".")
BILLCTU = {"tries": {"ctu": {"mark_bill_tried": True}, "preset": 3, "reset": {"bill_rows": ">0"}}}
add("bills-missing-fallback", 11.50, dict(BILLCTU),
    ["game_jump_camera_to_cell on the stove, select it, open Bills via game_get_ui_layout, Add bill -> simple meal, set Do until {MEAL_BILL_TARGET}",
     "read bill_rows again"],
    ["set a meal bill to Do forever", TIMER], False,
    R["bills-missing-fallback"]["why"].replace("came back empty 3 times", "came back empty 3 times (mark_bill_tried, set by bills-missing)"),
    "add_bill failed 3 times (mark_bill_tried counted).\n1. game_jump_camera_to_cell the stove, select it, open Bills via game_get_ui_layout.\n2. Add bill -> simple meal -> Do until {MEAL_BILL_TARGET}.\nDone: bill_rows > 0.\nOwner: \"how ive alllready tolsdd you how to do it effienctly so everyone can train and still get the most in one go\".")
bm = R["bills-missing"]
add("bills-missing", 11.60, {"colony_exists": True, "stoves": ">0", "bill_rows": 0, "go": {"not": dict(BILLCTU)}},
    ["game_set cmd add_bill (recipe CookMealSimple, count {MEAL_BILL_TARGET}) -- Do until X, never Forever",
     "re-read bill_rows: the Add-bill menu can throw and add nothing",
     "no skill restriction on the bill, so everyone trains; the best Cooking pawn stays the main cook",
     "refused / bill_rows still 0: ladder_set mark bill_tried true, then ladder_set mark bill_tried false (one count toward bills-missing-fallback)"],
    bm["never"], False, bm["why"],
    "A stove has no bills.\n1. game_set cmd add_bill (CookMealSimple, count {MEAL_BILL_TARGET}): Do until X, never forever.\n2. Re-read bill_rows; 0 means it silently failed: ladder_set mark bill_tried true, then false.\n3 failures: bills-missing-fallback does it by hand.\nNo skill limit: everyone trains.\nDone: bill_rows > 0.\nOwner: \"cook bill maintained at 50 rather than 10\" / \"and set amounts higher and higher as your base grows\".")
at = R["config-assign-tab"]
add("config-assign-tab", 11.70, {"colony_exists": True, "grid_matches_plan": True, "mark_assign_set": True},
    ["game_set cmd assign (pawn empty = all, food Fine, medicine Best, hostility Attack)",
     "read the result: every pawn listed with hostility Attack",
     "food restriction Fine must block raw food and human meat: game_open_main_tab Assign, game_get_ui_layout, Manage food restrictions -> Fine, untick raw food and human meat, read back (set_food_restriction missing tool)",
     "self-tend ON for every pawn (set_self_tend missing tool): select each pawn, game_get_ui_layout Health tab, tick Self-tend, read back"],
    ["assign hard drugs", "say the same line again: live in the moment (owner: " + Q_REPEAT + ")"], True,
    at["why"].replace(" / walkthrough-food-and-medicine.md [configuration] M: colonists best up to industrial, prisoners/animals herbal or worse", "") + " / walkthrough-food-and-medicine.md [configuration] F: Block raw food (-7 mood) and human meat",
    "Assign tab (after setup's assign).\n1. game_set cmd assign (all pawns, food Fine, medicine Best, hostility Attack); read back: every pawn Attack.\n2. Food restriction Fine: untick raw food (-7 mood) and human meat (Assign tab, Manage food restrictions).\n3. Self-tend: no tool yet; tick it per pawn on the Health tab, read back.\nDone: latch " + ln("config-assign-tab") + ".\nDon't repeat yourself: \"shes just repeating same things not living in the momnet\".\nOwner: \"do you have all the paws set up to heal attack and sleep whenever\".")
sc = R["config-schedule-anything"]
add("config-schedule-anything", 11.80, {"colony_exists": True, "mark_" + ln("config-assign-tab"): True},
    sc["then"][:-1], ["leave a pawn's hour on Sleep or Work"], True, sc["why"],
    "Schedule: Anything all 24 hours, every pawn.\n1. set_schedule is missing: game_open_main_tab Schedule, game_get_ui_layout.\n2. Pick the Anything brush, game_drag_cell across each pawn's 24 hours, read back.\n3. game_close_main_tab.\nDone: latch " + ln("config-schedule-anything") + ".\nOwner: \"set theri scheldule to anything at all times for all pawns\".")
dp = R["config-drug-policy"]
add("config-drug-policy", 11.90, {"colony_exists": True, "mark_" + ln("config-schedule-anything"): True},
    dp["then"][:-1], dp["never"] + ["set mark pawns_set or assign_set here (setup owns them)"], True, dp["why"],
    "Drug policy: no hard drugs for colonists (social drugs are for hospitality guests).\n1. set_drug_policy is missing: game_open_main_tab Assign, game_get_ui_layout.\n2. Each pawn's drug column -> the no-hard-drugs policy; read back.\nDone: latch " + ln("config-drug-policy") + ".\nOwner: \"set up drugs and scar to attack\" / \"were ur crops u get priorities done and scedukele and drug assignment and antibiotics\".")
ab = R["config-antibiotics"]
add("config-antibiotics", 12.00, {"mark_" + ln("config-drug-policy"): True, "research_penoxycylineproduction": True, "count_druglab": ">0"},
    ["edit_drug_policy: Penoxycyline every 5 days, carry 2 (missing tool; else Assign tab -> Manage drug policies by game_click_ui_target, read back)",
     "the DrugLab + Make_Penoxycyline bill belong to research:research-antibiotics; if no penoxycyline bill shows on the lab, game_set cmd add_bill (recipe Make_Penoxycyline, count {MEDICINE_RESERVE})"],
    ["give colonists hard drugs"], True, ab["why"],
    "Penoxycyline is researched and a drug lab stands.\n1. Assign tab -> Manage drug policies (edit_drug_policy missing): Penoxycyline every 5 days, carry 2; read back.\n2. No penox bill on the lab: game_set cmd add_bill (Make_Penoxycyline, count {MEDICINE_RESERVE}).\nNo drug lab: research:research-antibiotics builds it.\nDone: latch " + ln("config-antibiotics") + ".\nOwner: \"take only antibiotic pencylcin every 5 days and carry 2\".")
add("config-medical-defaults", 12.05, {"colony_exists": True, "mark_" + ln("config-assign-tab"): True},
    ["set_medical_care defaults (missing tool): select any pawn, game_get_ui_layout Health tab -> Default medical care",
     "colonists: best up to industrial medicine; prisoners and animals: herbal or worse; read back",
     "game_close_window"],
    ["give prisoners or animals industrial or glitterworld medicine by default"], True,
    "walkthrough-food-and-medicine.md [configuration] M: Default medical care colonists best up to industrial, prisoners/animals herbal or worse",
    "Default medical care.\n1. Select a pawn, game_get_ui_layout Health tab -> Default medical care (set_medical_care missing).\n2. Colonists: industrial; prisoners and animals: herbal or worse; read back.\n3. game_close_window.\nRefused: game_take_screenshot once, find the button, retry once.\nDone: latch " + ln("config-medical-defaults") + ".")
sp = R["config-stockpile-priority"]
add("config-stockpile-priority", 12.10, {"stockpile_cells": ">0", "colony_exists": True}, sp["then"][:-1], sp["never"], True, sp["why"],
    "Set stockpile priorities so goods flow inward.\n1. game_list_zones.\n2. Freezer: game_set cmd stockpile_filter (x,z,food, Important). Main store: nofood, Preferred. Dumping piles: Low.\nRefused: select the zone, game_get_ui_layout, pick priority by hand.\nNever click a storage row twice.\nDone: latch " + ln("config-stockpile-priority") + ".\nOwner: \"u have ppriorities set on stockpiles so thay pull it all through\".")
hp = R["config-haul-out-paced"]
add("config-haul-out-paced", 12.20, hp["when"], hp["then"], hp["never"], False, hp["why"],
    "Loose items outside storage (loose_items_unstored > 20).\n1. Two haulers at Hauling 1 (game_set cmd set_work_priority).\n2. order_pawn haul-to-capacity, one batch each, then let them rest and eat.\nRefused order: Hauling 1 alone does it, slower.\nDone: loose_items_unstored <= 20.\nOwner: \"you need to set stockpile and get everyone hueling stuff out without exahusting them\" / \"sending them on 50 runs without a break\".")
md = R["config-medicine-doctor"]
add("config-medicine-doctor", 12.30, {"mark_" + ln("config-assign-tab"): True, "needs_tend_count": ">0"},
    md["then"], [TIMER], False, md["why"],
    "Someone needs tending.\n1. Best Medicine pawn Doctor 1, a backup Doctor 2 (pawn_priorities custom, else game_set cmd set_work_priority).\n2. Herbal for small cuts, industrial for infections, glitterworld only to save a life.\n3. One pawn cleans the hospital first.\nDone: needs_tend_count 0.")
hv = R["config-hospitality-visitors"]
add("config-hospitality-visitors", 12.40, {"colony_exists": True, "mark_" + ln("config-drug-policy"): True}, hv["then"][:-1], hv["never"], True, hv["why"],
    "Visitors must be accepted.\n1. set_hospitality_accept missing: game_open_main_tab Hospitality, game_get_ui_layout, click accept visitors, read back.\nNever refuse the visitor pop-up.\nDone: latch " + ln("config-hospitality-visitors") + ".\nOwner: \"yes that one was to accept visitor if u refussed that pop up non will arrive until u set it in hospitality tab\".")
ps = R["config-post-strictness"]
add("config-post-strictness", 12.50, ps["when"], ["set_post_strictness default (missing tool: strict / default / mild)"], ps["never"], True, ps["why"],
    "Post-holding strictness should be default (between strict and mild).\nNo setting or tool exists yet (Rimrooms mod option needed): do nothing else here.\nDone: latch " + ln("config-post-strictness") + ".\nOwner: \"we cant have them not going to eat or finding saftey\" / \"stay at post strict mild, default> inbetween strict and mild\".",
    disabled=ps["disabled"])
br = R["bills-raise-target"]
add("bills-raise-target", 12.60, {"mark_camp_stable": True, "bill_rows": ">0", "hit": {"ons": {"meals": ">={MEAL_BILL_TARGET}"}}},
    ["set_bill_count missing: game_jump_camera_to_cell the stove, select it, open Bills via game_get_ui_layout, set the meal bill's Do until to {MEAL_BILL_TARGET} (the tag grows with the colony), read back",
     "never add a second meal bill"],
    ["set a meal bill to Do forever"], False, br["why"],
    "Meals reached the target: raise the bill as the base grows.\n1. game_jump_camera_to_cell the stove, open Bills (game_get_ui_layout).\n2. Do until {MEAL_BILL_TARGET} on the existing meal bill (set_bill_count missing); read back.\nNever a duplicate bill, never forever.\nDone: bill shows {MEAL_BILL_TARGET}.\nOwner: \"and set amounts higher and higher as your base grows\" / \"cook bill maintained at 50 rather than 10\".")

out = {"family": "configuration", "rungs": rungs, "prompts": prompts,
  "sensors_needed": [
    {"key": "hud_visible", "status": "TO_BUILD", "where": "RimPLC/Source/RimPLC/Sensors.cs fast cadence (ReadFast)", "csharp": "st[\"hud_visible\"] = !Find.UIRoot.screenshotMode.Active;"},
    {"key": "window_fullscreen", "status": "TO_BUILD", "where": "RimPLC/Source/RimPLC/Sensors.cs fast cadence (ReadFast)", "csharp": "st[\"window_fullscreen\"] = UnityEngine.Screen.fullScreen;"},
    {"key": "loose_items_unstored", "status": "TO_BUILD", "where": "RimPLC/Source/RimPLC/Sensors.cs normal cadence, new Sensors.ReadBuild(st, home, configuredPawns)", "csharp": "st[\"loose_items_unstored\"] = (double)home.listerHaulables.ThingsPotentiallyNeedingHauling().Count;"}],
  "variables_needed": [
    {"name": "POST_STRICTNESS", "value": "default", "rule": "strict / default / mild; default lets pawns eat and seek safety (text only: written as literal 'default' in config-post-strictness until a Rimrooms option exists)"}],
  "missing_tools": src["missing_tools"],
  "unplaced_rules": [
    "\"put all the mod wiki urls and github mod repo and stuff in the twitch write ups they are all blank too\" -- justified: Twitch channel panels are edited outside the game; no ladder rung or game tool can reach them (an owner task for the CLI, not RimPLC)"],
  "notes": [
    "see setup:setup-9-new-pawn (config-priorities-new-pawn deleted per decisions.json chain 'opening + camp'; its standing-order quote stays in work-priorities-unset's why)",
    "tags: MEAL_BILL -> MEAL_BILL_TARGET, WOOD_FLOOR -> WOOD_RESERVE, PENOX_STOCK -> MEDICINE_RESERVE (existing playbook variables with the same rules)",
    "config-drug-policy absorbs ideology-biotech-anomaly:ideo-colony-policy; config-antibiotics absorbs ideo-antibiotics' drug-policy half (DrugLab + bill live in research:research-antibiotics)",
    "dropped unmeasured sensor proposals (manual_priorities, schedule_all_anything, drug_policy_no_hard, penox_policy_set, hostility_all_attack, self_tend_all, meal_bill_target, room_count, stockpile_priorities_set, visitors_accepted, cleaning_assigned): not decisions.json TO_BUILD keys; those rungs run on their latches",
    "config-assign-tab now follows setup:setup-3-assign (mark_assign_set) so the landing assign is never doubled",
    "ctu inputs: mark_ui_close_tried (set by config-ui-clear), mark_bill_tried (set by bills-missing); primaries step aside via not-ctu once the fallback owns it"]}
json.dump(out, open(os.path.join(B, "families-fixed", "configuration.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(rungs), len(prompts), max(p.count("\n") + 1 for p in prompts.values()))
