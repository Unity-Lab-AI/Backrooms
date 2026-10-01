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


def _code(text):
    """The source with its line comments removed.

    **An absence claim cannot read raw source.** `"EnsureAssemblyBill" not in console` failed
    against correct code because the comment explaining the method's removal names it. Forty-first
    instance of that trap in this project; `proof-coordinate-layout.py` has had this view since
    0.12.62-dev and `proof-generation-batch.py` strips comments outright.
    """
    kept = []
    for line in text.split(chr(10)):
        if line.lstrip().startswith("//"):
            continue
        kept.append(line)
    return chr(10).join(kept)


def _read_mod(*parts):
    return io.open(os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6", *parts),
                   encoding="utf-8-sig").read()
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
      and "public bool ShouldBeLitNow() { return IsLiveGate || recordedGate || frontierGate; }"
      in gatecomp
      # **AND A RECORDED GATE COUNTS.** IsLiveGate needs a player mark, which a door inside a
      # coordinate never has, so a discovered way onward stopped glowing the moment it started
      # working. Sixth instance this run of a path built, registered and gated off.
      and "public bool IsRecordedGate" in gatecomp
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
      and "if (!IsLiveGate && !IsRecordedGate)" in menu_body
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

frontier = _read(_SRC, "Portals", "NaturalFrontierService.cs")
guarantee = _read(_SRC, "Portals", "GuaranteedFrontiers.cs")
services = _read(_SRC, "Company", "CampaignServices.cs")

# ------------------------------------------ a gate is never a door somebody needs
# Owner: *"i found a door that was a gate, but it was where a normal door should of been (gates
# natural need to not also be used and needed as normal doors, becasue on the other side was the
# rest of the backrooms map)"*. The guarantee collected EVERY door on the coordinate and picked
# two, so a door between two rooms could become a permanently open one-way gate and take an
# ordinary route away.
check("A NATURAL GATE IS ONLY EVER A DEAD-END DOOR",
      "internal static bool LeadsNowhere(Thing door)" in frontier
      and "return open == 1;" in frontier
      and 'if (!LeadsNowhere(door)) { return "RR_Frontier_LeadsNowhere"; }' in frontier
      and "if (!NaturalFrontierService.LeadsNowhere(door)) { continue; }" in guarantee,
      "-- checked inside `Evaluate`, so the glow, the float menu and the discovery all agree, AND "
      "inside the guarantee, so the chosen pair cannot be doors the service would then refuse. "
      "`FalseOpening` already builds *\"doors to now where\"* onto rock, so **the door that should "
      "not be there is the one that leads somewhere else**")

check("and another door counts as a way through, not as rock",
      "side.Walkable(map) || side.GetEdifice(map) is Building_Door" in frontier,
      "-- two doors in a row is still a route somebody walks")

# ------------------------------- the string length that capped the Backrooms at two
# **THE BIGGEST OF THE FOUR.** A coordinate's id embeds its parent's entire id, so a discovery id
# grew about eighty characters per level: 88 for the first step inward, 168 for the second -- past
# the 128 limit, refused with `RR_Company_InvalidRequest`, *"that request is not valid for this
# branch"*. `MaximumNaturalDepth` was unreachable and *"the backrooms never ends persay"* could
# not happen.
check("GOING DEEPER IS NOT CAPPED BY A STRING LENGTH",
      "public const int MaximumDiscoveryIdLength = 128;" in services
      and "discoveryId.Length > MaximumDiscoveryIdLength" in services
      and "private static string DiscoveryIdFor(FrontierOrigin origin, Thing door)" in frontier
      # **THE CALL SITE.** A plant reverting the inline composition left the method defined
      # and this claim passing while the id grew unbounded again. Sixth instance this run.
      and "string discoveryId = DiscoveryIdFor(origin, door);" in frontier
      and 'origin.OriginId + ":" + origin.KeyPrefix +' not in frontier
      and "if (full.Length <= RimroomsCampaignComponent.MaximumDiscoveryIdLength) { return full; }"
      in frontier,
      "-- the composer reads the limit the enforcer uses. A validator and its caller carrying "
      "separate copies of one number is the defect this project has paid for three times in a week")

