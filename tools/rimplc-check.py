"""RimPLC P0: validate a ladder against the frozen schemas and the import rules, and write the book preset.

    python tools/rimplc-check.py                      # validate docs/playbook.gates.json
    python tools/rimplc-check.py --emit               # also write RimPLC/Presets/LadderV2.json (the book preset)
    python tools/rimplc-check.py path/to/ladder.json  # validate any ladder / preset / export

Schemas: docs/rimplc/schema/*.json (ladder, rung, sensor, tag, mark; tools.schema.json holds the API shapes).
Import rules (docs/RIMPLC_DESIGN.md section 7): unique ids, numeric priority, every `when` key is a sensor, a tag,
mark_*, alert_* or letter_matches (rungs that are `disabled` may name unmeasured keys), every {TAG} bound names a
tag, and non-book rungs carry at most 8 `then` lines of at most 300 characters. The emitted preset is the playbook
unchanged plus `preset`, and per rung `source: book`, `mode: advise` (when absent) and `requires` for DLC / mod
families, so .local/autopilot/gates.py still loads it.
"""
import json, os, re, sys

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
        for k, w in (g.get("when") or {}).items():
            known = (k == "letter_matches" or k.startswith(("mark_", "alert_")) or k in sensors or k in tagnames)
            if not known:
                (warns if g.get("disabled") else errs).append("%s: when key %s has no sensor, tag or mark" % (rid, k))
            if isinstance(w, str):
                for t in re.findall(r"\{([^}]*)\}", w):
                    if t.strip() not in tagnames:
                        errs.append("%s: %s names unknown tag {%s}" % (rid, k, t))
                if w[:1] in "<>!" and not any(w.startswith(o) for o in (">=", "<=", "!=", ">", "<")):
                    errs.append("%s: %s has no operator in %r" % (rid, k, w))
    return errs, warns


def preset_of(book):
    out = dict(book)
    out["preset"] = {"id": "LadderV2", "source": "docs/playbook.gates.json", "schema": "docs/rimplc/schema/ladder.schema.json"}
    gates = []
    for g in book["gates"]:
        g = dict(g)
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
        pre = preset_of(doc)
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
