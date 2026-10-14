import json, re, copy, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
def L(fam): return json.load(open(f"families/{fam}.json", encoding="utf-8"))
def latch_name(rid): return re.sub(r"[^a-z0-9]+", "_", str(rid).lower()).strip("_")[:35] + "_done"
src = L("base-and-fortress")
R = {r["id"]: copy.deepcopy(r) for r in src["rungs"]}
ext = {}
for fam in ("survival", "ideology-biotech-anomaly", "royalty", "backrooms", "growth"):
    for r in L(fam)["rungs"]: ext[(fam, r["id"])] = r
rules = []
for x in "abc":
    for l in open(f"owner-rules-{x}.jsonl", encoding="utf-8"): rules.append(json.loads(l))
allq = {r["quote"] for r in rules}
def Q(*qs):
    for q in qs: assert q in allq, q
    return list(qs)
def whyq(s): return re.findall(r'"([^"]+)"', s or "")
def quotes_in(s):
    out = []
    for q in whyq(s):
        if q in allq: out.append(q)
        else:
            for aq in allq:
                if len(aq) > 25 and aq in q: out.append(aq)
    return list(dict.fromkeys(out))

DELETED = {
 "hostile-on-map": "war:war-mobilize", "raid-posted": "war:war-letter-classify",
 "raid-cleanup": "survival:after-the-kill", "repair-after-raid": "survival:repair-2-set",
 "camp-wood-wall-ring": "setup:setup-7-camp-defence (build steps + quotes merge verbatim)",
 "camp-wood-wall-fallback": "setup:setup-7-camp-defence (its CTU on blueprints moves with it)",
 "hospital": "survival:hospital-setup", "freezer-cluster": "survival:food-rotting-or-no-cold"}
notes = []
for k, v in DELETED.items():
    r = R.pop(k)
    notes.append({"deleted": k, "pointer": "see " + v, "quotes_to_move_verbatim": quotes_in(r.get("why"))})

MERGED = {
 "power-every-consumer": [("survival", "power-every-consumer"), ("ideology-biotech-anomaly", "power-grid-standing")],
 "rung-2-power-and-cold": [("ideology-biotech-anomaly", "power-generators-outside"), ("royalty", "generators-out")],
 "battery-room": [("ideology-biotech-anomaly", "power-batteries")],
 "coolers-and-vents": [("ideology-biotech-anomaly", "power-ac-fridge")],
 "firebreak-ring": [("survival", "firebreak")],
 "mountain-base-plan": [("royalty", "throne-base-plan"), ("backrooms", "br-base-layout")],
 "bedrooms-owned": [("growth", "growth-private-rooms"), ("growth", "growth-private-rooms-fallback")],
 "double-bed-rooms": [("ideology-biotech-anomaly", "bio-family-rooms")],
 "storage-shelves": [("growth", "growth-shelves-everything")],
}
for rid, donors in MERGED.items():
    r = R[rid]; r.setdefault("owner_rules", []); r.setdefault("merged_from", [])
    for fam, did in donors:
        d = ext[(fam, did)]; r["merged_from"].append(f"{fam}:{did}")
        for q in quotes_in(d.get("why")):
            if q not in r["owner_rules"]: r["owner_rules"].append(q)
        for n in d.get("never", []) or []:
            r.setdefault("never", [])
            if n not in r["never"]: r["never"].append(n)
pa = copy.deepcopy(ext[("ideology-biotech-anomaly", "power-alternate")]); pa["family"] = "base-and-fortress"
pa["moved_from"] = "ideology-biotech-anomaly:power-alternate"; pa["owner_rules"] = Q("your gonna need some alternate power")
pa["when"] = dict(pa["when"]); pa["when"] = {"mark_camp_stable": True, **pa["when"]}
R["power-alternate"] = pa

S = "ladder_set mark "
R["prisoner-bed-before-fight"]["then"] = ["game_set cmd beds (one bed in the prison room)", "game_set cmd set_bed_owner x <bx> z <bz> owner prisoner", S + "prisoner_bed true"]

