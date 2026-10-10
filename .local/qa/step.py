"""Step the game in short slices for raids and builds -- with a stream beat every slice.

    python .local/qa/step.py N [Normal|Fast|Superfast] [--hostiles]

Replaces bare `bridge.py call rimworld/play_for` loops, which moved the game in silence (owner,
2026-10-09: "iots so fucking quiet..."). Stops early on a modal dialog (a bare loop once stepped
past a pirate fee demand and froze the clock). --hostiles prints live non-colonist positions each slice.
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
n = int(sys.argv[1]); speed = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "Normal"


def call(tool, args=None):
    o = subprocess.run([PY, os.path.join(HERE, "bridge.py"), "call", tool, json.dumps(args or {})],
                       capture_output=True, text=True, encoding="utf-8").stdout
    try: return json.loads(o[o.find("{"):])
    except Exception: return {}


for i in range(n):
    call("rimworld/play_for", {"durationMs": 3000, "speed": speed})
    ui = call("rimworld/get_ui_state")
    if ui.get("nonImmediateDialogWindowOpen"):
        print(i + 1, "STOP modal:", ui.get("focusedWindowType")); break
    subprocess.run([PY, os.path.join(HERE, "stream-beat.py")], capture_output=True)
    if "--hostiles" in sys.argv:
        out = subprocess.run([PY, os.path.join(HERE, "live-hostiles.py")], capture_output=True, text=True).stdout.strip()
        print(i + 1, out)
        # keep the viewers on the fight (owner, 2026-10-09: "i mean keep the viewer able to see the action" /
        # "the view port is no where near the action"): frame hostiles + drafted colonists every slice
        import ast
        try: pts = list(ast.literal_eval(out or "[]"))
        except Exception: pts = []
        pts += [(c["position"]["x"], c["position"]["z"]) for c in call("rimworld/list_colonists").get("colonists", []) if c.get("drafted")]
        if pts:
            xs = [p[0] for p in pts]; zs = [p[1] for p in pts]
            rect = {"x": min(xs) - 3, "z": min(zs) - 3, "width": max(xs) - min(xs) + 7, "height": max(zs) - min(zs) + 7}
            call("rimworld/frame_cell_rect", rect)
            # unity-snap.py reads this so its shot hands the camera back to the fight, not to Unity's pawn
            import time
            json.dump({"ts": time.time(), "rect": rect}, open(os.path.join(os.path.dirname(os.path.dirname(HERE)), ".claude", ".fight.json"), "w"))