check("and the long form is kept whenever it fits, so saved coordinates still resolve",
      'string full = origin.OriginId + ":" + position;' in frontier
      and 'return "o" + first.ToString("x8") + second.ToString("x8") + ":" + position;' in frontier,
      "-- byte-for-byte what it always was below the limit, and an id that would be refused never "
      "existed in a save to begin with. **Two hashes, not one**: a single 31-bit FNV value shared "
      "by two parents would merge two different places into one coordinate, which is worse than "
      "any refusal")

# ----------------------------------- a way out is not a way deeper, and both work now
# A deeper find registers a portal EDGE. A way out saves a world-exit record and registers NO
# edge, because leaving for the world map is a caravan. The first draft asked for an edge in both
# cases, so a world exit recorded correctly and then reported that surveying was unavailable.
check("A WAY OUT AND A WAY DEEPER ARE BOTH WALKABLE FROM THE MENU",
      "PortalConnectionRecord edge = EdgeFor();" in gatecomp
      and "if (edge != null)" in gatecomp
      and "campaign.WorldExitFor(parent) != null" in gatecomp
      and "Show(WalkOutToWorld());" in gatecomp,
      "-- the edge for a deeper find, the caravan for a way out. Asking `EdgeFor()` for a world "
      "exit returns null BY DESIGN, and the first draft read that as a failure and said "
      "*\"surveying doors is unavailable\"*, which is neither true nor useful")

console = _read(_SRC, "Gate", "CompRimroomsGateConsole.cs")
nativebinding = _read(_SRC, "Gate", "NativeGateBinding.cs")
# Comment-free views, for the absence clauses only.
console_code = _code(console)
nativebinding_code = _code(nativebinding)
gaterecipe = _read_mod("Defs", "RecipeDefs", "RR_GateRecipes.xml")

# ----------------------------------------- the assembly is the player's decision
# Owner: *"the machining table to op[en the gate needs to be a bill currently they instantly try
# to open the gate and build it and i have no say in the mattter even tho nothing is connected or
# built yet and havent started the mission line yet"*.
#
# `BindNativeInfrastructure` ended with `EnsureAssemblyBill`, which **added an unsuspended
# `Bill_Production` to the machining table**, so commissioning a door sent crafters off with a
# hundred steel and eight components immediately. **Nothing in this battery mentioned the bill**,
# so it was never asserted and never planted against.
check("COMMISSIONING A GATE QUEUES NOBODY'S WORK",
      "public void SyncAssemblyBill()" in console
      and "EnsureAssemblyBill" not in console_code
      and "EnsureAssemblyBill" not in nativebinding_code
      and "BillStack.AddBill" not in console_code
      and "new Bill_Production(" not in console_code,
      "-- *ensure* was the whole defect. The bill is added by the player, from the machining "
      "table's own recipe list, when they are ready")

check("and it may only suspend, never un-suspend and never re-time",
      "if (Gate == null || !Gate.AssemblyComplete) { return; }" in console
      and "bill.suspended = true;" in console
      and "existing.suspended = Gate.AssemblyComplete" not in console_code
      # **COUNTED, not merely absent under an old name.** The first draft asserted the absence of
      # `existing.repeatMode`, which a plant adding `bill.repeatCount = 1` to the sync method
      # sailed straight past. Exactly TWO repeat writes exist and both are in
      # `MarkAssemblyBillComplete`, which runs after the work is finished -- where there is no
      # decision left to take. A third would be the sync method re-timing a player's bill.
      and console_code.count("repeatMode") == 1
      and console_code.count("repeatCount = ") == 1,
      "-- suspending a finished bill cannot take a decision away; it stops a repeating bill "
      "spending another hundred steel on a gate that exists. Un-suspending one would overrule a "
      "player who suspended it on purpose, and the repeat mode and count are theirs")

