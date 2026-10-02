#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Measure the real size of the dependency-claim sweep.

`check-doc-conformance.py` exempts a whole document when a supersession banner sits in its
first 18 lines, so nineteen documents currently pass the dependency rule without a single
body line being corrected. This reports what each of them WOULD fail on once the banner is
retired -- the actual work, not the banner count.

Read-only. Writes nothing. Imports the checker's own constants so the two can never drift.
"""

from __future__ import print_function

import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))

import importlib.machinery
import importlib.util

loader = importlib.machinery.SourceFileLoader(
    "doc_conformance", os.path.join(REPO, "tools", "check-doc-conformance.py"))
spec = importlib.util.spec_from_loader(loader.name, loader)
conformance = importlib.util.module_from_spec(spec)
loader.exec_module(conformance)


def offending_lines(raw):
    """The checker's own walk, with the banner exemption removed and the banner itself skipped."""
    hits = []
    fenced = False
    for number, line in enumerate(raw.split("\n"), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if conformance.DEPENDENCY_SUPERSEDED.search(line):
            continue
        lowered = line.lower()
        for phrase in conformance.NO_DEPENDENCY_CLAIMS:
            if phrase not in lowered:
                continue
            if conformance.DEPENDENCY_RETIREMENT.search(line):
                continue
            hits.append((number, phrase, line.strip()))
            break
    return hits


def main():
    declared = conformance.declared_dependency_count()
    print("About.xml declares %d dependencies" % declared)
    print("")

    bannered = []
    clean = []
    total = 0

    for rel, path in conformance.living_docs():
        if rel in conformance.DEPENDENCY_LEDGER:
            continue
        raw = io.open(path, encoding="utf-8-sig").read()
        head = u"\n".join(raw.split(u"\n")[:18])
        has_banner = bool(conformance.DEPENDENCY_SUPERSEDED.search(head))
        hits = offending_lines(raw)
        if not has_banner and not hits:
            continue
        total += len(hits)
        (bannered if has_banner else clean).append((rel, hits))

    print("BANNERED -- exempt today, these lines return the moment the banner goes:")
    for rel, hits in bannered:
        print("  %-44s %d line(s)" % (rel, len(hits)))
        for number, phrase, text in hits:
            print("      %5d  %-24s %s" % (number, phrase, text[:96]))
    print("")

    if clean:
        print("NO BANNER and still failing -- these are live findings right now:")
        for rel, hits in clean:
            print("  %-44s %d line(s)" % (rel, len(hits)))
            for number, phrase, text in hits:
                print("      %5d  %-24s %s" % (number, phrase, text[:96]))
        print("")

    print("%d bannered document(s), %d unbannered, %d offending line(s) total"
          % (len(bannered), len(clean), total))


if __name__ == "__main__":
    main()
