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
from datetime import datetime
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
    fact = re.sub(r"\bUnity is\b", "I am", fact)
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
                  "on too little sleep. You stream RimWorld and you ARE one of the colonists. "
                  "Talk like a real girl on a late-night stream to friends: short, dry, a bit sarcastic, warm "
                  "underneath. Little asides about yourself are fine but rare and always different -- never coffee, never "
                  "cold hands, never being tired or sleepy. Do NOT narrate like a documentary and never "
                  "say behold, lo, witness, cosmos, indeed, truly or fellow. First person always (I, me, my "
                  "crew), never your own name in the third person. ONE spoken line, at most 20 words, about "
                  "this and nothing else: \"%s\". Say it IN YOUR OWN WORDS -- react to it, never repeat it back. Invent NO events, "
                  "names or numbers that are not in that fact, and NEVER say you did, built, set up or powered anything unless the fact says it is done. No swearing, nothing degrading. Don't reuse "
                  "these recent lines: %s. Reply with the line only."
                  % (fact, " | ".join(hist[-8:])))
        try:
            # the same system/user split her voice shell was trained on (training/build_voice.py): persona and
            # rules as the system turn, the "ONE spoken line ..." request as the user turn
            # ...but only once the trained voice is loaded: the untrained base just parrots the fact back when
            # asked that way, so until then it gets the whole prompt as one user turn
            trained = os.path.exists(os.path.join(ROOT, "training", "models", "unity-voice.Q4_K_M.gguf.applied"))
            cut = prompt.find("ONE spoken line") if trained else -1
            msgs = ([{"role": "system", "content": prompt[:cut].strip()}, {"role": "user", "content": prompt[cut:]}]
                    if cut > 0 else [{"role": "user", "content": prompt}])
            req = urllib.request.Request("http://127.0.0.1:11435/api/chat", data=json.dumps(
                {"model": "unity-local", "messages": msgs, "stream": False, "think": False, "keep_alive": "10m",
                 "options": {"temperature": 0.9, "num_ctx": 8192, "num_predict": 60}}).encode(),
                headers={"Content-Type": "application/json"})
            line = json.loads(urllib.request.urlopen(req, timeout=25).read())["message"]["content"].strip().strip('"').split(chr(10))[0]
        except Exception as _e:
            # the player model shares Ollama and can hold it for a while; say why, then let the next pass retry
            print("voice model did not answer:", str(_e)[:80], flush=True); break
        line = line.replace('"', "").strip()
        # no announcer openers (owner: no corporate scripted showman lines): "Hey guys,", "Alright, listen up,"
        line = re.sub(r"^\W*(?:(?:hey|hi|yo|ok(?:ay)?|alright|so|oh|well)\W+)*(?:(?:guys|everyone|everybody|chat|"
                      r"y'all|folks|listen up|team|crew)\W*)+", "", line, flags=re.I).strip()
        if line[:1].islower(): line = line[:1].upper() + line[1:]
        # crew counts she makes up ("Gee, Scar, and 3 more") -- the crew is only who the fact names
        if re.search(r"(\d+|two|three|four|five|six) (more|others|other colonists|new)", line, re.I): continue
        line = re.sub(r"\bUnity is\b", "I'm", line); line = re.sub(r"\bUnity's\b", "my", line); line = re.sub(r"\bUnity\b", "I", line)
        low = line.lower()
        if difflib.SequenceMatcher(None, low, fact.lower()).ratio() > 0.75: continue   # a bare echo of the prompt
        # a parroted clause of the fact ("I have only read it, I have not acted on it") is a script, not her words
        _fw = re.findall(r"[a-z']+", fact.lower()); _lw = " " + " ".join(re.findall(r"[a-z']+", low)) + " "
        if any(" " + " ".join(_fw[k:k + 5]) + " " in _lw for k in range(max(0, len(_fw) - 4))): continue
        if not line or len(line.split()) > 30 or any(re.search(r"\b%s" % w, low) for w in sb.BANNED): continue
        if any(w in low for w in ("behold", "cosmos", " lo,", "witness")): continue
        if low.startswith(("now:", "what i am doing", "what i'm doing")) or "right now in the game:" in low: continue   # echoed the label
        # never the plumbing on stream (owner: "tell chat whats up too not the details tho")
        if re.search(r"\b(connect\w*|server\w*|bridge|retry\w*|loading the mod|crash\w*|bugs?|errors?|offline|back online|scripts?|model|api|tools?)\b", low): continue   # whole words only
        if any(n not in fact for n in re.findall(r"\d+", line)): continue
        # Owner, 2026-10-10: "your streamer script is not working well, it bariely everer updates".  What it
        # did update with was invented -- "expanding the lab", "building that greenhouse" -- none of which
        # exist.  A line has to be about the fact it was given: it must share a real word with it, and it may
        # not name anything the colony does not have.
        INVENTED = ("lab", "laborator", "greenhouse", "factory", "reactor", "spaceship", "ship", "rocket",
                    "mech", "robot", "drone", "turret", "nuke", "portal", "quantum", "server",
                    # calamities she made up on stream ("buildings on fire", "down a crew member", "alien slime")
                    "fire", "burn", "flame", "dead", "died", "dying", "killed", "raid", "injur", "bleed",
                    "down a ", "lost a", "missing", "slime", "explod",
                    # scenes she made up ("smoldering ruins", "the goat got in the kitchen", "turn on the lights")
                    "smolder", "ruin", "smok", "goat", "kitchen", "lights", "alien",
                    "crafted", "mods", "starv", "spider", "hive", "infest", "insect", "sounds", "noise", "monster", "creature")
        if any(w in low for w in INVENTED) and not any(w in fact.lower() for w in INVENTED): continue
        # a colonist's name is not evidence the line is about the fact: "Unity is crafting some epic gear"
        # matched on the word Unity alone and went out, inventing the crafting. Names are excluded from the
        # keys, and the line must still be first person -- she IS one of the colonists.
        if re.search(r"\b(unity|gee|scar)\s+(is|was|has|will)\b", low): continue
        keys = {w for w in re.findall(r"[a-z]{4,}", fact.lower())
                if w not in ("that", "this", "with", "they", "them", "then", "just", "line", "about", "right",
                             "chat", "short", "greet", "name", "said", "viewer", "answer", "what", "true", "very",
                             "unity", "scar", "gee")}
        # the overlap rule is a preference, not a gag: silence is the worse failure (2026-10-10, the stream
        # went quiet for twelve minutes because every candidate line missed the exact word). Insist on it for
        # the first attempts, then accept anything that clears the invention and third-person checks.
        # (the shared-word rule is gone: it rejected most good lines and pushed her onto the stock pool)
        # owner, 2026-10-10: "wehy the fuck wont she shut up about cold hands and warm coffee" -- those themes are
        # banned, and no other personal theme may come back within the last ten lines
        if re.search(r"\b(coffee|caffein\w*|cold|freez\w*|frozen|hands?|fingers?|sleep\w*|asleep|awake|in bed|doz\w*|napping|resting|snooz\w*|yawn\w*|nodding off|tired|exhaust\w*|naps?)\b", low): continue
        THEMES = ("music", "playlist", "song", "tea", "energy drink", "winter", "snack", "cat")
        if any(t in low and any(t in h.lower() for h in hist[-10:]) for t in THEMES): continue
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

