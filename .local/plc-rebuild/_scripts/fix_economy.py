import json, re, copy
B = r"C:/Users/gfour/Desktop/Backrooms/.local/plc-rebuild/"
e = json.load(open(B + "families/economy.json", encoding="utf-8"))


def latch_name(rid):
    return re.sub(r"[^a-z0-9]+", "_", str(rid).lower()).strip("_")[:35] + "_done"


DELETE = {"econ-freezer-shelves": "survival:freezer-sorting",
          "econ-freezer-fallback": "survival:freezer-sorting",
          "econ-butcher": "survival:butcher-table"}
notes, moved = [], {}
for r in e["rungs"]:
    if r["id"] in DELETE:
        qs = list(dict.fromkeys(re.findall(r'"([^"]+)"', r.get("why", ""))))
        moved[r["id"]] = {"see": DELETE[r["id"]], "owner_rules_to_move_verbatim": qs,
                          "steps_to_merge": r["then"], "never": r.get("never", [])}
        notes.append("see %s (was economy:%s)" % (DELETE[r["id"]], r["id"]))
notes.append("see economy:trade-run (space:space-trade-comms and space:space-trade-comms-fallback point here)")

orig_index = {r["id"]: i for i, r in enumerate(e["rungs"])}
rungs = [copy.deepcopy(r) for r in e["rungs"] if r["id"] not in DELETE]
R = {r["id"]: r for r in rungs}

# ---- when fixes
R["econ-druglab"]["when"] = {"mark_production_running": True, "research_drugproduction": True,
                             "count_druglab": "<1", "mark_druglab_set": False}
R["crops-full-set"]["when"] = {
    "mark_camp_stable": True, "growing_cells": ">0", "days_of_food": ">{FOOD_COMFORT_DAYS}", "mark_crops_full": False,
    "tries": {"not": {"under_3": {"ctu": {"mark_crops_tried": True}, "preset": 3, "reset": {"mark_crops_full": True}}}}}
R["econ-crops-fallback"]["when"] = {
    "mark_camp_stable": True, "mark_crops_full": False,
    "tries": {"ctu": {"mark_crops_tried": True}, "preset": 3, "reset": {"mark_crops_full": True}}}
R["econ-trader-arrived"]["when"] = {"arrival": {"ons": {"trader_letter": {"any": [
    {"letter_matches": "trader"}, {"letter_matches": "caravan"}]}}}}
R["econ-guest-beds-full"]["when"] = {"mark_guests_set": True,
                                     "full": {"ons": {"letter_matches": "not enough guest beds"}}}
R["rung-4-production"]["when"] = {"mark_camp_stable": True, "days_of_food": ">{FOOD_COMFORT_DAYS}",
                                  "has_power": True, "defences_built": True, "mark_crops_full": True}
for rid in ("comms", "trade-run", "econ-silver-company", "components-low", "econ-wealth-junk",
            "econ-money-to-security", "supply-steel-1-buy", "supply-steel-2-mine",
            "supply-weapons-1-sell", "supply-weapons-2-smelt", "econ-wood-winter"):
    R[rid]["when"] = dict([("mark_camp_stable", True)] + list(R[rid]["when"].items()))
R["econ-money-to-security"]["when"]["mark_mountain_base_done"] = True

# ---- then fixes
R["crops-full-set"]["then"] = [
    "ladder_set mark crops_tried false",
    "game_set cmd crops",
    "game_set cmd set_zone_plant x,z plant=<one per zone>: Plant_Berry, Plant_Potato, Plant_Corn, Plant_Healroot (grower Plants >= 8), Plant_Cotton, Plant_Smokeleaf, Plant_Psychoid, Plant_Hops, then every other crop as research unlocks it",
    "on a refused set_zone_plant: ladder_set mark crops_tried true (3 refusals hand over to econ-crops-fallback)",
    "re-read fields_all_default_crop: must be false",
    "when fields_all_default_crop is false: ladder_set mark crops_full true"]
R["econ-crops-fallback"]["then"] = [
    "ladder_set mark crops_tried false",
    "game_get_cell_info on one cell of each growing zone: read the plant and allowed plants",
    "game_set cmd set_zone_plant with that exact defName",
    "on a refused set_zone_plant: ladder_set mark crops_tried true",
    "ladder_set mark crops_full true"]
R["econ-checklist"]["then"] = R["econ-checklist"]["then"] + [
    "for a latched economy rung whose sensor fell back, clear its own mark AND its done-latch (e.g. ladder_set mark stockpiles_sized false + ladder_set mark stockpiles_sized_done false)",
    "when mark_mountain_base_done is true and colonists >= {ENDGAME_COLONISTS} and silver >= {EMPIRE_SILVER} and research_multianalyzer is true: ladder_set mark empire_ready true"]
R["rung-4-production"]["then"] = R["rung-4-production"]["then"] + [
    "ladder_set mark %s true" % latch_name("rung-4-production")]
R["econ-trader-arrived"]["then"][0] = 'read the letter now (game_state letters); letter_matches "trader" / "caravan"'

