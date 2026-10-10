# -*- coding: utf-8 -*-
"""Claims for the sixth launch's three findings: the conduit blowout, the look, the walk-through."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(REPO, ".local", "register")

# ------------------------------------------------------------------ the conduit blowout
GENP = os.path.join(REG, "proof-generation-batch.py")
text = io.open(GENP, encoding="utf-8").read()
ANCHOR = 'print("")\nif failures:'

CONDUIT = '''print("")
print("THE CONDUIT BLOWOUT THAT STOPPED EVERY 300x300 COORDINATE")
print("-" * 78)

# The sixth launch: SpawnNativeConduit threw RR_Generation_ContentPlacementFailed, so
# MarkLayoutReady never ran, so SoloGroupOpening stopped at step 2 again and the Store's back door
# was never marked. An unmarked door is an ordinary steel door, which is everything the owner
# reported: *"its not blue!!! it doesnt have a light aura, and it in no way is a portal"*.
#
# The cause, measured: the grid carpeted every powered room with conduit. At 12x12 rooms that was
# ~100 cells. At depth 1 a service_passage is 60x80, so ContractedBy(1) is 4,524 cells against
# MaxNativePowerConduits = 512 -- an EIGHTFOLD blowout on the first powered room, every time.
cap = re.search(r"const\\s+int\\s+MaxNativePowerConduits\\s*=\\s*(\\d+)", genstep)

check("THE WHOLE-ROOM CONDUIT CARPET IS GONE",
      "poweredRoomCoverage" not in genstep
      and "room.Bounds.ContractedBy(1)).ToList()" not in genstep,
      "-- wiring four thousand cells to catch one lamp is the wrong shape at any size, and at "
      "80x80 it made the coordinate impossible to generate rather than merely wasteful")

check("the grid hands back what it wired, so a later pass can route from it",
      "private static HashSet<IntVec3> SpawnNativePowerNetwork(" in genstep
      and "HashSet<IntVec3> wiredCells = SpawnNativePowerNetwork(" in genstep,
      "-- the carpet existed because the lamps the dressing adds did not exist yet; the answer is "
      "to wire them after they do, which needs the grid that was built")

stray_at = genstep.find("private static void ConnectStrayConsumers(")
stray_body = genstep[stray_at:genstep.find(chr(10) + "        }" + chr(10), stray_at)] \\
    if stray_at >= 0 else ""
populate_at = genstep.find("RoomContentBuilder.Populate(map, coordinate, entryCell")
call_at = genstep.find("ConnectStrayConsumers(map, voidFloor, conduitDef, wiredCells, generator);")
check("ANYTHING THAT DRAWS POWER IS WIRED AFTER THE DRESSING PLACES IT",
      stray_at >= 0 and populate_at >= 0 and call_at >= 0 and populate_at < call_at,
      "-- the lamps and benches the archetype dressing places only exist after Populate. Wiring "
      "before that is guessing where they will land. Populate at %d, pass at %d"
      % (populate_at, call_at))

check("it finds them the same way the validator finds them",
      "TryGetComp<CompPowerTrader>() != null" in stray_body
      and "map.listerThings.AllThings" in stray_body,
      "-- the thing that REPORTS a stray consumer and the thing that FIXES one now agree by "
      "construction rather than by two people remembering the same rule")

check("THE STRAY PASS CAN NEVER COST THE COORDINATE",
      stray_at >= 0 and "throw" not in stray_body
      and "private static void TrySpawnNativeConduit(" in genstep,
      "-- a lamp that cannot be reached is a dark corner. Losing the whole place over a conduit "
      "is the defect this checkpoint exists to fix, and the throwing form is kept only for the "
      "generator's own footprint where a failure really is a generator fault")

check("and it still respects the conduit cap",
      "wiredCells.Count >= MaxNativePowerConduits" in stray_body
      and cap is not None,
      "-- bounded, so a pathological map cannot carpet itself. Cap is %s"
      % (cap.group(1) if cap else "MISSING"))

# The arithmetic that caused it, so the shape cannot come back unnoticed.
MAPW, MARGIN, GAP, MINS = 300, 14, 10, 3
_spacing = (MAPW - MARGIN * 2) // MINS
_span = _spacing - GAP
if _span % 2:
    _span -= 1
_passage = (_span * 3 // 4) - ((_span * 3 // 4) % 2)
_carpet = (_passage - 2) * (_span - 2)
check("the arithmetic that caused it is recorded, not just the fix",
      cap is not None and _carpet > int(cap.group(1)),
      "-- one powered room at depth 1 is %d cells contracted by one, against a cap of %s. Any "
      "future per-room area pass has the same problem and this is the number that proves it"
      % (_carpet, cap.group(1) if cap else "MISSING"))

''' + ANCHOR

if text.count(ANCHOR) != 1:
    print("GEN ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(GENP, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, CONDUIT, 1))
print("conduit claims added to proof-generation-batch")


# ------------------------------------------------------------------ the look and the walk-through
LINKS = os.path.join(REG, "proof-gate-links.py")
links = io.open(LINKS, encoding="utf-8").read()
LANCHOR = 'print("")\nif failures:'

GATE = '''print("")
print("A GATE LOOKS LIKE A GATE, AND IS WALKED THROUGH LIKE ONE")
print("-" * 78)

# Owner, 2026-09-30, verbatim: *"its not blue!!! it doesnt have a light aura, and it in no way is
# a portal to the back rooms.. wtf!!! ... ive said stargate mod repeaditly is how the gates work
# but with normal does"*.
gatecomp = _read(_SRC, "Portals", "CompRimroomsEmergence.cs")
doorpatch = io.open(_os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Patches",
                                  "RR_NativeGateProviders.xml"),
                    encoding="utf-8-sig", errors="replace").read()

check("A LIVE GATE IS BLUE AND CASTS LIGHT",
      "CompProperties_Glower" in doorpatch and "CompProperties_Colorable" in doorpatch
      and "LiveGlowColor" in gatecomp and "LiveGlowRadius" in gatecomp
      and "colorable.SetColor(LiveGlowColor.ToColor)" in gatecomp,
      "-- both comps are Core and both are settable per instance, so this needs no new texture "
      "and no new def")

check("NO OTHER DOOR IN THE GAME IS AFFECTED, AND CORE'S OWN RULE IS WHAT GUARANTEES IT",
      "ThingComp, IThingGlower" in gatecomp
      and "public bool ShouldBeLitNow() { return IsLiveGate; }" in gatecomp,
      "-- CompGlower.ShouldBeLitNow walks every comp on its parent and asks any that implements "
      "IThingGlower; one false keeps the glower dark and unregistered. So every ordinary door in "
      "every colony, and every door any other mod ships, carries an inert glower refused by Core "
      "rather than by hoping a radius of zero is enough")

check("the glower default in the patch is dark",
      "<glowRadius>0</glowRadius>" in doorpatch,
      "-- belt and braces beside the IThingGlower veto, so even a Core change to that interface "
      "leaves ordinary doors unlit")

live_at = gatecomp.find("public bool IsLiveGate")
live_body = gatecomp[live_at:gatecomp.find(chr(10) + "        }" + chr(10), live_at)] \\
    if live_at >= 0 else ""
check("ONLY A GATE WITH A REAL WAY THROUGH LIGHTS UP",
      live_at >= 0 and "IsDesignated" in live_body and "network.Connections" in live_body,
      "-- a door the player marked but which nothing leads through yet is a plan, not a gate, and "
      "lighting it blue would promise a way through that does not exist")

check("the colour and radius are per-instance overrides, never shared props",
      "glower.GlowRadius =" in gatecomp and "glower.GlowColor =" in gatecomp
      and "Props.glowRadius" not in gatecomp,
      "-- editing a shared CompProperties would recolour every door in the game at once")

check("a gate that stops being live stops glowing",
      "glower.GlowRadius = live ? LiveGlowRadius : 0f;" in gatecomp
      and "else if (colorable.Active) { colorable.Disable(); }" in gatecomp,
      "-- a blue door that no longer leads anywhere is a worse lie than a plain one")

menu_at = gatecomp.find("public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)")
menu_body = gatecomp[menu_at:gatecomp.find(chr(10) + "        }" + chr(10), menu_at)] \\
    if menu_at >= 0 else ""
check("RIGHT-CLICK THE GATE WITH A COLONIST SELECTED AND WALK THROUGH IT",
      menu_at >= 0
      and "PortalTravelService.OrderCrossing(selPawn, subject)" in menu_body
      and "RR_DoorCross_Enter" in menu_body,
      "-- the order and the job already walked a pawn to the door and crossed them to the other "
      "map. What was missing was the place a player looks: it was only reachable by selecting "
      "pawns, selecting the door, clicking a gizmo and choosing from a float menu, which is a "
      "dispatch console rather than a door")

check("the gate decides nothing it is not allowed to decide",
      menu_at >= 0
      and "RimroomsPortalCrossingService.EligibilityFailureKey(selPawn)" in menu_body
      and "PortalTraversalPolicy" not in menu_body,
      "-- invariant 1: PortalTraversalPolicy is the only traversal chokepoint, and a second "
      "opinion in a menu is exactly how a chokepoint stops being one")

check("a pawn who cannot cross is told why rather than omitted",
      menu_at >= 0 and "RR_DoorCross_EnterRefused" in menu_body,
      "-- a name missing from a menu says nothing; *drafted* or *in transit* is something the "
      "player needs told")

check("both menu strings are written",
      "<RR_DoorCross_Enter>" in portal_keyed and "<RR_DoorCross_EnterRefused>" in portal_keyed,
      "-- an option the player cannot read is a silent failure")

''' + LANCHOR

if links.count(LANCHOR) != 1:
    print("LINKS ANCHOR PROBLEM: %d" % links.count(LANCHOR))
    raise SystemExit(1)
io.open(LINKS, "w", encoding="utf-8", newline="").write(links.replace(LANCHOR, GATE, 1))
print("gate claims added to proof-gate-links")
