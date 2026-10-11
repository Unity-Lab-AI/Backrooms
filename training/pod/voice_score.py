"""One scorer for her spoken lines, used for today's voice (training/eval_baseline.py, on the rig) and for the new
brain (pod/eval.py) -- the same rules the live stream applies, so "as good or better" means the same thing both
times.

    score(rows, lines) -> {"pass": fraction of lines the stream would speak, "distinct": fraction of lines that
                           share no 6-word run with another, "words": mean words per line, "n": count}
rows are eval_voice.jsonl rows (system, user, assistant); lines are the generated lines in the same order.
"""
import importlib.util, os, re, sys

REPO = os.environ.get("BRAIN_REPO") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _check_voice():
    p = os.path.join(REPO, "training", "check_voice.py")
    spec = importlib.util.spec_from_file_location("check_voice", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CV = _check_voice()


def fails(row, line):
    u = row["messages"][1]["content"]
    if u.startswith("ONE spoken line"):
        g = re.search(r'about this and nothing else: "(.*)"\. Say it IN YOUR OWN WORDS', u, re.S)
        fact = g.group(1) if g else u
        who = re.match(r"(\w+) just joined the stream; greet", fact) or re.match(r"viewer (\w+) said in chat", fact)
        extra = ["lacks name"] if who and who.group(1).lower() not in line.lower() else []
    else:
        fact = re.sub(r"^This is what is happening right now: |\. Talk to your chat about it.*$|^Say exactly this.*?keep every name, number and plan in it: ", "", u, flags=re.S)
        extra = [] if CV.uv.keeps_facts(fact, line) else ["drops facts"]
    return extra + CV.fresh_fail(line, fact)


def first_line(text):
    return (text or "").strip().strip('"').split("\n")[0].strip()


def score(rows, lines):
    lines = [first_line(l) for l in lines]
    ok = [not fails(r, l) for r, l in zip(rows, lines)]
    grams, dup = {}, set()
    for i, l in enumerate(lines):
        w = re.findall(r"[a-z0-9_']+", l.lower())
        for k in range(len(w) - 5):
            g = " ".join(w[k:k + 6])
            if g in grams and grams[g] != i:
                dup.update((i, grams[g]))
            grams.setdefault(g, i)
    n = max(1, len(lines))
    return {"pass": sum(ok) / n, "distinct": 1 - len(dup) / n,
            "words": sum(len(l.split()) for l in lines) / n, "n": len(lines)}


if __name__ == "__main__":
    sys.exit("import this module")
