# -*- coding: utf-8 -*-
"""The reconfigurable/deconstructable/minifiable claims, including the roof-support measurement.

Owner requirement, 2026-09-30, verbatim: *"and the store facilities walls floors and all of it
have to be reconfigureable deconstructable and minifyable(the minify mod) just like the game with
the mods allows"*.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-startplacement.py")

text = io.open(PROOF, encoding="utf-8").read()

IMPORT_ANCHOR = u"from collections import deque"
IMPORT_NEW = u"""import math
from collections import deque"""

TAIL_ANCHOR = u'''print("")
if failures:'''

TAIL_NEW = u'''# --------------------------------------------------------------------------------------------
# Owner requirement, 2026-09-30, verbatim: *"and the store facilities walls floors and all of it
# have to be reconfigureable deconstructable and minifyable(the minify mod) just like the game
# with the mods allows"*.
#
# Register row [128] MinifyEverything mutates `ThingDef.minifiedDef` and
# `building.alwaysUninstallable` at startup -- on DEFS, not on instances. The facility is built
# from Core defs only, so whatever it does to a wall applies to ours. What is left to check is
# that nothing this mod does makes its own placements special.
print("")
print("  -- the facility is the player's to take apart --")

# Counted against the spawns. Missing the faction on ONE of the three kinds is the failure mode,
# and a bare `in` test cannot see which one.
check("EVERY THING THE FACILITY PLACES BELONGS TO THE PLAYER",
      gen.count("SetFactionDirect(Faction.OfPlayer)") >= 3
      and gen.count("GenSpawn.Spawn(") >= 4
      and "wall.SetFactionDirect(Faction.OfPlayer);" in gen
      and "door.SetFactionDirect(Faction.OfPlayer);" in gen
      and "building.SetFactionDirect(Faction.OfPlayer);" in gen,
      "-- player faction is all Designator_Deconstruct and Designator_Uninstall require; found "
      "%d faction assignment(s) against %d spawn(s)"
      % (gen.count("SetFactionDirect(Faction.OfPlayer)"), gen.count("GenSpawn.Spawn(")))

check("the facility places Core defs only, so the minify mod can reach them",
      "ThingDefOf.Wall" in gen and "ThingDefOf.Door" in gen
      and "ThingMaker.MakeThing(plan.thing, plan.stuff)" in gen
      and "new ThingDef" not in gen,
      "-- MinifyEverything patches ThingDefs at startup; a def of our own would be outside its "
      "reach and could not be made minifiable by it at all")

check("the floor goes down through SetTerrain, so Remove Floor works",
      "map.terrainGrid.SetTerrain(cell, start.floorTerrain);" in gen,
      "-- TerrainGrid.SetTerrain records the displaced terrain in underGrid for any layerable "
      "floor, and CanRemoveTopLayerAt needs exactly that")

check("nothing in the facility path blocks a deconstruct or uninstall designation",
      "DesignationDefOf.Deconstruct" not in gen and "DesignationDefOf.Uninstall" not in gen
      and "designationManager" not in gen,
      "-- the facility must behave like anything else the player owns")

# The roof-support rule, replicated. RoofCollapseUtility.RoofMaxSupportDistance is 6.9 and
# support is a flood fill over ROOFED cells within that distance looking for a holdsRoof
# edifice -- so a wall reachable only by leaving the roof does not count. Walls and doors both
# hold roof, so the door cells make no difference.
ROOF_SUPPORT_DISTANCE = 6.9


def unsupported_roof(rooms):
    walls = set()
    roofed = set()
    for x, z, w, h, is_roofed in rooms:
        for cx in range(x, x + w):
            for cz in range(z, z + h):
                if cx in (x, x + w - 1) or cz in (z, z + h - 1):
                    walls.add((cx, cz))
                elif is_roofed:
                    roofed.add((cx, cz))
    # A wall cell beats an enclosing room's interior: the wall is what actually gets spawned.
    roofed -= walls
    bad = []
    for cell in sorted(roofed):
        seen = set([cell])
        queue = deque([cell])
        supported = False
        while queue and not supported:
            here = queue.popleft()
            for step in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                near = (here[0] + step[0], here[1] + step[1])
                if math.hypot(near[0] - cell[0], near[1] - cell[1]) > ROOF_SUPPORT_DISTANCE:
                    continue
                if near in walls:
                    supported = True
                    break
            if supported:
                break
            for step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                near = (here[0] + step[0], here[1] + step[1])
                if near in seen or near not in roofed:
                    continue
                if math.hypot(near[0] - cell[0], near[1] - cell[1]) > ROOF_SUPPORT_DISTANCE:
                    continue
                seen.add(near)
                queue.append(near)
        if not supported:
            bad.append(cell)
    return roofed, walls, bad


for name in ("RR_AsyncIndustriesStart", "RR_FurnitureStoreStart", "RR_SoloGroupStart"):
    body = start_block(name)
    plans = [(int(x), int(z), int(w), int(h), roofed == "true") for x, z, w, h, roofed in
             re.findall(r"<li><x>(-?\\d+)</x><z>(-?\\d+)</z><width>(\\d+)</width>"
                        r"<height>(\\d+)</height><roofed>(\\w+)</roofed>", body)]
    roofed_cells, wall_cells, bad_cells = unsupported_roof(plans)
    check("%s ROOFS NOTHING IT CANNOT HOLD UP" % name,
          len(plans) > 0 and not bad_cells,
          "-- %d roofed cell(s) and %d wall cell(s); %d cell(s) out of support range, e.g. %s. "
          "Deconstructing a wall under unsupported roof collapses it, so a layout like this "
          "drops a roof on the player's pawns the first time they remodel"
          % (len(roofed_cells), len(wall_cells), len(bad_cells), bad_cells[:6]))

print("")
if failures:'''

problems = []
for anchor in (IMPORT_ANCHOR, TAIL_ANCHOR):
    if text.count(anchor) != 1:
        problems.append("%d occurrence(s) of %r" % (text.count(anchor), anchor[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

text = text.replace(IMPORT_ANCHOR, IMPORT_NEW, 1)
text = text.replace(TAIL_ANCHOR, TAIL_NEW, 1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("proof extended with the reconfigurable claims")
