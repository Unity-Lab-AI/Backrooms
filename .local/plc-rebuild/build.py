"""Merge round 1: families-fixed/*.json + live ladder -> playbook.candidate.json + prompts.candidate.json."""
import glob, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
live = json.load(open(os.path.join(ROOT, "docs", "playbook.gates.json"), encoding="utf-8"))
dec = json.load(open(os.path.join(HERE, "decisions.json"), encoding="utf-8"))

rungs, prompts, seen = [], {}, set()
for p in sorted(glob.glob(os.path.join(HERE, "families-fixed", "*.json"))):
    fam = json.load(open(p, encoding="utf-8"))
    for r in fam["rungs"]:
        rungs.append(r); seen.add(r["id"])
    for k, v in (fam.get("prompts") or {}).items():
        prompts[k] = v
# a live id a family names in its notes / pointers was deleted into a survivor (decisions.json pointer_rung)
notes_txt = ""
for p in sorted(glob.glob(os.path.join(HERE, "families-fixed", "*.json"))):
    fam = json.load(open(p, encoding="utf-8"))
    notes_txt += json.dumps([fam.get("notes"), fam.get("pointers")])
import re
pointed = [g["id"] for g in live["gates"] if g["id"] not in seen and re.search(r"(?<![a-z0-9-])%s(?![a-z0-9-])" % re.escape(g["id"]), notes_txt)]
kept = [g for g in live["gates"] if g["id"] not in seen and g["id"] not in pointed]
print("live rungs dropped by family pointers: %s" % ", ".join(pointed))
for g in kept:
    rungs.append(g)
    if g["id"] not in prompts:   # live rung kept as is: its prompt is its own text, why quoted verbatim
        lines = []
        if g.get("disabled"): lines.append("DISABLED: " + str(g["disabled"]))
        lines.append("LOOK FIRST: " + json.dumps(g.get("when"), ensure_ascii=False))
        lines += ["DO: " + t for t in g.get("then") or []]
        lines += ["NEVER: " + t for t in g.get("never") or []]
        if g.get("why"): lines.append("WHY: " + g["why"])
        prompts[g["id"]] = chr(10).join(lines)

TYPES = {"power_margin_pct": "float", "monolith": "int", "owner_input_active": "bool", "owner_unread": "int",
         "chat_unanswered": "int", "chat_asks_mod": "bool", "new_joiners": "int", "seconds_since_spoken": "float",
         "voice_playing": "bool", "seconds_since_webcam": "float", "seconds_since_tool": "float",
         "prompt_version_changed": "bool"}
sensors = dict(live["sensors"])
added = []
for name, v in dec["sensors"]["keys"].items():
    if not v["status"].startswith("TO_BUILD"):
        continue
    key = v["canonical"]
    if key in sensors:
        continue
    cs = v.get("csharp", "")
    t = TYPES.get(key) or ("int" if "(double)" in cs else "bool")
    e = {"source": ("RimPLC: " + v.get("where", "")) if v["status"] == "TO_BUILD" else ("gates.py: " + v.get("how", "")),
         "type": t, "status": "not-measured"}
    if v.get("note"): e["note"] = v["note"]
    sensors[key] = e; added.append(key)

# keys Sensors.cs already writes that the live catalogue does not list
CS = {"able_shooters_armed": ("int", "colonists able to shoot who carry a ranged weapon"),
      "needs_tend_count": ("int", "colonists needing tending"),
      "hostile_threat": ("bool", "GenHostility.AnyHostileActiveThreatToPlayer(home)"),
      "outdoor_temp": ("float", "home.mapTemperature.OutdoorTemp"),
      "lowest_mood": ("float", "lowest colonist mood 0-1"),
      "title_seniority": ("int", "highest Empire title seniority (Royalty)")}
for k, (t, src) in CS.items():
    if k not in sensors:
        sensors[k] = {"source": "RimPLC Sensors.cs: " + src, "type": t, "status": "verified"}; added.append(k)
if "monolith_level" not in sensors:
    sensors["monolith_level"] = {"source": "RimPLC: Find.Anomaly.Level (decisions.json monolith entry)", "type": "int", "status": "not-measured", "requires": ["Anomaly"]}; added.append("monolith_level")
def leaves(w):
    for k, v in (w or {}).items():
        if isinstance(v, dict):
            for op in ("any", "not", "ton", "tof", "ctu", "ons"):
                if op in v:
                    subs = v[op] if op == "any" else [v[op]]
                    if op == "ctu" and isinstance(v.get("reset"), dict): subs = list(subs) + [v["reset"]]
                    for x in subs: yield from leaves(x)
        else:
            yield k
for g in rungs:
    for k in leaves(g.get("when")):
        if k.startswith("condition_") and k not in sensors:
            sensors[k] = {"source": "RimPLC Sensors.cs: condition_<defname lower>, true while the GameCondition is active", "type": "bool", "status": "verified"}; added.append(k)

# tags: variables the families need that the live table lacks (numeric only)
tags = json.loads(json.dumps(live["tags"])); tadded = []
have = set(tags["constants"]) | set(tags["variables"])
for p in sorted(glob.glob(os.path.join(HERE, "families-fixed", "*.json"))):
    for v in json.load(open(p, encoding="utf-8")).get("variables_needed") or []:
        n, val = v.get("name", ""), v.get("value")
        if isinstance(val, str):   # "<k> * TAG" against a tag that already has a value: keep the formula in the rule
            import re
            m = re.fullmatch(r"\s*([0-9.]+)\s*\*\s*([A-Z0-9_]+)\s*", val)
            base = (tags["variables"].get(m.group(2)) or {}).get("value") if m else None
            if isinstance(base, (int, float)):
                v = dict(v, rule=(v.get("rule", "") + " (value = %s)" % val).strip()); val = float(m.group(1)) * base
        if n in have or not n.isupper() or isinstance(val, bool) or not isinstance(val, (int, float)): continue
        e = {"value": val}
        if v.get("rule"): e["rule"] = v["rule"]
        tags["variables"][n] = e; have.add(n); tadded.append(n)

# rung fields outside the frozen rung schema go to a sidecar, untouched (owner quotes stay verbatim there)
ALLOWED = set(json.load(open(os.path.join(ROOT, "docs", "rimplc", "schema", "rung.schema.json"), encoding="utf-8"))["properties"])
extras, clean = {}, []
for g in rungs:
    x = {k: v for k, v in g.items() if k not in ALLOWED}
    if x: extras[g["id"]] = x
    clean.append({k: v for k, v in g.items() if k in ALLOWED})
rungs = clean
json.dump(extras, open(os.path.join(HERE, "rung-extras.candidate.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("tags added %d: %s; rungs with sidecar fields %d" % (len(tadded), ", ".join(tadded), len(extras)))
out = dict(live); out["gates"] = rungs; out["sensors"] = sensors; out["tags"] = tags
json.dump(out, open(os.path.join(HERE, "playbook.candidate.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(prompts, open(os.path.join(HERE, "prompts.candidate.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("rungs %d (family %d, live kept %d), prompts %d, sensors added %d: %s" % (len(rungs), len(rungs) - len(kept), len(kept), len(prompts), len(added), ", ".join(added)))
