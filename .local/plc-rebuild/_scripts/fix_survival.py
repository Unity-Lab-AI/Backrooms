"""Repair family 'survival' per decisions.json -> families-fixed/survival.json."""
import json, os, re, sys, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "..", "autopilot"))
from gates import latch_name, leaves  # noqa: E402

fam = json.load(open(os.path.join(ROOT, "families", "survival.json"), encoding="utf8"))
dec = json.load(open(os.path.join(ROOT, "decisions.json"), encoding="utf8"))


def other(family, rid):
    f = json.load(open(os.path.join(ROOT, "families", family + ".json"), encoding="utf8"))
    return next(r for r in f["rungs"] if r["id"] == rid)


rungs = {r["id"]: r for r in fam["rungs"]}
order = [r["id"] for r in fam["rungs"]]

# ---------------------------------------------------------------- pointers (decisions.chains)
notes = [
    "see base-and-fortress:power-every-consumer (survival:power-every-consumer deleted: duplicate id; its quotes \"you have shit all over your base that doesnt have power\" / \"8138 W (8400 Wd stored)\" belong in that survivor's owner_rules)",
    "see base-and-fortress:firebreak-ring (survival:firebreak deleted; its done-mark mark_firebreak_cut / latch firebreak_done retire with it)",
    "absorbed here (pointers in their families): animals:animals-hunter-armed -> hunter-weapon; animals:animals-butcher-standing -> butcher-fast; economy:econ-butcher -> butcher-table; base-and-fortress:hospital, growth:growth-hospital, growth:growth-hospital-fallback -> hospital-setup; base-and-fortress:freezer-cluster -> food-rotting-or-no-cold; economy:econ-freezer-shelves, economy:econ-freezer-fallback -> freezer-sorting; base-and-fortress:raid-cleanup, war:war-after-kill-storage -> after-the-kill; base-and-fortress:repair-after-raid -> repair-2-set; start:start-camp-beds -> beds-short; start:start-camp-food -> food-low",
    "latched done-marks (latch_name): " + ", ".join(
        f"{i} -> mark_{latch_name(i)}" for i in ["meals-early", "butcher-table", "freezer-sorting", "storage-logic",
                                                   "hospital-setup", "shelter-night-one", "hvac-clusters", "work-grid-set",
                                                   "kitchen-clean"]),
]
for gone in ("power-every-consumer", "firebreak"):
    order.remove(gone); del rungs[gone]


def merge(rid, family, src_id, steps=True, never=True):
    r, s = rungs[rid], other(family, src_id)
    r["why"] += f" || merged from {family}:{src_id}: " + s["why"]
    ors = r.setdefault("owner_rules", [])
    for q in s.get("owner_rules", []) or []:
        if q not in ors: ors.append(q)
    if steps:
        r["then"] += [f"({src_id}) " + t for t in s["then"] if "ladder_set" not in t]
    if never:
        for n in s.get("never", []) or []:
            if n not in r.setdefault("never", []): r["never"].append(n)


merge("hunter-weapon", "animals", "animals-hunter-armed")
merge("butcher-fast", "animals", "animals-butcher-standing")
merge("butcher-table", "economy", "econ-butcher")
merge("hospital-setup", "base-and-fortress", "hospital")
merge("hospital-setup", "growth", "growth-hospital")
merge("hospital-setup", "growth", "growth-hospital-fallback", steps=False)
merge("food-rotting-or-no-cold", "base-and-fortress", "freezer-cluster")
merge("freezer-sorting", "economy", "econ-freezer-shelves")
merge("freezer-sorting", "economy", "econ-freezer-fallback", steps=False)
merge("after-the-kill", "base-and-fortress", "raid-cleanup")
merge("after-the-kill", "war", "war-after-kill-storage")
merge("repair-2-set", "base-and-fortress", "repair-after-raid")
merge("beds-short", "start", "start-camp-beds")
merge("food-low", "start", "start-camp-food")

# ---------------------------------------------------------------- when / step repairs
R = rungs
R["colony-before-research"]["when"]["alert_idle"] = R["colony-before-research"]["when"].pop("idle")
# combat-0-reset: colonist_hurt is a measured sensor, not a mark
R["combat-0-reset"]["then"] = [t for t in R["combat-0-reset"]["then"] if "colonist_hurt" not in t]
# starving -> starving-no-game counter: input mark starve_tried, set on refusal
R["starving"]["when"] = {"alert_starv": True,
                         "hunt_tries": {"not": {"tries": {"ctu": {"mark_starve_tried": True}, "preset": 2, "reset": {"alert_starv": False}}}}}
R["starving"]["then"] = ["ladder_set mark starve_tried false (re-arm the counter edge)"] + \
    [t for t in R["starving"]["then"] if "starve_attempt" not in t] + \
    ["a hunt/harvest/bill refused or no game found: ladder_set mark starve_tried true (counts for starving-no-game)"]
R["starving-no-game"]["when"] = {"alert_starv": True,
                                 "starve_retry": {"ctu": {"mark_starve_tried": True}, "preset": 2, "reset": {"alert_starv": False}}}
R["starving-no-game"]["then"] = ["ladder_set mark starve_tried false (re-arm the counter edge)"] + R["starving-no-game"]["then"] + \
    ["slaughter and trade both refused: ladder_set mark starve_tried true and say on stream what is missing"]