R["terraform-water-first"]["owner_rules"] = Q("dont forget terriforming for soil plots")
R["terraform-water-first"]["then"].insert(2, "farm plots inside the walls on sand/gravel/rock: terraform to soil the same way before sowing")

g = R["firebreak-ring"]
g["then"] = ["game_apply_architect_designator PlantsCut on the FIREBREAK_WIDTH (3) band of grass/trees around the wall and fields (game_set cmd chop for trees)",
    "smooth-marble (or stone) floor ring FIREBREAK_WIDTH (3) wide outside the wall: game_select_architect_designator the stone floor + game_drag_cell",
    "cut grass around buildings", S + "firebreak_done true", S + "firebreak_cut true"]
fq = [q for q in allq if "3wide terrriom stone smooth marble" in q]
g["owner_rules"] = list(dict.fromkeys(g.get("owner_rules", []) + fq))

g = R["rung-2-power-and-cold"]
g["latch"] = False
g["when"] = {"mark_camp_stable": True, "days_of_food": ">{FOOD_MIN_DAYS}", "medicine": ">0", "mark_power_row_built": False,
             "cancelled": {"not": {"ctu": {"mark_generator_tried": True}, "preset": 2, "reset": {"power_generators": ">=2"}}}}
g["then"] = [S + "generator_tried false",
    "research Electricity, then Air conditioning (game_set cmd add_bill is not research: use the research tab search box)",
    "wood-fired generators OUTSIDE the rooms but INSIDE the defended wall, in ONE generator yard with the batteries, unroofed (remove-roof area to vent heat), away from the throne entrance hall",
    "game_select_architect_designator WoodFiredGenerator; game_click_cell each slot of the row; never cancel the blueprint",
    "generators already standing in the middle of a room: select -> Reinstall gizmo -> place in the yard (crowded cell: click until the inspect text names it)",
    "conduit as ONE continuous string from the yard to every consumer (link range 6 tiles)",
    "a powered cooler in the food room wall, blue side in, red side OUTSIDE",
    "standing lamps replace torches, LAMPS_PER_ROOM per room",
    "a placement refused or cancelled: " + S + "generator_tried true (2 -> power-generators-fallback asks the owner)",
    "power_generators >= 2 and has_power true: " + S + "power_row_built true"]
R["power-generators-fallback"] = {"id": "power-generators-fallback", "family": "base-and-fortress", "priority": 0,
    "when": {"mark_power_row_built": False, "cancelled": {"ctu": {"mark_generator_tried": True}, "preset": 2, "reset": {"power_generators": ">=2"}}},
    "then": ["reply_owner: generator placement keeps cancelling, one mouse pass on the generator yard row please", "unity_say a clean line to chat: waiting on one hand-placed generator row"],
    "never": ["retry the same placement a third time"], "latch": True,
    "why": "moved from ideology-biotech-anomaly:power-generators-fallback (decisions: power chain owned here; CTU fallback on the generator placement)",
    "owner_rules": Q("u never did your generators youd place them then jsut cancle their palcement"),
    "merged_from": ["ideology-biotech-anomaly:power-generators-fallback"]}

g = R["power-every-consumer"]; g["latch"] = False
g["when"] = {"mark_camp_stable": True, "has_power": True, "unpowered_consumers": ">0"}
g["then"] = ["game_get_cells_info round each unpowered building to find the nearest conduit",
    "game_select_architect_designator PowerConduit (HiddenConduit inside rooms) + game_drag_cell a single run to it; never leave an island or a string that ends in nothing",
    "one grid; read each heater/cooler grid line", "re-read unpowered_consumers next pass", "unpowered_consumers 0: " + S + "power_wired true"]
