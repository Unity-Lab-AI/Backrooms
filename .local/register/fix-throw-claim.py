# -*- coding: utf-8 -*-
"""Assert the guard does not THROW, and retarget one stale plant anchor.

The claim tested that `StartForMap` exists and that callers null-check it -- neither of which
notices a `throw` planted *inside* the guard. And that is the whole point of the guard: it lives
in Core's `Base_Player` now, so a throw breaks every player map a game ever generates.

The stale anchor is my own: rewriting `RequireStart` into `StartForMap` removed the line the
exact-size plant was written against.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-startplacement.py")
PLANT = os.path.join(REPO, ".local", "register", "plant-startplacement.py")

proof = io.open(PROOF, encoding="utf-8").read()

OLD = ('check("THE GEN STEPS RETURN QUIETLY WHEN IT IS NOT THE COMPANY START",\n'
       '      "internal static RimroomsStartDef StartForMap(Map map)" in gen\n'
       '      and gen.count("if (start == null) { return; }") >= 2\n'
       '      and "RequireStart" not in gen,')

NEW = ('# The guard\'s body is read on its own, because a `throw` planted INSIDE it changes none of\n'
       '# the surrounding facts -- the method still exists and the callers still null-check it.\n'
       'guard_body = ""\n'
       'guard_at = gen.find("internal static RimroomsStartDef StartForMap(Map map)")\n'
       'if guard_at >= 0:\n'
       '    guard_body = gen[guard_at:gen.find("\\n        }", guard_at)]\n'
       'check("THE GEN STEPS RETURN QUIETLY WHEN IT IS NOT THE COMPANY START",\n'
       '      guard_at >= 0\n'
       '      and "throw" not in guard_body\n'
       '      and guard_body.count("return null;") >= 4\n'
       '      and gen.count("if (start == null) { return; }") >= 2\n'
       '      and "RequireStart" not in gen,')

if OLD not in proof:
    print("PROOF ANCHOR PROBLEM: %d" % proof.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(proof.replace(OLD, NEW, 1))
print("claim now reads the guard's own body for a throw")

plant = io.open(PLANT, encoding="utf-8").read()
OLD_PLANT = ('    ("the generator goes back to demanding an exact map size", GEN,\n'
             '     "!HeadquartersLayout.Fits(part.startDef, map.Size) ||",\n'
             '     "map.Size.x != part.startDef.mapSize || map.Size.z != part.startDef.mapSize ||", PROOF),')
NEW_PLANT = ('    # Retargeted: rewriting RequireStart into StartForMap removed the line this was\n'
             '    # written against. The guard is a sequence of early returns now.\n'
             '    ("the generator goes back to demanding an exact map size", GEN,\n'
             '     "if (!HeadquartersLayout.Fits(part.startDef, map.Size)) { return null; }",\n'
             '     "if (map.Size.x != part.startDef.mapSize) { return null; }", PROOF),')
if OLD_PLANT not in plant:
    print("PLANT ANCHOR PROBLEM: %d" % plant.count(OLD_PLANT))
    raise SystemExit(1)
io.open(PLANT, "w", encoding="utf-8", newline="").write(plant.replace(OLD_PLANT, NEW_PLANT, 1))
print("exact-size plant retargeted")
