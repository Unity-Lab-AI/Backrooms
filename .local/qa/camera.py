"""Camera follow switch (owner, 2026-10-09: "wtf do u need a fololow pawn script u can turn on and off").

    python .local/qa/camera.py crew          # follow Unity, Gee, Scar (default)
    python .local/qa/camera.py pawn Unity    # follow one pawn
    python .local/qa/camera.py off           # stop following (to show something else)
    python .local/qa/camera.py status

follow-crew.py reads .claude/.camera.json every tick; a fresh fight rect (.claude/.fight.json) always wins."""
import json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, ".claude", ".camera.json")
a = sys.argv[1:] or ["status"]
if a[0] == "status":
    print(open(P).read() if os.path.exists(P) else '{"mode": "crew"}'); sys.exit()
mode = {"mode": a[0], "pawns": a[1:] if a[0] == "pawn" else ["Unity", "Gee", "Scar"], "ts": int(time.time())}
json.dump(mode, open(P, "w")); print("camera", mode["mode"], " ".join(mode["pawns"]) if mode["mode"] != "off" else "")
