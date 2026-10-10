"""Use the leader's and moral guide's abilities as a habit (owner: "now u have a leader u need a morasl
guide and they ahave abilities u want to always use").

    python .local/qa/abilities.py            # Unity: Reassure then Counsel; Gee: Work drive -- on the colonists who need it

Target: the first colonist named by a mental-break-risk alert, else any other colonist. The camera is put
on the target first, then the caster is selected, the ability's gizmo icon clicked (a real click above
its label -- a bridge click on the label does not start targeting) and the target clicked. An ability on
cooldown is reported, not forced.
"""
import importlib.util, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], "--dry"]
spec = importlib.util.spec_from_file_location("empire", os.path.join(HERE, "empire.py"))
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)
PY = sys.executable
CASTS = [("Thing_Human504", "Reassure"), ("Thing_Human504", "Counsel"), ("Thing_Human486", "Work drive")]


def find(n, k):
    if isinstance(n, dict):
        if k in n: return n[k]
        for v in n.values():
            r = find(v, k)
            if r is not None: return r
    return None


def targets():
    cols = {c["name"]: c for c in e.call("rimworld/list_colonists").get("colonists", []) if c.get("humanlike")}
    names = []
    for a in e.call("rimworld/list_alerts").get("alerts", []):
        if "break risk" in a.get("label", ""):
            names += re.findall(r">([^<]+)</color>", a.get("explanation", ""))
    return cols, [n for n in names if n in cols]


def cast(caster, ability, cols, want):
    me = next((c for c in cols.values() if c["pawnId"] == caster), None)
    if not me: return "caster missing"
    tgt = next((cols[n] for n in want if cols[n]["pawnId"] != caster), None) or \
          next((c for c in cols.values() if c["pawnId"] != caster and not c.get("downed")), None)
    x, z = tgt["position"]["x"], tgt["position"]["z"]
    e.call("rimworld/press_cancel"); e.call("rimworld/clear_selection")
    e.call("rimworld/jump_camera_to_cell", {"x": x, "z": z}); time.sleep(0.3)
    cam = e.call("rimworld/get_camera_state")
    x0, x1, z0, z1 = (find(cam, k) for k in ("minX", "maxX", "minZ", "maxZ"))
    px = int((x - x0 + 0.5) * 1600 / (x1 - x0 + 1)); py = int((z1 - z + 0.5) * 856 / (z1 - z0 + 1))
    e.call("rimworld/select_pawn", {"pawnId": caster}); time.sleep(0.3)
    g = e.find(e.layout(), lambda t: t == ability)
    if not g: return "%s: no %s gizmo" % (me["name"], ability)
    r = g["screenRect"]
    subprocess.run([PY, os.path.join(HERE, "game-click.py"), str(int((r["x"] + r["width"] / 2) * 1600 / 1920)),
                    str(int((r["y"] - 20) * 1600 / 1920))], capture_output=True); time.sleep(0.4)
    subprocess.run([PY, os.path.join(HERE, "game-click.py"), str(px), str(py)], capture_output=True); time.sleep(0.4)
    e.call("rimworld/press_cancel")
    job = next((c.get("job") for c in e.call("rimworld/list_colonists").get("colonists", []) if c["pawnId"] == caster), "")
    e.call("rimworld/clear_selection")
    return "%s %s -> %s: caster job now %s" % (me["name"], ability, tgt["name"], job)


if __name__ == "__main__":
    cols, want = targets()
    for caster, ability in CASTS:
        print(cast(caster, ability, cols, want))
