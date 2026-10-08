"""Configure portable OBS for Unity Plays RimWorld over obs-websocket (127.0.0.1:4455).

    python .claude/tools/obs-setup.py            # build scenes + Twitch service (no going live)
    python .claude/tools/obs-setup.py live       # ...then switch to Live and start streaming
    python .claude/tools/obs-setup.py brb|stop   # Be Right Back scene / stop streaming

LAW (CONSTRAINTS §THE STREAM IS CLEAN): viewers only ever see RimWorld. The Live scene is a
Game Capture of the RimWorld window ONLY, the overlay as a Browser Source, and application audio
from RimWorld and Unity's TTS (python). Desktop audio and mic are muted. Never Display Capture.
The stream key is read from .claude/.env and never printed.
"""
import os, sys
import obsws_python as obs

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIKENESS = os.path.join(ROOT, ".claude", "likeness", "unity-likeness-square.png")
RIM_WIN = "RimWorld by Ludeon Studios:UnityWndClass:RimWorldWin64.exe"


def env():
    o = {}
    for l in open(os.path.join(ROOT, ".claude", ".env"), encoding="utf-8"):
        if "=" in l and not l.lstrip().startswith("#"):
            k, v = l.split("=", 1); o[k.strip()] = v.strip()
    return o


def c():
    return obs.ReqClient(host="127.0.0.1", port=4455, timeout=10)


def ensure_scene(cl, name):
    if name not in [s["sceneName"] for s in cl.get_scene_list().scenes]:
        cl.create_scene(name)


def ensure_input(cl, scene, name, kind, settings):
    names = [i["inputName"] for i in cl.get_input_list().inputs]
    if name in names:
        cl.set_input_settings(name, settings, True)
        items = [i["sourceName"] for i in cl.get_scene_item_list(scene).scene_items]
        if name not in items:
            cl.create_scene_item(scene, name, True)
    else:
        cl.create_input(scene, name, kind, settings, True)
    return cl.get_scene_item_id(scene, name).scene_item_id


def setup():
    cl = c()
    e = env()
    # 1080p30 canvas
    cl.set_video_settings(numerator=30, denominator=1, base_width=1920, base_height=1080,
                          out_width=1920, out_height=1080)
    ensure_scene(cl, "Live"); ensure_scene(cl, "BRB")
    gid = ensure_input(cl, "Live", "RimWorld (game only)", "game_capture",
                       {"capture_mode": "window", "window": RIM_WIN, "capture_cursor": True})
    cl.set_scene_item_transform("Live", gid, {"positionX": 0, "positionY": 0,
                                "boundsType": "OBS_BOUNDS_SCALE_INNER", "boundsWidth": 1920, "boundsHeight": 1080})
    oid = ensure_input(cl, "Live", "Unity overlay", "browser_source",
                       {"url": "http://127.0.0.1:4317/", "width": 560, "height": 1150, "reroute_audio": False,
                        "css": "body{background:transparent !important}"})
    cl.set_scene_item_transform("Live", oid, {"positionX": 8, "positionY": 8,
                                "boundsType": "OBS_BOUNDS_SCALE_INNER", "boundsWidth": 330, "boundsHeight": 680})
    ensure_input(cl, "Live", "RimWorld audio", "wasapi_process_output_capture",
                 {"window": RIM_WIN, "priority": 2})
    ensure_input(cl, "Live", "Unity voice", "wasapi_process_output_capture",
                 {"window": ":ConsoleWindowClass:python.exe", "priority": 2})
    bid = ensure_input(cl, "BRB", "BRB image", "image_source", {"file": LIKENESS})
    cl.set_scene_item_transform("BRB", bid, {"positionX": 660, "positionY": 140,
                                "boundsType": "OBS_BOUNDS_SCALE_INNER", "boundsWidth": 600, "boundsHeight": 600})
    tid = ensure_input(cl, "BRB", "BRB text", "text_gdiplus_v3",
                       {"text": "Unity will be right back", "font": {"face": "Arial", "size": 64, "style": "Bold"}})
    cl.set_scene_item_transform("BRB", tid, {"positionX": 560, "positionY": 820})
    # mute everything that is not the game or Unity's voice
    for i in cl.get_input_list().inputs:
        if i["inputKind"] in ("wasapi_output_capture", "wasapi_input_capture"):
            cl.set_input_mute(i["inputName"], True)
    for n in ("Desktop Audio", "Mic/Aux"):
        try: cl.set_input_mute(n, True)
        except Exception: pass
    key = e.get("TWITCH_STREAM_KEY", "")
    if not key or "PASTE" in key:
        raise SystemExit("no TWITCH_STREAM_KEY in .claude/.env")
    cl.set_stream_service_settings("rtmp_common", {"service": "Twitch", "server": "auto", "key": key})
    cl.set_current_program_scene("BRB")
    print("OBS configured: scenes Live + BRB, Twitch service set, desktop/mic muted, on BRB")


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "setup"
    if arg == "setup":
        setup()
    elif arg == "live":
        setup(); cl = c(); cl.set_current_program_scene("Live")
        if not cl.get_stream_status().output_active:
            cl.start_stream()
        print("LIVE on Twitch, Live scene")
    elif arg == "brb":
        c().set_current_program_scene("BRB"); print("BRB scene")
    elif arg == "stop":
        cl = c()
        if cl.get_stream_status().output_active: cl.stop_stream()
        print("stream stopped")


if __name__ == "__main__":
    main()
