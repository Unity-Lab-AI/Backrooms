# -*- coding: utf-8 -*-
"""Bump to 0.12.76-dev.

**The version is bumped BEFORE determinism is measured**, which `docs/NOW.md` states because it
has been got wrong: the assembly embeds its own version, so a hash taken before the bump is a
hash of a build nobody will ever ship.

The occurrence in `RR_Bonds.xml` is deliberately left alone -- it is a historical note saying what
changed *at* 0.12.75-dev, and rewriting it would make the record lie.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSPROJ = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "RimroomsAsyncIndustries.csproj")
ABOUT = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "About", "About.xml")

OLD = u"0.12.75-dev"
NEW = u"0.12.76-dev"

EDITS = [
    (CSPROJ, u"<Version>" + OLD + u"</Version>", u"<Version>" + NEW + u"</Version>"),
    (ABOUT, u"<modVersion>" + OLD + u"</modVersion>", u"<modVersion>" + NEW + u"</modVersion>"),
    (ABOUT, u"Development build " + OLD + u".", u"Development build " + NEW + u"."),
]

problems = []
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    if text.count(old) != 1:
        problems.append("%d of %r in %s" % (text.count(old), old, os.path.basename(path)))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    io.open(path, "w", encoding="utf-8-sig", newline="").write(text.replace(old, new, 1))

failures = []
csproj = io.open(CSPROJ, encoding="utf-8-sig").read()
about = io.open(ABOUT, encoding="utf-8-sig").read()
if u"<Version>" + NEW + u"</Version>" not in csproj:
    failures.append("the csproj version did not change")
if u"<modVersion>" + NEW + u"</modVersion>" not in about:
    failures.append("the mod version did not change")
if u"Development build " + NEW not in about:
    failures.append("the description still names the old build")
if OLD in csproj:
    failures.append("the csproj still mentions the old version")
if OLD in about:
    failures.append("About.xml still mentions the old version")
# The dependency blocks must have survived the bump untouched.
if about.count(u"<packageId>") < 290:
    failures.append("the dependency block lost rows: only %d packageId entries"
                    % about.count(u"<packageId>"))
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("bumped to %s; %d dependency rows intact" % (NEW, about.count(u"<packageId>") - 1))