R["power-generation-margin"]["when"] = {"mark_camp_stable": True, "has_power": True, "power_margin_pct": "<125"}
g = R["battery-room"]
g["when"] = {"mark_camp_stable": True, "has_power": True, "mark_battery_room_done": False, "research_batteries": True}
g["then"] = ["a stone-walled, stone-floored, ROOFED battery room beside the generator yard, away from bedrooms and stockpiles",
    "batteries in rows with a 1-wide aisle so every battery has a path; game_select_architect_designator Battery; game_click_cell per slot",
    "conduit under every battery so the draw is shared, not tied to one battery; banks split by power switches",
    S + "battery_room_done true"]
g = R["coolers-and-vents"]
g["when"] = {"mark_camp_stable": True, "has_power": True, "research_airconditioning": True, "rooms_out_of_temp": ">0"}
g["then"] += ["freezer: cooler in the freezer wall, blue side in (rotate with Q x2), set to FREEZER_TARGET_C (MISSING set_cooler_target: open the cooler and click the temperature arrows)",
    "coolers on a narrow room (morgue freezer) go on the side that faces outdoors so they push heat outside"]
g["owner_rules"] += Q("u need to move those two cooler on the morgue freezer to east side of that narro room so they ppush outside correctly")
R["electric-lights"]["when"] = {"mark_camp_stable": True, "has_power": True, "torch_lamps": ">0"}

R["rung-3-defence"]["when"] = {"mark_camp_stable": True, "days_of_food": ">{FOOD_MIN_DAYS}", "has_power": True}
R["perimeter-hole"]["when"] = {"mark_camp_stable": True, "wall_gaps": ">0"}
R["perimeter-hole"].pop("note", None)
R["perimeter-hole"]["then"].append("fix the whole wall, not part of it: walk the full ring after each patch")
R["perimeter-hole"]["owner_rules"] = Q("no u need to fix the whole wall")
R["fortress-ring"]["when"] = {"mark_rung_3_defence_done": True, "defences_built": True, "embrasures": "<{EMBRASURE_TARGET}"}
R["turret-line"]["when"] = {"mark_rung_3_defence_done": True, "has_power": True, "turrets": "<{TURRET_TARGET}", "steel": ">{STEEL_RESERVE}", "research_gunturrets": True}
R["defense-3-turrets"]["when"] = {"mark_rung_3_defence_done": True, "has_power": True, "turrets": "<{TURRET_TARGET}", "mark_defense_secure": False}
R["stone-blocks-bench"]["when"] = {"mark_camp_stable": True, "mark_stonecutter_set": False, "research_stonecutting": True}
g = R["bedrooms-owned"]
g["when"] = {"mark_camp_stable": True, "colonists_without_bedroom": ">0"}
g["then"] = g["then"] + ["in the mountain base: one private room per colonist, interior >= 2x3, smoothed stone floor/walls, aim impressiveness >= 30",
    "rooms refused: game_set cmd shelter w 3 h 4 + beds now, real rooms later"]
g = R["double-bed-rooms"]
g["when"] = {"mark_mountain_base_done": True, "colonists": ">=4", "mark_double_rooms_set": False}
g["then"] = ["game_list_colonists: adults 18+ only",
    "private stone rooms inside the wall (game_set cmd rooms), a double bed each (game_select_architect_designator DoubleBed + game_click_cell)",
    "game_set cmd set_bed_owner x z owner=<partner> for both partners of each adult couple; swap partners between rooms over time",
    "milk, cribs and toys before births (ideology-biotech-anomaly:bio-milk-pen / bio-child-care read mark_double_rooms_set)",
    S + "double_rooms_set true"]
g["never"] = list(dict.fromkeys(g.get("never", []) + ["romance, pairing, double beds or concubines for anyone under 18, whatever the ideoligion allows"]))
g["owner_rules"] = list(dict.fromkeys(Q(
    "cant have kids until u build privet rooms with double beds and set them to sleep there. can swap em in and out till all, one guy can knock up[ many",
    "kids need milk and cribs and toys", "duble beds to start families", "mix an match need soldier born") + g.get("owner_rules", [])))
