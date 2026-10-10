"""Stream camera: show what Unity is DOING, zoomed in -- the crew only when she is idle.

Owner, 2026-10-09: "KEEP THE FOCUS ON UR PAWNS WEVE BEEN STARIRNG AT NOTHING".
Owner, 2026-10-10, live: "she just endlees clicking a pawn" -- so this never selects anything, it only moves the camera.
Owner, 2026-10-10, live: "is she ever gonna stop keeeping the pawns in view and use screen image capture and zoomed
highlighting" -- so when she acts on a spot on the map (a stockpile, a bill, a build, a designation, any tool call
with x/z), the camera frames that spot zoomed in for a while; only when she has not touched the map for a minute does
it drift back to the middle of the crew.

Priority: a fresh fight rect (.claude/.fight.json) > her latest map action (from the player's log) > the crew.
.claude/.camera.json mode "off" stops it.
"""
import json, os, re, subprocess, sys, time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
FIGHT = os.path.join(ROOT, ".claude", ".fight.json")
PLAYER_LOG = os.path.join(HERE, "_svc_autopilot.log")
NOWIN = {"creationflags": 0x08000000} if os.name == "nt" else {}
ACTION_HOLD = 60          # seconds the camera stays on her latest action before drifting back to the crew
TOOL_LINE = re.compile(r"^(\d\d:\d\d:\d\d) TOOL (\S+) (\{.*\})\s*$")


def bridge(name, args):
    r = subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", name, json.dumps(args)],
                       capture_output=True, text=True, timeout=30, **NOWIN)
    try: return json.loads(r.stdout)
    except Exception: return {}


def latest_action():
    """(x, z, w, h, age_s) of her newest tool call that names a map spot, or None."""
    try:
        with open(PLAYER_LOG, "rb") as f:
            f.seek(max(0, os.path.getsize(PLAYER_LOG) - 40000))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return None
    now = datetime.now()
    for ln in reversed(lines):
        m = TOOL_LINE.match(ln)
        if not m:
            continue
        try:
            a = json.loads(m.group(3))
        except Exception:
            continue
        if not isinstance(a, dict) or "x" not in a or "z" not in a:
            continue
        t = datetime.combine(now.date(), datetime.strptime(m.group(1), "%H:%M:%S").time())
        age = (now - t).total_seconds()
        if age < 0:
            age += 86400
        w = int(a.get("width") or 1); h = int(a.get("height") or 1)
        return int(a["x"]), int(a["z"]), max(1, w), max(1, h), age
    return None


def latest_pawn():
    """The pawn named in her newest tool call (priorities, assign, orders), if it was in the last minute."""
    try:
        with open(PLAYER_LOG, "rb") as f:
            f.seek(max(0, os.path.getsize(PLAYER_LOG) - 20000))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return None
    now = datetime.now()
    for ln in reversed(lines):
        m = TOOL_LINE.match(ln)
        if not m:
            continue
        t = datetime.combine(now.date(), datetime.strptime(m.group(1), "%H:%M:%S").time())
        if (now - t).total_seconds() > ACTION_HOLD:
            return None
        try:
            a = json.loads(m.group(3))
        except Exception:
            continue
        if isinstance(a, dict) and a.get("pawn"):
            return a["pawn"]
    return None


turn = 0
last_framed = None
while True:
    try: f = json.load(open(FIGHT))
    except Exception: f = {}
    try: cam = json.load(open(os.path.join(ROOT, ".claude", ".camera.json")))
    except Exception: cam = {"mode": "crew"}
    try:
        if cam.get("mode") != "off" and not (f.get("rect") and time.time() - f.get("ts", 0) < 90):
            act = latest_action()
            if act and act[4] < ACTION_HOLD:
                x, z, w, h, _ = act
                if last_framed != (x, z, w, h):
                    # zoomed on the spot she is working, a few cells of context around it
                    bridge("rimworld/frame_cell_rect", {"x": x, "z": z, "width": w, "height": h, "paddingCells": 6})
                    last_framed = (x, z, w, h)
            else:
                last_framed = None
                # a real pawn, one at a time -- the middle of the crew was often bare dirt between them
                # (owner: "she is stuck looking at dirt"); the pawn she just worked on goes first
                r = bridge("rimworld/list_colonists", {})
                r = r.get("result", r); r = r.get("structuredContent", r) if isinstance(r, dict) else {}
                names = [c.get("name") for c in r.get("colonists", []) if c.get("factionIsPlayer", True) and c.get("name")]
                focus = latest_pawn()
                if focus in names:
                    names.remove(focus); names.insert(0, focus)
                if names:
                    turn = (turn + 1) % len(names) if focus not in names[:1] or turn else 0
                    bridge("rimworld/jump_camera_to_pawn", {"pawnName": names[turn % len(names)]})
    except Exception:
        pass
    time.sleep(5 if last_framed else 30)
