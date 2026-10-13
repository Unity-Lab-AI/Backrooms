"""Unity's webcam renderer, SDXL edition (same HTTP API as unity-face-sd.py).

    python .claude/tools/unity-face-sdxl.py          # serves on 127.0.0.1:7862 (UNITY_FACE_PORT)

Model: RealVisXL V5.0 (photoreal SDXL finetune) + IP-Adapter Plus Face (h94/IP-Adapter sdxl_models)
fed with a crop of her owner-approved face (.claude/likeness/unity-likeness-2026-10-13.png). Every
frame is a fresh txt2img, so the expression and the layout really change while the face stays hers.

API: POST /sdapi/v1/txt2img | /sdapi/v1/img2img
  {prompt?, negative_prompt?, seed?, outfit?, layout?, mood?, width?, height?, steps?, face_scale?}
  -> {"images": [b64png]}
  layout: seated (default) | standing | away
  mood:   a MOODS key (laugh, shocked, wink, pout, ...) or free text
  outfit: a TOPS key (halter-crop, cami-crop, tiefront-crop, pink-halter-crop, keyhole-crop); default
          rotates every OUTFIT_MINUTES
  prompt: when no mood is given, the mood is taken from the caller's prompt (the part after the old
          BASE text that unity-cam.py prepends), so the old callers keep working.
Layout and mood words go at the FRONT of the prompt: CLIP reads only 77 tokens.

VRAM: UNITY_SDXL_OFFLOAD = group (default, layers streamed to the GPU, small peak) | model (whole
models moved on demand, faster, bigger peak) | none (everything on the GPU).
"""
import base64, io, json, os, re, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
LIKENESS = os.path.join(HERE, "..", "likeness", "unity-likeness-original-cam.png")   # owner 2026-10-13: "i want the girl from the cam image i gave you"
PORT = int(os.environ.get("UNITY_FACE_PORT", "7862"))
MODEL = os.environ.get("UNITY_SDXL_MODEL", "SG161222/RealVisXL_V5.0")
OFFLOAD = os.environ.get("UNITY_SDXL_OFFLOAD", "group")
STEPS = int(os.environ.get("UNITY_SDXL_STEPS", "24"))
W, H_ = 832, 1024
SEED = 4445
FACE_SCALE = float(os.environ.get("UNITY_SDXL_FACE", "0.5"))   # identity strength: higher = more her, lower = freer expressions
OUTFIT_MINUTES = 20
FACE_START = float(os.environ.get("UNITY_SDXL_FACE_START", "0.5"))   # fraction of steps before the face adapter joins

# Owner, 2026-10-13: keep the cleavage, about half as much fabric over the chest; underboob/sideboob allowed.
TOPS = {   # owner 2026-10-13: "her clevage is not enough and her tops cover way too much think bikini top"
    "triangle": "tiny black string triangle top, deep cleavage",
    "string-halter": "tiny black string halter top, plunging neckline, deep cleavage",
    "plunge": "tiny white plunge crop top, deep v, deep cleavage",
    "bandeau": "tiny black bandeau tube top, deep cleavage",
    "pink-triangle": "tiny pink string triangle top, deep cleavage",
    "flannel-triangle": "open red flannel shirt over a tiny black string triangle top, deep cleavage",
    "hoodie-bandeau": "unzipped black cropped hoodie over a tiny black bandeau top, deep cleavage",
    # owner 2026-10-13: "remembr shes a streamer noto a call girl and not a only fans chick i leike the loose sweater
    # open front hoodie idea at times and maybe blanket snuggling" -- cozy streamer looks in the same rotation
    "loose-sweater": "loose slouchy oversized black knit sweater falling off one shoulder, low neckline, cleavage",
    "open-hoodie": "oversized open-front grey hoodie over a low-cut black tank top, cleavage",
    "cozy-cardigan": "oversized cozy cream knit cardigan worn loose over a black scoop tank top, cleavage",
}
BOTTOMS = {   # owner 2026-10-13: "More outfits"
    "plaid-skirt": "red plaid pleated mini skirt",
    "black-skirt": "black pleated mini skirt",
    "denim-skirt": "denim mini skirt",
    "denim-shorts": "frayed denim short shorts",
    "ripped-jeans": "low-rise ripped black jeans",
    "bike-shorts": "black bike shorts",
    # owner 2026-10-13: "and skirts 50% of time all styles"
    "tennis-skirt": "white pleated tennis skirt",
    "pencil-skirt": "black fitted pencil skirt",
    "slip-skirt": "black satin slip skirt",
    "wrap-skirt": "floral wrap mini skirt",
    "cord-skirt": "brown corduroy mini skirt",
    "flowy-skirt": "long flowy black boho skirt",
}
SKIRTS = [b for b in BOTTOMS if b.endswith("skirt")]
OUTFIT_STATE = os.path.join(HERE, "..", ".studio-images", "wardrobe", "_sdxl_current.json")


