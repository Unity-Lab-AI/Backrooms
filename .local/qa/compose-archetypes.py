# -*- coding: utf-8 -*-
"""Tag the existing archetypes with themes and author the owner's named kinds.

Appended into the existing def file rather than a new one, so the 92-file
package allowlist does not move. Every `CategoryMember` slot uses a category
already proven to resolve in this file -- an unresolved ThingCategoryDef is a
load-time cross-reference failure, not a silently skipped slot.
"""
import io
import sys

NL = chr(10)
PATH = "Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsRoomArchetypeDefs/RR_RoomArchetypes.xml"

# Which of the eight themes each shipped archetype belongs to.
TAGS = {
    "RR_Room_Classroom": ["institution"],
    "RR_Room_WeaponsLocker": ["military"],
    "RR_Room_Laboratory": ["institution", "industry"],
    "RR_Room_Workshop": ["industry"],
    "RR_Room_Nursery": ["residential", "institution"],
    "RR_Room_Dormitory": ["residential", "military"],
    "RR_Room_Canteen": ["institution", "leisure"],
    "RR_Room_Storeroom": ["industry", "market"],
    "RR_Room_MachineHall": ["industry", "infrastructure"],
    "RR_Room_Ward": ["institution"],
    "RR_Room_Office": ["institution"],
    "RR_Room_Salvage": ["derelict", "industry"],
    "RR_Room_Gallery": ["leisure", "institution"],
    "RR_Room_Duplicate": ["derelict"],
    "RR_Room_Wrong": ["derelict"],
    "RR_Room_Hoard": ["derelict"],
}

HEADER = '''
  <!-- ====================================================================================
       THE OWNER'S NAMED KINDS, AND THE EXPANSION PAST THEM

       Verbatim owner direction, 2026-10-03: "so its more rooma corradors facilites
       infastructure roads neighborrs hood malls shoopping centers military(i cant name theme
       all but there are hundred s and hundreds of facilities and room types like underground
       lsd cities", and at the composition fork: "option 3 but keep it not limited to my
       examples i want you to expand and expound on everything in a lsd way".

       "hundred s and hundreds" is not a number of defs to author — it is a product. A room's
       identity is its ARCHETYPE (these) times its SHAPE (seven forms in RockIntrusionCells)
       times its coordinate's MATERIALS times every slot's rolled count and chance. Forty-four
       archetypes against seven shapes is three hundred and eight distinguishable rooms before
       a single slot is rolled, and the owner's named kinds are all in here by name.

       Every slot still asks for a CAPABILITY rather than naming furniture, for the reason at
       the top of this file: a profile mod that adds a bench puts it in Backrooms workshops the
       day it is installed. The CategoryMember slots below use only categories already proven
       to resolve in this file — an unresolved ThingCategoryDef is a load failure.

       themes is what makes a floor read as somewhere rather than as a list of rooms. A
       coordinate draws ONE theme and an archetype carrying it is three times likelier; it is
       deliberately a bias and not a filter, because a market coordinate holding nothing but
       shops is a themed level rather than a Backrooms level. The wrongness needs the one
       laboratory in the shopping centre.
       ==================================================================================== -->

'''

