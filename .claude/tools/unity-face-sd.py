"""Unity's webcam renderer with facial retention.

    python .claude/tools/unity-face-sd.py            # serves on 127.0.0.1:7862

Loads the Unity 3D project's realistic-vision checkpoint read-only. The first request with
"reference": true (or no reference on disk) renders Unity's reference portrait with a fixed seed
and saves it to .claude/.studio-images/unity-reference.png. Every later webcam frame is an
img2img pass over that reference at moderate strength with the same seed, so the face stays hers
while the expression and pose change.

API (A1111-shaped): POST /sdapi/v1/txt2img {prompt, negative_prompt?, strength?, seed?, reference?}
"""
import base64, io, json, os, sys, threading
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
SEED = 4445  # likeness chosen by the owner 2026-10-13 (.claude/likeness/unity-likeness-2026-10-13.png)
NEG = ("airbrushed, plastic skin, smooth skin, doll, cgi, render, glowing eyes, bright blue eyes, oversaturated, beauty filter, perfect skin, uncanny, bra, lingerie, underwear, nipples, nude, topless, nsfw, see-through, sheer, wardrobe malfunction, tattoo, tattoos, "
       "dark skin, pale white skin, black lipstick, heavy goth makeup, neon, cartoon, anime, 3d render, blurry, lowres, bad anatomy, "
       "deformed face, extra fingers, watermark, text, child, teen, old, middle aged, wrinkles, saggy breasts")
# Owner, 2026-10-10: "dont look like her a homie one not like currently your about 37" -- she kept reading
# mid-thirties, so the youth cues are explicit and every ageing cue is in the negatives.
# Owner, 2026-10-13: a gaming webcam, girl next door with a hint of emo, light caucasian skin (not pale), black wavy bob
# with pink ends, busty with lifted cleavage in everyday clothes, no tattoos, no lingerie
REF_PROMPT = ("amateur webcam photo, real human, natural skin texture with visible pores and small imperfections, her own grey-green eyes, slight webcam grain, natural lighting, unretouched, candid gaming webcam photo, waist-up, a 25 year old woman sitting at her desk gaming, facing the camera, girl next door "
              "with a hint of emo, light caucasian skin with a warm glow, black wavy bob with pink ends, soft dark eyeliner, small black "
              "choker, busty, lifted perky cleavage, fitted black scoop neck tank top, cozy bedroom with string lights, warm lamp light, realistic")
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
        _t2i.enable_attention_slicing()
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
        img = t2i(prompt=req.get("ref_prompt") or REF_PROMPT, negative_prompt=neg, num_inference_steps=STEPS, guidance_scale=6.5,
                  width=512, height=640, generator=g).images[0]
        os.makedirs(os.path.dirname(REF), exist_ok=True)
        img.save(REF)
        if req.get("reference"):
            return img
    ref_path = REF
    try:
        tops = sorted(f for f in os.listdir(WARDROBE) if f.endswith(".png"))
        want = req.get("outfit")
        if want and want + ".png" in tops:
            ref_path = os.path.join(WARDROBE, want + ".png")
        elif tops:
            ref_path = os.path.join(WARDROBE, current_outfit(tops))
    except OSError:
        pass
    ref = Image.open(ref_path).convert("RGB")
    prompt = (req.get("prompt") or "").strip() or REF_PROMPT
    strength = float(req.get("strength") or 0.55)   # 0.55: the mood shows, the face and the top stay
    return i2i(prompt=prompt, image=ref, strength=strength, negative_prompt=neg,
               num_inference_steps=STEPS, guidance_scale=6.5, generator=g).images[0]


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
