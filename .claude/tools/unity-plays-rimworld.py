"""Unity Plays RimWorld — start the whole stream stack in one go.

    python .claude/tools/unity-plays-rimworld.py          (or double-click "Unity Plays RimWorld.cmd")

Starts, each only if not already running:
  1. Unity's face server  (unity-face-sd.py, :7862)  — webcam frames from .claude/likeness/unity-likeness.png
  2. Local Stable Diffusion (Unity 3D project sd_server.py, :7860) — other images
  3. The studio server     (persona-studio.cjs, :4317, persistent)
  4. The always-on-top overlay window (top-left), then raises RimWorld under it
  5. A first webcam frame and a spoken hello
Twitch chat bridge starts too when TWITCH_CHANNEL is set in .claude/.env.
"""
import os, subprocess, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(ROOT, ".claude", "tools")
SD = os.path.expanduser(r"~\Desktop\Unity 3D Equational Model\Unity 18+\image-server\sd_server.py")
NEW = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)


def up(url):
    try:
        urllib.request.urlopen(url, timeout=2); return True
    except Exception:
        return False


def start(args, cwd=ROOT, env=None):
    e = dict(os.environ); e.update(env or {})
    return subprocess.Popen(args, cwd=cwd, env=e, creationflags=NEW)


def env_file():
    o = {}
    try:
        for l in open(os.path.join(ROOT, ".claude", ".env"), encoding="utf-8"):
            if "=" in l and not l.strip().startswith("#"):
                k, v = l.split("=", 1); o[k.strip()] = v.strip()
    except OSError:
        pass
    return o


def main():
    print("UNITY PLAYS RIMWORLD — starting the stream stack")
    if not up("http://127.0.0.1:7862/"):
        print(" face server..."); start([sys.executable, os.path.join(TOOLS, "unity-face-sd.py")])
    if os.path.exists(SD) and not up("http://127.0.0.1:7860/status"):
        print(" stable diffusion..."); start([sys.executable, SD], cwd=os.path.dirname(SD))
    if not up("http://127.0.0.1:4317/"):
        print(" studio..."); start(["node", os.path.join(TOOLS, "persona-studio.cjs")], env={"STUDIO_PERSIST": "1"})
        for _ in range(30):
            if up("http://127.0.0.1:4317/"): break
            time.sleep(1)
    channel = env_file().get("TWITCH_CHANNEL")
    if channel:
        print(" twitch chat bridge for #" + channel); start(["node", os.path.join(TOOLS, "twitch-bridge.cjs"), channel])
    print(" overlay..."); subprocess.run([sys.executable, os.path.join(TOOLS, "unity-overlay.py")])
    for _ in range(120):
        if up("http://127.0.0.1:7862/"): break
        time.sleep(2)
    subprocess.run([sys.executable, os.path.join(TOOLS, "unity-cam.py"), "chill", "live: Unity Plays RimWorld"])
    subprocess.run([sys.executable, os.path.join(TOOLS, "unity-say.py"), "Hey chat, Unity here. We're live. Let's play some RimWorld."])
    print("live. Overlay top-left, RimWorld underneath.")


if __name__ == "__main__":
    main()
