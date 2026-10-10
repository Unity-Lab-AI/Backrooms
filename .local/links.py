import io, os, re, glob, sys
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

root = r"C:\Users\gfour\Desktop\Backrooms"
broken = []
total = 0
for f in glob.glob(os.path.join(root, "**", "*.md"), recursive=True):
    if os.sep + ".git" + os.sep in f or os.sep + ".local" + os.sep in f:
        continue
    t = io.open(f, encoding="utf-8", errors="ignore").read()
    base = os.path.dirname(f)
    for m in re.finditer(r"\]\(([^)]+)\)", t):
        target = m.group(1).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1].strip()
        target = unquote(target)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#")[0].strip()
        if not target:
            continue
        total += 1
        p = os.path.normpath(os.path.join(base, target.replace("/", os.sep)))
        if not os.path.exists(p):
            broken.append("%s -> %s" % (os.path.relpath(f, root), target))
print("relative markdown links checked: %d" % total)
if broken:
    print("BROKEN: %d" % len(broken))
    for b in broken:
        print("  " + b)
    sys.exit(1)
print("zero broken")
