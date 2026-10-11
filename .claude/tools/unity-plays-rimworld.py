"""Unity Plays RimWorld -- retired as a separate launcher.

    python .claude/tools/unity-plays-rimworld.py          (or double-click "Unity Plays RimWorld.cmd")

It used to start the face server, studio, chat and overlay on its own and say "we're live" before OBS was
verified. Now it hands over to the one engine, stream/services.py start, which brings the whole rig up and
then waits for GO in the panel before anything goes live.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    print("UNITY PLAYS RIMWORLD -- handing over to stream/services.py start")
    return subprocess.run([sys.executable, os.path.join(ROOT, "stream", "services.py"), "start"], cwd=ROOT).returncode


if __name__ == "__main__":
    sys.exit(main())
