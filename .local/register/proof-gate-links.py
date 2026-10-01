# -*- coding: utf-8 -*-
"""Assert the premises the gate equipment-link design rests on.

Every claim below is one the design would be wrong without, and each is checked against the
INSTALLED game data rather than against memory. The first assertion is the one that already
bit: the owner said "multianalysers", and `Multianalyzer` is a ResearchProjectDef. The
building is `MultiAnalyzer`.

Run from the repository root.
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"
ROLES = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Defs",
                     "RimroomsGateEquipmentDefs", "RR_GateEquipment.xml")

failures = []


def check(claim, condition, detail=""):
    if condition:
        print("  OK   %s" % claim)
    else:
        print("  FAIL %s %s" % (claim, detail))
        failures.append(claim)


# --------------------------------------------------------------------------- game ThingDefs
thing_defs = {}
for path in glob.glob(os.path.join(GAME, "**", "ThingDefs*", "*.xml"), recursive=True):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        continue
    for node in root:
        name = node.findtext("defName")
        if node.tag == "ThingDef" and name:
            thing_defs[name.strip()] = (node, os.path.relpath(path, GAME))

print("installed ThingDefs indexed: %d" % len(thing_defs))
check("the game data was found and parsed", len(thing_defs) > 1000,
      "(only %d defs; is the install path right?)" % len(thing_defs))

# --------------------------------------------------------------------------- our roles
root = ET.parse(ROLES).getroot()
roles = []
for node in root:
    roles.append({
        "defName": node.findtext("defName"),
        "label": node.findtext("label"),
        "maxLinked": int(node.findtext("maxLinked") or "4"),
        "order": int(node.findtext("displayOrder") or "0"),
        "things": [li.text.strip() for li in node.find("thingDefNames")],
    })

print("")
print("roles declared: %d" % len(roles))
check("at least one role is declared", len(roles) > 0)

# 1. Every def name a role accepts must actually exist. THE one that already bit.
for role in roles:
    for name in role["things"]:
        check("%s accepts %s, which exists in the game" % (role["defName"], name),
              name in thing_defs,
              "-- not a ThingDef in the installed data")

# 2. No def name may appear in two roles: RoleFor() returns the first match in display order,
#    so an overlap would make a thing's role depend on display order rather than on what it is.
seen = {}
overlap = []
for role in roles:
    for name in role["things"]:
        if name in seen:
            overlap.append("%s is in both %s and %s" % (name, seen[name], role["defName"]))
        seen[name] = role["defName"]
check("no def name appears in two roles", not overlap, "-- " + "; ".join(overlap))

# 3. Display order must be unique, or the picker order is arbitrary between ties.
orders = [role["order"] for role in roles]
check("display orders are distinct", len(set(orders)) == len(orders))

# 4. maxLinked must be above one everywhere. The direction was "some shelves and multiples";
#    a role capped at one is the thing being fixed, not the fix.
for role in roles:
    check("%s allows multiples (maxLinked=%d)" % (role["defName"], role["maxLinked"]),
          role["maxLinked"] > 1)


def comp_classes(name):
    node = thing_defs[name][0]
    found = []
    comps = node.find("comps")
    if comps is None:
        return found
    for li in comps:
        found.append(li.get("Class") or "")
    return found


# 5. The power rule must actually bite on something, and the exemption must be necessary.
#    If every candidate were powered, the exemption would be dead code; if none were, the rule
#    would be. Both halves are asserted so neither can quietly become untrue.
powered = [n for n in seen if any("CompProperties_Power" in c for c in comp_classes(n))]
unpowered = [n for n in seen if n not in powered]
print("")
print("powered candidates:   %s" % ", ".join(sorted(powered)))
print("unpowered candidates: %s" % ", ".join(sorted(unpowered)))
check("at least one candidate is powered, so the same-power-net rule bites", len(powered) > 0)
check("at least one candidate is unpowered, so the exemption is necessary", len(unpowered) > 0)

# 6. Shelf specifically must be unpowered. The archive role is the queued evidence-case
#    replacement, and requiring a power net of a shelf would make it permanently unfillable.
check("Shelf has no power component", "Shelf" in unpowered)

# 7. The premise of not reusing Core's facility comps: its defaults really are 8 cells and
#    line-of-sight required. If Core ever changed these, the argument in the source comment
#    would stop being true and somebody should find out from here rather than from a player.
assembly = os.path.join(os.path.dirname(GAME), "RimWorldWin64_Data", "Managed", "Assembly-CSharp.dll")
ilspy = os.path.join(REPO, ".local", "tools", "ilspycmd.exe")
import subprocess
out = subprocess.check_output([ilspy, "-t", "RimWorld.CompProperties_Facility", assembly],
                              stderr=subprocess.STDOUT).decode("utf-8", "replace")
check("Core CompProperties_Facility still defaults to maxDistance 8",
      re.search(r"public float maxDistance = 8f;", out) is not None)
check("Core CompProperties_Facility still defaults to requiresLOS true",
      re.search(r"public bool requiresLOS = true;", out) is not None)

# 8. The candidates that carry Core's own facility comp keep it. Our link is a parallel
#    relationship, and silently removing theirs would change vanilla research linking.
core_facility = [n for n in seen if any("CompProperties_Facility" in c for c in comp_classes(n))]
print("")
print("candidates that also carry Core's facility comp: %s" % ", ".join(sorted(core_facility)))
check("MultiAnalyzer still carries Core's own facility comp", "MultiAnalyzer" in core_facility)
check("ToolCabinet still carries Core's own facility comp", "ToolCabinet" in core_facility)

print("")
print("A NATURAL GATE IS AN OBJECT YOU OWN: BREAK IT AND LOSE IT, CARRY IT AND KEEP IT")
print("-" * 78)

# Owner direction, 2026-09-30, verbatim: *"so we need a way to deconstruct natural gates too i
# think"*, *"and then u lose them forever but maybe allow minify move"*, and *"they are just doors
# too right that dont need the mechine gate systems"*.
#
# The third was confirmed by live measurement rather than inference: the natural gate in the
# owner's running game was a plain RimWorld.Building_Door in steel, already offering Deconstruct,
# Uninstall, Reinstall and the emergence gizmo, with no power, console, calibration or assembly.
import os as _os
_SRC = _os.path.join(REPO, "src", "RimroomsAsyncIndustries")


def _read(*parts):
    return io.open(_os.path.join(*parts), encoding="utf-8", errors="replace").read()


records = _read(_SRC, "Portals", "PortalConnectionRecord.cs")
network = _read(_SRC, "Portals", "RimroomsPortalNetwork.cs")
crossing = _read(_SRC, "Portals", "PortalCrossingService.cs")
comp = _read(_SRC, "Portals", "CompRimroomsEmergence.cs")
warning = _read(_SRC, "Portals", "PortalDoorWarning.cs")
portal_keyed = io.open(_os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6",
                                     "Languages", "English", "Keyed", "RR_Portals.xml"),
                       encoding="utf-8-sig", errors="replace").read()

check("A DESTROYED GATE STILL ENDS ITS ROUTE, WHICH IS WHAT THE OWNER ASKED FOR",
      "ValidDoor(endpoint.Anchor, endpoint.ApproachCell)" in network
      and "!anchor.Destroyed" in network,
      "-- *\"and then u lose them forever\"*. EndpointPresent refuses an edge whose anchor is "
      "destroyed, so the route is gone the moment the door is. That already held; nothing had to "
      "be added for it")

check("and the player is warned before they do it",
      "RR_Portals_RemoveWayInConfirm" in warning and "destructive: breaking" in warning,
      "-- informed consent rather than prohibition, which is what the owner asked for on "
      "2026-09-29 and this mod cannot honestly do otherwise: Core decides destructibility at the "
      "def level")

follow_at = records.find("internal bool TryFollowMovedAnchor(Thing thing, IntVec3 approach)")
follow_body = records[follow_at:records.find(chr(10) + "        }", follow_at)] \
    if follow_at >= 0 else ""

check("A CARRIED GATE TAKES ITS ROUTE WITH IT",
      follow_at >= 0
      and "public int NotifyAnchorInstalled(Thing anchor)" in network
      and "network.NotifyAnchorInstalled(parent)" in comp,
      "-- *\"but maybe allow minify move\"*. Before this, uninstalling lost the route exactly "
      "as destroying did, because EndpointPresent also requires Anchor.Position == AnchorCell")

check("IT ONLY EVER FOLLOWS THE SAME DOOR, NEVER A LOOKALIKE",
      follow_at >= 0 and "anchor != thing) { return false; }" in follow_body,
      "-- the snapshot this replaces existed so a moved door could not silently redirect a "
      "route. A different door rebuilt in the same cell is not this endpoint and never becomes "
      "one, so a route cannot be captured by building something that looks like it")

check("a move is refused unless the door is on ground the branch owns",
      "if (!OwnsMap(Campaign, anchor.Map)) { return 0; }" in network,
      "-- the same test registration had to pass")

# Scoped to the method's own body: `!receipt.IsTerminal` appears elsewhere in this file, so a
# whole-file claim passed a plant that deleted it from precisely this test.
flight_at = crossing.find("public bool IsConnectionInFlight(string connectionId)")
flight_body = crossing[flight_at:crossing.find(chr(10) + "        }", flight_at)]     if flight_at >= 0 else ""
check("NOBODY CAN BE MID-CROSSING WHEN A ROUTE MOVES",
      flight_at >= 0
      and "!receipt.IsTerminal" in flight_body
      and "receipt.ConnectionId == connectionId" in flight_body
      and "crossings.IsConnectionInFlight(edge.Id)) { continue; }" in network,
      "-- invariant 55: a receipt that is not terminal is a pawn part-way through. The route is "
      "left broken and visible rather than re-pointed under a traveller, which is the safer of "
      "the two")

check("loading a save is not a move",
      "if (respawningAfterLoad || parent == null || Current.Game == null) { return; }" in comp,
      "-- respawningAfterLoad means the door is being restored where it already was and the "
      "saved route already points there; re-anchoring then would turn every load into a move")

check("uninstalling and deconstructing no longer say the same thing",
      "RR_Portals_MoveWayInConfirm" in warning
      and "<RR_Portals_MoveWayInConfirm>" in portal_keyed
      and "<RR_Portals_WayThroughMoved>" in portal_keyed
      and "bool carrying = map.designationManager.DesignationOn(anchor, DesignationDefOf.Uninstall) != null;"
      in warning,
      "-- telling a player the same thing for both would be telling them something false about "
      "one of them, and the red destructive confirmation is reserved for the one that is")

print("")
print("A GATE LOOKS LIKE A GATE, AND IS WALKED THROUGH LIKE ONE")
print("-" * 78)

# Owner, 2026-09-30, verbatim: *"its not blue!!! it doesnt have a light aura, and it in no way is
# a portal to the back rooms.. wtf!!! ... ive said stargate mod repeaditly is how the gates work
# but with normal does"*.
gatecomp = _read(_SRC, "Portals", "CompRimroomsEmergence.cs")
doorpatch = io.open(_os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", "Patches",
                                  "RR_NativeGateProviders.xml"),
                    encoding="utf-8-sig", errors="replace").read()

# The EXACT tags. `CompProperties_Glower` is a prefix of `CompProperties_GlowerUnused`, so a
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
      # **THE TINT MUST BE OPAQUE, AND IT MUST NOT COME FROM THE GLOW CONSTANT.** This claim used
      # to require `SetColor(LiveGlowColor.ToColor)` -- which is the line that made the door
      # invisible, because `ColorInt.ToColor` divides alpha by 255 and the glow constant is
      # `a: 0`. The second time this file has held a bug in place by naming it exactly. Assert
      # the property, not the line.
      and "if (live) { colorable.SetColor(LiveTintColor); }" in gatecomp
      and "LiveGlowColor.ToColor" not in gatecomp
      and "220f / 255f, 1f)" in gatecomp,
      "-- both comps are Core and both are settable per instance, so this needs no new texture "
      "and no new def. The colourable one must be spelled the way Core spells it: there is no "
      "CompProperties_Colorable type, and naming it discarded the whole Door def")

check("NO OTHER DOOR IN THE GAME IS AFFECTED, AND CORE'S OWN RULE IS WHAT GUARANTEES IT",
      "ThingComp, IThingGlower" in gatecomp
      and "public bool ShouldBeLitNow() { return IsLiveGate || frontierGate; }" in gatecomp
      # **AND THE NEW CONDITION IS CONFINED TO A COORDINATE.** Evaluate serves ordinary
      # maps under its own worldfrontier: origin, so without this a door in an ancient
      # structure on the player's OWN colony map would glow blue on install. This claim
      # refused the change that introduced it, correctly, and is widened not relaxed.
      and "parent.Map != null && parent.Map.Parent is RimroomsDestinationMapParent" in gatecomp,
      "-- CompGlower.ShouldBeLitNow walks every comp on its parent and asks any that implements "
      "IThingGlower; one false keeps the glower dark and unregistered. So every ordinary door in "
      "every colony, and every door any other mod ships, carries an inert glower refused by Core "
      "rather than by hoping a radius of zero is enough")

check("the glower default in the patch is dark",
      "<glowRadius>0</glowRadius>" in doorpatch,
      "-- belt and braces beside the IThingGlower veto, so even a Core change to that interface "
      "leaves ordinary doors unlit")

live_at = gatecomp.find("public bool IsLiveGate")
live_body = gatecomp[live_at:gatecomp.find(chr(10) + "        }" + chr(10), live_at)] \
    if live_at >= 0 else ""
check("ONLY A GATE WITH A REAL WAY THROUGH LIGHTS UP",
      live_at >= 0 and "IsDesignated" in live_body
      and "GetComponent<RimroomsPortalNetwork>()" in live_body
      and "return true;" not in live_body.split("for (int index")[0],
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
menu_body = gatecomp[menu_at:gatecomp.find(chr(10) + "        }" + chr(10), menu_at)] \
    if menu_at >= 0 else ""
check("RIGHT-CLICK THE GATE WITH A COLONIST SELECTED AND WALK THROUGH IT",
      menu_at >= 0
      and "PortalTravelService.OrderCrossing(selPawn, subject)" in menu_body
      and "RR_DoorCross_Enter" in menu_body
      # A door that is NOT a live gate is now asked whether it is an undiscovered way onward
      # before the menu gives up. **`NaturalFrontierService.Discover` had ZERO callers** -- the
      # draw, the cap, the guaranteed pair and twenty `RR_Frontier_*` strings were all written
      # for a menu that did not exist. Owner: *"i just never found any other gates with option
      # to walk through"*.
      # The TEST as well as the branch. A plant turning `if (!IsLiveGate)` into `if (false)`
      # leaves the frontier branch written and simply never reaches it -- the branch is the
      # machinery, the test is the behaviour.
      and "if (!IsLiveGate)" in menu_body
      and "foreach (FloatMenuOption option in FrontierOptions(selPawn)) { yield return option; }"
      in menu_body
      and "private IEnumerable<FloatMenuOption> FrontierOptions(Pawn selPawn)" in gatecomp
      and "NaturalFrontierService.Discover(parent)" in gatecomp,
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

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every claim the equipment-link design rests on")
