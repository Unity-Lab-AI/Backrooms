"""Where the camp is, found live from the bridge's own reads -- home map, crew names, camp rectangle.

The old fixed values (Map_0, the founding crew's names, the first camp's rectangle, the gate cell, a 1920x1080
screen) are only fallbacks now. They live in .local/qa/_camp.json when the owner wants to pin one, otherwise the
defaults below apply. Nothing here selects, clicks or moves the camera.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CONF = os.path.join(HERE, "_camp.json")
DEFAULTS = {"home_map": "Map_0", "crew": ["Gee", "Scar", "Unity"], "camp_rect": [118, 96, 196, 176],
            "gate": [149, 146], "screen": [1920, 1080], "render": [3840, 2054], "pad": 30}


def conf():
    out = dict(DEFAULTS)
    try:
        out.update(json.load(open(CONF, encoding="utf-8")))
    except Exception:
        pass
    return out


def players(cols):
    return [c for c in cols or [] if c.get("factionIsPlayer", True)]


def crew_names(cols):
    """Every player colonist's name on any map, or the configured crew when the bridge gave none."""
    names = {c.get("name") for c in players(cols) if c.get("name")}
    return names or set(conf()["crew"])


def home_map(cols):
    """The map holding most of the player's colonists; the configured map when there are none."""
    count = {}
    for c in players(cols):
        if c.get("mapId"): count[c["mapId"]] = count.get(c["mapId"], 0) + 1
    return max(count, key=count.get) if count else conf()["home_map"]


def camp_rect(cols, map_id):
    """(minx, minz, maxx, maxz) around the colonists on map_id, padded; the configured rectangle otherwise."""
    pts = [(c["position"]["x"], c["position"]["z"]) for c in players(cols)
           if c.get("mapId") == map_id and isinstance(c.get("position"), dict)]
    if not pts:
        return tuple(conf()["camp_rect"])
    pad = int(conf()["pad"])
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    return (max(0, min(xs) - pad), max(0, min(zs) - pad), max(xs) + pad, max(zs) + pad)


def screen_size():
    """The primary screen as Windows reports it; the configured size when that cannot be read."""
    try:
        import ctypes
        u = ctypes.windll.user32
        w, h = u.GetSystemMetrics(0), u.GetSystemMetrics(1)
        if w > 0 and h > 0: return w, h
    except Exception:
        pass
    return tuple(conf()["screen"])
