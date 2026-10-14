"""A viewer asks for a picture -> the picture gets made and shown. The classifier and the bridge between the models.

Owner, 2026-10-14: "there needs to be a classifier and bridge thing between the models people are asking her for a apple
image and she doesnt even know se can make images".

    classify(text, confirm=True) -> the subject of the picture asked for, or None
        1. fast patterns ("draw/paint/make/show/generate ... a picture/image/pic/photo/drawing of X", "X image", "can you draw X")
        2. with confirm=True the small chat model (the voice writer on 11435) is asked to confirm and name the subject; a dead
           model falls back to the pattern's answer, never to nothing (owner: "no fallbacks!" is about invented pictures -- this
           only decides whether to paint what was asked)
        3. the subject must pass the stream filter; nudity and gore asks are refused (None)
    paint(subject, who) -> the PNG path
        the face service's plain text-to-image (no identity, no room) renders the subject; the studio shows it on the
        REPRESENTATION panel with "for @who: subject" and marks the highlight so cam-director leaves it up ~20 s

Used by stream-host.py (every viewer line) and, patterns only, by the autopilot's chat gatherer so her brief says the
picture is being made.
"""
import base64, importlib.util, io, json, os, re, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

_VERB = r"(?:draw|paint|sketch|make|generate|gen|create|render|show|give|send|want|do)"
_NOUN = r"(?:picture|pic|image|img|photo|drawing|painting|art|render)"
# "draw/make/show (me) (a) (picture of) X"
_ASK = re.compile(_VERB + r"\s+(?:me|us|chat)?\s*(?:an?|the|some)?\s*(?:" + _NOUN + r"\s+(?:of)?)?\s*(?P<a>[^?.!,;]{2,60})", re.I)
# "(a) picture of X" anywhere
_ASK2 = re.compile(r"\b" + _NOUN + r"\s+of\s+(?:an?|the)?\s*(?P<a>[^?.!,;]{2,60})", re.I)
# "(make/draw/...) X picture|image" -- the bare form only beside an ask verb
_ASK3 = re.compile(_VERB + r"\s+(?:me|us)?\s*(?:an?|the)?\s*(?P<a>[a-z][a-z0-9' -]{1,40}?)\s+" + _NOUN + r"\b", re.I)
_WORDS = re.compile(r"\b(?:" + _NOUN + r"|draw|paint|sketch|generate|gen)\b", re.I)
_STOP = ("me", "us", "it", "that", "this", "something", "anything", "one", "your", "you", "yourself", "u", "what", "how", "the", "a", "an")
_TAIL = re.compile(r"\s*\b(?:please|pls|plz|now|for me|for us|thanks|thx|lol|pic|picture|image|img|photo)\b\s*$", re.I)
_BAD = re.compile(r"\b(nude|naked|nsfw|topless|porn|sex|boob|tit|nipple|penis|dick|cock|pussy|gore|blood|dead body|corpse|murder|suicide|nazi|swastika|hitler)\b", re.I)


def _clean(s):
    try:
        spec = importlib.util.spec_from_file_location("guards_ia", os.path.join(ROOT, ".local", "autopilot", "guards.py"))
        g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
        return (g.clean_for_stream(s, max_len=80) or "").strip()
    except Exception:
        return re.sub(r"[^A-Za-z0-9 ,'-]", "", s).strip()[:80]


def _pattern(text):
    t = " " + str(text or "").strip() + " "
    if not _WORDS.search(t):
        return None
    for rx in (_ASK2, _ASK3, _ASK):
        m = rx.search(t)
        if not m:
            continue
        a = re.sub(r"\s+", " ", m.group("a")).strip(" '\"")
        a = re.sub(r"^(?:of|an?|the|some)\s+", "", a, flags=re.I).strip()
        for _ in range(3):
            a = _TAIL.sub("", a).strip()
        if len(a) >= 2 and a.lower() not in _STOP and not a.lower().startswith(("what ", "how ", "why ", "is ", "your ")):
            return a[:60]
    return None


