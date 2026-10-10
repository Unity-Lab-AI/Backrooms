"""Shift-queue 'Prioritize hauling' on a list of cells for one pawn.
    python .local/qa/queue-haul.py <pawn> "x,z x,z ..."
"""
import json, subprocess, sys
BR = ".local/qa/bridge.py"
def call(tool, args):
    out = subprocess.run([sys.executable, BR, "call", tool, json.dumps(args)], capture_output=True, text=True).stdout
    return json.loads(out[out.find("{"):]) if "{" in out else {}
pawn = sys.argv[1]; ok = 0
call("rimworld/select_pawn", {"pawnName": pawn})
for c in sys.argv[2].split():
    x, z = map(int, c.split(","))
    call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
    m = call("rimworld/open_context_menu", {"x": x, "z": z, "modifiers": "shift"})
    opt = next((o for o in m.get("options", []) if o.get("label", "").startswith("Prioritize hauling") and not o.get("disabled")), None)
    if opt:
        r = call("rimworld/execute_context_menu_option", {"menuId": m["menuId"], "optionIndex": opt["index"]})
        ok += bool(r.get("success"))
    else:
        call("rimworld/close_context_menu", {})
        print("no haul option at", x, z, [o.get("label") for o in m.get("options", [])][:3])
print(pawn, "queued", ok)
