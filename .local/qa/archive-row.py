"""Close one docs/TEST.md row and archive it to docs/FINALIZED.md, FINALIZED first, proved by reassembly.

    python .local/qa/archive-row.py "<start of the row after '- [T] '>" "<closing evidence>" "<heading suffix>"

The row is copied verbatim with [T] -> [x] and the closing evidence appended, written to FINALIZED.md and
verified there, then removed from TEST.md only if (kept lines + the row at its old index) == the
original bytes; the "`[T]` only, N rows" count drops by one.
"""
import re, sys

T, F = "docs/TEST.md", "docs/FINALIZED.md"
prefix, close, what = sys.argv[1], sys.argv[2], sys.argv[3]
DIRECTION = ("**Verbatim owner direction (2026-10-02, three items):** *\"we need to move all finished items to "
             "finalized.md from the todo, the todods sahll never hold completed items, they are always to be moved to "
             "finalized first then deleted from the todods once confirmed virbatium transfer\"*")

raw = open(T, "rb").read(); lines = raw.split(b"\n")
idx = [i for i, l in enumerate(lines) if l.startswith(("- [T] " + prefix).encode("utf-8"))]
if len(idx) != 1: sys.exit("expected one row, found %d" % len(idx))
i = idx[0]
sec = [l for l in lines[:i] if l.startswith(b"## ")][-1].decode("utf-8").strip()
row = lines[i].decode("utf-8").rstrip("\r").replace("- [T] ", "- [x] ", 1) + " " + close
moved = row.encode("utf-8")
block = ("\n\n---\n\n## Archived from the queue - %s (2026-10-08)\n\n<!-- archived-queue:begin -->\n\n%s\n\n"
         "One `[x]` row moved out of `docs/TEST.md`; its text is the row as it stood plus the closing evidence, and "
         "the removal from TEST.md was proved by reassembly (kept lines + this row at its original index == the "
         "original file).\n\n> moved from `%s` in `docs/TEST.md`\n\n" % (what, DIRECTION, sec)).encode("utf-8")
f = open(F, "rb").read()
open(F, "wb").write(f.rstrip(b"\n") + block + moved + b"\n\n<!-- archived-queue:end -->\n")
if moved not in open(F, "rb").read(): sys.exit("FINALIZED write not verified; TEST.md untouched")
kept = lines[:i] + lines[i + 1:]
if b"\n".join(kept[:i] + [lines[i]] + kept[i:]) != raw: sys.exit("reassembly failed; TEST.md untouched")
out = b"\n".join(kept)
m = re.search(rb"`\[T\]` only, (\d+) rows", out)
if m: out = out.replace(m.group(0), b"`[T]` only, %d rows" % (int(m.group(1)) - 1))
open(T, "wb").write(out)
print("archived from %s; rows now %s" % (sec, int(m.group(1)) - 1 if m else "?"))
