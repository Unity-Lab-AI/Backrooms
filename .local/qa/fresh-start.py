"""Make the next start.bat a brand-new run (owner: "next start.bat gets everything bran new the full new stream the
full game load and setup and plays the game").

    python .local/qa/fresh-start.py

1. stops the whole stack (stream, game, models, helpers) and the BRB countdown
2. installs the newest mod build into the Steam mods folder (the game has to be closed for that)
3. arms a fresh colony (new seed and names picked by her voice) and arms GO, so start.bat goes live by itself
4. clears every per-colony flag: explore done, setup hold, asked-for-GO, ladder marks, her pad, the new-colony tries
The trained shells in training/models/ are loaded by start.bat itself (stream/services.py -> training/apply.py).
"""
import hashlib, json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
QA = HERE
DLL = os.path.join(ROOT, "src", "RimroomsAsyncIndustries", "bin", "Release", "net472", "RimroomsAsyncIndustries.dll")
STEAM_DLL = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Rimrooms - Async Industries\1.6\Assemblies\RimroomsAsyncIndustries.dll"
REPO_DLL = os.path.join(ROOT, "Mod", "Rimrooms - Async Industries", "1.6", "Assemblies", "RimroomsAsyncIndustries.dll")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def main():
    print("1. stopping the stack")
    for f in (os.path.join(ROOT, ".local", "obs", "_brb_until"),):
        if os.path.exists(f):
            os.remove(f)                       # ends the countdown loop
    subprocess.run([sys.executable, os.path.join(ROOT, "stream", "services.py"), "stop"],
                   env=dict(os.environ, NO_ANNOUNCE="1"), timeout=180)
    time.sleep(3)

    print("2. installing the mod build")
    if os.path.exists(DLL):
        for dst in (STEAM_DLL, REPO_DLL):
            shutil.copy2(DLL, dst)
        same = md5(DLL) == md5(STEAM_DLL) == md5(REPO_DLL)
        print("   installed, identical copies:", same)
        if not same:
            raise SystemExit("mod copy mismatch -- game may still be running")
    else:
        print("   no build at", DLL)

    print("3. arming a fresh colony and GO")
    open(os.path.join(QA, "_new_colony.request"), "w").write("Async Industries\nforce")
    open(os.path.join(QA, "_go.request"), "w").write("go")

    print("4. clearing per-colony state")
    for f in ("_explore_done.flag", "_setup_hold.flag", "_asked.flag", "_new_colony.request.tries"):
        try:
            os.remove(os.path.join(QA, f))
        except OSError:
            pass
    scratch = os.path.join(ROOT, ".local", "autopilot", "scratch")
    json.dump({"marks": {}}, open(os.path.join(scratch, "ladder.json"), "w"), indent=1)
    open(os.path.join(scratch, "pad.md"), "w", encoding="utf-8").write(
        "FRESH COLONY -- the owner's order, one step at a time (time stays paused until the setup marks are true):\n"
        "[ ] explore: game_set cmd explore with time running, repeat until nothing left\n"
        "[ ] pawn_priorities for every pawn (1s Firefight through Cook, rest customised, no blanks)\n"
        "[ ] game_set cmd assign (food Fine, medicine Best, hostility Attack) -- schedule and drugs come from day one\n"
        "[ ] ladder_set mark pawns_set true and assign_set true\n"
        "[ ] stores: game_set cmd rooms, then stockpile_room on whole rooms (one food, one nofood)\n"
        "[ ] beds, shelves, stove + add_bill CookMealSimple\n"
        "[ ] only then unpause; then crops, hunt, outside, and grow the empire\n")
    st = os.path.join(scratch, "state.json")
    if os.path.exists(st):
        d = json.load(open(st)); d["pending"] = []; json.dump(d, open(st, "w"))

    models = os.path.join(ROOT, "training", "models")
    print("shells ready:", sorted(f for f in os.listdir(models) if f.endswith(".gguf")) if os.path.isdir(models) else "none")
    print("done -- press start.bat")


if __name__ == "__main__":
    main()