def current_outfit(req):
    """A random top + bottom held for a random 10-20 minutes, then a different pair (owner: "random 10-20 min")."""
    import random
    want = (req.get("outfit") or "").split("/")
    if len(want) == 2 and want[0] in TOPS and want[1] in BOTTOMS:
        return want[0], want[1]
    try:
        st = json.load(open(OUTFIT_STATE, encoding="utf-8"))
    except (OSError, ValueError):
        st = {}
    if st.get("top") in TOPS and st.get("bottom") in BOTTOMS and time.time() < st.get("until", 0):
        return st["top"], st["bottom"]
    top = random.choice([t for t in TOPS if t != st.get("top")])
    pool = SKIRTS if random.random() < 0.5 else [b for b in BOTTOMS if b not in SKIRTS]   # a skirt half the time
    bottom = random.choice([b for b in pool if b != st.get("bottom")] or pool)
    try:
        json.dump({"top": top, "bottom": bottom, "until": time.time() + random.randint(600, 1200)}, open(OUTFIT_STATE, "w", encoding="utf-8"))
    except OSError:
        pass
    return top, bottom
LAYOUTS = {   # owner 2026-10-13: "desk is not to be waist high but instead knee high"
    # owner 2026-10-13: "the desk worked purfect before" (the original week's framing: at her desk, desk and keyboard in front)
    # and "no one looks dirrectly at their webcamera they look at their monitor slighty off angle"
    # owner 2026-10-13: "just make it a side view of the deask and chair with her turned towards webcam not a pink room just
    # normal shit a chick has come on now girl next door" -- one fixed ordinary room, described the same way every frame
    "seated": "side view of her desk and gaming chair, she sits sideways at the desk and has turned in her chair toward the webcam, "
              "seen from head to knees, ROOM",
    "standing": "side view of her desk, she just stood up beside her gaming chair, ROOM, low webcam view from a knee-high desk, she stands right behind the low wooden desk, the desk edge at her knees "
                "in the foreground, full thighs and skirt visible, knees up, behind her a bed, posters and string lights",
    "blanket": "side view of her desk, she is curled up in her gaming chair turned toward the webcam snuggled in a big fuzzy blanket wrapped around "
               "her shoulders, knees pulled up, warm and sleepy-cute, behind her a bed, posters and string lights",
    "away": "very wide shot from a low desk across the room, she is a small full-body figure far away at the back of her bedroom, "
            "{action}, the room fills most of the frame, bed, posters, string lights",
}
BED = "on the bed, kneeling on the bed, lying on the bed, sitting on the bed, legs spread, legs apart, crotch, thighs spread, shorts riding up, "
ROOM = "her ordinary bedroom: a white desk with a monitor, keyboard and a small lamp, plain light beige walls, a bed with a grey duvet behind her, two small framed prints, a window with sheer white curtains, soft daylight"
LAYOUT_NEG = {"seated": BED + "desk at waist height, standing, arms raised, ",
              "standing": BED + "sitting, desk at waist height, long skirt, ",
              "blanket": BED + "standing, no blanket, ",
              "away": "close-up, portrait, headshot, upper body, cowboy shot, medium shot, she fills the frame, "}
# owner 2026-10-13: "poses alway different" -- one picked per frame at the desk (seed-based), unless the caller names one
POSES = ["leaning on one elbow on the desk", "chin resting in her hand", "leaning back in her gaming chair", "leaning in toward her monitor",
         "one hand on her headset", "sipping from a mug", "knees pulled up in her chair", "stretching both arms above her head",
         "twirling a strand of hair", "typing with both hands", "arms folded on the desk", "pointing at her screen"]
AWAY_ACTIONS = ["stretching her arms over her head", "sitting cross-legged on her bed", "dancing in the middle of her room",
                "lying on her bed on her stomach", "fixing her hair in the mirror"]
