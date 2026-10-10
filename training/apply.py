"""Load Unity's trained shells into Ollama -- run by stream/services.py on every start, a no-op once applied.

training/models/unity-brain.gguf          -> Ollama model "unity-brain" on :11434 -- the ONE brain (Qwen3.5-9B +
                                             LoRA) that plays, talks, answers chat, writes catch-ups and reads
                                             screenshots. Base "qwen3.5:9b" supplies the template and the vision
                                             projector. When the pod's brain-eval.json (downloaded beside it) says
                                             its voice scored as good or better than today's, a stamp
                                             models/brain-voice.ok is written and services.py points every voice
                                             caller at it too, so only one model sits on the GPU; otherwise the old
                                             voice stays and the brain only plays.
The two older shells below stay for rollback; they are skipped when their gguf is absent.

training/models/unity-player.Q4_K_M.gguf  -> Ollama model "unity-player" on :11434 (her player picks it up)
training/models/unity-voice.Q4_K_M.gguf   -> Ollama model "unity-local" on :11435 (the name every voice caller uses;
                                             the untrained voice stays as "unity-local-base")
Each model keeps its base's chat template / renderer / parameters (and the player keeps the vision projector):
the base's own Modelfile is reused with only the weights line swapped. A .applied stamp holds the gguf's sha256,
so a new training run re-applies and an unchanged one is skipped.
A gguf is only applied when its sha256 matches the expected digest written by the pod (training/models/<kind>.sha256
or <gguf>.sha256, sha256sum format) -- a truncated or substituted download is refused.
Exit status is 0 only when every trained shell is applied and answering; a refusal or failure exits 1.
"""
import hashlib, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")
NOWIN = {"creationflags": 0x08000000} if os.name == "nt" else {}

JOBS = [  # gguf, base it was trained from, ollama host, target name, backup of the old target
    ("unity-brain.gguf", "qwen3.5:9b", "127.0.0.1:11434", "unity-brain", None),
    ("unity-player.Q4_K_M.gguf", "qwen3.6:35b", "127.0.0.1:11434", "unity-player", None),
    ("unity-voice.Q4_K_M.gguf", "qwen3:8b", "127.0.0.1:11435", "unity-local", "unity-local-base"),
]


def ollama(host, *args, inp=None):
    return subprocess.run(["ollama", *args], input=inp, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
                          env=dict(os.environ, OLLAMA_HOST=host), **NOWIN)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def expected(gguf):
    kind = gguf.split(".")[0].replace("unity-", "")   # unity-brain.gguf -> brain.sha256 or unity-brain.gguf.sha256
    for f in (os.path.join(MODELS, kind + ".sha256"), os.path.join(MODELS, gguf + ".sha256")):
        if os.path.exists(f):
            m = re.match(r"\s*([0-9a-fA-F]{64})", open(f, encoding="utf-8", errors="replace").read())
            if m:
                return m.group(1).lower()
    return None


def ready(host, name):
    """The model is listed and actually answers one token."""
    if name not in ollama(host, "list").stdout:
        return False
    r = ollama(host, "run", name, "hi")
    return r.returncode == 0


def apply_one(gguf, base, host, name, backup):
    """(ok, message): ok is False only for a real refusal or failure, not for a shell that is not trained yet."""
    path = os.path.join(MODELS, gguf)
    if not os.path.exists(path):
        return True, "%s: not trained yet" % name
    stamp = path + ".applied"
    digest = sha(path)
    want = expected(gguf)
    if want is None:
        return False, "%s: no expected sha256 beside %s -- not applied" % (name, gguf)
    if digest != want:
        return False, "%s: %s sha256 %s does not match expected %s -- not applied" % (name, gguf, digest[:12], want[:12])
    if os.path.exists(stamp) and open(stamp).read().strip() == digest and name in ollama(host, "list").stdout:
        return True, "%s: already applied" % name
    mf = ollama(host, "show", base, "--modelfile").stdout
    if "FROM" not in mf:
        return False, "%s: base %s missing on %s -- not applied (ollama pull %s first)" % (name, base, host, base)
    # the first FROM is the base's weights; any later FROM (the vision projector) stays
    lines, swapped = [], False
    for ln in mf.splitlines():
        if not swapped and ln.startswith("FROM "):
            ln, swapped = "FROM " + path.replace("\\", "/"), True
        lines.append(ln)
    mfile = os.path.join(MODELS, name + ".Modelfile")
    open(mfile, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    if backup and name in ollama(host, "list").stdout and backup not in ollama(host, "list").stdout:
        ollama(host, "cp", name, backup)
    r = ollama(host, "create", name, "-f", mfile)
    if r.returncode != 0:
        return False, "%s: create failed: %s" % (name, (r.stderr or r.stdout)[-300:])
    if not ready(host, name):
        return False, "%s: created but does not answer -- not stamped" % name
    open(stamp, "w").write(digest)
    return True, "%s: applied from %s" % (name, gguf)


def brain_voice_stamp():
    """models/brain-voice.ok exists only while the applied brain's own eval said its voice is as good or better."""
    ok_path, ev = os.path.join(MODELS, "brain-voice.ok"), os.path.join(MODELS, "brain-eval.json")
    stamp = os.path.join(MODELS, "unity-brain.gguf.applied")
    try:
        import json
        good = os.path.exists(stamp) and json.load(open(ev, encoding="utf-8")).get("voice_replaces_today") is True
    except (OSError, ValueError):
        good = False
    if good:
        open(ok_path, "w").write(open(stamp).read())
    elif os.path.exists(ok_path):
        os.remove(ok_path)
    return "brain voice: %s" % ("replaces today's voice" if good else "not used (today's voice stays)")


if __name__ == "__main__":
    failed = False
    for job in JOBS:
        try:
            ok, msg = apply_one(*job)
        except Exception as e:
            ok, msg = False, "%s: %s" % (job[3], e)
        failed |= not ok
        print("shells     ", msg, flush=True)
    print("shells     ", brain_voice_stamp(), flush=True)
    sys.exit(1 if failed else 0)
