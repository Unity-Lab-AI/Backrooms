"""Check training/data/knowledge_game.jsonl: valid JSON, roles system/user/assistant, non-empty meta.source and
meta.topic, answers of 1-4 sentences, unique questions, and clean words (CLEAN_BLOCK / EXTRA_BLOCK from
.local/autopilot/guards.py).
    python training/check_knowledge.py   -> prints failures and counts, exit 1 if any failure
"""
import importlib.util, json, os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data", "knowledge_game.jsonl")

spec = importlib.util.spec_from_file_location("guards", os.path.join(ROOT, ".local", "autopilot", "guards.py"))
guards = importlib.util.module_from_spec(spec); spec.loader.exec_module(guards)
CLEAN_BLOCK, EXTRA_BLOCK = guards.CLEAN_BLOCK, guards.EXTRA_BLOCK


def sentences(text):
    # split on sentence-ending punctuation followed by space + capital/digit; decimals like 0.5 stay intact
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", text.strip()) if s]


def main():
    fails, seen, topics, n = [], {}, Counter(), 0
    with open(DATA, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                fails.append((i, "blank line")); continue
            n += 1
            try:
                row = json.loads(line)
            except Exception as e:
                fails.append((i, "bad json: %s" % e)); continue
            meta = row.get("meta") or {}
            if not str(meta.get("source", "")).strip():
                fails.append((i, "empty meta.source"))
            if not str(meta.get("topic", "")).strip():
                fails.append((i, "empty meta.topic"))
            msgs = row.get("messages")
            if not isinstance(msgs, list) or [m.get("role") for m in msgs] != ["system", "user", "assistant"]:
                fails.append((i, "roles must be system,user,assistant")); continue
            if any(not str(m.get("content", "")).strip() for m in msgs):
                fails.append((i, "empty content")); continue
            q, a = msgs[1]["content"].strip(), msgs[2]["content"].strip()
            k = q.lower()
            if k in seen:
                fails.append((i, "duplicate question (line %d): %s" % (seen[k], q)))
            seen.setdefault(k, i)
            ns = len(sentences(a))
            if not 1 <= ns <= 4:
                fails.append((i, "answer has %d sentences" % ns))
            for m in msgs:
                for rx, name in ((CLEAN_BLOCK, "CLEAN_BLOCK"), (EXTRA_BLOCK, "EXTRA_BLOCK")):
                    hit = rx.search(m["content"])
                    if hit:
                        fails.append((i, "%s word %r in %s" % (name, hit.group(0), m["role"])))
            topics[meta.get("topic", "?")] += 1
    for i, why in fails:
        print("line %d: %s" % (i, why))
    print("%d examples, %d failures" % (n, len(fails)))
    for t, c in sorted(topics.items(), key=lambda x: -x[1]):
        print("  %-18s %d" % (t, c))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
