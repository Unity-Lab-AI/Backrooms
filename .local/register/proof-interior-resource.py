# -*- coding: utf-8 -*-
"""Assert the interior of a coordinate is a resource: mineable, and worth lifting.

The property this exists for
----------------------------
Three owner directions, 2026-09-29:

    "and areas minable and of all types of materisals throughout"
    "and capte ands tile can all be uninstalled , moved, resued , sold , studied"
    "all of it"

The 0.12.14-dev backlog audit marked two of those **STILL OPEN, confirmed unbuilt by grep**, and
invented a third row claiming vanilla returns no materials for a lifted floor. **All three verdicts
were wrong**, and this proof exists because of how they were wrong:

  * The mineable fill IS built -- `FillWithRock` and `NaturalRockTypesFor` in
    `GenStep_BackroomsDestination.cs`. The audit grepped `Generation/` for "Mineable", "Granite",
    "RockRubble" and so on; the code contains none of those words, because it asks
    `Find.World.NaturalRockTypesIn(map.Tile)` for whatever the tile actually has. **A grep for the
    words I expected, in the file I expected, is not a search.**
  * `BackroomsContainment.cs` was accused of claiming mineability its code does not implement.
    **The comment was telling the truth**; the implementation is in a different file.
  * Vanilla `TerrainGrid.RemoveTopLayer` defaults `doLeavings: true` and calls
    `GenLeaving.DoLeavingsFor(TerrainDef, cell, map)`, which returns `CostListAdjusted()` times
    `resourcesFractionWhenDeconstructed` -- **0.5 by default on `BuildableDef`**.

So the interior already is a resource, and nothing needed building. What needed building is this:
**the behaviour depends entirely on which terrains the palette picks**, and nothing was watching.

Core ships terrains that return NOTHING: `PackedDirt`, `BrokenAsphalt`, and stone tiles override
`resourcesFractionWhenDeconstructed` to 0. If a future palette change swapped a carpet for one of
those, *"capte ands tile can all be uninstalled, moved, resued, sold"* would silently stop being
true -- no build error, no checker, no log. That is the failure this asserts against.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"

failures = []


def check(claim, condition, detail=""):
    print("  %s %s %s" % ("OK  " if condition else "FAIL", claim, detail if not condition else ""))
    if not condition:
        failures.append(claim)


def read(*parts):
    return io.open(os.path.join(*parts), encoding="utf-8-sig").read()


def strip_comments(text):
    """Comments must never satisfy or break a claim.

    Both of this proof's first-run failures were comments. The roof claim searched for
    'RoofConstructed' and found the two doc comments that say the roof is deliberately NOT
    RoofConstructed -- a claim broken by the code explaining itself. Sixth time in this project.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("//") and not line.lstrip().startswith("///"))


# ---------------------------------------------------------------- 1. the interior is mineable
generation = strip_comments(read(SRC, "Generation", "GenStep_BackroomsDestination.cs"))

check("the solid space between rooms is filled with rock",
      "FillWithRock(map, coordinate, rockTypes)" in generation,
      "-- the owner direction is that areas are mineable throughout; an empty void is not")
check("the rock types come from the world tile, not from a hardcoded list",
      "Find.World.NaturalRockTypesIn(map.Tile)" in generation,
      "-- 'of all types of materisals' means whatever that tile actually has, which also keeps "
      "this Core-only and correct on any planet")
check("the fill is deterministic per cell",
      re.search(r'CampaignSeed\.Derive\(coordinate\.Seed,\s*"rock:"', generation) is not None,
      "-- the same coordinate must look the same on reload, invariant 27")
check("rock is cleared where a room is carved",
      "ClearRock(map, cell)" in generation,
      "-- a room full of rock is not a room")
check("mining can never open a hole in the world",
      "RoofDefOf.RoofRockThick" in generation and "RoofConstructed" not in generation,
      "-- thick roof never vanishes on collapse, which is what lets a coordinate be mined to "
      "nothing and still have no outside. Constructed roof IS removable")

