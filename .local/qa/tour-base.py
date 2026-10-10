"""Base tour for the stream: frame each facility, post a ringed + labelled shot, say a line about it.
Owner/chat, 2026-10-09: "giveeverone a view of the basefacilitys with prompt images highlights". Bridge only."""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); PY = sys.executable
TOOLS = os.path.join(ROOT, ".claude", "tools")
def call(tool, args): subprocess.run([PY, os.path.join(HERE, "bridge.py"), "call", tool, json.dumps(args)], capture_output=True)
STOPS = [
 ((158, 80, 18, 21), "The freezer and the new morgue",
  ["166,90,Freezer: food, plants, herbs", "166,96,Morgue (own cold room)", "164,82,Cooler", "172,88,Cooler"],
  "Stop one, chat: the freezer. Fourteen degrees, every food, plant and herb lives here. The top strip is our brand new morgue, walled off with its own coolers, so the bodies never touch dinner."),
 ((150, 81, 12, 18), "Dry storage",
  ["156,90,Dry storage shelves", "153,95,Trade beacon"],
  "Stop two: dry storage. Shelves stacked two deep, a trade beacon so traders can see everything, and no food allowed. Very organized. Very goth."),
 ((170, 72, 21, 13), "Storage hall and the vault",
  ["177,78,Storage hall", "185,76,Vault", "176,82,Cooler"],
  "Stop three: the big storage hall, with a vault in the back corner for silver and gold. Climate controlled, because even our loot deserves comfort."),
 ((113, 63, 30, 18), "Power yard and solar field",
  ["127,68,Utility generators", "128,71,Wood generators", "131,77,Solar field", "150,72,Mortar", "160,72,Mortar"],
  "Stop four: the power yard. Generators lined up in rows, the solar field behind them, and two mortar pits going in so we can shell anything that knocks."),
 ((110, 129, 45, 9), "North fields",
  ["119,133,Cotton", "135,133,Psychoid", "148,133,Hops"],
  "Stop five: the north fields. Cotton for cloth, psychoid for the expensive stuff, hops for beer. Cash crops of every kind, as chat demanded."),
 ((109, 115, 20, 11), "Hospital",
  ["118,120,Hospital beds", "119,123,Trade beacon", "112,123,Medicine shelf"],
  "Stop six: the hospital, now for colonists instead of prisoners. Gee says hi, he's still in bed."),
 ((141, 97, 18, 13), "Throne room",
  ["150,107,Throne", "148,107,Speaker", "152,107,Speaker"],
  "Stop seven: the throne room. Six speakers going in for proper parties, and the effigy's been moved outside where it can burn safely."),
 ((119, 56, 12, 10), "A gun tower",
  ["124,61,Embrasure tower", "124,60,Exit door"],
  "Last stop: one of our eighteen gun towers. Embrasures to shoot through, a lamp so the snipers can see, and a marble exit door for sallying out. Come at us."),
]
for (x, z, w, h), cap, marks, line in STOPS:
    call("rimworld/frame_cell_rect", {"x": x, "z": z, "width": w, "height": h}); time.sleep(0.6)
    args = [PY, os.path.join(TOOLS, "unity-glance.py"), cap]
    for m in marks: args += ["--mark", m]
    subprocess.run(args, capture_output=True)
    subprocess.run([PY, os.path.join(TOOLS, "unity-say.py"), "--wait", "--raw", line], capture_output=True, env=dict(os.environ, UNITY_NO_GLANCE="1"))
    print("stop:", cap)
