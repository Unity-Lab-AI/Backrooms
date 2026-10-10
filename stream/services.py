"""One switch for the whole stream: start everything, stop everything, or see what is up.

Owner, 2026-10-10, verbatim: *"still dont have the streamer script working with a easy start stop for it so i
can stop everything and start it with one press only here in the game files"*. Double-click
`Stream Start.cmd` or `Stream Stop.cmd` in the repo root, or run this directly:

    python .local/qa/services.py start     # start every service that is not already running
    python .local/qa/services.py stop      # stop every one of them
    python .local/qa/services.py status    # one line each: UP with its pid, or DOWN
    python .local/qa/services.py restart

Each service is matched by its own command line, so a service already running by any other route is
recognised and never started twice. Nothing here touches RimWorld itself -- the game is the owner's to launch
and to close.
"""
import importlib.util, json, os, re, subprocess, sys, time

# detaching differs per platform: Windows wants creationflags, posix wants its own session
DETACH = ({'creationflags': 0x00000200 | 0x00000008} if os.name == 'nt' else {'start_new_session': True})

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QA = os.path.join(ROOT, ".local", "qa")
PY = sys.executable
NODE = "node"

# name, the fragment that identifies it in a command line, how to start it
SERVICES = [
    ("studio",      ".claude/tools/persona-studio.cjs", [NODE, os.path.join(ROOT, ".claude/tools/persona-studio.cjs")]),
    ("face",        ".claude/tools/unity-face-sd.py",   [PY, os.path.join(ROOT, ".claude/tools/unity-face-sd.py")]),
    ("twitch",      ".claude/tools/twitch-bridge.cjs",  [NODE, os.path.join(ROOT, ".claude/tools/twitch-bridge.cjs")]),
    ("host",        ".local/qa/stream-host.py",         [PY, "-u", os.path.join(QA, "stream-host.py")]),
    ("popups",      ".local/qa/popup-guard.py",         [PY, os.path.join(QA, "popup-guard.py")]),
    ("heat",        ".local/qa/heat-guard.py",          [PY, os.path.join(QA, "heat-guard.py")]),
    ("cursorjobs",  ".local/qa/cursor-jobs.py",         [PY, os.path.join(QA, "cursor-jobs.py")]),
    ("autopilot",   ".local/autopilot/autopilot.py",    [PY, "-u", os.path.join(ROOT, ".local/autopilot/autopilot.py"), "--num-gpu", "0"]),
    ("admin",       ".local/qa/admin.py",               [PY, "-u", os.path.join(HERE, "admin.py")]),
    ("overlay",     ".claude/tools/unity-overlay.py",    [PY, os.path.join(ROOT, ".claude/tools/unity-overlay.py")]),
]
# Not python or node, so they are matched and started by their own executables.
EXTRAS = [
    ("obs", "obs64.exe", [os.path.expandvars(r"%USERPROFILE%/OBS-Portable/bin/64bit/obs64.exe"),
                          "--portable", "--disable-updater", "--minimize-to-tray"],
     os.path.expandvars(r"%USERPROFILE%/OBS-Portable/bin/64bit")),
    ("twitchui", "twitch-profile", [os.path.expandvars(r"%LOCALAPPDATA%/ms-playwright/chromium-1223/chrome-win64/chrome.exe"),
                                    "--user-data-dir=" + os.path.join(ROOT, ".local/twitch-profile"),
                                    "--remote-debugging-port=9333", "--no-first-run",
                                    "--new-window", "https://www.twitch.tv/"], None),
]

OLLAMA = os.path.expandvars(r"%LOCALAPPDATA%/Programs/Ollama/ollama.exe")
if not os.path.exists(OLLAMA): OLLAMA = "ollama"
MODELS = ["dolphin3:8b", "qwen3.6:35b"]      # the voice and the player
VOICE = "dolphin3:8b"

def deps():
    """Bring up what the models need before any service starts.

    Owner, 2026-10-10, verbatim: "it needs to start up the api and shit needed too for the model to run it all
    and all needed models". So: the Ollama server, every model the stack uses (pulled in the background if one
    is missing), and the voice model preloaded so the first line out is not a cold start. The RimBridge API
    lives inside RimWorld, which the owner launches -- nothing here starts the game.
    """
    import urllib.request
    def api(path, data=None, timeout=8):
        req = urllib.request.Request("http://127.0.0.1:11434" + path,
                                     data=(json.dumps(data).encode() if data else None),
                                     headers={"Content-Type": "application/json"})
        return urllib.request.urlopen(req, timeout=timeout).read()
    try:
        api("/api/version"); print("ollama      already up")
    except Exception:
        log = open(os.path.join(QA, "_svc_ollama.log"), "ab", buffering=0)
        subprocess.Popen([OLLAMA, "serve"], stdout=log, stderr=log,
                         **DETACH)
        for _ in range(40):
            time.sleep(1)
            try: api("/api/version"); break
            except Exception: pass
        print("ollama      started")
    have = subprocess.run([OLLAMA, "list"], capture_output=True, text=True).stdout
    for m in MODELS:
        if m.split(":")[0] in have:
            print("model       %s present" % m)
        else:
            log = open(os.path.join(QA, "_svc_pull_%s.log" % m.replace(":", "_")), "ab", buffering=0)
            subprocess.Popen([OLLAMA, "pull", m], stdout=log, stderr=log,
                             **DETACH)
            print("model       %s pulling in the background" % m)
    try:
        api("/api/generate", {"model": VOICE, "prompt": "hi", "stream": False, "keep_alive": "30m",
                              "options": {"num_ctx": 4096, "num_predict": 1}}, timeout=180)
        print("model       %s warm" % VOICE)
    except Exception as e:
        print("model       %s warm-up skipped (%s)" % (VOICE, str(e)[:40]))