# (defName, label, description, minDepth, weight, themes, anomalous, slots)
# A slot is (kind, extra, count, chance) where extra is a category name or None.
KINDS = [
    # ---------------------------------------------------------------------------- market
    ("RR_Room_ShopFront", "shop front",
     "A counter, and racks still arranged to be browsed. The prices are gone but the layout "
     "assumes somebody is coming in off a street that does not exist.",
     2, 1.0, ["market"], False,
     [("Table", None, "1~2", 1.0), ("Storage", None, "2~5", 1.0),
      ("CategoryMember", "Apparel", "1~4", 0.7), ("Seat", None, "0~2", 0.5),
      ("Light", None, "0~2", 0.6)]),

    ("RR_Room_MallConcourse", "mall concourse",
     "Benches facing nothing, planters, and the lighting of a place built to be walked through. "
     "The walking-through has no other end.",
     2, 1.2, ["market", "leisure"], False,
     [("Seat", None, "3~8", 1.0), ("Art", None, "1~3", 0.8),
      ("Light", None, "2~5", 0.9), ("Storage", None, "0~2", 0.35),
      ("CategoryMember", "Manufactured", "1~3", 0.6)]),

    ("RR_Room_FoodCourt", "food court",
     "Tables bolted in rows, a serving line, and meals that have not spoiled. Nobody is "
     "eating and nothing is cold.",
     2, 1.0, ["market", "leisure"], False,
     [("Table", None, "2~5", 1.0), ("Seat", None, "4~10", 1.0),
      ("CategoryMember", "FoodMeals", "1~4", 0.85), ("WorkTable", None, "0~2", 0.6),
      ("Light", None, "1~3", 0.7)]),

    ("RR_Room_Checkout", "checkout lane",
     "Six identical stations in a row, all of them facing the same way, all of them clear.",
     3, 0.9, ["market"], False,
     [("Table", None, "3~6", 1.0), ("Storage", None, "1~4", 0.8),
      ("CategoryMember", "Manufactured", "1~3", 0.6), ("Light", None, "1~2", 0.5)]),

    ("RR_Room_Stockroom", "stockroom",
     "Shelving to the ceiling with the aisles too narrow for the pallets. Somebody stocked it "
     "and never had to walk it.",
     2, 1.0, ["market", "industry"], False,
     [("Storage", None, "4~9", 1.0), ("CategoryMember", "ResourcesRaw", "2~5", 0.8),
      ("Light", None, "0~2", 0.5)]),

    # -------------------------------------------------------------------------- military
    ("RR_Room_Barracks", "barracks",
     "Beds squared off on a grid, lockers at the foot of each. The bedding is made to a "
     "standard nobody is here to inspect.",
     2, 1.1, ["military", "residential"], False,
     [("Bed", None, "3~8", 1.0), ("Storage", None, "2~6", 0.9),
      ("Light", None, "1~3", 0.7), ("CategoryMember", "Apparel", "0~3", 0.5)]),

    ("RR_Room_Checkpoint", "checkpoint",
     "A desk across the only way through, and racks behind it. Whatever was being checked for "
     "was expected to come from inside.",
     2, 1.0, ["military", "infrastructure"], False,
     [("Table", None, "1~2", 1.0), ("Seat", None, "1~3", 0.9),
      ("CategoryMember", "Weapons", "1~3", 0.7), ("Storage", None, "1~3", 0.8),
      ("Light", None, "1~2", 0.8)]),

    ("RR_Room_MotorPool", "motor pool",
     "Benches, parts and the bays for vehicles too wide for any door in the building.",
     3, 0.9, ["military", "industry"], False,
     [("WorkTable", None, "1~3", 1.0), ("CategoryMember", "Manufactured", "2~6", 0.9),
      ("Storage", None, "1~4", 0.8), ("Light", None, "1~3", 0.6)]),

    ("RR_Room_BriefingRoom", "briefing room",
     "Chairs in ranks facing a board. The chairs are occupied by nothing and arranged for "
     "somebody who was going to stand at the front.",
     2, 0.9, ["military", "institution"], False,
     [("Seat", None, "5~12", 1.0), ("Table", None, "1~2", 0.8),
      ("Art", None, "0~2", 0.5), ("Light", None, "1~2", 0.7),
      ("CategoryMember", "Books", "1~2", 0.7)]),

    # ----------------------------------------------------------------------- residential
    ("RR_Room_Apartment", "apartment",
     "Somebody lived in exactly this shape of room, with exactly this furniture, and the door "
     "opens onto a corridor with no address.",
     2, 1.2, ["residential"], False,
     [("Bed", None, "1~2", 1.0), ("Table", None, "1~2", 0.9),
      ("Seat", None, "1~3", 0.9), ("Storage", None, "1~3", 0.8),
      ("Art", None, "0~2", 0.6), ("Light", None, "1~2", 0.7),
      ("CategoryMember", "Apparel", "1~4", 0.8)]),

    ("RR_Room_LaundryRoom", "laundry room",
     "Machines along one wall and folded clothing that is not anybody's size.",
     2, 0.8, ["residential"], False,
     [("WorkTable", None, "1~3", 0.9), ("Storage", None, "1~4", 0.9),
      ("CategoryMember", "Apparel", "2~6", 0.9), ("Light", None, "0~2", 0.5)]),

    ("RR_Room_Playroom", "play room",
     "Small chairs, soft flooring, and the picture books stacked by somebody who could read.",
     3, 0.8, ["residential", "leisure"], False,
     [("Seat", None, "2~6", 1.0), ("CategoryMember", "Books", "1~4", 0.8),
      ("Art", None, "1~3", 0.8), ("Light", None, "0~2", 0.5)]),

    ("RR_Room_StairwellLanding", "stairwell landing",
     "A landing with no stairs at either end of it. The handrail is worn exactly where a hand "
     "would go.",
     2, 1.0, ["infrastructure", "residential"], False,
     [("Light", None, "1~3", 0.9), ("Seat", None, "0~1", 0.3),
      ("Art", None, "0~1", 0.25), ("CategoryMember", "ResourcesRaw", "1~2", 0.45)]),

    # -------------------------------------------------------------------- infrastructure
    ("RR_Room_ServiceTunnel", "service tunnel",
     "Conduit, cable trays and the stencilled numbers of a system the building does not have.",
     2, 1.2, ["infrastructure", "industry"], False,
     [("Light", None, "2~5", 0.9), ("CategoryMember", "Manufactured", "1~4", 0.8),
      ("Storage", None, "0~2", 0.4)]),

    ("RR_Room_Substation", "substation",
     "Switchgear humming with nothing drawing on it, and the floor marked out for feet that "
     "should not stand there.",
     3, 0.9, ["infrastructure", "industry"], False,
     [("CategoryMember", "Manufactured", "2~5", 1.0), ("WorkTable", None, "0~2", 0.6),
      ("Light", None, "1~3", 0.8), ("Storage", None, "0~2", 0.4)]),

    ("RR_Room_PumpHouse", "pump house",
     "Pumps, valve wheels, and the stains of water moved through a place with no source and "
     "no drain.",
     3, 0.9, ["infrastructure", "industry"], False,
     [("WorkTable", None, "1~2", 0.9), ("CategoryMember", "Manufactured", "2~5", 0.9),
      ("Storage", None, "1~3", 0.7), ("Light", None, "1~2", 0.6)]),

    ("RR_Room_Roadway", "roadway",
     "Lane markings, a kerb, and lighting at the spacing of a road. It is indoors, it is "
     "roofed, and it is wide enough for two lanes of something.",
     2, 1.0, ["infrastructure"], False,
     [("Light", None, "3~7", 1.0), ("CategoryMember", "Manufactured", "0~3", 0.5),
      ("Art", None, "0~1", 0.2)]),

    # --------------------------------------------------------------------------- leisure
    ("RR_Room_Cinema", "cinema",
     "Seating in a rake, facing a wall that was built to be looked at. The wall is a wall.",
     3, 0.9, ["leisure"], False,
     [("Seat", None, "6~14", 1.0), ("Art", None, "0~2", 0.5),
      ("Light", None, "0~2", 0.4), ("CategoryMember", "FoodMeals", "1~3", 0.7)]),

    ("RR_Room_WaitingRoom", "waiting room",
     "Chairs round the wall, a low table, and magazines nobody has disturbed. Whoever was "
     "waiting is not here and has not been called.",
     2, 1.1, ["leisure", "institution"], False,
     [("Seat", None, "4~9", 1.0), ("Table", None, "1~2", 0.9),
      ("CategoryMember", "Books", "1~3", 0.7), ("Art", None, "0~2", 0.6),
      ("Light", None, "1~2", 0.6)]),

    ("RR_Room_Sauna", "changing room",
     "Benches, hooks, and the close warmth of a room with nothing heating it.",
     3, 0.8, ["leisure", "residential"], False,
     [("Seat", None, "2~6", 1.0), ("CategoryMember", "Apparel", "1~4", 0.8),
      ("Storage", None, "1~3", 0.7), ("Light", None, "0~2", 0.5)]),

    # ----------------------------------------------------------------------- institution
    ("RR_Room_RecordsVault", "records vault",
     "Files in ranks, indexed by a scheme that holds all the way through and refers to "
     "nothing.",
     3, 0.9, ["institution"], False,
     [("Storage", None, "4~9", 1.0), ("CategoryMember", "Books", "2~6", 0.9),
      ("Light", None, "1~2", 0.6), ("Table", None, "0~1", 0.4)]),

    ("RR_Room_Chapel", "quiet room",
     "Seating in rows facing one end, and a space at that end left deliberately empty.",
     4, 0.7, ["institution", "leisure"], False,
     [("Seat", None, "4~10", 1.0), ("Art", None, "1~2", 0.8),
      ("Light", None, "1~3", 0.7), ("CategoryMember", "Books", "1~2", 0.6)]),

    ("RR_Room_Infirmary", "infirmary",
     "Two beds, a supply cabinet, and medicine stocked for a number of people this room could "
     "never hold.",
     2, 0.9, ["institution", "military"], False,
     [("Bed", None, "1~3", 1.0), ("CategoryMember", "Medicine", "1~4", 0.9),
      ("Storage", None, "1~3", 0.9), ("Light", None, "1~2", 0.7)]),

    # ------------------------------------------------------- the LSD register, deeper in
    ("RR_Room_EndlessShelves", "endless shelving",
     "Shelving on every wall and down the middle, all of it the same shelving, all of it "
     "stocked with the same thing. The aisles meet at the far end.",
     4, 0.8, ["derelict", "market"], True,
     [("Storage", None, "6~12", 1.0), ("CategoryMember", "Manufactured", "3~8", 0.9),
      ("Light", None, "0~2", 0.4)]),

    ("RR_Room_FurnitureDrift", "drifted furniture",
     "Everything in the room has been moved to one wall. Not stacked, not piled -- moved, "
     "upright, and still facing the way it was.",
     4, 0.8, ["derelict", "residential"], True,
     [("Seat", None, "3~9", 1.0), ("Table", None, "2~5", 0.9),
      ("Storage", None, "1~4", 0.7), ("Art", None, "0~2", 0.5),
      ("CategoryMember", "Apparel", "1~4", 0.7)]),

    ("RR_Room_MirrorWard", "mirrored ward",
     "Beds in a grid so exact that the gaps are the same width as the beds, and the room is "
     "symmetrical about an axis the door is not on.",
     5, 0.7, ["derelict", "institution"], True,
     [("Bed", None, "4~10", 1.0), ("Light", None, "2~4", 0.8),
      ("CategoryMember", "Medicine", "0~2", 0.4)]),

    ("RR_Room_CarpetSea", "one chair",
     "A room of this size, carpeted wall to wall, holding one chair. The chair is in the "
     "middle and it is facing a corner.",
     5, 0.6, ["derelict"], True,
     [("Seat", None, "1~1", 1.0), ("Light", None, "0~1", 0.3),
      ("CategoryMember", "Apparel", "1~1", 0.5)]),

    ("RR_Room_Vending", "vending wall",
     "Machines in an unbroken line, every one of them the same, every one of them stocked, "
     "none of them taking anything.",
     4, 0.7, ["derelict", "market"], True,
     [("Storage", None, "4~8", 1.0), ("CategoryMember", "FoodMeals", "2~6", 0.9),
      ("Light", None, "1~3", 0.7)]),
]