# ---------------------------------------------------------------- 2. lifting a floor pays
palette = strip_comments(read(SRC, "Generation", "BackroomsPalette.cs"))

# Only the terrains the palette lays as a ROOM FLOOR are relevant, and they are found by the
# assignment that lays them -- `floor = Named<TerrainDef>("X")` and the same for `accent`.
#
# The first version of this claim collected EVERY Named<TerrainDef> call and then skipped any
# terrain with no cost list, on the reasoning that natural terrain was never built and cannot be
# lifted. That reasoning excused the exact case this proof exists for: a fault-plant swapping a
# palette floor for PackedDirt PASSED, because PackedDirt has no cost list and was skipped as
# "not a built floor". **A filter that skips the case it is guarding against is worse than no
# check**, and it took a planted fault to find it -- reading it would not have.
#
# So now a palette floor must satisfy BOTH halves: it cost something to lay, and it returns some
# of that when lifted. PackedDirt fails the first, a stone tile fails the second.
# A palette floor is named one of two ways: directly, or through the Carpet helper, which resolves
# a template-generated def from a structure colour.
floors = set(re.findall(r'(?:floor|accent)\s*=\s*Named<TerrainDef>\("([A-Za-z0-9_]+)"\)', palette))
for color in re.findall(r'(?:floor|accent)\s*=\s*Carpet\("([A-Za-z0-9_]+)"\)', palette):
    floors.add("Carpet" + (color[len("Structure_"):] if color.startswith("Structure_") else color))
print("floors the palette lays: %s" % (", ".join(sorted(floors)) or "NONE"))
check("the palette's room floors were found",
      len(floors) >= 3,
      "-- found %d; without them every claim below is vacuous" % len(floors))

# THE DEFECT GUARD. There is no TerrainDef called "Carpet" -- Core ships a TerrainTemplateDef of
# that name and generates one real terrain per structure colour. Asking for "Carpet" returns null
# silently, every carpet band falls through to its fallback, and the depth-1 yellow rooms were laid
# in WOOD PLANK FLOORING from the day the palette shipped. Nothing said so.
check("the palette never asks for a bare Carpet terrain",
      'Named<TerrainDef>("Carpet")' not in palette,
      '-- there is no TerrainDef called "Carpet"; GetNamedSilentFail returns null and the ?? '
      'fallback makes the wrong floor look deliberate')
check("carpet is resolved from the colour the band already names",
      'Carpet("Structure_' in palette and 'private static TerrainDef Carpet(' in palette,
      "-- a carpet cannot be tinted at runtime, so the colour has to pick the def")

# Enumerate the installed game rather than trusting a remembered list -- invariant 19. This has to
# include template-generated defs, which exist only at runtime: TerrainDefGenerator_Carpet names
# them `Carpet` + the ColorDef name with "Structure_" removed.
terrain_cost = {}
terrain_fraction = {}
structure_colors = set()
templates = {}
parsed = skipped = 0
for path in glob.glob(os.path.join(GAME, "**", "*.xml"), recursive=True):
    try:
        root = ET.parse(path).getroot()
        parsed += 1
    except Exception:
        skipped += 1
        continue
    for tag, bucket in (("TerrainDef", terrain_cost), ("TerrainTemplateDef", templates)):
        for node in root.iter(tag):
            name = (node.findtext("defName") or "").strip()
            if not name:
                continue
            cost = node.find("costList")
            costs = [] if cost is None else [c.tag for c in list(cost)]
            fraction = node.findtext("resourcesFractionWhenDeconstructed")
            fraction = 0.5 if fraction is None else float(fraction)
            bucket[name] = costs
            if tag == "TerrainDef":
                terrain_fraction[name] = fraction
            else:
                templates[name] = (costs, fraction)
    for node in root.iter("ColorDef"):
        name = (node.findtext("defName") or "").strip()
        if name.startswith("Structure_"):
            structure_colors.add(name)

