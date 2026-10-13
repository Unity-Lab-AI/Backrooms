"""Unity's webcam renderer with facial retention.

    python .claude/tools/unity-face-sd.py            # serves on 127.0.0.1:7862

Loads the Unity 3D project's realistic-vision checkpoint read-only. The first request with
"reference": true (or no reference on disk) renders Unity's reference portrait with a fixed seed
and saves it to .claude/.studio-images/unity-reference.png. Every later webcam frame is an
img2img pass over that reference at moderate strength with the same seed, so the face stays hers
while the expression and pose change.

API (A1111-shaped): POST /sdapi/v1/txt2img {prompt, negative_prompt?, strength?, seed?, reference?}
"""
import base64, io, json, os, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CKPT = os.path.expanduser(r"~\Desktop\Unity 3D Equational Model\Unity 18+\models\realistic-vision-v51.safetensors")
HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", ".studio-images", "unity-reference.png")
PORT = int(os.environ.get("UNITY_FACE_PORT", "7862"))
# Owner, 2026-10-13: "Webcam pictures on the CPU" -- with the game, OBS and the brain on the 16 GB card, a picture
# rendered on the GPU pushed it past 16 GB and every brain call timed out (she went silent). CPU by default;
# UNITY_FACE_DEVICE=cuda puts it back on the GPU.
DEVICE = os.environ.get("UNITY_FACE_DEVICE", "cpu")
# a CPU step is ~15 s while the game runs; 20 steps keeps a webcam frame near 2 minutes (the studio waits 5)
STEPS = 20 if DEVICE == "cpu" else 30
SEED = 1031  # the owner's cam image is the reference (.claude/likeness/unity-likeness-original-cam.png), 2026-10-13
NEG = ("airbrushed, plastic skin, smooth skin, doll, cgi, render, glowing eyes, bright blue eyes, oversaturated, beauty filter, perfect skin, uncanny, nipples, nude, topless, nsfw, see-through, sheer, wardrobe malfunction, tattoo, tattoos, "
       "t-shirt, sleeves, covered chest, high neckline, hat, beret, cap, beanie, black headset, black headphones, dark skin, pale white skin, black lipstick, heavy goth makeup, neon, cartoon, anime, 3d render, blurry, lowres, bad anatomy, "
       "deformed face, extra fingers, watermark, text, child, teen, old, middle aged, wrinkles, saggy breasts")
# Owner, 2026-10-10: "dont look like her a homie one not like currently your about 37" -- she kept reading
# mid-thirties, so the youth cues are explicit and every ageing cue is in the negatives.
# Owner, 2026-10-13: a gaming webcam, girl next door with a hint of emo, light caucasian skin (not pale), black wavy bob
# with pink ends, busty with lifted cleavage in everyday clothes, no tattoos, no lingerie
# Owner, 2026-10-13: the girl from his cam image at her desk (the original image gen, NOT SDXL -- "its fucked just cookie
# cutting images together"): the whole frame painted over that one reference, everything else is words in the prompt
REF_PROMPT = ("amateur webcam photo of a 25 year old girl next door with a hint of emo at her desk, long straight dark hair with "
              "pink-purple streaks and blunt bangs, a bright pink cat-ear gaming headset with pink cat ears, no hat, black choker, light skin, "
              "busty, realistic")
OUTFITS = {   # owner: bikini-style tops, string straps "ARE A GO", cozy at times; skirts half the time (seen when she stands)
    "triangle": "a tiny black triangle top, deep cleavage", "string-triangle": "a tiny black string triangle top, thin string straps, deep cleavage",
    "string-halter": "a tiny black string halter top, plunging neckline, deep cleavage", "spaghetti-cami": "a tiny white spaghetti strap crop cami, deep cleavage",
    "bandeau": "a black strapless bandeau top, deep cleavage, bare shoulders", "sweetheart": "a red sweetheart crop top, deep cleavage",
    "cutout-halter": "a black keyhole cut-out halter crop top, deep cleavage", "tie-front": "a white tie-front crop top knotted under the bust, deep cleavage",
    "off-shoulder": "a loose black off-shoulder sweater pulled low, deep cleavage", "open-hoodie": "an open grey hoodie over a tiny black bandeau top, deep cleavage",
    "corset": "a black push-up corset top, deep cleavage",
}
BOTTOMS = {"plaid-skirt": "a red plaid pleated mini skirt", "black-skirt": "a black pleated mini skirt", "denim-skirt": "a denim mini skirt",
           "tennis-skirt": "a white tennis skirt", "slip-skirt": "a black satin slip skirt",
           "shorts": "frayed denim short shorts", "jeans": "low-rise ripped jeans", "bike-shorts": "black bike shorts"}
