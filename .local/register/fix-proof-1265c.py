# -*- coding: utf-8 -*-
"""The walk-through claim reads `menu_body`, a window, not the whole file."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LINKS = os.path.join(REPO, ".local", "register", "proof-gate-links.py")

OLD = u'''      and "if (!IsLiveGate) { yield break; }" in menu_body,
      "-- the order and the job already walked a pawn to the door and crossed them to the other "
      "map. What was missing was the place a player looks: it was only reachable by selecting "
      "pawns, selecting the door, clicking a gizmo and choosing from a float menu, which is a "
      "dispatch console rather than a door")'''

NEW = u'''      # A door that is NOT a live gate is now asked whether it is an undiscovered way onward
      # before the menu gives up. **`NaturalFrontierService.Discover` had ZERO callers** -- the
      # draw, the cap, the guaranteed pair and twenty `RR_Frontier_*` strings were all written
      # for a menu that did not exist. Owner: *"i just never found any other gates with option
      # to walk through"*.
      and "foreach (FloatMenuOption option in FrontierOptions(selPawn)) { yield return option; }"
      in menu_body
      and "private IEnumerable<FloatMenuOption> FrontierOptions(Pawn selPawn)" in gatecomp
      and "NaturalFrontierService.Discover(parent)" in gatecomp,
      "-- the order and the job already walked a pawn to the door and crossed them to the other "
      "map. What was missing was the place a player looks: it was only reachable by selecting "
      "pawns, selecting the door, clicking a gizmo and choosing from a float menu, which is a "
      "dispatch console rather than a door")'''

text = io.open(LINKS, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(LINKS, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("walk-through claim covers the frontier branch")
