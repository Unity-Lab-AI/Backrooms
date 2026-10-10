"""Collect screenshot -> question -> answer examples for the brain's screen-reading, from the live game.

    python training/collect_screens.py [--shots 40] [--every 45]

Each shot: the game's own screenshot (rimworld/take_screenshot) plus, at the same moment, the game's own state
(colonists, letters, alerts, UI). Questions are only about things the screen always shows -- the colonist bar,
the letter stack on the right, the alert list, the pause/speed readout, the open window -- and every answer comes
from that state, never from a guess at the pixels. Read-only bridge calls: nothing is clicked, nothing changes
in the colony. Output: .local/train/screens/<n>.png + <n>.json; build_brain.py picks them up as "screen" rows.
Run it while the game is up (between streams or while it plays); it never touches the stream.
"""
import argparse, importlib.util, json, os, re, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, ".local", "train", "screens")
sys.path.insert(0, os.path.join(ROOT, ".local", "autopilot"))


def bridge():
    spec = importlib.util.spec_from_file_location("ap_tools", os.path.join(ROOT, ".local", "autopilot", "tools.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.Bridge()


def plain(s):
    return re.sub(r"<[^>]+>", "", str(s or "")).strip()


def qa_from(state):
    cols = [c for c in state["colonists"].get("colonists", []) if not c.get("dead")]
    letters = [plain(l.get("label")) for l in state["letters"].get("letters", [])][:8]
    alerts = [plain(a.get("label") or a.get("title")) for a in state["alerts"].get("alerts", [])][:8]
    ui = state["ui"]
    qa = [{"q": "Who is in the colonist bar at the top?", "a": ", ".join(c["name"] for c in cols) or "Nobody."},
          {"q": "How many colonists are there?", "a": str(len(cols))},
          {"q": "Is the game paused?", "a": "Yes, it is paused." if ui.get("paused") else "No, it is running at %s." % ui.get("timeSpeed", "normal speed")}]
    qa.append({"q": "What letters are waiting on the right?", "a": ("; ".join(letters) + ".") if letters else "No letters."})
    qa.append({"q": "What alerts are showing?", "a": ("; ".join(alerts) + ".") if alerts else "No alerts."})
    for c in cols:
        if c.get("downed") or c.get("mentalState") or c.get("drafted"):
            what = "downed" if c.get("downed") else ("in a %s" % plain(c["mentalState"])) if c.get("mentalState") else "drafted"
            qa.append({"q": "Anything wrong with %s?" % c["name"], "a": "%s is %s." % (c["name"], what)})
    return qa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, default=40)
    ap.add_argument("--every", type=int, default=45, help="seconds between shots")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    b = bridge()
    start = len([f for f in os.listdir(OUT) if f.endswith(".json")])
    for k in range(a.shots):
        st = {"colonists": b.call("rimworld/list_colonists", {}), "letters": b.call("rimworld/list_letters", {"limit": 15}),
              "alerts": b.call("rimworld/list_alerts", {"limit": 20}), "ui": b.call("rimworld/get_ui_state", {})}
        shot = b.call("rimworld/take_screenshot", {"suppressMessage": True})
        st2 = b.call("rimworld/list_colonists", {})
        if not (isinstance(shot, dict) and shot.get("path") and os.path.exists(shot["path"])) or any("error" in v for v in st.values() if isinstance(v, dict)):
            print("shot %d skipped (bridge said: %s)" % (k, str(shot)[:120]), flush=True)
        elif [c.get("name") for c in st2.get("colonists", [])] != [c.get("name") for c in st["colonists"].get("colonists", [])]:
            print("shot %d skipped (colony changed during the shot)" % k, flush=True)
        else:
            n = "%05d" % (start + k)
            shutil.copyfile(shot["path"], os.path.join(OUT, n + ".png"))
            json.dump({"image": n + ".png", "at": time.time(), "qa": qa_from(st)}, open(os.path.join(OUT, n + ".json"), "w", encoding="utf-8"), indent=1)
            print("shot %s saved" % n, flush=True)
        time.sleep(a.every)


if __name__ == "__main__":
    main()