g = R["storage-shelves"]
g["when"] = {"mark_camp_stable": True, "loose_items_unstored": ">20"}
g["then"] = ["game_set cmd shelves in the dry store (add another shelf row directly on the N side of the existing ones, and fill the missing ones)",
    "configure ONE shelf (game_set cmd stockpile_filter), then its copy button and paste to the rest",
    "warehouses Normal, freezer Important, workstation shelves Preferred",
    "game_set cmd set_work_priority work Hauling level 2 on the lowest-skill pawns",
    "saying 'storage' is not placing it: place it this pass"]
g["owner_rules"] = list(dict.fromkeys(Q("ur dry storage needs more shleves", "add another shelfe N side of existing ones directly", "and missing ones",
    "ur dry storage needs more shleves / add another shelfe N side of existing ones directly / and missing ones",
    "shes mentioned storage like 10 times and hasnt placed a storage yet, are you seeing this,, this is the shit you are to be monitoring for",
    "u can set one and use copy button to paste it to other shelves with paste", "full base storage logic rewaork and maintain") +
    [q for q in allq if q.startswith("use proper prioritys normal on all places like stockpiles")] + g.get("owner_rules", [])))
R["flooring-by-purpose"]["when"] = {"mark_camp_stable": True, "has_power": True, "unfloored_room_cells": ">0"}
R["dining-room"]["when"] = {"mark_camp_stable": True, "mark_dining_done": False, "day": ">=3"}
g = R["prison-wing"]
g["when"] = {"mark_mountain_base_done": True, "mark_prison_wing_done": False}
g["then"].insert(0, "a prison hold can be an existing walled room: sleeping spot in it, storage moved to where the table and chairs were (move benches if needed)")
g["owner_rules"] = Q("nmake that sotrage room a prison hold toss in a spot and put the storage where the table and chairs are might have to move benches, compelte evertthing ive sdaid")
g = R["finish-before-new"]
g["when"] = {"mark_camp_stable": True, "blueprints": ">0", "unfinished_hold": {"ton": {"blueprints": ">0"}, "hours": 24}}
g["owner_rules"] = Q("something is wrong u are clicking a million times in a row and it looked weird on steeam",
    "something is wrong u are clicking a million times in a row and it looked weird on steeam / sounds spammy, warn viewers for shit before like that",
    "talk come on NEVER FUCKING IGNORE CHAT TELL THEM IF U HAVE TO PROCESS SOMETHING GIVE TO BARE WITH YOU", "upgrade build shit you need")
g = R["walls-halls-roofs"]
g["when"] = {"mark_camp_stable": True, "room_wall_holes": ">0"}
g["then"] = g["then"] + ["halls 3 wide, never 1; rooms hang off halls with proper pathing; cross halls, no mile-long corridors; uniform rooms; anything can be moved or redone"]
g["owner_rules"] = Q("your base sucks you are a shitty achitect",
    "you build it as you play i mena shit make some goals not some indefencable narrow halled peice of shit",
    "you have to continue halls and shit u cnat just attach rooms to a fucking straightr other room u need appropriate pathing",
    "dont forget cros paths dont want mile long corridors and need vents and lights and furnature for beds",
    "dont make single widthc halways quickly redo that",
    "and archetecture archetuecture look shit up if u need to u can move walss and shit anywehere to fill holes and fix building layout to anything at all you can completely redo it to make it your dream hive for your peoples",
    "come on archeteture archeteture fix your archetecture completely door in correct place no blocked pathing walls complete embrasure fixed and powered , nothing without power need one power gen place not spead all over and not not organized",
    "and you need make a straight wall north of edge wall of the alter room", "u got double doors side ways one path thinck",
    "comew on your base sucks think industrial facility designer and archetect, get shit finished up")
