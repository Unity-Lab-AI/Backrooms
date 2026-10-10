# -*- coding: utf-8 -*-
"""Eight claims written this checkpoint were loose enough for a plant to walk through.

All eight are the one family that now outranks every other trap in this project:

  * two **prefix** traps: `CompProperties_Glower` is a prefix of `…GlowerUnused`;
  * one **duplicate**: the cap check appears twice in the stray pass and the harness replaces the
    first, so the second kept satisfying the claim;
  * five that asserted a **name** where the property is a **behaviour** -- the old constant's
    name, a call that is still present inside `if (false)`, a lookup whose later use survives an
    early `return true`, and a guard nothing asserted at all.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(REPO, ".local", "register")

# ------------------------------------------------------------------ generation
GENP = os.path.join(REG, "proof-generation-batch.py")
gen = io.open(GENP, encoding="utf-8").read()

GEDITS = [
    # 1. The carpet is a BEHAVIOUR, not two retired names. Read the grid method's own body.
    ('''check("THE WHOLE-ROOM CONDUIT CARPET IS GONE",
      "poweredRoomCoverage" not in genstep
      and "room.Bounds.ContractedBy(1)).ToList()" not in genstep,''',
     '''# Read the grid method's own BODY. The first version of this named the two retired symbols, so a
# plant that re-carpeted using different names walked straight past it. What is forbidden is the
# SHAPE -- flattening whole rects into conduit cells -- not the old variable name.
grid_at = genstep.find("private static HashSet<IntVec3> SpawnNativePowerNetwork(")
grid_body = genstep[grid_at:genstep.find(chr(10) + "        }" + chr(10), grid_at)] \\
    if grid_at >= 0 else ""
check("THE WHOLE-ROOM CONDUIT CARPET IS GONE",
      grid_at >= 0
      and "poweredRoomCoverage" not in genstep
      and "ContractedBy(1)).ToList()" not in genstep
      and "SelectMany" not in grid_body,'''),

    # 2. The stray pass must call the NON-throwing form, which is the property.
    ('''check("THE STRAY PASS CAN NEVER COST THE COORDINATE",
      stray_at >= 0 and "throw" not in stray_body
      and "private static void TrySpawnNativeConduit(" in genstep,''',
     '''check("THE STRAY PASS CAN NEVER COST THE COORDINATE",
      stray_at >= 0 and "throw" not in stray_body
      and "private static void TrySpawnNativeConduit(" in genstep
      and "TrySpawnNativeConduit(map, voidFloor, conduitDef, route[step], wiredCells);" in stray_body
      and "SpawnNativeConduit(map, voidFloor, conduitDef, route[step]" not in stray_body,'''),

    # 3. COUNT the cap checks: there are two and removing either is the fault.
    ('''check("and it still respects the conduit cap",
      "wiredCells.Count >= MaxNativePowerConduits" in stray_body
      and cap is not None,''',
     '''check("and it still respects the conduit cap",
      stray_body.count("wiredCells.Count >= MaxNativePowerConduits") >= 2
      and cap is not None,'''),
]

problems = []
for old, _ in GEDITS:
    if gen.count(old) != 1:
        problems.append("gen %d of %r" % (gen.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in GEDITS:
    gen = gen.replace(old, new, 1)
io.open(GENP, "w", encoding="utf-8", newline="").write(gen)
print("proof-generation-batch: 3 claims tightened")


# ------------------------------------------------------------------ gate links
LINKS = os.path.join(REG, "proof-gate-links.py")
links = io.open(LINKS, encoding="utf-8").read()

LEDITS = [
    # 4, 5, 6. Exact tags, not prefixes, and the colour assertion must read the CONDITION.
    ('''check("A LIVE GATE IS BLUE AND CASTS LIGHT",
      "CompProperties_Glower" in doorpatch and "CompProperties_Colorable" in doorpatch
      and "LiveGlowColor" in gatecomp and "LiveGlowRadius" in gatecomp
      and "colorable.SetColor(LiveGlowColor.ToColor)" in gatecomp,''',
     '''# The EXACT tags. `CompProperties_Glower` is a prefix of `CompProperties_GlowerUnused`, so a
# plant that renamed the class left a presence test satisfied -- twice over, once per comp. And the
# colour assertion reads the CONDITION, because `SetColor` survives being wrapped in `if (false)`.
check("A LIVE GATE IS BLUE AND CASTS LIGHT",
      '<li Class="CompProperties_Glower">' in doorpatch
      and '<li Class="CompProperties_Colorable" />' in doorpatch
      and "LiveGlowColor" in gatecomp and "LiveGlowRadius" in gatecomp
      and "if (live) { colorable.SetColor(LiveGlowColor.ToColor); }" in gatecomp,'''),

    # 7. The live test must actually ask the network, and must not bail out true.
    ('''check("ONLY A GATE WITH A REAL WAY THROUGH LIGHTS UP",
      live_at >= 0 and "IsDesignated" in live_body and "network.Connections" in live_body,''',
     '''check("ONLY A GATE WITH A REAL WAY THROUGH LIGHTS UP",
      live_at >= 0 and "IsDesignated" in live_body
      and "GetComponent<RimroomsPortalNetwork>()" in live_body
      and "return true;" not in live_body.split("for (int index")[0],'''),

    # 8. The guard nothing asserted.
    ('''check("RIGHT-CLICK THE GATE WITH A COLONIST SELECTED AND WALK THROUGH IT",
      menu_at >= 0
      and "PortalTravelService.OrderCrossing(selPawn, subject)" in menu_body
      and "RR_DoorCross_Enter" in menu_body,''',
     '''check("RIGHT-CLICK THE GATE WITH A COLONIST SELECTED AND WALK THROUGH IT",
      menu_at >= 0
      and "PortalTravelService.OrderCrossing(selPawn, subject)" in menu_body
      and "RR_DoorCross_Enter" in menu_body
      and "if (!IsLiveGate) { yield break; }" in menu_body,'''),
]

problems = []
for old, _ in LEDITS:
    if links.count(old) != 1:
        problems.append("links %d of %r" % (links.count(old), old[:60]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for old, new in LEDITS:
    links = links.replace(old, new, 1)
io.open(LINKS, "w", encoding="utf-8", newline="").write(links)
print("proof-gate-links: 3 claims tightened")
