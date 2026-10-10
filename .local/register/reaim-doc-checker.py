# -*- coding: utf-8 -*-
"""Point `check-doc-conformance.py` at the real public documents, and tighten the wall rule.

Owner direction, 2026-10-01, verbatim: *"public facing docs are concise easy to read and have no in
house dev names and no todo numbering and no actual work information"*, and *"public facing
documnets ARE NOT to be text walls get to each point in as short a way as possible"*.

## The list was wrong, and that is why nobody noticed

`READER_FACING` held thirteen entries and **several were never reader documents**:

* `HOWTO.md` opens *"This is the practical guide for anyone (human or build agent) opening this
  repository"* and carries in-house tooling names, owner-decision identifiers, the branch cascade
  and the task-record pattern. **It breaks three of the owner's four rules at once.**
* `SCENARIOS.md` announces itself as a *"design contract"* with *"tuning hypotheses"*, phase
  ordering and an acceptance checklist.
* `GAME_DESIGN.md`, `RESEARCH.md`, `TUTORIAL_SCRIPT.md`, `CONTENT_REUSE_POLICY.md` and
  `BUILDING.md` are project working material.

Holding a dev document to a reader's vocabulary made it *look* supervised while nothing was ever
going to notice it was the wrong kind of document.

## What replaces it

`docs/wiki/` — twelve pages written as a wiki and nothing else. `README.md` stays on the list,
because it is the front door.

The wall limit drops from **700** to **360** characters for these pages. 700 was derived from the
old documents' own paragraph shapes; the owner has asked for shorter than those, so the number has
to come down with the instruction. **The wiki as written tops out well under it**, so this is a
floor under a standard already met rather than a target to grow into.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO, "tools", "check-doc-conformance.py")

OLD_LIST = u'''READER_FACING = (
    "README.md",
    os.path.join("docs", "HOWTO.md"),
    # The play document, rows 1193 and 1220. It belongs here for the same reason `HOWTO.md`
    # does and for one more: it is the one document whose every sentence is an instruction to
    # a player, so a stale claim in it is a lie about what will happen rather than a lie about
    # the repository.
    os.path.join("docs", "PLAYING.md"),
    os.path.join("docs", "COMPATIBILITY.md"),
    os.path.join("docs", "MULTIPLAYER.md"),
    os.path.join("docs", "GAME_DESIGN.md"),
    os.path.join("docs", "SCENARIOS.md"),
    os.path.join("docs", "BUILDING.md"),
    os.path.join("docs", "RESEARCH.md"),
    os.path.join("docs", "CONTENT_REUSE_POLICY.md"),
    os.path.join("docs", "RIMROOMS_MOD_OVERVIEW.md"),
    os.path.join("docs", "TUTORIAL_SCRIPT.md"),
    os.path.join("docs", "CREDITS.md"),
)'''

NEW_LIST = u'''# The documents a player reads. **Nothing else belongs on this list.**
#
# Owner direction, 2026-10-01: *"public facing docs are concise easy to read and have no in house
# dev names and no todo numbering and no actual work information"*.
#
# This list used to hold `HOWTO.md`, `SCENARIOS.md`, `GAME_DESIGN.md`, `RESEARCH.md`,
# `TUTORIAL_SCRIPT.md`, `CONTENT_REUSE_POLICY.md`, `BUILDING.md` and `PLAYING.md`. **Most of
# those were never reader documents.** `HOWTO.md` opens *"the practical guide for anyone (human or
# build agent) opening this repository"*; `SCENARIOS.md` calls itself a *"design contract"* with
# *"tuning hypotheses"*. Holding a development document to a reader's vocabulary made it look
# supervised while nothing was ever going to notice it was the wrong KIND of document.
#
# They are still checked as living documents. They are no longer checked as public ones, because
# they are not public ones.
WIKI = os.path.join("docs", "wiki")
READER_FACING = (
    "README.md",
    os.path.join(WIKI, "index.md"),
    os.path.join(WIKI, "install.md"),
    os.path.join(WIKI, "first-hour.md"),
    os.path.join(WIKI, "scenarios.md"),
    os.path.join(WIKI, "gates.md"),
    os.path.join(WIKI, "backrooms.md"),
    os.path.join(WIKI, "company.md"),
    os.path.join(WIKI, "interface.md"),
    os.path.join(WIKI, "mods.md"),
    os.path.join(WIKI, "multiplayer.md"),
    os.path.join(WIKI, "troubleshooting.md"),
    os.path.join(WIKI, "links.md"),
    os.path.join(WIKI, "credits.md"),
)'''

OLD_WALL = u'''# A paragraph past this many characters with no break. Grounded in this project's own
# accepted practice rather than picked: the documents rewritten deliberately for readability
# top out at 393 and 542 characters per paragraph, so 700 is real headroom above the shape
# already agreed to be readable, and still less than half the worst offender found (1,467).
DOC_WALL_CHARS = 700'''

NEW_WALL = u'''# A paragraph past this many characters with no break.
#
# **Lowered from 700 to 360 on 2026-10-01**, on the owner's direction: *"public facing documnets
# ARE NOT to be text walls get to each point in as short a way as possible"*.
#
# 700 was derived from the old documents' own paragraph shapes, and the owner has asked for
# shorter than those -- so the number comes down with the instruction rather than staying at a
# figure the instruction supersedes. The wiki as written tops out well below 360, which makes this
# **a floor under a standard already met**, not a target to grow into.
DOC_WALL_CHARS = 360'''

text = io.open(CHECKER, encoding="utf-8").read()
problems = []
for old in (OLD_LIST, OLD_WALL):
    if text.count(old) != 1:
        problems.append("%d of %r" % (text.count(old), old[:52]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)
text = text.replace(OLD_LIST, NEW_LIST, 1).replace(OLD_WALL, NEW_WALL, 1)
io.open(CHECKER, "w", encoding="utf-8", newline="").write(text)

after = io.open(CHECKER, encoding="utf-8").read()
failures = []
if u"DOC_WALL_CHARS = 360" not in after:
    failures.append("the wall limit did not change")
if u'os.path.join(WIKI, "index.md")' not in after:
    failures.append("the wiki is not on the reader list")
if u'os.path.join("docs", "HOWTO.md")' in after:
    failures.append("HOWTO.md is still held to the reader vocabulary")
if u'os.path.join("docs", "SCENARIOS.md")' in after:
    failures.append("SCENARIOS.md is still held to the reader vocabulary")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("reader list re-aimed at docs/wiki (14 pages); wall limit 700 -> 360")
