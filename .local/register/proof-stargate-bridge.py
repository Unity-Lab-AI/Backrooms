# -*- coding: utf-8 -*-
"""The Stargate mod's own gate, on a normal door, on both ends, dialled by us.

Owner, four messages, four requirements:

    "we use the fucjkign stargate MOD but use a normal door im not telling u again"
    "and connect them together to the backrooms and the map"
    "we just use our own dialing converstion in the background"
    "we still use the stargate mod as normal but we also use it for our backrroms purposes"

and the complaint that started it:

    "i shouldnt have to click on the door right to send a pawn through it and how the fuck are
     they suppose to auto pick up materials on one side and use them on the other"

READ FROM THEIR SOURCE, which they ship in `Source/`. Every claim below is checked against the
installed Stargate mod's actual code, not against a description of it -- the same instinct as
`proof-class-resolution.py` and `proof-comp-tickers.py`: **when the truth lives in somebody
else's code, go and read it.**

REGISTER, AND THE CORRECTION THAT CAME WITH IT. Row **[218] Stargates!** is stance
*"No integration"*, and that was read as *"do not use it"* for three checkpoints while the owner
said the opposite every time. **The register is guidance; the owner's direction is not.** What
the row actually protects is ownership of state -- *"Backrooms coordinates and the company's
machine must keep their own stable IDs and state"* -- and that is kept exactly: their addresses
stay theirs, our coordinate records stay ours, and the only thing crossing between is a dial.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "RimroomsAsyncIndustries")
BRIDGE = os.path.join(SRC, "Portals", "StargateBridge.cs")
EMERGENCE = os.path.join(SRC, "Portals", "CompRimroomsEmergence.cs")
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "1.6")
THEIRS = (r"C:\Program Files (x86)\Steam\steamapps\workshop\content"
          r"\294100\2831698056\Source\Stargates")

failures = []


def check(claim, held, detail=""):
    print("  %s  %s%s" % ("HOLDS " if held else "FAILS!", claim,
                          "" if held else "\n          " + detail))
    if not held:
        failures.append(claim)


def read(path):
    try:
        return io.open(path, encoding="utf-8-sig", errors="replace").read()
    except IOError:
        return None


print("")
print("THEIR GATE, OUR DOOR, OUR DIALLING -- AND THEIR MOD UNTOUCHED")
print("=" * 78)
print("")

bridge = read(BRIDGE)
emergence_raw = read(EMERGENCE)
# COMMENTED-OUT CODE IS NOT CODE. Three plants commented a call out and every presence test still
# matched, because the text was still in the file. Read the way `check-compliance.py` reads C#.
emergence = re.sub(r"/\*.*?\*/", " ",
                   re.sub(r"//[^\n]*", " ", emergence_raw or ""), flags=re.S)
theirs = read(os.path.join(THEIRS, "CompStargate.cs"))

check("the bridge exists", bridge is not None,
      "-- StargateBridge.cs is the whole integration surface")

# ------------------------------------------------------------------ against their actual code
print("")
print("CHECKED AGAINST THE INSTALLED MOD'S OWN SOURCE, not against a description of it")
print("-" * 78)

if theirs is None:
    check("the Stargate mod's source was found", False,
          "-- without it these claims verify nothing, so they fail rather than pass. The mod is "
          "optional at RUNTIME; it is required to PROVE this integration still matches it")
else:
    check("CompStargate really is a ThingComp, so it goes on an ordinary door",
          re.search(r"class\s+CompStargate\s*:\s*ThingComp\b", theirs) is not None,
          "-- the whole of *\"but use a normal door\"* rests on this. If they made it a Building "
          "subclass, a door can never carry it and this integration must be redesigned")

    check("a gate registers its own address on spawn, so both ends self-register",
          "AddressComp.AddAddress(GateAddress)" in theirs
          and "AddressComp.AddPocketMapAddress(GateAddress)" in theirs,
          "-- we attach the component and their InitGate does the registering; we never write to "
          "their address list")

    check("THEIR GATE USES CORE'S TRANSPORTER, which is the automatic hauling",
          "parent.GetComp<CompTransporter>()" in theirs,
          "-- owner: *\"how the fuck are they suppose to auto pick up materials on one side\"*. "
          "With Core's transporter on the door, colonists haul the chosen materials to the gate "
          "themselves and the gate sends them. Their mod does it, not us")

    check("the dial we call is a public method with the signature we pass",
          re.search(r"public\s+void\s+OpenStargateDelayed\s*\(\s*PlanetTile\s+\w+\s*,"
                    r"\s*int\s+\w+\s*,\s*DialMode\s+\w+\s*\)", theirs) is not None,
          "-- three arguments, in this order. A signature change must fail here rather than at "
          "runtime in the owner's colony")

    check("and closing is public too",
          re.search(r"public\s+void\s+CloseStargate\s*\(", theirs) is not None)

    check("the fields we read are public",
          re.search(r"public\s+bool\s+StargateIsActive", theirs) is not None
          and re.search(r"public\s+bool\s+IsHibernating", theirs) is not None
          and re.search(r"public\s+bool\s+IsReceivingGate", theirs) is not None,
          "-- a private read is banned outright, and would also be a lie about how stable this "
          "is. Public members are what they publish")

    check("ONE GATE PER MAP IS THEIR RULE, which is why we attach per instance",
          "IsHibernating = true" in theirs and "GetAllStargatesOnMap" in theirs,
          "-- patching the comp onto Core's `Door` would make every door a gate and announce one "
          "hibernation per extra door. That is the reason this is not an XML comps patch")

    check("the def we borrow settings from is one of theirs",
          "StargateMod_Stargate" in read(os.path.join(
              os.path.dirname(THEIRS), "..", "1.6", "Defs", "ThingDefs_Buildings",
              "StargateBuilding.xml")) if os.path.isfile(os.path.join(
                  os.path.dirname(THEIRS), "..", "1.6", "Defs", "ThingDefs_Buildings",
                  "StargateBuilding.xml")) else "StargateMod_Stargate" in bridge,
          "-- borrowed rather than constructed, so a Backrooms gate is configured exactly as "
          "their stargate is and retunes when they retune it")

# ------------------------------------------------------------------------- our side of the line
print("")
print("NOTHING OF THEIRS IS EDITED, PATCHED, OR REQUIRED")
print("-" * 78)

check("no XML patch of ours names their mod's defs or types",
      not any("StargatesMod" in (read(os.path.join(root, name)) or "")
              for root, _, names in os.walk(MOD) for name in names if name.endswith(".xml")),
      "-- owner: *\"WE ARE NOT EDITING OTHER PEOPLES MODS!\"* and *\"we still use the stargate "
      "mod as normal\"*. The integration is per-instance and in code; their files and their defs "
      "are untouched")

check("THE BUILD HAS NO REFERENCE TO THEIR ASSEMBLY",
      "Stargates" not in (read(os.path.join(REPO, "src", "RimroomsAsyncIndustries",
                                            "RimroomsAsyncIndustries.csproj")) or ""),
      "-- owner: *\"i need someone else to work on this in parrellel through git hub\"*. A "
      "collaborator without this Workshop item installed must still compile the package")

check("EVERY type of theirs is found by Core's own name lookup",
      bridge.count("GenTypes.GetTypeInAnyAssembly") >= 3 and "Type.GetType(" not in bridge,
      "-- three types are resolved, and a plant swapped one for a bare `Type.GetType` that cannot "
      "see mod assemblies while the other two kept the presence test satisfied. "
      "GenTypes is the lookup def loading itself uses")

check("AVAILABLE IS HONEST ABOUT WHETHER THEIR MOD IS THERE",
      "return compType != null && donorProps != null && openMethod != null;" in bridge,
      "-- counting guard clauses says nothing about whether the guard tells the truth. A plant "
      "made this `return true;` and every count still held, which would crash a Core-only colony")

check("every entry point answers false when the mod is absent",
      bridge.count("if (!Available") >= 4,
      "-- Attach, Dial, Close and the flag reads all refuse first. Installing this mod without "
      "theirs must behave exactly as it did before")

# COMMENTS STRIPPED FIRST, because the first draft of this claim failed against correct code:
# the file's own doc comment SAYS "no Harmony, no detour, no `SetValue`, no
# `BindingFlags.NonPublic`", and a bare substring test cannot tell an explanation from a
# violation. `check-compliance.py` strips comments before scanning for exactly this reason, and
# a proof that does not is checking the prose rather than the code.
_code = re.sub(r"//[^\n]*", " ", bridge)
_code = re.sub(r"/\*.*?\*/", " ", _code, flags=re.S)
check("no Harmony, no detour, no reflection write, no private read",
      "Harmony" not in _code and "SetValue" not in _code
      and "BindingFlags.NonPublic" not in _code,
      "-- the standing rule, and this is the file most likely to be tempted to break it")

check("and the file still EXPLAINS that rule rather than only obeying it",
      "BindingFlags.NonPublic" in bridge,
      "-- the doc comment naming what is banned is why the claim above must strip comments; "
      "losing the explanation to satisfy a grep would be the wrong fix")

check("their CompProperties is BORROWED, never constructed",
      "donorProps" in bridge and "new CompProperties_Stargate" not in bridge,
      "-- constructing it would mean assigning their fields, and our copy of their numbers would "
      "go stale the moment they retune the gate")

check("only Core's own transporter is constructed by us",
      "new CompProperties_Transporter()" in bridge,
      "-- Core's type, our object, so no other mod's fields are ever assigned")

check("the component is added to the instance, not to the def",
      "door.AllComps.Add(gate);" in bridge and "door.AllComps.Add(transporter);" in bridge
      and "def.comps.Add" not in bridge,
      "-- `AllComps.Add(` appears twice for two different components, so a bare presence test "
      "stayed satisfied when the gate was moved onto the def. Adding to the DEF would make every "
      "door in every colony a stargate, which is the one thing this must never do") if True else check(
      "placeholder", True,
      "-- ThingWithComps.AllComps is a public list; this is what keeps every other door in every "
      "colony exactly as it was")

print("")
print("BOTH ENDS, AND WE DIAL")
print("-" * 78)

check("BOTH ANCHORS OF THE ROUTE GET THE GATE, BOTH AS NATURAL",
      "StargateBridge.Attach(near, true)" in emergence
      and "StargateBridge.Attach(far, true)" in emergence,
      "-- owner: *\"and connect them together to the backrooms and the map\"*. The far anchor "
      "stands inside a coordinate, which is not an ordinary branch map, so it can never mark "
      "itself; the near side knows the edge and attaches both")

check("the far end is read from the edge rather than searched for",
      "private ThingWithComps FarAnchor(PortalConnectionRecord edge)" in emergence,
      "-- the network already records the pairing; searching for a door would be a second "
      "opinion that could disagree with it")

check("WE DIAL, IN THE BACKGROUND, FROM OUR OWN NETWORK",
      # The whole guard, not the call: a plant wrapped it in `if (false && ...)` and the call was
      # still "in" the file.
      "if (!StargateBridge.Dial(near, far.Map, 0))" in emergence,
      "-- owner: *\"we just use our own dialing converstion in the background\"*. The address is "
      "read off the destination map; the player never touches a DHD for the Backrooms")

check("the address conversion handles a pocket map as well as a world tile",
      "new PlanetTile(destination.Index)" in bridge and "destination.Tile" in bridge
      and '"PocketMap" : "Map"' in bridge,
      "-- their InitGate registers a map index for a pocket map and a tile otherwise, so the dial "
      "has to speak both. `destination.IsPocketMap` appears in two ternaries, so naming the "
      "string was not enough to prove the ADDRESS half survived")

# **EVERY REFUSAL NAMES ITSELF.** The wormhole took a whole launch to diagnose because these
# paths returned silently and the owner's log held nothing at all. Silence is correct for a colony
# without their mod; it is useless the moment something does not work, which is every time it
# matters.
check("A LIVE GATE THAT CANNOT DIAL SAYS WHY, ONCE",
      "private void ReportGateState(string reason)" in emergence
      and "if (reportedGateState) { return; }" in emergence
      and emergence.count("ReportGateState(") >= 5,
      "-- Log.Message, not Log.Error: a gate that cannot dial is information, not a fault. Once "
      "per door, because this runs on a tick")

check("and the far end being a non-door is one of the reasons it can give",
      # `"not a doorway"` CONTAINS `"not a door"`. The prefix trap, so the clause continues.
      'is not a door, so no gate can be ' in emergence,
      "-- a destination below DoorThresholdContentVersion keeps a historical anchor that is not "
      "a door, so `as ThingWithComps` yields null and the route has no far end to put a gate on. "
      "That was the one stop that said nothing")

check("a receiving or hibernating end is never dialled",
      "StargateBridge.IsReceiving(near)" in emergence
      and "StargateBridge.IsHibernating(near)" in emergence,
      "-- their wormhole is one-way and their one-gate-per-map rule is theirs to enforce; "
      "fighting either would be using the mod wrongly rather than using it")

# ANCHORED TO THE INTERVAL TICK, which is the one a Normal-ticker door actually receives.
# The first draft matched the identical pair inside CompTickRare, so deleting the pair that runs
# on a door still passed.
_interval = emergence.find("public override void CompTickInterval(int delta)")
# BOUNDED BY THE NEXT METHOD, not by a character count. With comments stripped, CompTickRare sits
# a few lines below and a fixed-width window swallowed its identical pair -- so deleting the call
# from the tick a door actually receives still matched the copy in the tick it never gets.
_after = emergence[_interval:] if _interval >= 0 else ""
_next = _after.find("public override", 40)
_window = _after[:_next] if _next > 0 else _after
check("and it is driven from the same tick that paints the gate",
      "RefreshGateAppearance();" in _window and "RefreshStargate();" in _window,
      "-- one place asks *is this a gate yet*, so the glow and the wormhole can never disagree "
      "about the answer -- and it must be the tick a door really gets")

check("only a LIVE gate is wired, never a merely marked door",
      re.search(r"private void RefreshStargate\(\)(?:.|\n){0,400}?if \(edge == null \|\| "
                r"!IsLiveGate\) \{ return; \}", emergence) is not None,
      "-- a marked door nothing leads through is a plan, not a gate, and turning one into a "
      "stargate would register an address for a place that does not exist")

print("")
print("THEIR EFFECTS, AT A DOOR'S SCALE -- COMPUTED FROM THE SOURCE, NOT READ FROM IT")
print("-" * 78)

# Owner: *"lets use the fx and visual stuff if we can and make them appropriate sizes to the sizes
# of possible doors natural and maching gate types"*.
_ratio_match = re.search(r"float puddle = width \* ([0-9.]+)f;", bridge)
_width_match = re.search(r"int width = Math\.Max\(1, Math\.Max\(door\.size\.x, door\.size\.z\)\);",
                         bridge)

check("the size is read off the door's own footprint",
      _width_match is not None,
      "-- not a list of def names. Core's 1x1 Door, the 2x1 OrnateDoor, Anomaly's SecurityDoor "
      "and the wider doors another mod ships are all covered by reading `def.size`")

check("and the ratio was found in the source rather than assumed by this proof",
      _ratio_match is not None,
      "-- a renamed or inlined constant must fail here rather than let the claims below pass by "
      "modelling nothing")

if _ratio_match is not None:
    _ratio = float(_ratio_match.group(1))

    # Their own three gates, measured off their defs.
    _theirs = [("StargateMod_Stargate", 5, 8.7),
               ("StargateMod_OrlinStargate", 3, 5.3),
               ("StargateMod_AdvancedStargate", 5, 7.9)]
    _band = [puddle / float(size) for _, size, puddle in _theirs]
    check("THE RATIO IS INSIDE THEIR OWN BAND, so this is their look at our scale",
          min(_band) - 0.01 <= _ratio <= max(_band) + 0.01,
          "-- %.2f against their %s. A number outside what they ship is our invention wearing "
          "their textures" % (_ratio, ", ".join("%.2f" % value for value in _band)))

    print("     footprint        width  puddle  vortex cells  iris")
    _worst = 0
    for _label, _x, _z in [("Door", 1, 1), ("OrnateDoor", 2, 1), ("SecurityDoor", 2, 1),
                           ("gate 1x2", 1, 2), ("gate 1x3", 1, 3), ("gate 2x3", 2, 3)]:
        _width = max(1, max(_x, _z))
        _half = _width // 2
        _cells = [(_offset, 1) for _offset in range(-_half, _width - _half)]
        _worst = max(_worst, len(_cells))
        print("     %-16s %5d %7.2f %13d  %s"
              % (_label, _width, _width * _ratio, len(_cells), "yes" if _width >= 2 else "no"))

    check("THE VORTEX IS A DOORWAY, NEVER THEIR THIRTEEN-CELL CRATER",
          _worst <= 3,
          "-- worst case %d cells. Their own pattern is 13, three wide and four deep, which is "
          "right for a ring standing in the open and wrong for a shop's back wall" % _worst)

check("THE GATE IS ACTUALLY GIVEN THE SIZED PROPERTIES",
      "gate.Initialize(SizedProps(door.def, naturalGate));" in bridge,
      "-- every other claim here proves the sizing is COMPUTED correctly. This is the one that "
      "proves it is USED. A plant swapped this back to their unsized properties and the whole "
      "section still passed while a 1x1 door got a seven-by-seven kawoosh")

check("A NATURAL GATE HAS NO UNSTABLE VORTEX AT ALL",
      "naturalGate ? false : offset <= width - 1 - half" in bridge,
      "-- owner: *\"the natural portals are open always right?\"*. A natural gate never OPENS, "
      "so nothing spins up and nothing is vaporised. **And this is not cosmetic:** their wormhole "
      "closes itself after about forty seconds idle, so a permanently-open gate is re-dialled on "
      "a loop -- a vortex on it would have detonated its own doorway every time, for ever")

check("the machine gate's vortex is one cell deep, across the door's width",
      '.Append(",0,1)</li>")' in bridge
      and "for (int offset = -half; naturalGate ? false : offset <= width - 1 - half; offset++)"
      in bridge
      and bridge.count('Append("<li>(') == 1,
      "-- owner: *\"i understand the machine gate opening and closing and will kill anyone "
      "standing near in front on start up\"*. The threshold, whichever way the door faces. EVERY "
      "cell must come from the one loop -- checking that the right cell is emitted does not stop "
      "a second one being appended after it")

check("and the two kinds cannot share a cached result",
      'door.defName + (naturalGate ? "|natural" : "|machine")' in bridge,
      "-- caching on the def alone would hand the first kind asked for to the second, which is "
      "how a natural gate quietly inherits a machine gate's kawoosh")

check("an iris is offered only where there is an opening worth covering",
      'Append(width >= 2 ? "true" : "false")' in bridge,
      "-- their own makeshift gate sets canHaveIris false for the same reason")

check("THE PROPERTIES ARE BUILT BY CORE'S OWN XML LOADER, so no field of theirs is assigned",
      "DirectXmlToObject.ObjectFromXml<CompProperties>" in bridge,
      "-- the same call def loading makes, reading the same `Class=` attribute. This is how the "
      "effects get OUR sizes without this package ever writing to their type")

check("the texture paths are read from their own gate, so a retexture follows",
      'FieldInfo field = donorProps.GetType().GetField(fieldName);' in bridge
      and "field.GetValue(donorProps) as string" in bridge,
      "-- a public field read; nothing is written and nothing private is touched")

check("a failure to size falls back to their properties rather than breaking the gate",
      "cached = built ?? donorProps;" in bridge,
      "-- theirs unchanged is a worse look, never a dead route. The one thing that failed was "
      "how it is drawn")

check("and the result is cached per def rather than rebuilt per door",
      "sizedProps.TryGetValue(key, out cached)" in bridge,
      "-- a shop has nine doors and a coordinate has dozens; parsing XML for each one would be a "
      "load-time cost for a value that depends only on the def")

print("")
if failures:
    print("%d CLAIM(S) FAILED" % len(failures))
    for claim in failures:
        print("  - %s" % claim)
    sys.exit(1)
print("ALL STARGATE-BRIDGE CLAIMS HOLD")
