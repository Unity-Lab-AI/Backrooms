"""Write the stream layout into OBS's own files (OBS must be CLOSED): 1920x1080 canvas, the game filling the
overlay's 16:9 game panel edge to edge, the overlay full-frame on top. golive runs this before every launch.

Owner, 2026-10-10, verbatim: *"the fucking window in the twitch skin is still cutting off the sides and bottom of
the screen"* / *"and make sure what ever is grabing rimworld screen displays the full thing edge to edge top to
bottom"* / *"in twitch"*.
The overlay (.claude/tools/stream-overlay.html) draws its game panel at left 12, top 12, 1403x789 = 16:9, the
game's own 3840x2160, so the capture is stretched to exactly that box: no crop, no bars, nothing under the frame.
"""
import glob, json, os, re
C = os.path.expandvars(r"%USERPROFILE%/OBS-Portable/config/obs-studio")
W, H = 1920, 1080
GAME = (12, 12, 1403, 789)
for ini in glob.glob(os.path.join(C, "basic", "profiles", "*", "basic.ini")):
    s = open(ini, encoding="utf-8-sig").read()
    for k, v in (("BaseCX", W), ("BaseCY", H), ("OutputCX", W), ("OutputCY", H)):
        s = re.sub(r"(?m)^%s=\d+" % k, "%s=%d" % (k, v), s)
    open(ini, "w", encoding="utf-8").write(s)
for f in glob.glob(os.path.join(C, "basic", "scenes", "*.json")):
    d = json.load(open(f, encoding="utf-8"))
    for src in d["sources"]:
        if src["id"] != "scene" or src["name"] != "Live": continue
        items = src["settings"].get("items", [])
        for it in items:
            for c in ("crop_left", "crop_right", "crop_top", "crop_bottom"): it[c] = 0
            if it["name"] == "RimWorld (game only)":
                it.update(pos={"x": float(GAME[0]), "y": float(GAME[1])}, align=5, bounds_type=1, bounds_align=0,
                          bounds={"x": float(GAME[2]), "y": float(GAME[3])}, scale={"x": 1.0, "y": 1.0})
            if it["name"] == "Unity overlay":
                it.update(pos={"x": 0.0, "y": 0.0}, align=5, bounds_type=1, bounds_align=0,
                          bounds={"x": float(W), "y": float(H)}, scale={"x": 1.0, "y": 1.0})
        # the overlay draws above the game
        ov = [i for i in items if i["name"] == "Unity overlay"]
        src["settings"]["items"] = [i for i in items if i["name"] != "Unity overlay"] + ov
    json.dump(d, open(f, "w", encoding="utf-8"), indent=4)
print("obs layout: canvas %dx%d, game panel %s, overlay on top" % (W, H, GAME))
