# -*- coding: utf-8 -*-
"""Three claims refused this checkpoint, and one of them caught a real regression.

* **"NO OTHER DOOR IN THE GAME IS AFFECTED"** pinned `ShouldBeLitNow() { return IsLiveGate; }`.
  Lighting an undiscovered way onward made that false -- and the claim was right to refuse,
  because `NaturalFrontierService.Evaluate` serves **ordinary maps too**, under its own
  `worldfrontier:` origin. A door in an ancient structure on the player's own colony map would
  have started glowing blue the moment this mod was installed, which
  `CONTENT_REUSE_POLICY.md` forbids outright. `IsFrontierGate` is now gated on the map being a
  coordinate. **The claim earned its keep; it is widened to cover the new condition rather than
  relaxed.**

* **"SHALLOW COORDINATES STAY RECTANGULAR"** and **"RIGHT-CLICK THE GATE ... AND WALK THROUGH
  IT"** both pinned literal lines that gained a clause. The intent of each still holds and the
  text moved, so each claim keeps its original assertion and adds the new one.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAYOUT = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")
LINKS = os.path.join(REPO, ".local", "register", "proof-gate-links.py")

LAYOUT_OLD = u'''      "if (room == null || depth <= 1) { yield break; }" in planner'''
LAYOUT_NEW = u'''      "if (room == null || room.index == 0 || depth <= 1) { yield break; }" in planner
      # The hall is excluded as well now, for the reason `FalseOpening` excludes it: it is the
      # room the player arrives in and the one meant to read as built.
      and "room.index == 0" in planner'''

LIT_OLD = u'''      "public bool ShouldBeLitNow() { return IsLiveGate; }" in emergence'''
LIT_NEW = u'''      "public bool ShouldBeLitNow() { return IsLiveGate || frontierGate; }" in emergence
      # **AND THE NEW CONDITION IS CONFINED TO A COORDINATE.** `Evaluate` serves ordinary maps
      # under its own `worldfrontier:` origin, so without this a door in an ancient structure on
      # the player's own colony map would glow blue on install. This claim refused the change
      # that introduced it, correctly, and is widened rather than relaxed.
      and "parent.Map != null && parent.Map.Parent is RimroomsDestinationMapParent" in emergence'''

WALK_OLD = u'''      "if (!IsLiveGate) { yield break; }" in emergence'''
WALK_NEW = u'''      "foreach (FloatMenuOption option in FrontierOptions(selPawn)) { yield return option; }"
      in emergence
      # A door that is not a live gate is now asked whether it is an undiscovered way onward
      # before the menu gives up, which is the whole of the owner's *"i just never found any
      # other gates with option to \\"walk through\\""*.
      and "private IEnumerable<FloatMenuOption> FrontierOptions(Pawn selPawn)" in emergence
      and "NaturalFrontierService.Discover(parent)" in emergence'''

for path, edits in [(LAYOUT, [(LAYOUT_OLD, LAYOUT_NEW)]),
                    (LINKS, [(LIT_OLD, LIT_NEW), (WALK_OLD, WALK_NEW)])]:
    text = io.open(path, encoding="utf-8").read()
    problems = []
    for old, _ in edits:
        if text.count(old) != 1:
            problems.append("%s: %d of %r" % (os.path.basename(path), text.count(old), old[:60]))
    if problems:
        for problem in problems:
            print("ANCHOR PROBLEM: %s" % problem)
        raise SystemExit(1)
    for old, new in edits:
        text = text.replace(old, new, 1)
    io.open(path, "w", encoding="utf-8", newline="").write(text)
    print("updated %s" % os.path.basename(path))
