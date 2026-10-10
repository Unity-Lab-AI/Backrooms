# -*- coding: utf-8 -*-
"""Refuse a living document that claims the package has no dependencies.

The owner's direction on 2026-10-01 made **26 living documents lie in one commit**: *"Core only"*,
*"Core-only"*, *"no hard dependencies"*, *"needs Core only"*. Every one of those was true when it
was written and none of them is true now -- `About.xml` declares **294**.

**Hand-fixing 26 files without a rule means it rots again**, and this is the dated-count defect
this project has already met repeatedly: a claim that was true once, read as current for
thirty-six checkpoints.

So the count comes from `About.xml` itself. **When the package declares dependencies, no living
document may say it has none** -- and if the owner ever reverses the decision, the rule stops
firing on its own because it reads the file rather than a number typed here.

Dated records are untouched. `FINALIZED.md`, the implementation records and the changelog are
history, and history is allowed to say what was true at the time.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO, "tools", "check-doc-conformance.py")

ANCHOR = u'''def living_docs():'''

ADDITION = u'''# Phrases that assert the package needs nothing but Core. Each was true until 2026-10-01 and
# none is true now: `About.xml` declares 294 dependencies, five of them expansions.
#
# **The count is read from About.xml, never typed here.** If the owner reverses the decision the
# rule stops firing on its own, which is the difference between a check and a dated assertion --
# and a dated assertion read as current is this project's most repeated documentation defect.
NO_DEPENDENCY_CLAIMS = (
    "no hard dependencies",
    "no hard dependency",
    "core only",
    "core-only",
    "needs core only",
    "no dependencies",
    "without dlc",
    "zero hard dependencies",
)

# A line may name the old claim while saying it is over. The retirement has to be ON the line,
# the same shape as the retired-def rule above.
DEPENDENCY_RETIREMENT = re.compile(
    r"\\b(no longer|superseded|used to|previously|until|was true|retired|overruled|"
    r"changed on|historically|before)\\b", re.I)


def declared_dependency_count():
    """How many dependencies About.xml declares. Zero when it declares none."""
    about = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "About", "About.xml")
    if not os.path.isfile(about):
        return 0
    text = io.open(about, encoding="utf-8-sig").read()
    blocks = re.findall(r"<modDependencies>(.*?)</modDependencies>", text, re.S)
    return sum(block.count("<packageId>") for block in blocks)


def check_dependency_claims(rel, text, declared, problems):
    """Refuse a living document saying the package needs nothing, when it declares 294."""
    if declared <= 0:
        return
    for number, line in enumerate(text.split("\\n"), start=1):
        lowered = line.lower()
        for phrase in NO_DEPENDENCY_CLAIMS:
            if phrase not in lowered:
                continue
            if DEPENDENCY_RETIREMENT.search(line):
                continue
            problems.append("%s:%d says %r, and About.xml declares %d dependencies"
                            % (rel, number, phrase, declared))
            break


'''

text = io.open(CHECKER, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
text = text.replace(ANCHOR, ADDITION + ANCHOR, 1)

# Wire it into the loop, beside the other per-document rules.
LOOP_OLD = u"""        for pattern in CHECKER_PHRASES:
            found = pattern.search(text)
            if found:"""
LOOP_NEW = u"""        check_dependency_claims(rel, text, declared_dependencies, problems)

        for pattern in CHECKER_PHRASES:
            found = pattern.search(text)
            if found:"""
if text.count(LOOP_OLD) != 1:
    print("LOOP ANCHOR PROBLEM: %d" % text.count(LOOP_OLD))
    raise SystemExit(1)
text = text.replace(LOOP_OLD, LOOP_NEW, 1)

SETUP_OLD = u"""    problems = []
    docs = living_docs()"""
SETUP_NEW = u"""    problems = []
    docs = living_docs()
    declared_dependencies = declared_dependency_count()"""
if text.count(SETUP_OLD) != 1:
    print("SETUP ANCHOR PROBLEM: %d" % text.count(SETUP_OLD))
    raise SystemExit(1)
text = text.replace(SETUP_OLD, SETUP_NEW, 1)

REPORT_OLD = u'''    print("  living documents checked : %d" % len(docs))'''
REPORT_NEW = (u'''    print("  living documents checked : %d" % len(docs))\n'''
              u'''    print("  declared dependencies    : %d (no living document may say there are '''
              u'''none)"\n          % declared_dependencies)''')
if text.count(REPORT_OLD) != 1:
    print("REPORT ANCHOR PROBLEM: %d" % text.count(REPORT_OLD))
    raise SystemExit(1)
text = text.replace(REPORT_OLD, REPORT_NEW, 1)

io.open(CHECKER, "w", encoding="utf-8", newline="").write(text)

after = io.open(CHECKER, encoding="utf-8").read()
failures = []
if u"def check_dependency_claims(" not in after:
    failures.append("the rule was not defined")
if u"check_dependency_claims(rel, text, declared_dependencies, problems)" not in after:
    failures.append("THE RULE IS DEFINED AND NEVER CALLED -- the defect this project keeps meeting")
if u"def declared_dependency_count()" not in after:
    failures.append("the count is not derived from About.xml")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("rule added AND called; the count is read from About.xml")
