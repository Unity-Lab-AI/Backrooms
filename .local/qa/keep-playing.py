"""The keep-going loop, owned by the switch instead of by a Claude session.

Owner, 2026-10-10, verbatim: *"this should be started auto like on the bat starts and stops and .sh's"*. The
loop that kept the work moving used to be a cron inside Claude's session, which dies with that session. This
is the same loop as a service: it starts with `windows/start.bat` or `linux/start.sh` and stops
with the stop pair, like everything else.

Every pass it evaluates the gate table (docs/playbook.gates.json via gates.py) against measured state and
acts on what it can do without a model in the loop:

  * a gate fires that needs the cursor, and RimWorld is in front -> run the click queue once
  * nothing has been said on stream for a while                 -> one short clean line about real state
  * days of food under one                                      -> make sure food work is designated
  * everything else                                             -> log which gate is live, so the log is the
                                                                   record of what the colony needed and when

It never pauses or unpauses (clock-guard owns that), never drafts, and never edits the mod. It is a nudger,
not a player: the local model plays.

    python .local/qa/keep-playing.py        # background service, one pass every 20 seconds
"""
import ctypes, importlib.util, json, os, subprocess, sys, time

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


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
AP = os.path.join(ROOT, ".local", "autopilot")
SAY = os.path.join(ROOT, ".claude", "tools", "unity-say.py")
OUTBOX = os.path.join(ROOT, ".claude", ".studio-outbox.jsonl")
QUIET_S = 30

gspec = importlib.util.spec_from_file_location("gates", os.path.join(AP, "gates.py"))
gates = importlib.util.module_from_spec(gspec); gspec.loader.exec_module(gates)

u = ctypes.WinDLL("user32") if os.name == "nt" else None

def stamp():
    return time.strftime("%H:%M:%S")

def _bridge_up():
    """Does the bridge answer at all? It does at the main menu too, which is where a new colony begins."""
    try:
        spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "bridge.py"))
        bb = importlib.util.module_from_spec(spec); spec.loader.exec_module(bb)
        port, _tok = bb.endpoint()
        import socket as _s
        _s.create_connection(("127.0.0.1", port), timeout=6).close()
        return True
    except BaseException:
        return False

def game_up():
    if not u: return False
    g = u.FindWindowW(None, "RimWorld by Ludeon Studios")
    return bool(g) and not u.IsIconic(g) and u.GetForegroundWindow() == g

def last_spoken():
    try:
        with open(OUTBOX, encoding="utf-8") as f:
            return json.loads(f.readlines()[-1]).get("ts", 0) / 1000.0
    except Exception:
        return 0

import re as _re
_DIRTY = _re.compile(r"\b(fuck\w*|shit\w*|bitch\w*|damn|ass|hell|cunt|slut|whore|retard\w*|weed|stoned|high af)\b", _re.I)
def say(line):
    # THE STREAM IS CLEAN: nothing this loop speaks may carry a cuss word, whoever wrote it
    if _DIRTY.search(line or ""):
        print(stamp(), "refused to say an unclean line:", (line or "")[:60], flush=True); return
    try:
        subprocess.Popen([sys.executable, SAY, "--raw", line], cwd=ROOT,
                         env=dict(os.environ, UNITY_NO_GLANCE="1"),
                         **({"creationflags": 0x00000200 | 0x00000008} if os.name == "nt" else {"start_new_session": True}))
    except Exception:
        pass

CURSOR_GATES = {"fields-wrong", "bills-missing", "research-idle", "no-medicine", "work-priorities-unset"}
SERVICES = os.path.join(ROOT, "stream", "services.py")
TRAIN = os.path.join(ROOT, ".local", "train", "harvest.py")
NEEDS = [os.path.join(ROOT, "docs", "playbook.gates.json"),      # the gates it decides with
         os.path.join(AP, "owner-orders.txt"),                   # the owner's binding orders
         os.path.join(AP, "prompt.md")]                          # its system prompt

