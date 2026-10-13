"""Label, group, explain and set the warning rule of every RimPLC sensor (docs/playbook.gates.json "sensors").

Owner, 2026-10-13: "pawn with out a wepaon is a very high rankeing need to fix just like the other hundred and hundreds of
sensores need to wewarn properly and be diplayed well organized and formated with in game tool tip explinations".

Each row: key -> (group, label, warn, severity, tip). warn is when the reading is a PROBLEM (">0", "<3", "==0", or a
boolean the value equals). severity: critical (RimWorld's alert column + red), warning (amber in the window), info.
Re-run after adding sensors:   python tools/annotate-sensors.py   (then: python tools/rimplc-check.py --emit)
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.join(ROOT, "docs", "playbook.gates.json")

C, W, I = "critical", "warning", "info"
T = {
    # ---- threats
    "hostiles_on_map": ("Threats", "Hostiles on the map", ">0", C, "Active enemies on the home map. Draft, post the crew behind cover, ranged first."),
    "hostile_threat": ("Threats", "Hostile threat active", True, C, "The game says an active threat is on the map right now."),
    "hostile_pawns_listed": ("Threats", "Hostile pawns", ">0", W, "Hostile pawns the colonist list shows."),
    "threat_letter": ("Threats", "Threat letter (2 days)", True, W, "A raid or threat letter arrived in the last 2 days: prepare before contact, prisoner bed first."),
    "fight_ratio": ("Threats", "Shooters per enemy", "<1", W, "Armed, able colonists divided by hostiles. Under 1 means fall back to a defended spot."),
    "danger_animals_near": ("Threats", "Dangerous animals", ">0", W, "Bears, thrumbos, elephants and the like on the map. Never hunt them with fewer than 3 rifles."),
    "fire_cells": ("Threats", "Fire", ">0", C, "Cells on fire on the home map. Firefight now."),
    "mental_break": ("Threats", "Mental break", True, C, "A colonist is in a mental break."),
    "humanlikes_not_ours": ("Threats", "Outsiders on the map", ">0", I, "Visitors, traders or raiders that are not colonists or prisoners."),
    "empire_hostile": ("Threats", "Empire hostile", True, W, "The Empire faction is hostile."),
    # ---- health
    "downed_count": ("Health", "Downed colonists", ">0", C, "Colonists lying downed. Rescue and tend them."),
    "pawn_bleeding": ("Health", "Someone is bleeding", True, C, "A colonist is bleeding. Tend now, before they bleed out."),
    "colonist_hurt": ("Health", "Someone is hurt", True, W, "A colonist has injuries."),
    "needs_tend_count": ("Health", "Need tending", ">0", W, "Colonists with an untended injury or illness."),
    "lowest_mood": ("Health", "Lowest mood", "<0.35", W, "The unhappiest colonist's mood (0-1). Under 0.35 risks a mental break: recreation, food, comfort."),
    "medicine": ("Health", "Medicine", "==0", C, "Medicine in storage. Zero means tends are weak and infections kill."),
    # ---- crew
    "colonists": ("Crew", "Colonists", "<3", W, "Free colonists. Fewer than 3 is a fragile colony: recruit."),
    "unarmed_colonists": ("Crew", "Unarmed colonists", ">0", C, "Colonists able to fight but holding no weapon. Owner: an unarmed pawn is top priority. Run empire_pass."),
    "pawns_without_sidearm": ("Crew", "No melee sidearm", ">0", W, "Fighters with no melee weapon carried. Rifle primary, baton or knife as sidearm."),
    "able_shooters": ("Crew", "Able to fight", "==0", W, "Colonists not downed, dead or in a mental break."),
    "able_shooters_armed": ("Crew", "Able and armed", "==0", C, "Colonists able to fight AND holding a weapon."),
    "colonists_without_armor": ("Crew", "No armour", ">0", I, "Colonists with little sharp armour. Flak or plate once production allows."),
    "flee_hostility_count": ("Crew", "Set to flee", ">0", W, "Colonists whose hostility response is not Attack. Owner: attack, not flee."),
    "drafted_count": ("Crew", "Drafted", ">0", I, "Colonists currently drafted."),
    "colonists_without_bedroom": ("Crew", "No bedroom", ">0", W, "Colonists without their own bed in a room."),
    "pawns_sharing_bedroom": ("Crew", "Sharing a bedroom", ">0", I, "Colonists sleeping in a barracks."),
    "children": ("Crew", "Children", ">0", I, "Children in the colony: cribs, toys, schooling."),
    "lovers_unmarried": ("Crew", "Unmarried couples", ">0", I, "Lover couples not married yet."),
    "prisoners": ("Crew", "Prisoners", ">0", I, "Prisoners: set Recruit and a warden."),
    "best_plants_skill": ("Crew", "Best plants skill", "<6", I, "The best grower's Plants skill. Low skill fails harvests."),
    "researchers_only_research": ("Crew", "Research-only pawns", ">0", W, "Colonists doing nothing but research. Colony work comes first."),
    "grid_matches_plan": ("Crew", "Work grid as planned", False, W, "Firefight to Cook at 1 for everyone, nothing they can do left at 0."),
    "new_joiners": ("Crew", "New joiners", ">0", I, "Twitch viewers who joined and were not greeted yet (stream)."),
    # ---- food
    "days_of_food": ("Food", "Days of food", "<3", C, "Edible nutrition in storage divided by what the crew eats. Under 3 days: hunt, harvest, cook."),
    "meals": ("Food", "Meals", "==0", W, "Cooked meals in storage."),
    "raw_food": ("Food", "Raw food", "<20", W, "Raw meat and vegetables in storage."),
    "food_store": ("Food", "Food store exists", False, W, "A stockpile labelled food. Make one (stockpile_room or stockpile_camp)."),
    "store_roofed_fraction": ("Food", "Store under roof", "<1", W, "Share of the store cells that are roofed. Food rots outdoors."),
    "unroofed_store_cells": ("Food", "Unroofed store cells", ">0", W, "Store cells without a roof."),
    "berry_bushes": ("Food", "Berry bushes", ">0", I, "Wild berry bushes to harvest."),
    "healroot_plants": ("Food", "Healroot plants", ">0", I, "Wild healroot to harvest for medicine."),
    "wild_game": ("Food", "Huntable game", "==0", I, "Safe animals to hunt on the map."),
    "growing_cells": ("Food", "Growing zone cells", "==0", W, "Cells in growing zones."),
    "fields_all_default_crop": ("Food", "Every field the same crop", True, W, "More than one field, all growing the same plant. Owner wants rice, corn, potatoes, healroot, cotton, smokeleaf, psychoid, hops."),
    "stoves": ("Food", "Stoves", "==0", W, "Stoves built. No stove, no meals."),
    "bill_rows": ("Production", "Bills on benches", "==0", W, "Every bill on every workbench. Zero means nothing is being made."),
    # ---- stores
    "wood": ("Stores", "Wood", "<50", W, "Wood logs in storage. Chop trees near the crew."),
    "steel": ("Stores", "Steel", "<50", W, "Steel in storage. Mine compacted steel or scrap."),
    "components": ("Stores", "Components", "<5", W, "Industrial components. Needed for power, turrets, research."),
    "adv_components": ("Stores", "Advanced components", "<1", I, "Spacer components."),
    "plasteel": ("Stores", "Plasteel", "<1", I, "Plasteel."),
    "uranium": ("Stores", "Uranium", "<1", I, "Uranium."),
    "gold": ("Stores", "Gold", None, I, "Gold. Vault it."),
    "silver": ("Stores", "Silver", "<100", I, "Silver for trade. Vault it."),
    "chemfuel": ("Stores", "Chemfuel", "<20", I, "Chemfuel for generators."),
    "cloth": ("Stores", "Cloth", "<20", I, "Cloth and leather for clothes."),
    "stockpile_cells": ("Stores", "Stockpile cells", "==0", W, "Cells in stockpile zones."),
    "main_store": ("Stores", "Main store exists", False, I, "A stockpile labelled main."),
    "loose_items_unstored": ("Stores", "Loose items", ">20", W, "Items lying outside storage. Haul them in."),
    "forbidden_items": ("Stores", "Forbidden items", ">0", W, "Forbidden items in the camp. Owner: unforbid the starting materials."),
    "loose_weapons": ("Stores", "Weapons on the ground", ">0", I, "Weapons lying on the map. Equip them (empire_pass)."),
    "junk_weapons": ("Stores", "Junk weapons", ">0", I, "Awful or poor weapons on the ground: smelt or sell."),
    "corpses": ("Stores", "Corpses", ">0", W, "Corpses on the map. Bury, butcher or burn."),
    # ---- power
    "has_power": ("Power", "Power exists", False, W, "A generator or battery is built."),
    "power_generators": ("Power", "Generators", "==0", I, "Power generators built."),
    "power_margin_pct": ("Power", "Power margin %", "<110", W, "Power made as a percent of power used. Under 110 means brownouts are close."),
    "unpowered_consumers": ("Power", "Unconnected consumers", ">0", W, "Powered buildings on no power net: lay conduit."),
    "unpowered_embrasures": ("Power", "Unpowered embrasures", ">0", W, "Powered embrasures switched off or without power."),
    # ---- rooms
    "beds": ("Rooms", "Beds", "<3", W, "Beds built."),
    "rooms_out_of_temp": ("Rooms", "Rooms too hot or cold", ">0", W, "Rooms under 10C or over 35C. Heaters, coolers, vents."),
    "unfloored_room_cells": ("Rooms", "Unfloored room cells", ">0", I, "Room cells on bare or natural floor. Floors lift beauty and cleanliness."),
    "room_wall_holes": ("Rooms", "Rooms with roof holes", ">0", W, "Rooms with open roof cells: they are not rooms for temperature."),
    "lab_lit": ("Rooms", "Research benches lit", False, W, "Every research bench has light. Dark research is slow."),
    "torch_lamps": ("Rooms", "Torch lamps", "==0", I, "Torch lamps built."),
    "home_cells": ("Rooms", "Home area cells", "==0", I, "Cells in the home area."),
    "camp_water_cells": ("Rooms", "Marsh or water in the camp", ">0", I, "Marsh, mud or water inside the home area. Owner: terraform or move."),
    "blueprints": ("Rooms", "Blueprints waiting", ">30", I, "Unbuilt blueprints."),
    "blueprints_against_rock": ("Rooms", "Wall plans against rock", ">0", W, "Wall blueprints next to unmined rock. Mine first."),
    "buildings_damaged": ("Rooms", "Damaged buildings", ">0", W, "Buildings below full health. Repair."),
    # ---- defence
    "defences_built": ("Defence", "Any defences", False, W, "Sandbags, barricades, embrasures or turrets built."),
    "embrasures": ("Defence", "Embrasures", "<16", I, "Embrasures built."),
    "turrets": ("Defence", "Turrets", "==0", I, "Turrets built."),
    "wall_gaps": ("Defence", "Gaps in the ring", ">0", W, "Open walkable cells on the home area's edge. Close the ring."),
    "embrasure_gaps": ("Defence", "Gaps by embrasures", ">0", W, "Ring gaps next to an embrasure."),
    # ---- research / production
    "research_benches": ("Research", "Research benches", "==0", W, "Research benches built. Build one by day 3."),
    "simple_benches": ("Research", "Simple research benches", None, I, "Simple research benches."),
    "hitech_benches": ("Research", "Hi-tech benches", None, I, "Hi-tech research benches."),
    "multi_analyzers": ("Research", "Multi-analyzers", None, I, "Multi-analyzers built."),
    "ship_research_done": ("Research", "Ship research done", None, I, "Ship basics researched."),
    "ship_parts": ("Research", "Ship parts", None, I, "Ship parts built."),
    "comms_console": ("Production", "Comms console", False, I, "A comms console for traders and factions."),
    "throne": ("Production", "Throne room", None, I, "A throne is built."),
    "grav_parts": ("Production", "Grav parts", None, I, "Gravship parts."),
    # ---- colony
    "colony_exists": ("Colony", "Colony exists", False, C, "There are colonists on a map."),
    "colony_animals": ("Colony", "Tamed animals", None, I, "Animals owned by the colony."),
    "colony_mechs": ("Colony", "Colony mechs", None, I, "Mechanoids owned by the colony."),
    "mount_candidates": ("Colony", "Mount animals", None, I, "Animals that could be mounts."),
    "explore_done": ("Colony", "Exploring done", False, I, "No unexplored frontier within 30 cells of the crew."),
    "monolith": ("Colony", "Void monolith", None, I, "The Anomaly monolith is on the map."),
    "monolith_level": ("Colony", "Monolith level", None, I, "The Anomaly monolith's level."),
    "title_seniority": ("Colony", "Royal title", None, I, "The highest royal title held."),
    "away_maps": ("Colony", "Colonists away", ">0", I, "Maps other than home with colonists on them."),
    "map_count": ("Colony", "Maps", None, I, "Maps loaded."),
    # ---- world
    "day": ("World", "Day", None, I, "Days since the colony started."),
    "quadrum_index": ("World", "Quadrum", None, I, "Quadrum counter (not the season)."),
    "outdoor_temp": ("World", "Outdoor temperature", None, I, "Outdoor temperature in C."),
    "game_conditions": ("World", "Active events", None, I, "Active map and world conditions (any mod)."),
    "letters": ("World", "Unread letters", ">0", W, "Letters not read yet. Read every one."),
    "quest_letter": ("World", "Quest letter", True, I, "A new quest letter."),
    "empire_letter": ("World", "Empire letter", True, I, "A letter from the Empire."),
    # ---- stream (host inputs, from the stream PC)
    "seconds_since_spoken": ("Stream", "Seconds since she spoke", ">45", W, "Dead air on stream. Say something, ask chat something."),
    "chat_unanswered": ("Stream", "Chat unanswered", ">0", C, "Viewer messages she has not answered. Owner: never ignore chat."),
    "chat_asks_mod": ("Stream", "Chat asks for the mod", True, W, "A viewer asked where to get the mod. Give the link."),
    "voice_playing": ("Stream", "Voice playing", None, I, "Her voice is speaking a line right now."),
    "seconds_since_webcam": ("Stream", "Seconds since webcam", ">180", W, "Her webcam picture is stale. Owner: update it every couple of minutes."),
    "seconds_since_tool": ("Stream", "Seconds since she acted", ">180", W, "Her player has not acted in a while."),
    "owner_input_active": ("Stream", "Owner at the controls", True, I, "The owner used the keyboard or mouse in the last minute. Never fight his input."),
    "owner_unread": ("Stream", "Owner messages unread", ">0", C, "Private owner messages in the last hour that no reply_owner has answered."),
    "prompt_version_changed": ("Stream", "Her prompt changed", True, I, "Her prompt or ladder file changed since the last scan."),
    # ---- game
    "paused": ("Game", "Paused", None, I, "The game is paused."),
    "ticks_moving": ("Game", "Time running", False, W, "Game time is running. A paused game builds nothing."),
    "dialog_open": ("Game", "Dialog open", True, W, "A dialog is open and freezes play. Read its buttons and answer it."),
    "game_foreground": ("Game", "Game window in front", False, I, "The game window has focus."),
    "home_on_screen": ("Game", "Home map shown", False, I, "The home map is the one on screen."),
    "hud_visible": ("Game", "HUD visible", False, I, "The game's interface is visible."),
    "window_fullscreen": ("Game", "Fullscreen", None, I, "The game window is fullscreen."),
    "camera_on_colonist": ("Game", "Camera on the crew", False, I, "The camera shows at least one colonist."),
    # ---- inventory section D + pawn setup (2026-10-13)
    "toxic_buildup_max": ("Health", "Worst toxic buildup", ">=0.4", C, "The worst colonist's toxic buildup (0-1). At 40% pull that pawn inside to rest under a roof."),
    "worst_disease_margin": ("Health", "Disease race margin", "<0.1", C, "Immunity minus severity of the worst disease a colonist is still fighting. Under 0.1 the disease may win: bed rest, best medicine, tend every 12 h."),
    "battery_days_stored": ("Power", "Battery days stored", "<1", W, "Stored battery energy divided by what the colony draws now, in days. Under 1 a night or eclipse can black out the base."),
    "kitchen_tables_no_bill": ("Food", "Kitchen tables with no bill", ">0", W, "A built stove with no meal bill or a butcher table with no butcher bill. game_set cmd kitchen."),
    "butcher_tables": ("Food", "Butcher tables", "==0", I, "Built butcher tables. Hunting with none means meat rots on the ground."),
    "freezer_coolers": ("Food", "Freezer coolers", "==0", W, "Built coolers chilling an indoor room. None means no freezer: game_set cmd freezer."),
    "freezer_coolers_warm": ("Food", "Freezer coolers not cold", ">0", W, "Freezer coolers set above 0 C. game_set cmd freezer sets -5 C."),
    "cooler_planned": ("Food", "Coolers planned", ">0", I, "Cooler blueprints or frames waiting for materials and a builder."),
    "stone_blocks": ("Stores", "Stone blocks", "<50", I, "Stone blocks of every kind in storage: walls, towers and floors."),
    "tower_ne": ("Defence", "Tower NE", False, I, "An embrasure stands or is planned near the north-east corner of the Home area (a tower or the wall's own)."),
    "corner_ne_x": ("Defence", "NE corner x", None, I, "The north-east corner of the Home area: where game_set cmd tower goes."),
    "corner_ne_z": ("Defence", "NE corner z", None, I, "The north-east corner of the Home area: where game_set cmd tower goes."),
    "tower_nw": ("Defence", "Tower NW", False, I, "An embrasure stands or is planned near the north-west corner of the Home area (a tower or the wall's own)."),
    "corner_nw_x": ("Defence", "NW corner x", None, I, "The north-west corner of the Home area: where game_set cmd tower goes."),
    "corner_nw_z": ("Defence", "NW corner z", None, I, "The north-west corner of the Home area: where game_set cmd tower goes."),
    "tower_se": ("Defence", "Tower SE", False, I, "An embrasure stands or is planned near the south-east corner of the Home area (a tower or the wall's own)."),
    "corner_se_x": ("Defence", "SE corner x", None, I, "The south-east corner of the Home area: where game_set cmd tower goes."),
    "corner_se_z": ("Defence", "SE corner z", None, I, "The south-east corner of the Home area: where game_set cmd tower goes."),
    "tower_sw": ("Defence", "Tower SW", False, I, "An embrasure stands or is planned near the south-west corner of the Home area (a tower or the wall's own)."),
    "corner_sw_x": ("Defence", "SW corner x", None, I, "The south-west corner of the Home area: where game_set cmd tower goes."),
    "corner_sw_z": ("Defence", "SW corner z", None, I, "The south-west corner of the Home area: where game_set cmd tower goes."),
    "research_upgrades_unbuilt": ("Research", "Upgrades not built", ">0", W, "Researched buildings (hi-tech bench, multi-analyzer, trade beacon, comms console, drug lab) not built yet. Build each the moment it is researched."),
    "research_upgrades_missing": ("Research", "Upgrades to build", None, I, "The researched buildings not built yet, by def name."),
    "prisoners_new": ("Crew", "New prisoners", ">0", W, "Prisoners with no stance yet (still on Maintain only and never seen with another). game_set cmd prisoner mode recruit pawn <name>."),
    "prisoners_new_names": ("Crew", "New prisoner names", None, I, "Who the new prisoners are."),
    "trader_caravans_on_map": ("World", "Trader caravans here", ">0", I, "A trader caravan is on the map: game_set cmd trade lists what it buys and sells."),
    "gate_watch_posture": ("Colony", "Gate watch posture", "!=1", I, "How long a gate operator stays at the console: 0 Mild, 1 Balanced (the owner's default), 2 Strict. The eat/safety floor holds in every posture."),
    "tower_ne_built": ("Defence", "Tower NE built", None, I, "A built embrasure stands near the north-east corner: its security room can go up."),
    "tower_nw_built": ("Defence", "Tower NW built", None, I, "A built embrasure stands near the north-west corner: its security room can go up."),
    "tower_se_built": ("Defence", "Tower SE built", None, I, "A built embrasure stands near the south-east corner: its security room can go up."),
    "tower_sw_built": ("Defence", "Tower SW built", None, I, "A built embrasure stands near the south-west corner: its security room can go up."),
    "tower_ne_cooler": ("Defence", "Tower NE cooler", "==3", W, "The north-east tower room's cooler: 0 none, 1 planned, 2 built and powered, 3 built with no power."),
    "tower_ne_cell_x": ("Defence", "Tower NE cell x", None, I, "A cell inside the north-east tower room (room_cooler goes here)."),
    "tower_ne_cell_z": ("Defence", "Tower NE cell z", None, I, "A cell inside the north-east tower room (room_cooler goes here)."),
    "tower_nw_cooler": ("Defence", "Tower NW cooler", "==3", W, "The north-west tower room's cooler: 0 none, 1 planned, 2 built and powered, 3 built with no power."),
    "tower_nw_cell_x": ("Defence", "Tower NW cell x", None, I, "A cell inside the north-west tower room (room_cooler goes here)."),
    "tower_nw_cell_z": ("Defence", "Tower NW cell z", None, I, "A cell inside the north-west tower room (room_cooler goes here)."),
    "tower_se_cooler": ("Defence", "Tower SE cooler", "==3", W, "The south-east tower room's cooler: 0 none, 1 planned, 2 built and powered, 3 built with no power."),
    "tower_se_cell_x": ("Defence", "Tower SE cell x", None, I, "A cell inside the south-east tower room (room_cooler goes here)."),
    "tower_se_cell_z": ("Defence", "Tower SE cell z", None, I, "A cell inside the south-east tower room (room_cooler goes here)."),
    "tower_sw_cooler": ("Defence", "Tower SW cooler", "==3", W, "The south-west tower room's cooler: 0 none, 1 planned, 2 built and powered, 3 built with no power."),
    "tower_sw_cell_x": ("Defence", "Tower SW cell x", None, I, "A cell inside the south-west tower room (room_cooler goes here)."),
    "tower_sw_cell_z": ("Defence", "Tower SW cell z", None, I, "A cell inside the south-west tower room (room_cooler goes here)."),
    "pawns_unconfigured": ("Crew", "Not set up", '>0', C, "Colonists never fully set up: gun + melee sidearm, Attack, self-tend, a job, the No drugs policy. Owner: an unarmed or unset pawn is top priority. game_set cmd crew_setup, then empire_pass."),
    "trade_ships_in_orbit": ("World", "Trade ships in orbit", '>0', I, "Orbital traders passing. Call them from the comms console; goods land on the trade beacons."),
    "trade_beacons": ("World", "Trade beacons", None, I, "Orbital trade beacons. Only goods in their range can be sold to ships."),
    "comms_consoles": ("World", "Comms consoles", None, I, "Comms consoles: traders, factions and (No Quests Without Comms) quests."),
    "caravans_out": ("World", "Caravans out", '>0', I, "Player caravans travelling. Home has fewer hands: no big builds, keep the defence staffed."),
    "caravan_pawns_out": ("World", "Colonists away", '>0', I, "Colonists inside caravans right now."),
    "transport_pods": ("World", "Transport pods", None, I, "Transport pods built."),
    "pod_launchers": ("World", "Pod launchers", None, I, "Pod launchers built."),
    "quests_active": ("World", "Quests running", None, I, "Accepted quests in progress."),
    "quests_offered": ("World", "Quests offered", '>0', I, "Quests waiting for an answer. Read each one; accept what the colony can do."),
    "pen_markers": ("Colony", "Animal pens", None, I, "Animal pen markers."),
    "pen_animals_unpenned": ("Colony", "Animals outside a pen", '>0', W, "Roped animals with no pen. They wander and eat the fields. Build a pen (game_set cmd pen)."),
    "power_nets": ("Power", "Power nets", None, I, "Separate power grids."),
    "power_nets_dead": ("Power", "Dead power nets", '>0', W, "Grids with machines but no working power source: a cut or missing conduit. Route conduit to a generator or battery."),
    "stockpiles": ("Stores", "Stockpiles", None, I, "Stockpile zones."),
    "storage_buildings": ("Stores", "Storage buildings", None, I, "Shelves and other storage buildings."),
    "stockpiles_default_priority": ("Stores", "Stockpiles at Normal", None, I, "Stockpiles still at Normal priority. Food and medicine stores should be Important."),
    "ideo_roles": ("Colony", "Ideoligion roles", None, I, "Roles the ideoligion has."),
    "ideo_roles_unassigned": ("Colony", "Empty ideo roles", '>0', I, "Ideoligion roles nobody holds. Assign leader and moral guide once 3+ colonists."),
    "ideo_leader_assigned": ("Colony", "Leader assigned", False, I, "The ideoligion leader role is held."),
    "ritual_spots": ("Colony", "Ritual spots", None, I, "Ritual spots built."),
    "ideo_rituals": ("Colony", "Rituals", None, I, "Rituals the ideoligion has."),
    "visitors": ("World", "Visitors", '>0', I, "Friendly outsiders on the map: greet them on stream, trade if a trader."),
    "hospitality_guests": ("World", "Hospitality guests", '>0', I, "Guests staying (Hospitality). They need guest beds and recreation."),
    "guest_beds": ("World", "Guest beds", None, I, "Hospitality guest beds."),
}
PREFIX_GROUPS = [("designations_", "Production", "Designations"), ("condition_", "World", "Event"),
                 ("alert_", "Game", "Alert"), ("count_", "Stores", "Count")]


def main():
    d = json.load(open(BOOK, encoding="utf-8"))
    done, generic = 0, 0
    for k, spec in d["sensors"].items():
        row = T.get(k)
        if row is None:
            pre = next((p for p in PREFIX_GROUPS if k.startswith(p[0])), None)
            label = k.replace("_", " ").capitalize()
            if pre:
                label = pre[2] + ": " + k[len(pre[0]):].replace("_", " ")
            row = (pre[1] if pre else "Colony", label, None, I, spec.get("source", ""))
            if k.startswith("condition_"):
                row = ("World", label, True, W, "A map condition is active: " + k[len("condition_"):].replace("_", " ") + ".")
            generic += 1
        group, label, warn, sev, tip = row
        spec["group"], spec["label"], spec["severity"], spec["tip"] = group, label, sev, tip
        if warn is None:
            spec.pop("warn", None)
        else:
            spec["warn"] = warn
        done += 1
    with open(BOOK, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("annotated %d sensors (%d from the generic rule)" % (done, generic))
    missing = [k for k in T if k not in d["sensors"]]
    if missing:
        print("in the table but not declared:", ", ".join(missing))


if __name__ == "__main__":
    main()
