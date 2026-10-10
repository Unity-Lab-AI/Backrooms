"""Put the game exactly inside the overlay's game panel, live, through OBS's websocket (no restart, no drop).

Owner, 2026-10-10, verbatim: *"the fucking window in the twitch skin is still cutting off the sides and bottom of
the screen"*. The overlay (.claude/tools/stream-overlay.html) frames the game in #game: left 12, top 12,
1472x789 -- the game's own 1.869:1. The capture was stretched under the whole 1920x1080 frame, so the cam,
chat and bottom bar covered its right side and bottom. This fits the capture to that box (scale-inner) and keeps
the overlay full-frame on top.
"""
import obsws_python as obs
GAME = {"x": 12, "y": 12, "w": 1403, "h": 789}   # 16:9, the game's real 3840x2160: fills the panel edge to edge
c = obs.ReqClient(host="127.0.0.1", port=4455, timeout=5)
scene = "Live"
items = c.get_scene_item_list(scene).scene_items
ids = {i["sourceName"]: i["sceneItemId"] for i in items}
c.set_scene_item_transform(scene, ids["RimWorld (game only)"], {
    "positionX": GAME["x"], "positionY": GAME["y"], "alignment": 5,
    "boundsType": "OBS_BOUNDS_STRETCH", "boundsWidth": GAME["w"], "boundsHeight": GAME["h"], "boundsAlignment": 0,
    "cropLeft": 0, "cropRight": 0, "cropTop": 0, "cropBottom": 0})
c.set_scene_item_transform(scene, ids["Unity overlay"], {
    "positionX": 0, "positionY": 0, "alignment": 5,
    "boundsType": "OBS_BOUNDS_STRETCH", "boundsWidth": 1920, "boundsHeight": 1080})
# overlay above the game
c.set_scene_item_index(scene, ids["Unity overlay"], len(items) - 1)
t = c.get_scene_item_transform(scene, ids["RimWorld (game only)"]).scene_item_transform
print("game now at", t["positionX"], t["positionY"], "size", round(t["width"]), "x", round(t["height"]))
