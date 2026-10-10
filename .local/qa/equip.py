"""Equip a pawn with the weapon on a cell: python .local/qa/equip.py "<pawn>" X Z [pawnId]
Selects the pawn, opens the right-click menu on the cell and runs the option starting with "Equip"."""
import json, subprocess, sys
def call(t, a):
    o = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", t, json.dumps(a)], capture_output=True, text=True, encoding="utf-8").stdout
    return json.loads(o[o.find("{"):]) if "{" in o else {}
name, x, z = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
sel = {"pawnName": name}
if len(sys.argv) > 4: sel["pawnId"] = sys.argv[4]
call("rimworld/select_pawn", sel)
call("rimworld/open_context_menu", {"x": x, "z": z})
opts = call("rimworld/get_context_menu_options", {})
labels = []
def walk(n):
    if isinstance(n, dict):
        if "label" in n and ("index" in n or "optionIndex" in n): labels.append(n)
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(opts)
pick = next((o for o in labels if str(o.get("label", "")).startswith("Equip")), None)
if not pick:
    call("rimworld/close_context_menu", {}); raise SystemExit("no Equip option: %s" % [o.get("label") for o in labels])
r = call("rimworld/execute_context_menu_option", {"optionIndex": pick.get("index", pick.get("optionIndex"))})
print(name, "->", pick["label"], r.get("success"))
