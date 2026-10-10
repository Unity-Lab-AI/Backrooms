# -*- coding: utf-8 -*-
"""Plant every way the sized effects could quietly go back to being unsized.

Owner: *"lets use the fx and visual stuff if we can and make them appropriate sizes to the sizes
of possible doors natural and maching gate types"*.

The dangerous ones are not the crashes. They are the two that leave the package compiling, every
checker passing, and a thirteen-cell kawoosh going off inside a shop: the vortex pattern silently
reverting to theirs, and the sizing falling back to the donor without anybody noticing.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANT = os.path.join(REPO, ".local", "register", "plant-stargate-bridge.py")

ANCHOR = u'''    ("the pocket-map half of the address conversion is dropped", BRIDGE,'''

NEW = u'''    # -------------------------------------------------------- the effects stop being sized
    ("THE GATE GOES BACK TO THEIR UNSIZED PROPERTIES, so a 1x1 door gets a 7x7 kawoosh", BRIDGE,
     "gate.Initialize(SizedProps(door.def));", "gate.Initialize(donorProps);"),

    ("the puddle stops being read off the door's footprint", BRIDGE,
     "int width = Math.Max(1, Math.Max(door.size.x, door.size.z));", "int width = 5;"),

    ("THE RATIO LEAVES THE BAND THEIR OWN GATES SIT IN", BRIDGE,
     "float puddle = width * 1.6f;", "float puddle = width * 4f;"),

    ("the vortex gets deeper than a doorway", BRIDGE,
     '.Append(",0,1)</li>");', '.Append(",0,1)</li>").Append("<li>(0,0,2)</li>");'),

    ("the vortex stops spanning the door's width", BRIDGE,
     "for (int offset = -half; offset <= width - 1 - half; offset++)",
     "for (int offset = -half; offset <= -half; offset++)"),

    ("an iris is offered on a door with no opening to cover", BRIDGE,
     'Append(width >= 2 ? "true" : "false")', 'Append("true")'),

    ("the properties stop being built by Core's loader", BRIDGE,
     "return DirectXmlToObject.ObjectFromXml<CompProperties>(document.DocumentElement, false);",
     "return donorProps;"),

    ("the texture paths stop following their gate", BRIDGE,
     "FieldInfo field = donorProps.GetType().GetField(fieldName);",
     "FieldInfo field = null;"),

    ("A SIZING FAILURE BREAKS THE ROUTE instead of just looking wrong", BRIDGE,
     "cached = built ?? donorProps;", "cached = built;"),

    ("the properties are rebuilt for every door instead of cached per def", BRIDGE,
     "if (sizedProps.TryGetValue(door, out cached)) { return cached; }", ""),

    ("the pocket-map half of the address conversion is dropped", BRIDGE,'''

text = io.open(PLANT, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PLANT, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, NEW, 1))
print("ten fx plants added")
