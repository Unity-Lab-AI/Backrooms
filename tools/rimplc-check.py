"""RimPLC P0: validate a ladder against the frozen schemas and the import rules, and write the book preset.

    python tools/rimplc-check.py                      # validate docs/playbook.gates.json
    python tools/rimplc-check.py --emit               # also write RimPLC/Presets/LadderV2.json (the book preset)
    python tools/rimplc-check.py path/to/ladder.json  # validate any ladder / preset / export

Schemas: docs/rimplc/schema/*.json (ladder, rung, sensor, tag, mark; tools.schema.json holds the API shapes).
Import rules (docs/RIMPLC_DESIGN.md section 7): unique ids, numeric priority, every `when` key is a sensor, a tag,
mark_*, alert_*, count_*, research_* or letter_matches (rungs that are `disabled` may name unmeasured keys), every
{TAG} bound names a tag, a nested instruction is exactly one of any / not / ton / tof / ctu / ons with its own fields
(checked inside too), non-book rungs carry at most 8 `then` lines of at most 300 characters, and a unity rung's notice
passes the stream's clean-word filter. RimPLC's Validate.cs applies the same rules in game (editor, import, API).

The emitted preset is the playbook plus `preset`, and per rung `source: book`, `mode: advise` (when absent) and
`requires` for DLC / mod families. Conditions on marks that RimPLC now measures are rewritten to the sensor
(MEASURED below), and the sensor's catalogue entry names the old mark as its `fallback`, so .local/autopilot/gates.py
(which cannot measure them) still reads the mark and gives the same answer.
"""
import importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(ROOT, "docs", "rimplc", "schema")
PLAYBOOK = os.path.join(ROOT, "docs", "playbook.gates.json")
PRESET = os.path.join(ROOT, "RimPLC", "Presets", "LadderV2.json")

# family / id -> requires. Only the rungs that cannot apply without the content are gated.
REQUIRES_BY_ID = {
    "anomaly-entity": ["Anomaly"], "anomaly-monolith": ["Anomaly"],
    "genes": ["Biotech"], "mechanitor": ["Biotech"],
    "ideo-ritual": ["Ideology"], "ideo-roles": ["Ideology"],
    "grav-build": ["Odyssey"], "grav-core": ["Odyssey"], "grav-ready": ["Odyssey"], "megaship-drop": ["Odyssey"],
}
REQUIRES_BY_FAMILY = {"royalty": ["Royalty"], "backrooms": ["mod:Rimrooms.AsyncIndustries"]}

# old mark condition -> the sensor RimPLC measures instead (RimPLC/Source/RimPLC/Sensors.cs). research_<def> is
# ResearchProjectDef.IsFinished under the def name in lower case; a def that is not loaded leaves the key unmeasured,
# and then the fallback mark is read, exactly as before.
MEASURED = {
    "mark_research_microelectronics": ("research_microelectronicsbasics", {
        "source": "RimPLC: ResearchProjectDef MicroelectronicsBasics .IsFinished", "type": "bool", "cadence": "slow",
        "api": "ResearchProjectDef.IsFinished", "status": "verified",
        "note": "defName verified (decomp, ResearchProjectDefOf.MicroelectronicsBasics)"}),
    "mark_research_transport_pod": ("research_transportpod", {
        "source": "RimPLC: ResearchProjectDef TransportPod .IsFinished", "type": "bool", "cadence": "slow",
        "api": "ResearchProjectDef.IsFinished", "status": "UNVERIFIED",
        "note": "defName TransportPod UNVERIFIED (no ResearchProjectDefOf entry); if it is wrong the key stays unmeasured and the fallback mark is read"}),
    "mark_research_xenogenetics": ("research_xenogenetics", {
        "source": "RimPLC: ResearchProjectDef Xenogenetics .IsFinished", "type": "bool", "cadence": "slow",
        "api": "ResearchProjectDef.IsFinished", "status": "UNVERIFIED", "requires": ["Biotech"],
        "note": "defName Xenogenetics UNVERIFIED (Biotech); if it is wrong the key stays unmeasured and the fallback mark is read"}),
    "mark_caravan_out": ("caravan_out", {
        "source": "RimPLC: Find.WorldObjects.Caravans, any IsPlayerControlled", "type": "bool", "cadence": "slow",
        "api": "WorldObjectsHolder.Caravans", "status": "verified"}),
}
KNOWN_PREFIXES = ("mark_", "alert_", "count_", "research_")
NESTED = ("any", "not", "ton", "tof", "ctu", "ons")