# butcher-table: measured table count joins (econ-butcher)
R["butcher-table"]["when"]["count_tablebutcher"] = "<1"
# shelter-night-one: backstop behind setup:setup-4b-shelter, never a second shelter
R["shelter-night-one"]["when"]["mark_shelter_set"] = False
R["beds-short"]["when"] = {"beds": "<{BEDS_NEEDED}", "shelter_up": {"any": [{"mark_shelter_built": True}, {"mark_shelter_set": True}]}}
# after-the-kill: one-shot per kill, no forever-latch
R["after-the-kill"]["when"] = {"hostiles_on_map": 0, "kill_over": {"ons": {"hostiles_on_map": 0, "threat_letter": True}}}
R["after-the-kill"]["then"] = [t for t in R["after-the-kill"]["then"] if "after_kill_done" not in t] + \
    ["game_set_draft off for everyone (raid-cleanup)",
     "ladder_set mark after_kill_done true (others may read it; this rung itself is one-shot on the kill)"]
# storage-audit fires only when something lies unstored (TO_BUILD loose_items_unstored)
R["storage-audit"]["when"]["loose_items_unstored"] = ">0"
R["storage-audit"].pop("note", None)
# hospital: merged fallback + mark
R["hospital-setup"]["then"] = [t for t in R["hospital-setup"]["then"] if "ladder_set" not in t] + [
    "Medical gizmo or medicine filter refused twice: beds in the room nearest the stores, medicine stays in the main store (stockpile_filter mode all), say the medical-bed tool is missing",
    "ladder_set mark hospital_set true"]
# freezer: merged fallback
R["freezer-sorting"]["then"] = [t for t in R["freezer-sorting"]["then"] if "ladder_set" not in t] + [
    "filter/room refused twice: game_set cmd stockpile_camp mode food (roofed, beside the stove) and stockpile_filter mode nofood on every other store (econ-freezer-fallback)",
    "ladder_set mark freezer_sorted true"]
# cold: the mark it set had no reader
R["cold"]["then"] = [t for t in R["cold"]["then"] if "outdoor_cold" not in t]

# ---------------------------------------------------------------- unplaced rules + critic section 6
place = {
    "you can set one pawn then paste templet to others then a customize them character editor tab bottom right is a go, correct the record": "work-grid-set",
    "you are slacking ther should be a order of operation between talking to chat always sayiong hi, keeping pawns needs up and healthy, and chating, and making images and guidesing them through think on everything in gaem": "mental-break",
}
left = []
justify = {
    "nmake that sotrage room a prison hold": "base-and-fortress (room layout: storage room -> prison hold); critic section 6 lists it there",
    "you need to put horse shoes up": "growth / base-and-fortress (rec room layout, horseshoe pin vs interaction cell)",
    "saw an error, u tried mining": "base-and-fortress / setup (mining designations over unexplored rock) -- a mining rule, no survival rung designates mining",
    "dont forget terriforming": "economy (soil / fields); critic section 6 lists it",
    "and u can move walls and furnature": "base-and-fortress (furniture placement / rotation)",
    "do whal alfreddo guy said": "meta (owner relays a viewer's advice; owner-message rung)",
    "colony dies... start another": "meta:new-colony (decisions chains 'new colony': a colony starts only on the owner's order; meta owns that rule)",
    "make em comperable to us": "growth / setup (pawn creation in the character editor)",
    "next time that guy wants a character": "chat (viewer requests)",
    "all of the crops grow them all": "economy (crops-full-set / guest trade)",
    "Male, age 14": "base-and-fortress (halls, pathing, uniformity) -- critic section 6 'halls 3 wide' group",
}
for u in fam["unplaced_rules"]:
    q = u["quote"]
    if q in place:
        r = R[place[q]]
        r["why"] += f" / owner: \"{q}\""
        r.setdefault("owner_rules", []).append(q)
    else:
        k = next(k for k in justify if q.startswith(k))
        left.append({**u, "reason": "not placed in survival: belongs to " + justify[k]})

# critic section 6 quote that is survival's ("keeping pawns needs up" is above); dry-storage shelves go to storage-logic
dry = "ur dry storage needs more shleves / add another shelfe N side of existing ones directly / and missing ones"
R["storage-logic"]["why"] += f" / owner: \"{dry}\""
R["storage-logic"].setdefault("owner_rules", []).append(dry)
R["storage-logic"]["then"].insert(-1, "dry storage: add shelves on the N side of the existing ones, directly against them, and fill any missing shelf spots")

# ---------------------------------------------------------------- new rung: blight (critic section 7)
R["blight"] = {
    "id": "blight", "family": "survival",
    "when": {"blight_new": {"ons": {"letter_matches": "blight"}}},
    "then": ["game_get_cells_info over every growing zone: find the blighted plants",
             "game_apply_architect_designator PlantsCut on every blighted plant at once (it spreads to neighbours)",
             "pawn_priorities the best grower: PlantCutting/Growing 1 until it is cut"],
    "never": ["leave a blighted plant standing"],
    "why": "walkthrough (critic section 7): \"cut blighted plants at once\"",
    "latch": False,
}
order.insert(order.index("starving"), "blight")