g = R["furniture-tight-and-uniform"]
g["when"] = {"mark_mountain_base_done": True}
g["then"] = g["then"] + ["recreation (horseshoes pins) against a wide wall, keeping at least one interaction cell unblocked"]
g["owner_rules"] = Q("you need to put horse shoes up against wide wall so action area isnt clicked need at minimum one action area unblocked")
g = R["rung-5-the-mountain-base"]
g["then"] = ["unity_say a clean line first: what the build is and that it takes a minute (bulk jobs are announced, never silent)",
    "mine the cutout: ONE door in (MOUNTAIN_DOORS_IN), never pierce the outer rock",
    "the door opens into the throne room centred on the SPINE_WIDTH (3) spine running NE; prison wing hall east, guest wing hall west",
    "labs and tech deeper in; ROCK_CELLS_AROUND_ROOMS (2) of natural rock between every room, neighbour and the outside (room for the room wall without breaking the exposed mountain)",
    "a rock pillar or column every 5-6 tiles in big halls; fields, solar and wind outside under sky",
    "move the natural gate into a sealed laboratory at the back (later)",
    "sealed (one door in, wall_gaps 0) and days_of_food > FOOD_COMFORT_DAYS: " + S + "mountain_base_done true"]
g["owner_rules"] = Q("your gonna have to mine alot nothing is exposed struture out side the mountina walls and plan for the intoer rooms wall too so 2x mountain space along all inrteror warooms / on exterior maountain walls bunped up to rooms / need 2 so u have rrom for you room wall with out breaking the exposed mountain",
    "on exterior maountain walls bunped up to rooms", "need 2 so u have rrom for you room wall with out breaking the exposed mountain")
g = R["mountain-base-plan"]
g["then"] = [S + "plan_needed true",
    "game_take_screenshot of the natural mountain cut-out; plan there: one door into the mountain, never pierce the edge from inside",
    "game_select_architect_designator Plan; game_drag_cell the districts with real floor plans (facility/massive lab, secure prison, office, factory, homes), mirrored symmetry in the overall composition, not a grid",
    "entrance door straight into the throne room on the 3-wide spine; east hall to the prison wing, west hall to the guest wing, kept separate; labs/tech deeper; dissection rooms behind the security embrasure halls",
    "altar room in the offset area west of the throne room; one generator area with the batteries, away from the throne entrance hall",
    "planting areas in the existing cut-out mountain areas to the SE (terraform/smooth the rock); king's chambers, moral guide's room, drug lab, party room, vault, hospital, bedrooms, guest quarters, landing pad",
    "bastions: half-rooms against the inside of the wall, embrasures on all sides, at every corner and both sides of every entrance; monolith in the footprint: game_execute_gizmo Uninstall, reinstall outside",
    "note the plan cells (note tool)", S + "throne_plan_done true", S + "mountain_plan_done true"]

def norm(s):
    s = re.sub(r"ladder_set op mark name (\w+) value (\w+)", r"ladder_set mark \1 \2", s)
    return re.sub(r"op=mark name=(\w+) value=(\w+)", r"ladder_set mark \1 \2", s)
for r in R.values():
    r["family"] = "base-and-fortress"; r["then"] = [norm(s) for s in r["then"]]
    r.setdefault("owner_rules", [])
    if r.get("latch"): r["done_mark"] = latch_name(r["id"])
    else: r.pop("done_mark", None)

order = sorted([rid for rid in R if rid not in ("prisoner-bed-before-fight", "mine-before-wall", "perimeter-hole")],
               key=lambda i: {"power-alternate": 22.15, "power-generators-fallback": 20.05}.get(i, R[i]["priority"]))
R["prisoner-bed-before-fight"]["priority"] = 1.8; R["mine-before-wall"]["priority"] = 15.0; R["perimeter-hole"]["priority"] = 15.02
for n, rid in enumerate(order): R[rid]["priority"] = round(15.10 + 0.12 * n, 2)
pr = [r["priority"] for r in R.values()]; assert len(pr) == len(set(pr)) and max(pr) <= 19.99

P = json.load(open("_scripts/base_prompts.json", encoding="utf-8"))
for k, v in P.items(): assert len(v) <= 12, k
assert set(P) == set(R), (set(P) ^ set(R))

