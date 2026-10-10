# -*- coding: utf-8 -*-
"""Two power plants anchored on the old one-line `try`, and the claim they break.

`RebuildPowerNets` returns a bool now, so its body is a block rather than a one-liner, and both
plants reported `PLANT SETUP BROKEN (0 matches)` -- which is the suite doing its job: an anchor
that no longer exists is reported, never silently skipped.

**And the claim is restored to its full strength on the way past.** Re-aiming it earlier dropped
the `try` from the assertion and left only the call, which would have passed against an unguarded
rebuild -- the exact defect the claim exists for. It asserts the whole guarded block now.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-generation.py")

CLAIM_OLD = u'      and "map.powerNetManager.UpdatePowerNetsAndConnections_First();" in genstep\n'
CLAIM_NEW = (
    u'      # **THE GUARD, not just the call.** Re-aiming this claim at 0.12.71-dev briefly left\n'
    u'      # only the call, which passes against an unguarded rebuild -- the defect the claim\n'
    u'      # exists for. The whole block is asserted, in order.\n'
    u'      and ("            try" + chr(10)\n'
    u'           + "            {" + chr(10)\n'
    u'           + "                map.powerNetManager.UpdatePowerNetsAndConnections_First();" + chr(10)\n'
    u'           + "                return true;" + chr(10)\n'
    u'           + "            }" + chr(10)\n'
    u'           + "            catch (Exception exception)") in genstep\n')

PLANT_OLD = u'''    ("A POWER-GRID THROW TAKES THE WHOLE LEVEL AGAIN", GEN,
     "            try { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }",
     "            if (true) { map.powerNetManager.UpdatePowerNetsAndConnections_First(); }"),

    ("the rebuild is guarded in one place and bare in another", GEN,
     "                RebuildPowerNets(map, coordinate);" + NL
     + "                // Whatever the dressing just placed that draws power, wired now that it exists.",'''

PLANT_NEW = u'''    ("A POWER-GRID THROW TAKES THE WHOLE LEVEL AGAIN", GEN,
     "            try" + NL + "            {" + NL
     + "                map.powerNetManager.UpdatePowerNetsAndConnections_First();",
     "            if (true)" + NL + "            {" + NL
     + "                map.powerNetManager.UpdatePowerNetsAndConnections_First();"),

    ("the rebuild stops reporting whether it worked", GEN,
     "                return true;" + NL + "            }" + NL
     + "            catch (Exception exception)",
     "            }" + NL + "            catch (Exception exception)"),

    ("the rebuild is guarded in one place and bare in another", GEN,
     "                RebuildPowerNets(map, coordinate);" + NL
     + "                // Whatever the dressing just placed that draws power, wired now that it exists.",'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(CLAIM_OLD) != 1:
    print("CLAIM ANCHOR PROBLEM: %d" % text.count(CLAIM_OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(CLAIM_OLD, CLAIM_NEW, 1))
print("the claim asserts the whole guarded block again")

suite = io.open(SUITE, encoding="utf-8").read()
if suite.count(PLANT_OLD) != 1:
    print("PLANT ANCHOR PROBLEM: %d" % suite.count(PLANT_OLD))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(suite.replace(PLANT_OLD, PLANT_NEW, 1))
print("two power plants re-aimed and one added for the return value")
