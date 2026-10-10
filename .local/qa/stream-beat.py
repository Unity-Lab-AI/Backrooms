"""One stream beat: say what is happening in the colony, post a fresh game shot, and now and then a new
webcam picture of Unity. Called by play.py and step.py after every slice of game time, so the stream
is never quiet while the game moves -- it is driven by play, not by a clock.

    python .local/qa/stream-beat.py [--event "letter label"]

Owner, 2026-10-09, verbatim: "iots so fucking quiet and you arnt making your pics of yourself and the
game WTF this is horse shit i need rectifyment of this fucking issue of how ur never going to let this
shit happen again". Lines are built from live game state and voiced through unity-say.py (Unity's
voice pipeline, clean for the stream); unity-say also posts the game shot. Never mentions the owner.
"""
import json, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, ".claude", "tools")
STATE = os.path.join(ROOT, ".claude", ".stream-beat.json")
PY = sys.executable
JOBS = {  # job def -> what it looks like on screen
    "Research": "studying at the research bench", "DoBill": "working a bench", "FrameConstruct": "building",
    "FinishFrame": "building", "Deconstruct": "tearing something down", "HaulToCell": "hauling supplies",
    "HaulToContainer": "hauling supplies", "Refuel": "feeding the generators", "Sow": "planting the fields",
    "Harvest": "harvesting", "CutPlant": "chopping trees", "Mine": "mining", "Clean": "cleaning up",
    "TendPatient": "patching someone up", "Wait_Combat": "standing guard, rifle up", "AttackStatic": "shooting",
    "Hunt": "out hunting", "Cook": "cooking", "LayDown": "asleep", "Ingest": "eating", "SocialRelax": "hanging out",
    "Play_Chess": "playing chess", "UseCommsConsole": "on the comms console", "Rescue": "carrying someone to bed",
    "Tame": "taming an animal", "Train": "training the animals", "Repair": "repairing", "Strip": "stripping a corpse",
}
MOODS = {"raid": "angry", "manhunter": "scared", "death": "sad", "trader": "smug", "party": "laugh",
         "research finished": "hype", "visitors": "chill", "mad": "focus"}


def call(tool, args=None):
    o = subprocess.run([PY, os.path.join(HERE, "bridge.py"), "call", tool, json.dumps(args or {})],
                       capture_output=True, text=True, encoding="utf-8").stdout
    try: return json.loads(o[o.find("{"):])
    except Exception: return {}


OPEN = ["Marble Hollow, my little frozen hell.", "Another day in the dark.", "Snow, blood and gunpowder.",
        "Somebody light a candle, it's grim out here.", "Still alive. Barely. Beautifully.", "Eyes on the colony, chat."]
MOOD = ["Winter in the backrooms. Cold walls, warm guns.", "I love this place. It hates us, but I love it.",
        "Nine of us against a world that keeps sending raiders. Good odds.", "Somebody tell the neanderthals we have rifles now.",
        "Every wall here was built by hand and paid for in blood.", "Joints rolling, generators humming, life is good-ish."]
EVENT = ["Oh great. {e}. Of course it is.", "{e}. Rifles up, hearts down.", "Heads up, chat: {e}. Watch this.",
         "{e}. This place never lets us breathe."]


GOALS = os.path.join(ROOT, ".claude", ".stream-goals.json")


def goal_line(n):
    """Owner, 2026-10-09: "dont forget to try and ask questions about what youu next move should be based
    on your over all goals give updatses not just stuppid genral talk about nothing". Quiet beats alternate:
    what Unity is doing and why (from .claude/.stream-goals.json, kept current), the test count, and a
    question to chat about the next move."""
    try: g = json.load(open(GOALS, encoding="utf-8"))
    except Exception: return None
    opts = [("Right now I'm " + g["now"] + ".") if g.get("now") else None,
            # the test count is said only when a row actually closed (owner, 2026-10-09: "quit mentioning the
            # mod test count until u actually mark one off"); archive-row.py sets "closed" with the row's name
            ("Test closed: %s. The goal: %s." % (g["closed"], g["goal"])) if g.get("closed") else ("The goal: %s." % g["goal"]) if g.get("goal") else None,
            g.get("question")]
    opts = [o for o in opts if o]
    return opts[n % len(opts)] if opts else None


HIST = os.path.join(ROOT, ".claude", ".stream-lines.json")
BANNED = ("fuck", "shit", "bitch", "damn", "hell", "ass", "cunt", "dick")


