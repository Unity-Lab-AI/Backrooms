"""Try to break the gate table before the game does. Synthetic states in, expected gate out.

Written 2026-10-09 after the first version of the table shipped with two real faults: a gate could fire on a
condition nobody measured (a missing key read as false, so a frozen game routed to work-priorities), and a
heat wave lost to generic letter reading because a heat wave IS a letter -- the gate that kills the colony in
three minutes was being answered with "read your letters".

    python .local/autopilot/test/gate-routing.py
"""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
AP = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("g", os.path.join(AP, "gates.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

BASE = dict(ticks_moving=True, dialog_open=False, letters=0, letter_labels=[], alerts=[], crew=[],
            meals=5, raw_food=20, wood=200, medicine=5, blueprints=0, humanlikes_not_ours=0,
            store_roofed_fraction=1.0, hostiles_on_map=0, wall_gaps=0, game_foreground=True,
            days_of_food=6.0)      # a fed colony by default; the famine case overrides it

CASES = [
    ("a pop-up is open",            dict(dialog_open=True),                                      "dialog-open"),
    ("raiders are on the map",      dict(hostiles_on_map=4, letters=1, letter_labels=["Raid: pirates"]), "hostile-on-map"),
    ("a caravan, not a raid",       dict(humanlikes_not_ours=12, letters=1, letter_labels=["Mining goods trader"]), "letter-unread"),
    ("nobody has eaten",            dict(meals=0, raw_food=1, days_of_food=0.2),                 "pawn-starving"),
    ("the store has no roof",       dict(store_roofed_fraction=0.1),                             "food-rotting-or-no-cold"),
    ("a hole in the wall",          dict(wall_gaps=7),                                           "perimeter-hole"),
    ("no medicine at all",          dict(medicine=0),                                            "no-medicine"),
    ("a heat wave letter",          dict(letters=1, letter_labels=["Heat wave"]),                 "heat-wave"),
    ("the game is frozen",          dict(ticks_moving=False),                                    "game-paused"),
    ("a click with no focus",       dict(game_foreground=False, wants_click=True),               "window-not-in-front"),
    ("fed and stocked -> climb",    dict(),                                                      "rung-2-power-and-cold"),
    ("nothing to do at all",        dict(days_of_food=0.5, medicine=0, meals=0, raw_food=1),     "pawn-starving"),
]

fails = []
for name, patch, expect in CASES:
    st = dict(BASE); st.update(patch)
    gates, _ = g.decide(st)
    got = gates[0]["id"] if gates else "none"
    print(("PASS " if got == expect else "FAIL ") + name.ljust(26), "->", got,
          "" if got == expect else "(wanted %s)" % expect)
    if got != expect: fails.append(name)
print("\n%d/%d gate routings correct" % (len(CASES) - len(fails), len(CASES)))
sys.exit(1 if fails else 0)
