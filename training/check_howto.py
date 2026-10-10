"""Validate the how-to sets.
  voice_stream.jsonl   -- every live stream filter (check_voice.fresh_fail), exact fresh() prompt format,
                          <=20 words, viewer's name present, unique lines (no shared 6-word run), never a secret word.
  knowledge_code.jsonl -- JSON, meta.source URL + topic, system/user/assistant roles, clean words, 1-4 sentences.
    python training/check_howto.py   -> prints failures, exit 1 if any
"""
import importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
cv = load("cv", os.path.join(HERE, "check_voice.py"))
bh = load("bh", os.path.join(HERE, "build_howto.py"))
SECRET = cv.gd._secret_words() + ["forever11231"]

def check_stream(fails):
    seen = {}; texts = {}; n_ok = 0
    for n, raw in enumerate(open(os.path.join(HERE, "data", "voice_stream.jsonl"), encoding="utf-8"), 1):
        tag = "voice_stream:%d" % n
        try: m = json.loads(raw)["messages"]
        except Exception as e: fails.append((tag, "bad json %s" % e)); continue
        if [x.get("role") for x in m] != ["system", "user", "assistant"] or not all(x.get("content") for x in m):
            fails.append((tag, "roles/content")); continue
        if m[0]["content"] != bh.FRESH_SYSTEM: fails.append((tag, "system prompt differs from fresh()"))
        u, line = m[1]["content"], m[2]["content"]
        g = re.match(r'ONE spoken line, at most 20 words, about this and nothing else: "(.*)"\. Say it IN YOUR OWN WORDS', u, re.S)
        if not g or not u.endswith(". Reply with the line only."): fails.append((tag, "user prompt not fresh() format")); continue
        fact = g.group(1)
        who = re.match(r"(?:viewer )?(\w+) (?:just|said|resubscribed|gifted|cheered|is |redeemed|was made|spammed|from the raid)", fact)
        who = who.group(1) if who and who.group(1) not in ("I", "the") else None
        r = re.search(r"raiding (\w+) next", fact); who = r.group(1) if r else who
        if who and who.lower() not in line.lower(): fails.append((tag, "lacks name %s :: %s" % (who, line)))
        if len(line.split()) > 20: fails.append((tag, "over 20 words"))
        if any(s.lower() in (line + u).lower() for s in SECRET): fails.append((tag, "secret word"))
        for w in cv.fresh_fail(line, fact): fails.append((tag, "%s :: %s" % (w, line)))
        if line in texts: fails.append((tag, "duplicate of %d" % texts[line]))
        texts[line] = n
        w = re.findall(r"[a-z0-9_']+", line.lower())
        for k in range(len(w) - 5):
            gg = " ".join(w[k:k + 6])
            if gg in seen and seen[gg] != n: fails.append((tag, "shares 6 words with %d: %s" % (seen[gg], gg)))
            seen.setdefault(gg, n)
        n_ok += 1
    return n_ok

def check_code(fails):
    n_ok = 0
    for n, raw in enumerate(open(os.path.join(HERE, "data", "knowledge_code.jsonl"), encoding="utf-8"), 1):
        tag = "knowledge_code:%d" % n
        try: d = json.loads(raw); m = d["messages"]; meta = d["meta"]
        except Exception as e: fails.append((tag, "bad json %s" % e)); continue
        if not str(meta.get("source", "")).startswith("https://") or not meta.get("topic"): fails.append((tag, "meta"))
        if [x.get("role") for x in m] != ["system", "user", "assistant"] or not all(x.get("content") for x in m):
            fails.append((tag, "roles/content")); continue
        if m[0]["content"] != bh.CODE_SYSTEM: fails.append((tag, "system prompt"))
        for x in m[1:]:
            t = x["content"]
            if cv.uv.CLEAN_BLOCK.search(t) or cv.gd.EXTRA_BLOCK.search(t): fails.append((tag, "unclean: " + t))
            if any(ord(c) > 126 for c in t): fails.append((tag, "non-ascii"))
            if any(s.lower() in t.lower() for s in SECRET): fails.append((tag, "secret word"))
        s = len([p for p in re.split(r"(?<=[.!?])\s+", m[2]["content"].strip()) if p])
        if not 1 <= s <= 4: fails.append((tag, "answer has %d sentences" % s))
        n_ok += 1
    return n_ok

if __name__ == "__main__":
    fails = []; a = check_stream(fails); b = check_code(fails)
    for t, f in fails: print(t, f)
    print("voice_stream:", a, "| knowledge_code:", b, "| failures:", len(fails))
    print("PASS" if not fails else "FAIL"); sys.exit(1 if fails else 0)
