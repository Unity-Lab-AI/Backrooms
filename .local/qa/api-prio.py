"""Order a pawn through the in-game context menu, bridge API only (no OS mouse/keyboard -- owner, 2026-10-09:
"you dont fight me for control of tmy computer").

    python .local/qa/api-prio.py PAWN_ID X Z ["option prefix"] [--queue]

No prefix: lists the menu. --queue adds the order after the pawn's current ones (shift)."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
def call(tool, args=None):
    o = subprocess.run([PY, os.path.join(HERE, "bridge.py"), "call", tool, json.dumps(args or {})], capture_output=True, text=True, encoding="utf-8").stdout
    try: return json.loads(o[o.find("{"):])
    except Exception: return {}
args = [a for a in sys.argv[1:] if a != "--queue"]; queue = "--queue" in sys.argv
pid, x, z = args[0], int(args[1]), int(args[2]); pre = args[3] if len(args) > 3 else None
if not queue: call("rimworld/clear_selection")
call("rimworld/select_pawn", {"pawnId": pid})
call("rimworld/right_click_cell", {"x": x, "z": z, **({"modifiers": "shift"} if queue else {})})
opts = call("rimworld/get_context_menu_options")
labels = []
def walk(n):
    if isinstance(n, dict):
        if "label" in n and ("index" in n or "optionIndex" in n or "disabled" in n): labels.append(n)
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(opts)
if not pre:
    for o in labels: print(o.get("label"))
else:
    hit = next((o for o in labels if (o.get("label") or "").startswith(pre)), None)
    if not hit: print("no entry", pre, [o.get("label") for o in labels][:8]); call("rimworld/close_context_menu")
    else:
        r = call("rimworld/execute_context_menu_option", {"label": hit["label"]})
        print("done:", hit["label"], r.get("success"))