SKIRTS = [k for k in BOTTOMS if k.endswith("skirt")]
GAZE_PC, GAZE_CAM = "looking at her computer monitor, focused on her screen, head turned to her screen", "glancing at the camera"
PROPS = {   # owner: "the images can have details the tesxt model speaks of ie drinking a sods pop , she has a soda pop"
    r"(soda|pop|coke|can of)": "holding a can of soda", r"(coffee|latte)": "holding a mug of coffee", r"tea": "holding a mug of tea",
    r"(snack|chips|crisps)": "eating chips from a bag", r"(pizza)": "eating a slice of pizza", r"(candy|gummy|chocolate)": "eating candy",
    r"(controller|gamepad)": "holding a game controller", r"(phone|text)": "holding her phone", r"(water)": "drinking from a water bottle",
    r"(blanket|cold|freez|cozy|comfy)": "wrapped in a fuzzy blanket", r"(hot|heat|warm in here)": "fanning herself, a strap slipping off her shoulder",
    r"(stretch|tired|long day)": "stretching her arms above her head", r"(dance|song|music)": "dancing in her chair",
    r"(win|won|yes|lets go|let's go)": "both fists raised in victory", r"(oops|died|dead|lost)": "facepalming", r"(cat|kitty)": "a cat on her lap",
}
WARDROBE = os.path.join(HERE, "..", ".studio-images", "wardrobe")   # one reference per everyday top, same face
OUTFIT_STATE = os.path.join(WARDROBE, "_current.json")


def current_outfit(tops):
    """A random top held for a random 10-20 minutes, then a different one (owner, 2026-10-13: "random outfits evry 10
    minutes-20 it changes" -> "Yes, random 10-20 min"). The choice survives a restart of this service."""
    import random, time as _t
    try:
        st = json.load(open(OUTFIT_STATE, encoding="utf-8"))
    except (OSError, ValueError):
        st = {}
    if st.get("top") in tops and _t.time() < st.get("until", 0):
        return st["top"]
    pick = random.choice([t for t in tops if t != st.get("top")] or tops)
    st = {"top": pick, "until": _t.time() + random.randint(600, 1200)}
    try:
        json.dump(st, open(OUTFIT_STATE, "w", encoding="utf-8"))
    except OSError:
        pass
    return pick

_t2i = _i2i = None
_lock = threading.Lock()          # one render (and the one-time pipeline load) at a time
_waiting = threading.Semaphore(3)  # at most this many requests queued or rendering; the rest are refused


CAM = os.path.join(HERE, "..", "likeness", "unity-likeness-original-cam.png")
FACE_SCALE = float(os.environ.get("UNITY_FACE_SCALE", "0.3"))   # light: same girl, but head, gaze and expression free (owner: "her face is not to be locked")
_face_img = []


def face_image():
    if not _face_img:
        from PIL import Image as _I
        _face_img.append(_I.open(CAM).convert("RGB").crop((185, 95, 425, 335)).resize((224, 224)))
    return _face_img[0]


# owner 2026-10-13: "side view mixed gazes mixed clothing, mixed poses, dynamic actions"
ACTIONS = ["leaning in to type on her keyboard", "stretching her arms above her head", "spinning in her gaming chair",
           "one hand on her headset", "sipping from a can of soda", "leaning back with her feet up on the chair",
           "hugging one knee up on the chair", "laughing with her head thrown back", "chin resting in her hand",
           "pointing at her monitor", "twirling a strand of hair", "leaning on the desk with both elbows"]


