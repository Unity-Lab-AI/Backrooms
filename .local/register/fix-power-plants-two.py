# -*- coding: utf-8 -*-
"""The last two power plants anchored on call shapes 0.12.71-dev moved.

Both still plant the same fault -- a bare `UpdatePowerNetsAndConnections_First()` outside the one
guarded implementation -- against the call sites as they stand now.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-generation.py")

OLD = u'''    ("the rebuild is guarded in one place and bare in another", GEN,
     "                RebuildPowerNets(map, coordinate);" + NL
     + "                // Whatever the dressing just placed that draws power, wired now that it exists.",
     "                map.powerNetManager.UpdatePowerNetsAndConnections_First();" + NL
     + "                // Whatever the dressing just placed that draws power, wired now that it exists."),

    ("and the stray pass stops naming the coordinate it failed on", GEN,
     "                RebuildPowerNets(map, coordinate);" + NL + "            }" + NL + "        }",
     "                map.powerNetManager.UpdatePowerNetsAndConnections_First();" + NL'''

NEW = u'''    ("the rebuild is guarded in one place and bare in another", GEN,
     "                    RebuildPowerNets(map, coordinate);",
     "                    map.powerNetManager.UpdatePowerNetsAndConnections_First();"),

    ("and the stray pass stops naming the coordinate it failed on", GEN,
     "                if (!RebuildPowerNets(map, coordinate)) { return false; }",
     "                map.powerNetManager.UpdatePowerNetsAndConnections_First();" + NL'''

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % suite.count(OLD))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite.replace(OLD, NEW, 1))
print("the last two power plants re-aimed")