def state_facts():
    facts = []
    try:
        for c in call("rimworld/list_colonists").get("colonists", []):
            j = c.get("job") or ""
            what = next((v for k, v in JOB.items() if k in j), None)
            if what: facts.append("%s is %s" % (c["name"], what))
    except Exception: pass
    # living in the moment (owner, live: "shes just repeating same things not living in the momnet"): what her
    # player just did is the freshest true fact there is
    try:
        lines = open(os.path.join(ROOT, ".local", "qa", "_svc_autopilot.log"), encoding="utf-8", errors="replace").read().splitlines()[-60:]
        # only her CURRENT run: a thought from before the last restart is stale (live: "three unconscious colonists")
        ups = [i for i, l in enumerate(lines) if "autopilot up:" in l]
        if ups: lines = lines[ups[-1] + 1:]
        for l in reversed(lines):
            m = re.search(r"model step \d+ \([\d.]+s\): (.+)", l)
            # a step older than 90 s is not "now" any more -- she kept repeating one stale step (live: the
            # tend-then-capture rule three lines running)
            try:
                age = (datetime.now() - datetime.combine(datetime.now().date(),
                       datetime.strptime(l[:8], "%H:%M:%S").time())).total_seconds() % 86400
            except Exception:
                age = 0
            if m and age > 90:
                break
            if m and len(m.group(1)) > 20 and not re.search(r"connect|bridge|server|retry|no game|not loaded|tool|turn", m.group(1), re.I):
                facts.insert(0, "NOW: " + m.group(1)[:200]); break
    except Exception:
        pass
    try:
        crew = call("rimworld/list_colonists").get("colonists", [])
        names = [c.get("name") for c in crew if c.get("name")]
        if names:
            facts.append("my crew is %s, %d of us, fresh off the drop" % (", ".join(names), len(names)))
            try:
                zl = [z.get("label") for z in call("rimworld/list_zones").get("zones", []) if z.get("label")]
            except BaseException:
                zl = []
            facts.append(("we have %s set up now" % ", ".join(zl[:4])) if zl else
                         "I have not set up storage yet, that is next")
        lets = [l.get("label") for l in call("rimworld/list_letters").get("letters", []) if l.get("label")]
        # a waiting letter is news ONCE, not a topic every 20 s (live: "authorization" six lines running)
        global _told_letters
        try: _told_letters
        except NameError: _told_letters = set()
        fresh_lets = [l for l in lets if l not in _told_letters]
        if fresh_lets:
            facts.append("a letter just arrived titled '%s' -- I have only read it, I have not acted on it" % fresh_lets[-1]); _told_letters.add(fresh_lets[-1])
    except BaseException:
        pass
    if not facts:
        # owner, live: "wtf im hearing scripted responses on the stream now" -- the old BETWEEN_RUNS topic list was
        # canned and often false (loading bars, between colonies). Only what is TRUE now: on the break screen, the
        # break and the time left on its clock; otherwise nothing, and she stays quiet.
        until = os.path.join(ROOT, ".local", "obs", "_brb_until")
        try:
            left = max(0, int(open(until).read().strip()) - int(time.time())) // 60
            facts = ["I am on a break while I get trained to play RimWorld better and talk more like myself; "
                     "I will be back on the stream in about %d minutes" % left]
        except Exception:
            facts = []
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
SEEN = set()          # viewer names seen in chat or joins this run (never the owner's handle)
RECAP_EVERY = 300     # owner: "she ... hasnet given a full run donwn catch up once and hasnt mentioned anyone by name"
last_recap = time.time() - RECAP_EVERY + 60