placed_blob = json.dumps(list(R.values()), ensure_ascii=False) + json.dumps(P, ensure_ascii=False)
KEEP = []
for u in src["unplaced_rules"]:
    if u["quote"] in placed_blob or u["quote"] in [k["quote"] for k in KEEP]: continue
    ql = u["quote"]
    why = ("economy (harvest/sow)" if "HARVET" in ql else "setup:setup-2-pawns / setup-9-new-pawn (work grid, new pawn setup)" if ("priorities" in ql or "REV" in ql)
           else "meta / start (world generation, storyteller)" if ("procedd" in ql or "community" in ql or "no wood" in ql)
           else "meta (goals / NOW.md)" if "test items" in ql else "meta (stream, overlay, webcam, chat, persona)")
    KEEP.append({"quote": u["quote"], "rule": u["rule"], "reason": "not a base build lever; belongs to " + why})
for r in rules:
    if r["family"] == "base-and-fortress" and r["quote"] not in placed_blob and r["quote"] not in [k["quote"] for k in KEEP]:
        ql = r["quote"]
        fam = ("setup:setup-1-explore (explore every door)" if "exploring" in ql else "economy (harvest/sow)" if "HARVET" in ql
               else "economy/survival (sowing) + setup:setup-2-pawns (work grid)" if "soeing" in ql
               else "setup:setup-2-pawns / configuration (work grid)" if "priorities" in ql else "meta (stream/overlay/chat)")
        KEEP.append({"quote": r["quote"], "rule": r["rule"], "reason": f"not a base build lever; belongs to {fam}"})

CS_SNIP = json.load(open("_scripts/base_sensors_cs.json", encoding="utf-8"))
def keys(w):
    for k, v in (w or {}).items():
        if isinstance(v, dict):
            for b in v.get("any", []) or []: yield from keys(b)
            for op in ("ton", "tof", "ctu", "ons", "not", "reset"):
                sub = v.get(op)
                if isinstance(sub, dict):
                    if any(o in sub for o in ("ton", "tof", "ctu", "ons", "not", "any")): yield from keys({"_": sub})
                    else: yield from keys(sub)
        else: yield k
used = set()
for r in R.values(): used |= set(keys(r["when"]))
sensors_needed = [{"key": k, "status": "TO_BUILD", "csharp": CS_SNIP[k], "where": "Sensors.ReadBuild (inventory.md section C), normal cadence"} for k in sorted(used) if k in CS_SNIP]

out = {"family": "base-and-fortress", "rungs": sorted(R.values(), key=lambda r: r["priority"]),
       "prompts": {k: "\n".join(v) for k, v in P.items()}, "sensors_needed": sensors_needed,
       "variables_needed": src["variables_needed"], "missing_tools": src["missing_tools"],
       "unplaced_rules": KEEP, "notes": notes + [
         "mine-before-wall and terraform-water-first read no stage mark on purpose: they stop a pawn being walled into rock / a wall on water at any stage, camp included.",
         "power-generators-fallback moved in from ideology-biotech-anomaly:power-generators-fallback; its CTU input mark_generator_tried is set true by rung-2-power-and-cold on a refused/cancelled placement and cleared at the start of each pass, so every refusal is a rising edge.",
         "rung-2-power-and-cold is no longer latched (a latch would end it after one refused pass); its done mark is power_row_built.",
         "mountain-base-plan also sets throne_plan_done (royalty:throne-room / royal-vault read it; royalty:throne-base-plan merged here).",
         "main_base_started is not set: its only reader (ideology-biotech-anomaly:bio-family-rooms) is deleted per decisions.marks.",
         "loose_items_unstored threshold is the literal 20 (LOOSE_ITEMS_MAX is not in the tag table)."]}
json.dump(out, open("families-fixed/base-and-fortress.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(R), len(P), len(sensors_needed), len(KEEP), sorted(used))
