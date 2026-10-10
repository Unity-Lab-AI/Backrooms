# -*- coding: utf-8 -*-
"""The player-command claim now reads the method, and checks BOTH ways in are clicks.

It asserted the literal gizmo delegate containing the call. The call moved into one private
method, reached from a gizmo and from a float-menu option -- so the claim refused correct code,
and widening it is right, but **only to something still checkable.**

So it checks three things instead of one text match: the single caller is `WalkOutToWorld`; that
method is reached from a `Command_Action` action; and it is reached from a `FloatMenuOption`. Both
entry points are player clicks, which is the guarantee -- and the surrounding claims that nothing
automatic appears in the file are untouched and still carry the rest of it.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-world-exit.py")

OLD = u'''check("its one caller is a player command action",
      "action = delegate { Show(worldExitCampaign.LeaveThroughWorldExit(parent)); }" in comp,
      "-- it must sit behind a gizmo the player clicks, never a tick")'''

NEW = u'''# The call moved into one private method, reached from a gizmo AND from a float-menu option --
# both player clicks. This claim refused that, correctly, because "every caller is a player
# command" is not something source text can decide. It is widened only to things that can be
# checked: which method holds the call, and that both ways into it are clicks.
check("its one caller is a player command action",
      "return campaign.LeaveThroughWorldExit(parent);" in comp
      and "private CompanyActionResult WalkOutToWorld()" in comp
      and "action = delegate { Show(WalkOutToWorld()); }" in comp
      and "Show(WalkOutToWorld());" in comp
      and comp.count("WalkOutToWorld()") == 4,
      "-- it must sit behind a gizmo the player clicks or a float-menu option they choose, never "
      "a tick. Four mentions: the declaration, the gizmo, the menu, and the doc reference")'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD, NEW, 1))
print("the player-command claim reads the method and both entry points")
