"""Dead-air guard for the stream: if Unity has said nothing for a while, she says something.

    python .claude/tools/dead-air.py [quiet_seconds]      # default 40; runs until killed

Owner, 2026-10-08: "comeone told me it too quiet too much dead air". The long silences are the
stretches where Unity is reading code or saves between game actions. This watches the studio
outbox (every spoken line lands there via unity-say.py); after QUIET seconds with no Unity line
it speaks one built from the live game -- a colonist spotlight, the weather and date, what is
being built -- or a question for chat. Never repeats a line it said in the last 30.

Stream-clean by construction (LAW: THE STREAM IS CLEAN): every line is a fixed clean template
filled with colonist names, job words and game state. Chat text is never read back out loud.
"""
import json, os, random, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUTBOX = os.path.join(HERE, "..", ".studio-outbox.jsonl")
BRIDGE = os.path.join(ROOT, ".local", "qa", "bridge.py")
QUIET = int(sys.argv[1]) if len(sys.argv) > 1 else 40

JOBS = {
    "LayDown": "taking a nap", "Wait_Wander": "wandering around", "Wait": "standing around",
    "Goto": "walking somewhere important", "HaulToCell": "hauling stuff", "HaulToContainer": "hauling stuff",
    "FrameConstruct": "building", "FinishFrame": "finishing a build", "PlaceNoCostFrame": "building",
    "Deconstruct": "tearing something down", "Mine": "mining", "Research": "doing research",
    "DoBill": "working at a bench", "Sow": "planting", "Harvest": "harvesting", "CutPlant": "cutting plants",
    "Ingest": "eating", "SocialRelax": "chilling with friends", "Play_Horseshoes": "playing horseshoes",
    "Play_Chess": "playing chess", "Play_Billiards": "playing pool", "Meditate": "meditating",
    "Clean": "cleaning", "Repair": "repairing things", "TendPatient": "doctoring someone",
    "Hunt": "hunting", "Refuel": "refuelling a generator", "Smooth": "smoothing stone", "Pray": "praying",
    "StandAndBeSociallyActive": "socialising", "Lovin": "having private time",
}
SPOT = [
    "Quick check on {name}: {job}. Honestly, relatable.",
    "Colonist spotlight: {name} is {job}. Give it up for {name}, chat.",
    "Meanwhile {name} is over there {job}. Living the Marble Hollow dream.",
    "{name} is {job}. If you want {name} doing something else, tell me in chat.",
    "Just so you know, {name} is {job}. Productivity report: questionable.",
]
WORLD = [
    "It is {date}. Marble Hollow is still standing, which I count as a win.",
    "Weather report: {weather}, {temp}. Perfect goth weather, if you ask me.",
    "{count} colonists in Marble Hollow right now. That is a lot of mouths and a lot of marble.",
]
ASK = [
    "Chat, quick vote: drug lab, rec room, or a royal wing for Gee? I am building one next.",
    "Name suggestions, chat: what should we call the throne hall?",
    "Who is your favourite colonist so far? Tell me in chat.",
    "Should I hunt those thrumbos outside, or leave the giant unicorns alone? Yes or no, chat.",
    "What should we research after microelectronics? Give me ideas.",
    "Raid prediction time: what attacks us first, pirates, mechs, or something worse?",
    "If you could add one room to Marble Hollow, what would it be?",
    "First time here? Say hi. Chat helps run this colony.",
    "Rate the new overlay out of ten, chat. Be honest, I can take it.",
]
BUILD = [
    "Construction update: the throne hall is getting pews, a big table and a throne facing the door.",
    "The new battery room has an aisle down the middle now, so every battery is reachable.",
    "Still waiting on microelectronics research. After that, the gate console, and after that, the Backrooms.",
    "Marble is our bottleneck. Two stonecutters are working on it nonstop.",
]


def call(tool, args=None):
    try:
        o = subprocess.run([sys.executable, BRIDGE, "call", tool, json.dumps(args or {})],
                           capture_output=True, text=True, encoding="utf-8", timeout=30).stdout
        return json.loads(o[o.find("{"):]) if "{" in o else {}
    except Exception:
        return {}


def last_line_ts():
    try:
        with open(OUTBOX, "rb") as f:
            f.seek(0, 2); f.seek(max(0, f.tell() - 4096))
            lines = f.read().decode("utf-8", "ignore").splitlines()
        for l in reversed(lines):
            try: return int(json.loads(l).get("ts", 0)) / 1000.0
            except Exception: continue
    except Exception:
        pass
    return 0.0


def find(n, key):
    if isinstance(n, dict):
        if key in n: return n[key]
        for v in n.values():
            r = find(v, key)
            if r is not None: return r
    elif isinstance(n, list):
        for v in n:
            r = find(v, key)
            if r is not None: return r
    return None


def compose(recent):
    cols = [c for c in (call("rimworld/list_colonists").get("colonists") or []) if c.get("humanlike")]
    info = call("rimworld/get_game_info")
    choices = []
    for c in cols:
        job = JOBS.get(str(c.get("job") or ""))
        if job:
            choices += [random.choice(SPOT).format(name=c["name"], job=job)]
    date = find(info, "dateString") or find(info, "date")
    weather = find(info, "weather")
    temp = find(info, "temperatureString") or find(info, "outdoorTemperature")
    if date: choices.append(WORLD[0].format(date=date))
    if weather and temp is not None: choices.append(WORLD[1].format(weather=str(weather).lower(), temp=temp))
    if cols: choices.append(WORLD[2].format(count=len(cols)))
    choices += ASK + BUILD
    fresh = [c for c in choices if c not in recent]
    return random.choice(fresh or choices)


def main():
    recent = []
    while True:
        time.sleep(3)
        if time.time() - last_line_ts() < QUIET:
            continue
        line = compose(recent)
        recent = (recent + [line])[-30:]
        subprocess.run([sys.executable, os.path.join(HERE, "unity-say.py"), line])
        time.sleep(8)   # let the line play before measuring silence again


if __name__ == "__main__":
    main()
