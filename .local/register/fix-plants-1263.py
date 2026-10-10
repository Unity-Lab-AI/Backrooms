# -*- coding: utf-8 -*-
"""Plants for the margin fallback, the landmark split and the conduit guard.

Each one re-creates the defect that cost the eleventh launch, so the claims that now guard them
are proved to be load-bearing rather than merely present.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-generation.py")

ANCHOR = u"PLANTS = ["

NEW = u'''PLANTS = [
    # ------------------------------- the furniture rule that stopped a level being built
    # `Place` refused any cell whose footprint had an edifice within one. The room's wall, its
    # pillar lattice, the rock in its shaped corners, the lamp on every pillar and every fixture
    # already placed are all edifices, on top of the reserved three-cell route cross -- so a room
    # could be left with ONE placeable cell. The first fixture took it and the second threw out
    # of `GenStep.Generate`, stopping the level halfway: the owner got a Backrooms map with no
    # content and a door that was never marked.
    ("THE WALKABLE MARGIN GOES BACK TO BEING MANDATORY", CONTENT,
     "                if (!footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null))"
     + NL + "                { return cell; }",
     "                if (footprint.ExpandedBy(1).Cells.Any(c => c.InBounds(map) && c.GetEdifice(map) != null))"
     + NL + "                { continue; }"),

    ("the cell without a margin is found and then thrown away", CONTENT,
     "            return withoutMargin;", "            return IntVec3.Invalid;"),

    ("EVERY FAMILY FIXTURE BECOMES REQUIRED AGAIN", CONTENT,
     "                count, false);", "                count, true);"),

    ("a decoration goes back to being a throwing Place call", CONTENT,
     '                            Decorate(map, room, coordinate, "Stool", reserved, seed, 1);'
     + NL + "                            break;" + NL + '                        case "survey_lobby":',
     '                            Place(map, room, coordinate, "Stool", reserved, seed, 1);'
     + NL + "                            break;" + NL + '                        case "survey_lobby":'),

    ("the cell search is derived a second time inside TryPlace", CONTENT,
     "            IntVec3 cell = FixtureCell(map, room, reserved, thing, rotation, preferred);"
     + NL + "            if (!cell.IsValid) { return null; }",
     "            IntVec3 cell = interior_unused;" + NL + "            if (!cell.IsValid) { return null; }"),

    ("A LANDMARK REFUSAL GOES SILENT AGAIN", CONTENT,
     '                    Log.Warning("[Rimrooms][Generation] No cell for the landmark " + defName',
     '                    Log.Warning("[Rimrooms][Generation] No cell for a landmark" + ("" + defName'),

    ("the route cross is derived in two places again", CONTENT,
     "                { if (OnRouteCross(room, cell)) { reserved.Add(cell); } }",
     "                { if (Math.Abs(cell.x - room.Bounds.CenterCell.x) <= 1) { reserved.Add(cell); } }"),

    # ------------------------------------------- two transmitters on one cell
    # Core refuses the second and leaves its bookkeeping inconsistent, so
    # PowerConnectionMaker.TryConnectToAnyPowerNet throws out of Map.FinalizeInit and then out of
    # every Update for the rest of the session.
    ("A SECOND TRANSMITTER LANDS ON A CELL THAT ALREADY HAS ONE", GEN,
     "            if (AlreadyTransmits(map, cell)) { return; }" + NL
     + "            Thing conduit = MakeBuilding(conduitDef, null);" + NL
     + "            conduit.SetFaction(Faction.OfPlayer);" + NL
     + "            GenSpawn.Spawn(conduit, cell, map, Rot4.North);" + NL
     + "        }",
     "            Thing conduit = MakeBuilding(conduitDef, null);" + NL
     + "            conduit.SetFaction(Faction.OfPlayer);" + NL
     + "            GenSpawn.Spawn(conduit, cell, map, Rot4.North);" + NL
     + "        }"),

    ("the guard is kept on one path and dropped from the other", GEN,
     "            // Not a generator fault: the cell is already wired, by somebody else, and that is"
     + NL + "            // exactly as good as wiring it ourselves." + NL
     + "            if (AlreadyTransmits(map, cell)) { return; }" + NL, ""),

    ("and it stops asking Core whether the thing transmits", GEN,
     "                if (thing != null && thing.def != null && thing.def.EverTransmitsPower)",
     "                if (thing != null && thing.def != null && thing.def == conduitDefUnused)"),
'''

text = io.open(SUITE, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("ten plants added to plant-generation.py")
