"""Keep the stream camera on the crew (owner, 2026-10-09: "KEEP THE FOCUS ON UR PAWNS WEVE BEEN STARIRNG AT NOTHING").

Owner, 2026-10-10, live: "she just endlees clicking a pawn". This used to call rimworld/frame_pawns every 12 s, and
framing SELECTS the pawns -- so every 12 s the crew was re-selected, fighting whatever the owner or Unity had
selected. Now it only moves the camera: every 30 s it jumps to the middle of the crew, never touching the
selection. A fresh fight rect (.claude/.fight.json) still owns the camera; .claude/.camera.json mode "off" stops it.
"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
FIGHT = os.path.join(ROOT, ".claude", ".fight.json")
NOWIN = {"creationflags": 0x08000000} if os.name == "nt" else {}

def bridge(name, args):
    r = subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", name, json.dumps(args)],
                       capture_output=True, text=True, timeout=30, **NOWIN)
    try: return json.loads(r.stdout)
    except Exception: return {}

while True:
    try: f = json.load(open(FIGHT))
    except Exception: f = {}
    try: cam = json.load(open(os.path.join(ROOT, ".claude", ".camera.json")))
    except Exception: cam = {"mode": "crew"}
    try:
        if cam.get("mode") != "off" and not (f.get("rect") and time.time() - f.get("ts", 0) < 90):
            r = bridge("rimworld/list_colonists", {})
            r = r.get("result", r); r = r.get("structuredContent", r) if isinstance(r, dict) else {}
            pos = [c["position"] for c in r.get("colonists", []) if c.get("position")]
            if pos:
                x = round(sum(p["x"] for p in pos) / len(pos)); z = round(sum(p["z"] for p in pos) / len(pos))
                bridge("rimworld/jump_camera_to_cell", {"x": x, "z": z})
    except Exception:
        pass
    time.sleep(30)
