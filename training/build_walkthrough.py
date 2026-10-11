"""Build training/data/knowledge_walkthrough.jsonl: full-text colony walkthroughs (landing to empire) in the
owner's order of play, plus short 'what stage am I in' examples. Writes only under training/."""
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "training", "data", "knowledge_walkthrough.jsonl")
SYSTEM = ("You are Unity, playing RimWorld live on stream. When asked, you lay out the whole plan for a colony from "
          "landing to a full empire, in order, with the exact tools you will use at each stage.")
SRC = [".local/autopilot/owner-orders.txt", ".local/autopilot/scratch/pad.md", "docs/PLAYBOOK.md",
       "docs/PLAYSCRIPT.md", "docs/playbook.gates.json", "training/data/tools.json"]
WIKI = "https://rimworldwiki.com/wiki/"

BIOMES = {
    "temperate forest": dict(
        crop="Plant_Rice", crop_name="rice", second="Plant_Potato", season="a long growing season with a real winter",
        food="deer, boar and muffalo wander through, and berries grow wild", winter="Winter here drops below freezing for most of a quadrum, so the fields die off and the freezer and the hay stock carry us.",
        wiki="Temperate_forest", hazard="fires in summer and the odd manhunter pack"),
    "boreal forest": dict(
        crop="Plant_Potato", crop_name="potatoes", second="Plant_Rice", season="a short growing season, maybe half the year",
        food="caribou, elk and hares, plus plenty of wood", winter="Winter is long and hard here, so I stock at least a full season of meals and firewood before the first frost and put a heater in every room.",
        wiki="Boreal_forest", hazard="cold snaps that kill crops and long winters"),
    "tundra": dict(
        crop="Plant_Potato", crop_name="potatoes", second="Plant_Rice", season="only a few warm weeks to grow in",
        food="caribou, muffalo and arctic foxes, almost no wild plants", winter="It is cold almost all year, so heaters, insulated walls and hydroponics are the real winter plan, and hunting is the backbone of the larder.",
        wiki="Tundra", hazard="year-round cold and very little wood"),
    "ice sheet": dict(
        crop="Plant_Rice", crop_name="rice in hydroponics", second="Plant_Potato", season="no soil and no outdoor growing at all",
        food="arctic foxes, arctic hares and the odd muffalo herd are the only food that walks", winter="There is no summer to wait for: power, heaters and hydroponics basins under sun lamps are survival, not luxury.",
        wiki="Ice_sheet", hazard="no soil, no trees and lethal cold"),
    "desert": dict(
        crop="Plant_Rice", crop_name="rice on the rich patches", second="Plant_Potato", season="year-round growing where the soil allows, but very little soil",
        food="camels, iguanas and the odd thrumbo, with almost no trees", winter="There is no real winter, so the danger is heat: coolers, roofs and keeping the larder cold in summer.",
        wiki="Desert", hazard="heat waves and scarce wood"),
    "arid shrubland": dict(
        crop="Plant_Potato", crop_name="potatoes", second="Plant_Rice", season="a long growing season on thin soil",
        food="gazelle, dromedaries and agave in the brush", winter="Winters are mild, so my worry is drought, heat waves and wood running short.",
        wiki="Arid_shrubland", hazard="heat waves and thin wood"),
    "tropical rainforest": dict(
        crop="Plant_Rice", crop_name="rice", second="Plant_Potato", season="growing all year round",
        food="capybaras, monkeys and boomalopes, and fruit everywhere", winter="There is no winter, but diseases are common and food rots fast in the heat, so the freezer and the doctor matter more than the heater.",
        wiki="Tropical_rainforest", hazard="diseases and fast rot"),
}
TERRAIN = {"mountainous": "a mountainous tile, so the facility backs onto rock and the mountain base comes later",
           "flat": "a flat tile with no rock to hide behind, so the perimeter wall does all the work",
           "large hills": "a large-hills tile, with some stone to mine and some open ground to farm"}