check("and the recipe was on the table's own list the whole time",
      "<recipeUsers><li>TableMachining</li></recipeUsers>" in gaterecipe
      and "Designate the native door, communications console, battery and machining table in"
      in gaterecipe,
      "-- **the recipe's own description is an instruction to a player who then adds the bill**, "
      "and nothing had to be built to give them the choice. The choice had been taken")

spinup = _read(_SRC, "Gate", "GateSpinUp.cs")

# ------------------------------------------------- gate control, and it cuts both ways
# Owner: *"we should have a set to gate control for these components so other things arnt
# available and can toggle between normal op and gate op depending whats wanted.."*
check("A COMPONENT DOES ITS ORDINARY JOB OR THE GATE'S, AND THE PLAYER CHOOSES",
      "public bool IsGateControl { get { return gateControl && linkedGate != null; } }" in console
      and "public void SetGateControl(bool running)" in console
      and "action = delegate { SetGateControl(!running); }" in console
      and "RR_NativeGate_GateControlLabel" in console
      and "RR_NativeGate_NormalOpLabel" in console,
      "-- DEFINED AND CALLED, and the switch is offered only on a component actually bound to a "
      "gate, because a button that can only refuse is worse than no button")

check("and it BEGINS in normal operation",
      "private bool gateControl;" in console
      and 'Scribe_Values.Look(ref gateControl, "rr_gateConsoleGateControl", false);' in console,
      "-- commissioning a door must not change how the colony works. That was the other half of "
      "the complaint this came from, where binding queued a hundred steel of assembly nobody "
      "asked for")

check("ORDINARY COMPANY FUNCTIONS ARE WITHDRAWN IN GATE CONTROL",
      "if (IsGateControl) { yield break; }" in console
      and console.index("if (IsGateControl) { yield break; }")
      < console.index("Procurement.CorporateSupplyGizmos.For(parent)"),
      "-- *\"so other things arnt available\"*. The withdrawal is BEFORE the four gizmos, not "
      "after: a console running the gate is not also taking deliveries, paying credit, raising "
      "the alarm or placing the corporation call")

check("and a machining table's other bills are suspended, by id, and resumed exactly",
      # **THE SUSPENDING, not just the recording.** A plant deleted `bill.suspended = true`
      # and left the Add line, so gate control recorded which bills it had suspended while
      # suspending none of them, and every asserted line was still there. Eighth instance this
      # session. The two are pinned together and in order, so neither can go without the other.
      (u"bill.suspended = true;" + chr(10)
       + "                    suspendedByGateControl.Add(bill.GetUniqueLoadID());") in console
      and "if (bill == null || bill.suspended) { continue; }" in console
      and 'bill.recipe.defName == "RR_AssembleMachineGate")' in console
      and "suspendedByGateControl.Contains(bill.GetUniqueLoadID())" in console
      and "suspendedByGateControl.Clear();" in console,
      "-- **recorded rather than inferred.** A bill the player had already suspended must stay "
      "suspended, and the current state cannot tell those two apart")

check("AND NORMAL OPERATION REFUSES THE GATE, so the modes are exclusive both ways",
      "&& console.IsGateControl;" in console
      and "RR_NativeGate_NotInGateControl" in spinup
      and "!spinUpStation.IsGateControl" in spinup
      and "!spinUpWorkshop.IsGateControl" in spinup,
      "-- the recipe is unavailable on a bench doing its day job, and spin-up refuses while "
      "either installation is still in normal operation. *\"depending whats wanted\"* only means "
      "something if both directions hold")

print("")
if failures:
    print("PROOF FAILED: %d claim(s)" % len(failures))
    sys.exit(1)
print("PROOF HELD: every claim the equipment-link design rests on")
