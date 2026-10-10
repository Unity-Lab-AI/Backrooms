# -*- coding: utf-8 -*-
"""Teach proof-interior-resource.py about template-generated carpet defs, and guard the defect."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, '.local', 'register', 'proof-interior-resource.py')

s = io.open(PATH, encoding='utf-8').read()

old_start = s.index('floors = set(re.findall(')
old_end = s.index('# ---------------------------------------------------------------- 3. nothing is protected')

new_block = '''# A palette floor is named one of two ways: directly, or through the Carpet helper, which resolves
# a template-generated def from a structure colour.
floors = set(re.findall(r'(?:floor|accent)\\s*=\\s*Named<TerrainDef>\\("([A-Za-z0-9_]+)"\\)', palette))
for color in re.findall(r'(?:floor|accent)\\s*=\\s*Carpet\\("([A-Za-z0-9_]+)"\\)', palette):
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

'''

io.open(PATH, 'w', encoding='utf-8', newline='').write(s[:old_start] + new_block + s[old_end:])
print('proof updated: templates expanded, and the bare-Carpet defect is guarded')