WINDOWS = os.name == "nt"

def _ps_lines(pattern):
    """(pid, command line) for every process whose command line matches, on Windows or Linux/macOS."""
    if WINDOWS:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '%s' } | "
                              "ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }" % pattern],
                             capture_output=True, text=True).stdout
    else:
        out = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True).stdout
        keep = []
        for line in out.splitlines():
            line = line.strip()
            if not line: continue
            pid, _, args = line.partition(" ")
            if re.search(pattern, args): keep.append("%s	%s" % (pid, args))
        out = chr(10).join(keep)
    return out

def running():
    """{fragment: [pid, ...]} for every python/node process whose command line carries a fragment."""
    out = _ps_lines("python|node")

    found = {}
    for line in out.splitlines():
        if "\t" not in line: continue
        pid, cmd = line.split("\t", 1)
        cmd = cmd.replace("\\", "/")
        for _, frag, _start in SERVICES:
            if frag in cmd:
                found.setdefault(frag, []).append(int(pid))
    # the extras are not python or node: ask for them by image name
    out2 = _ps_lines("obs64|chrome|chromium")
    for line in out2.splitlines():
        if "	" not in line: continue
        pid, cmd = line.split("	", 1); cmd = cmd.replace("\\", "/")
        for _, frag, _c, _cwd in EXTRAS:
            if frag in cmd: found.setdefault(frag, []).append(int(pid))
    return found

def status():
    found = running()
    for name, frag, _c, _cwd in EXTRAS:
        pids = found.get(frag, [])
        print("%-11s %s" % (name, ("UP   " + " ".join(map(str, pids))) if pids else "DOWN"))
    for name, frag, _ in SERVICES:
        pids = found.get(frag, [])
        print("%-11s %s" % (name, ("UP   " + " ".join(map(str, pids))) if pids else "DOWN"))
    return found

def announce(line):
    """One short line to chat -- owner, 2026-10-10: "tell chat whats up too / not the details tho"."""
    say = os.path.join(ROOT, ".claude", "tools", "unity-say.py")
    try:
        subprocess.Popen([PY, say, "--raw", line], cwd=ROOT,
                         **DETACH,
                         env=dict(os.environ, UNITY_NO_GLANCE="1"))
    except Exception:
        pass

def start():
    found = running()
    env = dict(os.environ, OWNER_LENT_MOUSE="1", PYTHONUNBUFFERED="1", STUDIO_PERSIST="1")
    if os.environ.get("TWITCH_CHANNEL") is None: env["TWITCH_CHANNEL"] = "unityplaysrimworld"
    for name, frag, cmd in SERVICES:
        if found.get(frag):
            print("%-11s already up (%s)" % (name, found[frag][0])); continue
        log = open(os.path.join(QA, "_svc_%s.log" % name), "ab", buffering=0)
        subprocess.Popen(cmd, cwd=ROOT, stdout=log, stderr=log,
                         **DETACH, env=env)
        print("%-11s started" % name); time.sleep(0.6)
    for name, frag, cmd, cwd in EXTRAS:
        if found.get(frag): print("%-11s already up (%s)" % (name, found[frag][0])); continue
        if not os.path.exists(cmd[0]): print("%-11s SKIPPED (not installed: %s)" % (name, cmd[0])); continue
        log = open(os.path.join(QA, "_svc_%s.log" % name), "ab", buffering=0)
        subprocess.Popen(cmd, cwd=cwd or ROOT, stdout=log, stderr=log,
                         **DETACH, env=env)
        print("%-11s started" % name); time.sleep(1.0)
    # the game's own API lives inside RimWorld, which stays the owner's to launch
    try:
        bspec = importlib.util.spec_from_file_location("b", os.path.join(QA, "bridge.py"))
        bb = importlib.util.module_from_spec(bspec); bspec.loader.exec_module(bb); bb.endpoint()
        print("rimbridge   UP   (RimWorld is running and the API answers)")
    except Exception:
        print("rimbridge   DOWN (launch RimWorld yourself -- this switch never touches the game)")

def stop():
    found = running()
    pids = sorted({p for frag, lst in found.items() for p in lst})
    if not pids:
        print("nothing to stop"); return
    if WINDOWS:
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "foreach ($p in %s) { try { Stop-Process -Id $p -Force } catch {} }" % ",".join(map(str, pids))],
                       capture_output=True, text=True)
    else:
        for p in pids:
            try: os.kill(p, 15)
            except Exception: pass
    print("stopped", len(pids), "processes:", " ".join(map(str, pids)))

cmd = (sys.argv[1] if len(sys.argv) > 1 else "status").lower()
if cmd == "start":
    deps(); start(); print("---"); status(); announce("We are live, chat. Everything is up and I am back on the colony.")
elif cmd == "stop":
    announce("That is me done for now, chat. Thanks for hanging out, I will be back."); time.sleep(3); stop()
elif cmd == "restart":
    announce("Quick reboot, chat. Back in a second."); stop(); time.sleep(2); deps(); start(); print("---"); status()
else: status()
