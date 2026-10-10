#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compare what About.xml declares against the owner's live ModsConfig, read-only.

Answers three questions with numbers rather than impressions:
  1. what we declare that is no longer active on the machine
  2. what is active on the machine that we do not declare
  3. whether anything QA-only is declared as a player dependency

Reads ModsConfig.xml. Never writes it, never touches the active list.
"""

from __future__ import print_function

import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
ABOUT = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "About", "About.xml")
CONFIG = os.path.join(
    os.environ.get("USERPROFILE", os.path.expanduser("~")),
    "AppData", "LocalLow", "Ludeon Studios",
    "RimWorld by Ludeon Studios", "Config", "ModsConfig.xml")

# Tooling that must never be declared as a player dependency. The bridge is attach-only QA
# tooling by the standing constraint in AGENTS.md; a player told they need a debug server has
# been told something false.
QA_ONLY = {"brrainz.rimbridgeserver"}

OURS = "rimrooms.asyncindustries"
CORE = "ludeon.rimworld"


def declared():
    text = io.open(ABOUT, encoding="utf-8-sig").read()
    blocks = re.findall(r"<modDependencies>(.*?)</modDependencies>", text, re.S)
    ids = []
    for block in blocks:
        ids.extend(re.findall(r"<packageId>([^<]+)</packageId>", block))
    load_after = re.findall(r"<loadAfter>(.*?)</loadAfter>", text, re.S)
    after = []
    for block in load_after:
        after.extend(re.findall(r"<li>([^<]+)</li>", block))
    return [i.strip().lower() for i in ids], [a.strip().lower() for a in after]


def active():
    if not os.path.isfile(CONFIG):
        return None
    text = io.open(CONFIG, encoding="utf-8-sig").read()
    return [m.strip().lower() for m in re.findall(r"<li>([^<]+)</li>", text)]


def main():
    deps, after = declared()
    live = active()

    print("declared modDependencies : %d" % len(deps))
    print("declared loadAfter       : %d" % len(after))
    if live is None:
        print("ModsConfig.xml not readable at %s" % CONFIG)
        return 1
    print("live active entries      : %d" % len(live))
    print("")

    live_set = set(live)
    dep_set = set(deps)

    stale = sorted(dep_set - live_set)
    missing = sorted(live_set - dep_set - {OURS, CORE})

    print("DECLARED BUT NO LONGER ACTIVE -- %d" % len(stale))
    for item in stale:
        print("    %s" % item)
    print("")

    print("ACTIVE BUT NOT DECLARED -- %d (Core and our own id excluded)" % len(missing))
    for item in missing:
        print("    %s" % item)
    print("")

    bad = sorted(dep_set & QA_ONLY)
    print("QA-ONLY TOOLING DECLARED AS A PLAYER DEPENDENCY -- %d" % len(bad))
    for item in bad:
        in_after = " (and in loadAfter)" if item in set(after) else ""
        print("    %s%s" % (item, in_after))
    if not bad:
        print("    none")
    print("")

    for item in (OURS, CORE):
        if item in dep_set:
            print("REFUSED CASE PRESENT: %s is declared as its own dependency" % item)

    return 0


if __name__ == "__main__":
    sys.exit(main())
