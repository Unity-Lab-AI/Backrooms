# -*- coding: utf-8 -*-
"""Teach proof-starts.py about inside starts, whose map IS the coordinate."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(REPO, '.local', 'register', 'proof-starts.py')
s = io.open(p, encoding='utf-8').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:70]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:70]
    s = s.replace(old, new, 1)


# Collect the two new fields.
sub(u'            "contact": (node.findtext("beginsInCorporationContact") or "false").strip().lower(),\n        })',
    u'            "contact": (node.findtext("beginsInCorporationContact") or "false").strip().lower(),\n'
    u'            "inside": (node.findtext("insideStart") or "false").strip().lower() == "true",\n'
    u'            "generator": (node.findtext("mapGenerator") or "").strip(),\n'
    u'            "conduits": len(node.find("conduits") or []),\n'
    u'        })')

# Know which generators we ship, and that each names a genStep class we define.
sub(u'print("starts          : %d" % len(starts))',
u'''generators = {}
for path in glob.glob(os.path.join(MOD, "Defs", "**", "*.xml"), recursive=True):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        continue
    for node in root.iter("MapGeneratorDef"):
        name = node.findtext("defName")
        if name:
            generators[name.strip()] = [li.text.strip() for li in (node.find("genSteps") or []) if li.text]
    for node in root.iter("GenStepDef"):
        name = node.findtext("defName")
        step = node.find("genStep")
        if name and step is not None:
            generators.setdefault("genstep:" + name.strip(), [step.get("Class") or ""])

SRC = os.path.join(REPO, "src")
source_text = ""
for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
    source_text += io.open(path, encoding="utf-8-sig").read()

print("starts          : %d" % len(starts))''')

# Branch the per-start body.
sub(u'''    # Walls, and interiors, exactly as the generator lays them.''',
u'''    # An inside start declares no layout at all: the map IS a generated coordinate, wall to
    # wall, so every geometry claim below is about a facility that does not exist. What must
    # be true instead is that it declares nothing, and that the generator it names is real.
    if start["inside"]:
        check("%s declares no rooms, doors, buildings or conduits" % name,
              not start["rooms"] and not start["doors"] and not start["buildings"]
              and start["conduits"] == 0,
              "-- a facility built on top of a coordinate that is already wall to wall")
        check("%s uses the coordinate map size (60)" % name, start["mapSize"] == 60,
              "-- GenStep_InsideStart refuses any other size, so the start would fail at new game")
        check("%s names a map generator the mod ships" % name,
              start["generator"] in generators,
              "-- '%s' does not exist, and Core would fall back to an ordinary colony map"
              % start["generator"])
        for step in generators.get(start["generator"], []):
            cls = generators.get("genstep:" + step, [""])[0]
            short = cls.split(".")[-1] if cls else ""
            if not short:
                continue
            check("%s genstep %s resolves to a real class" % (name, step),
                  ("class " + short) in source_text,
                  "-- named in XML, defined nowhere; the step silently does nothing")
        check("%s declares between one and five roles (%d)" % (name, start["roles"]),
              1 <= start["roles"] <= 5)
        print("")
        continue

    # Walls, and interiors, exactly as the generator lays them.''')

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('proof-starts now understands inside starts')

import ast
ast.parse(s)
print('proof-starts.py parses clean')
