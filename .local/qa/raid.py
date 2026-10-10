"""Raid drill for Marble Hollow, the same way every time.

    python .local/qa/raid.py block              draft every gun into the mid-base block, kids into the hall
    python .local/qa/raid.py block X Z          the same block, centred on X Z (a spot that SEES them)
    python .local/qa/raid.py down               undraft everyone

Owner: "set everyone to attack not flee and group up when something attacks and draft and flee attack
never letting someone melle person or animal get close to your pawns kill them with range at all costs".
Lessons (docs/PLAYSCRIPT.md): place at the letter, stand still, never walk toward them; the block
needs sight lines; re-send any order that did not take; the children go inside, never left outside.
"""
import json, subprocess, sys, time

GUNS = ["Thing_Human486", "Thing_Human504", "Thing_Human495",
        "Thing_Human48974", "Thing_Human58758", "Thing_CreepJoiner46497",
        "Thing_Human68406", "Thing_Human68414", "Thing_Human68421"]   # Rev and Alfonzoid died; Selena, Skissor, Val hired 2026-10-08
KIDS = {}   # both children died 2026-10-08
BLOCK = (105, 103)                                                        # faces the open west sand
OFFS = [(0, -3), (1, -2), (0, -1), (1, 0), (0, 1), (1, 2), (0, 3), (1, 4), (0, 5)]


def call(t, a=None):
    o = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", t, json.dumps(a or {})],
                       capture_output=True, text=True, encoding="utf-8").stdout
    return json.loads(o[o.find("{"):]) if "{" in o else {}


def order(pid, x, z):
    call("rimworld/clear_selection"); call("rimworld/select_pawn", {"pawnId": pid})
    call("rimworld/right_click_cell", {"x": x, "z": z})


def block(cx, cz):
    want = {p: (cx + dx, cz + dz) for p, (dx, dz) in zip(GUNS, OFFS)}
    want.update(KIDS)
    for p in want: call("rimworld/set_draft", {"pawnId": p, "drafted": True})
    for p, (x, z) in want.items(): order(p, x, z)
    call("rimworld/clear_selection")
    # orders given to a pawn asleep or mid-job do not always take: check and re-send once
    call("rimworld/play_for", {"durationMs": 1500, "speed": "Normal"})
    cols = {c["pawnId"]: c for c in call("rimworld/list_colonists").get("colonists", [])}
    redo = [p for p, (x, z) in want.items() if p in cols and cols[p].get("job") == "Wait_Combat"
            and abs(cols[p]["position"]["x"] - x) + abs(cols[p]["position"]["z"] - z) > 2]
    for p in redo: order(p, *want[p])
    call("rimworld/clear_selection")
    print("block at", (cx, cz), "| re-sent:", [cols[p]["name"] for p in redo] or "-")


def down():
    for p in GUNS + list(KIDS): call("rimworld/set_draft", {"pawnId": p, "drafted": False})
    print("stood down")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "block": block(*(map(int, a[1:3]) if len(a) >= 3 else BLOCK))
    elif a and a[0] == "down": down()
    else: print(__doc__)
