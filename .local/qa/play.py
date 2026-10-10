"""Play the game in slices and stop the moment something needs a decision.

    python .local/qa/play.py <slices> [--stop "regex"] [--cell x z "label regex"]

Each slice is 10 s at Superfast. After every slice:
  * a modal dialog (nonImmediateDialogWindowOpen) stops it;
  * every new letter is printed with its text. Letters matching INFO are dismissed and play
    continues; anything else (raids, traders, requests, mad animals, quests...) stops it so it can
    be acted on;
  * --stop REGEX also stops when a letter label matches it;
  * --cell X Z REGEX stops when a label on that cell matches.
"""
import json, os, re, subprocess, sys

BR = ".local/qa/bridge.py"
INFO = re.compile(r"(Torrential rain|Fog|Heat wave|Cold snap|Party|Research finished|"
                  r"New lovers|Gift from|Something was heard|A fragment of transmission|Somebody is here|"
                  r"An animal, in here|A missing person|Bandits are spreading|Meteorite|Successful role|Inspired |Inspiration|Look change|frenzy|Disturbing vision|title gained|"
                  r"Faction Contention|Faction Defense|Intercepted|Royal tribute|Paperwork received|"
                  r"A journal for the job|Eclipse|Aurora|Solar flare|Seepage|Something was heard|A fragment|Resocialization offer|Doctor request|Research request|Help wanted|Bandits are spreading|Psychic emitter drone|Look change desired|Roof collapse|self-tamed|New lovers|Bond|joined| join$|Ambrosia sprout|Wanderer|wild man|Herd migration|Thrumbo sighting|became an adult|birthday|Sad wander|Food binge|Insulting spree|Hide in room|Wander|Confused wandering|Tantrum|Corpse obsession|leader speech|emitter shutdown|Faction Contention|Sad wander|Psychic drone|Cold snap|Toxic fallout|Volcanic winter|opportunity|Annual expo|proposal|Breakup|Marriage|pod sprout|Gauranlen|Shooting star|Psychic soothe|Rare thrumbos|Faction Bombardment|Disease: |New Settlement|Diplomatic marriage|binge|Quest available|Insane ramblings|Meteorite|Masterwork|Excellent|Unsolicited delivery|Quest active|Heat wave|Sad wander|Dark visions|Berserk|Psychic pulse|Bandit outpost|Aurora|Animal disease|Conversion|Fun Party|Psychic soothe|corporate supply|Bulk goods trader|goods trader|Farming trader|Combat supplier|Exotic goods|Pirate merchant|Slaver|trader$|Offer from Orbital Traders Hub|Faction Assault|Distress signal|Quest available)", re.I)


def call(tool, args=None):
    out = subprocess.run([sys.executable, BR, "call", tool, json.dumps(args or {})],
                         capture_output=True, text=True, timeout=180).stdout
    return json.loads(out[out.find("{"):]) if "{" in out else {}


def letters():
    r = call("rimworld/list_letters")
    found = []
    def walk(n):
        if isinstance(n, dict):
            if "letters" in n and isinstance(n["letters"], list):
                found.extend(n["letters"])
            else:
                for v in n.values(): walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(r)
    return found


# "keep the focus on your actions too building is something to focus on": with no --follow, frame the
# colonist doing the most watchable thing -- a fight or a patient first, then building, then any work.
RANK = [r"AttackStatic|Wait_Combat|AttackMelee|TendPatient|Rescue|Flee",
        r"FrameConstruct|Build|Construct|Deconstruct|Repair|Uninstall|Install|Smooth|Mine",
        r"DoBill|Hunt|Haul|Sow|Harvest|Cut|Clean|Research|Refuel"]
def busiest():
    cols = []
    def walk(n):
        if isinstance(n, dict):
            if n.get("name") and "job" in n and n.get("humanlike"): cols.append(n)
            for v in n.values(): walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(call("rimworld/list_colonists"))
    for pat in RANK:
        for c in cols:
            if re.search(pat, str(c.get("job") or "")): return c["name"]
    return cols[0]["name"] if cols else "Unity"


def auto_hunt(label, text="", targets=None):
    """Mad animals -> Hunt orders on every animal of that kind; hunters shoot from weapon range.
    Owner: "never letting someone melle person or animal get close to your pawns kill them with range"."""
    m = re.match(r"(?:Mad |Psychic pulse!?: ?)(\w+)", label)
    if not m and label.startswith("Manhunter pack"):
        m = re.search(r"man-hunting ([a-z]+?)s? ", text)      # "a pack of man-hunting crows have"
    if not m: return False
    kind = m.group(1)[:1].upper() + m.group(1)[1:]   # letters say "Mad crow"; the def is Crow
    if label.startswith("Mad ") and targets:
        # one mad animal: hunt only the one the letter points at -- a species-wide Hunt on a
        # "Mad boomalope" enraged the whole herd (2026-10-08)
        for x, z in targets:
            call("rimworld/apply_architect_designator", {"designatorId": "architect-designator:orders:highlight-designator-tutortagnotset-4", "x": x, "z": z})
        print("  -> Hunt ordered on the %d %s the letter names" % (len(targets), kind))
        return True
    o = subprocess.run([sys.executable, ".local/qa/find-things.py", kind, "0", "0", "300", "300"],
                       capture_output=True, text=True, env=dict(__import__("os").environ, ALL="1")).stdout
    cells = [tuple(map(int, c)) for line in o.splitlines() if line.split(" ")[0] == kind
             for c in re.findall(r"\((\d+), (\d+)\)", line)]
    if not cells:   # mod animals are named e.g. "Bird_Crow": any def containing the kind, not a corpse
        cells = [tuple(map(int, c)) for line in o.splitlines()
                 if kind.lower() in line.split(" ")[0].lower() and not line.startswith("Corpse")
                 for c in re.findall(r"\((\d+), (\d+)\)", line)]
    for x, z in cells:
        call("rimworld/apply_architect_designator", {"designatorId": "architect-designator:orders:highlight-designator-tutortagnotset-4", "x": x, "z": z})
    print("  -> Hunt ordered on %d %s" % (len(cells), kind))
    return True   # none alive = already dealt with; the letter is handled either way


