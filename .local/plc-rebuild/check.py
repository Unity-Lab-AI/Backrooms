"""Merge-round checker for playbook.candidate.json + prompts.candidate.json. Prints one section per check."""
import collections, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
doc = json.load(open(os.path.join(HERE, "playbook.candidate.json"), encoding="utf-8"))
prompts = json.load(open(os.path.join(HERE, "prompts.candidate.json"), encoding="utf-8"))
gates = doc["gates"]
GENERIC = ("count_", "alert_", "research_", "condition_")
NESTED = ("any", "not", "ton", "tof", "ctu", "ons")

def latch_name(rid):
    return re.sub(r"[^a-z0-9]+", "_", str(rid).lower()).strip("_")[:35] + "_done"

def leaves(w):
    for k, v in (w or {}).items():
        if isinstance(v, dict):
            op = [o for o in NESTED if o in v]
            if len(op) != 1: continue
            op = op[0]; subs = v[op] if op == "any" else [v[op]]
            if op == "ctu" and isinstance(v.get("reset"), dict): subs = list(subs) + [v["reset"]]
            for s in subs:
                if isinstance(s, dict): yield from leaves(s)
        else:
            yield k, v

results = collections.OrderedDict()
r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "rimplc-check.py"), os.path.join(HERE, "playbook.candidate.json")],
                   capture_output=True, text=True, cwd=ROOT)
out = (r.stdout + r.stderr).strip().splitlines()
results["1 rimplc-check"] = [] if out and out[-1].strip() == "-> valid" else out

ids = collections.Counter(g["id"] for g in gates)
results["2 duplicate ids"] = ["%s x%d" % (k, n) for k, n in ids.items() if n > 1]

pr = collections.defaultdict(list)
for g in gates: pr[g["priority"]].append(g["id"])
results["3 priority ties"] = ["%s: %s" % (p, ", ".join(v)) for p, v in sorted(pr.items()) if len(v) > 1]

setters = set()
for g in gates:
    if g.get("latch"): setters.add(latch_name(g["id"]))
    for s in (g.get("then") or []):
        for m in re.finditer(r"ladder_set mark ([a-z0-9_]+)", str(s)): setters.add(m.group(1))
reads = collections.defaultdict(set)
for g in gates:
    for k, _ in leaves(g.get("when")):
        if k.startswith("mark_"): reads[k[5:]].add(g["id"])
results["4 marks read, never set"] = ["mark_%s (read by %s)" % (m, ", ".join(sorted(v))) for m, v in sorted(reads.items()) if m not in setters]

sensors = set(doc["sensors"]); tg = doc["tags"]; tags = set(tg["constants"]) | set(tg["variables"])
bad, mixed = [], []
for g in gates:
    for k, _ in leaves(g.get("when")):
        if k.startswith(GENERIC) and k != k.lower(): mixed.append("%s: %s" % (g["id"], k))
        if k in sensors or k in tags or k == "letter_matches" or k.startswith("mark_") or k.startswith(GENERIC): continue
        bad.append("%s: %s" % (g["id"], k))
results["5 unknown when keys"] = bad
results["6 mixed-case generic keys"] = mixed
results["7 rungs without a prompt"] = [g["id"] for g in gates if not str(prompts.get(g["id"], "")).strip()]

fails = 0
for name, items in results.items():
    print("== %s: %d" % (name, len(items)))
    for i in items: print("   " + i)
    fails += len(items)
print("rungs %d, prompts %d, sensors %d, tags %d" % (len(gates), len(prompts), len(sensors), len(tags)))
print("CLEAN" if fails == 0 else "REMAINING %d" % fails)