def themes_block(themes, indent):
    pad = " " * indent
    out = [pad + "<themes>"]
    for theme in themes:
        out.append(pad + "  <li>" + theme + "</li>")
    out.append(pad + "</themes>")
    return NL.join(out)


def render(entry):
    name, label, description, min_depth, weight, themes, anomalous, slots = entry
    lines = ["  <RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>",
             "    <defName>" + name + "</defName>",
             "    <label>" + label + "</label>",
             "    <description>" + description + "</description>",
             "    <minDepth>" + str(min_depth) + "</minDepth>",
             "    <weight>" + str(weight) + "</weight>"]
    if anomalous:
        lines.append("    <anomalous>true</anomalous>")
    lines.append(themes_block(themes, 4))
    lines.append("    <slots>")
    for kind, extra, count, chance in slots:
        lines.append("      <li>")
        lines.append("        <kind>" + kind + "</kind>")
        if extra is not None:
            lines.append("        <category>" + extra + "</category>")
        lines.append("        <count>" + count + "</count>")
        if chance < 1.0:
            lines.append("        <chance>" + str(chance) + "</chance>")
        if kind == "CategoryMember":
            lines.append("        <stackCount>1~5</stackCount>")
        lines.append("      </li>")
    lines.append("    </slots>")
    lines.append("  </RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>")
    return NL.join(lines)


