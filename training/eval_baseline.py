"""Score TODAY's voice on the held-out voice lines, so the pod can tell whether the new brain is as good or better.

    python training/eval_baseline.py     -> training/data/brain/baseline_voice.json
    then: python training/build_brain.py && python training/check_brain.py   (the manifest must include it)

Asks the voice model exactly the way the stream does (stream-host fresh(): system + "ONE spoken line" user turn,
temperature 0.9, num_ctx 8192, no thinking) on the voice server (127.0.0.1:11435, model unity-local), SAMPLES
lines per prompt with fixed seeds. Run it between streams: it is ~130 short generations on the voice server and
would otherwise compete with live lines. It starts nothing and stops nothing; if the server is down it says so.
"""
import json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "brain")
sys.path.insert(0, os.path.join(HERE, "pod"))
import voice_score  # noqa: E402

URL = os.environ.get("BASELINE_URL", "http://127.0.0.1:11435")
MODEL = os.environ.get("BASELINE_MODEL", "unity-local")
SEEDS = (11, 22)


def gen(msgs, seed):
    body = {"model": MODEL, "messages": msgs, "stream": False, "think": False, "keep_alive": "10m",
            "options": {"temperature": 0.9, "num_ctx": 8192, "num_predict": 60, "seed": seed}}
    req = urllib.request.Request(URL + "/api/chat", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=120).read())["message"]["content"]


def main():
    rows = [json.loads(l) for l in open(os.path.join(OUT, "eval_voice.jsonl"), encoding="utf-8") if l.strip()]
    try:
        urllib.request.urlopen(URL + "/api/version", timeout=5).read()
    except Exception as e:
        sys.exit("voice server %s not answering (%s) -- nothing scored" % (URL, e))
    all_rows, lines = [], []
    for s in SEEDS:
        for r in rows:
            lines.append(gen(r["messages"][:2], s))
            all_rows.append(r)
    res = voice_score.score(all_rows, lines)
    res.update(model=MODEL, seeds=list(SEEDS), lines=[voice_score.first_line(l) for l in lines])
    json.dump(res, open(os.path.join(OUT, "baseline_voice.json"), "w", encoding="utf-8"), indent=1)
    print("today's voice: pass %.3f distinct %.3f words %.1f n %d" % (res["pass"], res["distinct"], res["words"], res["n"]))


if __name__ == "__main__":
    main()
