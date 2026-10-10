# -*- coding: utf-8 -*-
"""Restate the palette-size claim and add the wild-materials claims."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

text = io.open(PROOF, encoding="utf-8").read()

OLD = '''check("the palette is small enough to give a coordinate a character",
      "PaletteSize = 3" in materials)'''

NEW = '''# **RESTATED 0.12.52-dev, and the claim was right to fail.** It asserted `PaletteSize = 3`, which
# encoded the flat constant the owner asked to remove: *"with the wild variatiosn of material
# typeds ... found everywher deeper in"*. What is worth protecting is not the number 3 — it is that
# the palette is **bounded and small**, because a place fitted out in a dozen materials has no
# character, AND that it **grows inward**, because that is the direction.
shallow = re.search(r"const\\s+int\\s+ShallowPaletteSize\\s*=\\s*(\\d+)", materials)
deep = re.search(r"const\\s+int\\s+DeepPaletteSize\\s*=\\s*(\\d+)", materials)
check("THE PALETTE GROWS WITH DEPTH INSTEAD OF BEING A CONSTANT",
      shallow is not None and deep is not None
      and int(shallow.group(1)) < int(deep.group(1))
      and "internal static int PaletteSizeFor(int depth)" in materials
      and "PaletteSizeFor(coordinate == null ? 1 : coordinate.Depth)" in materials,
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
      'coordinate.Id ?? "") + ":" + coordinate.Depth' in materials,
      "-- the id alone was enough while the palette was one size everywhere. It is not now, and a "
      "cache that ignored depth would hand a deep coordinate a shallow palette for the rest of "
      "the session")

check("THE PALETTE REACHES THE DEPTH-SCALED DRESSING, NOT ONLY THE FAMILY FIXTURES",
      "CoordinateMaterials.StuffFor(definition, coordinate));" in content
      and content.count("GenStuff.DefaultStuffFor") == 0,
      "-- TryPlace places the archetype dressing, which is the benches, equipment and loot the "
      "owner means by *\\"found everywher deeper in\\"*, and it was taking Core's default material "
      "while the family fixtures a few lines below took the coordinate's palette. The content "
      "that was supposed to vary was the one content that could not")

check("WALLS ARE NO LONGER ONE OF TWO NAMED MATERIALS",
      "CoordinateMaterials.StuffFor(wallDef, coordinate)" in genstep
      and "coordinate.Depth <= 1 ? bandWallStuff" in genstep,
      "-- BackroomsPalette names exactly two wall materials across five bands, WoodLog or Steel, "
      "which is a hard-coded pair where every other material in the place is drawn from whatever "
      "the profile offers")

check("and the surface band keeps its wood walls",
      "ThingDef bandWallStuff = BackroomsPalette.For(coordinate.Depth, coordinate.Seed).wallStuff"
      in genstep
      and "?? bandWallStuff);" in genstep,
      "-- depth 1 is the canonical look and the band's own choice is still the fallback "
      "everywhere, so a coordinate with no usable palette material for a wall is unchanged")'''

if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)

io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("palette claims restated and widened")
