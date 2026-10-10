"""Plant a fault against every new corridor/degree/vault/fill claim, and re-aim the
one plant the work made toothless.

A claim with no plant behind it is a claim nobody has proved can fail. A plant
that no longer plants a real fault is worse than none, because it reports a
CAUGHT it did not earn -- so it is re-aimed at a fault that is still real
rather than deleted or weakened.
"""
import io
import sys

NL = chr(10)
PLANTS = ".local/register/plant-coordinate-layout.py"

# ------------------------------------------------------------------ the toothless one, re-aimed
#
# `("a braid is made that the validator would refuse", ...)` removed the braid's
# `AreNeighbourRooms` guard. It is no longer a fault: the diagonal braid asks `CorridorLegs` for a
# route on the very next line and an unroutable shape returns none, and an orthogonal braid pair is
# grid-adjacent so the guard was always true. **The guard became redundant, so the plant became a
# free pass** -- it reported CAUGHT for nothing, and when the degree work landed it reported
# MISSED, which is the instrument working.
#
# Re-aimed at the severe fault in the same function instead: a bent route used without being
# proved clear, which carves a corridor through a room.
STALE = (
    '    ("a braid is made that the validator would refuse", PLANNER,' + NL
    + '     "                    if (!AreNeighbourRooms(rooms[here], rooms[there])) { continue; }" + chr(10), ""),'
)
REAIMED = (
    '    ("A BENT ROUTE IS CARVED WITHOUT BEING PROVED CLEAR OF EVERY ROOM", PLANNER,' + NL
    + '     "if (candidate.Count == 3 && LegsClearEveryRoom(candidate, rooms))",' + NL
    + '     "if (candidate.Count == 3)"),'
)

NEW = '''
    # ------------------------------------------------------ the bend, the degree and the vaults
    ("CORRIDORS GO BACK TO BEING ALL STRAIGHT", PLANNER,
     "            return BentLegs(first, second, depth, rooms);",
     "            return legs;"),

    ("the bend loses its last leg, so the route stops short of the second room", PLANNER,
     "                legs.Add(LegAlongX(inFrom, inTo, centreB.z, halfWidth));" + NL, ""),

    ("THE STRAIGHT RUN STOPS BEING PROVED CLEAR, so a corridor is carved through a room", PLANNER,
     "                if (!LegsClearEveryRoom(legs, rooms)) { legs.Clear(); }" + NL
     + "                if (halfWidth > NarrowestCorridorHalfWidth && legs.Count == 0)",
     "                if (halfWidth > NarrowestCorridorHalfWidth && legs.Count == 0)"),

    ("A GRAPH EDGE IS LEFT STANDING WITH NO CORRIDOR UNDER IT", PLANNER,
     "            PruneUnroutableLinks(rooms, depth);" + NL, ""),

    ("the walk takes a step it cannot carve, so the spanning tree is a lie", PLANNER,
     "                    if (CorridorLegs(rooms[parent], room, depth, rooms).Count == 0 &&" + NL
     + "                        !SharesWall(rooms[parent], room))" + NL
     + "                    { continue; }" + NL, ""),

    ("THE DIAGONAL BRAID IS GONE, so max degree falls back to the slot grid's four", PLANNER,
     "                    if (!SlotIsJunction(seed, slot, depth) && roll % DiagonalBraidRarity != 0)" + NL
     + "                    { continue; }",
     "                    if (true) { continue; }"),

    ("the junction slot stops applying to the diagonals, so the degree spread narrows", PLANNER,
     "                    if (!SlotIsJunction(seed, slot, depth) && roll % DiagonalBraidRarity != 0)",
     "                    if (roll % DiagonalBraidRarity != 0 || false)"),

    ("THE REACHABILITY PROOF REFUSES A SEALED ROOM AGAIN, so degree 0 is unbuildable", PLANNER,
     "            return rooms.All(room => room.links.Count == 0 || seen.Contains(room.Bounds.CenterCell)) &&",
     "            return rooms.All(room => seen.Contains(room.Bounds.CenterCell)) &&"),

    ("a sealed vault is allowed to carry links, so it is just an ordinary room", PLANNER,
     "                rooms.Where(room => room.familyId == SealedFamily).All(room => room.links.Count == 0);",
     "                rooms.Where(room => room.familyId == SealedFamily).All(room => room.links.Count >= 0);"),

    ("THE WALK IS ALLOWED INTO A RESERVED SLOT, so nothing is ever sealed", PLANNER,
     "if (slotOf.ContainsKey(next) || sealedSlots.Contains(next)) { continue; }",
     "if (slotOf.ContainsKey(next)) { continue; }"),

    ("the vaults stop being reserved from the room budget and are silently dropped", PLANNER,
     "            int budget = Math.Max(1, MaxRooms - sealedSlots.Count);",
     "            int budget = MaxRooms;"),

    ("THE VALIDATOR CALLS A SEALED VAULT A DISCONNECTED LEVEL", SERVICE,
     "            if (!visited.Contains(0) ||" + NL
     + "                rooms.Any(room => room.links.Count > 0 && !visited.Contains(room.index)) ||" + NL
     + "                directedEdges < 2 * (linkedRooms - 1) ||",
     "            if (visited.Count != rooms.Count ||" + NL
     + "                directedEdges < 2 * (rooms.Count - 1) ||"),

    # ---------------------------------------------------------------- the door, off the midpoint
    ("EVERY DOOR GOES BACK TO THE EXACT MIDDLE OF ITS WALL", PLANNER,
     "&& cell.z == line) { return true; }",
     "&& cell.z == room.Bounds.CenterCell.z) { return true; }"),

    ("the straight run stops preferring the first room's own centre line", PLANNER,
     "                line = centreA.z >= low && centreA.z <= high ? centreA.z" + NL
     + "                    : centreB.z >= low && centreB.z <= high ? centreB.z : (low + high) / 2;",
     "                line = (low + high) / 2;"),

    # ------------------------------------------------------------- the lane, and filling the map
    ("THE SPAN VARIATION IS ALLOWED TO EAT THE CORRIDOR LANE", PLANNER,
     "            if (reach > lane) { reach = lane; }" + NL, ""),

    ("THE SLOT GRID GOES BACK TO TEN PER AXIS AND A DEEP LEVEL IS BARE ROCK AGAIN", PLANNER,
     "internal const int MaxSlotsPerAxis = 8;", "internal const int MaxSlotsPerAxis = 10;"),

    ("the margin goes back to throwing away a fifth of every map", PLANNER,
     "internal const int Margin = 6;", "internal const int Margin = 14;"),
]'''

text = io.open(PLANTS, encoding="utf-8").read()
problems = 0

if text.count(STALE) != 1:
    print("stale plant not found exactly once (%d)" % text.count(STALE))
    problems += 1
else:
    text = text.replace(STALE, REAIMED)
    print("re-aimed the toothless plant")

if text.count(NL + "]" + NL) < 1:
    print("plant list terminator not found")
    problems += 1
else:
    # The LAST bare `]` on its own line closes PLANTS.
    at = text.rfind(NL + "]" + NL)
    text = text[:at] + NL + NEW + text[at + len(NL + "]"):]
    print("added %d new plants" % NEW.count('    ("'))

if problems:
    sys.exit(1)
io.open(PLANTS, "w", encoding="utf-8", newline=NL).write(text)
print("written")
