# -*- coding: utf-8 -*-
"""Restate the material claims to the owner's specification, not to mine.

Two claims objected correctly and both encoded MY design argument rather than a property worth
protecting:

  * *"the material comes from the coordinate -- per coordinate, not per room and not per item: a
    room with three materials in it reads as noise, a coordinate fitted out in one reads as a
    place"*, and
  * the palette-grows-with-depth claim, which assumed a palette exists at every depth.

Owner correction, verbatim: *"this is wrong we want every type of wall and material for all things
randomly"* and *"but depth 0 in the backrroms is the standard yellow style"*. So the property to
protect is the **split**: coherent at level 0, every type per thing deeper in.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

text = io.open(PROOF, encoding="utf-8").read()

EDITS = [
    ('''check("the material comes from the coordinate",
      "CoordinateMaterials.StuffFor(definition, coordinate)" in content,
      "-- per coordinate, not per room and not per item: a room with three materials in it "
      "reads as noise, a coordinate fitted out in one reads as a place")''',
     '''# **RESTATED, and this claim was right to fail.** It asserted "per coordinate, not per room and
# not per item", with a rationale that was MINE: that per-item choice reads as noise. The owner
# overruled it in their own words -- *"this is wrong we want every type of wall and material for
# all things randomly"* -- while holding the other half fixed: *"but depth 0 in the backrroms is
# the standard yellow style"*. What is worth protecting is that SPLIT.
check("the material comes from the coordinate, and per fixture",
      "CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot)" in content
      and content.count("CoordinateMaterials.StuffFor(definition, coordinate, seed * 31 + slot)") == 2,
      "-- the variant is what lets two identical fixtures in one room be different materials "
      "deeper in, and BOTH placement helpers have to pass it or the dressing path silently goes "
      "back to one material per place")'''),

    ('''# **RESTATED 0.12.52-dev, and the claim was right to fail.** It asserted `PaletteSize = 3`, which
# encoded the flat constant the owner asked to remove: *"with the wild variatiosn of material
# typeds ... found everywher deeper in"*. What is worth protecting is not the number 3 — it is that
# the palette is **bounded and small**, because a place fitted out in a dozen materials has no
# character, AND that it **grows inward**, because that is the direction.
shallow = re.search(r"const\\s+int\\s+ShallowPaletteSize\\s*=\\s*(\\d+)", materials)
deep = re.search(r"const\\s+int\\s+DeepPaletteSize\\s*=\\s*(\\d+)", materials)
# The FUNCTION'S BODY, because the first version of this asserted only that the function existed
# and was called -- which a plant that made its body return a flat constant satisfied completely.
# A function taking `depth` is not a function that uses it.
size_body = body_of(materials, "int PaletteSizeFor(int depth)")
check("THE PALETTE GROWS WITH DEPTH INSTEAD OF BEING A CONSTANT",
      shallow is not None and deep is not None
      and int(shallow.group(1)) < int(deep.group(1))
      and "internal static int PaletteSizeFor(int depth)" in materials
      and "PaletteSizeFor(coordinate == null ? 1 : coordinate.Depth)" in materials
      and "depth" in size_body.replace("int depth", "")
      and "DeepPaletteSize" in size_body,
      "-- shallow %s, deep %s. A flat size meant the deepest coordinate in the game was fitted "
      "out in exactly as few materials as the shallowest"
      % (shallow.group(1) if shallow else "MISSING", deep.group(1) if deep else "MISSING"))

check("the shallowest band stays monotonous",
      shallow is not None and int(shallow.group(1)) <= 3,
      "-- the yellow rooms read as a place because they are monotonous, which is the same reason "
      "Derange and RockIntrusionCells leave depth 1 alone")

check("and the deepest is still bounded",
      deep is not None and int(deep.group(1)) <= 8,
      "-- a palette is walked in order and the first entry a fixture can take wins, so past a "
      "handful the later entries are chosen for almost nothing")

check("THE CACHE IS KEYED BY DEPTH AS WELL AS BY ID",
      \'coordinate.Id ?? "") + ":" + coordinate.Depth\' in materials,
      "-- the id alone was enough while the palette was one size everywhere. It is not now, and a "
      "cache that ignored depth would hand a deep coordinate a shallow palette for the rest of "
      "the session")''',
     '''# **RESTATED TWICE.** First it asserted `PaletteSize = 3`, the flat constant the owner asked to
# remove. Then it asserted a palette that grows with depth -- which the owner ALSO overruled,
# because a growing palette is still a palette, and *"every type of wall and material for all
# things randomly"* is not a palette at all. The specification is a split, and this is it.
shallow = re.search(r"const\\s+int\\s+ShallowPaletteSize\\s*=\\s*(\\d+)", materials)
coherent = re.search(r"const\\s+int\\s+CoherentDepth\\s*=\\s*(\\d+)", materials)
wild_body = body_of(materials, "ThingDef WildStuffFor(ThingDef definition, CoordinateRecord coordinate, int variant)")

check("LEVEL ZERO IS THE STANDARD YELLOW STYLE, SHARING ONE NARROW PALETTE",
      coherent is not None and int(coherent.group(1)) >= 1
      and shallow is not None and int(shallow.group(1)) <= 3
      and "if (depth > CoherentDepth)" in materials,
      "-- owner direction, verbatim: *\\"but depth 0 in the backrroms is the standard yellow "
      "style\\"*, and earlier *\\"yellow carpet and yellow wood walls for the main backrooms "
      "look\\"*. A level where the table, the shelf and the walls match is what makes the yellow "
      "rooms read as a place. CoherentDepth %s, palette %s"
      % (coherent.group(1) if coherent else "MISSING",
         shallow.group(1) if shallow else "MISSING"))

check("DEEPER IN, EVERY THING DRAWS FROM EVERY TYPE CORE ALLOWS IT",
      "GenStuff.AllowedStuffsFor(definition)" in wild_body
      and "allowed[Math.Abs(seed) % allowed.Count]" in wild_body,
      "-- owner correction, verbatim: *\\"this is wrong we want every type of wall and material "
      "for all things randomly\\"*. Not a palette down there at all: the full set for this "
      "particular def, indexed per fixture")

check("the wild path is still a pure function of the seed",
      "DestinationService.StableHash(coordinate.Seed," in wild_body
      and "Rand." not in wild_body,
      "-- a coordinate is regenerated from its seed, so two players on one seed must see the "
      "same place")

check("AND IT IS STILL SORTED, SO A MOD LIST CANNOT CHANGE A COORDINATE",
      "OrderBy(candidate => candidate.defName, StringComparer.Ordinal)" in wild_body,
      "-- AllowedStuffsFor returns database order, which depends on which mods are installed and "
      "in what order. This is the load-bearing line in the whole file")

check("it honours Core's own opt-out even on the wild path",
      "allowedInStuffGeneration" in wild_body,
      "-- Core already marks the materials that should not turn up in generated content, which is "
      "why no exclusion list of ours is needed anywhere in this file")

check("a def Core allows nothing for falls through rather than failing",
      "if (allowed.Count == 0) { return null; }" in wild_body
      and "if (wild != null) { return wild; }" in materials,
      "-- a generation pass must never fail over a furnishing choice; it falls to the palette and "
      "then to Core's own default")'''),
]

problems = []
for old, _ in EDITS:
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:70]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(text)
print("material claims restated to the owner's specification")
