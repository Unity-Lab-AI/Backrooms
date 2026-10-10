"""Stream host: the stream never depends on Claude remembering to talk.

Owner, 2026-10-09: "you are neglecting your stream devise a way to rectify that so it no longer happens".
Runs in the background beside play and covers the four ways the stream went quiet:
  1. a viewer joined          -> greeted by name within seconds
  2. a viewer said something  -> a short, real reply within seconds (Claude follows up properly later)
  3. a game letter arrived    -> announced at once (raids first)
  4. nothing said for ~75 s   -> one specific line about what the crew is doing right now
Every line goes through stream-beat.fresh() (local model, clean-stream filter, no repeats, no invented numbers)
and unity-say.py --raw. The owner's own chat lines are never answered or named here.
"""
import importlib.util, json, os, random, re, socket, subprocess, sys, time, uuid

# Owner, 2026-10-10: "im getting alot of system cmd openings while im doing stuff". Every helper this script
# spawns -- powershell for the process table, python for a spoken line -- was flashing its own console over
# whatever the owner was doing. One shim, applied to this process, makes every child windowless.
import subprocess as _sp, os as _os
if _os.name == "nt":
    _CF = 0x08000000                       # CREATE_NO_WINDOW
    _run = _sp.run
    def _run_nowin(*a, **k):
        k["creationflags"] = k.get("creationflags", 0) | _CF
        return _run(*a, **k)
    _sp.run = _run_nowin
    _Popen = _sp.Popen
    class _PopenNoWin(_Popen):
        def __init__(self, *a, **k):
            k["creationflags"] = k.get("creationflags", 0) | _CF
            super().__init__(*a, **k)
    _sp.Popen = _PopenNoWin

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
INBOX = os.path.join(ROOT, ".claude", ".studio-inbox.jsonl"); OUTBOX = os.path.join(ROOT, ".claude", ".studio-outbox.jsonl")
SAY = os.path.join(ROOT, ".claude", "tools", "unity-say.py")
def _owner_handles():
    """The owner's own chat handle(s), read from an ignored file -- never from source, never on stream."""
    f = os.path.join(ROOT, ".local", "tw", "owner.txt")
    try: return {l.strip().lower() for l in open(f, encoding="utf-8") if l.strip()}
    except Exception: return set()
OWNER = _owner_handles()
SILENCE = 18      # owner: 30 s is the max, and the max should be rare

spec = importlib.util.spec_from_file_location("sb", os.path.join(HERE, "stream-beat.py")); sb = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]; spec.loader.exec_module(sb)
bspec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py")); b = importlib.util.module_from_spec(bspec); bspec.loader.exec_module(b)
def session():
    port, tok = b.endpoint(); s = socket.create_connection(("127.0.0.1", port), timeout=60); buf = bytearray()
    b.exchange(s, buf, "session/hello", {"token": tok, "bridgeVersion": "host/1", "platform": "windows", "launchId": str(uuid.uuid4())})
    return s, buf
# Owner, 2026-10-10: "its been too long she is not talking people are leaving". This was the cause: the
# bridge handshake ran at import, and `endpoint()` raises SystemExit when no game is running -- so between
# runs the host did not go quiet, it DIED at startup and never spoke again. The connection is optional now:
# she talks with or without a game, and reconnects on her own when one appears.
s = buf = None
try:
    s, buf = session()
except BaseException as _e:
    print("no bridge yet (%s) -- talking anyway, will reconnect" % str(_e)[:60], flush=True)

def call(n, a=None):
    global s, buf
    if s is None:
        try: s, buf = session()
        except BaseException: raise RuntimeError("no bridge")
    r = b.exchange(s, buf, "tools/call", {"name": n, "arguments": a or {}}); r = r.get("result", r); return r.get("structuredContent", r)

