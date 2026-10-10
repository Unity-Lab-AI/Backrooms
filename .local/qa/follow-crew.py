"""Keep the stream camera on the crew (owner, 2026-10-09: "KEEP THE FOCUS ON UR PAWNS WEVE BEEN STARIRNG AT NOTHING").
Every 12 s frames the three colonists, unless a fresh fight rect (.claude/.fight.json) owns the camera."""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
FIGHT = os.path.join(ROOT, ".claude", ".fight.json")
while True:
    try: f = json.load(open(FIGHT))
    except Exception: f = {}
    try: cam = json.load(open(os.path.join(ROOT, ".claude", ".camera.json")))
    except Exception: cam = {"mode": "crew"}
    if cam.get("mode") != "off" and not (f.get("rect") and time.time() - f.get("ts", 0) < 90):
        subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", "rimworld/frame_pawns",
                        json.dumps({"pawnNames": cam.get("pawns") or ["Unity", "Gee", "Scar"]})], capture_output=True)
    time.sleep(12)
