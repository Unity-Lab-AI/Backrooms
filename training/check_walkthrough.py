"""Validate training/data/knowledge_walkthrough.jsonl: JSON and roles, word counts (long 600-1500), order
explore -> pawn_priorities -> unpause in long rows, clean words, tool names exist in tools.json."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "training", "data", "knowledge_walkthrough.jsonl")
sys.path.insert(0, os.path.join(ROOT, ".local", "autopilot"))
from guards import CLEAN_BLOCK, EXTRA_BLOCK  # noqa: E402

TOOLS = json.load(open(os.path.join(ROOT, "training", "data", "tools.json"), encoding="utf-8"))
TOOLS = [t.get("function", t) for t in TOOLS]
NAMES = {t["name"] for t in TOOLS}
CMDS = set(next(t for t in TOOLS if t["name"] == "game_set")["parameters"]["properties"]["cmd"]["enum"])
PREFIX = re.compile(r"\b((?:game|pawn|ladder|order|reply|play|run|empire|new|read|twitch)_[a-z_]+)\b")


def main():
    errs, counts, n, longs, shorts = [], {}, 0, 0, 0
    for ln, line in enumerate(open(DATA, encoding="utf-8"), 1):
        n += 1
        try:
            r = json.loads(line)
        except ValueError as e:
            errs.append(f"{ln}: bad json {e}"); continue
        msgs = r.get("messages")
        if not isinstance(msgs, list) or [m.get("role") for m in msgs] != ["system", "user", "assistant"]:
            errs.append(f"{ln}: roles"); continue
        if any(not isinstance(m.get("content"), str) or not m["content"].strip() for m in msgs):
            errs.append(f"{ln}: empty content")
        var = r.get("meta", {}).get("variant", "")
        if not var or not r["meta"].get("sources"):
            errs.append(f"{ln}: meta incomplete")
        a = msgs[2]["content"]
        words = len(a.split())
        if var.startswith("long"):
            longs += 1
            if not 600 <= words <= 1500:
                errs.append(f"{ln}: long walkthrough {words} words")
            i, j, k = a.find("game_set cmd explore"), a.find("pawn_priorities"), a.lower().find("unpause")
            if not (0 <= i < j < k):
                errs.append(f"{ln}: order explore/priorities/unpause broken ({i},{j},{k})")
        else:
            shorts += 1
        for key in var.split("|")[1:]:
            counts[key] = counts.get(key, 0) + 1
        for m in msgs[1:]:
            hit = CLEAN_BLOCK.search(m["content"]) or EXTRA_BLOCK.search(m["content"])
            if hit:
                errs.append(f"{ln}: unclean word {hit.group(0)!r}")
        for t in PREFIX.findall(a):
            if t not in NAMES:
                errs.append(f"{ln}: unknown tool {t}")
        for c in re.findall(r"game_set cmd (\w+)", a):
            if c not in CMDS:
                errs.append(f"{ln}: unknown game_set cmd {c}")
    print(f"rows={n} long={longs} short={shorts} errors={len(errs)}")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    for e in errs[:40]:
        print("  " + e)
    return 1 if errs or longs < 60 else 0


if __name__ == "__main__":
    sys.exit(main())
