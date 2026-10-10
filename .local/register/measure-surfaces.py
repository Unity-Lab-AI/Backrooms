# -*- coding: utf-8 -*-
"""Measure our displayed strings against RimWorld's own practice, per display surface.

Scratch measurement. The shipped rule lives in tools/check-display-style.py.
"""
import io
import os
import re
import glob
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD = os.path.join(REPO, "Mod", "Rimrooms - Async Industries")
SRC = os.path.join(REPO, "src")

PATTERNS = [
    ("message",       re.compile(r'Messages\.Message\(\s*\(?"(RR_[A-Za-z0-9_]+)"')),
    ("message",       re.compile(r'Messages\.Message\(\s*\(\s*[A-Za-z_.]+\s*\?\?\s*"(RR_[A-Za-z0-9_]+)"')),
    ("letter-label",  re.compile(r'ReceiveLetter\(\s*"(RR_[A-Za-z0-9_]+)"')),
    ("letter-body",   re.compile(r'ReceiveLetter\(\s*"RR_[A-Za-z0-9_]+"\.Translate\([^;]*?\)\s*,\s*"(RR_[A-Za-z0-9_]+)"')),
    ("gizmo-label",   re.compile(r'defaultLabel\s*=\s*"(RR_[A-Za-z0-9_]+)"')),
    ("gizmo-desc",    re.compile(r'defaultDesc\s*=\s*"(RR_[A-Za-z0-9_]+)"')),
    ("float-menu",    re.compile(r'new FloatMenuOption\(\s*"(RR_[A-Za-z0-9_]+)"')),
]


def keyed():
    found = {}
    for path in glob.glob(os.path.join(MOD, "*", "Languages", "English", "Keyed", "*.xml")):
        for node in ET.parse(path).getroot():
            if isinstance(node.tag, str) and node.text is not None:
                found[node.tag] = (node.text, os.path.basename(path))
    return found


def classify():
    surfaces = {}
    for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
        text = io.open(path, encoding="utf-8-sig").read()
        for surface, pattern in PATTERNS:
            for match in pattern.finditer(text):
                surfaces.setdefault(match.group(1), set()).add(surface)
    return surfaces


CORE = {
    # surface: (n, median, p90, max, ends-punct %, starts-cap %)
    "message":      (363, 42, 88, 156, 85, 49),
    "letter-label": (74, 15, 24, 45, 2, 79),
    "letter-body":  (166, 72, 216, 385, 70, 62),
    "float-menu":   (290, 19, 38, 76, 7, 61),
    "gizmo-label":  (301, 24, 92, 204, 54, 97),
}


def main():
    strings = keyed()
    surfaces = classify()
    buckets = {}
    for key, kinds in sorted(surfaces.items()):
        if key not in strings:
            continue
        for kind in kinds:
            buckets.setdefault(kind, []).append((key, strings[key][0], strings[key][1]))

    print("keys in Keyed/ : %d" % len(strings))
    print("keys classified by call site : %d" % len(surfaces))
    print("")
    for kind in sorted(buckets):
        rows = buckets[kind]
        lengths = sorted(len(" ".join(t.split())) for _, t, _ in rows)
        endp = sum(1 for _, t, _ in rows if t.strip().endswith((".", "!", "?")))
        cap = sum(1 for _, t, _ in rows if t.strip()[:1].isupper())
        core = CORE.get(kind)
        print("%-14s n=%-4d median=%-4d p90=%-4d max=%-4d endsPunct=%3d%% startsCap=%3d%%%s" % (
            kind, len(rows), lengths[len(lengths) // 2], lengths[int(len(lengths) * .9)],
            lengths[-1], 100 * endp // len(rows), 100 * cap // len(rows),
            ("   CORE: median=%d p90=%d max=%d endsPunct=%d%%" % (core[1], core[2], core[3], core[4])) if core else ""))
        if core:
            over = [(len(" ".join(t.split())), k, t) for k, t, _ in rows
                    if len(" ".join(t.split())) > core[3]]
            for length, k, t in sorted(over, reverse=True):
                print("      LONGER THAN ANY CORE %s: %s (%d > %d) %r" % (kind, k, length, core[3], " ".join(t.split())[:70]))
            if kind in ("float-menu", "letter-label"):
                for k, t, _ in rows:
                    if t.strip().endswith("."):
                        print("      TRAILING PERIOD (Core: %d%%): %s %r" % (core[4], k, t[:60]))
    print("")
    unclassified = [k for k in strings if k not in surfaces]
    print("keys not reached by any call-site pattern : %d" % len(unclassified))


main()