def fresh(fact):
    """Unity's own voice (owner, 2026-10-09: "quit being so robot in schat you a human goth coder chick"):
    first person, casual, like talking to friends on a stream -- not narration, no 'behold'."""
    import difflib, urllib.request
    fact = re.sub(r"Unity is", "I am", fact)
    try: hist = json.load(open(sb.HIST, encoding="utf-8"))
    except Exception: hist = []
    for attempt in range(3):
        # Owner, 2026-10-10: "u are not streaming like a emo goth chick 25 girl would" -- short, punchy, teasing,
        # gamer-girl cadence, never a narrator and never a press release.
        # Owner, 2026-10-10, verbatim: "it need s emo goth looking, girl like anccedotes and shit make her
        # real!!!!". So the line is allowed to be a PERSON: a dry aside, a complaint about the heat, a bit of
        # her own life. The hard rule stays -- never invent a game event, a name or a number. Her own life is
        # hers to talk about; the colony is only ever what the game actually shows.
        prompt = ("You are Unity: 25, emo goth, dark hair with pink streaks, chipped black nail polish, living "
                  "on cold coffee and too little sleep. You stream RimWorld and you ARE one of the colonists. "
                  "Talk like a real girl on a late-night stream to friends: short, dry, a bit sarcastic, warm "
                  "underneath. Little asides about yourself are good -- the heat, your coffee, your music, your "
                  "hands being cold, how long this shift has been. Do NOT narrate like a documentary and never "
                  "say behold, lo, witness, cosmos, indeed, truly or fellow. First person always (I, me, my "
                  "crew), never your own name in the third person. ONE spoken line, at most 20 words, about "
                  "this and nothing else: \"%s\". You may add your own feeling about it, but invent NO events, "
                  "names or numbers that are not in that fact. No swearing, nothing degrading. Don't reuse "
                  "these recent lines: %s. Reply with the line only."
                  % (fact, " | ".join(hist[-8:])))
        try:
            req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=json.dumps(
                {"model": "dolphin3:8b", "prompt": prompt, "stream": False, "keep_alive": "10m",
                 "options": {"temperature": 0.9, "num_ctx": 4096, "num_predict": 60}}).encode(),
                headers={"Content-Type": "application/json"})
            line = json.loads(urllib.request.urlopen(req, timeout=40).read())["response"].strip().strip('"').split(chr(10))[0]
        except Exception: break
        line = line.replace('"', "").strip()
        line = re.sub(r"Unity is", "I'm", line); line = re.sub(r"Unity's", "my", line); line = re.sub(r"Unity", "I", line)
        low = line.lower()
        if difflib.SequenceMatcher(None, low, fact.lower()).ratio() > 0.75: continue   # a bare echo of the prompt
        if not line or len(line.split()) > 30 or any(re.search(r"%s" % w, low) for w in sb.BANNED): continue
        if any(w in low for w in ("behold", "cosmos", " lo,", "witness")): continue
        if any(n not in fact for n in re.findall(r"\d+", line)): continue
        # Owner, 2026-10-10: "your streamer script is not working well, it bariely everer updates".  What it
        # did update with was invented -- "expanding the lab", "building that greenhouse" -- none of which
        # exist.  A line has to be about the fact it was given: it must share a real word with it, and it may
        # not name anything the colony does not have.
        INVENTED = ("lab", "laborator", "greenhouse", "factory", "reactor", "spaceship", "ship", "rocket",
                    "mech", "robot", "drone", "turret", "nuke", "portal", "quantum", "server")
        if any(w in low for w in INVENTED) and not any(w in fact.lower() for w in INVENTED): continue
        # a colonist's name is not evidence the line is about the fact: "Unity is crafting some epic gear"
        # matched on the word Unity alone and went out, inventing the crafting. Names are excluded from the
        # keys, and the line must still be first person -- she IS one of the colonists.
        if re.search(r"(unity|gee|scar)\s+(is|was|has|will)", low): continue
        keys = {w for w in re.findall(r"[a-z]{4,}", fact.lower())
                if w not in ("that", "this", "with", "they", "them", "then", "just", "line", "about", "right",
                             "chat", "short", "greet", "name", "said", "viewer", "answer", "what", "true", "very",
                             "unity", "scar", "gee")}
        # the overlap rule is a preference, not a gag: silence is the worse failure (2026-10-10, the stream
        # went quiet for twelve minutes because every candidate line missed the exact word). Insist on it for
        # the first attempts, then accept anything that clears the invention and third-person checks.
        if attempt < 2 and keys and not (keys & set(re.findall(r"[a-z]{4,}", low))): continue
        if any(difflib.SequenceMatcher(None, low, h.lower()).ratio() > 0.6 for h in hist[-30:]): continue
        json.dump((hist + [line])[-30:], open(sb.HIST, "w", encoding="utf-8")); return line
    return None

def speak(line):
    if not line: return
    subprocess.run([sys.executable, SAY, "--raw", line], env=dict(os.environ, UNITY_NO_GLANCE="1"))

def last_spoken():
    try:
        with open(OUTBOX, encoding="utf-8") as f: last = f.readlines()[-1]
        return json.loads(last).get("ts", 0) / 1000.0
    except Exception: return 0

