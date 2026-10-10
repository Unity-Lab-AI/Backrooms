import io, os, re, glob, hashlib, sys

root = r"C:\Users\gfour\Desktop\Backrooms"
mod = os.path.join(root, "Mod", "Rimrooms - Async Industries")
src = os.path.join(root, "src", "RimroomsAsyncIndustries")
fail = []

# 1. every package XML parses
import xml.etree.ElementTree as ET
xmls = glob.glob(os.path.join(mod, "**", "*.xml"), recursive=True)
for f in xmls:
    try:
        ET.parse(f)
    except Exception as e:
        fail.append("XML PARSE: %s :: %s" % (f, e))
print("xml files parsed: %d" % len(xmls))

# 2. keyed coverage: every RR_ key referenced from C# must exist in a keyed file
keys = set()
for f in glob.glob(os.path.join(mod, "**", "Keyed", "*.xml"), recursive=True):
    t = io.open(f, encoding="utf-8-sig").read()
    for m in re.finditer(r"<(RR_[A-Za-z0-9_]+)>", t):
        keys.add(m.group(1))
print("keyed RR_ strings defined: %d" % len(keys))

referenced = set()
for f in glob.glob(os.path.join(src, "**", "*.cs"), recursive=True):
    if os.sep + "bin" + os.sep in f or os.sep + "obj" + os.sep in f:
        continue
    t = io.open(f, encoding="utf-8-sig").read()
    for m in re.finditer(r'"(RR_[A-Za-z0-9_]+)"\s*\.\s*Translate', t):
        referenced.add(m.group(1))
    # keys passed as string literals into RecordEvent / failure-key fields
    for m in re.finditer(r'"(RR_(?:ConnectedWork|Event)_[A-Za-z0-9_]+)"', t):
        referenced.add(m.group(1))
missing = sorted(referenced - keys)
print("C# referenced RR_ keys: %d, missing: %d" % (len(referenced), len(missing)))
for k in missing:
    fail.append("MISSING KEY: %s" % k)

# 3. giverClass in WorkGiverDefs must exist as a public class in source
classes = set()
for f in glob.glob(os.path.join(src, "**", "*.cs"), recursive=True):
    if os.sep + "bin" + os.sep in f or os.sep + "obj" + os.sep in f:
        continue
    t = io.open(f, encoding="utf-8-sig").read()
    for m in re.finditer(r"class\s+([A-Za-z0-9_]+)", t):
        classes.add(m.group(1))
for f in glob.glob(os.path.join(mod, "**", "WorkGiverDefs", "*.xml"), recursive=True):
    t = io.open(f, encoding="utf-8-sig").read()
    for m in re.finditer(r"<giverClass>(.*?)</giverClass>", t):
        full = m.group(1).strip()
        if not full.startswith("RimroomsAsyncIndustries"):
            continue
        short = full.split(".")[-1]
        if short not in classes:
            fail.append("GIVER CLASS NOT FOUND: %s" % full)
print("workgiver giverClass checks done")

# 4. no AI attribution anywhere in shipped package or source
banned = ["Co-Authored-By: Claude", "Generated with [Claude", "Made with Claude",
          "noreply@anthropic.com", "Claude Code"]
scan = glob.glob(os.path.join(mod, "**", "*.*"), recursive=True) + \
       [f for f in glob.glob(os.path.join(src, "**", "*.cs"), recursive=True)
        if os.sep + "bin" + os.sep not in f and os.sep + "obj" + os.sep not in f]
hits = 0
for f in scan:
    if f.lower().endswith((".png", ".dll", ".pdb", ".wav", ".jpg")):
        continue
    try:
        t = io.open(f, encoding="utf-8-sig", errors="ignore").read()
    except Exception:
        continue
    for b in banned:
        if b in t:
            fail.append("ATTRIBUTION: %s in %s" % (b, f))
            hits += 1
print("attribution scan: %d hits" % hits)

# 5. assembly hash
dll = os.path.join(mod, "1.6", "Assemblies", "RimroomsAsyncIndustries.dll")
if not os.path.exists(dll):
    dll = glob.glob(os.path.join(mod, "**", "RimroomsAsyncIndustries.dll"), recursive=True)[0]
h = hashlib.sha256(io.open(dll, "rb").read()).hexdigest().upper()
print("assembly: %s" % dll.replace(root, "."))
print("sha256: %s" % h)

# 6. COMPLIANCE — mechanical checks behind docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md
pkg_xml = glob.glob(os.path.join(mod, "**", "*.xml"), recursive=True)
DLC_IDS = ["Ludeon.RimWorld.Royalty", "Ludeon.RimWorld.Ideology", "Ludeon.RimWorld.Biotech",
           "Ludeon.RimWorld.Anomaly", "Ludeon.RimWorld.Odyssey"]
destructive = 0
for f in pkg_xml:
    t2 = io.open(f, encoding="utf-8-sig", errors="ignore").read()
    for op in ("PatchOperationReplace", "PatchOperationRemove"):
        if op in t2:
            fail.append("COMPLIANCE destructive patch %s in %s" % (op, os.path.relpath(f, mod)))
            destructive += 1
    for m in re.finditer(r"<texPath>(.*?)</texPath>", t2):
        if "RR_" not in m.group(1):
            fail.append("COMPLIANCE non-RR texPath %s in %s" % (m.group(1), os.path.relpath(f, mod)))
    for dlc in DLC_IDS:
        for m in re.finditer(re.escape(dlc), t2):
            line_start = t2.rfind("<", 0, m.start())
            frag = t2[line_start:m.end() + 40]
            if "MayRequire" not in frag:
                fail.append("COMPLIANCE ungated DLC id %s in %s" % (dlc, os.path.relpath(f, mod)))
about = io.open(os.path.join(mod, "About", "About.xml"), encoding="utf-8-sig").read()
if "modDependencies" in about:
    fail.append("COMPLIANCE About.xml declares modDependencies")
import json as _json
_approved = _json.loads(io.open(os.path.join(root, "tools", "package-files.json"),
                                encoding="utf-8-sig").read())
if isinstance(_approved, dict):
    for _k in ("files", "approved", "packageFiles"):
        if _k in _approved:
            _approved = _approved[_k]
            break
for entry in _approved:
    pth = entry if isinstance(entry, str) else entry.get("path")
    if pth.lower().endswith((".png", ".wav", ".ogg", ".jpg")) and "RR_" not in pth and             not pth.endswith("About/Preview.png"):
        fail.append("COMPLIANCE non-original-looking asset in package: %s" % pth)
print("compliance: destructive patch ops %d, package assets and DLC gating checked" % destructive)

print("")
if fail:
    print("FAILURES: %d" % len(fail))
    for x in fail:
        print("  " + x)
    sys.exit(1)
print("ALL CHECKS PASSED")