# Expand each template across the structure colours, exactly as the generator does.
for template, (costs, fraction) in list(templates.items()):
    if not isinstance(costs, tuple) and template in terrain_cost and not isinstance(costs, list):
        continue
    for color in structure_colors:
        generated = template + color[len("Structure_"):]
        terrain_cost.setdefault(generated, costs if isinstance(costs, list) else costs[0])
        terrain_fraction.setdefault(generated, fraction if not isinstance(fraction, tuple) else fraction[1])

check("the installed game's terrain defs were enumerated, templates expanded",
      len(terrain_cost) > 20 and len(structure_colors) > 10,
      "-- %d terrains, %d structure colours, %d files unparseable; without real data every claim "
      "below is vacuous" % (len(terrain_cost), len(structure_colors), skipped))

unknown, costless, worthless = [], [], []
for name in sorted(floors):
    if name not in terrain_cost:
        unknown.append(name)
        continue
    if not terrain_cost[name]:
        costless.append(name)
        continue
    if terrain_fraction.get(name, 0.5) <= 0.0:
        worthless.append("%s (fraction %.2f)" % (name, terrain_fraction[name]))

check("every floor the palette lays exists in the installed game",
      not unknown,
      "-- %s: GetNamedSilentFail returns null and the floor is silently never laid"
      % ", ".join(unknown))
check("every floor the palette lays cost something to build",
      not costless,
      "-- %s: a floor with no cost list returns NOTHING when lifted, however generous the "
      "fraction, so 'uninstalled, moved, resued, sold' is empty for it" % ", ".join(costless))
check("every floor the palette lays returns some of that cost when lifted",
      not worthless,
      "-- %s: Core ships stone tiles, BrokenAsphalt and PackedDirt that override the fraction to "
      "0, and swapping one in would silently end the owner direction" % ", ".join(worthless))

for name in sorted(floors):
    if name in terrain_cost and terrain_cost[name]:
        print("  %s -> %s at fraction %.2f" % (name, ", ".join(terrain_cost[name]),
                                               terrain_fraction.get(name, 0.5)))

# ---------------------------------------------------------------- 3. nothing is protected from it
# "all rooms and walls and doors are all deconstructable" -- generation places with no faction, so
# everything is an ordinary building. A faction assignment here would make the interior untouchable.
# Keyed off the SPAWN, not off the absence of SetFaction anywhere in the file. The first version
# of this claim asserted "SetFaction" never appears -- and it appears six times, deliberately, on
# the return anchor, generator, climate unit, lights, conduit and doors. Those are the PLAYER'S
# faction, which is exactly what makes them the player's equipment to use. My claim was backwards.
#
# What actually matters is narrower and is invariant 75: the STRUCTURE -- walls and rock -- is
# placed with no faction, so it is ordinary deconstructable and mineable content.
wall_body = generation[generation.index("private static void PlaceWall("):]
wall_body = wall_body[:wall_body.index("private static IntVec3 FindBuildingCell(")]
check("a generated wall is spawned with no faction",
      "GenSpawn.Spawn(wall, cell, map);" in wall_body and "SetFaction" not in wall_body,
      "-- a faction-owned wall is not deconstructable by the player, which would contradict "
      "'all rooms and walls and doors are all deconstructable' and invariant 75")

fill_body = generation[generation.index("private static void FillWithRock("):]
fill_body = fill_body[:fill_body.index("private static void ClearRock(")]
check("generated rock is spawned with no faction",
      "GenSpawn.Spawn(ThingMaker.MakeThing(rock), cell, map);" in fill_body
      and "SetFaction" not in fill_body,
      "-- faction-owned rock cannot be mined, which is the whole of the owner direction")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: the interior is mineable, liftable and worth lifting")
