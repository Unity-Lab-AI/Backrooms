# -*- coding: utf-8 -*-
"""Plants for this checkpoint: the forms, the hallways, the frontier menu, the food."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAYOUT = os.path.join(REPO, ".local", "register", "plant-coordinate-layout.py")
LINKS = os.path.join(REPO, ".local", "register", "plant-gate-links-carry.py")
GENERATION = os.path.join(REPO, ".local", "register", "plant-generation.py")

# ------------------------------------------------------------------ the shape forms
LAYOUT_OLD = u'''    ("ROOMS GO BACK TO BEING PLAIN RECTANGLES", PLANNER,
     "            if (room == null || depth <= 1) { yield break; }",
     "            if (room != null) { yield break; }"),
'''
LAYOUT_NEW = u'''    ("ROOMS GO BACK TO BEING PLAIN RECTANGLES", PLANNER,
     "            if (room == null || room.index == 0 || depth <= 1) { yield break; }",
     "            if (room != null) { yield break; }"),

    # **THE PROBE MEASURED THE OLD SHAPING RUNNING THE WHOLE TIME** -- 89% of depth-1 rooms
    # carried rock at 7% of their interior -- so the amount was never the problem and the obvious
    # guess, more reach, would only have produced rounder squares. There was exactly ONE form.
    # Owner: *"they were all just square rooms again..wtf dont u know any other compbinations"*.
    ("THERE IS ONLY ONE ROOM FORM AGAIN", PLANNER,
     "            int form = roll % ShapeForms;",
     "            int form = 0;"),

    ("the form count collapses to the corner masses", PLANNER,
     "        internal const int ShapeForms = 7;",
     "        internal const int ShapeForms = 1;"),

    ("the grand hall starts being deranged like every other room", PLANNER,
     "            if (room == null || room.index == 0 || depth <= 1) { yield break; }",
     "            if (room == null || depth <= 1) { yield break; }"),
'''

# ------------------------------------------------------- the frontier walk-through
LINKS_OLD = u'''    ("the glow veto stops asking whether this is a live gate", COMP,
     "        public bool ShouldBeLitNow() { return IsLiveGate; }",
     "        public bool ShouldBeLitNow() { return true; }"),
'''
LINKS_NEW = u'''    ("the glow veto stops asking whether this is a live gate", COMP,
     "        public bool ShouldBeLitNow() { return IsLiveGate || frontierGate; }",
     "        public bool ShouldBeLitNow() { return true; }"),

    # **`NaturalFrontierService.Discover` HAD ZERO CALLERS.** The draw, the cap, the guaranteed
    # pair and twenty `RR_Frontier_*` strings were all written for a float menu that did not
    # exist. Owner, after walking a whole finished level: *"i never found any natural cates to the
    # world map tiles or natural portals to deep into the backrroooms"*.
    ("NOTHING ASKS A DOOR WHETHER IT IS A WAY ONWARD AGAIN", COMP,
     "                foreach (FloatMenuOption option in FrontierOptions(selPawn)) { yield return option; }"
     + chr(10), ""),

    ("the way onward can be seen but never walked through", COMP,
     "                CompanyActionResult found = NaturalFrontierService.Discover(parent);",
     "                CompanyActionResult found = CompanyActionResult.Applied();"),

    ("AN ORDINARY COLONY DOOR STARTS GLOWING BLUE ON INSTALL", COMP,
     "                if (!(parent.Map != null && parent.Map.Parent is RimroomsDestinationMapParent))"
     + chr(10) + "                { return false; }" + chr(10), ""),
'''

# ------------------------------------------------------------- the hallways as rooms
GEN_ANCHOR = u"PLANTS = ["
GEN_NEW = u'''PLANTS = [
    # ------------------------------------------------- a hallway is a room
    # Two hardcoded values made every corridor a grey steel service tunnel between themed rooms.
    # Owner: *"the hall ways are just rectangles and arnt correctly the themed color and
    # materials"*, and *"i see the whole map is almost like a string of pears. when it should just
    # be basicly \\"rooms\\" as halways with the exact shit thats in the rooms"*.
    ("CORRIDOR WALLS GO BACK TO BEING HARDCODED STEEL", GEN,
     "            PlaceWall(map, cell, wallDef, wallStuff);" + NL
     + "            Thing wall = cell.InBounds(map) ? cell.GetEdifice(map) : null;",
     "            PlaceWall(map, cell, ThingDefOf.Wall, ThingDefOf.Steel);" + NL
     + "            Thing wall = cell.InBounds(map) ? cell.GetEdifice(map) : null;"),

    ("a corridor stops taking the band's floor", GEN,
     "            TerrainDef terrain = look.accent != null && along % 4 == 0 ? look.accent : look.floor;",
     "            TerrainDef terrain = look.floor;" + NL
     + "            if (terrain == null) { return; }" + NL
     + "            terrain = terrain;"),

    ("a corridor wall stops taking the band's colour", GEN,
     "            { wall.TryGetComp<CompColorable>()?.SetColor(look.wallColor); }", "            { }"),

    ("THE CORRIDOR SIDE CELLS ARE COLLECTED AND NEVER SPENT", GEN,
     "                DressCorridors(map, coordinate, corridorSides, lightDef, placedLights," + NL
     + "                    reservedProviderCells);" + NL, ""),

    ("the hallways stop being lit", GEN,
     "                if (lightDef != null && index % CorridorLampSpacing == 0)",
     "                if (false)"),

    ("the hallways stop carrying anything the rooms carry", GEN,
     "                if (fixtures.Count == 0 || index % CorridorFixtureSpacing != 0) { continue; }",
     "                if (true) { continue; }"),

    ("furniture lands on the middle of a corridor and blocks the route", GEN,
     "                                if (offset != 0 && (offset == halfWidth - 1 || offset == 1 - halfWidth))"
     + NL + "                                { sides.Add(cell); }",
     "                                sides.Add(cell);"),
'''

EDITS = [
    (LAYOUT, [(LAYOUT_OLD, LAYOUT_NEW)]),
    (LINKS, [(LINKS_OLD, LINKS_NEW)]),
    (GENERATION, [(GEN_ANCHOR, GEN_NEW)]),
]

for path, edits in EDITS:
    text = io.open(path, encoding="utf-8").read()
    problems = []
    for old, _ in edits:
        if text.count(old) != 1:
            problems.append("%s: %d of %r" % (os.path.basename(path), text.count(old), old[:58]))
    if problems:
        for problem in problems:
            print("ANCHOR PROBLEM: %s" % problem)
        raise SystemExit(1)
    for old, new in edits:
        text = text.replace(old, new, 1)
    io.open(path, "w", encoding="utf-8", newline="").write(text)
    print("updated %s" % os.path.basename(path))
