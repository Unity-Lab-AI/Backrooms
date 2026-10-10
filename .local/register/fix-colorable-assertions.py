# -*- coding: utf-8 -*-
"""The proof and the plant both asserted the broken string, so they CONFIRMED the bug.

This is the sharpest thing in the whole checkpoint and it should be said plainly.

`proof-gate-links.py` asserted, as evidence that a gate is blue:

    '<li Class="CompProperties_Colorable" />' in doorpatch

That string is the defect. **The proof was not merely blind to the fault, it required the fault
to be present** -- and `plant-gate-links-carry.py` planted a mangled version of the same string
and watched the proof fail, which is a plant proving that a broken line is load-bearing. Thirteen
checkers and forty-one proofs agreed the gate work was sound, and one of them was holding the
bug in place.

THE RULE THIS YIELDS, and it is new: **asserting that our XML contains a string proves only that
we wrote it, never that the game can use it.** The string must additionally be resolvable, and
that is what `check-package-integrity.py` now does for every `Class` and `compClass` in the
package, and what `proof-class-resolution.py` demands the OUTPUT of.

Both assertions are retargeted at the correct declaration. They are not loosened: the plant still
renames the comp class and the proof still fails when it does.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-gate-links.py")
PLANT = os.path.join(REPO, ".local", "register", "plant-gate-links-carry.py")

PROOF_OLD = u'''# The EXACT tags. `CompProperties_Glower` is a prefix of `CompProperties_GlowerUnused`, so a
# plant that renamed the class left a presence test satisfied -- twice over, once per comp. And the
# colour assertion reads the CONDITION, because `SetColor` survives being wrapped in `if (false)`.
check("A LIVE GATE IS BLUE AND CASTS LIGHT",
      '<li Class="CompProperties_Glower">' in doorpatch
      and '<li Class="CompProperties_Colorable" />' in doorpatch
      and "LiveGlowColor" in gatecomp and "LiveGlowRadius" in gatecomp
      and "if (live) { colorable.SetColor(LiveGlowColor.ToColor); }" in gatecomp,
      "-- both comps are Core and both are settable per instance, so this needs no new texture "
      "and no new def")'''

PROOF_NEW = u'''# The EXACT tags. `CompProperties_Glower` is a prefix of `CompProperties_GlowerUnused`, so a
# plant that renamed the class left a presence test satisfied -- twice over, once per comp. And the
# colour assertion reads the CONDITION, because `SetColor` survives being wrapped in `if (false)`.
#
# AND THE COLOURABLE HALF OF THIS CLAIM USED TO ASSERT THE BUG. It required
# `<li Class="CompProperties_Colorable" />`, a type that does not exist in RimWorld -- so this
# proof did not merely miss the defect that cost the seventh launch, **it held it in place**, and
# the matching plant watched the proof fail when the broken string was mangled. `CompColorable`
# is declared with a plain `CompProperties` carrying a `compClass`, as Core does it for textiles,
# apparel and the Ideology floor coverings.
#
# THE RULE: asserting our XML contains a string proves we wrote it, never that the game can use
# it. Resolvability is checked by `check-package-integrity.py` for every Class and compClass in
# the package, and demanded as an OUTPUT by `proof-class-resolution.py`.
check("A LIVE GATE IS BLUE AND CASTS LIGHT",
      '<li Class="CompProperties_Glower">' in doorpatch
      and "<compClass>CompColorable</compClass>" in doorpatch
      and 'Class="CompProperties_Colorable"' not in doorpatch
      and "LiveGlowColor" in gatecomp and "LiveGlowRadius" in gatecomp
      and "if (live) { colorable.SetColor(LiveGlowColor.ToColor); }" in gatecomp,
      "-- both comps are Core and both are settable per instance, so this needs no new texture "
      "and no new def. The colourable one must be spelled the way Core spells it: there is no "
      "CompProperties_Colorable type, and naming it discarded the whole Door def")'''

PLANT_OLD = u'''    ("the colourable comp is never added to the door", DOORPATCH,
     '<li Class="CompProperties_Colorable" />', '<li Class="CompProperties_ColorableUnused" />'),'''

PLANT_NEW = u'''    ("the colourable comp is never added to the door", DOORPATCH,
     "<compClass>CompColorable</compClass>", "<compClass>CompColorableUnused</compClass>"),

    # THE DEFECT THAT COST THE SEVENTH LAUNCH, PLANTED WHERE IT WAS BORN. This plant used to
    # mangle `Class="CompProperties_Colorable"` -- a type that does not exist -- so it proved a
    # broken line was load-bearing. Now it restores that line and requires the proof to refuse
    # it, which is the opposite verdict on the same string.
    ("THE COLOURABLE COMP GOES BACK TO THE CLASS THAT DOES NOT EXIST", DOORPATCH,
     "          <li>\\n            <compClass>CompColorable</compClass>\\n          </li>",
     '          <li Class="CompProperties_Colorable" />'),'''

for path, old, new in ((PROOF, PROOF_OLD, PROOF_NEW), (PLANT, PLANT_OLD, PLANT_NEW)):
    text = io.open(path, encoding="utf-8").read()
    if text.count(old) != 1:
        print("ANCHOR PROBLEM in %s: %d" % (os.path.basename(path), text.count(old)))
        raise SystemExit(1)
    io.open(path, "w", encoding="utf-8", newline="").write(text.replace(old, new, 1))
    print("retargeted %s" % os.path.basename(path))