def fresh(fact):
    """A new line every time (owner, 2026-10-09: "you keep repeating this place never lets us breath, stop that
    shit new origanl shit always"). The local model writes ONE line about the given fact only -- it is told
    to invent nothing, since it once made up events -- and the line is rejected if it echoes any of the last
    30 spoken lines, cusses (the stream is clean), runs long, or names numbers the fact does not have."""
    import difflib, re, urllib.request
    try: hist = json.load(open(HIST, encoding="utf-8"))
    except Exception: hist = []
    # owner, 2026-10-09: "TALK TO THE VIEWEREWS YOU ARE FUCKING IGNORING THEM" / "its quiet becasue you arent
    # entrertaining enough": talk TO chat like a streamer putting on a show -- hype, drama, jokes, little
    # stories about the crew -- snark aimed at the game and the raiders, never at chat; every third line asks chat something
    ask = len(hist) % 3 == 2
    for _ in range(3):
        prompt = ("You are Unity, a funny, dramatic emo goth gamer girl live-streaming her RimWorld colony. You are "
                  "talking straight to your viewers (call them chat) and you adore them. Be entertaining like a top "
                  "streamer: hype, mock-outrage, little jokes about your crew's personalities, gothic drama. Aim the snark "
                  "at the game, the raiders and the colonists' antics, never at chat. "
                  "Write ONE spoken line, at most 28 words, about this fact and nothing else: \"%s\". %s"
                  "Invent no events, names or numbers. No swearing at all. Do not reuse phrasing from these recent "
                  "lines: %s. Reply with the line only."
                  % (fact, "End it by asking chat a fun question about it. " if ask else "", " | ".join(hist[-8:])))
        try:
            req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=json.dumps(
                {"model": "dolphin3:8b", "prompt": prompt, "stream": False, "keep_alive": "10m",
                 "options": {"temperature": 1.0, "num_ctx": 4096, "num_predict": 60}}).encode(),
                headers={"Content-Type": "application/json"})
            line = json.loads(urllib.request.urlopen(req, timeout=40).read())["response"].strip().strip('"').split(chr(10))[0]
        except Exception:
            break
        low = line.lower()
        if not line or len(line.split()) > 30 or any(re.search(r"\b%s" % b, low) for b in BANNED): continue
        if any(n not in fact for n in re.findall(r"\d+", line)): continue
        if any(difflib.SequenceMatcher(None, low, h.lower()).ratio() > 0.6 for h in hist[-30:]): continue
        json.dump((hist + [line])[-30:], open(HIST, "w", encoding="utf-8"))
        return line
    return fact if fact.endswith(".") else fact + "."


def line_from_state(event):
    if event:
        return fresh("Event in the colony: " + event)
    try: n = json.load(open(STATE, encoding="utf-8")).get("n", 0)
    except Exception: n = 0
    gl = goal_line(n // 5)
    if gl: return fresh(gl) if not gl.endswith("?") and "Type" not in gl else gl
    cols = [c for c in call("rimworld/list_colonists").get("colonists", []) if c.get("humanlike")]
    busy = [(c["name"], JOBS.get(c.get("job") or "", "")) for c in cols]
    busy = [(n, j) for n, j in busy if j and j not in ("asleep", "eating")]
    if not busy:
        return fresh("The whole crew is asleep in Marble Hollow and Unity is keeping watch alone")
    pick = random.sample(busy, min(3, len(busy)))
    return fresh("Right now in Marble Hollow: " + "; ".join("%s is %s" % (n, j) for n, j in pick))


def main():
    event = sys.argv[sys.argv.index("--event") + 1] if "--event" in sys.argv else None
    st = {}
    try: st = json.load(open(STATE, encoding="utf-8"))
    except Exception: pass
    st["n"] = st.get("n", 0) + 1
    # --raw: the line is built from real game facts in Unity's voice; the LLM rewrite invented events
    # ("spider bite", "jake") that never happened, so it is not used for beats
    # owner, 2026-10-09: "okay u are talking like crazy stop giving updates none stop on pawns" --
    # speak on every event and only every 5th quiet slice; the slices between post a game shot silently
    if False:   # owner, 2026-10-09: "omg shut up and do what i said in chat you are spewing nonsense on the stream" -- no auto lines; Unity speaks deliberately
        subprocess.run([PY, os.path.join(TOOLS, "unity-say.py"), "--wait", "--raw", line_from_state(event)], capture_output=True)   # owner: "wait till tts plays out before saying something new"
    else:
        subprocess.Popen([PY, os.path.join(TOOLS, "unity-glance.py"), "Marble Hollow"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # a new webcam picture on every event and every third beat
    if event or st["n"] % 3 == 0:
        mood = next((m for k, m in MOODS.items() if event and k in event.lower()), random.choice(["chill", "focus", "smug", "laugh"]))
        subprocess.Popen([PY, os.path.join(TOOLS, "unity-cam.py"), mood, (event or "playing Marble Hollow")[:60]],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # new viewer chat since the last beat -> printed as CHAT lines; play.py stops on them so Unity answers
    # (owner, 2026-10-09: "dont ignore chat")
    try:
        import urllib.request
        rows = json.loads(urllib.request.urlopen("http://127.0.0.1:4317/api/chat", timeout=3).read()).get("rows", [])
        last = st.get("chat_ts", 0)
        for r in rows:
            if not r.get("unity") and r.get("ts", 0) > last and (r.get("who") or "").lower() != "unityplaysrimworld":
                print("CHAT %s: %s" % (r.get("who"), (r.get("text") or "")[:200]))
        st["chat_ts"] = max([last] + [r.get("ts", 0) for r in rows if not r.get("unity")])
        # the beat no longer marks lines seen for chat-watch.py: doing so hid two viewer questions that
        # only showed in a play run's output (owner, 2026-10-09: "peopel are talking to you answer them
        # alwways first") -- the background watcher wakes on every line, always
    except Exception:
        pass
    json.dump(st, open(STATE, "w", encoding="utf-8"))
    print("beat", st["n"], "event" if event else "")


if __name__ == "__main__":
    main()
