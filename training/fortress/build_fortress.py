"""Build the fortress training episodes from the owner's 2026-10-10 fortress session.

    python training/fortress/build_fortress.py

Writes training/fortress/samples.jsonl (the 5 reviewed samples, coordinates corrected to the real camp ring
x137-168) and training/fortress/fortress.jsonl (every episode, each with coordinate-shifted variants), then
validates every row: tool names and arguments against training/data/tools.json and training/data/brain/tools.json,
check_player.check_episode, the stream filter on every spoken line, 1-3 sentences per say, and the secret words.
Recipe: training/fortress/ANALYSIS.md. Source lines per episode are in meta.source_lines.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.dirname(HERE)
sys.path.insert(0, TRAIN)
import check_player as cp  # noqa: E402

SYSTEM = json.loads(open(os.path.join(HERE, "samples.jsonl"), encoding="utf-8").readline())["messages"][0]["content"]
SRC = "session 372a4068, 2026-10-10"
VARIANTS = [(0, 0), (-14, 8), (19, -11), (-27, -19)]
SAMPLE_EXTRA = (33, 6)

D = "architect-designator:"
WALL, DOOR, EMB = D + "structure:build-wall", D + "structure:build-door", D + "structure:build-vin-embrasure"
REMB = D + "structure:build-remoteembrasure-close"
CANCEL, DECON, MINE = D + "orders:highlight-designator-cancel", D + "orders:highlight-designator-tutortagnotset", D + "orders:highlight-designator-mine"
PLAN, UNPLAN = D + "orders:highlight-designator-tutortagnotset-18", D + "orders:highlight-designator-tutortagnotset-19"
CUT, CHOP = D + "orders:highlight-designator-tutortagnotset-2", D + "orders:highlight-designator-plantsharvestwood"
SOIL, MARBLE = D + "terraforming:build-soil", D + "terraforming:build-smooth-marble"
GROW, PILE, DUMP = D + "zone:highlight-designator-zoneadd-growing", D + "zone:highlight-designator-zoneaddstockpile-resources", D + "zone:highlight-designator-tutortagnotset-2"
ZCANCEL, ROOF = D + "zone:highlight-designator-cancel", D + "zone:highlight-designator-areabuildroofexpand"
COOLER, TLAMP = D + "temperature:build-passivecooler", D + "furniture:build-torchwalllamp"
SPOT, TABLE, STOOL = D + "furniture:build-sleepingspot", D + "furniture:build-table2x2c", D + "furniture:build-stool"
SHOES, CHESS, GRAVE = D + "joy:build-horseshoespin", D + "joy:build-chesstable", D + "misc:build-grave"
BUTCHER, CRAFT = D + "production:build-butcherspot", D + "production:build-craftingspot"
TAILOR, STONE = D + "production:build-xer-smallhandtailoringbench", D + "production:build-tablestonecutter"
BEACON, CONDUIT = D + "misc:build-orbitaltradebeacon", D + "power:build-hiddenconduit"
SANDBAG, BARRICADE, TURRET = D + "security:build-sandbags", D + "security:build-barricade", D + "security:build-turret-miniturret"
WALLLAMP = D + "furniture:build-walllamp"

GEE, SCAR, UNITY, LLOGA = "Thing_Human1071", "Thing_Human1089", "Thing_Human1102", "Thing_Human1080"


class Ep:
    def __init__(self, turn, user):
        self.m = [{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": "UPDATE (turn %d) -- what is new; your orders from the start of this conversation still stand:\n%s" % (turn, user)}]

    def call(self, why, name, args, result):
        self.m.append({"role": "assistant", "content": why, "tool_calls": [{"function": {"name": name, "arguments": args}}]})
        self.m.append({"role": "tool", "tool_name": name, "content": result if isinstance(result, str) else json.dumps(result)})
        return self

    def ap(self, why, did, x, z, w=1, h=1, applied=None, rejected=0, reason=None, dry=False):
        args = {"designatorId": did, "x": x, "z": z}
        if w != 1 or h != 1:
            args.update(width=w, height=h)
        if dry:
            args["dryRun"] = True
        n = w * h if applied is None else applied
        res = {"success": n > 0, "designatorId": did, "x": x, "z": z, "width": w, "height": h, "appliedCells": n, "rejectedCells": rejected}
        if dry:
            res["dryRun"] = True
        if reason:
            res["reason"] = reason
        return self.call(why, "game_apply_architect_designator", args, res)

    def cells(self, why, x, z, w, h, summary):
        return self.call(why, "game_get_cells_info", {"x": x, "z": z, "width": w, "height": h},
                         {"success": True, "cellCount": w * h, "summary": summary})

    def order(self, why, pid, x, z, option):
        return self.call(why, "order_pawn", {"pawn_id": pid, "x": x, "z": z, "option": option}, "ok: %s -> %s (%d,%d)" % (pid, option, x, z))

    def note(self, why, name, text, append=True):
        args = {"name": name, "text": text}
        if append:
            args["append"] = True
        return self.call(why, "note", args, ("appended to " if append else "wrote ") + name)

    def gset(self, why, args, ok):
        return self.call(why, "game_set", args, "ok: " + ok)

    def say(self, text, emotion, act="statement", why=None):
        return self.call(why or text, "say", {"text": text, "emotion": emotion, "act": act}, "said: " + text)

    def end(self, text):
        self.m.append({"role": "assistant", "content": text})
        return self


def P(x, z):
    return "(%d,%d)" % (x, z)


# ---------------------------------------------------------------------------------------------------------------
# Episodes. Each builder takes X(), Z() (coordinate shift) and returns (Ep, source lines).
# ---------------------------------------------------------------------------------------------------------------

def e_mountain_plan(X, Z, t):
    e = Ep(t, 'OWNER: "Plan your base into the mountain, in that cutout surrounded on three sides. One single door, throne room first, prison and guests either side, tech deeper."\n'
              "MAP: cutout opening at %s, mountain on the west, north and east." % P(X(165), Z(186)))
    e.call("This is a full base layout, so it gets a real plan.", "plan",
           {"what": "Mountain fortress in the north cutout: one door at %s, 3-wide spine north, throne room first, prison wing east and guest wing west, bedrooms and kitchen with freezer deeper, storage and hospital, labs last. Every room keeps 2 cells of rock to the outside." % P(X(165), Z(186))},
           "planning: the game is paused; think it through on your next turn")
    e.cells("Checking the door cell is rock with open ground in front.", X(163), Z(184), 5, 4,
            "z%d-%d soil, no roof; z%d-%d granite rock, overhead mountain" % (Z(184), Z(185), Z(186), Z(187)))
    e.ap("Good. Marking the spine with the plan designator so it shows on stream before anything is dug.", PLAN, X(164), Z(186), 3, 50)
    e.ap("Throne room, 17 by 13, right past the door.", PLAN, X(168), Z(190), 17, 13)
    e.ap("Guest wing to the west.", PLAN, X(148), Z(190), 15, 11)
    e.note("Saving the layout as my build list.", "fortress-plan",
           "Door %s. Spine x%d-%d z%d-%d. Throne %d,%d 17x13. Guests %d,%d 15x11. Next: prison east, bedrooms %d,%d, kitchen and freezer %d,%d, storage %d,%d, labs %d,%d. Food and camp first, dig later."
           % (P(X(165), Z(186)), X(164), X(166), Z(186), Z(235), X(168), Z(190), X(148), Z(190), X(168), Z(205), X(150), Z(203), X(150), Z(216), X(152), Z(236)), append=False)
    e.call("Showing chat the drawing.", "snap", {"x": X(146), "z": Z(184), "w": 40, "h": 56, "caption": "The future mountain fortress, one door only",
                                                 "marks": [{"x": X(165), "z": Z(186), "note": "the only door"}, {"x": X(176), "z": Z(196), "note": "throne room"}]}, "posted")
    e.say("Big plan time. One door into the mountain, throne room first, guests on one side and the prison on the other. We dig once food is sorted.", "excited")
    e.end("Plan is drawn. Food first, digging later.")
    return e, "67748-67765"


def e_throne_redraw(X, Z, t):
    e = Ep(t, 'OWNER: "The entry room is the throne room, centred on the spine. Labs and tech go deeper in, with halls straight off it to the right and left for the prison and the guests, kept separate."\n'
              "PLAN: fortress v1 drawn in the north cutout, door %s, spine x%d-%d." % (P(X(165), Z(186)), X(164), X(166)))
    e.ap("Owner wants the door to open straight into the throne room. Clearing my old plan marks first.", UNPLAN, X(140), Z(180), 60, 75, applied=1436, rejected=3064)
    e.ap("The one door stays where it was.", PLAN, X(165), Z(186))
    e.ap("Throne room, 21 by 13, centred on the spine right past the door.", PLAN, X(156), Z(188), 21, 13)
    e.ap("Hall to the right, east, for the prison wing.", PLAN, X(177), Z(188), 12, 3)
    e.ap("Prison wing at the end of that hall.", PLAN, X(189), Z(186), 14, 12)
    e.ap("Hall to the left, west, for the guests.", PLAN, X(144), Z(188), 12, 3)
    e.ap("Guest wing, kept apart from the prisoners.", PLAN, X(130), Z(186), 14, 12)
    e.ap("The spine carries on north from the throne room.", PLAN, X(164), Z(201), 3, 40)
    e.ap("Labs and tech deep along the spine.", PLAN, X(150), Z(228), 31, 10)
    e.ap("The gate lab at the very back.", PLAN, X(155), Z(241), 21, 10)
    e.note("Replacing the build list with the new layout.", "fortress-plan",
           "v2: door %s opens into the throne room %d,%d 21x13 on the spine. East hall %d,%d to prison %d,%d 14x12. West hall %d,%d to guests %d,%d 14x12. Spine %d,%d 3x40. Labs %d,%d 31x10. Gate lab %d,%d 21x10."
           % (P(X(165), Z(186)), X(156), Z(188), X(177), Z(188), X(189), Z(186), X(144), Z(188), X(130), Z(186), X(164), Z(201), X(150), Z(228), X(155), Z(241)), append=False)
    e.call("Showing chat version two.", "snap", {"x": X(126), "z": Z(182), "w": 80, "h": 72, "caption": "Fortress v2: walk in and you are in my throne room",
                                                 "marks": [{"x": X(165), "z": Z(186), "note": "the one door"}, {"x": X(166), "z": Z(194), "note": "throne room"},
                                                           {"x": X(196), "z": Z(192), "note": "prison wing"}, {"x": X(137), "z": Z(192), "note": "guest wing"}]}, "posted")
    e.say("Fortress version two, chat. Walk through the one door and you are standing in my throne room. Prisoners to the right, guests to the left, never the two shall meet.", "excited")
    e.end("Layout is redrawn the owner's way. Nothing gets dug until food is sorted.")
    return e, "67827-67844"


def e_rock_margin(X, Z, t):
    e = Ep(t, 'OWNER: "Nothing of the base is exposed outside the mountain. Plan the inner room walls too, so keep two cells of mountain around every room, against the outside and between rooms."\n'
              "PLAN: fortress v2 drawn, throne room %d,%d 21x13 right behind the door." % (X(156), Z(188)))
    e.ap("Two cells of rock around every room means the rooms move apart. Clearing the old marks.", UNPLAN, X(120), Z(180), 95, 80, applied=1838, rejected=5762)
    e.ap("Door first, unchanged.", PLAN, X(165), Z(186))
    e.ap("A short 3 by 2 entry behind the door.", PLAN, X(164), Z(187), 3, 2)
    e.ap("Throne room 19 by 13, so its walls sit inside the rock.", PLAN, X(157), Z(190), 19, 13)
    e.ap("East hall to the prison, two cells of rock either side.", PLAN, X(176), Z(194), 14, 3)
    e.ap("Prison wing.", PLAN, X(192), Z(188), 14, 15)
    e.ap("West hall to the guests.", PLAN, X(143), Z(194), 14, 3)
    e.ap("Guest wing.", PLAN, X(127), Z(188), 14, 15)
    e.ap("Spine north, 52 long.", PLAN, X(164), Z(203), 3, 52)
    e.cells("Checking the throne room margin against real outside ground, not cave pockets.", X(155), Z(188), 23, 17,
            "throne rect plus 2 cells: all natural rock or roofed cave pocket, outside ground (no roof) inside the margin: 0")
    e.note("Writing the rule down.", "base-plan", "Fortress rooms are mined out of the rock and keep 2 cells of natural rock to the outside and to every neighbour. The built wall takes the inner cell, the outer cell stays mountain. Corridors and doors cut through the bands.")
    e.say("New rule for the fortress, chat. Every room keeps two cells of solid rock around it, so nothing ever pokes out of the mountain.", "neutral")
    e.end("All rooms redrawn with a rock margin. Next is the camp, not the digging.")
    return e, "68135-68197"


def e_food_first(X, Z, t):
    e = Ep(t, 'OWNER: "Let your people get good on food and set up camp before moving into the base, it will take a while."\n'
              "FORTRESS: mining ordered on the door %s, the 3x3 entry and the 19x13 throne room." % P(X(165), Z(186)))
    e.ap("Right, hours of digging would starve the crew. Cancelling the mining, the plan marks stay.", CANCEL, X(157), Z(186), 19, 17, applied=257, rejected=66)
    e.note("Recording the order of things.", "base-plan", "Camp and food before the fortress: steady food (hunt, rice, berries, cooking) and a working camp first. The fortress plan stays drawn, digging waits.")
    e.say("Change of plans, chat. The fortress stays drawn but no digging yet. First we get fed: rice in the ground, hunting in the jungle and a hot stove.", "neutral")
    e.end("Mining is off. Next: hunting and camp setup.")
    return e, "68237-68261"


def e_ne_farmland(X, Z, t):
    e = Ep(t, 'OWNER: "Terraform the rocky ground in the cutout pockets that already exist to the north east into planting areas."\n'
              "MAP: an enclosed pocket in the north east mountain, about x%d-%d z%d-%d, part rough stone and part soil." % (X(212), X(260), Z(174), Z(196)))
    e.call("Looking up the terraform options first.", "game_list_architect_designators", {"categoryId": "Terraforming"},
           {"success": True, "categoryId": "Terraforming", "designators": [{"id": SOIL, "label": "soil"}, {"id": D + "terraforming:build-soilrich", "label": "rich soil"},
                                                                         {"id": MARBLE, "label": "smooth marble"}]})
    e.ap("Soil over the whole pocket in one rectangle.", SOIL, X(212), Z(174), 49, 23, applied=1018, rejected=109)
    e.ap("That took 1018 cells, so it also re-soils ground that is soil already, wasted work. Cancelling it.", CANCEL, X(212), Z(174), 49, 23, applied=1018, rejected=109)
    e.ap("The soil cells can grow right now, so a growing zone over the pocket. Only fertile cells take it.", GROW, X(212), Z(174), 49, 23, applied=407, rejected=720, reason="Not fertile enough on 720 cells")
    e.note("Writing down what is left.", "base-plan", "North east pocket x%d-%d z%d-%d: 407 soil cells zoned for growing. 337 rough stone cells still need soil, placed strip by strip on the stone only, then the zone grows over them." % (X(212), X(260), Z(174), Z(196)))
    e.say("Hidden farm valley up in the north east, chat. The dirt part is a field already and the rocky part gets turned into soil next.", "happy")
    e.end("Pocket is zoned. Soil on the stone cells comes next.")
    return e, "67767-67844"


def e_wood_firebreak(X, Z, t):
    x0, x1, z0, z1 = X(137), X(168), Z(127), Z(154)
    e = Ep(t, 'OWNER: "Make the camp exterior wall out of wood, and terraform a three wide band of smooth marble outside it as a firebreak."\n'
              "CAMP: planned ring x%d-%d z%d-%d around the shell, gates to be north %s and east %s. Jungle all around." % (x0, x1, z0, z1, P(X(165), z1), P(x1, Z(145))))
    e.call("Checking the terraform list has smooth marble.", "game_list_architect_designators", {"categoryId": "Terraforming"},
           {"success": True, "categoryId": "Terraforming", "designators": [{"id": D + "terraforming:build-smooth-sandstone", "label": "smooth sandstone"}, {"id": MARBLE, "label": "smooth marble"}, {"id": SOIL, "label": "soil"}]})
    e.ap("Wall material is wood already. South side, full width.", WALL, x0, z0, 32, 1)
    e.ap("North side up to the north gate.", WALL, x0, z1, 28, 1)
    e.ap("North side past the gate.", WALL, X(166), z1, 3, 1)
    e.ap("West side between the corners.", WALL, x0, Z(128), 1, 26)
    e.ap("East side below the east gate.", WALL, x1, Z(128), 1, 17)
    e.ap("East side above the gate.", WALL, x1, Z(146), 1, 8)
    e.ap("North gate.", DOOR, X(165), z1)
    e.ap("East gate.", DOOR, x1, Z(145))
    e.ap("Firebreak, three wide, south band.", MARBLE, X(134), Z(124), 38, 3)
    e.ap("North band.", MARBLE, X(134), Z(155), 38, 3)
    e.ap("West band.", MARBLE, X(134), z0, 3, 28)
    e.ap("East band.", MARBLE, X(169), z0, 3, 28)
    e.note("Recording the camp ring.", "base-plan", "Camp: wooden wall ring x%d-%d z%d-%d, 114 cells, gates north %s and east %s. Three wide smooth marble firebreak outside it, 396 cells." % (x0, x1, z0, z1, P(X(165), z1), P(x1, Z(145))))
    e.say("Jungle fires are no joke, chat. The camp gets a wooden wall all the way around, and outside it a strip of smooth marble so a fire stops at my doorstep.", "neutral")
    e.end("Ring and firebreak are placed. Next: get everyone out of the gate room.")
    return e, "68309-68362"


def e_gate_room(X, Z, t):
    e = Ep(t, 'OWNER: "You should not be living in or using the natural gate room. That room gets moved later."\n'
              "CAMP: the crew sleeps on three beds inside the shell (the gate room) at x%d-%d z%d-%d. Open jungle west of it at x%d-%d z%d-%d." % (X(147), X(151), Z(150), Z(151), X(138), X(145), Z(146), Z(152)))
    e.ap("Gate room gets emptied. Marking its beds for deconstruction.", DECON, X(147), Z(150), 5, 2, applied=6, rejected=4)
    e.ap("Clearing the jungle west of the shell for a bunk hut.", CUT, X(138), Z(146), 8, 7, applied=31, rejected=25)
    e.ap("Hut south wall, left of the door.", WALL, X(139), Z(146), 3, 1)
    e.ap("Right of the door.", WALL, X(143), Z(146), 3, 1)
    e.ap("North wall.", WALL, X(139), Z(152), 7, 1)
    e.ap("West wall.", WALL, X(139), Z(147), 1, 5)
    e.ap("East wall.", WALL, X(145), Z(147), 1, 5)
    e.ap("The hut door.", DOOR, X(142), Z(146))
    e.note("Writing the rule down.", "base-plan", "The shell is the natural gate room: nobody sleeps or stores anything in it, it moves into the secure lab later. Crew bunk hut x%d-%d z%d-%d, door %s." % (X(139), X(145), Z(146), Z(152), P(X(142), Z(146))))
    e.say("House rule, chat. The little box with the magic door is not a bedroom and not a closet, so my crew gets their own wooden hut next door.", "neutral")
    e.end("Hut is placed. Beds go in once the walls are up.")
    return e, "68334-68362"


def e_embrasure_ring(X, Z, t):
    x0, x1, z0, z1 = X(137), X(168), Z(127), Z(154)
    gn, ge = (X(165), z1), (x1, Z(145))
    e = Ep(t, 'OWNER: "Make the whole camp wall the non powered embrasure type all the way around, so they can shoot out. Keep the gates."\n'
              "CAMP: wooden wall ring x%d-%d, z%d-%d, gates north %s and east %s. Hostiles: none." % (x0, x1, z0, z1, P(*gn), P(*ge)))
    e.call("Embrasure ids differ between games, so looking it up.", "game_list_architect_designators", {"categoryId": "Structure"},
           {"success": True, "categoryId": "Structure", "designators": [{"id": WALL, "label": "wall"}, {"id": DOOR, "label": "door"}, {"id": EMB, "label": "embrasure"},
                                                                      {"id": REMB, "label": "remote embrasure"}]})
    e.cells("Plain embrasure is the non powered one. Checking what the south wall is right now.", x0, z0, 32, 1, "32 cells: 32 wood wall blueprints, none built")
    e.ap("Still blueprints. South side first.", EMB, x0, z0, 32, 1)
    e.ap("West side between the corners.", EMB, x0, Z(128), 1, 26)
    e.ap("North side up to the north gate, which stays a door.", EMB, x0, z1, 28, 1)
    e.ap("North side past the gate.", EMB, X(166), z1, 3, 1)
    e.ap("East side below the east gate.", EMB, x1, Z(128), 1, 17)
    e.ap("East side above the gate.", EMB, x1, Z(146), 1, 8)
    e.note("Recording the rule so every later build keeps it.", "base-plan",
           "Camp perimeter = non powered wooden embrasures, 114 cells, gates kept at %s and %s. Never build plain wall over the ring." % (P(*gn), P(*ge)))
    e.say("The whole camp wall is firing slits now. Raiders get to meet my crew through little windows. Love that for them.", "amused")
    e.end("Next: doors near the corners so nobody walks around the whole ring.")
    return e, "68374-68416"


def e_side_doors(X, Z, t):
    e = Ep(t, 'OWNER: "Doors on the sides too."\n'
              "CAMP: embrasure ring x%d-%d z%d-%d, gates north %s and east %s only." % (X(137), X(168), Z(127), Z(154), P(X(165), Z(154)), P(X(168), Z(145))))
    e.ap("South side gets a door in the middle. Clearing the embrasure blueprint there first.", CANCEL, X(152), Z(127))
    e.ap("South door.", DOOR, X(152), Z(127))
    e.ap("Same on the west side.", CANCEL, X(137), Z(140))
    e.ap("West door.", DOOR, X(137), Z(140))
    e.note("Adding the doors to the plan.", "base-plan", "Ring doors mid side: south %s, west %s, north gate %s, east gate %s." % (P(X(152), Z(127)), P(X(137), Z(140)), P(X(165), Z(154)), P(X(168), Z(145))))
    e.say("Every side of the camp has a way out now, chat. Nobody gets trapped inside if the jungle catches fire.", "neutral")
    e.end("Four sides, four ways out.")
    return e, "68429-68443"


def e_corner_doors(X, Z, t):
    corners = [(X(137), Z(127)), (X(168), Z(127)), (X(137), Z(154)), (X(168), Z(154))]
    e = Ep(t, 'OWNER: "Doors on the extreme corners will not work. Corners stay embrasures, move the doors in off the corners."\n'
              "CAMP: ring x%d-%d z%d-%d. Doors were placed on the four ring corners %s %s %s %s. North gate %s." % (X(137), X(168), Z(127), Z(154), *[P(*c) for c in corners], P(X(165), Z(154))))
    names = ["south west", "south east", "north west", "north east"]
    e.ap("A corner door has wall on both walk-through sides. South west corner back to an embrasure first.", EMB, *corners[0])
    e.ap("South east corner.", EMB, *corners[1])
    e.ap("North west corner.", EMB, *corners[2])
    e.ap("North east corner. The north gate at %s already sits close to it, so no extra door there." % P(X(165), Z(154)), EMB, *corners[3])
    e.ap("Door two cells in from the %s corner." % names[0], DOOR, X(139), Z(127))
    e.ap("Two in from the %s corner." % names[1], DOOR, X(166), Z(127))
    e.ap("Two in from the %s corner." % names[2], DOOR, X(139), Z(154))
    e.note("Writing the correction down so it sticks.", "base-plan",
           "Ring corners are always embrasures. Corner doors sit two cells in from the corner: %s, %s, %s; the north gate %s serves the north east." % (P(X(139), Z(127)), P(X(166), Z(127)), P(X(139), Z(154)), P(X(165), Z(154))))
    e.say("Okay, corner doors were a bad idea. Corners are firing slits again and the doors moved two cells in.", "amused")
    e.end("Ring is right now. Back to the bunk hut.")
    return e, "68680-68698"


def e_fridge_workshop(X, Z, t):
    e = Ep(t, 'OWNER: "Camp fridge, a workshop, everything you need in the camp, tight, and no blocked paths."\n'
              "CAMP: ring x%d-%d z%d-%d, bunk hut west of the shell, jungle in the north east corner of the camp." % (X(137), X(168), Z(127), Z(154)))
    e.ap("Fridge goes in the north east corner. Clearing the plants.", CUT, X(155), Z(146), 7, 8, applied=31, rejected=25)
    e.ap("Fridge south wall, left of the door.", WALL, X(155), Z(146), 3, 1)
    e.ap("Right of the door.", WALL, X(159), Z(146), 3, 1)
    e.ap("North wall.", WALL, X(155), Z(152), 7, 1)
    e.ap("West wall.", WALL, X(155), Z(147), 1, 5)
    e.ap("East wall.", WALL, X(161), Z(147), 1, 5)
    e.ap("Fridge door.", DOOR, X(158), Z(146))
    e.ap("A passive cooler in the corner, no power needed.", COOLER, X(156), Z(147))
    e.ap("Food stockpile inside.", PILE, X(157), Z(148), 4, 4)
    e.ap("Workshop space east of it.", CUT, X(162), Z(146), 6, 8, applied=29, rejected=19)
    e.ap("Crafting spot against the wall.", CRAFT, X(163), Z(148))
    e.ap("Small tailoring bench.", TAILOR, X(163), Z(151))
    e.ap("Stonecutter.", STONE, X(166), Z(150))
    e.call("Showing chat the layout.", "snap", {"x": X(134), "z": Z(124), "w": 38, "h": 34, "caption": "Camp plan: tight and walkable",
                                                "marks": [{"x": X(158), "z": Z(149), "note": "fridge"}, {"x": X(164), "z": Z(150), "note": "workshop"}, {"x": X(142), "z": Z(149), "note": "bunk hut"}]}, "posted")
    e.say("Camp blueprint is done, chat. Bunk hut, fridge, a little workshop for clothes and stone, and walkways so nobody gets stuck.", "happy")
    e.end("Two-wide walkways kept between buildings. Next: storage settings.")
    return e, "68463-68492"


def e_layout_rules(X, Z, t):
    e = Ep(t, 'OWNER: "Place benches and furniture tight against the inner walls, and in the centre only if the room allows. Keep paths short: kitchen next to the freezer, workshops next to the storage room. Always configure the freezer and dry goods storage properly."\n'
              "CAMP: fridge room x%d-%d z%d-%d with a food pile, workshop east of it, no storage beside the workshop." % (X(155), X(161), Z(146), Z(152)))
    e.ap("The workshop has no storage beside it. Clearing a spot right outside its door.", CUT, X(162), Z(141), 6, 5, applied=10, rejected=20)
    e.ap("Dry goods stockpile next to the workshop.", PILE, X(162), Z(141), 6, 5)
    e.gset("Dry goods take everything except food.", {"cmd": "stockpile_filter", "x": X(162), "z": Z(141), "mode": "nofood", "priority": "Normal"}, "Stockpile zone 3 filter nofood, priority Normal")
    e.gset("The fridge pile takes food only, and it comes first.", {"cmd": "stockpile_filter", "x": X(157), "z": Z(148), "mode": "food", "priority": "Important"}, "Stockpile zone 2 filter food, priority Important")
    e.note("These are standing rules.", "base-plan", "Layout: benches and furniture tight to inner walls, centre only if the room allows. Kitchen beside the freezer, workshops beside storage. Every freezer is food only and Important, dry goods take everything but food.")
    e.say("Rules of the house, chat. Furniture hugs the walls, the kitchen sits by the fridge, and the workshop gets its own storage right outside the door.", "neutral")
    e.end("Storage is set. Back to building.")
    return e, "68559-68583"


def e_raid_backlog(X, Z, t):
    e = Ep(t, 'OWNER: "You have a huge backlog of messages you are not reading. Messages and chat come first."\n'
              "STATE: game clock frozen at tick 324000 for a while. Crew: Gee, Scar, Unity at home inside the camp ring x%d-%d z%d-%d." % (X(137), X(168), Z(127), Z(154)))
    e.call("A frozen clock usually means a letter paused the game. Reading them.", "game_list_letters", {},
           {"success": True, "count": 21, "letters": [{"letterId": "Letter_21", "label": "Raid: Tribe of Lousa", "text": "A group of tribespeople have arrived nearby. They are attacking immediately."},
                                                      {"letterId": "Letter_20", "label": "Something was heard"}]})
    e.call("Raid. Drafting Unity.", "game_set_draft", {"pawnName": "Unity", "drafted": True}, {"success": True, "pawnName": "Unity", "pawnId": UNITY, "drafted": True})
    e.call("Gee.", "game_set_draft", {"pawnName": "Gee", "drafted": True}, {"success": True, "pawnName": "Gee", "pawnId": GEE, "drafted": True})
    e.call("Scar.", "game_set_draft", {"pawnName": "Scar", "drafted": True}, {"success": True, "pawnName": "Scar", "pawnId": SCAR, "drafted": True})
    e.order("The raider is south of camp. Unity one cell inside the south wall.", UNITY, X(153), Z(128), "Go here")
    e.order("Gee next to her.", GEE, X(155), Z(128), "Go here")
    e.order("Scar on the right.", SCAR, X(157), Z(128), "Go here")
    e.say("Chat, raid! A tribal raider showed up south of camp, so everybody to the south wall with rifles up.", "excited", "exclamation")
    e.call("Letting it play out.", "play_slices", {"slices": 2}, "2 slices: one raider, Lloga, went down at %s south of the wall" % P(X(149), Z(132)))
    e.call("Clearing the raid letter now that it is handled.", "game_dismiss_letter", {"letterId": "Letter_21"}, {"success": True, "requestedLetterId": "Letter_21", "dismissed": True})
    e.note("Never again.", "base-plan", "Every loop starts with letters and chat. A raid letter pauses the game, so a frozen clock means read the letters first.")
    e.end("Raid over. Next: tend Lloga where he fell and take him prisoner.")
    return e, "68851-68942"


def e_tend_capture(X, Z, t):
    e = Ep(t, 'OWNER: "Two pawns are not using their rifles, figure it out. And save that raider if you can and imprison him. Always tend them right where they fall before you capture and haul."\n'
              "STATE: Lloga, a tribal scavenger, downed at %s. Crew drafted at the south wall." % P(X(149), Z(132)))
    e.call("Checking what Scar is actually holding.", "pawn_check", {"pawn": "Scar", "tab": "Gear"},
           "Scar: Equipped pain stick (melee). Sidearms: charge rifle. The sidearm mod swaps to melee when an enemy gets close.")
    e.call("The fight is over, so the swap back to rifles happens on its own. Gee is free to work, undrafting him.", "game_set_draft", {"pawnName": "Gee", "drafted": False},
           {"success": True, "pawnName": "Gee", "pawnId": GEE, "drafted": False})
    e.order("Unity tends Lloga right where he fell.", UNITY, X(149), Z(132), "Tend Lloga")
    e.order("Gee takes him prisoner.", GEE, X(149), Z(132), "Imprison Lloga")
    e.note("Saving the owner's rule.", "base-plan", "Downed enemies: tend them where they fall, then capture and haul. Melee swap is the sidearm mod, rifles come back after the fight.")
    e.say("Raid over, chat! Lloga went down at the south wall, and instead of leaving him in the dirt I am patching him up and taking him prisoner.", "happy")
    e.end("He needs a room next. Building a prison cell.")
    return e, "68888-68958"


def e_rock_chunk(X, Z, t):
    e = Ep(t, 'OWNER: "Mine out that rock chunk inside the base before you finish the wall, or someone gets trapped."\n'
              "CAMP: ring x%d-%d z%d-%d, embrasures half built." % (X(137), X(168), Z(127), Z(154)))
    e.cells("Reading the whole inside of the ring for rock.", X(137), Z(127), 32, 28,
            "896 cells: 44 limestone rock cells, all in the south west corner x%d-%d z%d-%d; the rest soil, marsh and gravel" % (X(137), X(143), Z(127), Z(133)))
    e.ap("Mining the outcrop. Only rock takes the order.", MINE, X(137), Z(127), 7, 7, applied=44, rejected=5)
    e.say("There is a lump of limestone in the corner of my camp, chat. Digging it out before the wall closes around somebody.", "neutral")
    e.end("Outcrop is marked for mining.")
    return e, "68914-68942"


def e_prison_swap(X, Z, t):
    e = Ep(t, 'OWNER: "Make that storage room a prison hold, put a sleeping spot in it, and put the storage where the table and chairs are. You might have to move benches."\n'
              "CAMP: walled fridge room x%d-%d z%d-%d, an unfinished prison cell in the south east corner, table and stools at %s." % (X(155), X(161), Z(146), Z(152), P(X(156), Z(138))))
    e.ap("The walled room becomes the prison hold. A sleeping spot inside.", SPOT, X(159), Z(151))
    e.gset("Marking it for prisoners right away.", {"cmd": "set_bed_owner", "x": X(159), "z": Z(151), "owner": "prisoner"}, "sleeping spot at %d,%d now for prisoners" % (X(159), Z(151)))
    e.ap("The separate cell I started in the south east corner is not needed. Cancelling it.", CANCEL, X(161), Z(128), 5, 5, applied=14, rejected=11)
    e.ap("Table and stools come out of the way.", CANCEL, X(155), Z(137), 5, 4, applied=5, rejected=15)
    e.ap("New food room by the stove, south wall.", WALL, X(153), Z(132), 8, 1)
    e.ap("North wall, left of the door.", WALL, X(153), Z(139), 3, 1)
    e.ap("Right of the door.", WALL, X(157), Z(139), 4, 1)
    e.ap("West wall.", WALL, X(153), Z(133), 1, 6)
    e.ap("East wall.", WALL, X(160), Z(133), 1, 6)
    e.ap("Food room door, facing the stove.", DOOR, X(156), Z(139))
    e.ap("Passive cooler inside.", COOLER, X(154), Z(133))
    e.ap("Food pile.", PILE, X(155), Z(134), 5, 5)
    e.gset("Food only.", {"cmd": "stockpile_filter", "x": X(155), "z": Z(134), "mode": "food", "priority": "Important"}, "Stockpile zone 4 filter food, priority Important")
    e.ap("Dining table goes to the south east corner.", TABLE, X(163), Z(130))
    e.say("Remodel time, chat. The walled room becomes Lloga's prison hold, and the food moves next to the stove so the cook barely walks.", "neutral")
    e.end("Prison hold is marked. The two missing walls on it come next.")
    return e, "69025-69042"


def e_force_finish(X, Z, t):
    e = Ep(t, 'OWNER: "Force them to finish the old storage into a prison quickly, before he dies."\n'
              "STATE: Lloga downed outside at %s, 98F. Prison hold x%d-%d z%d-%d." % (P(X(149), Z(132)), X(155), X(161), Z(146), Z(152)))
    e.cells("Reading what is still unbuilt on the prison room.", X(155), Z(146), 7, 7,
            "49 cells: 2 unbuilt wall blueprints %s %s; sleeping spot %s built, for prisoners" % (P(X(155), Z(152)), P(X(156), Z(152)), P(X(159), Z(151))))
    e.order("Only two walls left. Scar takes one.", SCAR, X(155), Z(152), "Prioritize working on wooden wall (blueprint)")
    e.order("Gee takes the other.", GEE, X(156), Z(152), "Prioritize working on wooden wall (blueprint)")
    e.say("Rush job, chat. Lloga is lying in the heat, so Scar and Gee are slapping up the last two walls of his cell right now.", "concerned")
    e.end("Once the room closes, Lloga gets carried in.")
    return e, "69054-69097"


def e_prisoner_lost(X, Z, t):
    e = Ep(t, 'OWNER: "You need to set up a prisoner room first, that is basic."\n'
              "ALERT: Lloga died, downed in the open at 98F before the prison room closed. His body is at %s." % P(X(149), Z(132)))
    e.ap("He needs somewhere to go that is not camp storage. A dumping zone south of the firebreak.", DUMP, X(148), Z(115), 6, 5)
    e.ap("And graves next to it.", GRAVE, X(148), Z(111))
    e.ap("A second grave for whoever is next.", GRAVE, X(150), Z(111))
    e.note("Writing the lesson down.", "base-plan", "Prisoner room first: a closed room with a prisoner bed is built before any fight ends. Lloga died downed in the heat because the room was not ready.")
    e.say("Bad news, chat. Lloga did not make it, he died out in the heat before his cell was ready, and that one is on me.", "sad")
    e.end("Prison room comes first from now on.")
    return e, "69152-69183"


def e_heat(X, Z, t):
    e = Ep(t, 'OWNER: "Your people are in the heat and close to dying. Figure out the temperature problem now, one heat wave and you are all dead."\n'
              "STATE: 98F outside. Bunk hut x%d-%d z%d-%d roofed, food store x%d-%d z%d-%d." % (X(139), X(145), Z(146), Z(152), X(153), X(160), Z(132), Z(139)))
    e.ap("Two passive coolers in the bunk hut.", COOLER, X(144), Z(147))
    e.ap("Second one.", COOLER, X(140), Z(147))
    e.order("Scar builds the first one right now.", SCAR, X(144), Z(147), "Prioritize working on passive cooler (blueprint)")
    e.cells("A cooler only works under a roof. Checking the food store.", X(154), Z(133), 6, 6, "36 cells, no roof on any cell; passive cooler built at %s" % P(X(154), Z(133)))
    e.ap("It is cooling the open sky. Roof area over the food store.", ROOF, X(153), Z(132), 8, 8)
    e.note("Heat plan.", "base-plan", "Heat: passive coolers in every roofed room, and a room only cools once it is walled and roofed. On a heat wave the whole crew goes through the gate into the backrooms until it breaks.")
    e.say("It is ninety eight degrees out here, chat. Coolers are going into every room with a roof, and if a heat wave hits, everybody hides in the backrooms.", "concerned")
    e.end("Coolers are queued and the food store gets its roof.")
    return e, "69201-69475"


def e_farm_plots(X, Z, t):
    e = Ep(t, 'OWNER: "Put farms outside the walls. Minimum berries, potatoes, corn and healroot, plus cotton, smokeleaf, psychoid and hops, so there is lots to sell and produce."\n'
              "MAP: north east pocket x%d-%d z%d-%d, soil, outside the camp wall." % (X(212), X(260), Z(174), Z(196)))
    cells = [116, 126, 108, 92, 124, 121, 36, 21]
    i = 0
    for z0, h in ((174, 11), (185, 12)):
        for x0, w in ((212, 12), (224, 12), (236, 12), (248, 13)):
            e.ap("Plot %d of 8." % (i + 1) if i else "Eight plots in the pocket, one crop each. Plot 1.", GROW, X(x0), Z(z0), w, h, applied=cells[i], rejected=w * h - cells[i])
            i += 1
    e.say("Farm valley update, chat. Eight fields up in the north east: berries, potatoes, corn, healroot, cotton, smokeleaf, psychoid and hops.", "happy")
    e.end("Plots are drawn. Crops get set next.")
    return e, "69263-69294"


def e_merged_field(X, Z, t):
    e = Ep(t, 'OWNER: "Not one massive field, what are you thinking?"\n'
              "FARM: eight plots drawn touching each other in the north east pocket x%d-%d z%d-%d." % (X(212), X(260), Z(174), Z(196)))
    e.call("Checking the zones.", "game_list_zones", {}, {"success": True, "zones": [{"id": "Zone_3", "label": "Growing zone 2", "cellCount": 744}, {"id": "Zone_2", "label": "Growing zone 1", "cellCount": 99}]})
    e.ap("All eight merged into one 744 cell zone, because touching drags join. Removing it.", ZCANCEL, X(212), Z(174), 49, 23, applied=744, rejected=383)
    cells = [95, 104, 95, 101, 30, 64, 94, 65]
    plants = ["Plant_Berry", "Plant_Potato", "Plant_Corn", "Plant_Healroot", "Plant_Cotton", "Plant_Smokeleaf", "Plant_Psychoid", "Plant_Hops"]
    rects = []
    i = 0
    for z0, h in ((174, 10), (185, 11)):
        for x0, w in ((212, 11), (224, 11), (236, 11), (248, 12)):
            e.ap("Redrawing with a one cell walkway between plots. Plot %d." % (i + 1) if not i else "Plot %d, a gap from the last." % (i + 1), GROW, X(x0), Z(z0), w, h, applied=cells[i], rejected=w * h - cells[i])
            rects.append((X(x0) + w // 2, Z(z0) + h // 2))
            i += 1
    for i, (x, z) in enumerate(rects):
        nice = plants[i].replace("Plant_", "").lower()
        e.gset("Plot %d grows %s." % (i + 1, nice), {"cmd": "set_zone_plant", "x": x, "z": z, "plant": plants[i]}, "Growing zone %d now grows %s plant" % (i + 12, nice))
    e.say("Fixed the farm, chat. My eight fields had glued themselves into one giant blob, so now they are eight separate plots with little walkways between them.", "amused")
    e.end("Eight crops, eight plots.")
    return e, "69315-69339"


def e_marsh(X, Z, t):
    e = Ep(t, 'OWNER: "Use terraform to remove the mud and water inside the camp perimeter."\n'
              "CAMP: ring x%d-%d z%d-%d." % (X(137), X(168), Z(127), Z(154)))
    e.cells("Reading the ground inside the wall.", X(138), Z(128), 30, 26,
            "780 cells: soil 581, marshy 61, marsh 5, limestone 57, concrete 49, gravel 27; the wet ground sits at x%d-%d z%d-%d; no open water" % (X(146), X(153), Z(128), Z(136)))
    e.ap("Soil over the wet patch. Cells that are already soil or under a building are skipped.", SOIL, X(146), Z(128), 8, 9, applied=60, rejected=12)
    e.say("No more swamp in my camp, chat. Every muddy tile inside the wall is turning into proper dirt, so nobody slogs through mud carrying dinner.", "happy")
    e.end("Sixty wet cells are getting soil. The other six sit under buildings.")
    return e, "69377-69396"


def e_rec_room(X, Z, t):
    e = Ep(t, 'OWNER: "You need the farms outside the walls, and an entertainment room to keep cool in."\n'
              "CAMP: a rice field still inside the ring at x%d-%d z%d-%d. Firebreak x%d-%d on the west." % (X(140), X(150), Z(130), Z(138), X(134), X(136)))
    e.ap("A farm outside the west wall, past the firebreak. Clearing it first.", CHOP, X(116), Z(141), 16, 10, applied=9, rejected=151)
    e.ap("Growing zone there.", GROW, X(116), Z(141), 16, 10)
    e.ap("Rec room where the inner field was. South wall.", WALL, X(140), Z(130), 11, 1)
    e.ap("North wall, left of the door.", WALL, X(140), Z(138), 5, 1)
    e.ap("Right of the door.", WALL, X(146), Z(138), 5, 1)
    e.ap("West wall.", WALL, X(140), Z(131), 1, 7)
    e.ap("East wall.", WALL, X(150), Z(131), 1, 7)
    e.ap("Door.", DOOR, X(145), Z(138))
    e.ap("A passive cooler so it is the cool room.", COOLER, X(141), Z(131))
    e.ap("Chess table.", CHESS, X(148), Z(136))
    e.say("Upgrades, chat. Farms moved outside the walls where they belong, and I am building a chill room with a cooler and a chess table to hide from the heat.", "happy")
    e.end("Horseshoes move into the rec room next.")
    return e, "69543-69572"


def e_workshop_cool(X, Z, t):
    e = Ep(t, 'OWNER: "And the workshops need to be cool."\n'
              "CAMP: workshop x%d-%d z%d-%d is open to the south; the prison hold and the camp wall close its other sides." % (X(162), X(167), Z(147), Z(153)))
    e.ap("South wall for the workshop, left of the door.", WALL, X(162), Z(146), 2, 1)
    e.ap("Right of the door, stopping one cell short of the camp wall.", WALL, X(165), Z(146), 2, 1)
    e.ap("Workshop door.", DOOR, X(164), Z(146))
    e.ap("Passive cooler inside.", COOLER, X(162), Z(153))
    e.ap("Roof area so the cooler has something to hold in.", ROOF, X(162), Z(147), 6, 7)
    e.say("The workshop gets walls, a roof and a cooler too, chat. No more crafting in a sauna.", "amused")
    e.end("Workshop is enclosed. The dry goods pile sits right outside its door.")
    return e, "69558-69572"


def e_horseshoes(X, Z, t):
    e = Ep(t, 'OWNER: "Put the horseshoe pin up against a wall so its action area is not blocked. At minimum one side has to stay clear."\n'
              "CAMP: rec room x%d-%d z%d-%d, horseshoe pin blueprint in the middle at %s." % (X(140), X(150), Z(130), Z(138), P(X(145), Z(134))))
    e.ap("Cancelling the pin in the middle.", CANCEL, X(145), Z(134))
    e.ap("Against the inside of the west wall, throwing side facing the room.", SHOES, X(141), Z(134))
    e.note("Furniture rule.", "base-plan", "Joy furniture with a play area (horseshoes) goes against a wall so its throwing side stays open.")
    e.say("Horseshoe pin moved against the wall, chat, so there is room to actually throw.", "neutral")
    e.end("Rec room is laid out.")
    return e, "69623-69636"


def e_prioritize(X, Z, t):
    e = Ep(t, 'OWNER: "Work on everything at once. Pause until everything is set, and force the important jobs instead of letting the crew wander onto random chores."\n'
              "CAMP: lots of half built blueprints: coolers, the food room, the rec room, the workshop, the ring.")
    e.call("Pausing while I set it all.", "game_pause_game", {"pause": True}, {"success": True, "paused": True})
    e.cells("Reading the camp for unbuilt jobs.", X(133), Z(124), 32, 32,
            "1024 cells: 76 unbuilt: 44 wall, 24 embrasure, 4 door, 2 passive cooler, 1 horseshoe pin, 1 chess table")
    e.order("Coolers first. Scar on the hut cooler.", SCAR, X(144), Z(147), "Prioritize working on passive cooler (blueprint)")
    e.order("Gee on the food room wall.", GEE, X(153), Z(133), "Prioritize working on wooden wall (blueprint)")
    e.order("Unity on the rec room wall.", UNITY, X(150), Z(131), "Prioritize working on wooden wall (blueprint)")
    e.order("Gee's next job queued behind it.", GEE, X(160), Z(135), "Prioritize working on wooden wall (blueprint)")
    e.call("Everyone has a job. Unpausing.", "game_pause_game", {"pause": False}, {"success": True, "paused": False, "timeSpeed": "Normal"})
    e.say("No more letting them wander around picking random chores, chat. I paused, lined up every job in order, coolers first, and handed each of them a list.", "neutral")
    e.end("When one finishes, the next ranked job goes to whoever is free.")
    return e, "69598-69636"


def e_trapped(X, Z, t):
    e = Ep(t, 'OWNER: "Unity is trapped."\n'
              "STATE: Unity was mining the limestone outcrop in the south west corner of the camp.")
    e.cells("Looking at the cells around her.", X(133), Z(122), 9, 9,
            "81 cells: Unity at %s on a mined cell; rock on every side except a diagonal gap; marble firebreak block at %s" % (P(X(137), Z(126)), P(X(135), Z(130))))
    e.ap("She dug into a pocket that only touches open ground diagonally. Marking the firebreak block for mining.", MINE, X(135), Z(130))
    e.order("Forcing her onto it.", UNITY, X(135), Z(130), "Prioritize mining marble")
    e.say("Okay chat, I dug myself into a little rock closet. Classic. Mining my way out right now.", "amused")
    e.end("One block and she is free.")
    return e, "69912-69949"


def e_lamps(X, Z, t):
    e = Ep(t, 'OWNER: "Get your benches inside, with wall lights. Use wall lights this time, they take no floor space, they sit in the cell in front of the wall. Minimum two lights per room for full brightness."\n'
              "CAMP: stove, research bench and butcher spot stand outside at x%d-%d z%d-%d." % (X(152), X(161), Z(139), Z(146)))
    e.ap("Butcher spot moves inside the new kitchen.", BUTCHER, X(153), Z(144))
    e.ap("Kitchen west wall below the door.", WALL, X(152), Z(139), 1, 3)
    e.ap("West wall above the door.", WALL, X(152), Z(143), 1, 4)
    e.ap("Kitchen door.", DOOR, X(152), Z(142))
    e.ap("Testing a wall lamp on the hut wall itself.", TLAMP, X(141), Z(152), dry=True, applied=0, rejected=1, reason="This object cannot be placed here.")
    e.ap("Right, it goes in the cell in front of the wall.", TLAMP, X(141), Z(151), dry=True)
    e.ap("Hut, first lamp.", TLAMP, X(141), Z(151))
    e.ap("Hut, second lamp.", TLAMP, X(143), Z(151))
    e.ap("Food store, two lamps.", TLAMP, X(155), Z(138))
    e.ap("Second.", TLAMP, X(158), Z(138))
    e.ap("Kitchen.", TLAMP, X(154), Z(145))
    e.ap("Second.", TLAMP, X(159), Z(145))
    e.note("Lamp rule.", "base-plan", "Every room gets at least two wall lamps, placed in the cell in front of the wall. Torch wall lamps until power, electric after.")
    e.say("Lighting upgrade, chat. Every room gets two little torch lamps on the walls, and the stove finally gets a real kitchen.", "happy")
    e.end("Prison, rec room and workshop lamps next.")
    return e, "70115-70157"


def e_priorities(X, Z, t):
    e = Ep(t, 'OWNER: "Set up priorities. The pawns have none set."\n'
              "CREW: Gee (scientist, cook), Scar (builder, crafter), Unity (miner, shooter). Manual priorities off.")
    e.call("Gee: research first, cooking next.", "pawn_priorities", {"pawn": "Gee", "custom": {"Research": 1, "Growing": 2, "Construction": 3, "Hauling": 3, "Cleaning": 3}},
           "Gee: 20/20 work types set (1s Firefighter..Cooking, rest as given, none blank)")
    e.call("Scar builds and crafts.", "pawn_priorities", {"pawn": "Scar", "custom": {"Construction": 1, "Crafting": 2, "Smithing": 2, "Tailoring": 2, "Hauling": 3}},
           "Scar: 20/20 work types set (1s Firefighter..Cooking, rest as given, none blank)")
    e.call("Unity mines, hunts and hauls.", "pawn_priorities", {"pawn": "Unity", "custom": {"Mining": 1, "Hunting": 2, "Hauling": 2, "Construction": 3}},
           "Unity: 20/20 work types set (1s Firefighter..Cooking, rest as given, none blank)")
    e.gset("Gee cooks at 2, not 1.", {"cmd": "set_work_priority", "pawn": "Gee", "work": "Cooking", "level": 2}, "Gee Cooking = 2")
    e.note("Every new pawn gets this.", "base-plan", "Work priorities: Gee Research 1 Cook 2, Scar Construction 1 Craft Smith Tailor 2, Unity Mining 1 Hunt Haul 2. Every new pawn gets a full pass the moment they join.")
    e.say("Job assignments are done, chat. Gee is the brain and the cook, Scar builds everything, and I dig and shoot.", "happy")
    e.end("Priorities set for all three.")
    return e, "70195-70258"


def e_table_rec(X, Z, t):
    e = Ep(t, 'OWNER: "Move the table and chairs into the game room. The centre room of the camp needs finishing."\n'
              "CAMP: dining table in the south east corner at %s, rec room x%d-%d z%d-%d." % (P(X(163), Z(130)), X(140), X(150), Z(130), Z(138)))
    e.ap("Clearing the corner table and stools.", CANCEL, X(161), Z(128), 7, 6, applied=5, rejected=37)
    e.ap("Table in the rec room.", TABLE, X(146), Z(132))
    e.ap("Stool west of it.", STOOL, X(145), Z(132))
    e.ap("Stool east.", STOOL, X(148), Z(132))
    e.ap("Two along the north side.", STOOL, X(146), Z(134))
    e.ap("Last one.", STOOL, X(147), Z(134))
    e.say("Dinner moves into the chill room, chat. Food, chess and air that does not cook you.", "happy")
    e.end("The rec room is the dining room now.")
    return e, "70550-70562"


def e_six_fields(X, Z, t):
    e = Ep(t, 'OWNER: "Do not sow the fields far away at the planned base until we move in. For now set the crops in 6x6 fields around the camp."\n'
              "FARM: eight plots in the far north east pocket starting at %s. Camp ring x%d-%d z%d-%d, firebreak three wide outside it." % (P(X(217), Z(179)), X(137), X(168), Z(127), Z(154)))
    e.gset("Sowing off on the far plots, first one.", {"cmd": "set_zone_sowing", "x": X(217), "z": Z(179), "allow": False}, "Growing zone 12 sowing off")
    e.gset("Second.", {"cmd": "set_zone_sowing", "x": X(229), "z": Z(179), "allow": False}, "Growing zone 13 sowing off")
    fields = [((126, 129), 1), ((126, 136), 18), ((126, 143), 36), ((126, 150), 36), ((173, 129), 16), ((173, 136), 36), ((173, 143), 36), ((173, 150), 30)]
    for i, ((x, z), n) in enumerate(fields):
        e.ap("6x6 field west of the camp, past the firebreak." if i == 0 else ("6x6 east of the camp." if i == 4 else "Next 6x6."), GROW, X(x), Z(z), 6, 6, applied=n, rejected=36 - n)
    e.say("Farm plan changed, chat. The big valley fields wait for the fortress, and the camp gets little six by six fields all around it.", "neutral")
    e.end("The first west field only took one cell, the ground there is bad. It gets soil next.")
    return e, "70550-70562"


def e_walls_over_embrasures(X, Z, t):
    e = Ep(t, 'OWNER: "Why are you putting walls up against the embrasures and replacing them? That will not work, fix those walls."\n'
              "CAMP: new storage room walls were placed out to x%d, the east perimeter, and a wall column at x%d right behind the west embrasures." % (X(168), X(138)))
    e.cells("Looking at the east ring column to see what my storage walls did.", X(168), Z(138), 1, 11,
            "%s embrasure; %s-%d wooden wall built over the embrasures and over the east gate %s; wall blueprints %s-%d; %s embrasure"
            % (P(X(168), Z(138)), P(X(168), Z(140)), Z(146), P(X(168), Z(145)), P(X(168), Z(139)), Z(147), P(X(168), Z(148))))
    e.ap("My storage ring ran onto the perimeter. Cancelling those wall blueprints first.", CANCEL, X(168), Z(139), 1, 9, applied=6, rejected=3)
    e.ap("Tearing out the wall that got built over the embrasures and the gate.", DECON, X(168), Z(140), 1, 7)
    e.ap("The interior run has to stop one cell short of the ring.", DECON, X(167), Z(146))
    e.ap("The column behind the west embrasures seals the crew off from their own firing lane. Out it goes.", DECON, X(138), Z(140), 1, 7)
    e.cells("Checking the east column reads right now.", X(168), Z(138), 1, 11,
            "%s-%d embrasure; %s door, the east gate; %s-%d embrasure; interior wall ends at %s" % (P(X(168), Z(138)), Z(144), P(X(168), Z(145)), P(X(168), Z(146)), Z(148), P(X(167), Z(146))))
    e.note("Rule for next time.", "base-plan", "The camp perimeter is never another room's wall. An inner room uses the ring as its outer side and puts no wall of its own there. Embrasures stay embrasures, gates stay gates, the lane behind them stays walkable.")
    e.say("I walled over my own firing slits. Fixed it, the east side shoots again and the gate opens.", "frustrated")
    e.end("Perimeter is clean again.")
    return e, "72436-72480"


def e_raid_positions(X, Z, t):
    e = Ep(t, 'OWNER: "You need to move people to the embrasures to shoot the bad guys."\n'
              "ALERT: raid, 3 tribals approaching from the south. Crew: Gee, Scar, Unity, all undrafted. Camp ring x%d-%d z%d-%d, south door %s." % (X(137), X(168), Z(127), Z(154), P(X(152), Z(127))))
    e.call("Raid from the south. Getting pawn ids first.", "game_list_colonists", {"currentMapOnly": True},
           {"success": True, "colonists": [{"name": "Gee", "pawnId": GEE}, {"name": "Scar", "pawnId": SCAR}, {"name": "Unity", "pawnId": UNITY}]})
    e.call("Drafting Gee.", "game_set_draft", {"pawnName": "Gee", "drafted": True}, {"success": True, "pawnName": "Gee", "pawnId": GEE, "drafted": True})
    e.call("Scar too.", "game_set_draft", {"pawnName": "Scar", "drafted": True}, {"success": True, "pawnName": "Scar", "pawnId": SCAR, "drafted": True})
    e.order("Gee one cell inside the south embrasure at %s." % P(X(150), Z(127)), GEE, X(150), Z(128), "Go here")
    e.order("Scar on the next slit east, so they cover the south door together.", SCAR, X(156), Z(128), "Go here")
    e.say("Raiders from the south and my crew is behind the firing slits. Come closer, I dare you.", "excited", "exclamation")
    e.call("Letting it play out a little.", "play_slices", {"slices": 1}, "1 slice: raiders reached the firebreak; Gee and Scar firing through the embrasures")
    e.end("Holding at the south wall until the raid breaks.")
    return e, "68851-68942, 59805-59856"


def e_no_material(X, Z, t):
    e = Ep(t, "STATE: Scar has Construction 1 but is playing horseshoes. 30 blueprints waiting in the camp ring x%d-%d z%d-%d. Alerts: Low medicine, Medical treatment needed." % (X(137), X(168), Z(127), Z(154)))
    e.cells("Scar idling with build jobs open is a tell. Checking what material is in camp.", X(132), Z(124), 22, 22, "484 cells: wood logs 2, steel 1; 30 blueprints waiting")
    e.ap("Nothing to build with. Chopping trees in a band west of camp.", CHOP, X(120), Z(120), 16, 20, applied=21, rejected=299)
    e.ap("East band.", CHOP, X(172), Z(120), 16, 20, applied=18, rejected=302)
    e.ap("South band.", CHOP, X(134), Z(100), 20, 16, applied=17, rejected=303)
    e.ap("North band.", CHOP, X(134), Z(158), 20, 16, applied=13, rejected=307)
    e.say("Found it, chat. The camp has two logs of wood, so nobody can build anything. Sixty nine trees are coming down right now.", "surprised")
    e.end("Wood flows to the blueprints as the trees fall.")
    return e, "72394-72430"


def e_raid_prepping(X, Z, t):
    e = Ep(t, "ALERT: letters Raid: Tomahawk Rig (preparing). Hostiles on the map: none. Gee, Scar and Unity drafted and standing still inside the camp at %s %s %s." % (P(X(156), Z(142)), P(X(148), Z(140)), P(X(152), Z(129))))
    e.call("The raiders are still preparing and nobody is on the map. Standing drafted wastes the window. Undrafting Unity.", "game_set_draft", {"pawnName": "Unity", "drafted": False},
           {"success": True, "pawnName": "Unity", "pawnId": UNITY, "drafted": False})
    e.call("Scar.", "game_set_draft", {"pawnName": "Scar", "drafted": False}, {"success": True, "pawnName": "Scar", "pawnId": SCAR, "drafted": False})
    e.call("Gee.", "game_set_draft", {"pawnName": "Gee", "drafted": False}, {"success": True, "pawnName": "Gee", "pawnId": GEE, "drafted": False})
    e.say("Pirates are getting ready somewhere out there, chat, but nobody is here yet. Back to work until they actually show up.", "neutral")
    e.end("Drafting again the moment a hostile spawns.")
    return e, "72386-72391"


def e_barricades(X, Z, t):
    e = Ep(t, "ALERT: Need defenses. Base shop with its single entrance on the south side, door at %s. Steel and components saved for the gate." % P(X(143), Z(133)))
    e.ap("A mini turret would eat steel the gate needs. Dry run on wood barricades by the south door.", BARRICADE, X(139), Z(134), 4, 1, dry=True)
    e.ap("Barricades west of the door.", BARRICADE, X(139), Z(134), 4, 1)
    e.ap("And east of it, a firing line toward the approach.", BARRICADE, X(144), Z(134), 4, 1)
    e.say("Defense time, chat. Wooden barricades on both sides of the front door, so anybody walking in gets shot at from cover.", "neutral")
    e.end("Eight barricades placed. A turret once steel allows.")
    return e, "15745-15774"


def e_perimeter(X, Z, t):
    e = Ep(t, 'OWNER: "Your base is badly designed. Plan it properly."\n'
              "BASE: a shop box with rooms stuck onto the outside. Slate is the remembered wall material. Limestone mountain on the east side around x%d z%d-%d." % (X(182), Z(136), Z(145)))
    e.ap("Goal one, a perimeter wall around the whole site. North side.", WALL, X(120), Z(176), 63, 1)
    e.ap("South side, west of the entrance.", WALL, X(120), Z(136), 22, 1)
    e.ap("South side, east of the entrance.", WALL, X(145), Z(136), 38, 1)
    e.ap("West side.", WALL, X(120), Z(137), 1, 39)
    e.ap("East side.", WALL, X(182), Z(137), 1, 39, applied=36, rejected=3)
    e.ap("The east wall runs over solid limestone, which is already wall. Cancelling the blueprints on rock.", CANCEL, X(182), Z(136), 1, 10)
    e.note("The plan, written down.", "base-goals", "1 perimeter wall, one entrance south. 2 killbox at that entrance. 3 a 3-wide main hall north of the shop, every room comes off it. 4 kitchen beside the freezer. 5 workshops and research off the hall. 6 guest wing. 7 gate facility deepest inside.", append=False)
    e.say("Fair, chat, the base was a box with rooms glued to the outside. Now there is a real plan, starting with a wall around everything and one way in.", "neutral")
    e.end("Perimeter is laid. Killbox next.")
    return e, "15798-15894"


def e_killbox(X, Z, t):
    e = Ep(t, "PLAN: goal two, a killbox inside the 3-wide south entrance at x%d-%d z%d. Perimeter wall placed." % (X(141), X(145), Z(136)))
    e.ap("Staggered sandbags inside the entrance. First.", SANDBAG, X(141), Z(138))
    e.ap("Second, the other side.", SANDBAG, X(145), Z(138))
    e.ap("Middle one.", SANDBAG, X(143), Z(140), applied=0, rejected=1, reason="Space already occupied")
    e.ap("That cell is taken. Second row instead.", SANDBAG, X(141), Z(142))
    e.ap("Last sandbag.", SANDBAG, X(145), Z(142))
    e.ap("A turret on each side. West.", TURRET, X(139), Z(139))
    e.ap("East.", TURRET, X(147), Z(139))
    e.ap("Hidden conduit to power them.", CONDUIT, X(139), Z(138), 9, 1)
    e.say("Killbox time, chat. Anybody who walks in the front door has to zigzag through sandbags while two turrets say hello.", "excited")
    e.end("Killbox is laid. The main hall comes next.")
    return e, "15896-15912"


def e_walls_on_water(X, Z, t):
    e = Ep(t, 'OWNER: "All those walls on top of water need to be cancelled. Terraform those cells to dirt first."\n'
              "BASE: perimeter and hall wall blueprints placed, some on marsh along the west wall x%d z%d-%d." % (X(120), Z(155), Z(167)))
    e.cells("Reading the west wall cells.", X(120), Z(155), 1, 13, "13 cells: 13 wall blueprints on marshy terrain")
    e.ap("All thirteen sit on marsh. Cancelling them.", CANCEL, X(120), Z(155), 1, 13)
    e.ap("Terraforming those cells to soil.", SOIL, X(120), Z(155), 1, 13)
    e.cells("Checking the east wall stretch too.", X(182), Z(160), 1, 12, "12 cells: 12 wall blueprints on marshy terrain")
    e.ap("Same treatment.", CANCEL, X(182), Z(160), 1, 12)
    e.ap("Soil there.", SOIL, X(182), Z(160), 1, 12)
    e.note("Rule.", "base-plan", "Never build a wall on marsh or water. Cancel it, terraform the cell to soil, re-lay the wall once the soil is down.")
    e.say("Walls on swamp would just sink, chat. Cancelled them, the mud turns into proper dirt first, then the walls go back.", "neutral")
    e.end("Walls go back on once the soil is done.")
    return e, "16048-16149"


def e_roofs(X, Z, t):
    e = Ep(t, 'OWNER: "Zone things in right, like roofs, so courtyards stay unroofed. And generators need to be outside."\n'
              "BASE: main hall walls at z%d and z%d from x%d to x%d. Wood-fired generator planned in the east yard at %s." % (Z(165), Z(169), X(121), X(181), P(X(176), Z(149))))
    e.ap("Roof area over the hall only, nothing over the open yard.", ROOF, X(121), Z(165), 61, 5)
    e.ap("Hidden conduit from the yard generator to the freezer line.", CONDUIT, X(174), Z(149), 1, 6)
    e.note("Rule.", "base-plan", "Roof areas only over rooms and halls, courtyards stay open. Generators stand outside in a yard, never in a room.")
    e.say("Roofs go over rooms only, chat, the courtyards stay open sky, and the generator lives outside where it belongs.", "neutral")
    e.end("Hall is roofed and the generator is wired from the yard.")
    return e, "16060-16253"


def e_bastions(X, Z, t):
    e = Ep(t, 'OWNER: "Use rows of five embrasures, not three, more angle. And build the bastions from the wall outward, not inward, with embrasures on all sides."\n'
              "BASE: city wall south side along z%d from x%d to x%d. One bastion goes at x%d." % (Z(64), X(108), X(192), X(124)))
    e.ap("Bastions project out from the wall. Front row, five wide.", REMB, X(122), Z(60), 5, 1)
    e.ap("West flank, embrasures so it fires along the wall.", REMB, X(121), Z(60), 1, 4)
    e.ap("East flank.", REMB, X(127), Z(60), 1, 4)
    e.ap("Door through the city wall into it.", DOOR, X(124), Z(64))
    e.ap("Roof over the bastion.", ROOF, X(121), Z(60), 7, 4)
    e.note("Bastion rule.", "base-plan", "Bastions stick out from the wall like a star fort: 7 wide, 4 deep, five embrasures on the front and embrasures on both flanks, a door through the wall. Corners get 7x7 bastions centred on the corner.")
    e.say("Wider gun slits, chat. Each bastion sticks out from the wall now with five firing slits up front and more on the sides, so nobody hugs the wall safely.", "excited")
    e.end("Same pattern for the rest of the bastions.")
    return e, "41180-41322"


def e_holes_power(X, Z, t):
    e = Ep(t, 'OWNER: "You have holes in your embrasure fortifications, and a bunch have no power so you cannot shoot out."\n'
              "BASE: remote embrasure bastions around the city wall; the west bastion around x%d z%d." % (X(106), Z(103)))
    e.cells("Scanning the west bastion ring for gaps.", X(104), Z(99), 5, 9, "45 cells: remote embrasures all around except %s, open ground; the inner side faces the base on purpose" % P(X(106), Z(103)))
    e.ap("One real hole. Filling it.", REMB, X(106), Z(103))
    e.ap("Hidden conduit under the west wall so this bastion gets power.", CONDUIT, X(108), Z(82), 1, 30)
    e.ap("And along the south wall to the next bastions.", CONDUIT, X(109), Z(64), 30, 1)
    e.say("Found it, chat. Some gun bastions had no power, so the slits could not open. Hidden wiring is going in under the walls and the hole in the west bastion is plugged.", "neutral")
    e.end("Next raid, every slit opens.")
    return e, "57003-57124"


def e_beacons(X, Z, t):
    e = Ep(t, 'OWNER: "Make sure all storage zones, shelves and items are within an orbital trade beacon. You might need to move or add some."\n'
              "BASE: warehouse around %s, freezer around %s, storeroom around %s." % (P(X(135), Z(85)), P(X(163), Z(91)), P(X(157), Z(86))))
    e.ap("A beacon in the warehouse.", BEACON, X(135), Z(85))
    e.ap("The freezer.", BEACON, X(163), Z(91))
    e.ap("The storeroom.", BEACON, X(157), Z(86))
    e.note("Trade rule.", "base-plan", "Every storage room has one orbital trade beacon so traders see everything. One per room is enough.")
    e.say("Trade beacons going into the warehouse, the freezer and the storeroom, chat. Once they are up, every trader sees every item we own.", "neutral")
    e.end("Three beacons queued, one per room.")
    return e, "56939-56974"


def e_tower_raid(X, Z, t):
    e = Ep(t, "ALERT: raid, four hostiles creeping up on the south west wall near the corner tower at %s. Crew: Gee, Scar, Unity." % P(X(108), Z(64)))
    e.call("Drafting Unity.", "game_set_draft", {"pawnName": "Unity", "drafted": True}, {"success": True, "pawnName": "Unity", "pawnId": UNITY, "drafted": True})
    e.call("Scar.", "game_set_draft", {"pawnName": "Scar", "drafted": True}, {"success": True, "pawnName": "Scar", "pawnId": SCAR, "drafted": True})
    e.call("Gee.", "game_set_draft", {"pawnName": "Gee", "drafted": True}, {"success": True, "pawnName": "Gee", "pawnId": GEE, "drafted": True})
    e.order("Everybody into the corner tower behind the embrasures.", UNITY, X(108), Z(64), "Go here")
    e.order("Scar next to her.", SCAR, X(109), Z(65), "Go here")
    e.order("Gee on the inside cell.", GEE, X(109), Z(66), "Go here")
    e.say("Hostiles, chat! Four of them creeping up on the south west wall. Everybody into the corner tower, rifles through the embrasures.", "excited", "exclamation")
    e.call("Letting the fight run.", "play_slices", {"slices": 4}, "4 slices: hostiles reached the wall, then pulled back south to %s %s %s %s" % (P(X(111), Z(40)), P(X(103), Z(44)), P(X(103), Z(52)), P(X(117), Z(52))))
    e.say("Look at them run! One taste of the tower and they are backing off. Stay sharp, they might regroup.", "amused", "exclamation")
    e.end("Holding the tower until they leave the map.")
    return e, "59805-59856"


def e_tower_rebuild(X, Z, t):
    e = Ep(t, 'OWNER: "Fix the destroyed fortifications, walls and embrasures."\n'
              "BASE: south west corner tower x%d-%d z%d-%d took raid damage; its west column and south face are gone." % (X(105), X(111), Z(61), Z(67)))
    e.cells("Reading the tower.", X(105), Z(61), 7, 7, "49 cells: west column x%d z%d-%d rubble, south face z%d x%d-%d rubble, roof missing over the middle" % (X(105), Z(61), Z(67), Z(61), X(106), X(111)))
    e.ap("West column back.", REMB, X(105), Z(61), 1, 7)
    e.ap("South face.", REMB, X(106), Z(61), 6, 1)
    e.ap("Roof back over the tower.", ROOF, X(106), Z(62), 5, 5)
    e.say("Patching up my corner tower, chat. New firing slits on the west and south faces and a roof back on top.", "neutral")
    e.end("Tower is queued for repair.")
    return e, "60036-60374"


def e_tower_lights(X, Z, t):
    e = Ep(t, 'OWNER: "Embrasures leak air, so the towers will not hold temperature. They need lights though."\n'
              "BASE: gun towers with embrasures all around, south west tower interior at %s." % P(X(107), Z(63)))
    e.call("Finding the lamp options.", "game_list_architect_designators", {"categoryId": "Furniture"},
           {"success": True, "categoryId": "Furniture", "designators": [{"id": TLAMP, "label": "torch wall lamp"}, {"id": WALLLAMP, "label": "wall lamp"}]})
    e.ap("A wall lamp inside the south west tower.", WALLLAMP, X(107), Z(63))
    e.ap("Second one, two per room.", WALLLAMP, X(109), Z(63))
    e.note("Tower rule.", "base-plan", "Towers with embrasures leak air, so no coolers or heaters in them. They still get two lamps each.")
    e.say("Gun towers will never hold air with all those slits, chat, so no coolers in there. They do get lights.", "neutral")
    e.end("Lamps go into every tower the same way.")
    return e, "61457-61487"


def e_chat_first(X, Z, t):
    e = Ep(t, 'OWNER: "People are talking to you, always answer them first."\n'
              'CHAT: [chat_id 4417] viewer_m: "what is flooring?"\n'
              "BASE: tower exit doors being placed along the city wall.")
    e.call("Chat first.", "reply_chat", {"chat_id": 4417, "viewer": "viewer_m", "text": "Flooring is what you lay on the ground in rooms. Nice floors make rooms prettier and easier to clean.", "emotion": "warm", "act": "statement"},
           "replied: viewer_m, Flooring is what you lay on the ground in rooms. Nice floors make rooms prettier and easier to clean.")
    e.say("Back to the walls, chat. Every gun tower gets its own exit door on the outside face.", "neutral")
    e.end("Chat answered, back to the towers.")
    return e, "60865-60869"


EPISODES = [
    (e_mountain_plan, 255, 3), (e_ne_farmland, 257, None), (e_throne_redraw, 258, None), (e_rock_margin, 262, None), (e_food_first, 266, None),
    (e_wood_firebreak, 290, None), (e_gate_room, 293, None), (e_embrasure_ring, 301, 1), (e_side_doors, 310, None), (e_corner_doors, 318, 2),
    (e_fridge_workshop, 322, None), (e_layout_rules, 330, None), (e_raid_backlog, 352, None), (e_tend_capture, 356, None), (e_rock_chunk, 358, None),
    (e_prison_swap, 366, None), (e_force_finish, 371, None), (e_prisoner_lost, 375, None), (e_heat, 380, None), (e_farm_plots, 388, None),
    (e_merged_field, 390, None), (e_marsh, 395, None), (e_rec_room, 402, None), (e_workshop_cool, 404, None), (e_prioritize, 408, None),
    (e_horseshoes, 410, None), (e_raid_positions, 420, 5), (e_trapped, 430, None), (e_lamps, 440, None), (e_priorities, 450, None),
    (e_table_rec, 470, None), (e_six_fields, 472, None), (e_walls_over_embrasures, 402, 4), (e_no_material, 520, None), (e_raid_prepping, 515, None),
    (e_barricades, 140, None), (e_perimeter, 150, None), (e_killbox, 152, None), (e_walls_on_water, 160, None), (e_roofs, 162, None),
    (e_bastions, 210, None), (e_holes_power, 230, None), (e_beacons, 228, None), (e_tower_raid, 240, None), (e_tower_rebuild, 244, None),
    (e_tower_lights, 246, None), (e_chat_first, 245, None),
]

COORD_KEYS = ("x", "z")


def build(fn, turn, dx, dz):
    X = lambda v: v + dx  # noqa: E731
    Z = lambda v: v + dz  # noqa: E731
    e, src = fn(X, Z, turn)
    return e.m, src


def in_bounds(msgs):
    bad = []
    for m in msgs:
        for c in m.get("tool_calls") or []:
            a = c["function"]["arguments"]
            for k in ("x", "z"):
                if k in a and not (0 <= a[k] < 300):
                    bad.append((c["function"]["name"], k, a[k]))
            w, h = a.get("width", a.get("w", 1)), a.get("height", a.get("h", 1))
            if "x" in a and a["x"] + w > 300 or "z" in a and a["z"] + h > 300:
                bad.append((c["function"]["name"], "rect", a))
    return bad


def sentences(t):
    return len([s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s])


def validate(ep, secret, schemas):
    errs = list(cp.check_episode(ep, secret))
    for m in ep["messages"]:
        for c in m.get("tool_calls") or []:
            f = c["function"]
            for label, sch in schemas.items():
                if f["name"] not in sch:
                    errs.append("%s: unknown tool %s" % (label, f["name"]))
                else:
                    errs += ["%s %s: %s" % (label, f["name"], e) for e in cp.validate(f["arguments"], sch[f["name"]])]
            if f["name"] in ("say", "reply_chat"):
                a = f["arguments"]
                if not (1 <= sentences(a["text"]) <= 3):
                    errs.append("say not 1-3 sentences: %r" % a["text"])
                if "emotion" not in a or "act" not in a:
                    errs.append("say without emotion/act")
    blob = json.dumps(ep, ensure_ascii=False).lower()
    if "forever11231" in blob:
        errs.append("owner handle")
    for m in ep["messages"][1:]:
        if cp.dirty(m.get("content") or "") and m["role"] != "tool":
            errs.append("dirty %s line" % m["role"])
    errs += ["out of bounds: %r" % (b,) for b in in_bounds(ep["messages"])]
    return errs


def main():
    secret = cp.secrets()
    schemas = {}
    for label, rel in (("tools.json", ("data", "tools.json")), ("brain/tools.json", ("data", "brain", "tools.json"))):
        schemas[label] = {t["function"]["name"]: t["function"]["parameters"] for t in json.load(open(os.path.join(TRAIN, *rel), encoding="utf-8"))}
    rows, samples, fails = [], {}, 0
    for idx, (fn, turn, sample) in enumerate(EPISODES, 1):
        offs = list(VARIANTS) + ([SAMPLE_EXTRA] if sample else [])
        for v, (dx, dz) in enumerate(offs):
            msgs, src = build(fn, turn + 37 * v, dx, dz)
            meta = {"category": "fortress", "source": SRC + ", transcript lines " + src, "source_lines": src, "episode": fn.__name__[2:], "episode_no": idx,
                    "variant": v, "shift": [dx, dz]}
            if sample:
                meta["sample"] = sample
            ep = {"tools": "TOOLS", "meta": meta, "kind": "fortress", "messages": msgs}
            errs = validate(ep, secret, schemas)
            if errs:
                fails += 1
                print("FAIL %s v%d:" % (fn.__name__, v))
                for e in errs[:6]:
                    print("   ", e)
            rows.append(ep)
            if sample and v == 0:
                samples[sample] = {"tools": "TOOLS", "meta": {"category": "fortress", "source": SRC + ", transcript lines " + src, "sample": sample}, "kind": "fortress", "messages": msgs}
    with open(os.path.join(HERE, "fortress.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(HERE, "samples.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for k in sorted(samples):
            f.write(json.dumps(samples[k], ensure_ascii=False) + "\n")
    print("%d episodes, %d rows, %d samples, %d failing, %d secret word(s) checked" % (len(EPISODES), len(rows), len(samples), fails, len(secret)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