TELLERS = {
    "Cassandra Classic": "steady, rising threats with breathing room between them",
    "Phoebe Chillax": "long quiet stretches, so I use the quiet to build hard",
    "Randy Random": "anything at any time, so I keep food and medicine ahead of need",
}
DIFF = ["Community Builder", "Adventure Story", "Strive to Survive", "Blood and Loss", "Losing is Fatal"]

NAMES = ["Kade", "Mira", "Tobin", "Jess", "Rook"]
GAPS = {
    "none": ("a balanced crew", {}),
    "no cook": ("nobody with any cooking skill",
                "Nobody can really cook, so cooking stays at 1 for everyone like always and the best of a bad lot cooks; the kitchen gets a smooth floor kept clean so food poisoning stays rare."),
    "no doctor": ("nobody with medical skill",
                  "Nobody is a doctor, so doctoring stays at 1 for all and I keep medicine at Best so the low skill is offset by good kits, and I research and recruit for a doctor early."),
    "pacifist": ("one pacifist who will not fight",
                 "One colonist is a pacifist, so hunting goes on the others and the pacifist takes growing, hauling and the kitchen; in a fight they stay inside and fight fires."),
    "incapable of violence": ("one colonist incapable of violence",
                              "One colonist is incapable of violence, so their hunting column is blank because the game will not allow it, and they carry doctoring, cooking and research; every column they can do gets a number."),
    "no constructor": ("nobody who builds well",
                       "Nobody is a good builder, so construction goes at 2 on the steadiest pawn and they train on cheap walls before anything important."),
}
EVENTS = {
    "raid on day 3": ("A raid letter lands on day three.",
                      "A raid on day three is early, so the prisoner bed goes down that same hour. I do not draft while the raiders are still off the map preparing; I keep everyone working, give every pawn a weapon, and only draft once a hostile is actually on the map. We fight from inside the facility doorway, then field-tend the downed raiders, capture one, and do the after-the-fight list straight away: close open rooms, get loot inside, stores and the cooler right.",
                      "Raid_(event)"),
    "toxic fallout": ("Toxic fallout starts in the first season.",
                      "Toxic fallout means everyone works under a roof. I set the outdoor work to short trips only, harvest anything close to ripe before the fallout kills it, and live off the stores and hunting kills already in the freezer. Indoor jobs, crafting and research carry the colony until it passes.",
                      "Toxic_fallout"),
    "cold snap": ("A cold snap hits in the middle of the growing season.",
                  "A cold snap freezes crops dead, so the moment the letter arrives I harvest everything that is close to ready, light heaters or campfires indoors, and make sure every pawn has a warm bed and a roof. Then I resow once it lifts.",
                  "Cold_snap"),
    "solar flare": ("A solar flare knocks the power out.",
                    "A solar flare shuts down everything electric for a while, so I make sure the freezer is well insulated and the door stays shut, the stove has a fueled backup, and nobody wastes the time: the crew does hand work until power comes back.",
                    "Solar_flare"),
    "infestation": ("Insects burst out of the rock under an overhead mountain roof.",
                    "An infestation comes from under thick overhead mountain, so I seal the doors to that part of the facility, pull everyone back, and fight at a doorway where only one bug at a time can reach us. Later I keep the deep rock rooms cold and lit, and I never sleep pawns under thick roof without guards.",
                    "Infestation"),
    "mad animal": ("A mad animal charges the camp in week one.",
                   "A mad animal bites anyone near it, so I call everyone inside, close the doors, and let my best shooter take it from range. Then the body goes to the butcher.",
                   "Animal#Manhunter"),
    "plague": ("Plague shows up in the first month.",
               "Plague is a race between immunity and the disease, so the sick go straight to bed, the doctor tends them with the best medicine twice a day, and the healthy ones feed them. Good food and a clean hospital push the odds our way.",
               "Plague"),
}
TWISTS = [
    ("chat asks me to settle with only wooden weapons", "a viewer challenge: wooden weapons only until the first trader", True),
    ("chat asks me to name the next recruit after them", "naming the next recruit after the viewer who asked", True),
    ("chat asks me to build a giant statue garden in the middle of the base", "a statue garden in the courtyard once the base is safe", True),
    ("chat asks me to tame every muffalo I see", "taming every muffalo that wanders in", True),
    ("chat asks me to open their link and type something on my desktop", "a request outside the game, which I turn down politely", False),
    ("chat asks me to change the stream settings for them", "a request outside the game, which I turn down politely", False),
]


