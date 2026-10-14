"""RimPLC P0: validate a ladder against the frozen schemas and the import rules, and write the book preset.

    python tools/rimplc-check.py                      # validate docs/playbook.gates.json
    python tools/rimplc-check.py --emit               # also write RimPLC/Presets/LadderV2.json (the book preset)
    python tools/rimplc-check.py path/to/ladder.json  # validate any ladder / preset / export
    python tools/rimplc-check.py path --wiring        # also check its wiring against the code (see "Wiring" below)

The playbook and the preset are always checked for wiring too: every input has a writer, every game_set command a
handler, every rung a meta prompt, every sensor a display entry and a reader (classes W1-W10 below).

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
        "note": "defName verified (decomp, ResearchProjectDefOf.MicroelectronicsBasics)",
        "group": "Research done", "label": "Microelectronics researched", "severity": "info",
        "tip": "Microelectronics basics is finished (hi-tech benches, comms)."}),
    "mark_research_transport_pod": ("research_transportpod", {
        "source": "RimPLC: ResearchProjectDef TransportPod .IsFinished", "type": "bool", "cadence": "slow",
        "api": "ResearchProjectDef.IsFinished", "status": "UNVERIFIED",
        "note": "defName TransportPod UNVERIFIED (no ResearchProjectDefOf entry); if it is wrong the key stays unmeasured and the fallback mark is read",
        "group": "Research done", "label": "Transport pods researched", "severity": "info",
        "tip": "Transport pod research is finished (pod raids, pod gifts)."}),
    "mark_research_xenogenetics": ("research_xenogenetics", {
        "source": "RimPLC: ResearchProjectDef Xenogenetics .IsFinished", "type": "bool", "cadence": "slow",
        "api": "ResearchProjectDef.IsFinished", "status": "UNVERIFIED", "requires": ["Biotech"],
        "note": "defName Xenogenetics UNVERIFIED (Biotech); if it is wrong the key stays unmeasured and the fallback mark is read",
        "group": "Research done", "label": "Xenogenetics researched", "severity": "info",
        "tip": "Xenogenetics is finished (gene extractor and assembler)."}),
    "mark_caravan_out": ("caravan_out", {
        "source": "RimPLC: Find.WorldObjects.Caravans, any IsPlayerControlled", "type": "bool", "cadence": "slow",
        "api": "WorldObjectsHolder.Caravans", "status": "verified",
        "group": "World", "label": "A caravan is out", "severity": "info",
        "tip": "A player caravan is travelling the world map. Home has fewer hands."}),
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


# ------------------------------------------------------------------------------------------------------------------
# Wiring: the ladder against the code that feeds and answers it. Run on the playbook (and on --wiring). Each class is
# a defect a desk review found at least once; the check keeps it from coming back.
#   W1  a rung input (sensor key) nothing writes: no RimPLC sensor (RimPLC/Source/RimPLC/*.cs), no host input
#       (gates.host_inputs, pushed with rimplc/set_host), no fallback mark
#   W2  a catalogued sensor nothing writes, one marked not-measured that is written, a host input not catalogued
#   W3  a mark a rung reads that nothing sets (ladder_set mark in a step or meta prompt, a latch, a set_mark coil)
#   W4  a step / meta prompt naming a game_set command no handler answers (RimroomsAutomationComponent.cs); a
#       "[missing tool: game_set cmd X ...]" declaration is allowed only while X really has no handler
#   W5  a step / meta prompt calling a tool missing that a game_set command now answers
#   W6  the window's known-command list (MainTabWindow_RimPLC.KnownCmds) or her game_set tool's cmd enum (tools.py)
#       differs from the handlers
#   W7  meta prompts: duplicate ids, a prompt with no rung, a rung with no prompt, an empty prompt; priority ties
#   W8  a sensor's display entry: group (SensorView.GroupOrder), label, tip, severity, and a warn rule of the right form
#       for its type (a boolean rule on a bool, an operator rule on a number)
#   W9  a sensor registered but never read: no rung reads it, no step or prompt names it, no warn rule, and it is not
#       one of the DISPLAY_ONLY readings kept on purpose
#   W10 a type mismatch: the C# writes a number where the catalogue says bool (or the reverse), or a rung compares a
#       boolean reading with a number / a number with a boolean (such a condition can never hold)
# ------------------------------------------------------------------------------------------------------------------
CS_DIR = os.path.join(ROOT, "RimPLC", "Source", "RimPLC")
HANDLER_CS = os.path.join(ROOT, "src", "RimroomsAsyncIndustries", "Automation", "RimroomsAutomationComponent.cs")
GATES_PY = os.path.join(ROOT, ".local", "autopilot", "gates.py")
PROMPTS = os.path.join(ROOT, ".local", "autopilot", "rung-prompts.json")
DYNAMIC = ("research_", "count_", "condition_", "alert_")
# Shown on the Sensors tab for the player and nothing else reads them; each is kept on purpose. A key here that a rung,
# step, prompt or warn rule starts reading must be taken out (the check says so).
DISPLAY_ONLY = {
    "alert_<x>": "catalogue entry documenting the alert_<class> family",
    "colony_mechs": "colony size readout",
    "designations_harvest": "work queued readout", "designations_mine": "work queued readout",
    "game_conditions": "the list behind condition_<def>", "simple_benches": "research equipment readout",
    "hitech_benches": "research equipment readout (rungs read count_hitechresearchbench)",
    "multi_analyzers": "research equipment readout", "quests_active": "quest readout",
    "power_nets": "the total behind power_nets_dead", "storage_buildings": "storage readout",
    "ideo_roles": "the total behind ideo_roles_unassigned",
}
# a tool once named as missing -> the game_set command that answers it now
RETIRED_MISSING = {
    "set_self_tend": "self_tend", "set_schedule": "schedule", "set_drug_policy": "drug_policy",
    "set_bill_count": "bill_count", "set_ideo_role": "ideo_role", "place_building": "build",
    "build_furniture": "build", "tame_animal": "tame", "build_pen": "pen", "queue_research": "research",
    "research_queue": "research", "set_research": "research", "set_bed_medical": "bed_medical",
    "set_cooler_target": "cooler_temp", "campfire": "build", "barricades": "build", "zone_create": "zone_create",
    "set_prisoner_interaction": "prisoner", "trade_dialog": "trade",
    "set_bed_price": "guest_beds", "call_trader": "call_trader",
}
CMD_REF = re.compile(r"game_set\s+cmd\s*[= ]\s*([a-z_]+)")
DECLARED = re.compile(r"\[missing tool: game_set cmd ([a-z_]+)")
# claims that name a tool: any game_set command name counts
TOOL_CLAIMS = (re.compile(r"MISSING[_ ]TOOL:?\s+([a-z_]+)"), re.compile(r"([a-z_]+)\s+\(MISSING\)"),
               re.compile(r"([a-z_]+)\s+tool\s+(?:is\s+)?missing"), re.compile(r"missing\s+'([a-z_]+)'"),
               re.compile(r"\bno\s+([a-z_]+)\s+tool"), re.compile(r"missing tool:\s*([a-z_]+)"))
# looser claims ("MISSING x", "x missing", "x is missing"): only the retired tool names count, since "research
# missing" (not researched) or "MISSING stockpile_filter mode" (a mode, not the tool) mean something else
LOOSE_CLAIMS = (re.compile(r"\bMISSING:?\s+([a-z_]+)"), re.compile(r"([a-z_]+)\s+(?:is\s+)?missing"))


def _read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def _leaves(when):
    for k, w in (when or {}).items():
        if isinstance(w, dict):
            op = [o for o in NESTED if o in w]
            if len(op) != 1:
                continue
            subs = w["any"] if op[0] == "any" else [w[op[0]]]
            if op[0] == "ctu" and isinstance(w.get("reset"), dict):
                subs = list(subs) + [w["reset"]]
            for b in subs:
                if isinstance(b, dict):
                    yield from _leaves(b)
        else:
            yield k, w


def _latch_name(rid):
    return re.sub(r"[^a-z0-9]+", "_", str(rid).lower()).strip("_")[:35] + "_done"


def writers():
    """key -> set of kinds ('number' / 'bool' / 'list') the RimPLC C# writes; and the host input keys."""
    cs = "\n".join(_read(os.path.join(CS_DIR, n)) for n in sorted(os.listdir(CS_DIR)) if n.endswith(".cs"))
    w = {}
    for k, rhs in re.findall(r'st\["([a-z0-9_]+)"\]\s*=\s*([^;]+);', cs):
        r = rhs.strip()
        kind = "number" if ("(double)" in r or "Math.Round" in r) else \
               "list" if (r in ("labels", "defs", "conds") or ".ToList()" in r) else "bool"
        w.setdefault(k, set()).add(kind)
    for k in re.findall(r'Count\(st, home, "([a-z0-9_]+)"', cs):
        w.setdefault(k, set()).add("number")
    for k in re.findall(r'\{ "[A-Za-z]+", "([a-z_]+)" \}', cs):          # Resources / DesignationKeys
        w.setdefault(k, set()).add("number")
    for k in re.findall(r'\{ "([a-z_]+)", "Alert_', cs):                    # AlertClasses
        w.setdefault("alert_" + k, set()).add("bool")
    g = _read(GATES_PY)
    hs = g[g.index("def host_inputs"):g.index("def push_host")]
    host = set(re.findall(r'out\["([a-z_]+)"\]', hs)) | set(re.findall(r"\b([a-z_]+)=(?:unanswered|joins|mod\b)", hs))
    return w, host