def main():
    args = sys.argv[1:]
    slices = int(args[0])
    stop = re.compile(args[args.index("--stop") + 1]) if "--stop" in args else None
    cell = None
    if "--cell" in args:
        i = args.index("--cell")
        cell = (int(args[i + 1]), int(args[i + 2]), re.compile(args[i + 3]))
    # Owner: "kekeep the view port on the action" / "zoom in like i said eyes on action" / "always".
    # --follow PAWN (default Unity) re-centres the camera at Closest zoom before every slice.
    # "zoom out at times to keeep all in fram in context to what ur talking about":
    # --frame X Z W H frames that whole rect instead (a fight, a building, the city).
    follow = args[args.index("--follow") + 1] if "--follow" in args else None
    frame = None
    if "--frame" in args:
        i = args.index("--frame")
        frame = dict(zip(("x", "z", "width", "height"), (int(v) for v in args[i + 1:i + 5])))
    for n in range(slices):
        if frame:
            call("rimworld/frame_cell_rect", frame)
        else:
            call("rimworld/set_camera_zoom", {"zoomRange": "Close"})
            call("rimworld/jump_camera_to_pawn", {"pawnName": follow or busiest()})
        call("rimworld/play_for", {"durationMs": 10000, "speed": "Superfast"})
        # every slice of game time is a stream beat: a spoken line + a fresh game shot (and webcam
        # pictures on events) -- the stream is never quiet while the game moves (owner, 2026-10-09)
        beat_events = []
        ui = call("rimworld/get_ui_state")
        if ui.get("nonImmediateDialogWindowOpen"):
            print("STOP modal:", ui.get("focusedWindowType")); return
        halt = False
        for l in letters():
            label = re.sub(r"<[^>]+>", "", l.get("label") or "")
            text = re.sub(r"<[^>]+>|\(\*[^)]*\)|\(/[^)]*\)", "", (l.get("text") or "")).replace("\n", " ")
            print("LETTER %s | %s" % (label, text[:300]))
            beat_events.append(label)
            if stop and stop.search(label):
                halt = True
            elif re.search(r"Cargo pods|Resource pod|Pods arrived|Gift from|Transport pod", label, re.I):
                call("rimworld/dismiss_letter", {"letterId": l.get("id")})
                call("rimworld/select_architect_designator", {"designatorId": "architect-designator:orders:highlight-designator-tutortagnotset-10"})
                print("  -> allowed everything (unforbid)")
            elif re.match(r"(Mad |Psychic pulse|Manhunter pack)", label) and auto_hunt(label, text, [
                    (t["position"]["x"], t["position"]["z"]) for t in (l.get("lookTargets") or {}).get("targets", [])
                    if t.get("kind") == "pawn" and t.get("position")]):
                call("rimworld/dismiss_letter", {"letterId": l.get("id")})
                # a pack runs faster than hunters walk out: stop so the guns draft (raid.py block) --
                # timber wolves killed Alfonzoid, catatonic and alone, 2026-10-08
                if label.startswith("Manhunter pack"): halt = True
            elif INFO.search(label):
                call("rimworld/dismiss_letter", {"letterId": l.get("id")})
            else:
                halt = True
        BEAT = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "stream-beat.py")]
        outs = [subprocess.run(BEAT + ["--event", ev], capture_output=True, text=True).stdout for ev in beat_events[:2]]
        if not beat_events: outs.append(subprocess.run(BEAT, capture_output=True, text=True).stdout)
        chat = [l for o in outs for l in o.splitlines() if l.startswith("CHAT ")]
        for l in chat: print(l)
        if chat: print("STOP chat"); call("rimworld/set_time_speed", {"speed": "Normal"}); return
        if halt:
            print("STOP letter"); return
        if cell:
            info = json.dumps(call("rimworld/get_cell_info", {"x": cell[0], "z": cell[1]}))
            labels = re.findall(r'"label": "([^"]*)"', info)
            if any(cell[2].search(x) for x in labels):
                print("STOP cell:", [x for x in labels if cell[2].search(x)]); return
    g = call("rimworld/get_game_info")
    print("done", slices, "slices, tick", g.get("ticksGame"))
    # never leave the stream on a paused game between runs (owner, 2026-10-09: "dont leave them in a paused game")
    call("rimworld/set_time_speed", {"speed": "Normal"})
    # the running checklist of every standing order, re-measured after every play run -- it never closes
    # (owner, 2026-10-09: "a running check list that is never complete and is always checking all things are done")
    print(subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "checklist.py")],
                         capture_output=True, text=True).stdout.rstrip())


if __name__ == "__main__":
    main()
