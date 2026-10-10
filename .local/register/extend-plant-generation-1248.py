# -*- coding: utf-8 -*-
"""Plants for the 0.12.48-dev power-grid and lamp-placement claims."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-generation.py")

text = io.open(PLANT, encoding="utf-8").read()

ANCHOR = u"]\n"

NEW = u'''    # ------------------------------------------ 0.12.48-dev: the light count that killed everything
    ("THE LIGHT COUNT FORMULA COMES BACK", GEN,
     "                string powerFault = ValidateNativePowerNetwork(map, generator, climate, placedLights);",
     "                int expectedPowerLights = coordinate.Rooms.Count;" + chr(10)
     + "                string powerFault = ValidateNativePowerNetwork(map, generator, climate, placedLights);"),

    ("the validator stops reading the lights that were placed", GEN,
     "                    placedLights.Add(light);" + chr(10), ""),

    ("THE MAP-WIDE CONSUMER SWEEP GOES", GEN,
     "            foreach (Thing thing in map.listerThings.AllThings)",
     "            foreach (Thing thing in new List<Thing>())"),

    ("the sweep stops looking for power consumers", GEN,
     "                if (thing.TryGetComp<CompPowerTrader>() != null) { consumers.Add(thing); }" + chr(10), ""),

    ("A POWER FAULT BECOMES FATAL AGAIN", GEN,
     "                if (powerFault != null)" + chr(10) + "                {" + chr(10)
     + '                    Log.Warning("[Rimrooms][Generation] Coordinate " + coordinate.Id +',
     "                if (powerFault != null)" + chr(10) + "                {" + chr(10)
     + "                    throw new InvalidOperationException(\\"RR_Generation_ContentPlacementFailed\\");" + chr(10)
     + '                    Log.Warning("[Rimrooms][Generation] Coordinate " + coordinate.Id +'),

    ("the power fault stops being reported at all", GEN,
     "                if (powerFault != null)", "                if (false)"),

    ("the structural validation stops running", GEN,
     "                ValidatePlacedLayout(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);" + chr(10),
     ""),

    ("THE WALL LAMP GOES BACK TO FLOATING OVER THE FLOOR", GEN,
     "                    GenSpawn.Spawn(light, lightCells[index], map, lightFacings[index]);",
     "                    GenSpawn.Spawn(light, lightCells[index], map, Rot4.North);"),

    ("the lamp stops being mounted on a wall", GEN,
     "                bool wallMounted = lightDef.building != null && lightDef.building.isAttachment;",
     "                bool wallMounted = false;"),

    ("the placement starts naming WallLamp instead of reading the def", GEN,
     "                bool wallMounted = lightDef.building != null && lightDef.building.isAttachment;",
     '                bool wallMounted = lightDef.defName == "WallLamp";'),

    ("the facing stops pointing at the wall", GEN,
     "                    facing = Rot4.FromIntVec3(direction);", "                    facing = Rot4.North;"),

    ("a lamp may be mounted on a door", GEN,
     "                    if (wall == null || wall.def != wallDef) { continue; }",
     "                    if (wall == null) { continue; }"),

    ("A ROOM WITH NOWHERE TO MOUNT FAILS THE COORDINATE AGAIN", GEN,
     "            return IntVec3.Invalid;",
     '            throw new InvalidOperationException("RR_Generation_NoSafeRoomCell");'),

    ("the fallback to a floor-standing cell goes", GEN,
     "                    if (!lightCell.IsValid)", "                    if (false)"),

]
'''

if text.count(ANCHOR) < 1:
    print("ANCHOR PROBLEM")
    raise SystemExit(1)

# The LAST bare "]\n" closes PLANTS.
index = text.rindex(u"\n]\n", 0, text.index(u"def write_verified") if u"def write_verified" in text else len(text))
updated = text[:index + 1] + NEW + text[index + 3:]
io.open(PLANT, "w", encoding="utf-8", newline="").write(updated)
print("plant-generation extended")