MOODS = {
    "laugh": "laughing hard, mouth wide open, eyes squeezed shut, head tilted back",
    "laughing": "laughing hard, mouth wide open, eyes squeezed shut, head tilted back",
    "shocked": "shocked screaming face, mouth wide open, eyes wide open, eyebrows raised high, hands on cheeks",
    "scared": "shocked face, mouth open in an O, eyes wide open, eyebrows raised high, hand over mouth",
    "wink": "winking one eye shut at the camera, one eye closed and one eye open, flirty smirk, tongue out",
    "flirty": "flirty wink, one eye closed, playful smirk, finger twirling her hair",
    "pout": "grumpy sulking pout, pouty lips pushed out, frowning, furrowed brows, arms crossed, not smiling",
    "sad": "pouting, bottom lip pushed out, sad puppy eyes, frowning eyebrows",
    "chill": "relaxed half smile, sleepy eyes, chin resting on her hand",
    "hype": "excited wide open-mouth grin, fist raised, leaning toward the camera",
    "angry": "furious scowl, gritted teeth, yelling, eyebrows pulled down",
    "focus": "intense focused stare, lip bitten, narrowed eyes",
    "smug": "smug smirk, one eyebrow raised, arms crossed",
}
LOOK = ("eyes looking off to the side at her monitor, not looking at the camera, 25yo woman, girl next door, hint of emo, light caucasian skin, warm glow, long straight dark hair with pink-purple streaks and blunt bangs, sleek pink cat-ear gaming headset, no hat, "
        " small black choker, busty, lifted perky cleavage, bare midriff")
PHOTO = "amateur webcam photo, real skin, pores, grey-green eyes, grain, unretouched"
NEG = ("nipples, nude, topless, nsfw, see-through, sheer, tattoo, tattoos, dark skin, tan skin, pale skin, "
       "airbrushed, plastic skin, smooth skin, doll, cgi, 3d render, cartoon, anime, painting, beauty filter, glowing eyes, "
       "hat, beret, cap, beanie, blue eyes, blonde, pink walls, pink room, neon, rgb lights, fairy lights, cutout, collage, desk behind her, "
       "deformed, bad anatomy, extra fingers, extra limbs, blurry, lowres, watermark, text, child, old, wrinkles")

_pipe = None
_face = None
_lock = threading.Lock()
_waiting = threading.Semaphore(3)


def face_crop():
    """Square crop around her face in the likeness picture (Haar cascade; centre-top fallback)."""
    from PIL import Image
    img = Image.open(LIKENESS).convert("RGB")
    box = None
    try:
        import cv2, numpy as np
        g = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        c = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        f = c.detectMultiScale(g, 1.1, 5, minSize=(80, 80))
        if len(f):
            x, y, w, h = max(f, key=lambda r: r[2] * r[3])
            cx, cy, s = x + w / 2, y + h / 2, max(w, h) * 1.6   # include hair and bangs
            box = (int(cx - s / 2), int(cy - s / 2), int(cx + s / 2), int(cy + s / 2))
    except Exception:
        pass
    if box is None:
        w, h = img.size
        s = int(w * 0.65)
        box = ((w - s) // 2, int(h * 0.05), (w + s) // 2, int(h * 0.05) + s)
    return img.crop(box).resize((224, 224))


def pipe():
    global _pipe, _face
    if _pipe is None:
        import torch
        from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
        p = StableDiffusionXLPipeline.from_pretrained(MODEL, torch_dtype=torch.float16, variant="fp16")
        p.scheduler = DPMSolverMultistepScheduler.from_config(p.scheduler.config, use_karras_sigmas=True,
                                                              algorithm_type="dpmsolver++")
        p.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter-plus-face_sdxl_vit-h.safetensors",
                          image_encoder_folder="models/image_encoder", torch_dtype=torch.float16)
        p.image_encoder.to(torch.float16)
        p.vae.enable_tiling()
        if OFFLOAD == "group":
            from diffusers.hooks import apply_group_offloading
            dev = torch.device("cuda")
            for name in ("unet", "text_encoder", "text_encoder_2", "image_encoder"):
                apply_group_offloading(getattr(p, name), onload_device=dev, offload_type="leaf_level", use_stream=True)
            p.vae.to(dev)   # small; the pipeline upcasts it to fp32 for decoding, which offload hooks do not survive
        elif OFFLOAD == "model":
            p.enable_model_cpu_offload()
        else:
            p.to("cuda")
        _pipe = p
        _face = face_crop()
    return _pipe


def mood_text(req):
    m = (req.get("mood") or "").strip()
    if m:
        return MOODS.get(m.lower(), m)
    pr = (req.get("prompt") or "").strip()
    if not pr:
        return MOODS["chill"]
    # old callers: BASE + mood + ", photo, detailed face" -> keep only the mood part
    pr = re.sub(r",?\s*photo, detailed face\s*$", "", pr)
    if "realistic, " in pr:
        pr = pr.rsplit("realistic, ", 1)[1]
    for k, v in MOODS.items():
        if pr.strip().lower() == v.lower():
            return v
    return pr


