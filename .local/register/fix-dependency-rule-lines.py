# -*- coding: utf-8 -*-
"""The dependency rule reported wrong line numbers. Fix the rule before trusting its output.

It was handed `strip_code(raw)` -- fenced blocks removed -- and then enumerated THAT while
reporting the numbers as if they came from the file. Every number after the first code fence in a
document was wrong, which is why the first run pointed at a bare ``` in `ARCHITECTURE.md` and a
blank line in `SKILL_TREE.md`.

**A finding with the wrong address is worse than no finding**: somebody reads the named line, sees
nothing wrong, and concludes the checker is noise.

The fix walks the **raw** text and tracks fence state itself, so a number is a real number and a
fenced example is still not a claim.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKER = os.path.join(REPO, "tools", "check-doc-conformance.py")

OLD = u'''def check_dependency_claims(rel, text, declared, problems):
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
            break'''

NEW = u'''def check_dependency_claims(rel, raw, declared, problems):
    """Refuse a living document saying the package needs nothing, when it declares 294.

    **Walks the RAW text and tracks fence state itself.** The first version was handed
    `strip_code(raw)` and enumerated that while reporting numbers as if they came from the file,
    so every number after a document's first code fence was wrong. A finding with the wrong
    address is worse than no finding: somebody reads the named line, sees nothing, and concludes
    the checker is noise.
    """
    if declared <= 0:
        return
    fenced = False
    for number, line in enumerate(raw.split("\\n"), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        lowered = line.lower()
        for phrase in NO_DEPENDENCY_CLAIMS:
            if phrase not in lowered:
                continue
            if DEPENDENCY_RETIREMENT.search(line):
                continue
            problems.append("%s:%d says %r, and About.xml declares %d dependencies"
                            % (rel, number, phrase, declared))
            break'''

text = io.open(CHECKER, encoding="utf-8").read()
if text.count(OLD) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(OLD))
    raise SystemExit(1)
text = text.replace(OLD, NEW, 1)

# And it must be given the raw text, not the stripped text.
CALL_OLD = u"        check_dependency_claims(rel, text, declared_dependencies, problems)"
CALL_NEW = u"        check_dependency_claims(rel, raw, declared_dependencies, problems)"
if text.count(CALL_OLD) != 1:
    print("CALL ANCHOR PROBLEM: %d" % text.count(CALL_OLD))
    raise SystemExit(1)
text = text.replace(CALL_OLD, CALL_NEW, 1)
io.open(CHECKER, "w", encoding="utf-8", newline="").write(text)

after = io.open(CHECKER, encoding="utf-8").read()
failures = []
if u"check_dependency_claims(rel, raw, declared_dependencies, problems)" not in after:
    failures.append("the rule is still given the stripped text")
if u"fenced = not fenced" not in after:
    failures.append("fence tracking was not added")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("line numbers now come from the file; fenced examples still are not claims")
