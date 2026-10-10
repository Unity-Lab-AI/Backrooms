# -*- coding: utf-8 -*-
"""Scope the corridor claims to the corridor methods, and pin the branches not the constants.

Two separate instances of the same two traps, found by the plants within minutes of each other:

* **Claim scoping, thirty-eighth instance.** `PlaceWall(map, cell, wallDef, wallStuff);` occurs
  **twice** in the generator -- once for a room's wall ring and once for a corridor wall. A plant
  that reverted the corridor one to hardcoded steel left the room one standing, and the claim read
  the file and was satisfied. The claim now reads `PlaceCorridorWall`'s own body.

* **The machinery is not the behaviour, fifth instance this run.** The lamp and fixture claims
  asserted that `CorridorLampSpacing` and `CorridorFixtureSpacing` *exist*. A plant that replaced
  `if (lightDef != null && index % CorridorLampSpacing == 0)` with `if (false)` left both
  constants defined, so both claims passed while no hallway was ever lit again. The claims now pin
  the conditions.

And the live-gate claim in `proof-gate-links.py` asserted that the frontier branch exists, which
a plant turning `if (!IsLiveGate)` into `if (false)` leaves untouched -- the branch is still
written, it is simply never reached. It pins the test as well now.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")
LINKS = os.path.join(REPO, ".local", "register", "proof-gate-links.py")

WALL_OLD = u'''check("A CORRIDOR IS FLOORED AND WALLED LIKE THE ROOMS IT JOINS",
      "private static void PaintCorridorCell(" in genstep
      and "BackroomsPalette.SetFloor(map, cell, terrain, look.floorColor);" in genstep
      and "private static void PlaceCorridorWall(" in genstep
      and "PlaceWall(map, cell, wallDef, wallStuff);" in genstep
      and "wall.TryGetComp<CompColorable>()?.SetColor(look.wallColor);" in genstep
      and "PlaceWall(map, new IntVec3(x, 0, centerZ - halfWidth), ThingDefOf.Wall, ThingDefOf.Steel)"
      not in genstep,'''

WALL_NEW = u'''corridor_wall_body = body_of(genstep,
      "private static void PlaceCorridorWall(Map map, IntVec3 cell, ThingDef wallDef,")
corridor_paint_body = body_of(genstep,
      "private static void PaintCorridorCell(Map map, IntVec3 cell, BackroomsPalette.Look look,")
corridor_dress_body = body_of(genstep, "private static void DressCorridors(")

# **SCOPED TO THE CORRIDOR'S OWN METHOD.** `PlaceWall(map, cell, wallDef, wallStuff);` occurs
# TWICE in this file -- once for a room's wall ring, once for a corridor wall -- so a plant that
# reverted the corridor one to hardcoded steel left the room one standing and a whole-file claim
# was satisfied by it. Thirty-eighth instance of the scoping trap.
check("A CORRIDOR IS FLOORED AND WALLED LIKE THE ROOMS IT JOINS",
      corridor_wall_body is not None and corridor_paint_body is not None
      and "BackroomsPalette.SetFloor(map, cell, terrain, look.floorColor);" in corridor_paint_body
      and "look.accent != null && along % 4 == 0 ? look.accent : look.floor" in corridor_paint_body
      and "PlaceWall(map, cell, wallDef, wallStuff);" in corridor_wall_body
      and "wall.TryGetComp<CompColorable>()?.SetColor(look.wallColor);" in corridor_wall_body
      and "ThingDefOf.Steel" not in corridor_wall_body
      and "PlaceWall(map, new IntVec3(x, 0, centerZ - halfWidth), ThingDefOf.Wall, ThingDefOf.Steel)"
      not in genstep,'''

LAMP_OLD = u'''check("and the hallways are lit and furnished, against their walls only",
      "private static void DressCorridors(" in genstep
      and "DressCorridors(map, coordinate, corridorSides, lightDef, placedLights," in genstep
      and "if (offset != 0 && (offset == halfWidth - 1 || offset == 1 - halfWidth))" in genstep
      and "CorridorLampSpacing" in genstep and "CorridorFixtureSpacing" in genstep,'''

LAMP_NEW = u'''# **THE BRANCHES, not the constants.** The first draft asserted that `CorridorLampSpacing` and
# `CorridorFixtureSpacing` exist. A plant replacing `if (lightDef != null && index %
# CorridorLampSpacing == 0)` with `if (false)` left both constants defined and both claims
# passing, while no hallway was ever lit again. Fifth instance this run of the same gap.
check("and the hallways are lit and furnished, against their walls only",
      corridor_dress_body is not None
      and "DressCorridors(map, coordinate, corridorSides, lightDef, placedLights," in genstep
      and "if (offset != 0 && (offset == halfWidth - 1 || offset == 1 - halfWidth))" in genstep
      and "if (lightDef != null && index % CorridorLampSpacing == 0)" in corridor_dress_body
      and "if (fixtures.Count == 0 || index % CorridorFixtureSpacing != 0) { continue; }"
      in corridor_dress_body
      and "placedLights.Add(lamp);" in corridor_dress_body,'''

LINKS_OLD = u'''      and "foreach (FloatMenuOption option in FrontierOptions(selPawn)) { yield return option; }"
      in menu_body'''

LINKS_NEW = u'''      # The TEST as well as the branch. A plant turning `if (!IsLiveGate)` into `if (false)`
      # leaves the frontier branch written and simply never reaches it -- the branch is the
      # machinery, the test is the behaviour.
      and "if (!IsLiveGate)" in menu_body
      and "foreach (FloatMenuOption option in FrontierOptions(selPawn)) { yield return option; }"
      in menu_body'''

for path, edits in [(PROOF, [(WALL_OLD, WALL_NEW), (LAMP_OLD, LAMP_NEW)]),
                    (LINKS, [(LINKS_OLD, LINKS_NEW)])]:
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
    print("scoped the claims in %s" % os.path.basename(path))