def compose(req):
    """The whole frame as words: what the caller asked (mood / pose) + her outfit of the moment + where she looks + what
    she is holding (from the line she just said) + who she is. Mood first: CLIP reads only 77 tokens."""
    import random, re as _re
    asked = (req.get("prompt") or "").strip()
    top = current_outfit(sorted(OUTFITS))
    rnd = random.Random(top + str(int(time.time() // 600)))        # the bottom changes with the outfit: a skirt half the time
    bottom = BOTTOMS[rnd.choice(SKIRTS if rnd.random() < 0.5 else [k for k in BOTTOMS if k not in SKIRTS])]
    outfit = OUTFITS[top]
    gaze = GAZE_CAM if random.random() < 0.25 else GAZE_PC          # her PC most of the time, the camera now and then
    said = (req.get("caption") or req.get("said") or "").lower()
    props = [v for k, v in PROPS.items() if _re.search(k, said)][:1]
    action = req.get("action") or random.choice(ACTIONS)
    # CLIP reads 77 tokens: the clothes and skin FIRST (owner: "not nearly enough skin and shoulders and her clevage was all
    # covered up"), then the moment (mood, action, gaze, props), then who she is
    return ", ".join([x for x in ["wearing " + outfit + " and " + bottom, "bright pink cat-ear headset",
                                  "bare shoulders, bare stomach, deep cleavage showing", asked, action, gaze] + props + [REF_PROMPT] if x])


def pipes():
    global _t2i, _i2i
    if _t2i is None:
        import torch
        from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
        # Owner, 2026-10-10: "i think u can double up some major processas and still leave room for rimworld to
        # run 14gb is using alot" -- the GPU had 1 GB of 16 free with the stream, RimWorld, OBS and Ollama on it.
        # A webcam frame is wanted about once every 90 s, so the pipeline lives in system RAM and only the layer
        # being executed rides the GPU: it frees roughly 4 GB of VRAM between frames at the cost of a few seconds
        # per render, which leaves the local model room to load without swapping.
        if DEVICE == "cpu":
            _t2i = StableDiffusionPipeline.from_single_file(CKPT, torch_dtype=torch.float32, safety_checker=None)
            _t2i.scheduler = DPMSolverMultistepScheduler.from_config(_t2i.scheduler.config)
            _t2i.to("cpu")
        else:
            _t2i = StableDiffusionPipeline.from_single_file(CKPT, torch_dtype=torch.float16, safety_checker=None)
            _t2i.scheduler = DPMSolverMultistepScheduler.from_config(_t2i.scheduler.config)
            _t2i.enable_model_cpu_offload()
        # no attention slicing: it replaces the IP-Adapter attention processors (the face lock); offload keeps VRAM low
        # the cam girl's face on every frame (owner 2026-10-13: "cam-1791666443672 girl"): IP-Adapter Plus Face for SD1.5,
        # fed with her face from the cam image, below the beret
        _t2i.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter-plus-face_sd15.safetensors")
        _t2i.set_ip_adapter_scale(FACE_SCALE)
        if getattr(_t2i, "feature_extractor", None) is None:   # from_single_file without a safety checker leaves it out
            from transformers import CLIPImageProcessor
            _t2i.feature_extractor = CLIPImageProcessor()
        if DEVICE != "cpu":
            _t2i.enable_model_cpu_offload()   # again: the adapter's image encoder came after the first offload set-up
        _i2i = StableDiffusionImg2ImgPipeline(**_t2i.components)
    return _t2i, _i2i


def render(req):
    if not _waiting.acquire(blocking=False):
        raise RuntimeError("busy: render queue full")
    try:
        with _lock:
            return _render_locked(req)
    finally:
        _waiting.release()


def _render_locked(req):
    import torch
    from PIL import Image
    t2i, i2i = pipes()
    if DEVICE != "cpu":
        torch.cuda.empty_cache()
    seed = int(req.get("seed") or SEED)
    g = torch.Generator(DEVICE).manual_seed(seed)
    neg = req.get("negative_prompt") or NEG
    if req.get("reference") or not os.path.exists(REF):
        img = t2i(prompt=req.get("ref_prompt") or REF_PROMPT, negative_prompt=neg, num_inference_steps=STEPS, guidance_scale=6.5, ip_adapter_image=face_image(),
                  width=512, height=640, generator=g).images[0]
        os.makedirs(os.path.dirname(REF), exist_ok=True)
        img.save(REF)
        if req.get("reference"):
            return img
    ref = Image.open(REF).convert("RGB")
    prompt = compose(req)
    strength = float(req.get("strength") or 0.7)   # room for a new pose and outfit; the scene and her face hold   # 0.55: the mood shows, the face and the top stay
    out = i2i(prompt=prompt, image=ref, strength=strength, negative_prompt=neg, ip_adapter_image=face_image(),
              num_inference_steps=STEPS, guidance_scale=6.5, generator=g).images[0]
    # her room never changes (owner, 2026-10-13: "so the room is just going to change every time??? i already pioced the
    # room"): outside her zone the picked room's own pixels come back, blended softly, so only she moves
    return Image.composite(out, ref, her_zone(ref))


_zone = {}


def her_zone(ref):
    """Where she may move: her silhouette and the chair in the reference, widened a lot and feathered. Computed once."""
    from PIL import ImageFilter
    key = (os.path.getmtime(REF), ref.size)
    if key not in _zone:
        try:
            from rembg import remove, new_session
            m = remove(ref, session=new_session("isnet-general-use"), only_mask=True).point(lambda v: 255 if v > 30 else 0)
        except Exception:
            from PIL import Image as _I, ImageDraw
            m = _I.new("L", ref.size, 0)
            ImageDraw.Draw(m).rectangle([ref.width // 6, ref.height // 12, ref.width * 5 // 6, ref.height], fill=255)
        _zone.clear()
        _zone[key] = m.filter(ImageFilter.MaxFilter(71)).filter(ImageFilter.GaussianBlur(28))
    return _zone[key]


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        self._send(200, {"state": "ready" if _t2i is not None else "idle", "reference": os.path.exists(REF)})

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 1_000_000:
                return self._send(413, {"error": "request too large"})
            req = json.loads(self.rfile.read(n) or b"{}")
            img = render(req)
            buf = io.BytesIO(); img.save(buf, format="PNG")
            self._send(200, {"images": [base64.b64encode(buf.getvalue()).decode()]})
        except Exception as e:
            self._send(500, {"error": str(e)})


if __name__ == "__main__":
    print("unity-face-sd on 127.0.0.1:%d (%s)" % (PORT, DEVICE), flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