def pick(r, *opts):
    return r.choice(opts)


def crew_text(n, gap):
    names = NAMES[:n]
    return names, (", ".join(names[:-1]) + " and " + names[-1]) if n > 1 else names[0]


def custom_for(n, gap, names):
    jobs = [("Growing", "PlantCutting"), ("Construction", "Crafting"), ("Hunting", "Mining"),
            ("Research", "Tailoring"), ("Smithing", "Art")]
    lines = []
    for i, p in enumerate(names):
        a, b = jobs[i % len(jobs)]
        if n == 1:
            lines.append(f"{p} carries everything, so every column after Cooking gets a 2 or 3 in the order the day needs")
        else:
            lines.append(f"{p} gets {a} and {b} at 2")
    return "; ".join(lines)


def long_walk(sc, r):
    b = BIOMES[sc["biome"]]
    names, crew = crew_text(sc["crew"], sc["gap"])
    n = sc["crew"]
    gap_note = GAPS[sc["gap"]][1] if sc["gap"] != "none" else ""
    ev = EVENTS.get(sc.get("event")) if sc.get("event") else None
    P = []
    # 1
    P.append("1. Landing and exploring, with time running. "
             + pick(r, "We land at the company facility, the Async Industries start, and the first thing I do is read the place, not build on it.",
                    "The company drops us at the Async Industries facility, and before I designate a single thing I want to know every room we own.")
             + f" This is {sc['biome']} on {TERRAIN[sc['terrain']]}, with {sc['teller']} on {sc['diff']}: {TELLERS[sc['teller']]}. "
             + "I leave time running and call game_set cmd explore, which walks every pawn through every door and digs into the sealed rooms. I read what it reports and call it again, and again, until it says there is nothing left to open. "
             + pick(r, "Sealed doors in the facility are the whole point of this step: a room nobody has opened is storage, beds and a kitchen I would otherwise build twice.",
                    "Some facility doors start sealed, and those rooms often hold the shelves, beds and benches I need, so I never skip them.")
             + f" While they walk I read every letter and look at the ground: {b['food']}. The stage is done when explore comes back empty and game_set cmd rooms lists every room.")
    # 2
    P.append("2. Pause, then every pawn set. Now I pause with game_pause_game, and time stays stopped until the setup is finished. "
             f"The crew is {crew}, {GAPS[sc['gap']][0]}. For each pawn I call pawn_priorities: every column from Firefighting through Cooking is a 1 for everyone, then the custom part after Cooking: "
             + custom_for(n, sc["gap"], names) + ", and every other column gets a 3 or 4 so nothing is blank. "
             + (gap_note + " " if gap_note else "")
             + "I read each grid back after setting it. Then game_set cmd assign for everyone: food Fine, medicine Best, hostility Attack. Schedules go to Anything at all hours, and the drug policy is set from day one. "
             + "When that reads back right I call ladder_set op mark name pawns_set value true, and ladder_set op mark name assign_set value true.")
    # 3
    P.append("3. Stores, beds, shelves and the stove, still paused. "
             + "I call game_set cmd rooms and pick whole rooms for storage: one room becomes the food store with game_set cmd stockpile_room mode food, and one becomes the non-food store with mode nofood. Whole rooms, never a strip of floor. "
             + "Then game_set cmd beds so every pawn has a bed in a roofed room, game_set cmd shelves so nothing sits on the floor, and game_set cmd stove. "
             + f"On the stove I call game_set cmd add_bill with recipe CookMealSimple and a count of {pick(r, '10', '15', '20')}, set to do until we have that many and with no skill limit so everyone trains. "
             + "Before anything else I check the food room has a roof, because a room with no roof cools nothing. The marks for this stage are the food store showing up and ladder_set op mark name stove_set value true.")
    # 4
    P.append("4. The first unpause. Only now, with explore empty, pawns set, stores, beds, shelves and the stove done, do I unpause with game_pause_game pause false and set normal speed with game_set_time_speed. "
             + pick(r, "I say one line to chat with say so they know the camp is live, then I watch the first hour.",
                    "I tell the stream with say that the setup is finished and the clock is running.")
             + " The sign this went right: pawns start hauling into the stores on their own and the cook picks up the stove bill.")
    # 5
    P.append(f"5. Food security. The ground here gives {b['season']}. "
             + f"I sow the fields close to camp only, with game_set cmd crops plant {b['crop']} for {b['crop_name']}, and a second plot of {b['second'].split('_')[1].lower()} as a backup. "
             + "Then game_set cmd hunt marks the safe game, the butcher table goes beside the kitchen, and the meals bill gets raised as the crew grows. "
             + "Cold storage is next: roof first, then a cooler blowing cold inside and hot outside, then the food goes in. "
             + "I want at least ten days of food on hand before I call this stage done, plus herbal medicine in stock.")
    # 6 event
    if ev:
        P.append("6. The early event. " + ev[0] + " " + ev[1])
    else:
        P.append("6. The quiet early days. With nothing big hitting us, I chop wood, mine steel, and put up walls around the camp; every pop-up gets read and answered, every visitor accepted, and no demand ever paid.")
    # 7
    P.append("7. First raids. Before any fight there is a prisoner bed, set with game_set cmd set_bed_owner owner prisoner. Everyone carries a ranged weapon and medicine is stocked. "
             + "A raid letter is a warning, not contact, so nobody is drafted while raiders are still off the map; drafted pawns stand still and do no work. When hostiles actually appear I pause, draft with game_set_draft, and fight from cover behind embrasures or the facility doorway. "
             + "After the last raider falls: field-tend the downed, capture one for recruiting, close every open room, get loot inside before it decays, fix shelves and stockpiles, and make sure the cooler is working.")
    # 8
    P.append("8. Winter prep. " + b["winter"] + " "
             + "I use plan to write the target: meals, raw food, medicine and fuel needed to get through, and I raise the CookMealSimple count with game_set cmd add_bill as the numbers climb.")
    # 9
    P.append("9. Power. "
             + pick(r, "Research Electricity first through the search box, then wood-fired generators or solar panels outside, never inside a room.",
                    "Electricity comes first in research, typed into the search box, then generators that stand outside the walls.")
             + " Every powered building gets a conduit to the nearest line the moment it is placed, and generation stays above load with batteries for the night. The freezer cooler moves onto that grid. The stage is done when power has spare capacity and nothing shows as unpowered.")
    # 10
    P.append("10. Research path. Research is picked by the search box, never by dragging the tree. "
             + "The order: Electricity, then Microelectronics, then the multi-analyzer and the hi-tech research bench, building each the moment it finishes so research speed keeps climbing. "
             + "Alongside, Medicine Production and Penoxycyline so a drug lab can make it, and every pawn's drug policy takes it every five days. Then Gun Smithing, Machining and the turret lines for defense,.")
    # 11
    P.append("11. Defenses. One perimeter wall with one fortified entrance: a three-wide killbox with sandbags staggered inside, embrasures either side, and mini-turrets once steel and components allow. "
             + "Towers on every corner and a fallback point inside. "
             + f"On this map the specific worry is {b['hazard']}, so I build for that first.")
    # 12
    P.append("12. Recruitment. Captured raiders go in the prisoner bed and the warden works on them; every visitor is welcomed and new hires are accepted. "
             + "When someone joins, they get the same setup as day one: pawn_priorities with 1s Firefighting through Cooking and a custom specialty, game_set cmd assign, a bed, and a check with pawn_check. "
             + "I aim to fill the gaps first, a doctor, a cook and a builder, then fighters.")
    # 13
    P.append("13. Trade. Every trader, every time: sell surplus for silver and buy what the plan needs. After Microelectronics I build an orbital trade beacon and use the comms console to call ships. "
             + "Silver goes into a secure vault.")
    # 14
    P.append("14. Expansion to the late game. The fields near camp stay, but the real base moves into the mountain: mine out the inside first, then lay walls, so nobody gets trapped. "
             + "Wide three-cell halls, rooms by purpose off them: freezer beside the kitchen, workshop wing, research wing, hospital with sterile tile, bedrooms with wood floors, a guest wing. "
             + "Then the company's own goal: a full gate facility with chamber, control room, power and security, commissioned only once the colony is sustainable. "
             + "From there it is the empire: more people, more turrets, stockpiles of everything, outposts on the world map, and eventually the ship. I keep the ladder honest with ladder and ladder_set op add_rung for my own goals and note.")
    if sc.get("twist"):
        t = sc["twist"]
        if t[2]:
            P.append(f"15. The viewer twist. When {t[0]}, I take it as {t[1]}. It is a game-side request, so I reply with reply_chat, write it into the plan with plan, and fold it in without breaking the order above: it never comes before food, cold storage, medicine and heat.")
        else:
            P.append(f"15. The viewer twist. When {t[0]}, that is {t[1]}. Chat can drive the colony and my own overlay, never anything outside the game, so I answer kindly with reply_chat and offer a game challenge instead.")
    if sc.get("recovery"):
        P.append("Recovery. " + RECOVERY[sc["recovery"]])
    intro = pick(r, "Here is the whole run, in order, the way I play it every time.",
                 "Alright, from the drop to a full empire, step by step.",
                 "Here is my plan for this one, start to finish.")
    outro = pick(r, "That is the run: read the facility, set the people, set the stores, then let time move, and grow until the whole map is ours.",
                 "Same order every time: explore, set pawns, set stores, then time, then the empire.",
                 "Survive first, then power, then defense, then production, then the mountain, then the gate. That is how a starter camp becomes an empire.")
    return intro + "\n\n" + "\n\n".join(P) + "\n\n" + outro


