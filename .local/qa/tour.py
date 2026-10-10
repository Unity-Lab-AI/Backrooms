"""Base tour for the stream: draft a pawn, run waypoints, camera locked on it, a line at each stop.
    python .local/qa/tour.py [Pawn]"""
import json, subprocess, sys, time
BR = ".local/qa/bridge.py"
PAWN = sys.argv[1] if len(sys.argv) > 1 else "Unity"
def call(tool, args=None):
    o = subprocess.run([sys.executable, BR, "call", tool, json.dumps(args or {})], capture_output=True, text=True).stdout
    return json.loads(o[o.find("{"):]) if "{" in o else {}
def say(t):
    subprocess.run([sys.executable, ".claude/tools/unity-say.py", t], capture_output=True)
def pos():
    r = subprocess.run([sys.executable, BR, "call", "rimworld/list_colonists", "{}"], capture_output=True, text=True).stdout
    i = r.find('"name": "%s"' % PAWN); seg = r[i:i + 4000]
    import re
    m = re.search(r'"position": \{\s*"x": (\d+),\s*"z": (\d+)', seg)
    return (int(m.group(1)), int(m.group(2))) if m else None
STOPS = [
    ((150, 68), "Tour time, chat! I am running the whole wall of Marble Hollow. We start at the main gate, the only way in, flanked by two bastions."),
    ((114, 68), "Southwest corner bastion. Seven by seven, embrasures on both outer faces, so anything hugging the wall gets shot from the side."),
    ((114, 85), "On our right, the bedroom block and the old storehouse, the first thing we built after the crash."),
    ((114, 100), "West wall. Inside is Hotel Gloom, three marble guest rooms, twenty silver a night."),
    ((114, 120), "The hospital, sterile tile, hospital beds, a vitals monitor beside every bed."),
    ((130, 132), "North side. Behind us the new bedrooms, and over there Alfonzoid and Rev's gardens are down south. Stee's potato fields sit outside the north wall."),
    ((150, 116), "The centre of the city. The throne hall for God Almighty Gee, and the altar room beside it."),
    ((166, 116), "And this is the big one. The gate complex. Airlocks, shooting galleries, ballistic glass. When the console research lands, we open a door into the Backrooms right here."),
    ((188, 132), "Northeast corner bastion. Every corner and every long wall has one."),
    ((186, 104), "East side, the prison. Reaper the minstrel lives here now, and behind the security hall, the dissection room."),
    ((186, 88), "The warehouse, the freezer we call Alfonzoid's Morgue, and the power yard going in next door."),
    ((150, 68), "And we are back at the gate. That is Marble Hollow, chat. A goth city built from the ground up, and we are just getting started."),
]
call("rimworld/set_draft", {"pawnName": PAWN, "drafted": True})
call("rimworld/set_camera_zoom", {"zoomRange": "Close"})
for (x, z), line in STOPS:
    call("rimworld/select_pawn", {"pawnName": PAWN})
    call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
    call("rimworld/right_click_cell", {"x": x, "z": z})
    for _ in range(40):
        call("rimworld/jump_camera_to_pawn", {"pawnName": PAWN})
        call("rimworld/play_for", {"durationMs": 1200, "speed": "Normal"})
        p = pos()
        if p and abs(p[0] - x) <= 2 and abs(p[1] - z) <= 2:
            break
    call("rimworld/pause_game")
    call("rimworld/jump_camera_to_pawn", {"pawnName": PAWN})
    say(line)
    print("stop", x, z, "reached", pos())
call("rimworld/set_draft", {"pawnName": PAWN, "drafted": False})
print("tour done")