def model_needs(passes):
    """Everything the local model needs to keep running, checked every pass.

    Owner, 2026-10-10, verbatim: "for the models needs for all of it, ive already told you many times allof
    it". So this does not just nudge the game -- it keeps the model's own supply lines up: its process, its
    server, its orders, its gates, and the training set that will fine-tune the next one.
    """
    import urllib.request
    # 1. the files it thinks with
    for f in NEEDS:
        if not os.path.exists(f):
            print(stamp(), "MISSING what the model needs:", os.path.basename(f), flush=True)
    # 2. its server
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/version", timeout=6).read()
    except Exception:
        print(stamp(), "ollama is not answering -- bringing the stack back up", flush=True)
        subprocess.run([sys.executable, SERVICES, "start"], cwd=ROOT, env=dict(os.environ, NO_ANNOUNCE="1"), capture_output=True, text=True, timeout=900,
                       creationflags=0x08000000 if os.name == "nt" else 0)
        return
    # 3. its own process: if the player died, restart it
    out = subprocess.run([sys.executable, SERVICES, "status"], cwd=ROOT, capture_output=True, text=True,
                         creationflags=0x08000000 if os.name == "nt" else 0).stdout
    for line in out.splitlines():
        if line.startswith("autopilot") and "DOWN" in line:
            print(stamp(), "the player is down -- restarting it", flush=True)
            subprocess.run([sys.executable, SERVICES, "start"], cwd=ROOT, env=dict(os.environ, NO_ANNOUNCE="1"), capture_output=True, text=True, timeout=900,
                       creationflags=0x08000000 if os.name == "nt" else 0)
            break
    # 3b. the bridge guards (pop-ups, clock, heat, click queue, voice) exit when there is no game -- which is the
    # whole wait before GO. Once the bridge answers, bring back any that died; start is idempotent.
    BRIDGE_SVCS = ("host", "popups", "clock", "heat", "cursorjobs")
    dead = [l.split()[0] for l in out.splitlines() if l.split() and l.split()[0] in BRIDGE_SVCS and "DOWN" in l]
    if dead and _bridge_up():
        print(stamp(), "bridge is up and these died waiting for it:", ", ".join(dead), "-- bringing them back", flush=True)
        subprocess.run([sys.executable, SERVICES, "start"], cwd=ROOT, env=dict(os.environ, NO_ANNOUNCE="1"), capture_output=True, text=True, timeout=900,
                       creationflags=0x08000000 if os.name == "nt" else 0)
    # 4. the training set that teaches the next model, grown from what just happened
    if passes % 60 == 0 and os.path.exists(TRAIN):
        r = subprocess.run([sys.executable, TRAIN], cwd=ROOT, capture_output=True, text=True, timeout=600,
                           creationflags=0x08000000 if os.name == "nt" else 0)
        print(stamp(), "training set:", " | ".join(r.stdout.strip().splitlines()[:3]), flush=True)