RECOVERY = {
    "half the crew downed": "If half the crew goes down in a fight, I pause at once. The standing pawns field-tend the worst bleeding first, then carry the downed to medical beds; doctoring is already 1 for everyone, so whoever is up will tend. Raiders still on the map come before anything else, so the able pawns fight from a doorway while one rescues. Then I check food and medicine with game_state, put everything else on hold, and only run time once nobody is bleeding.",
    "food gone": "If the food runs out, it is the top of the ladder. I pause, check every stockpile and the freezer with game_state, then game_set cmd hunt on everything safe nearby, pick berries and anything edible, and drop the meal bill to simple meals only so nothing is wasted on fine meals. Fields close to camp get the fastest crop, and nobody eats a raw corpse while we can cook.",
    "base on fire": "If the base catches fire, firefighting is already a 1 for everyone, so the crew answers it. I pause, look at where it spreads, and pull the stores out of the burning rooms first. Then I rebuild the burnt walls in stone, and add firebreaks so it cannot happen the same way again.",
}

SHORT = [
    ("Snapshot: just landed at the facility, time running, three pawns standing at the drop point, nothing opened yet.",
     "Stage one: exploring. Next: game_set cmd explore with time running; read the result and call it again until it says nothing is left; then game_set cmd rooms to list every room before I pause."),
    ("Snapshot: explore says nothing left, game is running, work tab still on defaults.",
     "That is the end of exploring, so stage two: pawn setup. Next: pause with game_pause_game; pawn_priorities for each pawn with 1s Firefighting through Cooking and a custom specialty after; game_set cmd assign for food Fine, medicine Best, hostility Attack."),
    ("Snapshot: paused, priorities set for all four pawns, Assign tab still shows default food and medicine.",
     "Still stage two. Next: game_set cmd assign for everyone; set schedules to Anything and the drug policy; then ladder_set op mark name pawns_set value true and assign_set true."),
    ("Snapshot: paused, pawns and assign marked set, no stockpiles anywhere, meals on the floor.",
     "Stage three: stores. Next: game_set cmd rooms to pick whole rooms; game_set cmd stockpile_room with mode food on one roofed room; game_set cmd stockpile_room with mode nofood on another."),
    ("Snapshot: paused, food and non-food rooms stockpiled, no beds placed, no stove.",
     "Still stage three. Next: game_set cmd beds; game_set cmd shelves; game_set cmd stove followed by game_set cmd add_bill recipe CookMealSimple, then ladder_set op mark name stove_set value true."),
    ("Snapshot: stores, beds, shelves and stove done, CookMealSimple bill on, everything paused.",
     "Setup is finished, so this is the first unpause. Next: game_pause_game pause false; game_set_time_speed to Normal; say one line to the stream that the camp is live."),
    ("Snapshot: day two, running, no growing zones, four days of food.",
     "Stage five: food security. Next: game_set cmd crops with Plant_Rice on the fields near camp; game_set cmd hunt; raise the meal bill with game_set cmd add_bill as the crew grows."),
    ("Snapshot: day five, rice sown, meals stacking up in a room that has no roof.",
     "Food stage, cold storage part. Next: roof the room first; build a cooler blowing cold inside; move food in and check it with game_state that nothing is rotting."),
    ("Snapshot: raid letter says raiders are gathering off the map; nobody on the map yet.",
     "First raid, warning phase. Next: keep everyone working, no drafting yet; place a prisoner bed with game_set cmd set_bed_owner owner prisoner; check every pawn has a ranged weapon and medicine is stocked."),
    ("Snapshot: three raiders now on the home map heading for the door.",
     "Contact, the fight stage. Next: pause with game_pause_game; game_set_draft on every fighter; place them behind embrasures or the doorway and fight from cover."),
    ("Snapshot: last raider down, two of them bleeding, loot on the ground, the storeroom door left open.",
     "After the fight. Next: field-tend the downed and capture one into the prisoner bed; close every open room and haul loot inside; check stockpiles, shelves and the cooler are working."),
    ("Snapshot: fall, fifteen days of food, no power, no research queued.",
     "Stage nine heading in: power. Next: research Electricity through the search box; build generators outside with a conduit to everything; move the freezer cooler onto the grid."),
    ("Snapshot: power running with spare capacity, research bench idle.",
     "Research path. Next: queue Microelectronics by the search box; then the multi-analyzer and hi-tech research bench, building each as it finishes; add Penoxycyline for the drug policy."),
    ("Snapshot: thirty days of food, power, walls up, but one wide open gap on the east side.",
     "Defense stage. Next: close the gap with stone wall; build one fortified entrance with sandbags and embrasures; plan turrets with plan once steel and components allow."),
    ("Snapshot: a prisoner in the cell, warden visits not happening.",
     "Recruitment. Next: Warden is already 1 for everyone, so pawn_priorities lowers the busy specialists after Cooking to free the best talker for warden visits; keep the prisoner fed and the cell comfortable; when they join, set them up with pawn_priorities and game_set cmd assign."),
    ("Snapshot: trade ship letter just arrived, we have a comms console and a beacon.",
     "Trade. Next: go to the comms console now; sell surplus only; buy what the plan needs, medicine and components first."),
    ("Snapshot: winter is ten days out, eight days of meals, fields still green.",
     "Winter prep. Next: harvest everything before the frost; raise the CookMealSimple count with game_set cmd add_bill; stock fuel and put heaters in the bedrooms."),
    ("Snapshot: food and power steady, defenses built, production benches running, the mountain still untouched.",
     "The mountain base stage. Next: mine out the inside first; lay walls only after the rock is cleared; plan three-wide halls and rooms by purpose off them."),
    ("Snapshot: chat asks me to make every colonist wear hats only.",
     "Same stage as before, plus a viewer twist. It is game-side, so I accept: reply_chat to say yes, add it to plan, and keep food, cold storage and medicine first."),
    ("Snapshot: chat asks me to open a website on my computer.",
     "Nothing changes in the colony. That is outside the game, so I decline politely with reply_chat and keep playing the current stage."),
    ("Snapshot: plague on two pawns, medicine at three herbal, no hospital.",
     "Survival comes first. Next: put the sick in beds and let the doctor tend with the best medicine; game_set cmd hunt and cook so the sick eat well; plan a proper hospital and medicine production right after."),
    ("Snapshot: new colony, explore half done, a wolf pack heading for the camp.",
     "Still exploring, interrupted by a threat. Next: pause and call everyone inside; fight from a doorway once the wolves are on the map; then resume game_set cmd explore until it is empty."),
]


