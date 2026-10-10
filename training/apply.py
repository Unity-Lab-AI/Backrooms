"""Load Unity's trained shells into Ollama -- run by stream/services.py on every start, a no-op once applied.

training/models/unity-player.Q4_K_M.gguf  -> Ollama model "unity-player" on :11434 (her player picks it up)
training/models/unity-voice.Q4_K_M.gguf   -> Ollama model "unity-local" on :11435 (the name every voice caller uses;
                                             the untrained voice stays as "unity-local-base")
Each model keeps its base's chat template / renderer / parameters (and the player keeps the vision projector):
the base's own Modelfile is reused with only the weights line swapped. A .applied stamp holds the gguf's sha256,
so a new training run re-applies and an unchanged one is skipped.
"""
import hashlib, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")
NOWIN = {"creationflags": 0x08000000} if os.name == "nt" else {}

JOBS = [  # gguf, base it was trained from, ollama host, target name, backup of the old target
    ("unity-player.Q4_K_M.gguf", "qwen3.6:35b", "127.0.0.1:11434", "unity-player", None),
    ("unity-voice.Q4_K_M.gguf", "qwen3:8b", "127.0.0.1:11435", "unity-local", "unity-local-base"),
]


def ollama(host, *args, inp=None):
    return subprocess.run(["ollama", *args], input=inp, capture_output=True, text=True, timeout=1800,
                          env=dict(os.environ, OLLAMA_HOST=host), **NOWIN)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def apply_one(gguf, base, host, name, backup):
    path = os.path.join(MODELS, gguf)
    if not os.path.exists(path):
        return "%s: not trained yet" % name
    stamp = path + ".applied"
    digest = sha(path)
    if os.path.exists(stamp) and open(stamp).read().strip() == digest and name in ollama(host, "list").stdout:
        return "%s: already applied" % name
    mf = ollama(host, "show", base, "--modelfile").stdout
    if "FROM" not in mf:
        return "%s: base %s missing on %s -- not applied" % (name, base, host)
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
        return "%s: create failed: %s" % (name, (r.stderr or r.stdout)[-300:])
    open(stamp, "w").write(digest)
    return "%s: applied from %s" % (name, gguf)


if __name__ == "__main__":
    for job in JOBS:
        try:
            print("shells     ", apply_one(*job), flush=True)
        except Exception as e:
            print("shells      %s: %s" % (job[3], e), flush=True)
    sys.exit(0)
