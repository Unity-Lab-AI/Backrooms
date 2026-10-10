import io, os

# (defName, label, description, minDepth, maxDepth, weight, anomalous, slots)
# slot = (kind, payload, countLow, countHigh, chance, minified, stackLow, stackHigh)
A = [
 ("RR_Room_Laboratory", "laboratory", "Benches, samples and the residue of work nobody finished.", 2, 0, 1.2, False, [
   ("WorkTable", None, 1, 2, 1.0, False, 1, 1),
   ("Storage", None, 1, 3, 0.9, False, 1, 1),
   ("Seat", None, 1, 2, 0.7, False, 1, 1),
   ("Table", None, 0, 1, 0.5, False, 1, 1),
   ("CategoryMember", "Medicine", 1, 2, 0.6, False, 4, 18),
 ]),
 ("RR_Room_Workshop", "workshop", "Half-finished work, tools left where they fell, and material nobody came back for.", 2, 0, 1.3, False, [
   ("WorkTable", None, 1, 3, 1.0, False, 1, 1),
   ("Storage", None, 1, 2, 0.8, False, 1, 1),
   ("CategoryMember", "ResourcesRaw", 2, 4, 0.9, False, 20, 75),
   ("Seat", None, 0, 2, 0.5, False, 1, 1),
 ]),
 ("RR_Room_Nursery", "nursery", "Small furniture in a room with no children in it.", 3, 0, 0.8, False, [
   ("Bed", None, 2, 4, 1.0, False, 1, 1),
   ("Art", None, 1, 2, 0.7, False, 1, 1),
   ("Seat", None, 1, 2, 0.6, False, 1, 1),
   ("Storage", None, 0, 1, 0.5, False, 1, 1),
 ]),
 ("RR_Room_Dormitory", "dormitory", "Beds in rows, made up and never slept in.", 2, 0, 1.0, False, [
   ("Bed", None, 3, 6, 1.0, False, 1, 1),
   ("Storage", None, 1, 2, 0.6, False, 1, 1),
   ("Light", None, 0, 2, 0.5, False, 1, 1),
 ]),
 ("RR_Room_Canteen", "canteen", "Tables set for a shift that never came off.", 2, 0, 1.1, False, [
   ("Table", None, 1, 3, 1.0, False, 1, 1),
   ("Seat", None, 3, 6, 1.0, False, 1, 1),
   ("CategoryMember", "FoodMeals", 1, 3, 0.7, False, 2, 8),
   ("Storage", None, 0, 1, 0.5, False, 1, 1),
 ]),
 ("RR_Room_Storeroom", "storeroom", "Racking, crates, and stock counted by nobody.", 2, 0, 1.4, False, [
   ("Storage", None, 2, 5, 1.0, False, 1, 1),
   ("CategoryMember", "ResourcesRaw", 2, 5, 0.9, False, 25, 110),
   ("CategoryMember", "Manufactured", 1, 3, 0.6, False, 5, 30),
 ]),
 ("RR_Room_MachineHall", "machine hall", "Equipment still bolted down, still warm, still running on nothing.", 3, 0, 1.0, False, [
   ("WorkTable", None, 2, 4, 1.0, False, 1, 1),
   ("Light", None, 1, 3, 0.8, False, 1, 1),
   ("CategoryMember", "Manufactured", 2, 4, 0.7, False, 8, 40),
 ]),
 ("RR_Room_Ward", "ward", "Beds, medicine, and the smell of a place that treated people once.", 3, 0, 0.9, False, [
   ("Bed", None, 2, 5, 1.0, False, 1, 1),
   ("CategoryMember", "Medicine", 2, 4, 0.9, False, 8, 30),
   ("Storage", None, 1, 2, 0.7, False, 1, 1),
   ("Seat", None, 0, 2, 0.4, False, 1, 1),
 ]),
 ("RR_Room_Office", "office floor", "Desks in a grid under a light that hums at the wrong pitch.", 2, 0, 1.3, False, [
   ("Table", None, 2, 5, 1.0, False, 1, 1),
   ("Seat", None, 2, 5, 1.0, False, 1, 1),
   ("Art", None, 0, 2, 0.5, False, 1, 1),
   ("Storage", None, 0, 2, 0.5, False, 1, 1),
 ]),
 ("RR_Room_Salvage", "salvage cache", "Furniture pulled up and stacked, ready to be carried somewhere that does not exist.", 2, 0, 1.0, False, [
   ("Table", None, 1, 2, 0.8, True, 1, 1),
   ("Seat", None, 1, 3, 0.8, True, 1, 1),
   ("WorkTable", None, 0, 1, 0.5, True, 1, 1),
   ("CategoryMember", "ResourcesRaw", 1, 3, 0.7, False, 20, 60),
 ]),
 ("RR_Room_Gallery", "gallery", "Pieces hung with care by somebody who is not here.", 4, 0, 0.6, True, [
   ("Art", None, 3, 6, 1.0, False, 1, 1),
   ("Light", None, 1, 3, 0.8, False, 1, 1),
   ("Seat", None, 0, 2, 0.4, False, 1, 1),
 ]),
 ("RR_Room_Duplicate", "the same room again", "Identical furniture in identical positions. You have been here. You have not been here.", 4, 0, 0.5, True, [
   ("Seat", None, 4, 4, 1.0, False, 1, 1),
   ("Table", None, 2, 2, 1.0, False, 1, 1),
   ("Light", None, 2, 2, 1.0, False, 1, 1),
 ]),
 ("RR_Room_Wrong", "wrong assembly", "Things that belong in different rooms, arranged by something that had only read about rooms.", 5, 0, 0.7, True, [
   ("Bed", None, 1, 2, 0.8, False, 1, 1),
   ("WorkTable", None, 1, 2, 0.8, False, 1, 1),
   ("Table", None, 1, 3, 0.7, False, 1, 1),
   ("Art", None, 1, 3, 0.7, False, 1, 1),
   ("Storage", None, 1, 2, 0.6, False, 1, 1),
   ("CategoryMember", "ResourcesRaw", 1, 3, 0.6, False, 10, 50),
 ]),
 ("RR_Room_Hoard", "hoard", "Everything of one kind, far more of it than anybody needed.", 5, 0, 0.5, True, [
   ("CategoryMember", "ResourcesRaw", 5, 9, 1.0, False, 60, 180),
   ("Storage", None, 2, 4, 0.8, False, 1, 1),
 ]),
]

