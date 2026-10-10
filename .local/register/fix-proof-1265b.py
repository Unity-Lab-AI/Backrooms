# -*- coding: utf-8 -*-
"""Same three claims, against the real variable names this time.

The first attempt guessed the bindings -- `planner` and `emergence` -- and the files use
`intrusion_body` and `gatecomp`. The anchors refused rather than matching something close, which
is the behaviour that matters.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAYOUT = os.path.join(REPO, ".local", "register", "proof-coordinate-layout.py")
LINKS = os.path.join(REPO, ".local", "register", "proof-gate-links.py")

LAYOUT_EDIT = (
    u'''      "if (room == null || depth <= 1) { yield break; }" in intrusion_body,''',
    u'''      "if (room == null || room.index == 0 || depth <= 1) { yield break; }" in intrusion_body
      # The hall is excluded as well now, for the reason `FalseOpening` excludes it: it is the
      # room the player arrives in and the one meant to read as built.
      and "room.index == 0" in intrusion_body
      # **AND THERE IS MORE THAN ONE FORM NOW.** The probe measured the old shaping running on
      # 89% of depth-1 rooms at 7% of their interior -- so the amount was never the problem and
      # the obvious guess, more reach, would only have made rounder squares. There was exactly
      # ONE form: a quarter-ellipse per corner. Owner: *"they were all just square rooms
      # again..wtf dont u know any other compbinations"*.
      and "internal const int ShapeForms = 7;" in planner
      and "int form = roll % ShapeForms;" in planner,''')

LIT_EDIT = (
    u'''      and "public bool ShouldBeLitNow() { return IsLiveGate; }" in gatecomp,''',
    u'''      and "public bool ShouldBeLitNow() { return IsLiveGate || frontierGate; }" in gatecomp
      # **AND THE NEW CONDITION IS CONFINED TO A COORDINATE.** `NaturalFrontierService.Evaluate`
      # serves ordinary maps under its own `worldfrontier:` origin, so without this a door in an
      # ancient structure on the player's OWN colony map would glow blue on install. This claim
      # refused the change that introduced it, correctly, and is widened rather than relaxed.
      and "parent.Map != null && parent.Map.Parent is RimroomsDestinationMapParent" in gatecomp,''')

WALK_EDIT = (
    u'''      "if (!IsLiveGate) { yield break; }" in gatecomp''',
    u'''      "foreach (FloatMenuOption option in FrontierOptions(selPawn)) { yield return option; }"
      in gatecomp
      # A door that is not a live gate is now asked whether it is an undiscovered way onward
      # before the menu gives up. **`NaturalFrontierService.Discover` had ZERO callers** -- the
      # draw, the cap, the guaranteed pair and twenty `RR_Frontier_*` strings were all written
      # for a menu that did not exist. Owner: *"i just never found any other gates with option to
      # walk through"*.
      and "private IEnumerable<FloatMenuOption> FrontierOptions(Pawn selPawn)" in gatecomp
      and "NaturalFrontierService.Discover(parent)" in gatecomp''')


def apply(path, edits):
    text = io.open(path, encoding="utf-8").read()
    problems = []
    for old, _ in edits:
        if text.count(old) != 1:
            problems.append("%s: %d of %r" % (os.path.basename(path), text.count(old), old[:58]))
    if problems:
        for problem in problems:
            print("ANCHOR PROBLEM: %s" % problem)
        raise SystemExit(1)
    for old, new in edits:
        text = text.replace(old, new, 1)
    io.open(path, "w", encoding="utf-8", newline="").write(text)
    print("updated %s" % os.path.basename(path))


apply(LAYOUT, [LAYOUT_EDIT])
apply(LINKS, [LIT_EDIT, WALK_EDIT])
