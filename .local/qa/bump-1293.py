# -*- coding: utf-8 -*-
"""Bump 0.12.92-dev -> 0.12.94-dev, preserving each file's existing BOM exactly.

**Writing a file with the wrong encoding silently changes it.** Two batches ago the bump stripped
three BOMs and the changelog script added one. So every file is read as bytes, its BOM recorded,
and the same BOM written back -- never assumed either way. `git diff --stat` afterwards is the
check that matters: the line counts do not lie.
"""
import io
import os
import sys

OLD = "0.12.92-dev"
NEW = "0.12.94-dev"
BOM = b"\xef\xbb\xbf"

TARGETS = [
    os.path.join("Mod", "Rimrooms - Async Industries", "About", "About.xml"),
    os.path.join("src", "RimroomsAsyncIndustries", "RimroomsAsyncIndustries.csproj"),
    "README.md",
]

total = 0
for rel in TARGETS:
    if not os.path.isfile(rel):
        print("MISSING %s" % rel)
        sys.exit(1)
    raw = io.open(rel, "rb").read()
    had_bom = raw.startswith(BOM)
    text = raw[len(BOM):].decode("utf-8") if had_bom else raw.decode("utf-8")
    hits = text.count(OLD)
    if hits == 0:
        print("  %-70s no occurrence of %s" % (rel, OLD))
        continue
    text = text.replace(OLD, NEW)
    body = text.encode("utf-8")
    io.open(rel, "wb").write((BOM + body) if had_bom else body)
    back = io.open(rel, "rb").read()
    if back.startswith(BOM) != had_bom:
        print("  %-70s BOM CHANGED -- ABORT" % rel)
        sys.exit(1)
    print("  %-70s %d replacement(s), BOM %s" % (rel, hits, "kept" if had_bom else "absent"))
    total += hits

print("")
print("%d version string(s) moved %s -> %s" % (total, OLD, NEW))