def _grounded(subject, text):
    """The model's subject must share a content word with the viewer's own line (no invented pictures)."""
    words = {w for w in re.findall(r"[a-z]{3,}", str(text).lower())}
    return any(w in words for w in re.findall(r"[a-z]{3,}", str(subject).lower()))


def _confirm(text, guess):
    """The small model REFINES a pattern hit ('yes: <subject>' / 'no'); it never creates one (it answered 'dolphin playing'
    to 'i like your picture'). Its subject must be grounded in the line, else the pattern's guess stands; any failure -> the guess."""
    if guess is None:
        return None
    try:
        body = {"model": os.environ.get("UNITY_VOICE_LLM", "unity-local"), "stream": False, "think": False, "keep_alive": -1,
                "options": {"temperature": 0.0, "num_predict": 24, "num_ctx": 2048},
                "prompt": ("A Twitch viewer typed this line in chat: \"%s\". Is the viewer asking for a picture, image, drawing or "
                           "photo to be MADE (not describing one, not asking a question about one)? If yes reply exactly: yes: <what the "
                           "picture should show, 2-6 words>. If no reply exactly: no. Nothing else." % str(text)[:200])}
        req = urllib.request.Request(os.environ.get("UNITY_VOICE_URL", "http://127.0.0.1:11435") + "/api/generate",
                                     data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        out = json.loads(urllib.request.urlopen(req, timeout=20).read())["response"].strip().lower()
        if out.startswith("no"):
            return guess if re.search(r"\b(draw|paint|sketch|make|generate|gen|show me|picture of|image of)\b", text, re.I) else None
        m = re.match(r"yes\s*:?\s*(.+)", out)
        if m:
            s = m.group(1).strip(" .'\"")
            return s[:60] if len(s) >= 2 and _grounded(s, text) else guess
    except Exception:
        pass
    return guess


def classify(text, confirm=True):
    guess = _pattern(text)
    subject = _confirm(text, guess) if confirm else guess
    if not subject:
        return None
    if _BAD.search(subject) or _BAD.search(str(text)):
        return None
    subject = _clean(subject)
    return subject or None


def paint(subject, who="", steps=14):
    """The subject painted plainly and shown on the panel. Returns the PNG path or raises."""
    face = os.environ.get("STUDIO_FACE_URL", "http://127.0.0.1:7862")
    prompt = subject + ", detailed, soft studio lighting, high quality"
    req = urllib.request.Request(face + "/sdapi/v1/txt2img",
                                 data=json.dumps({"prompt": prompt, "plain": True, "steps": int(steps), "width": 512, "height": 512}).encode(),
                                 headers={"Content-Type": "application/json"})
    j = json.loads(urllib.request.urlopen(req, timeout=600).read())
    png = base64.b64decode(j["images"][0])
    out_dir = os.path.join(ROOT, ".claude", ".studio-images"); os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "ask-%d.png" % int(time.time()))
    open(path, "wb").write(png)
    try:
        tok = open(os.path.join(ROOT, ".claude", ".studio-token"), encoding="utf-8").read().strip()
    except OSError:
        tok = ""
    cap = ("for @" + who + ": " if who else "") + subject
    req = urllib.request.Request("http://127.0.0.1:4317/api/cam",
                                 data=json.dumps({"png": base64.b64encode(png).decode(), "caption": cap[:120]}).encode(),
                                 headers={"Content-Type": "application/json", "X-Studio-Token": tok})
    urllib.request.urlopen(req, timeout=60).read()
    try:
        json.dump({"ts": time.time()}, open(os.path.join(ROOT, ".claude", ".cam-highlight.json"), "w"))
    except Exception:
        pass
    return path


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "paint":
        print(paint(" ".join(a[2:]) or "a red apple", a[1] if len(a) > 1 else ""))
    else:
        print(classify(" ".join(a), confirm="--no-confirm" not in a))
