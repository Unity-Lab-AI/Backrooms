"""Fit the stream to Twitch: a true 16:9 canvas with the WHOLE game inside it, nothing cropped.

Owner, 2026-10-10, verbatim: *"as you can see the twitch window is still cut off on the sides"*.
The game runs at 3840x2054 (1.869:1), wider than Twitch's 16:9 player; a 1.869 canvas got its sides cut.
So the canvas is 1920x1080 and the game is fitted (scale-inner) into the full width, centred vertically.
OBS must be CLOSED when this runs -- it rewrites its scene file on exit.
"""
import configparser, glob, json, os, re

C = os.path.expandvars(r"%USERPROFILE%/OBS-Portable/config/obs-studio")
W, H = 1920, 1080

for ini in glob.glob(os.path.join(C, "basic", "profiles", "*", "basic.ini")):
    s = open(ini, encoding="utf-8-sig").read()
    for k, v in (("BaseCX", W), ("BaseCY", H), ("OutputCX", W), ("OutputCY", H)):
        s = re.sub(r"(?m)^%s=\d+" % k, "%s=%d" % (k, v), s)
    open(ini, "w", encoding="utf-8").write(s)
    print("canvas", W, "x", H, "->", ini)

GAME_W, GAME_H = 3840, 2054
fit_h = W * GAME_H / GAME_W                      # 1027 -- full width, bars top and bottom
for f in glob.glob(os.path.join(C, "basic", "scenes", "*.json")):
    d = json.load(open(f, encoding="utf-8"))
    for src in d["sources"]:
        if src["id"] != "scene" or src["name"] != "Live": continue
        for it in src["settings"].get("items", []):
            if it["name"] in ("RimWorld (game only)", "Unity overlay"):
                it["pos"] = {"x": 0.0, "y": round((H - fit_h) / 2, 1)}
                it["bounds_type"] = 2                     # scale to inner bounds: whole image, never cropped
                it["bounds"] = {"x": float(W), "y": round(fit_h, 1)}
                it["bounds_align"] = 0; it["align"] = 5
                it["scale"] = {"x": 1.0, "y": 1.0}
                for c in ("crop_left", "crop_right", "crop_top", "crop_bottom"): it[c] = 0
                print("fitted", it["name"], it["pos"], it["bounds"])
    json.dump(d, open(f, "w", encoding="utf-8"), indent=4)
