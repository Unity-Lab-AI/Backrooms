"""Webcam panel director (owner, 2026-10-09: "leave the profile pic of ur up more and the slide show highlights
just intermittently for liek 20 second max so it settle on a new you doing things").

A highlight (unity-snap / unity-glance) marks .claude/.cam-highlight.json; ~20 s later this puts a NEW picture of
Unity back up, her expression matched to what the crew is doing (a fight -> scared/angry, building -> focus,
idle -> chill...). Runs in the background."""
import json, os, random, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
HL = os.path.join(ROOT, ".claude", ".cam-highlight.json"); FIGHT = os.path.join(ROOT, ".claude", ".fight.json")
CAM = os.path.join(ROOT, ".claude", "tools", "unity-cam.py")
def mood():
    try:
        if time.time() - json.load(open(FIGHT)).get("ts", 0) < 90: return random.choice(["scared", "angry", "hype"]), "fighting for the camp"
    except Exception: pass
    try:
        o = subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", "rimworld/list_colonists", "{}"],
                           capture_output=True, text=True, timeout=30).stdout
        jobs = " ".join(c.get("job") or "" for c in json.loads(o[o.find("{"):]).get("colonists", []))
    except Exception: jobs = ""
    if any(k in jobs for k in ("Frame", "Construct", "Mine", "Build")): return "focus", "building the camp"
    if any(k in jobs for k in ("Hunt",)): return "smug", "out hunting"
    if any(k in jobs for k in ("LayDown",)): return "chill", "everyone napping"
    return random.choice(["chill", "laugh", "smug", "focus"]), "running the colony"
done = 0.0
while True:
    try: ts = json.load(open(HL)).get("ts", 0)
    except Exception: ts = 0
    # owner: "cpu is burning at 99% ... gigs on gpu are nearly pegged". Every spoken line marks a highlight, and this
    # used to render a NEW Stable Diffusion face ~20 s after each one (about 3 renders a minute). Now a fresh face is
    # rendered at most every 4 minutes; in between nothing is generated at all.
    if ts > done and time.time() - ts >= 20 and time.time() - done >= 240:
        m, cap = mood(); subprocess.run([sys.executable, CAM, m, cap]); done = time.time()
        print("unity back up:", m, cap, flush=True)
    time.sleep(10)