def slot_xml(kind, payload, lo, hi, chance, minified, slo, shi):
    parts = ["      <li>", "        <kind>%s</kind>" % kind]
    if kind == "CategoryMember":
        parts.append("        <category>%s</category>" % payload)
    parts.append("        <count>%d~%d</count>" % (lo, hi))
    if chance < 1.0:
        parts.append("        <chance>%s</chance>" % chance)
    if minified:
        parts.append("        <minified>true</minified>")
    if (slo, shi) != (1, 1):
        parts.append("        <stackCount>%d~%d</stackCount>" % (slo, shi))
    parts.append("      </li>")
    return "\n".join(parts)

blocks = []
for (name, label, desc, lo, hi, weight, anom, slots) in A:
    p = ["  <RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>",
         "    <defName>%s</defName>" % name,
         "    <label>%s</label>" % label,
         "    <description>%s</description>" % desc,
         "    <minDepth>%d</minDepth>" % lo]
    if hi > 0:
        p.append("    <maxDepth>%d</maxDepth>" % hi)
    p.append("    <weight>%s</weight>" % weight)
    if anom:
        p.append("    <anomalous>true</anomalous>")
    p.append("    <slots>")
    for sl in slots:
        p.append(slot_xml(*sl))
    p.append("    </slots>")
    p.append("  </RimroomsAsyncIndustries.Generation.RimroomsRoomArchetypeDef>")
    blocks.append("\n".join(p))

header = """<?xml version="1.0" encoding="utf-8"?>
<Defs>

  <!-- Owner direction 2026-09-29: "lots of furnature and equipment and different types of
       rooms and materials of all types from labs, to workshops, to nursaries, to everything
       imanginable and every variation of them and even wild waky carzxzy creepy things", with
       the clarification that the yellow rooms are only the shallow look and "further in it
       gets very varied and weird".

       Every slot asks for a CAPABILITY rather than naming furniture. A hand-written list of
       defNames would cover Core, miss every DLC, miss all 274 profile mods, and rot the first
       time anything was renamed. Asking the game "what is a work table" means a profile that
       adds a new bench puts it in Backrooms workshops the day it is installed.

       minDepth is what keeps the shallow yellow rooms empty. Nothing here can appear at
       depth 1, because that emptiness IS the look.

       Counts and chances are rolled per room from the room's own seed, which is how "every
       variation of them" is answered without authoring each variation: two laboratories in one
       coordinate share an archetype and are not the same room, and the same room is identical
       every time it loads. -->

"""

io.open('Mod/Rimrooms - Async Industries/1.6/Defs/RimroomsRoomArchetypeDefs/RR_RoomArchetypes.xml',
        'w', encoding='utf-8', newline='').write(header + "\n\n".join(blocks) + "\n\n</Defs>\n")
print("archetypes written:", len(A))