def _clean():
    """The stream's clean-word check (guards.clean_for_stream), or None when guards cannot be loaded."""
    try:
        here = os.path.join(ROOT, ".local", "autopilot")
        sys.path.insert(0, here)
        spec = importlib.util.spec_from_file_location("guards_check", os.path.join(here, "guards.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m.clean_for_stream
    except Exception:
        return None


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def schema_errors(doc):
    try:
        import jsonschema
        from referencing import Registry, Resource
    except ImportError:
        return ["jsonschema / referencing not installed: schema pass skipped (pip install jsonschema)"]
    res = []
    for n in os.listdir(SCHEMA_DIR):
        if n.endswith(".schema.json"):
            s = load(os.path.join(SCHEMA_DIR, n))
            res.append((s["$id"], Resource.from_contents(s)))
    reg = Registry().with_resources(res)
    top = load(os.path.join(SCHEMA_DIR, "ladder.schema.json"))
    v = jsonschema.Draft202012Validator(top, registry=reg)
    return ["%s: %s" % ("/".join(str(x) for x in e.absolute_path), e.message) for e in v.iter_errors(doc)]


def rule_errors(doc):
    errs, warns = [], []
    sensors = set((doc.get("sensors") or {}).keys())
    tg = doc.get("tags") or {}
    tagnames = set((tg.get("constants") or {}).keys()) | set((tg.get("variables") or {}).keys())
    seen = set()
    for g in doc.get("gates", []):
        rid = g.get("id")
        if rid in seen:
            errs.append("duplicate id %s" % rid)
        seen.add(rid)
        if not isinstance(g.get("priority"), (int, float)) or isinstance(g.get("priority"), bool):
            errs.append("%s: priority is not a number" % rid)
        src = g.get("source", "book")
        if src != "book":
            then = g.get("then") or []
            if len(then) > 8 or any(len(s) > 300 for s in then):
                errs.append("%s: then over 8 lines / 300 characters" % rid)
            if not str(rid).startswith(src + "-"):
                errs.append("%s: a %s rung id starts with %s-" % (rid, src, src))
        if src == "unity" and g.get("notice") is not None:
            clean = _clean()
            if clean is not None and clean(str(g["notice"])) is None:
                errs.append("%s: notice is not clean for the stream: reword it" % rid)
        _when(rid, g.get("when") or {}, sensors, tagnames, bool(g.get("disabled")), errs, warns, 0)
    return errs, warns


def _when(rid, when, sensors, tagnames, disabled, errs, warns, depth):
    if depth > 8:
        errs.append("%s: instructions nested too deep" % rid); return
    for k, w in when.items():
        if isinstance(w, dict):
            _instruction(rid, k, w, sensors, tagnames, disabled, errs, warns, depth); continue
        known = (k == "letter_matches" or k.startswith(KNOWN_PREFIXES) or k in sensors or k in tagnames)
        if not known:
            (warns if disabled else errs).append("%s: when key %s has no sensor, tag or mark" % (rid, k))
        if isinstance(w, str):
            for t in re.findall(r"\{([^}]*)\}", w):
                if t.strip() not in tagnames:
                    errs.append("%s: %s names unknown tag {%s}" % (rid, k, t))
            if w[:1] in "<>!" and not any(w.startswith(o) for o in (">=", "<=", "!=", ">", "<")):
                errs.append("%s: %s has no operator in %r" % (rid, k, w))


def _whole(v, lo=1):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v >= lo and float(v).is_integer()


def _instruction(rid, k, e, sensors, tagnames, disabled, errs, warns, depth):
    ops = [o for o in NESTED if o in e]
    if len(ops) != 1:
        errs.append("%s: %s is not exactly one of %s" % (rid, k, "/".join(NESTED))); return
    op = ops[0]
    allowed = {op} | ({"ticks", "hours"} if op in ("ton", "tof") else {"preset", "reset"} if op == "ctu" else set())
    for f in e:
        if f not in allowed:
            errs.append("%s: %s (%s) has an unknown field %s" % (rid, k, op, f))
    if op == "any":
        br = e.get("any")
        if not isinstance(br, list) or not br:
            errs.append("%s: %s any needs a list of at least one condition object" % (rid, k)); return
        for b in br:
            if isinstance(b, dict): _when(rid, b, sensors, tagnames, disabled, errs, warns, depth + 1)
            else: errs.append("%s: %s any branch is not an object" % (rid, k))
        return
    if isinstance(e.get(op), dict): _when(rid, e[op], sensors, tagnames, disabled, errs, warns, depth + 1)
    else: errs.append("%s: %s %s needs a condition object" % (rid, k, op))
    if op in ("ton", "tof"):
        ticks = _whole(e.get("ticks")) if "ticks" in e else False
        hours = isinstance(e.get("hours"), (int, float)) and not isinstance(e.get("hours"), bool) and e["hours"] > 0
        if ticks == hours:
            errs.append("%s: %s %s needs ticks (a whole number, 1 or more) or hours (more than 0), not both" % (rid, k, op))
    if op == "ctu":
        if not _whole(e.get("preset")):
            errs.append("%s: %s ctu needs preset (a whole number, 1 or more)" % (rid, k))
        if "reset" in e:
            if isinstance(e["reset"], dict): _when(rid, e["reset"], sensors, tagnames, disabled, errs, warns, depth + 1)
            else: errs.append("%s: %s ctu reset is not a condition object" % (rid, k))


def measured(when, log, rid):
    """A when with the MEASURED mark conditions renamed to their sensors, key order kept."""
    out = {}
    for k, w in when.items():
        if k in MEASURED:
            log.append("%s: %s -> %s" % (rid, k, MEASURED[k][0]))
            k = MEASURED[k][0]
        out[k] = w
    return out


def preset_of(book, log=None):
    log = [] if log is None else log
    out = dict(book)
    out["preset"] = {"id": "LadderV2", "source": "docs/playbook.gates.json", "schema": "docs/rimplc/schema/ladder.schema.json"}
    sensors = dict(book.get("sensors") or {})
    used = {k for g in book["gates"] for k in (g.get("when") or {}) if k in MEASURED}
    for mk in sorted(used):
        key, spec = MEASURED[mk]
        if key not in sensors:
            sensors[key] = dict(spec, fallback=mk)
    out["sensors"] = sensors
    gates = []
    for g in book["gates"]:
        g = dict(g)
        if any(k in MEASURED for k in (g.get("when") or {})):
            g["when"] = measured(g["when"], log, g["id"])
        g["source"] = "book"
        g.setdefault("mode", "advise")
        req = REQUIRES_BY_ID.get(g["id"]) or REQUIRES_BY_FAMILY.get(g.get("family"))
        if req and "requires" not in g:
            g["requires"] = list(req)
        gates.append(g)
    out["gates"] = gates
    # keep the top-level key order of the book, preset first after version
    order = ["version", "preset", "note", "sensors", "gates", "tags", "marks"]
    return {k: out[k] for k in order if k in out}


def check(doc, label):
    se = schema_errors(doc)
    re_, rw = rule_errors(doc)
    n = len(doc.get("gates", []))
    print("%s: %d rungs, %d sensors, %d constants, %d variables" % (
        label, n, len(doc.get("sensors") or {}), len((doc.get("tags") or {}).get("constants") or {}),
        len((doc.get("tags") or {}).get("variables") or {})))
    for e in se: print("  SCHEMA", e)
    for e in re_: print("  RULE  ", e)
    for w in rw: print("  note  ", w)
    ok = not se and not re_
    print("  ->", "valid" if ok else "INVALID")
    return ok


def main(argv):
    paths = [a for a in argv if not a.startswith("--")]
    src = paths[0] if paths else PLAYBOOK
    doc = load(src)
    ok = check(doc, os.path.relpath(src, ROOT))
    if "--emit" in argv and src == PLAYBOOK:
        log = []
        pre = preset_of(doc, log)
        for line in log:
            print("  rewrite", line)
        ok = check(pre, "RimPLC/Presets/LadderV2.json (emitted)") and ok
        os.makedirs(os.path.dirname(PRESET), exist_ok=True)
        with open(PRESET, "w", encoding="utf-8", newline="\n") as f:
            json.dump(pre, f, indent=1, ensure_ascii=False)
            f.write("\n")
        gated = [g["id"] for g in pre["gates"] if g.get("requires")]
        print("  wrote %s (%d rungs gated by requires)" % (os.path.relpath(PRESET, ROOT), len(gated)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
