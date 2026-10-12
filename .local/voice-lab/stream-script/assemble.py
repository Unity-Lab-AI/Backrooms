"""Assemble the writers' parts into the two corpus files the renderer reads.

    python .local/voice-lab/stream-script/assemble.py <out_dir> [part files...]   (default: all part-*.jsonl here)

Writes <out_dir>/STREAM_CORPUS.jsonl (lines without laughter) and <out_dir>/STREAM_EVENT_CORPUS.jsonl (lines with
[laughter]) in the renderer's exact six-field schema:
  id         "stream_" + first 20 hex of sha1(text): stable, unique, safe
  intensity  0.0 for neutral, 0.35 for every other emotion (the recipe's two trained levels)
  pace       1.0 (the renderer refuses any other pace)
Fails on any duplicate text or id. Run validate.py first.
"""
import glob, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out = sys.argv[1]
    parts = sys.argv[2:] or sorted(glob.glob(os.path.join(HERE, "part-*.jsonl")),
                                   key=lambda p: int(os.path.basename(p)[5:-6]))
    os.makedirs(out, exist_ok=True)
    ordinary, events, seen = [], [], set()
    for path in parts:
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            text = r["text"].strip()
            key = " ".join(text.lower().split())
            if key in seen:
                raise SystemExit("duplicate text: " + text)
            seen.add(key)
            row = {"id": "stream_" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:20], "text": text,
                   "emotion": r["emotion"], "intensity": 0.0 if r["emotion"] == "neutral" else 0.35,
                   "pace": 1.0, "speech_act": r["speech_act"]}
            (events if "[laughter]" in text else ordinary).append(row)
    for name, rows in (("STREAM_CORPUS.jsonl", ordinary), ("STREAM_EVENT_CORPUS.jsonl", events)):
        with open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    print("ordinary %d, laughter %d, total %d -> %s" % (len(ordinary), len(events), len(ordinary) + len(events), out))


if __name__ == "__main__":
    main()
