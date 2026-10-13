"""16 GB stress test: load every stream model at once, exercise each, record the VRAM peak.

    python .local/qa/vram-stress.py

Brain (unity-brain, 32K context, keep-alive) on :11434, line writer (unity-local) on :11435, her own voice
(training/voice/serve.py) on :5123 and the webcam renderer (unity-face-sd.py) on :7862, then a burst of real work
on all four together. nvidia-smi is sampled every 0.25 s throughout; the report is written to
.local/qa/vram-stress-<time>.json and printed.
"""
import json, os, subprocess, sys, threading, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OLLAMA = os.path.expandvars(r"%LOCALAPPDATA%/Programs/Ollama/ollama.exe")
samples, stop, marks = [], threading.Event(), []


def vram():
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.split(",")
    return int(out[0]), int(out[1]), int(out[2])


def sampler():
    while not stop.is_set():
        try:
            samples.append((time.time(), *vram()))
        except Exception:
            pass
        time.sleep(0.25)


def mark(label):
    used = vram()[0]
    marks.append((label, used))
    print("%-34s %6d MiB" % (label, used), flush=True)


def post(url, body, timeout=600):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read()


def up(url):
    try:
        urllib.request.urlopen(url, timeout=3).read(); return True
    except Exception:
        return False


def wait(url, secs=300):
    end = time.time() + secs
    while time.time() < end:
        if up(url): return True
        time.sleep(1)
    return False


LONG = ("You are streaming RimWorld. " * 600)          # ~ a long turn's worth of context


def main():
    threading.Thread(target=sampler, daemon=True).start()
    env = dict(os.environ, OLLAMA_FLASH_ATTENTION="1", OLLAMA_KV_CACHE_TYPE="q8_0")
    procs = []
    mark("idle")
    if not up("http://127.0.0.1:11434/api/version"):
        procs.append(subprocess.Popen([OLLAMA, "serve"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        wait("http://127.0.0.1:11434/api/version")
    if not up("http://127.0.0.1:11435/api/version"):
        procs.append(subprocess.Popen([OLLAMA, "serve"], env=dict(env, OLLAMA_HOST="127.0.0.1:11435"),
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        wait("http://127.0.0.1:11435/api/version")
    post("http://127.0.0.1:11434/api/generate", {"model": "unity-brain", "prompt": LONG + "Say hi.", "stream": False,
         "think": False, "keep_alive": "20m", "options": {"num_ctx": 32768, "num_predict": 20}})
    mark("brain loaded (32K ctx, long prompt)")
    BRAIN_LINES = "--brain-lines" in sys.argv    # owner 2026-10-13: "Brain writes lines too" -- no second LLM
    if BRAIN_LINES:
        try: post("http://127.0.0.1:11435/api/generate", {"model": "unity-local", "keep_alive": 0})
        except Exception: pass
    else:
        post("http://127.0.0.1:11435/api/generate", {"model": "unity-local", "prompt": "Say hi to chat.", "stream": False,
             "think": False, "keep_alive": "20m", "options": {"num_predict": 30}})
        mark("+ line writer (unity-local)")
    if not up("http://127.0.0.1:5123/health"):
        procs.append(subprocess.Popen([sys.executable, os.path.join(ROOT, "training/voice/serve.py")], cwd=ROOT,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        wait("http://127.0.0.1:5123/health")
    post("http://127.0.0.1:5123/say", {"text": "Hey chat, the colony is still standing. Barely.", "emotion": "amused"})
    mark("+ her voice (one line)")
    if not up("http://127.0.0.1:7862/"):
        procs.append(subprocess.Popen([sys.executable, os.path.join(ROOT, ".claude/tools/unity-face-sd.py")], cwd=ROOT,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        time.sleep(5)
    post("http://127.0.0.1:7862/sdapi/v1/txt2img", {"prompt": "goth woman streaming, webcam, smiling"})
    mark("+ webcam picture (one render)")
    # everything at once, the way a busy stream moment hits it
    errs = []
    def job(f):
        try: f()
        except Exception as e: errs.append(str(e)[:120])
    jobs = [lambda: post("http://127.0.0.1:11434/api/generate", {"model": "unity-brain", "prompt": LONG + "What now?",
                    "stream": False, "think": False, "keep_alive": "20m", "options": {"num_ctx": 32768, "num_predict": 200}}),
            lambda: post("http://127.0.0.1:11434/api/generate" if "--brain-lines" in sys.argv else "http://127.0.0.1:11435/api/generate",
                    {"model": "unity-brain" if "--brain-lines" in sys.argv else "unity-local", "prompt": "Roast the raiders.",
                     "options": {"num_ctx": 32768 if "--brain-lines" in sys.argv else 8192, "num_predict": 120},
                    "stream": False, "think": False, "keep_alive": "20m"}),
            lambda: post("http://127.0.0.1:5123/say", {"text": "Okay, that raid went exactly as badly as I predicted. "
                    "Which is to say, perfectly badly.", "emotion": "frustrated"}),
            lambda: post("http://127.0.0.1:7862/sdapi/v1/txt2img", {"prompt": "goth woman laughing at screen, webcam"})]
    t0 = time.time()
    ts = [threading.Thread(target=job, args=(j,)) for j in jobs]
    [t.start() for t in ts]; [t.join() for t in ts]
    mark("all four at once (%.0f s)" % (time.time() - t0))
    time.sleep(2)
    stop.set()
    peak = max(samples, key=lambda s: s[1])
    total = samples[0][2]
    ps = json.loads(urllib.request.urlopen("http://127.0.0.1:11434/api/ps").read())["models"]
    try: ps2 = json.loads(urllib.request.urlopen("http://127.0.0.1:11435/api/ps").read())["models"]
    except Exception: ps2 = []
    report = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "total_mib": total, "peak_mib": peak[1],
              "headroom_mib": total - peak[1], "marks": marks, "errors": errs,
              "ollama_models": [{"name": m["name"], "vram_gb": round(m["size_vram"] / 1e9, 2), "total_gb": round(m["size"] / 1e9, 2)}
                                for m in ps + ps2],
              "note": "RimWorld and OBS were NOT running; add their own VRAM to the peak."}
    out = os.path.join(ROOT, ".local", "qa", "vram-stress-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    json.dump(report, open(out, "w"), indent=1)
    print(json.dumps(report, indent=1))
    print("report:", out)


if __name__ == "__main__":
    main()
