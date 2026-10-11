"""Check training/data/brain/ (built by build_brain.py) before it goes anywhere near a pod. Reads files only.

    python training/check_brain.py     -> prints every failure, exit 1 if any

  - MANIFEST.json matches every file byte for byte (the pod refuses a digest it was not launched with)
  - every tool episode (play / highlight / image) passes check_player's rules against the CURRENT tools.json
  - every voice / chat line passes check_voice's stream rules (clean, first person, no invented facts, short)
  - every spoken argument, caption, write-up and screen answer passes the live stream filter
  - none of the stale habit lines anywhere in her turns
  - the held-out voice and tool evals share nothing with train.jsonl
  - the owner's handle appears in no file (read from the secret files at check time, never printed)
"""
import hashlib, importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "data", "brain")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


cp = load("check_player", os.path.join(HERE, "check_player.py"))
cv = load("check_voice", os.path.join(HERE, "check_voice.py"))
TOOLS = json.load(open(os.path.join(OUT, "tools.json"), encoding="utf-8"))
cp.TOOLS = TOOLS
cp.SCHEMA = {t["function"]["name"]: t["function"]["parameters"] for t in TOOLS}
STALE = re.compile(r"(once it stands|after the kill\b|we just landed and i am about to explore everything|"
                   r"we just landed and i am reading every door)", re.I)
KINDS = {"play", "knowledge", "voice", "chat", "writeup", "highlight", "image", "screen"}


def voice_fails(m):
    """check_voice's per-line rules for one system/user/assistant row."""
    u, line = m[1]["content"], m[2]["content"]
    errs = []
    if u.startswith("ONE spoken line"):
        g = re.search(r'about this and nothing else: "(.*)"\. Say it IN YOUR OWN WORDS', u, re.S)
        if not g:
            return ["unparsable voice prompt"]
        fact = g.group(1)
        who = re.match(r"(\w+) just joined the stream; greet", fact) or re.match(r"viewer (\w+) said in chat", fact)
        if who and who.group(1).lower() not in line.lower():
            errs.append("chat line lacks the viewer's name")
    else:
        fact = re.sub(r"^This is what is happening right now: |\. Talk to your chat about it.*$|^Say exactly this.*?keep every name, number and plan in it: ", "", u, flags=re.S)
        if not cv.uv.keeps_facts(fact, line):
            errs.append("announce drops the facts")
    return errs + cv.fresh_fail(line, fact)


def her_text(ep):
    """Every string of hers: narration plus every argument of every call."""
    for m in ep["messages"]:
        if m["role"] != "assistant":
            continue
        c = m.get("content")
        if isinstance(c, str):
            yield c
        for t in m.get("tool_calls") or []:
            for v in ((t.get("function") or {}).get("arguments") or {}).values():
                if isinstance(v, str):
                    yield v


def main():
    fails, secret = [], cp.secrets()
    man = json.load(open(os.path.join(OUT, "MANIFEST.json"), encoding="utf-8"))
    for rel, want in man["files"].items():
        p = os.path.join(OUT, rel)
        if not os.path.exists(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != want:
            fails.append("manifest: %s changed or missing -- rebuild" % rel)
    digest = hashlib.sha256("".join("%s  %s\n" % (man["files"][k], k) for k in sorted(man["files"])).encode()).hexdigest()
    if digest != man["digest"]:
        fails.append("manifest digest does not match its file list")

    for rel in man["files"]:
        if rel.endswith((".jsonl", ".json")):
            low = open(os.path.join(OUT, rel), encoding="utf-8").read().lower()
            if any(w in low for w in secret):
                fails.append("%s: owner handle present" % rel)

    keys, counts = {}, {}
    for n, raw in enumerate(open(os.path.join(OUT, "train.jsonl"), encoding="utf-8"), 1):
        ep = json.loads(raw)
        k = ep.get("kind")
        counts[k] = counts.get(k, 0) + 1
        if k not in KINDS:
            fails.append("train %d: unknown kind %r" % (n, k)); continue
        if k in ("play", "highlight", "image"):
            fails += ["train %d (%s): %s" % (n, k, e) for e in cp.check_episode(ep, [])[:4]]
        elif k in ("voice", "chat"):
            fails += ["train %d (%s): %s :: %s" % (n, k, e, ep["messages"][-1]["content"]) for e in voice_fails(ep["messages"])]
        elif k in ("writeup", "screen"):
            a = ep["messages"][-1]["content"]
            if cp.dirty(a) or len(a.split()) > 90:
                fails.append("train %d (%s): fails the stream filter or too long: %r" % (n, k, a[:120]))
            if k == "screen" and not all(os.path.exists(os.path.join(OUT, i)) for i in ep.get("images", [])):
                fails.append("train %d: screenshot file missing" % n)
        if k != "knowledge":
            for t in her_text(ep):
                if STALE.search(t):
                    fails.append("train %d (%s): stale habit line: %r" % (n, k, t[:80]))
        m = ep["messages"]
        keys[json.dumps(m[1:3], sort_keys=True)] = n
        if k in ("voice", "chat"):
            keys["line:" + m[-1]["content"]] = n

    for name, kind in (("eval_voice.jsonl", "voice"), ("eval_tools.jsonl", "play")):
        for n, raw in enumerate(open(os.path.join(OUT, name), encoding="utf-8"), 1):
            ep = json.loads(raw)
            m = ep["messages"]
            if json.dumps(m[1:3], sort_keys=True) in keys or ("line:" + m[-1]["content"]) in keys:
                fails.append("%s %d: also in train.jsonl (eval leak)" % (name, n))
            if kind == "voice":
                fails += ["%s %d: %s" % (name, n, e) for e in voice_fails(m)]
            else:
                fails += ["%s %d: %s" % (name, n, e) for e in cp.check_episode(ep, [])[:4]]

    for f in fails:
        print(f)
    print("train:", counts, "| eval_voice:", man["eval_voice"], "| eval_tools:", man["eval_tools"],
          "| secret words checked:", len(secret), "| failures:", len(fails))
    print("PASS" if not fails else "FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
