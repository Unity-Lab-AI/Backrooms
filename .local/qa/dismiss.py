"""Dismiss every letter whose label contains one of the given strings: python .local/qa/dismiss.py "Trader" "rain" """
import json, subprocess, sys, re
o = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", "rimworld/list_letters", "{}"], capture_output=True, text=True).stdout
for m in re.finditer(r'"id": "(Letter_\d+)",\s*"type": "[^"]*",\s*"letterDef": "[^"]*",\s*"label": "([^"]*)"', o):
    if any(k.lower() in m.group(2).lower() for k in sys.argv[1:]):
        r = subprocess.run([sys.executable, ".local/qa/bridge.py", "call", "rimworld/dismiss_letter", json.dumps({"letterId": m.group(1)})], capture_output=True, text=True).stdout
        print(m.group(2), "dismissed" if '"success": true' in r else "FAILED")