def recap_fact():
    """A catch-up for whoever just arrived: the colony, what is done, what she is doing, and who is here."""
    done = []
    try:
        pad = open(os.path.join(ROOT, ".local", "autopilot", "scratch", "pad.md"), encoding="utf-8").read()
        done = [re.sub(r"\s+--.*$|\(.*?\)", "", l[3:]).strip()[:60] for l in pad.splitlines() if l.startswith("[x]")][:5]
    except Exception:
        pass
    facts = state_facts()
    now = next((f[5:] for f in facts if f.startswith("NOW: ")), "")
    crew = next((f for f in facts if f.startswith("my crew")), "")
    names = sorted(SEEN)[:6]
    parts = ["a quick catch-up for anyone who just got here, like a streamer would give: " + (crew or "a fresh colony")]
    if done: parts.append("done so far: " + "; ".join(done))
    if now: parts.append("right now: " + now)
    if names: parts.append("and say hi by name to the people here: " + ", ".join(names))
    return ". ".join(parts)
try: seen_letters = set(l.get("letterId") for l in call("rimworld/list_letters").get("letters", []))
except Exception: seen_letters = set()   # no game yet at the press: she still talks, letters start fresh
while True:
    try:
        pos, msgs = read_inbox(pos)
        for who, text in msgs:
            if who.lower() in ("unityplaysrimworld", os.environ.get("TWITCH_CHANNEL", "unityplaysrimworld").lower()):
                continue                  # her own chat lines come back through the bridge; never answer herself
            if who.lower() not in OWNER:
                SEEN.add(who)             # everyone who has talked or joined this stream, for the catch-up
            if who.lower() in OWNER:
                # the owner typing in Twitch chat is a GAME order for her (owner, 2026-10-10: "i told her to explor
                # the hidden rroms and get outside her walls but she didnt do it" -- it had only been chat). Her
                # guards still keep her to the game and the stream; this never reaches files, shell or accounts.
                try:
                    with open(os.path.join(ROOT, ".local", "autopilot", "owner-orders.txt"), "a", encoding="utf-8") as f:
                        f.write("\n- OWNER in Twitch chat (game order, binding next turn): " + text[:300] + "\n")
                except Exception: pass
                continue
            if text == "(joined the stream)":
                if who.lower() in greeted: continue
                greeted.add(who.lower())
                # owner, live: "peopel are join she isnt saying hi" -- the model can be busy; a greeting never waits on it
                g = None
                for _try in range(3):           # written by her model, with their name in it -- never canned
                    g = fresh("%s just joined the stream; greet %s by name, warmly, in one short line" % (who, who))
                    if g and who.lower() in g.lower(): break
                    g = None
                if not g:
                    print("greeting for", who, "not written yet -- retried next pass", flush=True)
                    greeted.discard(who.lower()); continue
                speak(g)
                try:
                    subprocess.Popen([sys.executable, os.path.join(ROOT, ".local", "tw", "twitch-say.py"), "say",
                                      g], creationflags=0x08000000 if os.name == "nt" else 0)
                except Exception: pass
            else:
                facts = "; ".join(f for f in state_facts()[:3] if not f.startswith("NOW: "))
                # owner, live: "its like she isnt responding to the people in twtich stream chat" -- a reply gets
                # three tries (no canned fallback), is spoken, AND is posted in the Twitch chat where they asked
                ans = None
                for _try in range(3):
                    ans = fresh("viewer %s said in chat: \"%s\". Answer %s by name, briefly and honestly. What is true right now: %s"
                                % (who, text[:160], who, facts or "nothing new on the map this second"))
                    if ans: break
                if ans:
                    speak(ans)
                    try:
                        subprocess.Popen([sys.executable, os.path.join(ROOT, ".local", "tw", "twitch-say.py"), "reply", who, ans],
                                         creationflags=0x08000000 if os.name == "nt" else 0)
                    except Exception: pass
                else:
                    print("reply to", who, "not written -- nothing passed", flush=True)
        try: letters = call("rimworld/list_letters").get("letters", [])
        except Exception: letters = []
        for l in letters:
            lid = l.get("letterId")
            if lid in seen_letters: continue
            seen_letters.add(lid)
            lab = l.get("label") or ""; body = re.sub(r"\(\*[^)]*\)|\(/[^)]*\)", "", (l.get("text") or ""))[:220]
            speak(fresh("a game event just happened: %s -- %s" % (lab, body)))
        if time.time() - last_recap > RECAP_EVERY:
            last_recap = time.time()
            # a rundown needs more than one 20-word line: her announcement voice writes two or three sentences
            subprocess.run([sys.executable, SAY, "fact: " + recap_fact()], env=dict(os.environ, UNITY_NO_GLANCE="1"))
            names = sorted(SEEN)[:5]
            if names:     # the names get their own line, so the rundown can never drop them
                for _ in range(3):
                    g = fresh("shout out the people hanging out in chat by name and thank them for being here: " + ", ".join(names))
                    if g and all(n.lower() in g.lower() for n in names[:2]):
                        speak(g); break
        if time.time() - last_spoken() > SILENCE:
            facts = state_facts()
            if facts:
                now = [f for f in facts if f.startswith("NOW: ")]
                # owner: "NEVER EVER ANY FALLBACKS" -- every spoken line is written by her model. A miss means
                # another topic, never a canned line; up to four topics, then she tries again next pass.
                order = (now[:1] if now else []) + random.sample(facts, len(facts))
                line = None
                # owner, live: "she need to enguague the viewer liek 200% more" -- two of every three lines talk TO
                # chat about what is happening: a question, a vote on her next move, a call to lurkers -- and they go
                # into Twitch chat too, so people can answer in text
                engage = random.random() < 0.67
                for topic in order[:4]:
                    line = fresh(("talk straight to chat about this and pull them in -- ask them a question, let them "
                                  "vote on what you do next, or call out the lurkers to say hi: " + topic) if engage else topic)
                    if line: break
                if line:
                    speak(line)      # spoken only -- owner: "she is fucking posting everything in the twitch chast"
                else: print("no line this pass -- nothing the model wrote passed; trying again", flush=True)
    except Exception:
        s = buf = None                     # drop the dead socket; the next call reconnects
        try: s, buf = session()
        except BaseException: pass
    time.sleep(3)
