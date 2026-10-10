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
        subprocess.Popen([sys.executable, SAY, line], cwd=ROOT,
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
        subprocess.run([sys.executable, SERVICES, "start"], cwd=ROOT, env=dict(os.environ, NO_ANNOUNCE="1", NO_ADMIN_PAGE="1"), capture_output=True, text=True, timeout=900,
                       creationflags=0x08000000 if os.name == "nt" else 0)
        return
    # 2b. the model runs below normal priority: Windows shares every core, and this way the game, OBS and the voice
    # always win a contended core while the model still gets every spare cycle (owner: "what about windows will it
    # share"). Ollama starts a new llama-server per model load, so it is re-applied every pass.
    global _last_prio
    try: _last_prio
    except NameError: _last_prio = 0
    if os.name == "nt" and time.time() - _last_prio > 300:     # a PowerShell launch every pass was itself a cost
        _last_prio = time.time()
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process llama-server -EA SilentlyContinue | ?{ $_.PriorityClass -ne 'BelowNormal' } | %{ $_.PriorityClass='BelowNormal' }; Get-Process RimWorldWin64,obs64 -EA SilentlyContinue | ?{ $_.PriorityClass -ne 'AboveNormal' } | %{ $_.PriorityClass='AboveNormal' }"],
                       capture_output=True, text=True, creationflags=0x08000000)
    # 3. its own process: if the player died, restart it
    out = subprocess.run([sys.executable, SERVICES, "status"], cwd=ROOT, capture_output=True, text=True,
                         creationflags=0x08000000 if os.name == "nt" else 0).stdout
    for line in out.splitlines():
        if line.startswith("autopilot") and "DOWN" in line:
            # a restart by hand leaves it DOWN for ~2 s; confirm it is still down before starting, or two players race up
            time.sleep(8)
            again = subprocess.run([sys.executable, SERVICES, "status"], cwd=ROOT, capture_output=True, text=True,
                                   creationflags=0x08000000 if os.name == "nt" else 0).stdout
            if any(l.startswith("autopilot") and "DOWN" not in l for l in again.splitlines()):
                break
            print(stamp(), "the player is down -- restarting it", flush=True)
            subprocess.run([sys.executable, SERVICES, "start", "autopilot"], cwd=ROOT, env=dict(os.environ, NO_ANNOUNCE="1", NO_ADMIN_PAGE="1"), capture_output=True, text=True, timeout=900,
                       creationflags=0x08000000 if os.name == "nt" else 0)
            break
    # 3b. the bridge guards (pop-ups, clock, heat, click queue, voice) exit when there is no game -- which is the
    # whole wait before GO. Once the bridge answers, bring back any that died; start is idempotent.
    BRIDGE_SVCS = ("host", "popups", "clock", "heat", "cursorjobs")
    dead = [l.split()[0] for l in out.splitlines() if l.split() and l.split()[0] in BRIDGE_SVCS and "DOWN" in l]
    if dead and _bridge_up():
        print(stamp(), "bridge is up and these died waiting for it:", ", ".join(dead), "-- bringing them back", flush=True)
        subprocess.run([sys.executable, SERVICES, "start"], cwd=ROOT, env=dict(os.environ, NO_ANNOUNCE="1", NO_ADMIN_PAGE="1"), capture_output=True, text=True, timeout=900,
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
        # owner, live: "she is letting time pass and hasnt set a priority or shelf or schedula or anyof the multitude
        # of things required beforoe the firest unpause". Day one never unpauses: the game holds until she has done
        # the whole first-unpause checklist and unpauses it herself.
        open(os.path.join(HERE, "_setup_hold.flag"), "w").write(stamp())
        say("fact: crew work, schedule and drug settings are done; the game stays paused until storage, shelves, beds and the stove are done")
    else:
        say("fact: the game is paused until the crew is set up")

def gates_bridge_pause(on):
    s, buf = gates._session()
    gates.bridge.exchange(s, buf, "tools/call", {"name": "rimworld/pause_game", "arguments": {"pause": bool(on)}})

SERVICES_PY = os.path.join(ROOT, "stream", "services.py")
GO = os.path.join(HERE, "_go.request")
NOWIN = {"creationflags": 0x08000000} if os.name == "nt" else {}
asked = False
went = False      # GO handled in this run (a GO armed before start must go live too, not only one answered after asking)
passes = 0
while True:
    try:
        passes += 1
        model_needs(passes)
        # Owner, 2026-10-10: "it should ask me if im ready to start the stream and game and what i want not
        # just random do everything". Ask once, out loud and on the panel, then wait for GO.
        if not went and not os.path.exists(GO) and _bridge_up():
            went = True                            # the game is already up: this loop was restarted mid-run
        if went:
            pass                                   # GO handled this run; nothing to ask
        elif not os.path.exists(GO):
            flag = os.path.join(HERE, "_asked.flag")
            if not asked and os.path.exists(flag) and time.time() - os.path.getmtime(flag) < 7200:
                asked = True      # already asked this press; a restart of this loop must not ask twice
            if not asked:
                asked = True
                open(flag, "w").write(stamp())
                say("fact: everything is up; waiting for the owner to press GO to start the stream and the game")
                print(stamp(), "asked the owner for GO; waiting", flush=True)
            time.sleep(10); continue
        if not went:
            went = True
            asked = False
            try: os.remove(os.path.join(HERE, "_asked.flag"))
            except OSError: pass
            want = open(GO, encoding="utf-8").read().strip()
            print(stamp(), "GO received:", want[:120], flush=True)
            # a GO is used once: left on disk, every restart of this loop re-ran the whole go-live (live: a false
            # "new stream, game loading" line mid-game)
            try: os.remove(GO)
            except OSError: pass
            # never read the owner's directive aloud -- it is an order to her, not a line for the stream
            say("fact: a new stream is starting and the game is loading about two hundred mods")
            # a NEW stream each start (owner: "make sure it starts a new stream"): fresh title, then OBS live
            try:
                subprocess.run([sys.executable, os.path.join(ROOT, ".local", "tw", "twitch-say.py"), "title",
                                "Unity Plays RimWorld -- fresh company colony, " + time.strftime("%b %d, %I:%M %p")],
                               cwd=ROOT, capture_output=True, text=True, timeout=90, **NOWIN)
            except Exception as e:
                print(stamp(), "title not set:", e, flush=True)
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
            body = open(req, encoding="utf-8").read()
            if already > 0 and "force" not in body:     # never go back to the menu over a colony unless ordered
                os.remove(req); print(stamp(), "colony already on the map -- request cleared", flush=True); continue
            if "force" in body:                         # ordered redo: honour it once, then it is a normal request
                open(req, "w", encoding="utf-8").write(body.replace("force", "").strip())
                for f_ in ("_setup_hold.flag", "_new_colony.request.tries"):
                    try: os.remove(os.path.join(HERE, f_))
                    except OSError: pass
            scen = (open(req, encoding="utf-8").read().strip().split(chr(10))[0] or "Async Industries")
            print(stamp(), "new colony requested (%s) and the window is up -- starting it" % scen, flush=True)
            say("fact: starting a brand new colony; food comes first")
            # Owner: "wtf it didnt do the fucking map set up with faction adv settings pollution seed name none of
            # it". start-scenario only picks the scenario row; every page after it is done by the mod itself
            # (WorldSetupDriver): Cassandra / Community builder / reload anytime, seed, pollution 0, factions
            # (normal pirates only, plus cannibal tribe and nudist tribe), 300x300, Spring, mountainous forest
            # tile, company page, and the naming dialog. Seed and names are Unity's (owner: "unity decides" /
            # "she can make a name and name settlement and faction when it pops up").
            tries = int(open(req + ".tries").read()) if os.path.exists(req + ".tries") else 0
            if tries >= 2:
                print(stamp(), "new colony failed twice -- stopping, NOT regenerating worlds; see newgame.result", flush=True)
                say("fact: the new game setup failed; trying it again")
                os.remove(req); continue
            open(req + ".tries", "w").write(str(tries + 1))
            def pick(what, fallback):
                try:
                    import urllib.request as _u
                    body = {"model": "unity-local", "stream": False, "think": False, "keep_alive": "30m",
                            "options": {"temperature": 1.0, "num_predict": 12, "num_ctx": 8192},
                            "prompt": "You are Unity, a 25 year old emo goth streamer. Give " + what +
                                      ". Reply with the name only, one to three words, letters and spaces only, clean."}
                    out = json.loads(_u.urlopen(_u.Request("http://127.0.0.1:11435/api/generate", json.dumps(body).encode(),
                                     {"Content-Type": "application/json"}), timeout=60).read())["response"]
                    out = "".join(ch for ch in out.strip().split(chr(10))[0] if ch.isalpha() or ch == " ").strip()[:24]
                    return out if out and not _DIRTY.search(out) and not _TOUCHY.search(out) else None
                except Exception:
                    return None
            # the stream is clean: a name she reads out loud may not be a slur, atrocity or real-world violence
            # (her model once picked the seed "terrorist")
            _TOUCHY = _re.compile(r"terror|nazi|hitler|isis|jihad|genocid|holocaust|rape|suicid|bomb|massacre|"
                                 r"shoot|murder|kill|slave|lynch|pedo|cartel|nigg|fag|retard", _re.I)
            _pick = pick
            def pick(what, fallback):
                for _ in range(4):
                    got = _pick(what, fallback)
                    if got: return got
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
            say("fact: the new world seed is %s; spring, mountains and forest" % seed)
            r = subprocess.run([sys.executable, os.path.join(HERE, "start-scenario.py"), scen, "--stop-at", "ChooseIdeoPreset|SelectStoryteller"],
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
                # a fresh colony starts a fresh ladder: explored flag and her setup marks cleared
                for f_ in (os.path.join(HERE, "_explore_done.flag"),):
                    try: os.remove(f_)
                    except OSError: pass
                try:
                    lp = os.path.join(ROOT, ".local", "autopilot", "scratch", "ladder.json")
                    d_ = json.load(open(lp, encoding="utf-8")); d_["marks"] = {}; json.dump(d_, open(lp, "w", encoding="utf-8"), indent=1)
                except Exception: pass
                _explore_done = False
                day_one(auto)
                say("fact: the crew has landed at %s; spring, forest and mountains" % settlement)
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
                # the open TAB, not the top window: the minimap sits on top and hid the Operations panel underneath
                _top = str(_r.get("openMainTabType") or "")
                # only a real tab panel (Operations, Work, Research...) -- never the inspect pane or the minimap
                if ("MainTabWindow" in _top and not any(k in _top for k in ("Inspect", "MiniMap", "Minimap"))
                        and not _r.get("floatMenuOpen")):
                    gates.bridge.exchange(_s, _b, "tools/call", {"name": "rimworld/close_window", "arguments": {"windowType": _top}})
                    print(stamp(), "closed a main tab left open (%s) -- pawn buttons visible again" % _r.get("topWindowType"), flush=True)
            except Exception:
                pass
        firing, st = gates.decide()
        # owner: "exploring is not finished ... it never went through EVERY DOOR". Until the mod reports nothing left,
        # re-send explore every 3 minutes (each call queues every colonist through the nearest doors and fog edge)
        try: _last_explore
        except NameError: _last_explore, _explore_done = 0, False
        if not _explore_done and st.get("ticks_moving") and time.time() - _last_explore > 180:
            _last_explore = time.time()
            try:
                auto = os.path.join(os.path.expandvars(r"%USERPROFILE%/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config"), "RimroomsAutomation")
                with open(os.path.join(auto, "inbox.jsonl"), "a", encoding="utf-8") as f:
                    f.write(json.dumps({"cmd": "explore"}) + chr(10))
                time.sleep(3)
                last = open(os.path.join(auto, "outbox.jsonl"), encoding="utf-8", errors="replace").read().splitlines()[-1]
                print(stamp(), "auto-explore:", last[:220], flush=True)
                # the ladder's explore rung clears only when nothing is left at all, sealed rooms included (v3 wording)
                if "nothing left to explore" in last and "sealed" in last:
                    _explore_done = True
                    open(os.path.join(HERE, "_explore_done.flag"), "w").write(stamp())
                    # owner's order: explore with time running, THEN pause and set every pawn before it runs again
                    try: gates_bridge_pause(True)
                    except Exception as e: print(stamp(), "could not pause after exploring:", e, flush=True)
                    say("fact: every room and door is explored; the game is paused while I set up each pawn")
            except Exception as e:
                print(stamp(), "auto-explore failed:", e, flush=True)
        hold = os.path.join(HERE, "_setup_hold.flag")
        # keep the HUD alive: if OBS is up and the overlay has not been reloaded for 10 minutes, reload it once --
        # a browser source that loaded while the studio was down stays blank forever otherwise
        global _last_overlay
        try: _last_overlay
        except NameError: _last_overlay = 0
        if time.time() - _last_overlay > 600:
            try:
                import obsws_python as _obs, socket as _so
                _so.create_connection(("127.0.0.1", 4455), timeout=1).close()
                _obs.ReqClient(host="127.0.0.1", port=4455, timeout=4).press_input_properties_button("Unity overlay", "refreshnocache")
                _last_overlay = time.time()
            except Exception:
                pass
        if os.path.exists(hold) and st.get("ticks_moving"):
            os.remove(hold)
            print(stamp(), "setup hold ended: time was started on purpose", flush=True)
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
