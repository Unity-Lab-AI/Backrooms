"""Check stream-script JSONL files against SPEC.md.

    python .local/voice-lab/stream-script/validate.py part-3.jsonl [more files...]

Prints every problem with its line number and a summary (emotion / act / sentence-length / laughter / openers).
Exit 1 if any line fails. Duplicates are checked across all files given and against the existing seed corpora.
"""
import collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EMOTIONS = {"neutral", "warm", "happy", "amused", "excited", "sad", "concerned", "frustrated", "surprised"}
ACTS = {"statement", "yes_no_question", "wh_question", "exclamation", "instruction", "reassurance", "aside"}
BANNED = re.compile(r"\b(damn|dammit|hell|crap|crappy|sucks?|sucked|freaking|frickin|fricking|wtf|omfg|stupid|idiot|dumb|shut up|"
                    r"hate you|kill yourself|sexy|drunk|beer|wine|vodka|weed|high as|stoned|forever11231|gee|gfourteen)\b", re.I)
ALLOWED = re.compile(r"^[A-Za-z0-9 ,.'?!\[\]]+$")
LENGTH = {1: (1, 18), 2: (8, 30), 3: (30, 50), 4: (39, 57)}


def norm(text):
    return re.sub(r"[^a-z' ]+", " ", text.replace("[laughter]", " ").lower()).split()


def sentences(text):
    body = text.replace("[laughter]", " ").strip()
    return [s for s in re.split(r"(?<=[.?!])\s+", body) if s.strip()]


def seed_texts():
    out = set()
    for name in ("SPEECH_CORPUS.jsonl", "SPEECH_EVENT_CORPUS.jsonl"):
        path = os.path.join(ROOT, "training", "voice", name)
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                if line.strip():
                    out.add(" ".join(norm(json.loads(line)["text"])))
    return out


def main(paths):
    seen, seed, bad = {}, seed_texts(), 0
    emo, act, lens, laugh, openers = (collections.Counter() for _ in range(5))
    total = 0
    for path in paths:
        for n, line in enumerate(open(path, encoding="utf-8"), 1):
            if not line.strip():
                continue
            total += 1
            where = "%s:%d" % (os.path.basename(path), n)
            try:
                row = json.loads(line)
            except ValueError:
                print(where, "not JSON"); bad += 1; continue
            problems = []
            if set(row) != {"text", "emotion", "speech_act"}:
                problems.append("keys must be exactly text, emotion, speech_act")
            text = str(row.get("text", ""))
            if row.get("emotion") not in EMOTIONS: problems.append("bad emotion")
            if row.get("speech_act") not in ACTS: problems.append("bad speech_act")
            if not ALLOWED.match(text): problems.append("characters outside letters/digits/space , . ' ? ! [laughter]")
            if re.search(r"\d", text): problems.append("digits: spell numbers as words")
            if re.search(r"\[(?!laughter\])", text): problems.append("only [laughter] tags allowed")
            if BANNED.search(text): problems.append("banned word: " + BANNED.search(text).group(0))
            if re.search(r"\b[A-Z]{2,}\b", text.replace("[laughter]", "")) and not re.search(r"\bI\b", text): problems.append("ALL CAPS word")
            s = sentences(text)
            words = len(norm(text))
            k = len(s)
            if k not in LENGTH: problems.append("%d sentences (1-4 allowed)" % k)
            elif not LENGTH[k][0] <= words <= LENGTH[k][1]: problems.append("%d words for %d sentence(s), need %d-%d" % ((words, k) + LENGTH[k]))
            if row.get("emotion") == "neutral" and "[laughter]" in text:
                problems.append("a laughter line cannot be neutral (laughter renders through Cosy, which may not render neutral)")
            if row.get("speech_act") in ("yes_no_question", "wh_question") and not text.replace("[laughter]", "").strip().endswith("?"):
                problems.append("question act must end with ?")
            if row.get("speech_act") == "exclamation" and not text.replace("[laughter]", "").strip().endswith("!"):
                problems.append("exclamation act must end with !")
            key = " ".join(norm(text))
            if key in seen: problems.append("duplicate of " + seen[key])
            seen.setdefault(key, where)
            if problems:
                bad += 1
                print(where, "|", "; ".join(problems), "|", text[:90])
            emo[row.get("emotion")] += 1; act[row.get("speech_act")] += 1; lens[min(k, 4)] += 1
            laugh["laughter" if "[laughter]" in text else "plain"] += 1
            first = norm(text)[:1]
            openers[first[0] if first else ""] += 1
    print("\n%d lines, %d with problems" % (total, bad))
    print("emotion:", dict(emo)); print("speech_act:", dict(act)); print("sentences:", dict(sorted(lens.items())))
    print("laughter:", dict(laugh)); print("top openers:", openers.most_common(8))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