text = io.open(PATH, encoding="utf-8-sig").read()
problems = 0

# 1. tag the shipped sixteen, inserting <themes> immediately after <weight>
for name, themes in sorted(TAGS.items()):
    anchor = "<defName>" + name + "</defName>"
    if text.count(anchor) != 1:
        print("defName not unique: %s" % name)
        problems += 1
        continue
    at = text.index(anchor)
    weight_at = text.find("</weight>", at)
    slots_at = text.find("<slots>", at)
    if weight_at == -1 or (slots_at != -1 and weight_at > slots_at):
        print("no <weight> before <slots> for %s" % name)
        problems += 1
        continue
    end = text.index(NL, weight_at)
    text = text[:end] + NL + themes_block(themes, 4) + text[end:]

if problems:
    print("%d archetype(s) not tagged; nothing written" % problems)
    sys.exit(1)

# 2. author the new kinds, before the closing tag
close = "</Defs>"
assert text.count(close) == 1
at = text.rindex(close)
body = HEADER + (NL + NL).join(render(entry) for entry in KINDS) + NL + NL
text = text[:at] + body + text[at:]

io.open(PATH, "w", encoding="utf-8", newline=NL).write(text)
print("tagged %d shipped archetypes, authored %d new kinds (%d total)"
      % (len(TAGS), len(KINDS), len(TAGS) + len(KINDS)))