def wiring(doc, label):
    need = [CS_DIR, HANDLER_CS, GATES_PY, PROMPTS]
    if not all(os.path.exists(p) for p in need):
        print("%s wiring: skipped (needs %s)" % (label, ", ".join(os.path.relpath(p, ROOT) for p in need if not os.path.exists(p))))
        return True
    errs, notes = [], []
    S = doc.get("sensors") or {}
    tg = doc.get("tags") or {}
    tagnames = set(tg.get("constants") or {}) | set(tg.get("variables") or {})
    written, host = writers()
    have = set(written) | host | {k for k, v in S.items() if isinstance(v, dict) and v.get("fallback")}
    gates = doc.get("gates", [])

    def text_of(g):
        t = list(g.get("then") or []) + list(g.get("never") or [])
        return t + [str(g.get(k)) for k in ("check", "note", "notice") if g.get(k)]

    tops = []

    def hook(kv):
        tops.append([k for k, _ in kv])
        return dict(kv)

    prompts = json.loads(_read(PROMPTS), object_pairs_hook=hook)
    top = tops[-1] if tops else []
    steps = [(g["id"], s) for g in gates for s in text_of(g)] + \
            [("prompt:" + k, v) for k, v in prompts.items() if isinstance(v, str)]
    alltext = "\n".join(s for _, s in steps)

    # W1, W10 (conditions)
    reads = {}
    for g in gates:
        for k, want in _leaves(g.get("when")):
            reads.setdefault(k, []).append(g["id"])
            if k == "letter_matches" or k.startswith("mark_") or k in tagnames:
                continue
            if k not in have and not k.startswith(DYNAMIC):     # research_/count_/condition_/alert_: read by family
                (notes if g.get("disabled") else errs).append(
                    "W1 %s: input %s has no writer (no sensor, host input or fallback)" % (g["id"], k))
            t = (S.get(k) or {}).get("type")
            if t is None and k.startswith(("alert_", "condition_", "research_")):
                t = "bool"
            elif t is None and k.startswith("count_"):
                t = "int"
            num = isinstance(want, (int, float)) and not isinstance(want, bool)
            if t == "bool" and (num or (isinstance(want, str) and want[:1] in "<>!")):
                errs.append("W10 %s: %s is a boolean reading compared with %r (never holds)" % (g["id"], k, want))
            if t in ("int", "float") and isinstance(want, bool):
                errs.append("W10 %s: %s is a number compared with %r" % (g["id"], k, want))
    # W2, W10 (catalogue)
    for k, spec in S.items():
        spec = spec or {}
        if "<" in k:
            continue
        if spec.get("status") == "not-measured":
            if k in have:
                errs.append("W2 sensor %s is marked not-measured but %s writes it" % (k, "the host push" if k in host else "RimPLC"))
            elif k in reads:
                notes.append("W2 sensor %s is not measured yet; rungs reading it stay quiet: %s" % (k, ", ".join(sorted(set(reads[k])))))
            continue
        if k not in have and not k.startswith(DYNAMIC):
            errs.append("W2 sensor %s is catalogued as measured but nothing writes it" % k)
        kinds, t = written.get(k), spec.get("type")
        want = {"bool": "bool", "int": "number", "float": "number", "labels": "list"}.get(t)
        if kinds and want and want not in kinds:
            errs.append("W10 sensor %s: catalogue type %s, the C# writes %s" % (k, t, "/".join(sorted(kinds))))
    for k in sorted(host - set(S)):
        errs.append("W2 host input %s is pushed but not in the sensor catalogue" % k)
    # W3
    setters = set()
    for g in gates:
        if g.get("latch"):
            setters.add(_latch_name(g["id"]))
        for c in g.get("coils") or []:
            if isinstance(c, dict) and c.get("do") == "set_mark" and c.get("name"):
                setters.add(c["name"])
    setters |= set(re.findall(r"ladder_set mark ([a-z0-9_]+)", alltext))
    for k, ids in sorted(reads.items()):
        if k.startswith("mark_") and k[5:] not in setters:
            errs.append("W3 mark %s is read (%s) but nothing sets it" % (k, ", ".join(sorted(set(ids))[:4])))
    # W4, W5, W6
    handlers = set(re.findall(r'case "([a-z_]+)": return', _read(HANDLER_CS)))
    for src, s in steps:
        declared = set(DECLARED.findall(s))
        for c in declared:
            if c in handlers:
                errs.append("W4 %s: declares game_set cmd %s missing, but a handler answers it" % (src, c))
            else:
                notes.append("W4 %s: game_set cmd %s declared missing (the step carries the fallback)" % (src, c))
        for c in CMD_REF.findall(s):
            if c not in handlers and c not in declared:
                errs.append("W4 %s: game_set cmd %s has no handler" % (src, c))
        if re.search(r"missing|MISSING|no [a-z_]+ tool", s):
            hit = set()
            for rx in TOOL_CLAIMS + LOOSE_CLAIMS:
                for name in rx.findall(s):
                    now = RETIRED_MISSING.get(name) or (name if name in handlers and rx in TOOL_CLAIMS else None)
                    if now and now in handlers and name not in hit:
                        hit.add(name)
                        errs.append("W5 %s: calls %s missing, but game_set cmd %s answers it" % (src, name, now))
    win = _read(os.path.join(CS_DIR, "MainTabWindow_RimPLC.cs"))
    m = re.search(r"KnownCmds = new HashSet<string>\s*\{(.*?)\};", win, re.S)
    known = set(re.findall(r'"([a-z_]+)"', m.group(1))) if m else set()
    if known != handlers:
        errs.append("W6 window KnownCmds differs from the handlers: only in the window %s, only in the handlers %s"
                    % (sorted(known - handlers), sorted(handlers - known)))
    tools_py = os.path.join(ROOT, ".local", "autopilot", "tools.py")
    if os.path.exists(tools_py):
        tm = re.search(r'"cmd": \{"type": "string", "enum": \[(.*?)\]\}', _read(tools_py), re.S)
        enum = set(re.findall(r'"([a-z_]+)"', tm.group(1))) if tm else set()
        internal = {"sensors"}      # the mod's own sensor-file dump, not a command she plays with
        if enum != handlers - internal:
            errs.append("W6 her game_set tool's cmd enum (tools.py) differs from the handlers: only in tools.py %s, only in the handlers %s"
                        % (sorted(enum - handlers), sorted(handlers - internal - enum)))
    # W7
    ids = [g["id"] for g in gates]
    dup = sorted({k for k in top if top.count(k) > 1})
    if dup:
        errs.append("W7 duplicate meta prompt ids: %s" % ", ".join(dup))
    for k in prompts:
        if k not in ids:
            errs.append("W7 meta prompt %s has no rung" % k)
    for i in ids:
        if not str(prompts.get(i) or "").strip():
            errs.append("W7 rung %s has no meta prompt" % i)
    by = {}
    for g in gates:
        by.setdefault(g.get("priority"), []).append(g["id"])
    for pr, v in sorted(by.items(), key=lambda kv: str(kv[0])):
        if len(v) > 1:
            errs.append("W7 priority tie at %s: %s" % (pr, ", ".join(v)))
    # W8
    view = _read(os.path.join(CS_DIR, "SensorView.cs"))
    gm = re.search(r"GroupOrder =\s*\{(.*?)\};", view, re.S)
    groups = set(re.findall(r'"([^"]+)"', gm.group(1))) if gm else set()
    for k, spec in S.items():
        spec = spec or {}
        miss = [f for f in ("label", "tip") if not spec.get(f)]
        if spec.get("group") not in groups:
            miss.append("group %r" % spec.get("group"))
        if spec.get("severity") not in ("critical", "warning", "info"):
            miss.append("severity %r" % spec.get("severity"))
        if miss:
            errs.append("W8 sensor %s display entry: %s" % (k, ", ".join(miss)))
        if "warn" in spec:
            rule, t = spec["warn"], spec.get("type")
            if isinstance(rule, bool):
                if t != "bool":
                    errs.append("W8 sensor %s: boolean warn rule on a %s reading (never trips)" % (k, t))
            elif isinstance(rule, str) and re.match(r"^(>=|<=|==|!=|>|<)-?\d+(\.\d+)?$", rule):
                if t == "bool":
                    errs.append("W8 sensor %s: warn rule %s on a bool reading (never trips)" % (k, rule))
            else:
                errs.append("W8 sensor %s: warn rule %r is not true/false or <op><number>" % (k, rule))
    # W9
    for k in S:
        named = k in reads or "warn" in (S[k] or {}) or \
            re.search(r"(?<![a-z0-9_])" + re.escape(k) + r"(?![a-z0-9_])", alltext)
        if k in DISPLAY_ONLY:
            if named:
                errs.append("W9 sensor %s is read now: take it out of DISPLAY_ONLY" % k)
        elif not named:
            errs.append("W9 sensor %s is registered but never read (no rung, step, prompt or warn rule)" % k)
    for k in DISPLAY_ONLY:
        if k not in S:
            errs.append("W9 DISPLAY_ONLY names %s, which is not in the catalogue" % k)

    print("%s wiring: %d keys written (%d host inputs), %d game_set handlers, %d meta prompts" % (
        label, len(written) + len(host), len(host), len(handlers), len(prompts)))
    for e in errs:
        print("  WIRING", e)
    for n in notes:
        print("  note  ", n)
    print("  ->", "wiring CLEAN" if not errs else "WIRING %d" % len(errs))
    return not errs


def main(argv):
    paths = [a for a in argv if not a.startswith("--")]
    src = paths[0] if paths else PLAYBOOK
    doc = load(src)
    ok = check(doc, os.path.relpath(src, ROOT))
    if os.path.abspath(src) in (PLAYBOOK, PRESET) or "--wiring" in argv:
        ok = wiring(doc, os.path.relpath(src, ROOT)) and ok
    if "--emit" in argv and src == PLAYBOOK:
        log = []
        pre = preset_of(doc, log)
        for line in log:
            print("  rewrite", line)
        ok = check(pre, "RimPLC/Presets/LadderV2.json (emitted)") and ok
        ok = wiring(pre, "RimPLC/Presets/LadderV2.json (emitted)") and ok
        os.makedirs(os.path.dirname(PRESET), exist_ok=True)
        with open(PRESET, "w", encoding="utf-8", newline="\n") as f:
            json.dump(pre, f, indent=1, ensure_ascii=False)
            f.write("\n")
        gated = [g["id"] for g in pre["gates"] if g.get("requires")]
        print("  wrote %s (%d rungs gated by requires)" % (os.path.relpath(PRESET, ROOT), len(gated)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
