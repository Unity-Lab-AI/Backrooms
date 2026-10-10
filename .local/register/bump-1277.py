# -*- coding: utf-8 -*-
"""Bump to 0.12.77-dev and point the in-game description at the wiki.

The version is bumped **before** determinism is measured, because the assembly embeds it.

And the bump is earned rather than ceremonial: `About.xml`'s description is player-facing text and
it now names the wiki, so somebody reading the mod page in game has somewhere to go. That is a
real package change.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSPROJ = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "RimroomsAsyncIndustries.csproj")
ABOUT = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "About", "About.xml")
README = os.path.join(REPO, "README.md")

OLD = u"0.12.76-dev"
NEW = u"0.12.77-dev"

DESC_ANCHOR = u"Original Backrooms menu backgrounds show the mod title and loaded version beside the native version information."
DESC_NEW = (u"--- THE WIKI ---\n\n"
            u"How to install it, how to set up your mod manager, how to play, what is through the "
            u"gate, and what to do when something refuses: "
            u"https://github.com/Unity-Lab-AI/Backrooms\n\n"
            u"Original Backrooms menu backgrounds show the mod title and loaded version beside "
            u"the native version information.")

EDITS = [
    (CSPROJ, u"<Version>" + OLD + u"</Version>", u"<Version>" + NEW + u"</Version>"),
    (ABOUT, u"<modVersion>" + OLD + u"</modVersion>", u"<modVersion>" + NEW + u"</modVersion>"),
    (ABOUT, u"Development build " + OLD + u".", u"Development build " + NEW + u"."),
    (ABOUT, DESC_ANCHOR, DESC_NEW),
    (README, u"**Current development version: " + OLD + u".**",
     u"**Current development version: " + NEW + u".**"),
]

problems = []
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    if text.count(old) != 1:
        problems.append("%d of %r in %s" % (text.count(old), old[:46], os.path.basename(path)))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
for path, old, new in EDITS:
    text = io.open(path, encoding="utf-8-sig").read()
    io.open(path, "w", encoding="utf-8-sig", newline="").write(text.replace(old, new, 1))

about = io.open(ABOUT, encoding="utf-8-sig").read()
csproj = io.open(CSPROJ, encoding="utf-8-sig").read()
readme = io.open(README, encoding="utf-8").read()

failures = []
if OLD in about or OLD in csproj or OLD in readme:
    failures.append("something still names the old version")
if u"--- THE WIKI ---" not in about:
    failures.append("the description does not name the wiki")
if about.count(u"<packageId>") < 290:
    failures.append("the dependency block lost rows: %d" % about.count(u"<packageId>"))
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("bumped to %s; description names the wiki; %d dependency rows intact"
      % (NEW, about.count(u"<packageId>") - 1))
