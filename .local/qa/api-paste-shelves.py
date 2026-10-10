"""Copy a shelf's storage settings and paste them onto other shelves -- bridge gizmos only, no mouse.
    python .local/qa/api-paste-shelves.py SRC_X SRC_Z [--exclude x0,z0,x1,z1] [--only x0,z0,x1,z1]   (pastes onto every built shelf in the base)"""
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
def call(tool, args=None):
    o = subprocess.run([PY, os.path.join(HERE, "bridge.py"), "call", tool, json.dumps(args or {})], capture_output=True, text=True, encoding="utf-8").stdout
    try: return json.loads(o[o.find("{"):])
    except Exception: return {}
def gizmo(label):
    g = call("rimworld/list_selected_gizmos")
    ids = re.findall(r'"id": "(selection-gizmo:[^"]+)",\s*"label": "%s"' % re.escape(label), json.dumps(g, indent=1))
    if not ids:
        flat = json.dumps(g); m = re.search(r'"id": "(selection-gizmo:[^"]+)"[^{}]*?"label": "%s"' % re.escape(label), flat)
        ids = [m.group(1)] if m else []
    if not ids: return False
    return call("rimworld/execute_gizmo", {"gizmoId": ids[0]}).get("success")
sx, sz = int(sys.argv[1]), int(sys.argv[2])
ex = tuple(map(int, sys.argv[sys.argv.index("--exclude") + 1].split(","))) if "--exclude" in sys.argv else None
only = tuple(map(int, sys.argv[sys.argv.index("--only") + 1].split(","))) if "--only" in sys.argv else None
# warn the viewers first: a run of selections clicks and flickers (owner, 2026-10-09: "sounds spammy, warn
# viewers for shit before like that")
subprocess.run([PY, os.path.join(os.path.dirname(os.path.dirname(HERE)), ".claude", "tools", "unity-say.py"), "--wait", "--raw",
                "Heads up, chat: I'm about to click through a stack of shelves to set them all at once. Expect a minute of clicky noises and flickering boxes. Totally on purpose."], capture_output=True)
call("rimworld/clear_selection"); call("rimworld/click_cell", {"x": sx, "z": sz})
print("copy", gizmo("Copy settings"))
o = subprocess.run([PY, os.path.join(HERE, "find-things.py"), "Shelf", "95", "55", "205", "148"], capture_output=True, text=True, env=dict(os.environ, ALL="1")).stdout
cells = []
for line in o.splitlines():
    if line.split(" ")[0] in ("Shelf", "ShelfSmall"):
        cells += [tuple(map(int, m)) for m in re.findall(r"\((\d+), (\d+)\)", line)]
done = 0
for x, z in cells:
    if ex and ex[0] <= x <= ex[2] and ex[1] <= z <= ex[3]: continue
    if only and not (only[0] <= x <= only[2] and only[1] <= z <= only[3]): continue
    if (x, z) == (sx, sz): continue
    call("rimworld/clear_selection"); call("rimworld/click_cell", {"x": x, "z": z})
    if gizmo("Paste settings"): done += 1
    time.sleep(0.6)   # a burst of selections flickers on the stream (owner, 2026-10-09: "u are clicking a million times in a row and it looked weird on steeam")
call("rimworld/clear_selection")
print("pasted on", done, "shelf cells")
