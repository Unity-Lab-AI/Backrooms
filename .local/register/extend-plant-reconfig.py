# -*- coding: utf-8 -*-
"""Plants for the reconfigurable/deconstructable/minifiable claims."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-startplacement.py")

text = io.open(PLANT, encoding="utf-8").read()

ANCHOR = '''    ("a layout grows past the smallest map RimWorld offers", STARTS,'''

NEW = '''    # ------------------------------------------------- the facility is the player's to take apart
    ("THE WALLS STOP BELONGING TO THE PLAYER", GEN,
     "                        wall.SetFactionDirect(Faction.OfPlayer);" + CHR_NL, "", PROOF),

    ("the doors stop belonging to the player", GEN,
     "                door.SetFactionDirect(Faction.OfPlayer);" + CHR_NL, "", PROOF),

    ("the furniture stops belonging to the player", GEN,
     "                building.SetFactionDirect(Faction.OfPlayer);" + CHR_NL, "", PROOF),

    ("THE FLOOR STOPS RECORDING WHAT IT COVERED", GEN,
     "if (room.floor) { map.terrainGrid.SetTerrain(cell, start.floorTerrain); }",
     "if (room.floor) { }", PROOF),

    ("the facility starts authoring a def the minify mod cannot reach", GEN,
     "            int index = 0;", "            ThingDef invented = new ThingDef();" + CHR_NL
     + "            int index = 0;", PROOF),

    ("the facility starts interfering with designations", GEN,
     "                        GenSpawn.Spawn(wall, cell, map);",
     "                        GenSpawn.Spawn(wall, cell, map);" + CHR_NL
     + "                        map.designationManager.RemoveAllDesignationsOn(wall);", PROOF),

    ("A LAYOUT ROOFS A SPAN NOTHING HOLDS UP", STARTS,
     "<li><x>27</x><z>27</z><width>7</width><height>7</height>",
     "<li><x>27</x><z>27</z><width>40</width><height>40</height>", PROOF),

    ("the Store loses the inner walls that hold its showroom roof up", STARTS,
     "      <li><x>10</x><z>10</z><width>18</width><height>14</height><roofed>true</roofed><floor>true</floor></li>" + CHR_NL,
     "", PROOF),

'''

if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d occurrence(s)" % text.count(ANCHOR))
    raise SystemExit(1)

io.open(PLANT, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW + ANCHOR, 1))
print("plant suite extended with the reconfigurable plants")