# ---- owner quotes placed verbatim
Q_DUMP = "get that dead body and chuncks out you should be doing this shit by now where is your freexzer shelves torages sized for expansion / and remember you dont want visitors walking through you labratory you want them in the zone gor guestss and shops with in your protected base"
Q_CASH = "start growing cash crops / what can u doi to make the next visitors happier with their stay beauty better food sales of goods have to set a sell zone and use guests tab and only sell what u dont need like smoneleaft on its higher process"
Q_FIELDS = "put famrs out side the walls when u get to it / need berrys potatos corn and healroot minimum plus cotton smoke leaf psycoid and hops so lots to sell and production / items as u unlock"
Q_FREEZER = "you still havent started growing cash crops and you still havent figured out you freezer storage as ive already told you how , you have shelfs outside the freezer set to hold freezer goods and good in the freezer not ment to be frozen, i already told you how to set up the shelves and zones, do it"
extra = {"econ-dump-zone": [Q_DUMP], "rung-4-production": [Q_CASH], "guest-wing": [Q_CASH, Q_DUMP],
         "econ-fields-outside": [Q_FIELDS], "crops-full-set": [Q_FREEZER, Q_CASH]}
for rid, qs in extra.items():
    for q in qs:
        if '"%s"' % q not in R[rid]["why"]:
            R[rid]["why"] += ' / owner: "%s"' % q

# ---- priorities: economy band 20.00-24.99, old relative order, no ties
order = sorted(rungs, key=lambda r: (float(r["priority"]), orig_index[r["id"]]))
step = min(0.12, round(4.99 / (len(order) - 1) - 0.005, 2))
for i, r in enumerate(order):
    r["priority"] = round(20.0 + i * step, 2)
rungs = order

for r in rungs:
    r["owner_rules"] = list(dict.fromkeys(re.findall(r'"([^"]+)"', r.get("why", ""))))
    r["latch"] = bool(r.get("latch"))
    if r["latch"]:
        pass
    else:
        r.pop("done_mark", None)

# ---- prompts
P = {k: v for k, v in e["prompts"].items() if k not in DELETE}
P["crops-full-set"] = "\n".join([
    "FULL CROP SET (after camp_stable). Look first: fields_all_default_crop, growing_cells, the plant in each zone.",
    "0. ladder_set mark crops_tried false.",
    "1. game_set cmd set_zone_plant x,z plant=Plant_Berry / Potato / Corn / Healroot / Cotton / Smokeleaf / Psychoid / Hops, one zone each.",
    "2. Re-read fields_all_default_crop: false.",
    "Fallback: a plant refused -> ladder_set mark crops_tried true; 3 refusals -> econ-crops-fallback.",
    "Done = ladder_set mark crops_full true.",
    'Owner: "need psycoid and hops too, you dont need two crops of smokeleaf" / "fidure it our ur not sleecting crops right" / "start growing cash cropsa"'])
P["econ-crops-fallback"] = "\n".join([
    "CROPS FALLBACK (set_zone_plant refused 3 times).",
    "0. ladder_set mark crops_tried false.",
    "1. game_get_cell_info on each zone; read the exact plant defName.",
    "2. game_set cmd set_zone_plant with it.",
    "Fallback: refused again -> ladder_set mark crops_tried true, name the zone on stream.",
    "Done = ladder_set mark crops_full true.",
    'Owner: "fidure it our ur not sleecting crops right"'])
P["rung-4-production"] = "\n".join([
    "PRODUCTION (stage 3). Look first: bill_rows, count_beer, count_smokeleafjoint, count_psychitetea, cloth.",
    "1. game_set cmd add_bill for beer, joints, tea, clothes, stone blocks, Do until PRODUCT_BILL.",
    "2. game_set cmd set_work_priority Crafting 2 / Tailoring 2 on a free pawn.",
    "Fallback: add_bill refuses -> bench missing or recipe locked; skip it, name it on stream.",
    "Done = ladder_set mark production_running true; the latch sets rung_4_production_done (the base family waits on it).",
    'Owner: "lots to sell and production" / "set amounts higher and higher as your base grows" / "only sell what u dont need like smoneleaft on its higher process"'])
P["econ-checklist"] = "\n".join([
    "DAILY ECONOMY CHECK. Look first: bill_rows, fields_all_default_crop, stockpile_cells, silver, colonists.",
    "1. A job whose sensor fell back: ladder_set its mark false AND its <id>_done latch false.",
    "2. mark_mountain_base_done + colonists >= ENDGAME_COLONISTS + silver >= EMPIRE_SILVER + research_multianalyzer: ladder_set mark empire_ready true.",
    "Fallback: a sensor unmeasured -> leave that mark alone.",
    "Done = every economy sensor at level (standing check, no mark).",
    'Owner: "maintain everything in totality ive evr told you" / "evrything in the game is fair game get to it"'])
P["econ-wood-reset"] = "\n".join([
    "WOOD RESET. Look first: wood vs WOOD_RESERVE.",
    "1. ladder_set mark wood_short_set false.",
    "Fallback: none needed (a mark write).",
    "Done = wood_short_set false; econ-wood-winter can fire again.",
    'Owner: "got to gain meore any means available"'])