def build_prompt(req):
    layout = (req.get("layout") or "seated").lower()
    if layout not in LAYOUTS:
        layout = "seated"
    seed = int(req.get("seed") or SEED)
    lay = LAYOUTS[layout].replace("ROOM", ROOM).replace("{action}", req.get("action") or AWAY_ACTIONS[seed % len(AWAY_ACTIONS)])
    if layout in ("seated", "blanket"):
        lay = (req.get("pose") or POSES[(seed * 7 + int(time.time() // 60)) % len(POSES)]) + ", " + lay
    top, bottom = current_outfit(req)
    # mood and layout first: the first 75-token chunk carries the most weight (see encode())
    return ", ".join([mood_text(req), lay, TOPS[top], BOTTOMS[bottom], LOOK, PHOTO]), layout


def encode(p, prompt, neg):
    """A1111-style long prompts: each encoder reads 75-token chunks, the chunks are concatenated, so
    nothing past CLIP's 77-token window is dropped. Returns the four SDXL embedding tensors."""
    import torch
    dev = torch.device("cuda")

    def ids(tok, text):
        return tok(text, add_special_tokens=False).input_ids

    toks = [(p.tokenizer, p.text_encoder), (p.tokenizer_2, p.text_encoder_2)]
    n = max(1, *[-(-len(ids(t, x)) // 75) for t, _ in toks for x in (prompt, neg)])
    out = []
    for text in (prompt, neg):
        per_enc, pooled = [], None
        for tok, enc in toks:
            t = ids(tok, text)
            chunks = []
            for k in range(n):
                c = [tok.bos_token_id] + t[k * 75:(k + 1) * 75] + [tok.eos_token_id]
                c += [tok.pad_token_id] * (77 - len(c))
                with torch.no_grad():
                    o = enc(torch.tensor([c], device=dev), output_hidden_states=True)
                chunks.append(o.hidden_states[-2])
                if enc is p.text_encoder_2 and pooled is None:
                    pooled = o[0]
            per_enc.append(torch.cat(chunks, 1))
        out.append((torch.cat(per_enc, -1).to(torch.float16), pooled.to(torch.float16)))
    (pe, pp), (ne, npool) = out
    return pe, ne, pp, npool


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
    p = pipe()
    if req.get("raw"):   # a set piece (the empty room plate): the prompt as given, no face adapter
        p.set_ip_adapter_scale(0.0)
        pe, ne, pp, npool = encode(p, req.get("prompt") or "", req.get("negative_prompt") or "")
        return p(prompt_embeds=pe, negative_prompt_embeds=ne, pooled_prompt_embeds=pp, negative_pooled_prompt_embeds=npool,
                 ip_adapter_image=_face, num_inference_steps=int(req.get("steps") or STEPS), guidance_scale=5.0,
                 width=W, height=H_, generator=torch.Generator("cpu").manual_seed(int(req.get("seed") or SEED))).images[0]
    prompt, layout = build_prompt(req)
    seed = int(req.get("seed") or SEED)
    scale = float(req.get("face_scale") or (0.45 if layout == "away" else FACE_SCALE))
    # The face adapter also drags in the reference's pose, framing and smile. It stays off for the first
    # FACE_START of the steps, so the prompt sets the layout and the expression, then it puts her face on.
    p.set_ip_adapter_scale(0.0)
    start = int(round(float(req.get("face_start") or FACE_START) * int(req.get("steps") or STEPS)))

    def _cb(pipe_, i, t, kw):
        if i + 1 == start:
            pipe_.set_ip_adapter_scale(scale)
        return kw
    g = torch.Generator("cpu").manual_seed(seed)
    neg = req.get("negative_prompt") or (LAYOUT_NEG[layout] + NEG)
    pe, ne, pp, npool = encode(p, prompt, neg)
    return p(prompt_embeds=pe, negative_prompt_embeds=ne, pooled_prompt_embeds=pp, negative_pooled_prompt_embeds=npool,
             ip_adapter_image=_face,
             num_inference_steps=int(req.get("steps") or STEPS), guidance_scale=5.0,
             width=W, height=H_,   # SDXL native size; the studio's 640x768 hint is for SD1.5 and ignored
             generator=g, callback_on_step_end=_cb).images[0]


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        self._send(200, {"state": "ready" if _pipe is not None else "idle", "reference": os.path.exists(LIKENESS)})

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 1_000_000:
                return self._send(413, {"error": "request too large"})
            img = render(json.loads(self.rfile.read(n) or b"{}"))
            buf = io.BytesIO(); img.save(buf, format="PNG")
            self._send(200, {"images": [base64.b64encode(buf.getvalue()).decode()]})
        except Exception as e:
            self._send(500, {"error": str(e)})


if __name__ == "__main__":
    print("unity-face-sdxl on 127.0.0.1:%d (offload=%s)" % (PORT, OFFLOAD), flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
