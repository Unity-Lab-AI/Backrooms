"""Live parity read: the Python ladder (gates.py, bridge sweep) against RimPLC (in-game engine) on the same game state.
    python .local/qa/rimplc-parity.py      -> prints sensor differences and live-rung differences"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "autopilot"))
import gates, tools
call = tools.Toolbox().bridge.call
hits, st = gates.decide(every=True, write=False)
rs = gates.rimplc("read_state", {}, call=call) or {}
rl = gates.rimplc("read_ladder", {"top": 50}, call=call) or {}
cs = rs.get("state") or {}
same, diff, only_py, only_cs = [], [], [], []
for k in sorted(set(st) | set(cs)):
    if k in ("crew", "ok"): continue
    a, b = st.get(k, "<none>"), cs.get(k, "<none>")
    if a == "<none>": only_cs.append(k)
    elif b == "<none>": only_py.append(k)
    elif (isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) <= max(0.01, 0.02 * abs(a))) or a == b: same.append(k)
    else: diff.append((k, a, b))
print("sensors: %d same, %d differ, %d python-only, %d rimplc-only" % (len(same), len(diff), len(only_py), len(only_cs)))
for k, a, b in diff: print("  DIFF %-28s python=%-14s rimplc=%s" % (k, json.dumps(a, default=str)[:14], json.dumps(b, default=str)[:40]))
print("  python-only:", only_py[:40]); print("  rimplc-only:", only_cs[:40])
py = [h["id"] for h in hits]; cs_ids = [h["id"] for h in rl.get("live_rungs", [])]
print("live rungs python:", py); print("live rungs rimplc:", cs_ids)
print("RUNGS MATCH" if py == cs_ids else "RUNGS DIFFER")
