"""Restart the whole rig for an update WITHOUT dropping the stream or the colony.

Owner, 2026-10-10: "give warning before restart that brb massive update to my systems game is save so we will be
right back at it".

    python .local/qa/resume-restart.py [minutes-estimate]

1. tells chat (spoken in her voice + one chat line) and puts the BRB scene up with a countdown
2. saves the game as Unity-autosave
3. stops everything except OBS (still streaming) and the Twitch window
4. installs the newest mod build into the Steam mods folder (the game is closed now)
5. arms a resume (load Unity-autosave, never a new colony) and GO, then starts the rig -- GO puts the Live scene back
"""
import hashlib, json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable
SAVE = "Unity-autosave"
DLL = os.path.join(ROOT, "src", "RimroomsAsyncIndustries", "bin", "Release", "net472", "RimroomsAsyncIndustries.dll")
STEAM_DLL = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Rimrooms - Async Industries\1.6\Assemblies\RimroomsAsyncIndustries.dll"
REPO_DLL = os.path.join(ROOT, "Mod", "Rimrooms - Async Industries", "1.6", "Assemblies", "RimroomsAsyncIndustries.dll")
KEEP = ("obs", "twitchui")
NOWIN = {"creationflags": 0x08000000} if os.name == "nt" else {}


def run(*a, timeout=180, env=None):
    return subprocess.run([PY, *a], cwd=ROOT, capture_output=True, text=True, timeout=timeout,
                          env=dict(os.environ, **(env or {})), **NOWIN)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def main():
    minutes = float(sys.argv[1]) if len(sys.argv) > 1 else 12
    print("1. warning chat and BRB")
    run(os.path.join(ROOT, ".claude", "tools", "unity-say.py"),
        "fact: be right back, chat -- I am doing a massive update to my own systems; the game is saved, so we will be "
        "right back at it in a few minutes; say it in my voice, a bit dramatic", timeout=120)
    run(os.path.join(ROOT, ".local", "tw", "twitch-say.py"), "say",
        "BRB: massive update to my systems. The game is saved, we will be right back at it in about %d minutes." % minutes,
        timeout=90)
    try:
        import obsws_python as o
        c = o.ReqClient(host="127.0.0.1", port=4455, timeout=5)
        c.set_current_program_scene("BRB")
    except Exception as e:
        print("   BRB scene not set:", e)
    subprocess.Popen([r"C:\Program Files\Python310\pythonw.exe", os.path.join(ROOT, ".local", "obs", "brb-countdown.py"),
                      str(minutes)], cwd=ROOT, creationflags=0x00000008 | 0x00000200, close_fds=True)

    print("2. saving the game as", SAVE)
    r = run(os.path.join(HERE, "bridge.py"), "call", "rimworld/save_game", json.dumps({"saveName": SAVE}), timeout=120)
    print("   ", (r.stdout or r.stderr)[:160].replace("\n", " "))
    if '"success": false' in (r.stdout or "").lower():
        raise SystemExit("save failed -- not restarting")

    print("3. stopping everything but OBS and the Twitch window")
    status = run(os.path.join(ROOT, "stream", "services.py"), "status").stdout
    for line in status.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "UP" and parts[0] not in KEEP and parts[0] != "rimbridge":
            run(os.path.join(ROOT, "stream", "services.py"), "stop", parts[0])
            print("   stopped", parts[0])
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-Process RimWorldWin64 -EA 0 | Stop-Process -Force"], capture_output=True, **NOWIN)
    time.sleep(6)

    print("4. installing the mod build")
    if os.path.exists(DLL):
        for dst in (STEAM_DLL, REPO_DLL):
            shutil.copy2(DLL, dst)
        print("   identical copies:", md5(DLL) == md5(STEAM_DLL) == md5(REPO_DLL))

    print("5. arming resume + GO and starting")
    open(os.path.join(HERE, "_resume.request"), "w").write(SAVE)
    open(os.path.join(HERE, "_go.request"), "w").write("go")
    for f in ("_asked.flag", "_new_colony.request", "_new_colony.request.tries"):
        try: os.remove(os.path.join(HERE, f))
        except OSError: pass
    run(os.path.join(ROOT, "stream", "services.py"), "start", timeout=900, env={"NO_ADMIN_PAGE": "1"})
    print("done -- the game loop loads", SAVE, "and goes back Live")


if __name__ == "__main__":
    main()
