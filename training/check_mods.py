"""Validate training/data/knowledge_mods.jsonl: JSON, roles, sources on disk, every register mod >= 2 rows,
unique questions, clean words."""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "training", "data", "knowledge_mods.jsonl")
REG = os.path.join(ROOT, "outputs", "rimrooms-async-industries-register-2026-09-27",
                   "Rimrooms_Async_Industries_294_Mod_Integration_Register.html")
sys.path.insert(0, os.path.join(ROOT, ".local", "autopilot"))
from guards import CLEAN_BLOCK, EXTRA_BLOCK  # noqa: E402


def main():
    errs, counts, questions, n = [], {}, set(), 0
    for ln, line in enumerate(open(DATA, encoding="utf-8"), 1):
        n += 1
        try:
            r = json.loads(line)
        except ValueError as e:
            errs.append(f"{ln}: bad json {e}"); continue
        meta, msgs = r.get("meta", {}), r.get("messages")
        if not isinstance(msgs, list) or [m.get("role") for m in msgs] != ["system", "user", "assistant"]:
            errs.append(f"{ln}: roles"); continue
        if any(not isinstance(m.get("content"), str) or not m["content"].strip() for m in msgs):
            errs.append(f"{ln}: empty content")
        src = meta.get("source", "")
        if not src or not os.path.isfile(os.path.join(ROOT, src)):
            errs.append(f"{ln}: source missing {src!r}")
        if not meta.get("mod"):
            errs.append(f"{ln}: no meta.mod")
        counts[meta.get("mod")] = counts.get(meta.get("mod"), 0) + 1
        q = msgs[1]["content"].strip().lower()
        if q in questions:
            errs.append(f"{ln}: duplicate question {q!r}")
        questions.add(q)
        for m in msgs[1:]:
            hit = CLEAN_BLOCK.search(m["content"]) or EXTRA_BLOCK.search(m["content"])
            if hit:
                errs.append(f"{ln}: unclean word {hit.group(0)!r}")
    h = open(REG, encoding="utf-8").read()
    names = [html.unescape(x).strip() for x in
             re.findall(r'<article id="mod-\d+"><h3><span class="idx">\d+</span>\s*(.*?)\s*<span class="idx">', h)]
    missing = [x for x in names if counts.get(x, 0) < 2]
    for x in missing:
        errs.append(f"mod under-covered: {x} ({counts.get(x, 0)})")
    cross = sum(v for k, v in counts.items() if k and (k.startswith("cross-mod") or k not in names))
    print(f"rows={n} register_mods={len(names)} covered>=2={len(names) - len(missing)} "
          f"cross/other_rows={cross} errors={len(errs)}")
    for e in errs[:40]:
        print("  " + e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
