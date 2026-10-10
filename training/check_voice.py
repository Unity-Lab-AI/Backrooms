"""Check training/data/voice.jsonl against the live stream filters (stream-host fresh(), unity-voice tidy()/
keeps_facts()/CLEAN_BLOCK, autopilot guards clean_for_stream/EXTRA_BLOCK/TECH_BLOCK).
    python training/check_voice.py        -> prints every failure, exit 1 if any
"""
import difflib, importlib.util, json, os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
uv = load("uv", os.path.join(ROOT, ".claude", "tools", "unity-voice.py"))
gd = load("gd", os.path.join(ROOT, ".local", "autopilot", "guards.py"))

BANNED = ("fuck", "shit", "bitch", "damn", "hell", "ass", "cunt", "dick")   # stream-beat.BANNED
INVENTED = ("lab", "laborator", "greenhouse", "factory", "reactor", "spaceship", "ship", "rocket",
            "mech", "robot", "drone", "turret", "nuke", "portal", "quantum", "server",
            "fire", "burn", "flame", "dead", "died", "dying", "killed", "raid", "injur", "bleed",
            "down a ", "lost a", "missing", "slime", "explod",
            "smolder", "ruin", "smok", "goat", "kitchen", "lights", "alien",
            "crafted", "mods", "spider", "hive", "infest", "insect", "sounds", "noise", "monster", "creature")
OPENER = re.compile(r"^\W*(?:(?:hey|hi|yo|ok(?:ay)?|alright|so|oh|well)\W+)*(?:(?:guys|everyone|everybody|chat|"
                    r"y'all|folks|listen up|team|crew)\W*)+", re.I)
NUMWORDS = {"two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8",
            "nine": "9", "ten": "10", "eleven": "11", "twelve": "12", "twenty": "20", "hundred": "100"}

def fresh_fail(line, fact):
    """Every reason fresh() (plus the guards) would refuse this line; empty list = it would be spoken."""
    why = []; low = line.lower()
    if OPENER.sub("", line).strip() != line.strip(): why.append("announcer opener")
    if re.match(r"(?i)^\W*(hey|hi guys|alright|okay|ok|so|well|listen)\b", line): why.append("opener word")
    if re.search(r"(\d+|two|three|four|five|six) (more|others|other colonists|new)", line, re.I): why.append("crew count")
    if re.search(r"\bUnity\b", line): why.append("own name")
    if difflib.SequenceMatcher(None, low, fact.lower()).ratio() > 0.75: why.append("echo of fact")
    fw = re.findall(r"[a-z']+", fact.lower()); lw = " " + " ".join(re.findall(r"[a-z']+", low)) + " "
    if any(" " + " ".join(fw[k:k + 5]) + " " in lw for k in range(max(0, len(fw) - 4))): why.append("parrots 5 words")
    if not line or len(line.split()) > 30: why.append("too long")
    if any(re.search(r"\b%s" % w, low) for w in BANNED): why.append("banned word")
    if any(w in low for w in ("behold", "cosmos", " lo,", "witness", "indeed", "truly", "fellow")): why.append("narrator word")
    if low.startswith(("now:", "what i am doing", "what i'm doing")) or "right now in the game:" in low: why.append("label echo")
    if re.search(r"\b(connect\w*|server\w*|bridge|retry\w*|loading the mod|crash\w*|bugs?|errors?|offline|back online|scripts?|model|api|tools?)\b", low): why.append("tech")
    if any(n not in fact for n in re.findall(r"\d+", line)): why.append("number not in fact")
    for w, d in NUMWORDS.items():
        if re.search(r"\b%s\b" % w, low) and not re.search(r"\b(%s|%s)\b" % (w, d), fact.lower()): why.append("number word " + w)
    if any(w in low for w in INVENTED) and not any(w in fact.lower() for w in INVENTED):
        why.append("invented: " + ",".join(w for w in INVENTED if w in low))
    if re.search(r"\b(unity|gee|scar)\s+(is|was|has|will)\b", low): why.append("third person")
    if re.search(r"\b(coffee|caffein\w*|cold|freez\w*|frozen|hands?|fingers?|sleep\w*|asleep|awake|yawn\w*|nodding off|tired|exhaust\w*|naps?)\b", low): why.append("banned theme")
    if uv.CLEAN_BLOCK.search(line) or gd.EXTRA_BLOCK.search(line) or gd.TECH_BLOCK.search(line): why.append("guards block")
    if gd.clean_for_stream(line) != line.replace("_", " ").strip(" -,"): why.append("clean_for_stream changes it")   # it speaks _ as a space
    if uv.tidy(line) != line: why.append("tidy changes it")
    if any(ord(c) > 126 for c in line) or "*" in line: why.append("non-ascii / stage direction")
    return why

def main():
    path = os.path.join(HERE, "data", "voice.jsonl"); fails = []; lines = []; cats = Counter(); long20 = 0
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        try: m = json.loads(raw)["messages"]
        except Exception as e: fails.append((n, "bad json: %s" % e)); continue
        if [x.get("role") for x in m] != ["system", "user", "assistant"] or not all(x.get("content") for x in m):
            fails.append((n, "roles/content")); continue
        u, line = m[1]["content"], m[2]["content"]
        if u.startswith("ONE spoken line"):
            fact = re.search(r'about this and nothing else: "(.*)"\. Say it IN YOUR OWN WORDS', u, re.S).group(1)
            g = re.match(r"(\w+) just joined the stream; greet", fact)
            v = re.match(r'viewer (\w+) said in chat', fact)
            cat = "greet" if g else "reply" if v else "game/thin"
            if g and g.group(1).lower() not in line.lower(): fails.append((n, "greeting lacks name"))
            if v and v.group(1).lower() not in line.lower(): fails.append((n, "reply lacks name"))
        else:
            cat = "announce"
            fact = re.sub(r"^This is what is happening right now: |\. Talk to your chat about it.*$|^Say exactly this.*?keep every name, number and plan in it: ", "", u, flags=re.S)
            if not uv.keeps_facts(fact, line): fails.append((n, "announce drops the facts"))
        cats[cat] += 1
        if len(line.split()) > 20: long20 += 1
        for w in fresh_fail(line, fact): fails.append((n, "%s :: %s" % (w, line)))
        lines.append((n, line))
    # unique: no two lines share 6+ words in a row
    seen = {}
    for n, line in lines:
        w = re.findall(r"[a-z0-9_']+", line.lower())
        for k in range(len(w) - 5):
            g = " ".join(w[k:k + 6])
            if g in seen and seen[g] != n: fails.append((n, "shares 6 words with line %d: %s" % (seen[g], g)))
            seen.setdefault(g, n)
    for n, f in fails: print("line %d: %s" % (n, f))
    print("examples:", sum(cats.values()), dict(cats), "| over 20 words:", long20, "| failures:", len(fails))
    print("PASS" if not fails else "FAIL"); sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