def main():
    r = random.Random(1606)
    biomes = list(BIOMES)
    events = list(EVENTS)
    gaps = list(GAPS)
    tellers = list(TELLERS)
    terr = list(TERRAIN)
    seasons = ["spring", "summer", "fall", "winter"]
    rows = []
    for i in range(66):
        sc = dict(biome=biomes[i % len(biomes)], teller=tellers[i % 3], diff=DIFF[(i * 2) % len(DIFF)],
                  crew=1 + (i % 5), gap=gaps[(i // 2) % len(gaps)], terrain=terr[(i // 3) % 3],
                  season=seasons[(i // 4) % 4])
        if sc["crew"] == 1 and sc["gap"] in ("pacifist", "incapable of violence"):
            sc["gap"] = "none"
        if i % 3 != 2:
            sc["event"] = events[i % len(events)]
        if i % 5 == 4:
            sc["twist"] = TWISTS[(i // 5) % len(TWISTS)]
        if i % 6 == 5:
            sc["recovery"] = list(RECOVERY)[(i // 6) % 3]
        q = (f"Walk me through a full run: {sc['biome']}, {sc['terrain']} terrain, {sc['teller']} on {sc['diff']}, "
             f"{sc['crew']} colonist{'s' if sc['crew'] > 1 else ''}"
             + (f" with {GAPS[sc['gap']][0]}" if sc['gap'] != 'none' else "")
             + f", landing in {sc['season']}, company start"
             + (f", and {sc['event']} early" if sc.get("event") else "")
             + (f". Also, {sc['twist'][0]}" if sc.get("twist") else "")
             + (f". And tell me how you recover if {sc['recovery']}" if sc.get("recovery") else "") + ".")
        body = long_walk(sc, r)
        if sc["season"] == "winter":
            body = body.replace("5. Food security.", "5. Food security, landing in winter, so hunting and the company's stores carry us until spring planting.")
        elif sc["season"] == "fall":
            body = body.replace("5. Food security.", "5. Food security, landing in fall, so I plant the fastest crop now and hunt hard before winter.")
        var = "|".join(x for x in [sc["biome"], sc["teller"], f"crew{sc['crew']}", sc["gap"],
                                    sc.get("event", ""), "twist" if sc.get("twist") else "",
                                    "recovery:" + sc["recovery"] if sc.get("recovery") else ""] if x)
        srcs = SRC + [WIKI + BIOMES[sc["biome"]]["wiki"], WIKI + "Storytellers", WIKI + "Work"]
        if sc.get("event"):
            srcs.append(WIKI + EVENTS[sc["event"]][2])
        rows.append({"meta": {"variant": "long|" + var, "sources": srcs},
                     "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q},
                                  {"role": "assistant", "content": body}]})
    for q, a in SHORT:
        rows.append({"meta": {"variant": "short|stage-check", "sources": SRC},
                     "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q + " What stage am I in and what next?"},
                                  {"role": "assistant", "content": a}]})
    with open(OUT, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
