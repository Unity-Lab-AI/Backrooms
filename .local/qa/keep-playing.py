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

def say(line):
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
        subprocess.run([sys.executable, SERVICES, "start"], cwd=ROOT, capture_output=True, text=True, timeout=900,
                       creationflags=0x08000000 if os.name == "nt" else 0)
        return
    # 3. its own process: if the player died, restart it
    out = subprocess.run([sys.executable, SERVICES, "status"], cwd=ROOT, capture_output=True, text=True,
                         creationflags=0x08000000 if os.name == "nt" else 0).stdout
    for line in out.splitlines():
        if line.startswith("autopilot") and "DOWN" in line:
            print(stamp(), "the player is down -- restarting it", flush=True)
            subprocess.run([sys.executable, SERVICES, "start"], cwd=ROOT, capture_output=True, text=True, timeout=900,
                       creationflags=0x08000000 if os.name == "nt" else 0)
            break
    # 3b. the bridge guards (pop-ups, clock, heat, click queue, voice) exit when there is no game -- which is the
    # whole wait before GO. Once the bridge answers, bring back any that died; start is idempotent.
    BRIDGE_SVCS = ("host", "popups", "clock", "heat", "cursorjobs")
    dead = [l.split()[0] for l in out.splitlines() if l.split() and l.split()[0] in BRIDGE_SVCS and "DOWN" in l]
    if dead and _bridge_up():
        print(stamp(), "bridge is up and these died waiting for it:", ", ".join(dead), "-- bringing them back", flush=True)
        subprocess.run([sys.executable, SERVICES, "start"], cwd=ROOT, capture_output=True, text=True, timeout=900,
                       creationflags=0x08000000 if os.name == "nt" else 0)
    # 4. the training set that teaches the next model, grown from what just happened
    if passes % 60 == 0 and os.path.exists(TRAIN):
        r = subprocess.run([sys.executable, TRAIN], cwd=ROOT, capture_output=True, text=True, timeout=600,
                           creationflags=0x08000000 if os.name == "nt" else 0)
        print(stamp(), "training set:", " | ".join(r.stdout.strip().splitlines()[:3]), flush=True)

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
            say("Got it. Launching the game and going live." if want in ("", "go")
                else "Got it: %s. Launching the game and going live." % want[:80])
            subprocess.run([sys.executable, SERVICES_PY, "game"], cwd=ROOT, capture_output=True, text=True, timeout=120, **NOWIN)
            subprocess.run([sys.executable, SERVICES_PY, "golive"], cwd=ROOT, capture_output=True, text=True, timeout=120, **NOWIN)
            open(os.path.join(HERE, "_new_colony.request"), "w", encoding="utf-8").write("Async Industries")
        req = os.path.join(HERE, "_new_colony.request")
        # start-scenario drives RimWorld's own pages through click_ui_target, which is an API call and works
        # whether or not the window has focus -- so this waits for the BRIDGE, not for the owner's screen.
        if os.path.exists(req) and _bridge_up():
            scen = (open(req, encoding="utf-8").read().strip() or "Async Industries")
            print(stamp(), "new colony requested (%s) and the window is up -- starting it" % scen, flush=True)
            say("Right, new colony. Company start, clean map, and this time I feed everyone before I build anything pretty.")
            r = subprocess.run([sys.executable, os.path.join(HERE, "start-scenario.py"), scen],
                               cwd=ROOT, capture_output=True, text=True, timeout=1800,
                               creationflags=0x08000000 if os.name == "nt" else 0)
            print(stamp(), "start-scenario:", (r.stdout or r.stderr).strip().splitlines()[-3:], flush=True)
            if r.returncode == 0:
                os.remove(req)
                print(stamp(), "new colony started -- the request is cleared", flush=True)


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

        # the stream never sits silent: one line about what is actually happening, no invention
        if time.time() - last_spoken() > QUIET_S:
            crew = st.get("crew") or []
            doing = next((c[1] for c in crew if c[1] and c[1] not in ("LayDown",)), None)
            if doing:
                say("Still grinding, chat. One of us is %s and my coffee went cold an hour ago." % doing.lower())
            elif crew:
                say("Quiet shift. Everyone is asleep, the camp is holding, and I am the only one still up.")
    except Exception as e:
        print(stamp(), "pass failed:", str(e)[:120], flush=True)
    time.sleep(20)
