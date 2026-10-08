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
SEED = 1031  # canonical likeness, see .claude/likeness/LIKENESS.md
NEG = ("neon, glowing, ghost, pale white skin, cartoon, anime, 3d render, blurry, lowres, bad anatomy, "
       "deformed face, extra fingers, watermark, text, child, teen, old")
REF_PROMPT = ("webcam photo of a 25 year old woman, girl next door, natural emo goth style, dark brown hair "
              "with subtle pink streaks and bangs, soft eyeliner, small silver nose stud, black band t-shirt, "
              "warm natural skin tone, gentle smile looking at the camera, sitting at her home desk in front of "
              "a computer monitor showing code, mechanical keyboard, gaming headset around her neck, warm desk "
              "lamp light, cozy bedroom, candid, realistic, detailed face")

_t2i = _i2i = None
_lock = threading.Lock()


def pipes():
    global _t2i, _i2i
    if _t2i is None:
        import torch
        from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
        _t2i = StableDiffusionPipeline.from_single_file(CKPT, torch_dtype=torch.float16, safety_checker=None).to("cuda")
        _t2i.scheduler = DPMSolverMultistepScheduler.from_config(_t2i.scheduler.config)
        _i2i = StableDiffusionImg2ImgPipeline(**_t2i.components)
    return _t2i, _i2i


def render(req):
    import torch
    from PIL import Image
    t2i, i2i = pipes()
    seed = int(req.get("seed") or SEED)
    g = torch.Generator("cuda").manual_seed(seed)
    neg = req.get("negative_prompt") or NEG
    with _lock:
        if req.get("reference") or not os.path.exists(REF):
            img = t2i(prompt=req.get("ref_prompt") or REF_PROMPT, negative_prompt=neg, num_inference_steps=30, guidance_scale=6.5,
                      width=512, height=640, generator=g).images[0]
            os.makedirs(os.path.dirname(REF), exist_ok=True)
            img.save(REF)
            if req.get("reference"):
                return img
        ref = Image.open(REF).convert("RGB")
        prompt = (req.get("prompt") or "").strip() or REF_PROMPT
        strength = float(req.get("strength") or 0.45)
        return i2i(prompt=prompt, image=ref, strength=strength, negative_prompt=neg,
                   num_inference_steps=30, guidance_scale=6.5, generator=g).images[0]


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
            req = json.loads(self.rfile.read(n) or b"{}")
            img = render(req)
            buf = io.BytesIO(); img.save(buf, format="PNG")
            self._send(200, {"images": [base64.b64encode(buf.getvalue()).decode()]})
        except Exception as e:
            self._send(500, {"error": str(e)})


if __name__ == "__main__":
    print("unity-face-sd on 127.0.0.1:%d" % PORT, flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
