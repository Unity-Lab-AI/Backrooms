# -*- coding: utf-8 -*-
"""Re-teach proof-starts.py: an inside start now has a layout and an opening sequence."""
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


# Collect the emergence cell.
sub(u'            "conduits": len(node.find("conduits") or []),\n        })',
    u'            "conduits": len(node.find("conduits") or []),\n'
    u'            "exitDoor": cell(node.findtext("emergenceDoorCell")),\n'
    u'        })')

# Replace the old inside-start early-exit with claims that fit the reworked design. An inside
# start now has a real layout, so it falls THROUGH to every geometry claim as well.
sub(u'''    # An inside start declares no layout at all: the map IS a generated coordinate, wall to
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

''',
u'''    # EVERY start names a generator, and every genstep that generator lists must resolve. A
    # class named in XML and defined nowhere does not crash: the step silently does nothing, so
    # the player gets an ordinary colony while the scenario description promises otherwise.
    check("%s names a map generator the mod ships" % name, start["generator"] in generators,
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

    # An inside start's people begin in a coordinate generated BESIDE the surface map, so it has
    # an ordinary layout like the others -- just a very small one -- and it additionally has to
    # name which of its own doors is the way out.
    if start["inside"]:
        check("%s names an emergence door" % name, start["exitDoor"] is not None,
              "-- nothing to mark, so the start would have no registered exit at all")
        check("%s emergence door is one of its own doors" % name,
              start["exitDoor"] in start["doors"],
              "-- no door is generated at %s, so there is nothing to mark"
              % str(start["exitDoor"]))

''')

# The opening sequence's ORDER is the safety, exactly like the way-out cap.
sub(u'''# --------------------------------------------------------------------------- the natural chain''',
u'''# --------------------------------------------------------------------------- the solo opening
# The guaranteed exit. Owner: "needs to 100% have a exit to map natural portal on their first
# backrroms level". A survey draw cannot deliver a guarantee, so the opening registers the
# connection directly -- and the ORDER of its steps is the safety of it.
OPENING = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "Scenario", "SoloGroupOpening.cs")
if os.path.isfile(OPENING):
    opening = io.open(OPENING, encoding="utf-8-sig").read()
    print("")
    i_site = opening.find("DestinationService.EnsureSite(")
    i_mark = opening.find("anchor.Mark()")
    i_reg = opening.find("PortalAddressService.RegisterEmergenceAddress(")
    i_move = opening.find("MoveOpeningPartyInside(")

    check("the opening generates a real coordinate", i_site != -1,
          "-- without a RimroomsDestinationMapParent no connection can ever be registered")
    check("the opening marks the surface door", i_mark != -1,
          "-- the network refuses an Emergence endpoint that is not marked")
    check("the opening registers the way out", i_reg != -1,
          "-- the exit would not exist, which is the one thing the direction requires at 100%")
    check("the opening moves the party inside", i_move != -1,
          "-- they would start on the surface, not in the Backrooms")

    # THE claim. Registering before moving means a failure anywhere above leaves everybody
    # standing safely on the surface. Moving first would seal a group inside a coordinate with
    # no registered way out, which is the exact trap invariant 28 forbids.
    check("the way out is registered BEFORE anybody is moved inside",
          i_reg != -1 and i_move != -1 and i_reg < i_move,
          "-- a failure would seal the group inside with no registered exit")
    check("the door is marked before the connection is registered",
          i_mark != -1 and i_reg != -1 and i_mark < i_reg,
          "-- the network would refuse an unmarked Emergence endpoint")

# --------------------------------------------------------------------------- the natural chain''')

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('proof re-taught for the reworked solo start')

import ast
ast.parse(s)
print('proof-starts.py parses clean')