# ---------------------------------------------------------------- priorities (decisions.bands)
rows = [r for r in dec["bands"]["rows"] if r["family"] == "survival"]
explicit = {k: v for r in rows for k, v in r["explicit"].items()}
sustain = [i for i in sorted(order, key=lambda i: (R[i]["priority"] if "priority" in R[i] else 3.99, order.index(i)))
           if i not in explicit]
for i, rid in enumerate(sustain):
    R[rid]["priority"] = round(4.0 + 0.1 * i, 2)
for rid, p in explicit.items():
    R[rid]["priority"] = p
assert len({R[i]["priority"] for i in order}) == len(order)

# ---------------------------------------------------------------- mark syntax normalisation
for r in R.values():
    r["then"] = [re.sub(r"ladder_set op mark name (\w+) value (\S+)", r"ladder_set mark \1 \2", t) for t in r["then"]]

# ---------------------------------------------------------------- prompts
SW = "Owner: \"can she handle this fight if yes unpasue if no plan help o can help get there soon? no then run keep range too many get help\"."
P = {
"fire-in-camp": """LIVE: fire on the map (fire_cells > 0).
1. game_pause_game pause true.
2. pawn_priorities: every pawn not downed, Firefighter stays 1.
3. game_apply_architect_designator Home over the burning cells + a 3-cell ring (outside Home they ignore fire).
4. game_set cmd set_area pawn X area '' for anyone fenced out.
5. game_pause_game pause false.
Fallback: a tool refuses -> say it, re-read game_state, never leave the game paused more than one turn.
Never draft pawns into a burning room; fight from the edge.
Done = fire_cells 0 (no mark). Items ignite near 235C.""",
"downed-pawn": """LIVE: someone is downed and the map is clear.
1. game_list_colonists -> who is down, bleeding?
2. Bleeding: order_pawn <doctor> tend <downed> where they lie FIRST.
3. order_pawn <nearest> rescue <downed> to a Medical bed; order_pawn <downed> rest until healed.
4. Bed reads For prisoners: game_set cmd set_bed_owner x z owner colonist.
Fallback: order_pawn refuses the tend -> game_right_click_cell on the pawn, pick Tend.
Done = downed_count 0 (no mark).
Owner: "remmebr always field tnde directly brefopre cpature and haul" / "hospital is prisoner only fix that".""",
"mental-break": """LIVE: a mental break (mental_break true).
1. game_list_colonists -> who, which break.
2. Berserk: game_set_draft 2 pawns, fists only, down them; no guns.
3. Fire-starter: firefighters on 1, others away.
4. Say the cause on stream, clean words.
5. Fix the root (food, bed, temperature, corpses) -- each has its own rung.
Fallback: draft refused -> game_click_cell the pawn, Draft gizmo via game_execute_gizmo.
Done = mental_break false (no mark).
Owner: "maintain ur colonists' needs" / "keeping pawns needs up and healthy".""",
"combat-0-reset": f"""LIVE: fight over (combat_paused true, hostiles_on_map 0).
1. game_set_draft false for every pawn.
2. game_pause_game pause false.
3. ladder_set mark combat_paused false; ladder_set mark combat_plan 0; ladder_set mark help_coming false.
Fallback: undraft refused -> game_execute_gizmo Draft toggle on the pawn.
Done = mark combat_paused false. Say it on stream, clean.
{SW}""",
"combat-0-reassess-worse": f"""LIVE: we chose to fight (combat_plan 1) but fight_ratio fell under FIGHT_RATIO_MIN.
1. game_pause_game pause true.
2. ladder_set mark combat_plan 0 -- the branch rungs choose again next scan.
Fallback: pause refused -> say it and still reset combat_plan.
Done = mark combat_plan 0. Never paused more than one turn.
{SW}""",
"combat-0-reassess-better": f"""LIVE: holding/kiting/retreating (combat_plan > 1) and fight_ratio is back at FIGHT_RATIO_MIN.
1. game_pause_game pause true.
2. ladder_set mark combat_plan 0 so combat-2-fight takes over.
Fallback: pause refused -> say it and still reset combat_plan.
Done = mark combat_plan 0. Never paused more than one turn.
{SW}""",
"combat-1-damage-pause": f"""LIVE: float switch -- a colonist is hurt (colonist_hurt) with hostiles on the map.
1. game_pause_game pause true.
2. Read fight_ratio (able shooters / hostiles) off the ladder.
3. ladder_set mark combat_paused true -- the combat-2 rungs pick the plan.
Fallback: pause refused -> still set the mark; say the plan on stream, clean.
Done = mark combat_paused true.
Owner: "float switch for healt bars and colonist has taken damage pausing".""",
"combat-2-fight": f"""LIVE: YES we can take it (fight_ratio >= FIGHT_RATIO_MIN).
1. game_set_draft true per armed shooter.
2. order_pawn / game_click_cell each to an embrasure on the threatened side.
3. ladder_set mark combat_plan 1; game_pause_game pause false.
Fallback: an order refused -> game_right_click_cell the spot for that pawn; never melee with shooters.
Done = mark combat_plan 1.
{SW}""",
"combat-2-help-coming": f"""LIVE: outmatched, help is coming (mark help_coming true).
1. game_set_draft true; order_pawn everyone inside the walls, out of their range.
2. ladder_set mark combat_plan 2; game_pause_game pause false; hold until help lands.
Fallback: a pawn cannot path inside -> kite with it (keep range).
Done = mark combat_plan 2.
{SW}""",
"combat-2-call-help-comms": f"""LIVE: too many (fight_ratio < CALL_HELP_RATIO), a comms console stands.
1. game_click_cell the console with a pawn -> call an ally's military aid (read the menu, never guess the cost).
2. ladder_set mark help_coming true; ladder_set mark combat_plan 4.
3. Fall back inside the walls, unpause.
Fallback: the call menu refuses -> leave help_coming false; combat-2-retreat takes over.
Done = mark combat_plan 4.
{SW}""",
"combat-2-call-help-permit": f"""LIVE: too many, no comms answer, a title permit (mark_title_rank > 3).
1. Select the titled pawn -> game_list_selected_gizmos -> game_execute_gizmo the military-aid permit.
2. ladder_set mark help_coming true; ladder_set mark combat_plan 4.
3. Retreat inside the walls, unpause.
Fallback: permit on cooldown/refused -> combat-2-retreat takes over.
Done = mark combat_plan 4.
{SW}""",
"combat-2-retreat": f"""LIVE: too many and nobody to call.
1. game_set_draft true; order_pawn everyone inside the walls (mountain base, or an open gate).
2. Close the doors; shoot from embrasures only.
3. ladder_set mark combat_plan 5; game_pause_game pause false.
Fallback: walls breached -> kite (keep range) toward the next wall.
Done = mark combat_plan 5.
{SW}""",
"combat-2-kite": f"""LIVE: outmatched, no help soon, not swamped.
1. game_set_draft true; order_pawn fall back while shooting, never stand in melee.
2. ladder_set mark combat_plan 3; game_pause_game pause false.
Fallback: cornered -> retreat inside the walls (combat-2-retreat steps).
Done = mark combat_plan 3.
{SW}""",
"med-1-bleeding-under-fire": f"""LIVE: a pawn bleeds (pawn_bleeding) with hostiles on the map.
1. Threat first: follow combat_plan (game_set_draft everyone able, kill the threat).
2. Never carry a bleeding pawn under fire.
3. Shooting near them stops -> med-2-field-tend takes over.
Fallback: the bleeder is in the line of fire -> order_pawn them to crawl/hold behind cover.
Done = hostiles_on_map 0 (no mark).
Owner: "ppawn bnleeding is there enemy on map if so daft all kill thing" / "remmebr always field tnde directly brefopre cpature and haul".""",
"combat-3-hold-plan": f"""LIVE: fight in progress, plan chosen (combat_plan > 0).
Follow combat_plan: 1 fight, 2 hold for help, 3 kite, 4 help called, 5 retreat.
Tools: game_set_draft, order_pawn, game_click_cell -- one order per pawn, read it back.
Re-read fight_ratio every scan; the reassess rungs re-plan.
Fallback: an order refuses -> pause one turn, re-issue, say it on stream.
Done = hostiles_on_map 0 (combat-0-reset clears the marks).
{SW}""",
"med-2-field-tend": """LIVE: bleeding, map clear, not yet field tended.
1. order_pawn <best doctor> tend <bleeder> where they lie, best medicine.
2. ladder_set mark field_tended true.
Fallback: order refused -> game_right_click_cell the pawn -> Tend.
Done = mark field_tended true; med-3 carries them next.
Owner: "save pawns field tend before carry to hospiital".""",
"med-3-carry-to-hospital": """LIVE: field tended, map clear.
1. order_pawn <nearest> rescue <patient> to a Medical bed.
2. order_pawn <doctor> tend <patient> again in the bed.
3. ladder_set mark field_tended false.
Fallback: no Medical bed -> any colonist bed (set_bed_owner owner colonist).
Done = mark field_tended false.
Owner: "save pawns field tend before carry to hospiital".""",
"heat-wave": """LIVE: heat wave (condition_heatwave, +17C for 1.5-3.5 days).
1. game_set cmd set_area pawn <each> area Home -- roofed, cooled rooms only.
2. game_get_cell_info a freezer cell: still under 0C? If not, a cooler there first.
3. No power: passive cooler (wood) in each roofed living room.
4. A backrooms gate open: send the crew through. Watch fire_cells.
Fallback: build_cooler missing -> game_select_architect_designator + game_click_cell, check rotation.
Done = condition_heatwave false (no mark).
Owner: "you need to figure out the tmepature pronblem asap ASAP one heat wave and your dead in 3 minutes".""",
"cold-snap": """LIVE: cold snap (condition_coldsnap, -20C).
1. Heat bedrooms: heater, or campfire mid-room.
2. game_set cmd add_bill recipe Make_Apparel_Parka count <colonists> (or Tuque/TribalWear).
3. game_apply_architect_designator Harvest on every crop before -10C (outdoor_temp).
Fallback: add_bill refuses the recipe -> read the bench's bill menu for the exact defName.
Done = condition_coldsnap false (no mark).""",
"solar-flare": """LIVE: solar flare -- every powered thing is off 0.15-0.5 days.
1. Campfire in the coldest lived room; passive cooler in the freezer if hot.
2. Weapons in hand, no outings, no fights started.
3. Freezer above 0C (game_get_cell_info) -> cook raw meat now.
Fallback: no wood for campfire -> game_set cmd chop count 50 first.
Done = condition_solarflare false (no mark).""",
"eclipse-battery": """LIVE: eclipse -- solar gives 0.
1. game_click_cell a battery: read stored Wd vs use.
2. Under a day of storage: game_execute_gizmo off on lamps in empty rooms; keep coolers, heaters, freezer on.
3. wood >= WOOD_RESERVE: queue a wood-fired generator.
Fallback: battery unreadable -> switch off non-vital consumers anyway.
Done = condition_eclipse false (no mark).
Owner readout: "Grid excess: 0 W (0 Wd stored) ... Current power use: Off".""",
"toxic-fallout": """LIVE: toxic fallout.
1. game_set cmd set_area pawn <each> area Home (roofed rooms).
2. game_apply_architect_designator Harvest on unroofed crops now.
3. A pawn at 40% toxic buildup (TOXIC_PULL_IN): order_pawn rest in a bed indoors.
Fallback: area tool refused -> game_set_draft and order_pawn each inside.
Done = condition_toxicfallout false (no mark).""",
"volcanic-winter": """LIVE: volcanic winter and under 20 days of food.
1. ladder_set tag MEAL_BILL_TARGET 100; game_set cmd add_bill recipe CookMealSimple count {MEAL_BILL_TARGET}.
2. game_set cmd hunt on safe game (never NEVER_HUNT).
3. A roofed, heated room with sun lamps + growing zone (greenhouse).
Fallback: no sun lamp research -> bank meals and pemmican, trade for food.
Done = days_of_food >= 20 or condition_volcanicwinter false (no mark).""",
"flashstorm": """LIVE: flashstorm.
1. game_set cmd set_area pawn <each> area Home -- away from the storm radius.
2. When it ends: fire-in-camp takes over any fire_cells.
Fallback: area tool refused -> order_pawn each indoors.
Done = condition_flashstorm false (no mark).""",
"blight": """LIVE: a blight letter (letter_matches "blight") -- one-shot per letter.
1. game_get_cells_info over each growing zone: find the blighted plants.
2. game_apply_architect_designator PlantsCut on every blighted plant at once.
3. pawn_priorities the best grower: Growing 1 until cut.
Fallback: blighted cells unreadable -> cut the whole affected field.
Done = no blighted plant left (no mark; the ons fires once per letter).
Walkthrough: "cut blighted plants at once".""",
"starving": """LIVE: colonists are starving (alert_starv), hunt not yet failed twice.
1. ladder_set mark starve_tried false.
2. game_set cmd hunt (safe game, never NEVER_HUNT) -> Harvest berries/agave -> add_bill CookMealSimple count {MEAL_BILL_TARGET}.
3. No field: game_set cmd crops plant Plant_Rice. pawn_priorities Cooking 1, Hunting 2 for the best shooter.
Fallback: anything refused or no game: ladder_set mark starve_tried true (2 times -> starving-no-game).
Done = alert_starv false (no mark).
Owner: "you have no food!! emergency no frefrisgeration hunt make food bills come one your perople WILL DIE!".""",
"starving-no-game": """LIVE: starving and the hunt failed twice (ctu on mark starve_tried, preset 2).
1. ladder_set mark starve_tried false.
2. game_right_click_cell a spare animal -> Slaughter (never a trained mount).
3. Trade any caravan for packaged meals/pemmican; insect/human meat last, say the mood hit.
Fallback: both refused -> ladder_set mark starve_tried true, say what is missing on stream.
Done = alert_starv false (resets the counter).
Owner: "YOU PEOPLE WILL DIE!!!".""",
"pawn-starving": """LIVE: zero meals, raw food < 5, under FOOD_PANIC_DAYS left.
1. game_apply_architect_designator Harvest on every food plant near camp.
2. game_set cmd hunt (never boomalope near wood).
3. game_set cmd add_bill recipe CookMealSimple count 30; order_pawn the nearest to it.
Fallback: hunt refused (no ranged weapon) -> hunter-weapon rung; nothing on the map -> say so.
Done = days_of_food >= FOOD_PANIC_DAYS (no mark).
Owner: "YOU PEOPLE WILL DIE!!!".""",
"hunter-weapon": """LIVE: "No hunter has a valid hunting weapon" (alert_hunterlacksrangedweapon).
1. game_list_colonists: the pawn with Hunting on and the best Shooting.
2. game_set cmd unforbid; order_pawn <hunter> equip the best loose bow/rifle, read it back.
3. pawn_priorities <hunter> custom {Hunting:2}.
Fallback: no ranged weapon -> game_set cmd add_bill recipe Make_Bow_Short count 1, or Hunting off.
Done = the alert clears (no mark). Never send a melee-only pawn to hunt.""",
"food-low": """LIVE: days_of_food under FOOD_MIN_DAYS.
1. game_set cmd add_bill recipe CookMealSimple count {MEAL_BILL_TARGET} (bulk x4 first, single below).
2. game_set cmd crops a second field (colonists x FIELD_CELLS_PER_PAWN); game_set cmd hunt safe game.
3. Under FOOD_MIN_DAYS on a new camp: harvest every berry bush near camp; no fortress digging yet.
Fallback: recipe refused -> read the stove's bill menu for the defName.
Done = days_of_food >= FOOD_MIN_DAYS (no mark).
Owner: "cook bill maintained at 50 rather than 10" / "let your people get good on food and set up camp before moving into the base".""",
"meals-early": f"""LIVE: a stove stands, the meal bill was never set.
1. game_set cmd add_bill recipe CookMealSimple_Bulk count {{MEAL_BILL_TARGET}}, then CookMealSimple below.
2. Meat + veg stocked: add_bill CookMealFine count 10. Do until X, never Forever.
3. ladder_set mark meal_bill_set true.
Fallback: recipe name refused -> game_click_cell the stove, read the bill menu.
Done = mark meal_bill_set true; latch mark {latch_name('meals-early')}.
Owner: "u need to make meals sooner than later" / "dont set build forever if anything set 1000 each type".""",
"butcher-table": f"""LIVE: stove set (mark_stove_set), no butcher table (count_tablebutcher < 1).
1. game_apply_architect_designator TableButcher beside the freezer/stove, outside the kitchen.
2. Built: game_set cmd add_bill recipe ButcherCorpseFlesh count 20.
3. ladder_set mark butcher_built true.
Fallback: no wood/steel -> setup-chop first; say it.
Done = mark butcher_built true; latch mark {latch_name('butcher-table')}.
Owner: "how u plan on cutting up them animals?".""",
"butcher-fast": """LIVE: corpses lying 24 h and a butcher table stands.
1. game_set cmd unforbid (the kill).
2. game_set cmd add_bill recipe ButcherCorpseFlesh count 20 if missing (read the bill list first).
3. pawn_priorities: Cooking 1 for the cook until done; meat to the freezer.
Fallback: corpse rotten -> it cannot be butchered: bury/dump it.
Done = corpses 0 (no mark).
Owner: "make sure u set it right ur clicking the options twice".""",
"power-fail-cook-meat": """LIVE: power is down and the freezer was sorted (raw meat warming).
1. game_set cmd add_bill recipe CookMealSimple count {MEAL_BILL_TARGET} and Make_Pemmican.
2. game_get_cell_info a generator: fuel it / repair it.
Fallback: stove unpowered too -> campfire cooking.
Done = has_power true (no mark).""",
"winter-food-stock": """LIVE: outdoor_temp under 10C and food under FOOD_COMFORT_DAYS.
1. Raise the meal bill: meals >= 10 x colonists.
2. game_apply_architect_designator Harvest all crops before -10C.
3. A roofed outdoor stockpile below 0C is a free freezer (game_set cmd stockpile_camp mode food).
Fallback: harvest refused -> pawn_priorities Growing 1 on the farmer.
Done = days_of_food >= FOOD_COMFORT_DAYS (no mark).""",
"food-rotting-or-no-cold": """LIVE: the food store is not fully roofed (store_roofed_fraction < 1).
1. game_get_cells_info over the store -> unroofed cells.
2. game_apply_architect_designator areabuildroofexpand over them; walls on interior sides only.
3. Then the cooler: freezer ~7x7, one door to the kitchen, blue in / red out, -5C.
Fallback: roof refused (no support within 6 cells) -> a wall/column inside first.
Done = store_roofed_fraction 1.0 (no mark).
Owner: "rot is rotting away still havent figured cooler /freezer and vents in rooms".""",
"rot-alert": """LIVE: something is rotting (alert_food_rot).
1. game_list_alerts: which item, where.
2. Freezer: game_set cmd stockpile_filter x z mode food priority Important.
3. The shelf it sat on: game_set cmd stockpile_filter x z mode nofood.
Fallback: filter refused -> haul it by hand (order_pawn haul) into the freezer.
Done = alert_food_rot false (no mark).
Owner: "DO YOU KNOW WHEN U SETSOME SOME EHWERRE U HAVE TO DESET IT EVERYWHERE ELSE".""",
"freezer-sorting": f"""LIVE: power and a roofed store, freezer not sorted.
1. Coolers in the freezer wall: BLUE in, RED out to open sky, one per ~12 cells, -5 to -10C.
2. game_set cmd stockpile_filter (freezer) mode food priority Important -- food, plants, healroot, ambrosia, wort.
3. Every other shelf/zone mode nofood: set one, Copy/Paste gizmo to the rest. Medicine only in the hospital.
Fallback: refused twice -> game_set cmd stockpile_camp mode food beside the stove, nofood elsewhere.
Done = mark freezer_sorted true; latch mark {latch_name('freezer-sorting')}.
Owner: "red faces outside blue inside" / "perishables only go in freezers".""",
"storage-logic": f"""LIVE: freezer sorted; the rest of storage is not.
1. Tiers: stockpiles Normal, freezer Important, shelves one tier above their room's floor zone.
2. game_set cmd stockpile_filter per store; Copy/Paste gizmo for twins.
3. Dry storage: shelves added on the N side of the existing ones.
Fallback: filter refused -> game_click_cell the shelf, set it in the storage tab.
Done = mark storage_logic true; latch mark {latch_name('storage-logic')}.
Owner: "dont just critical everything use logic chains" / "ur dry storage needs more shleves".""",
"storage-audit": """LIVE: daily audit (24 h on) and items lie unstored (loose_items_unstored > 0).
1. game_list_zones -> each store's filter vs its job.
2. Freezer goods outside the freezer, junk in it: game_set cmd stockpile_filter fix.
3. Say on stream how many you fixed.
Fallback: zone list refused -> game_get_cells_info over the stores.
Done = loose_items_unstored 0 (standing order, no mark).
Owner: "a running check list that is never complete".""",
"no-medicine": """LIVE: zero medicine.
1. healroot_plants > 0: game_apply_architect_designator Harvest on them.
2. game_set cmd crops plant Plant_Healroot (if researched); trade a caravan / comms trader.
3. Self-tend ON for everyone (game_click_cell pawn -> Health tab).
Fallback: self_tend tool missing -> click the checkbox via game_click_cell.
Done = medicine > 0 (no mark).
Owner: "those medicail red x;s need to be checked for self heal".""",
"medicine-reserve": """LIVE: medicine under MEDICINE_RESERVE for 48 h.
1. game_set cmd crops plant Plant_Healroot (colonists x 6 cells).
2. research_medicineproduction done: game_set cmd add_bill recipe MakeMedicineIndustrial count {MEDICINE_RESERVE}.
3. Minor wounds: no medicine.
Fallback: no research -> trade for medicine.
Done = medicine >= MEDICINE_RESERVE (no mark).""",
"disease": """LIVE: someone is sick (alert_sickness).
1. order_pawn <sick> rest until healed in a Medical bed.
2. game_set cmd assign pawn <sick> medicine Best; pawn_priorities <best doctor> {Doctor:1}.
3. Tend every 12 h until immune; Cleaning 2 on a pawn.
Fallback: no Medical bed -> any bed, still rest until healed.
Done = alert_sickness false (no mark).
Owner: "slect gee and tell him rest till healed in hospital bed".""",
"life-threat": """LIVE: a life-threatening hediff (alert_life_threat).
1. game_list_colonists: which pawn, which hediff.
2. game_set cmd assign pawn medicine Best; order_pawn <best doctor> tend now.
3. Severity past immunity: glitterworld medicine if any.
Fallback: doctor busy -> next best doctor; never send the doctor to the front.
Done = alert_life_threat false (no mark).""",
"needs-tend": """LIVE: a colonist needs tending, map clear.
1. order_pawn <best doctor> tend <patient>; bleeding first.
Fallback: doctor busy elsewhere -> the next best doctor.
Done = alert_needs_tend false (no mark).
Owner: "remmebr always field tnde directly brefopre cpature and haul".""",
"hospital-setup": f"""LIVE: hospital not set up (3+ colonists, electricity).
1. A room near the entrance and stores; beds owner colonist (set_bed_owner) + Medical (game_execute_gizmo).
2. Vitals monitor + IV drip beside each bed; floored, lit, 16-26C via vents.
3. Medicine shelf in the room; pawn_priorities best Medicine on Doctor 1.
Fallback: Medical gizmo refused twice -> beds by the stores, meds in main store, say the tool is missing.
Done = mark hospital_set true; latch mark {latch_name('hospital-setup')}.
Owner: "hospital is prisoner only fix that" / "vuitals a life support have to be next to beds" / "meds in hospital".""",
"cold": """LIVE: hypothermia (alert_hypotherm).
1. game_set cmd set_area pawn <each> area Home.
2. No power: campfire mid-room; power: heater at 21C.
3. game_set cmd add_bill recipe Make_Apparel_Parka count <colonists>.
Fallback: no heater/campfire placeable -> crowd pawns into the warmest roofed room.
Done = alert_hypotherm false (no mark). Never a sick pawn in an unheated hospital.""",
"heat": """LIVE: heatstroke (alert_heatstroke).
1. Pawns into roofed rooms (game_set cmd set_area pawn <each> area Home).
2. Passive coolers (wood) or powered coolers at 21C.
3. A backrooms gate open: send the crew through.
Fallback: cooler placement refused -> game_select_architect_designator + game_click_cell.
Done = alert_heatstroke false (no mark).""",
"warm-clothes": """LIVE: someone needs warm clothes (alert_warm_clothes).
1. game_set cmd add_bill recipe Make_Apparel_Parka count <colonists> (or Tuque/TribalWear).
2. Trade for clothes.
Fallback: no tailor bench -> crafting spot TribalWear.
Done = alert_warm_clothes false (no mark).""",
"shelter-night-one": f"""LIVE: day < 3, no shelter (setup-4b-shelter has not run).
1. game_set cmd unforbid; game_set cmd chop count 150.
2. game_set cmd shelter w 7 h 5; game_set cmd beds (one per colonist); campfire mid-room.
3. ladder_set mark shelter_built true.
Fallback: shelter refused (no wood) -> chop again; still refused -> sleeping spots under any roof.
Done = mark shelter_built true; latch mark {latch_name('shelter-night-one')}.
Owner: "remmeber dont go building a massive camp".""",
"beds-short": """LIVE: fewer beds than BEDS_NEEDED and a shelter stands.
1. game_set cmd beds -- one per pawn inside the shelter.
2. game_set cmd set_bed_owner x z owner colonist for each unowned bed.
Fallback: no wood -> sleeping spots now, beds when chopped.
Done = beds >= BEDS_NEEDED (no mark).
Owner: "just have to always set up everything for new pawns".""",
"hvac-clusters": f"""LIVE: AC researched, power on, HVAC not laid.
1. Clusters: hub room heater + cooler, vents to <= 3 neighbours (VENT_MAX_PER_UNIT), halls included, 21C.
2. Cooler hot side to unroofed outdoors; big rooms get more coolers.
3. ladder_set mark hvac_done true.
Fallback: build_cooler/build_vent missing -> game_select_architect_designator + game_click_cell, check rotation.
Done = mark hvac_done true; latch mark {latch_name('hvac-clusters')}.
Owner: "a ac can cool like 4 rooms, u need vents" / "not more that 3 vents to a ac and heater".""",
"work-grid-set": f"""LIVE: the work grid is not set.
1. pawn_priorities first pawn (Firefighter..Cooking 1, then custom).
2. Copy/paste that row to every other pawn, then tune (farmer, hunter, doctor). No blank cells.
3. ladder_set mark work_grid_set true.
Fallback: copy/paste refused -> pawn_priorities one call per pawn.
Done = mark work_grid_set true; latch mark {latch_name('work-grid-set')}.
Owner: "use copy paset to set defalts then change" / "no priorities shall be blank in the work tab".""",
"colony-before-research": """LIVE: research benches exist, nobody idle, while food/rot/freezer is open.
1. pawn_priorities: Research 4 for everyone until the food and storage rungs clear.
2. Say on stream what the colony needs instead.
Fallback: priorities refused -> game_set cmd set_work_priority per pawn.
Done = this rung drops (no urgent need; no mark).
Owner: "SHE JSUT RESEARCHING AT THE DESKS AND NOT DOING ANYTHING THE COLONY NEEDS".""",
"corpses-buried": """LIVE: corpses above CORPSE_LIMIT, map clear.
1. Strip first; build a grave and Bury human corpses.
2. Animal corpses to the butcher (butcher-fast).
Fallback: no grave -> a dump zone outside the wall.
Done = corpses <= CORPSE_LIMIT (no mark).""",
"kitchen-clean": f"""LIVE: kitchen not floored.
1. game_select_architect_designator a floor + game_drag_cell over the kitchen.
2. A cook with skill >= 3 on Cooking 1.
3. ladder_set mark kitchen_floored true.
Fallback: no floor material -> Cleaning 2 on a pawn until it is.
Done = mark kitchen_floored true; latch mark {latch_name('kitchen-clean')}.""",
"repair-0-reset": """LIVE: repairs finished (buildings_damaged 0).
1. ladder_set mark repairs_set false.
Fallback: none needed -- one mark write.
Done = mark repairs_set false.
Owner: "make sure ur base isnt gonna collapse death".""",
"repair-1-wait": """LIVE: buildings damaged, hostiles on the map.
Nobody walks out to repair under fire; wait (no tool call).
Fallback: a wall is breached -> combat rungs decide, not this one.
Done = hostiles_on_map 0, then repair-2-set (no mark).
Owner: "buildings damaged? set repairs if pawns safe".""",
"repair-2-set": """LIVE: damaged buildings, map safe.
1. game_apply_architect_designator Home over every damaged building.
2. game_set cmd set_work_priority pawn <builder> work Construction level 1; nothing blank.
3. ladder_set mark repairs_set true.
Fallback: Home refused -> game_set cmd set_area area Home.
Done = mark repairs_set true (repair-0-reset clears it).
Owner: "no u need to fix the whole wall".""",
"after-the-kill": """LIVE: the enemy is dead (one-shot as hostiles hit 0).
1. game_set_draft off; game_set cmd unforbid (loot, dropped gear).
2. Perishables into the freezer; areabuildroofexpand over open rooms; game_set cmd shelves.
3. Downed raiders: field tend, then capture to the prisoner bed; corpses to a dump outside.
Fallback: a step refused -> say it, do the rest; nothing new built first.
Done = ladder_set mark after_kill_done true.
Owner: "<<<do all this dirrectly after enemy kill" / "you forgot to unforbid everything thats a constant tasks".""",
}
missing = set(order) - set(P)
assert not missing, missing

# ---------------------------------------------------------------- assemble
out_rungs = []
for rid in sorted(order, key=lambda i: R[i]["priority"]):
    r = R[rid]
    r["family"] = "survival"
    out_rungs.append(r)

sensors = [{"key": "loose_items_unstored", "status": "TO_BUILD (decisions.json)", "read_by": ["storage-audit"],
            "csharp": "st[\"loose_items_unstored\"] = (double)home.listerHaulables.ThingsPotentiallyNeedingHauling().Count;  // inventory.md section C, ReadBuild, normal cadence"}]
for s in fam["sensors_needed"]:
    sensors.append({**s, "status": "proposal only: no survival rung reads it (not in decisions.json TO_BUILD)"})

result = {"family": "survival", "rungs": out_rungs, "prompts": {r["id"]: P[r["id"]] for r in out_rungs},
          "sensors_needed": sensors, "variables_needed": fam["variables_needed"],
          "missing_tools": fam["missing_tools"], "unplaced_rules": left, "notes": notes}
json.dump(result, open(os.path.join(ROOT, "families-fixed", "survival.json"), "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(out_rungs), len(result["prompts"]), len(left))
