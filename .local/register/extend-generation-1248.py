# -*- coding: utf-8 -*-
"""The power-grid and lamp-placement claims for 0.12.48-dev."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

text = io.open(PROOF, encoding="utf-8").read()

TAIL_ANCHOR = u'''print("")
if failures:'''

TAIL_NEW = u'''print("")
print("the fifth launch: a light count took the whole coordinate down")
print("-" * 78)

# Owner, verbatim: *"i dont see a natural gate thats suppose to be on the back wall of one of the
# storage rooms so that they can eneter theri 300x300 gate ie the stargate mode that prcedurally
# generated the backrooms of diffent levels with thir natual gate spawns to different levels
# within"*.
#
# The door WAS there -- confirmed live, a steel Building_Door at (160, 161) with the emergence
# comp's "Mark as way home" gizmo enabled. It was never MARKED, because SoloGroupOpening stops at
# step 2 when the destination site fails, and the site failed on a light count.

check("THE LIGHT COUNT FORMULA IS GONE",
      "expectedPowerLights" not in genstep
      and 'room.familyId == "service_passage" || room.familyId == "utility_room")' not in
      genstep.replace('.Where(room => room.familyId == "service_passage" || room.familyId == "utility_room")', ""),
      "-- it required the number of things whose def == lightDef to equal "
      "Rooms.Count + Rooms.Count(service_passage or utility_room). The extra lamps in that sum "
      "are RoomContentBuilder's hard-coded StandingLamp, and BackroomsPalette switched lightDef "
      "to WallLamp at 0.7.8-dev. climateRoom requires at least one of those rooms to exist, so "
      "the shortfall was GUARANTEED and no coordinate generated for thirty-nine checkpoints")

check("the validator checks the lights that were ACTUALLY placed",
      "var placedLights = new List<Thing>();" in genstep
      and "placedLights.Add(light);" in genstep
      and "ValidateNativePowerNetwork(map, generator, climate, placedLights)" in genstep
      and "List<Thing> placedLights)" in genstep,
      "-- a list the caller built, rather than a number re-derived from the coordinate")

check("EVERY POWER CONSUMER ON THE MAP IS CHECKED, WHATEVER PLACED IT",
      "foreach (Thing thing in map.listerThings.AllThings)" in genstep
      and "thing.TryGetComp<CompPowerTrader>() != null) { consumers.Add(thing); }" in genstep,
      "-- this is the invariant a player can see: nothing here is dark or cold. It names no def "
      "and predicts no count, so a lamp any other code adds later is covered automatically")

check("A POWER FAULT IS REPORTED AND NEVER FATAL",
      "string powerFault = ValidateNativePowerNetwork" in genstep
      and "if (powerFault != null)" in genstep
      and "Log.Warning(" in genstep
      and "return null;" in genstep,
      "-- a coordinate with an unconnected heater is dark, cold and playable. A coordinate that "
      "does not exist costs the player the gate that leads to it, which is exactly what the "
      "fifth launch reported")

check("the structural validation is still fatal",
      "ValidatePlacedLayout(map, coordinate, entryCell, returnCell, officeEvidenceCell, anchor);"
      in genstep
      and 'throw new InvalidOperationException("RR_Generation_UnreachableRoom")' in genstep,
      "-- a coordinate you cannot walk through really is broken, and weakening that would be "
      "trading one silent failure for another")

check("THE WALL LAMP IS MOUNTED ON A WALL, FACING IT",
      "FindWallAttachmentCell(" in genstep
      and "lightDef.building.isAttachment" in genstep
      and "GenSpawn.Spawn(light, lightCells[index], map, lightFacings[index]);" in genstep
      and "facing = Rot4.FromIntVec3(direction);" in genstep,
      "-- WallLamp draws with drawOffsetNorth (0,0,0.9), almost a full cell INTO the wall it is "
      "mounted on, so the rotation is the difference between a lamp on the wall and a lamp "
      "hanging over the floor")

check("it branches on the DEF rather than a def name",
      'lightDef.building != null && lightDef.building.isAttachment' in genstep
      and '"WallLamp"' not in genstep,
      "-- BackroomsPalette still falls back to StandingLamp, which stands on the floor and must "
      "keep doing so; naming WallLamp here would recreate the coupling that caused the outage")

check("a lamp mounts on the room's own wall, not on a door",
      "wall.def != wallDef) { continue; }" in genstep,
      "-- a door also holds up roof, and a lamp mounted on a door is mounted on nothing the "
      "moment it opens")

check("A ROOM WITH NOWHERE TO MOUNT FALLS BACK INSTEAD OF FAILING",
      "return IntVec3.Invalid;" in genstep
      and "if (!lightCell.IsValid)" in genstep
      and "lightCell = FindClearInteriorCell(map, room," in genstep,
      "-- the threshold room holds the gate anchor, the entry cell, the return cell and the "
      "anchor's whole expanded rect, so its wall-adjacent cells can all be reserved. A lamp on "
      "the floor is a cosmetic compromise; a coordinate that does not generate is not")

print("")
if failures:'''

if text.count(TAIL_ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d occurrence(s)" % text.count(TAIL_ANCHOR))
    raise SystemExit(1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(TAIL_ANCHOR, TAIL_NEW, 1))
print("proof-generation-batch extended")
