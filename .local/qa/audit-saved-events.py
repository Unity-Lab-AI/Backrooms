"""Every company event in the newest save whose key wants more {n} arguments than it was saved with."""
import glob, os, re, sys
import xml.etree.ElementTree as ET

keys = {}
for path in glob.glob("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/*.xml"):
    for m in re.finditer(r"<(RR_[A-Za-z0-9_]+)>(.*?)</\1>", open(path, encoding="utf-8").read(), re.S):
        keys[m.group(1)] = m.group(2)

saves = glob.glob(os.path.join(os.environ["USERPROFILE"], "AppData", "LocalLow", "Ludeon Studios",
                               "RimWorld by Ludeon Studios", "Saves", "rimbridge_save_*.rws"))
path = sys.argv[1] if len(sys.argv) > 1 else max(saves, key=os.path.getmtime)
print("save:", os.path.basename(path))
seen = set()
for node in ET.parse(path).getroot().iter("li"):
    key = None
    for child in node:
        if child.text and child.text.startswith("RR_") and child.tag.lower().endswith("key"):
            key = child.text
    if not key or key not in keys:
        continue
    args = [c for c in node if c.tag.lower().endswith("arguments")]
    count = len(list(args[0])) if args else 0
    wanted = [int(n) for n in re.findall(r"\{(\d+)", keys[key])]
    need = max(wanted) + 1 if wanted else 0
    if need > count and key not in seen:
        seen.add(key)
        print("%s wants %d, saved with %d: %s" % (key, need, count, keys[key][:120]))