P["econ-components-reset"] = "\n".join([
    "COMPONENTS RESET. Look first: components vs COMPONENT_RESERVE.",
    "1. ladder_set mark components_short_set false.",
    "Fallback: none needed (a mark write).",
    "Done = components_short_set false; components-low can fire again.",
    'Owner: "maintain everything in totality ive evr told you"'])
P["econ-trade-reset"] = "\n".join([
    "TRADE RESET. 72 h since trade_run_done went true.",
    "1. ladder_set mark trade_run_done false.",
    "Fallback: none needed (a mark write).",
    "Done = trade-run can fire again.",
    'Owner: "calling traders selling all ur junk and crap u dont need"'])
P["econ-trader-arrived"] = P["econ-trader-arrived"].replace("TRADER ARRIVED (one scan).", "TRADER ARRIVED (one scan, letter_matches trader/caravan).")
P["econ-dump-zone"] += '\nOwner: "and remember you dont want visitors walking through you labratory you want them in the zone gor guestss and shops with in your protected base"'
P["guest-wing"] += '\nOwner: "have to set a sell zone and use guests tab and only sell what u dont need"'
P["econ-fields-outside"] = P["econ-fields-outside"].replace('"items as u unlock"', '"items as u unlock" / "need berrys potatos corn and healroot minimum plus cotton smoke leaf psycoid and hops"')
P["econ-guest-beds-full"] = P["econ-guest-beds-full"].replace("Done = no", "Fallback: set_bed_price missing -> build the bed, name the price on stream.\nDone = no")
P["econ-art"] = P["econ-art"].replace("Done =", "Fallback: no sculpting table -> build one (TableSculpting) first.\nDone =")
P["econ-marble"] = P["econ-marble"].replace("Done =", "Fallback: no marble on the map -> trade-run buys it.\nDone =")
P["econ-wealth-junk"] = P["econ-wealth-junk"].replace("Done =", "Fallback: no smelter -> sell the rest at the next trader.\nDone =")
P["components-low"] = P["components-low"].replace("Done =", "Fallback: no fabrication research -> buy at the next trader.\nDone =")
P["econ-money-to-security"] = P["econ-money-to-security"].replace("MONEY TO SECURITY.", "MONEY TO SECURITY (after the mountain base).")
for r in rungs:
    if r["latch"]:
        ln = latch_name(r["id"])
        if ln not in P[r["id"]]:
            P[r["id"]] = re.sub(r"(Done = [^\n]*)", lambda m: m.group(1).rstrip(".") + " (latch %s)." % ln, P[r["id"]], count=1)
for k, v in P.items():
    assert len(v.splitlines()) <= 12, k
    for w in ("Done", "Owner", "Fallback"):
        assert w in v, (k, w)

sn = [dict(s, status="PROPOSED (not in decisions.json TO_BUILD; no fixed rung reads it)")
      for s in e["sensors_needed"] if s["key"] != "defnames_to_verify"]
sn.append({"key": "defnames_to_verify", "status": "CHECK",
           "how": "count_druglab (was count_drug_lab), count_tablesculpting, count_blocksmarble, research_drugproduction, research_microelectronicsbasics, research_multianalyzer, research_brewing, research_fabrication, research_deepdrilling: confirm defNames in-game"})
out = {"family": "economy", "rungs": rungs, "prompts": {r["id"]: P[r["id"]] for r in rungs},
       "sensors_needed": sn,
       "variables_needed": e["variables_needed"] + [
           {"name": "EMPIRE_SILVER", "value": "4 * TRADE_SILVER_MIN", "rule": "decisions.json progression: empire_ready needs silver >= EMPIRE_SILVER (new tag)"},
           {"name": "ENDGAME_COLONISTS", "value": "as defined by the endgame family", "rule": "shared tag; read by the econ-checklist empire_ready step"}],
       "missing_tools": e["missing_tools"],
       "unplaced_rules": [],
       "notes": notes,
       "moved_to_other_families": moved,
       "fix_log": [
           "deleted econ-freezer-shelves, econ-freezer-fallback -> survival:freezer-sorting; econ-butcher -> survival:butcher-table (decisions chains); quotes/steps listed under moved_to_other_families for the survival fixer",
           "priorities re-banded into 20.00-24.99 in old relative order, step %.2f, no ties" % step,
           "count_drug_lab -> count_druglab; letter_labels '~x' -> letter_matches 'x'",
           "illegal shapes fixed: not{ctu,preset,reset} and ons{any} wrapped in a label",
           "ctu input mark_crops_attempt -> mark_crops_tried: set true on a refused set_zone_plant, false at the start of each attempt, in both crops rungs",
           "stage interlock: mark_camp_stable on crops-full-set onward (alarms, resets, trader/quest events excepted); rung-4-production latch writes rung_4_production_done",
           "econ-checklist sets mark_empire_ready (decisions progression)",
           "owner_rules filled from each rung's why; 3 combined section-6 / owner-rules-b quotes placed verbatim"]}
json.dump(out, open(B + "families-fixed/economy.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(rungs), len(out["prompts"]), step)
