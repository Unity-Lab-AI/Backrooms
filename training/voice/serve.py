"""Unity's own voice as a small local server: the model loads once, every line is one POST.

    python training/voice/serve.py [models/unity-voice] [--port 5123]

POST /say  {"text": "...", "emotion": "amused", "intensity": 0.35, "speech_act": "statement"}  -> audio/wav
GET  /health                                                                                    -> {"ok": true}

Listens on 127.0.0.1 only. There is no fallback (owner 2026-10-13: fallbacks are against the
laws): an unknown emotion/act or a delivery outside the pair's recorded support is a 422 with the reason, and the
caller logs it.
"""
import io, json, os, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import soundfile as sf                       # noqa: E402
from dataset_contract import EMOTIONS, FEATURES, SPEECH_ACTS   # noqa: E402
from infer import Voice                      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
CKPT = next((a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()), os.path.join(ROOT, "models", "unity-voice"))
PORT = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else int(os.environ.get("UNITY_VOICE_PORT", "5123"))
VOICE = Voice(CKPT)
LOCK = threading.Lock()                      # one line on the GPU at a time


def render(text, emotion=None, intensity=None, act=None):
    emotion = emotion or "neutral"
    if emotion not in EMOTIONS:
        raise ValueError("unknown emotion %r (trained: %s)" % (emotion, ", ".join(EMOTIONS)))
    if act is not None and act not in SPEECH_ACTS:
        raise ValueError("unknown speech act %r (trained: %s)" % (act, ", ".join(SPEECH_ACTS)))
    with LOCK:
        return VOICE.say(text, emotion, intensity, 1.0, act)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body, kind="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, b'{"ok": true}')
        else:
            self._send(404, b"{}")

    def do_POST(self):
        if self.path != "/say":
            return self._send(404, b"{}")
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0") or 0)) or b"{}")
            wav = render(str(req.get("text", "")), req.get("emotion"), req.get("intensity"), req.get("speech_act"))
        except Exception as error:
            return self._send(422, json.dumps({"error": str(error)[:300]}).encode())
        buf = io.BytesIO()
        sf.write(buf, wav, FEATURES["sample_rate"], format="WAV", subtype="PCM_16")
        self._send(200, buf.getvalue(), "audio/wav")


if __name__ == "__main__":
    print("unity voice serving %s on 127.0.0.1:%d (%s)" % (CKPT, PORT, VOICE.dev), flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
