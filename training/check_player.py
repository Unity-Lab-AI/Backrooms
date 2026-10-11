"""Validate training/data/player.jsonl against the player's real tool list and the owner's laws.

    python training/check_player.py [path]

Checks every episode: JSON; role order (system, user, then assistant/tool rounds, ending on a plain assistant
line); every tool_call names a tool in tools.json and its arguments validate against that tool's schema (types,
enums, required, no unknown keys where the schema forbids them); never unpause (or run time) after exploring is
done until pawns_set and assign_set are marked -- unless that step is a weight-0 mistake the guard refused; no
UI clicking for what game_set does; no looping cell reads; the owner's handle nowhere (read from the secret files
at check time only, never written anywhere); every spoken line and every narration passes the stream filter.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, ".local", "autopilot"))
import guards  # noqa: E402  (read-only use: the same filter the live stream uses)

TOOLS = json.load(open(os.path.join(HERE, "data", "tools.json"), encoding="utf-8"))
SCHEMA = {t["function"]["name"]: t["function"]["parameters"] for t in TOOLS}
SPOKEN = {"say": ["text"], "reply_chat": ["text"], "twitch_chat": ["text"], "webcam": ["caption"], "snap": ["caption"]}
CLICKS = {"game_right_click_cell", "game_drag_cell", "game_execute_context_menu_option", "game_get_context_menu_options"}
REFUSAL = ("REFUSED", "refused", "error", "bad arguments", "unknown tool", "BLOCKED")


def secrets():
    out = []
    for p in (os.path.join(ROOT, ".local", "autopilot", "secret-words.txt"), os.path.join(ROOT, ".local", "tw", "owner.txt")):
        try:
            for w in open(p, encoding="utf-8"):
                w = w.strip()
                if w and not w.startswith("#") and len(w) >= 3:
                    out.append(w.lower())
        except OSError:
            pass
    return out


TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "object": dict, "array": list}


def validate(val, sch, path="args"):
    errs = []
    t = sch.get("type")
    if t:
        ts = t if isinstance(t, list) else [t]
        ok = False
        for tt in ts:
            py = TYPES.get(tt)
            if py is None:
                ok = True
            elif tt in ("integer", "number") and isinstance(val, bool):
                continue
            elif isinstance(val, py):
                ok = True
        if not ok:
            return ["%s: expected %s, got %r" % (path, t, val)]
    if "enum" in sch and val not in sch["enum"]:
        errs.append("%s: %r not in enum %s" % (path, val, sch["enum"]))
    if isinstance(val, dict) and (sch.get("type") == "object" or "properties" in sch):
        props = sch.get("properties", {})
        for k in sch.get("required", []):
            if k not in val:
                errs.append("%s: missing required %s" % (path, k))
        for k, v in val.items():
            if k in props:
                errs += validate(v, props[k], path + "." + k)
            elif sch.get("additionalProperties") is False:
                errs.append("%s: unknown key %s" % (path, k))
    if isinstance(val, list) and "items" in sch:
        for i, v in enumerate(val):
            errs += validate(v, sch["items"], "%s[%d]" % (path, i))
    return errs


def dirty(text):
    if guards.CLEAN_BLOCK.search(text) or guards.EXTRA_BLOCK.search(text) or guards.TECH_BLOCK.search(text):
        return True
    if re.search(r"\*[^*]+\*|#\w|https?://", text) or any(ord(c) >= 0x2190 for c in text):
        return True
    return False


def starts_time(name, a):
    return ((name == "game_pause_game" and a.get("pause", True) is False) or
            (name == "game_set_time_speed" and str(a.get("speed", "")).lower() not in ("", "0", "paused")) or
            name == "play_slices")


def check_episode(ep, secret):
    errs = []
    if ep.get("tools") != "TOOLS" and ep.get("tools") != TOOLS:
        errs.append("tools is neither 'TOOLS' nor the tools.json list")
    msgs = ep.get("messages")
    if not isinstance(msgs, list) or len(msgs) < 4:
        return errs + ["messages missing or too short"]
    meta = ep.get("meta") or {}
    explored = bool(meta.get("explore_done"))
    marks = dict(meta.get("marks") or {})
    blob = json.dumps(ep, ensure_ascii=False).lower()
    for w in secret:
        if w in blob:
            errs.append("owner handle present")
    if msgs[0].get("role") != "system" or msgs[1].get("role") != "user":
        errs.append("must start system, user")
    cell_reads = 0
    i = 2
    pending = []
    last = "user"
    while i < len(msgs):
        m = msgs[i]
        role = m.get("role")
        if role == "user":
            if last != "final":
                errs.append("msg %d: user must follow a final assistant line" % i)
            last = "user"
        elif role == "assistant":
            if last == "final":
                errs.append("msg %d: two assistant turns with no user between" % i)
            content = m.get("content") or ""
            if content and dirty(content):
                errs.append("msg %d: narration fails the stream filter: %r" % (i, content[:120]))
            if len(content) > 320:
                errs.append("msg %d: narration too long" % i)
            calls = m.get("tool_calls") or []
            if len(calls) > 6:
                errs.append("msg %d: more than 6 tool calls" % i)
            results = msgs[i + 1:i + 1 + len(calls)]
            if len(results) != len(calls) or any(r.get("role") != "tool" for r in results):
                errs.append("msg %d: tool results do not match the calls" % i)
                return errs
            weight0 = m.get("weight") == 0
            refused_any = False
            for c, res in zip(calls, results):
                fn = c.get("function") or {}
                name, a = fn.get("name"), fn.get("arguments")
                if res.get("tool_name") != name:
                    errs.append("msg %d: tool_name %s != call %s" % (i, res.get("tool_name"), name))
                if name not in SCHEMA:
                    errs.append("msg %d: unknown tool %s" % (i, name)); continue
                if not isinstance(a, dict):
                    errs.append("msg %d: %s arguments are not an object" % (i, name)); continue
                errs += ["msg %d %s: %s" % (i, name, e) for e in validate(a, SCHEMA[name])]
                rtxt = str(res.get("content", ""))
                refused = rtxt.startswith(REFUSAL) or "\n   refused:" in rtxt or "; refused:" in rtxt
                refused_any = refused_any or refused
                for k in SPOKEN.get(name, []):
                    if k in a and dirty(str(a[k])):
                        errs.append("msg %d: %s.%s fails the stream filter: %r" % (i, name, k, a[k]))
                if name in CLICKS:
                    errs.append("msg %d: UI click %s where game_set does it in one call" % (i, name))
                if name == "game_execute_gizmo" and str(a.get("gizmoId", "")).startswith("main-tab"):
                    errs.append("msg %d: opening a main tab instead of game_set" % i)
                if name in ("game_get_cell_info", "game_get_cells_info"):
                    cell_reads += 1
                if starts_time(name, a) and explored and not (marks.get("pawns_set") and marks.get("assign_set")):
                    if not (weight0 and refused):
                        errs.append("msg %d: %s starts time before pawns_set and assign_set are marked" % (i, name))
                if name == "game_set" and a.get("cmd") == "explore" and "nothing left to explore" in rtxt:
                    explored = True
                if name == "ladder_set" and a.get("op") == "mark" and rtxt.startswith("ladder updated"):
                    marks[a.get("name")] = a.get("value") in (True, "true", 1)
            if weight0 and not refused_any:
                errs.append("msg %d: weight 0 on a step the game did not refuse" % i)
            if weight0:
                nxt = next((x for x in msgs[i + 1 + len(calls):] if x.get("role") == "assistant"), None)
                if not nxt or not nxt.get("tool_calls"):
                    errs.append("msg %d: a refused mistake must be followed by a corrective call" % i)
            i += len(calls)
            last = "calls" if calls else "final"
        elif role == "tool":
            errs.append("msg %d: stray tool message" % i)
        else:
            errs.append("msg %d: bad role %r" % (i, role))
        i += 1
    if msgs[-1].get("role") != "assistant" or msgs[-1].get("tool_calls"):
        errs.append("must end on a plain assistant line")
    if cell_reads > 2:
        errs.append("%d cell reads in one episode (reading cells in a loop)" % cell_reads)
    return errs


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "data", "player.jsonl")
    secret = secrets()
    bad = total = 0
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if not line.strip():
            continue
        total += 1
        try:
            ep = json.loads(line)
        except Exception as e:
            print("line %d: bad JSON: %s" % (n, e)); bad += 1; continue
        errs = check_episode(ep, secret)
        if errs:
            bad += 1
            print("line %d (%s):" % (n, (ep.get("meta") or {}).get("category")))
            for e in errs[:8]:
                print("   ", e)
    print("%d episodes, %d failing, %d secret word(s) checked" % (total, bad, len(secret)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