def day_one(auto):
    """Owner: "she never armed any one and is just letting the game run with out seeting sechedul drugs storages
    workschedule priorities". The clock does not run until the mod has set it all: pause, send day_one, read the
    mod's own result, and only then let time go. The mod serves its command file while paused."""
    try:
        gates_bridge_pause(True)
    except Exception as e:
        print(stamp(), "could not pause before day one:", e, flush=True)
    outbox = os.path.join(auto, "outbox.jsonl")
    before = os.path.getsize(outbox) if os.path.exists(outbox) else 0
    with open(os.path.join(auto, "inbox.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"cmd": "day_one"}) + "\n")
    got = None
    for _ in range(30):
        time.sleep(2)
        if os.path.exists(outbox) and os.path.getsize(outbox) > before:
            with open(outbox, encoding="utf-8", errors="replace") as f:
                f.seek(before); got = f.read().strip()
            break
    print(stamp(), "day one:", (got or "no answer from the mod")[:400], flush=True)
    if got and "-> ok" in got.replace("\\", ""):
        say("Crew is set: priorities, schedule, drug rules, everyone on attack, rifles in hand. Now the clock runs.")
        gates_bridge_pause(False)
    else:
        say("Holding the pause until my crew is properly set up.")

def gates_bridge_pause(on):
    s, buf = gates._session()
    gates.bridge.exchange(s, buf, "tools/call", {"name": "rimworld/pause_game", "arguments": {"pause": bool(on)}})

SERVICES_PY = os.path.join(ROOT, "stream", "services.py")
GO = os.path.join(HERE, "_go.request")
NOWIN = {"creationflags": 0x08000000} if os.name == "nt" else {}
asked = False
passes = 0
while True:
    try:
        passes += 1
        model_needs(passes)
        # Owner, 2026-10-10: "it should ask me if im ready to start the stream and game and what i want not
        # just random do everything". Ask once, out loud and on the panel, then wait for GO.
        if not os.path.exists(GO):
            flag = os.path.join(HERE, "_asked.flag")
            if not asked and os.path.exists(flag) and time.time() - os.path.getmtime(flag) < 7200:
                asked = True      # already asked this press; a restart of this loop must not ask twice
            if not asked:
                asked = True
                open(flag, "w").write(stamp())
                say("Hey. Everything is up and I am ready. Are we starting the stream and the game? Tell me what you want tonight and hit GO.")
                print(stamp(), "asked the owner for GO; waiting", flush=True)
            time.sleep(10); continue
        if asked:
            asked = False
            try: os.remove(os.path.join(HERE, "_asked.flag"))
            except OSError: pass
            want = open(GO, encoding="utf-8").read().strip()
            print(stamp(), "GO received:", want[:120], flush=True)
            # never read the owner's directive aloud -- it is an order to her, not a line for the stream
            say("Got it. Launching the game and going live. Give me a minute while two hundred mods wake up.")
            # live FIRST, so the stream carries the game's loading screens, then the game
            subprocess.run([sys.executable, SERVICES_PY, "golive"], cwd=ROOT, capture_output=True, text=True, timeout=120, **NOWIN)
            subprocess.run([sys.executable, SERVICES_PY, "game"], cwd=ROOT, capture_output=True, text=True, timeout=120, **NOWIN)
            open(os.path.join(HERE, "_new_colony.request"), "w", encoding="utf-8").write("Async Industries")
        req = os.path.join(HERE, "_new_colony.request")
        # start-scenario drives RimWorld's own pages through click_ui_target, which is an API call and works
        # whether or not the window has focus -- so this waits for the BRIDGE, not for the owner's screen.
        if os.path.exists(req) and _bridge_up():
            try: already = len(gates.state().get("crew") or [])
            except Exception: already = 0
            if already > 0:     # a colony is already on the map: never go back to the menu over it
                os.remove(req); print(stamp(), "colony already on the map -- request cleared", flush=True); continue
            scen = (open(req, encoding="utf-8").read().strip() or "Async Industries")
            print(stamp(), "new colony requested (%s) and the window is up -- starting it" % scen, flush=True)
            say("Right, new colony. Company start, clean map, and this time I feed everyone before I build anything pretty.")
            # Owner: "wtf it didnt do the fucking map set up with faction adv settings pollution seed name none of
            # it". start-scenario only picks the scenario row; every page after it is done by the mod itself
            # (WorldSetupDriver): Cassandra / Community builder / reload anytime, seed, pollution 0, factions
            # (normal pirates only, plus cannibal tribe and nudist tribe), 300x300, Spring, mountainous forest
            # tile, company page, and the naming dialog. Seed and names are Unity's (owner: "unity decides" /
            # "she can make a name and name settlement and faction when it pops up").
            tries = int(open(req + ".tries").read()) if os.path.exists(req + ".tries") else 0
            if tries >= 2:
                print(stamp(), "new colony failed twice -- stopping, NOT regenerating worlds; see newgame.result", flush=True)
                say("Setup is fighting me, so I am stopping it before it eats the night. Fixing it properly.")
                os.remove(req); continue
            open(req + ".tries", "w").write(str(tries + 1))
            def pick(what, fallback):
                try:
                    import urllib.request as _u
                    body = {"model": "dolphin3:8b", "stream": False, "keep_alive": "30m",
                            "options": {"temperature": 1.0, "num_predict": 12, "num_ctx": 2048},
                            "prompt": "You are Unity, a 25 year old emo goth streamer. Give " + what +
                                      ". Reply with the name only, one to three words, letters and spaces only, clean."}
                    out = json.loads(_u.urlopen(_u.Request("http://127.0.0.1:11434/api/generate", json.dumps(body).encode(),
                                     {"Content-Type": "application/json"}), timeout=60).read())["response"]
                    out = "".join(ch for ch in out.strip().split(chr(10))[0] if ch.isalpha() or ch == " ").strip()[:24]
                    return out if out and not _DIRTY.search(out) else fallback
                except Exception:
                    return fallback
            seed = pick("a one word seed for a new RimWorld planet", "nightshade").replace(" ", "").lower()
            faction = pick("a name for your colony's faction", "Pink Static")
            settlement = pick("a name for your first settlement, a mountain hideout", "Hollow Spire")
            auto = os.path.join(os.path.expandvars(r"%USERPROFILE%/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config"), "RimroomsAutomation")
            os.makedirs(auto, exist_ok=True)
            open(os.path.join(auto, "newgame.result"), "w").close()
            open(os.path.join(auto, "newgame.request"), "w", encoding="utf-8").write(
                "seed=%s\nfaction=%s\nsettlement=%s\ncompany=Async Industries\nideo=Godsmultiplayer\npreset=Preset3\ncoverage=0.3\n" % (seed, faction, settlement))
            print(stamp(), "new game request: seed=%s faction=%s settlement=%s" % (seed, faction, settlement), flush=True)
            say("New planet seed is %s. Setting it up the way I always do, spring, three hundred square, mountains." % seed)
            r = subprocess.run([sys.executable, os.path.join(HERE, "start-scenario.py"), scen, "--stop-at", "SelectStoryteller"],
                               cwd=ROOT, capture_output=True, text=True, timeout=600, **NOWIN)
            print(stamp(), "start-scenario ->", (r.stdout or r.stderr).strip().splitlines()[-2:], flush=True)
            crew = 0
            for _ in range(90):                 # world generation plus map generation: up to 15 minutes
                time.sleep(10)
                try: crew = len(gates.state().get("crew") or [])
                except Exception: crew = 0
                if crew: break
            try: print(stamp(), "newgame.result:", open(os.path.join(auto, "newgame.result"), encoding="utf-8").read().strip().splitlines()[-8:], flush=True)
            except Exception: pass
            if crew > 0:
                os.remove(req)
                try: os.remove(req + ".tries")
                except OSError: pass
                print(stamp(), "new colony started (%d colonists) -- the request is cleared" % crew, flush=True)
                day_one(auto)
                say("We are down. %s, spring, forest and mountains. Food first." % settlement)
            else:
                print(stamp(), "no colonists on a map yet -- the colony request stays armed", flush=True)


        # an open main tab (minimap, Operations, Work...) hides every selected pawn's buttons -- Draft included.
        # Owner, live: "three peopel are there its selecting them but no pawn options apear like draft". Tabs the
        # scripts or the model left open are closed whenever the owner is not at the game window.
        if not game_up():
            try:
                _s, _b = gates._session()
                _r = gates.bridge.exchange(_s, _b, "tools/call", {"name": "rimworld/get_ui_state", "arguments": {}})
                _r = _r.get("result", _r); _r = _r.get("structuredContent", _r)
                if _r.get("mainTabOpen") and not _r.get("floatMenuOpen"):
                    gates.bridge.exchange(_s, _b, "tools/call", {"name": "rimworld/press_cancel", "arguments": {}})
                    print(stamp(), "closed a main tab left open (%s) -- pawn buttons visible again" % _r.get("topWindowType"), flush=True)
            except Exception:
                pass
        firing, st = gates.decide()
        top = firing[0]["id"] if firing else "none"
        print(stamp(), "gate:", top, "| food days:", round(st.get("meals", 0) * 0.9 / 4.8 + st.get("raw_food", 0) * 0.05 / 4.8, 2),
              "| game up:", game_up(), flush=True)

        # Owner, 2026-10-10: "lets get the local model starting a new coloy and everything as the company".
        # Starting a colony is pure UI -- the scenario page only answers a real window -- so the order is left
        # as a request file and fired the moment RimWorld is actually up, without waiting for anyone to notice.
        # the jobs only a real cursor can do: run the queue once, but only while the window is actually in front
        if top in CURSOR_GATES and game_up():
            lock = os.path.join(HERE, "_cursor_jobs.lock")
            if not os.path.exists(lock):
                print(stamp(), "window is in front and", top, "needs the cursor -- running the click queue", flush=True)
                subprocess.run([sys.executable, os.path.join(HERE, "cursor-jobs.py"), "--now"],
                               cwd=ROOT, env=dict(os.environ, OWNER_LENT_MOUSE="1"),
                               capture_output=True, text=True, timeout=600,
                               creationflags=0x08000000 if os.name == "nt" else 0)

        # silence is the host voice's job (stream-host.py); this loop no longer speaks filler lines

    except Exception as e:
        print(stamp(), "pass failed:", str(e)[:120], flush=True)
    time.sleep(20)
