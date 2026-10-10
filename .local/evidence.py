import io, os, json, glob, hashlib, subprocess

root = r"C:\Users\gfour\Desktop\Backrooms"
mod = os.path.join(root, "Mod", "Rimrooms - Async Industries")
src = os.path.join(root, "src", "RimroomsAsyncIndustries")
out = os.path.join(root, "docs", "implementation", "evidence", "gate-servicing-2026-09-29")
ver = "0.7.1-dev"
os.makedirs(out, exist_ok=True)


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest().upper()


dll = os.path.join(mod, "1.6", "Assemblies", "RimroomsAsyncIndustries.dll")
asm = sha(dll)

# ---- source manifest
sources = []
for f in sorted(glob.glob(os.path.join(src, "**", "*.cs"), recursive=True)):
    if os.sep + "bin" + os.sep in f or os.sep + "obj" + os.sep in f:
        continue
    rel = os.path.relpath(f, root).replace("\\", "/")
    sources.append({"path": rel, "bytes": os.path.getsize(f), "sha256": sha(f)})
io.open(os.path.join(out, "source-manifest.json"), "w", encoding="utf-8").write(json.dumps({
    "note": "Compiled C# source inputs for %s. Compilation establishes API consistency only; "
            "no game, test or runtime compatibility result is claimed." % ver,
    "modVersion": ver,
    "sourceFileCount": len(sources),
    "assemblySha256": asm,
    "sources": sources,
}, indent=2))

# ---- package manifest from the approved allowlist
approved = json.loads(io.open(os.path.join(root, "tools", "package-files.json"),
                              encoding="utf-8-sig").read())
if isinstance(approved, dict):
    for k in ("files", "approved", "packageFiles"):
        if k in approved:
            approved = approved[k]
            break
files, missing = [], []
for entry in approved:
    rel = entry if isinstance(entry, str) else entry.get("path")
    p = os.path.join(mod, rel.replace("/", os.sep))
    if not os.path.exists(p):
        missing.append(rel)
        continue
    files.append({"path": rel, "bytes": os.path.getsize(p), "sha256": sha(p)})
io.open(os.path.join(out, "package-manifest.json"), "w", encoding="utf-8").write(json.dumps({
    "note": "Approved game-loadable package files for %s." % ver,
    "modVersion": ver,
    "packageFileCount": len(files),
    "missingFromDisk": missing,
    "files": files,
}, indent=2))

# ---- reference manifest, RECOMPUTED (never copied forward)
prev = json.loads(io.open(os.path.join(
    root, "docs", "implementation", "evidence", "world-frontiers-2026-09-29",
    "reference-manifest.json"), encoding="utf-8-sig").read())
managed = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed"
refs, changed = [], []
for r in prev["References"]:
    p = os.path.join(managed, r["Name"])
    if not os.path.exists(p):
        changed.append(r["Name"] + " (absent from disk)")
        continue
    h = sha(p)
    refs.append({"Name": r["Name"], "AssemblyVersion": r["AssemblyVersion"], "SHA256": h})
    if h != r["SHA256"]:
        changed.append(r["Name"])
io.open(os.path.join(out, "reference-manifest.json"), "w", encoding="utf-8").write(json.dumps({
    "SDK": prev["SDK"],
    "Configuration": "Release",
    "TargetFramework": "net472",
    "note": "Reference assembly hashes recomputed for this build rather than copied forward.",
    "changedSincePreviousCheckpoint": changed,
    "References": refs,
}, indent=2))

print("source files: %d" % len(sources))
print("package files: %d  missing: %d" % (len(files), len(missing)))
print("references recomputed: %d  changed: %s" % (len(refs), changed or "none"))
print("assembly sha256: %s" % asm)
