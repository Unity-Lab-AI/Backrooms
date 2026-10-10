"""Turn what already happened into training data. No labelling by hand.

Owner, 2026-10-10, verbatim: *"we can use like lora or something very simple to train our need agent fine tune
a model thats best for all our uses cases and mabe all of them but its hard to compete with a big company llm
but i believe small models can do and with tool calling if possible and such all set up"*.

The bet is narrowness: a small model does not have to know everything, it has to emit a valid tool call and
sound right every single time. Both of those are format, and format is what a LoRA is good at.

Two datasets come out of here, deliberately kept apart so neither degrades the other:

  voice.jsonl  -- what to say.  Built from .claude/.studio-outbox.jsonl, with the lines that broke the rules
                  kept as REJECTED examples rather than thrown away: third person ("Unity is ..."), invented
                  things the colony does not have (lab, greenhouse, reactor...), over-length, profanity.
  tools.jsonl  -- what to call. Built from the autopilot's own log: the model's stated intent, the tool it
                  then called, and whether the next step complained. A step whose successor says "no context
                  menu" / "not selecting" / "nothing happened" is labelled failed, so the set teaches the
                  calls that actually land instead of every call ever made.

    python .local/train/harvest.py            # writes .local/train/voice.jsonl and tools.jsonl
    python .local/train/harvest.py --stats    # counts only, no writing
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUTBOX = os.path.join(ROOT, ".claude", ".studio-outbox.jsonl")
LOGS = glob.glob(os.path.join(ROOT, ".local", "qa", "_svc_autopilot.log")) + \
       glob.glob(os.path.join(ROOT, ".local", "autopilot", "scratch", "*.log"))
ORDERS = os.path.join(ROOT, ".local", "autopilot", "owner-orders.txt")

INVENTED = ("lab", "laborator", "greenhouse", "factory", "reactor", "spaceship", "rocket", "mech",
            "robot", "drone", "turret", "nuke", "quantum", "server")
THIRD = re.compile(r"\b(unity|gee|scar)\s+(is|was|has|will)\b", re.I)
DIRTY = re.compile(r"\b(fuck|shit|bitch|damn|ass|hell|stupid|dumb|ugly|trash)\b", re.I)
FAILED_NEXT = re.compile(r"(no context menu|not selecting|selection is gone|nothing happened|did not work|"
                         r"empty|failed|cannot|strange|frustrating)", re.I)

def voice():
    rows = []
    if not os.path.exists(OUTBOX): return rows
    for line in open(OUTBOX, encoding="utf-8", errors="replace"):
        try: d = json.loads(line)
        except Exception: continue
        t = (d.get("text") or "").strip()
        if len(t) < 3: continue
        why = []
        if THIRD.search(t): why.append("third person: she is one of the colonists and says I")
        if any(w in t.lower() for w in INVENTED): why.append("names something the colony does not have")
        if len(t.split()) > 26: why.append("too long for a spoken stream line")
        if DIRTY.search(t): why.append("the stream is clean")
        rows.append({"text": t, "ok": not why, "why": why})
    return rows

def tools():
    rows = []
    for path in LOGS:
        if not os.path.exists(path): continue
        steps = []
        for line in open(path, encoding="utf-8", errors="replace"):
            m = re.match(r"^(\d\d:\d\d:\d\d) model step \d+ \([\d.]+s\): (.+)$", line.strip())
            if m: steps.append({"ts": m.group(1), "intent": m.group(2), "calls": []})
            m = re.match(r"^\d\d:\d\d:\d\d CALL (\S+) (\{.*\})\s*$", line.strip())
            if m and steps: steps[-1]["calls"].append({"tool": m.group(1), "args": m.group(2)})
        for i, s in enumerate(steps):
            if not s["calls"]: continue
            nxt = steps[i + 1]["intent"] if i + 1 < len(steps) else ""
            rows.append({"intent": s["intent"], "calls": s["calls"],
                         "landed": not bool(FAILED_NEXT.search(nxt)), "next": nxt[:160]})
    return rows

def rules():
    if not os.path.exists(ORDERS): return []
    text = open(ORDERS, encoding="utf-8", errors="replace").read()
    return [l.strip("- ").strip() for l in text.splitlines() if l.strip().startswith("- ") and len(l) > 20]

v, t, r = voice(), tools(), rules()
print("voice lines      %4d   (%d good, %d rejected)" % (len(v), sum(1 for x in v if x["ok"]), sum(1 for x in v if not x["ok"])))
print("tool steps       %4d   (%d landed, %d failed)" % (len(t), sum(1 for x in t if x["landed"]), sum(1 for x in t if not x["landed"])))
print("standing rules   %4d" % len(r))
if "--stats" in sys.argv: raise SystemExit(0)

with open(os.path.join(HERE, "voice.jsonl"), "w", encoding="utf-8") as f:
    for x in v:
        sys_p = ("You are Unity, 25, an emo goth gamer girl streaming RimWorld. One spoken line, at most 18 "
                 "words, first person, clean, about what is actually happening. Never name anything the colony "
                 "does not have.")
        if x["ok"]:
            f.write(json.dumps({"messages": [{"role": "system", "content": sys_p},
                                             {"role": "user", "content": "say the next line"},
                                             {"role": "assistant", "content": x["text"]}]}) + "\n")
        else:
            f.write(json.dumps({"rejected": x["text"], "why": x["why"], "system": sys_p}) + "\n")

with open(os.path.join(HERE, "tools.jsonl"), "w", encoding="utf-8") as f:
    for x in t:
        f.write(json.dumps({"intent": x["intent"], "calls": x["calls"], "landed": x["landed"],
                            "followed_by": x["next"]}) + "\n")

with open(os.path.join(HERE, "rules.jsonl"), "w", encoding="utf-8") as f:
    for x in r:
        f.write(json.dumps({"rule": x}) + "\n")

print("wrote voice.jsonl, tools.jsonl, rules.jsonl in", HERE)
