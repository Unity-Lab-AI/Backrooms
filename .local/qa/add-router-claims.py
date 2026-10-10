"""Three claims the plants proved were missing.

Each of these faults was planted, the suite rebuilt, and **no claim anywhere
noticed**. That is the mutation battery doing the one job source-text proofs
cannot do for themselves: a claim can assert that a function exists and be
perfectly satisfied while the line that calls it has been turned into a
constant.
"""
import io
import sys

NL = chr(10)
PROOF = ".local/register/proof-coordinate-layout.py"

GATE = (
    "if failures:" + NL
    + '    print("PROOF FAILED: %d claim(s)" % len(failures))' + NL
    + "    sys.exit(1)" + NL
)

CLAIMS = '''
# ======================================================================================
# THREE CLAIMS THE PLANTS ASKED FOR. Each fault below was planted and caught by nothing:
# the guard was still defined, still called, and the call had been replaced by a constant.
# ======================================================================================

check("THE PUSH'S ROUTE CHECK IS ASKED, not merely written",
      "bool blocksARoute = !EveryLinkRoutes(rooms, mover, depth);" in planner
      and "bool blocksARoute = false;" not in planner_code,
      "-- a plant replaced this assignment with `false` and every claim about `EveryLinkRoutes` "
      "still held: the function was defined, the condition still named it, and no room was ever "
      "checked again. **The thing to assert is the call, not the callee** -- the same gap that let "
      "a plant switch off room-size variation while the variation function sat there untouched")

check("AND A ROUTE'S TWO TERMINI ARE NOT EXTENDED, so corridor floor never reaches inside a room",
      "if (index != 0) { start -= step * reach; }" in planner
      and "if (index + 2 != points.Count) { end += step * reach; }" in planner,
      "-- every interior end of every leg overruns its turn so the corner is a solid block, and "
      "the two ends that sit one cell outside a room's wall do not, because extending them would "
      "put corridor floor inside the room. **A plant dropped the `index != 0` guard and nothing "
      "failed**: the route still carved, the level still validated, and a corridor quietly ate "
      "the edge of every room it left -- which is the wall the doorway is in")

check("THE REACH BRAID'S ROLL IS ASKED, so links to a slot two away actually happen",
      "internal const int ReachBraidRarity = 5;" in planner
      and "if (roll % ReachBraidRarity != 0) { continue; }" in planner
      and 'StableHash(seed,' in planner
      and '"reach:" + slot.x + "," + slot.z + ":" + side, depth);' in planner
      and "new IntVec2(2, 0), new IntVec2(0, 2), new IntVec2(2, 1), new IntVec2(2, -1)," in planner,
      "-- the eight offsets with a span of two, each considered once from the lower-left of the "
      "pair. **These are the only links that pass eight**, because eight is every neighbour a slot "
      "has, and the five-leg route forms are what arrive at a slot the pair are not adjacent to. "
      "Measured: max degree 8 without them, 13 to 16 with. A plant disabled the roll and no claim "
      "noticed, because the constant and the offsets were all still sitting there")

'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(GATE) != 1:
    print("exit gate not found exactly once (%d)" % text.count(GATE))
    sys.exit(1)
io.open(PROOF, "w", encoding="utf-8", newline=NL).write(text.replace(GATE, CLAIMS + GATE))
print("three claims inserted before the exit gate")
