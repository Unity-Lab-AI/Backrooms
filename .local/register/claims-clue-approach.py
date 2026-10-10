# -*- coding: utf-8 -*-
"""Claims and plants for the landmark's approach, and for the power rebuild that asked twice."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-generation.py")

ANCHOR = u'''print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)'''

CLAIMS = u'''# ----------------------------------------------- the landmark keeps a way up to it
# `ValidatePlacedLayout` requires a standable, entry-reachable cell orthogonally beside every clue
# landmark, and **nothing reserved one.** Every landmark this builder places is PassThroughOnly, so
# its own cell never counts; `FixtureCell` relaxed its margin to a preference; and `DressRoom`
# places fixtures until one will not fit, so the last cells it takes are the no-margin cells flush
# against whatever is there. Including all four neighbours of the landmark.
#
# That threw `RR_Generation_UnreachableRequiredCell` out of `GenStep.Generate`, so the level was
# never finished, so `EnsureSite` failed, so `SoloGroupOpening` never moved anybody inside and
# never registered the way out. Owner: *"i ended up in the world map with no connection to the
# back rooms.. i should of been in the back rooms and i dont have a warp do to get back"*.
check("THE LANDMARK IS OFFERED A CELL BESIDE THE ROOM'S OWN RESERVED ROUTE CROSS",
      "private static HashSet<IntVec3> RouteTrunk(Map map, RoomRecord room)" in content
      and "HashSet<IntVec3> trunk = required ? RouteTrunk(map, room) : null;" in content
      and "trunk != null && trunk.Count > 0 ? trunk : null);" in content,
      "-- DEFINED AND CALLED, and called only for the landmark. A cross cell is reserved for the "
      "whole of population, so a landmark beside one cannot be sealed in by anything placed "
      "later: the guarantee is structural instead of lucky")

check("and the trunk is the JOINED-UP part of the cross, not merely the cross",
      "if (!interior.Contains(next) || !OnRouteCross(room, next)) { continue; }" in content
      and "if (!ClearTrunkCell(map, next) || !trunk.Add(next)) { continue; }" in content
      and "private static bool ClearTrunkCell(Map map, IntVec3 cell)" in content
      and "return cell.InBounds(map) && cell.Standable(map) && cell.GetEdifice(map) == null;"
      in content,
      "-- a pillar or a stand of shaped rock severs an arm, and a cell in a severed arm is "
      "standable and unreachable, which is the exact pair of properties the validator rejects")

check("and the approach test is ORTHOGONAL, the same test the validator applies",
      "private static bool TouchesApproach(CellRect footprint, HashSet<IntVec3> approach)"
      in content
      and "if (Math.Abs(cell.x - part.x) + Math.Abs(cell.z - part.z) == 1) { return true; }"
      in content
      and "if (approach != null && !TouchesApproach(footprint, approach)) { continue; }" in content,
      "-- a diagonal neighbour is not an approach in `ValidatePlacedLayout`, so it is not one "
      "here. Two derivations of one rule is the defect this project keeps meeting")

check("and it FALLS BACK rather than refusing, so it can never cost a level",
      "if (!cell.IsValid && trunk != null && trunk.Count > 0)" + chr(10)
      + "            { cell = FixtureCell(map, room, reserved, thing, rotation, preferred, null); }"
      in content,
      "-- refusing a landmark throws `RR_Generation_NoSafeRoomCell`, which is the same dead level "
      "by another name. `check-planner-layouts.py` measures how often the fallback is needed and "
      "fails if it ever is")

check("AND NOTHING ELSE IS PLACED BESIDE THE LANDMARK AFTERWARDS",
      "if (required)" in content
      and ("foreach (IntVec3 ring in thing.OccupiedRect().ExpandedBy(1).Cells)" + chr(10)
           + "                { reserved.Add(ring); }") in content,
      "-- the ring it was placed with is the ring it keeps, which is exactly what `Populate` "
      "already does for the gate anchor. Decorations are allowed to be absent; a clue is not "
      "allowed to be unreachable")

check("and an unreachable clue is REPORTED rather than fatal",
      "has no reachable cell beside it, so that one room's" in genstep
      and genstep.count('throw new InvalidOperationException("RR_Generation_UnreachableRequiredCell")')
      == 1,
      "-- the generator's own rule, applied where it had been missed: *\\"A coordinate whose "
      "heater or one lamp failed to join the grid is dark and cold and completely playable. A "
      "coordinate that does not exist costs the player the gate that leads to it.\\"* One throw "
      "site left for that key, because two raising one key is why the log could not say which "
      "had fired")

# -------------------------------------------- the power rebuild that asked sixty-two times
# The owner's log carried sixty-two copies of one warning and, in the middle of them, Core's
# *"Tried to register trasmitter ... but there is already a power net here"* naming the generator
# on the generator's own cell -- which no conduit of ours can occupy. Core clears its delayed
# queue only after the loop that processes it, so a throw part-way leaves applied entries queued
# and the next call re-applies them. The retry made the permanent fault.
check("A FAILED POWER REBUILD IS NOT ASKED AGAIN THIS GENERATION",
      "private static bool RebuildPowerNets(Map map, CoordinateRecord coordinate)" in genstep
      and "if (!RebuildPowerNets(map, coordinate)) { return false; }" in genstep
      and "if (RebuildPowerNets(map, coordinate) &&" in genstep,
      "-- the first failure was the real one and the next sixty-one were self-inflicted")

check("and the sweep that produced them stops with it",
      "private static bool ConnectStrayConsumers(Map map, CoordinateRecord coordinate," in genstep
      and "if (plant == null || wiredCells == null) { return true; }" in genstep,
      "-- every decision after a failed rebuild reads `power.PowerNet` out of bookkeeping Core "
      "has already said is wrong")

check("and the exception is logged IN FULL, once",
      '+ exception);' in genstep
      and "will not be asked again this" in genstep,
      "-- sixty-two lines reading `(NullReferenceException)` could not name the Core method or "
      "the thing, and that was the whole question")

''' + ANCHOR

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, CLAIMS, 1))
print("nine claims added for the landmark approach and the power rebuild")

P_ANCHOR = u"PLANTS = ["
P_NEW = u'''PLANTS = [
    # --------------------------------------- the landmark's approach, and the retry
    ("THE LANDMARK IS NO LONGER OFFERED A CROSS-ADJACENT CELL", CONTENT,
     "            HashSet<IntVec3> trunk = required ? RouteTrunk(map, room) : null;",
     "            HashSet<IntVec3> trunk = null;"),

    ("the trunk takes severed arms as well as the joined-up part", CONTENT,
     "                    if (!ClearTrunkCell(map, next) || !trunk.Add(next)) { continue; }",
     "                    if (!trunk.Add(next)) { continue; }"),

    ("a diagonal neighbour counts as an approach", CONTENT,
     "                    if (Math.Abs(cell.x - part.x) + Math.Abs(cell.z - part.z) == 1) { return true; }",
     "                    return true;"),

    ("THE DRESSING CAN STILL FILL THE CELLS BESIDE THE LANDMARK", CONTENT,
     "                foreach (IntVec3 ring in thing.OccupiedRect().ExpandedBy(1).Cells)" + NL
     + "                { reserved.Add(ring); }" + NL, ""),

    ("the approach requirement is read and then not applied", CONTENT,
     "                if (approach != null && !TouchesApproach(footprint, approach)) { continue; }" + NL,
     ""),

    ("AN UNREACHABLE CLUE TAKES THE WHOLE LEVEL AGAIN", GEN,
     "                    Log.Warning(\\"[Rimrooms][Generation] Coordinate \\" + coordinate.Id + \\": the clue \\"",
     "                    throw new InvalidOperationException(\\"RR_Generation_UnreachableRequiredCell\\"); Log.Warning(\\"[Rimrooms][Generation] Coordinate \\" + coordinate.Id + \\": the clue \\""),

    ("the stray-consumer sweep carries on after a failed rebuild", GEN,
     "                if (!RebuildPowerNets(map, coordinate)) { return false; }",
     "                RebuildPowerNets(map, coordinate);"),

    ("the rebuild is asked again after it refused", GEN,
     "                if (RebuildPowerNets(map, coordinate) &&",
     "                RebuildPowerNets(map, coordinate);" + NL + "                if (true &&"),

    ("the exception is logged by type name only, as it was", GEN,
     "                    + exception);",
     "                    + exception.GetType().Name + \\").\\");"),
'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(P_ANCHOR) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(P_ANCHOR))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite.replace(P_ANCHOR, P_NEW, 1))
print("nine plants added")