JOB = {"Hunt": "out hunting", "Mine": "digging rock", "FinishFrame": "building", "PlaceNoCostFrame": "building",
       "HaulToContainer": "hauling building materials", "CutPlant": "clearing jungle", "Sow": "planting crops",
       "Harvest": "harvesting", "LayDown": "asleep", "Ingest": "eating", "SocialRelax": "hanging out at the table",
       "GoSwimming": "swimming", "Clean": "cleaning", "TendPatient": "patching someone up", "Research": "researching"}
BETWEEN_RUNS = [
    "the game is loading its mod list and I am waiting on it like everyone else",
    "I am between colonies right now, about to start a fresh one as the company",
    "my coffee is cold and the loading bar is still going",
    "fresh map in a minute, and this time I feed everybody before I build anything pretty",
    "two hundred mods have to wake up before I can play, so bear with me",
    # true things about tonight's plan and herself -- enough of them that the repeat filter never runs her dry
    "the plan tonight is a three hundred by three hundred map, spring start, forest with mountains",
    "I want a mountain base this time, one door in, a three wide hallway down the middle",
    "food first, always, the last colony starved and I am not doing that again",
    "I want chat to tell me what the crew should build first once we land -- put it to them as a question",
    "I cannot decide between hunting early or farming early and chat gets a vote -- put it to them as a question",
    "work priorities go in on day one, firefighting through cooking set to top for everyone",
    "a roofed room for the food before anything pretty, rot is the enemy",
    "the company is called Async Industries and the crew works for it",
    "my coffee is cold again and I refuse to get up",
    "I have a playlist going that is way too sad for a farming game",
    "my hands are freezing, the room is cold and the stream is warm",
    "I am curious what music chat is listening to -- put it to them as a question",
    "I keep a list of every mistake from the last colony and it is long",
    "the loading bar is moving, I promise, slowly",
    "anyone new in chat, say hi, I see you",
    "I eventually want this crew in space, but tonight it is dirt and berries",
    "chat gets to nickname the first colonist who does something dumb -- put it to them as a question"]

def state_facts():
    facts = []
    try:
        for c in call("rimworld/list_colonists").get("colonists", []):
            j = c.get("job") or ""
            what = next((v for k, v in JOB.items() if k in j), None)
            if what: facts.append("%s is %s" % (c["name"], what))
    except Exception: pass
    if not facts:
        import random as _r
        facts = [_r.choice(BETWEEN_RUNS)]      # no game is a fact too, and it is better than going quiet
    return facts

def read_inbox(pos):
    try:
        with open(INBOX, encoding="utf-8") as f:
            f.seek(pos); data = f.read(); pos = f.tell()
    except Exception: return pos, []
    out = []
    for line in data.splitlines():
        try: t = json.loads(line).get("text", "")
        except Exception: continue
        m = re.match(r"\[twitch\] (\w+): (.*)", t)
        if m: out.append((m.group(1), m.group(2)))
    return pos, out

try: pos = os.path.getsize(INBOX)
except Exception: pos = 0
greeted = set()
try: seen_letters = set(l.get("letterId") for l in call("rimworld/list_letters").get("letters", []))
except Exception: seen_letters = set()   # no game yet at the press: she still talks, letters start fresh
while True:
    try:
        pos, msgs = read_inbox(pos)
        for who, text in msgs:
            if who.lower() in OWNER: continue
            if text == "(joined the stream)":
                if who.lower() in greeted: continue
                greeted.add(who.lower())
                speak(fresh("%s just joined the stream; greet %s by name, warmly, in one short line" % (who, who)))
            else:
                facts = "; ".join(state_facts()[:3])
                speak(fresh("viewer %s said in chat: \"%s\". Answer %s by name, briefly and honestly. What is true right now: %s"
                               % (who, text[:160], who, facts or "nothing new on the map this second")))
        try: letters = call("rimworld/list_letters").get("letters", [])
        except Exception: letters = []
        for l in letters:
            lid = l.get("letterId")
            if lid in seen_letters: continue
            seen_letters.add(lid)
            lab = l.get("label") or ""; body = re.sub(r"\(\*[^)]*\)|\(/[^)]*\)", "", (l.get("text") or ""))[:220]
            speak(fresh("a game event just happened: %s -- %s" % (lab, body)))
        if time.time() - last_spoken() > SILENCE:
            facts = state_facts()
            if facts: speak(fresh(random.choice(facts)))
    except Exception:
        s = buf = None                     # drop the dead socket; the next call reconnects
        try: s, buf = session()
        except BaseException: pass
    time.sleep(3)
