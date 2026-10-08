"""Update Unity's stream webcam: python .claude/tools/unity-cam.py <mood> "caption"

mood picks the expression; the base look is always the same girl at the same desk.
Renders through the local Stable Diffusion via the studio's /api/cam. Runs in the background.
"""
import json, subprocess, sys, urllib.request

BASE = ("photo of a 25 year old woman, girl next door, natural goth emo style, dark brown hair with subtle pink streaks, "
        "black band t-shirt, at a home gaming desk, warm desk lamp light, bedroom, candid webcam photo, realistic, ")
MOODS = {
    "chill": "relaxed half smile, smoking a joint, a little smoke, sleepy eyes",
    "hype": "excited wide grin, leaning toward the camera, fist raised",
    "angry": "furious scowl, yelling at the monitor, gripping the headset",
    "focus": "intense focused stare at the screen, typing fast, joint in the ashtray",
    "laugh": "laughing hard, head back, joint between fingers",
    "smug": "smug smirk at the camera, one eyebrow raised, exhaling smoke",
    "scared": "shocked wide eyes, hand over mouth, monitor glow on face",
    "sad": "pouting, chin on hand, glossy eyes",
}


def main():
    mood = sys.argv[1] if len(sys.argv) > 1 else "chill"
    caption = sys.argv[2] if len(sys.argv) > 2 else ""
    if "--now" not in sys.argv:
        subprocess.Popen([sys.executable, __file__, mood, caption, "--now"],
                         creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    prompt = BASE + MOODS.get(mood, mood) + ", photo, detailed face"
    req = urllib.request.Request("http://127.0.0.1:4317/api/cam",
                                 data=json.dumps({"prompt": prompt, "caption": caption, "face": True}).encode(),
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=300).read()


if __name__ == "__main__":
    main()
