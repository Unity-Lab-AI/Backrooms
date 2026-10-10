# -*- coding: utf-8 -*-
"""0.12.94-dev -> 0.12.95-dev, BOM preserved by reading and writing bytes."""
import io
import os
import sys

OLD, NEW, BOM = "0.12.94-dev", "0.12.95-dev", b"\xef\xbb\xbf"
TARGETS = [os.path.join("Mod", "Rimrooms - Async Industries", "About", "About.xml"),
           os.path.join("src", "RimroomsAsyncIndustries", "RimroomsAsyncIndustries.csproj"),
           "README.md"]
total = 0
for rel in TARGETS:
    raw = io.open(rel, "rb").read()
    had = raw.startswith(BOM)
    text = (raw[len(BOM):] if had else raw).decode("utf-8")
    hits = text.count(OLD)
    if not hits:
        print("  %-66s NO OCCURRENCE -- check by hand" % rel)
        sys.exit(1)
    body = text.replace(OLD, NEW).encode("utf-8")
    io.open(rel, "wb").write((BOM + body) if had else body)
    if io.open(rel, "rb").read().startswith(BOM) != had:
        print("  BOM CHANGED for %s -- ABORT" % rel)
        sys.exit(1)
    print("  %-66s %d replacement(s), BOM %s" % (rel, hits, "kept" if had else "absent"))
    total += hits
print("")
print("%d version string(s) moved %s -> %s" % (total, OLD, NEW))
