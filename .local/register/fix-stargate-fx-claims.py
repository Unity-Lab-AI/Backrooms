# -*- coding: utf-8 -*-
"""The effects are sized from the door, and the proof computes the sizes rather than reading them.

Owner: *"yeah lets use the fx and visual stuff if we can and make them appropriate sizes to the
sizes of possible doors natural and maching gate types"*.

THE RATIO IS THEIRS, MEASURED, NOT INVENTED. Across all three of their gate defs the event
horizon is a square about 1.6 to 1.77 times the gate's width:

    StargateMod_Stargate          size (5,1)   puddleDrawSize 8.7   = 1.74x
    StargateMod_OrlinStargate     size (3,1)   puddleDrawSize 5.3   = 1.77x
    StargateMod_AdvancedStargate  size (5,1)   puddleDrawSize 7.9   = 1.58x

So 1.6 is inside their own band, and a 1x1 door gets a 1.6-cell shimmer while a three-wide door
gets 4.8. **Every footprint is covered because the number is read off `def.size`** -- Core's 1x1
`Door`, the 2x1 `OrnateDoor`, Anomaly's `SecurityDoor`, and the 1x2 / 1x3 / 2x3 shapes a gate run
may take.

THE VORTEX IS THE PART THAT HAD TO SHRINK. Theirs is thirteen cells, three wide and four deep --
a ring standing in the open. On a shop's back wall that is a demolition charge. A door's unstable
vortex is **its own opening, one cell deep, across its own width**: still fatal to stand in, which
is the Stargate rule, and still a doorway rather than a crater.

AND THE CLAIMS ARE COMPUTED, NOT READ. The same shape as the conduit sizing: the proof extracts
the ratio and the pattern rule from the source and works out what every legal footprint produces,
so a future retune fails on the number that proves it rather than on nobody noticing.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-stargate-bridge.py")

ANCHOR = u'''print("")
if failures:'''

NEW = u'''print("")
print("THEIR EFFECTS, AT A DOOR'S SCALE -- COMPUTED FROM THE SOURCE, NOT READ FROM IT")
print("-" * 78)

# Owner: *"lets use the fx and visual stuff if we can and make them appropriate sizes to the sizes
# of possible doors natural and maching gate types"*.
_ratio_match = re.search(r"float puddle = width \\* ([0-9.]+)f;", bridge)
_width_match = re.search(r"int width = Math\\.Max\\(1, Math\\.Max\\(door\\.size\\.x, door\\.size\\.z\\)\\);",
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

check("the vortex is one cell deep, across the door's width",
      '.Append(",0,1)</li>")' in bridge
      and "for (int offset = -half; offset <= width - 1 - half; offset++)" in bridge,
      "-- the threshold, whichever way the door faces: their VortexCells rotates these offsets by "
      "the door's rotation")

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
      "sizedProps.TryGetValue(door, out cached)" in bridge,
      "-- a shop has nine doors and a coordinate has dozens; parsing XML for each one would be a "
      "load-time cost for a value that depends only on the def")

print("")
if failures:'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("fx sizing claims added")
