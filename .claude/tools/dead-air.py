"""Dead-air guard for the stream: if Unity has said nothing for a while, she says something.

    python .claude/tools/dead-air.py [quiet_seconds]      # default 40; runs until killed

Owner, 2026-10-08: "comeone told me it too quiet too much dead air". The long silences are the
stretches where Unity is reading code or saves between game actions. This watches the studio
outbox (every spoken line lands there via unity-say.py); after QUIET seconds with no Unity line
it speaks one built from the live game -- a colonist spotlight, the weather and date, what is
being built -- or a question for chat. Never repeats a line it said in the last 30.

Questions to chat are about the GAME only -- never the overlay, tools or code (owner: "You do not
take code advice from the twitch!"). Stream-clean by construction (LAW: THE STREAM IS CLEAN): every line is a fixed clean template
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
    "{name} is {job}. Riveting. Truly.",
    "Checking on {name}. {name} is {job}. Sure. Why not.",
    "{name}, {job}, as usual. I keep that one around for the vibes.",
    "Oh look, {name} is {job}. Nobody asked, {name}.",
    "{name} is {job} while the rest of us hold this place together.",
    "I am watching you, {name}. Still {job}. Mm.",
]
WORLD = [
    "{date}. Still alive. Do not get excited.",
    "Weather: {weather}, {temp}. Perfect. Gloomy, the way I like it.",
    "{count} colonists. {count} problems. All mine.",
]
ASK = [
    "Drug lab, rec room, or a royal wing for Gee. Pick one, chat. I am not asking twice.",
    "Somebody name the throne hall. Make it dark. No, darker.",
    "Favourite colonist. Go. Wrong answers will be remembered.",
    "Thrumbos outside. Hunt them or leave them. Your call, your funeral.",
    "What do I research after microelectronics. Make it worth my time.",
    "What raids us first. Pirates, mechs, or something worse. Place your bets.",
    "New here? Say hi. Or lurk. I see you either way.",
    "One room you would add to my city. One. Make it good.",
]
BUILD = [
    "The throne hall is getting there. Pews, a big table, a throne staring at the door. Mine.",
    "Battery room, take two. Now you can actually walk to the batteries. Revolutionary.",
    "Still waiting on microelectronics. Then the gate console. Then the Backrooms. Patience is not my thing.",
    "Marble. Always marble. Two stonecutters, zero days off.",
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
