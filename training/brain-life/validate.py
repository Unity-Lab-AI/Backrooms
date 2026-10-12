"""Check brain "life" episodes against SPEC.md.

    python training/brain-life/validate.py part-1.jsonl [more...]

Prints each problem with file:line and a summary; exit 1 if anything fails. Duplicate spoken lines are checked
across every file given.
"""
import collections, json, os, re, sys

CATS = {"pacing", "hard_moments", "advice", "stream_running", "boundaries", "qa", "setup", "banter", "reactions"}
EMOTIONS = {"neutral", "warm", "happy", "amused", "excited", "sad", "concerned", "frustrated", "surprised"}
ACTS = {"statement", "yes_no_question", "wh_question", "exclamation", "instruction", "reassurance", "aside"}
BANNED = re.compile(r"\b(damn|dammit|hell|crap|crappy|shit|fuck\w*|bitch|ass|sucks?|freaking|frickin|wtf|omfg|stupid|"
                    r"idiot|dumb|retard\w*|shut up|sexy|drunk|beer|wine|vodka|weed|stoned|forever11231|gfourteen)\b", re.I)
SPOKEN_OK = re.compile(r"^[A-Za-z0-9 ,.'?!\-\[\]]+$")


def sentences(text):
    return [s for s in re.split(r"(?<=[.?!])\s+", text.replace("[laughter]", " ").strip()) if s.strip()]


def main(paths):
    seen, bad, total = {}, 0, 0
    cats, emo, acts, turns = (collections.Counter() for _ in range(4))
    for path in paths:
        for n, line in enumerate(open(path, encoding="utf-8"), 1):
            if not line.strip():
                continue
            total += 1
            where = "%s:%d" % (os.path.basename(path), n)
            probs = []
            try:
                ep = json.loads(line)
            except ValueError:
                print(where, "not JSON"); bad += 1; continue
            if ep.get("category") not in CATS: probs.append("bad category")
            t = ep.get("turns")
            if not isinstance(t, list) or not 1 <= len(t) <= 4: probs.append("needs 1-4 turns")
            for k, turn in enumerate(t or [], 1):
                if ("chat" in turn) == ("event" in turn): probs.append("turn %d needs exactly one of chat/event" % k)
                viewers = {c.get("viewer") for c in turn.get("chat", [])}
                for c in turn.get("chat", []):
                    if not c.get("viewer") or not c.get("msg"): probs.append("turn %d chat entry needs viewer and msg" % k)
                    if "forever11231" in (c.get("viewer", "") + c.get("msg", "")).lower(): probs.append("owner handle")
                if not turn.get("think") or len(turn["think"].split()) > 25: probs.append("turn %d think missing/too long" % k)
                calls = turn.get("calls") or []
                if ep.get("category") == "pacing":
                    if len(calls) > 1: probs.append("pacing turn %d may speak at most once" % k)
                elif not 1 <= len(calls) <= 2: probs.append("turn %d needs 1-2 calls" % k)
                for c in calls:
                    a, name = c.get("args", {}), c.get("name")
                    if name not in ("say", "reply_chat"): probs.append("tool %s not allowed" % name); continue
                    if name == "reply_chat" and a.get("viewer") not in viewers: probs.append("reply_chat viewer not in this turn's chat")
                    text = a.get("text", "")
                    if a.get("emotion") not in EMOTIONS: probs.append("bad emotion")
                    if a.get("act") not in ACTS: probs.append("bad act")
                    if not SPOKEN_OK.match(text): probs.append("characters outside plain speech: " + text[:40])
                    if re.search(r"\[(?!laughter\])", text): probs.append("only [laughter] tag allowed")
                    if BANNED.search(text): probs.append("banned word: " + BANNED.search(text).group(0))
                    if "[laughter]" in text and a.get("emotion") in ("neutral", "sad", "concerned"): probs.append("laughter on a %s line" % a.get("emotion"))
                    if a.get("act") in ("yes_no_question", "wh_question") and not text.replace("[laughter]", "").strip().endswith("?"): probs.append("question act must end with ?")
                    k2 = " ".join(text.lower().split())
                    if k2 in seen: probs.append("duplicate line of " + seen[k2])
                    seen.setdefault(k2, where)
                    if len(sentences(text)) > 5: probs.append("more than five sentences")
                    emo[a.get("emotion")] += 1; acts[a.get("act")] += 1
            if probs:
                bad += 1
                print(where, "|", "; ".join(sorted(set(probs))))
            cats[ep.get("category")] += 1; turns[len(t or [])] += 1
    print("\n%d episodes, %d with problems" % (total, bad))
    print("category:", dict(cats)); print("turns:", dict(sorted(turns.items())))
    print("emotion:", dict(emo)); print("act:", dict(acts))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
