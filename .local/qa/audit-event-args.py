"""Every RecordEvent("KEY", args...) call against the highest {n} in KEY's English text."""
import glob, re

keys = {}
for path in glob.glob("Mod/Rimrooms - Async Industries/1.6/Languages/English/Keyed/*.xml"):
    for m in re.finditer(r"<(RR_[A-Za-z0-9_]+)>(.*?)</\1>", open(path, encoding="utf-8").read(), re.S):
        keys[m.group(1)] = m.group(2)

for path in glob.glob("src/RimroomsAsyncIndustries/**/*.cs", recursive=True):
    text = open(path, encoding="utf-8").read()
    for m in re.finditer(r'(?:RecordEvent|Note)\(\s*"(RR_[A-Za-z0-9_]+)"((?:[^;])*?)\);', text):
        key, rest = m.group(1), m.group(2)
        depth, args = 0, 0
        for ch in rest:
            if ch in "([{": depth += 1
            elif ch in ")]}": depth -= 1
            elif ch == "," and depth == 0: args += 1
        wanted = [int(n) for n in re.findall(r"\{(\d+)", keys.get(key, ""))]
        need = max(wanted) + 1 if wanted else 0
        if key not in keys:
            print("MISSING KEY", key, path)
        elif need > args - (1 if "RecordEvent" in m.group(0)[:12] else 0):
            line = text[:m.start()].count("\n") + 1
            print("%s needs %d, gets %d  -- %s:%d  %s" % (key, need, args - (1 if "RecordEvent" in m.group(0)[:12] else 0), path, line, rest.strip()[:110]))
