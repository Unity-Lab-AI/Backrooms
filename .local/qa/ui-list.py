"""List the actionable/labelled elements of the top RimWorld window through the bridge (no real input)."""
import json, re, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), "call", "rimworld/get_ui_layout", "{}"],
                     capture_output=True, text=True, encoding="utf-8").stdout
pat = re.compile(r'"targetId":\s*"([^"]+)",\s*"kind":\s*"([^"]+)",\s*"source":\s*"([^"]*)",\s*"label":\s*("[^"]*"|null)[^}]*?"actionable":\s*(true|false)', re.S)
filt = sys.argv[1].lower() if len(sys.argv) > 1 else ""
for m in pat.finditer(out):
    line = "%s %s %s %s" % (m.group(1), m.group(2), m.group(4), m.group(5))
    if filt in line.lower(): print(line)
