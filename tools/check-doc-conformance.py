"""Refuse to ship documentation that describes a mod this is not.

Why this exists
---------------
Owner direction, 2026-09-29, verbatim:

    "we need to keep using the mod register and all the prep docs while updating old
     out of date docs, readmes, how tos and other docs making sure they conform to the
     wanted stake state"

`README.md` opened with **"Current development version: 0.4.1-dev"** while the build was at
0.9.9-dev -- twenty-five checkpoints stale, on the front page. Nobody reads a README against
a csproj by hand, which is the same argument that produced every other checker here.

Living documents and dated records are different things
-------------------------------------------------------
This distinction is the whole design of the check, and getting it wrong would be worse than
having no check at all.

* A **living document** -- a readme, a contributor guide, a publishing procedure, an
  architecture map -- must describe the mod **as it is now**. A stale one actively misleads.
* A **dated record** -- an implementation record, `FINALIZED.md`, `CHANGELOG.md`, a mod
  review -- describes a moment that has passed. An implementation record that said "all four
  checkers pass" was **telling the truth** on the day it was written. Rewriting it to say
  five would be falsifying the evidence trail, and this project's whole method rests on that
  trail being trustworthy.

So dated records are **never** checked, and living documents are checked strictly.

What it checks, in living documents only
-----------------------------------------
1. **The version it claims** matches the csproj, wherever a document states one.
2. **The working branch it names** is the branch that actually exists.
3. **No retired def is described as live.** Naming one as something a player has or builds
   is a promise the package cannot keep.
4. **The checker count is right**, because documents that tell a future agent to run "all
   four checkers" will cause them to skip one.
5. **`DEFERRED.md` is not described as a live queue.** It is closed, and the standing rule
   is that nothing is ever deferred.

Usage
-----
    python tools/check-doc-conformance.py
"""

import glob
import io
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSPROJ = os.path.join(REPO, "src", "RimroomsAsyncIndustries", "RimroomsAsyncIndustries.csproj")

# Dated records. Never checked: they describe a moment that has passed, and editing them to
# match today would falsify the evidence trail this project's method depends on.
HISTORICAL_DIRS = (
    os.path.join("docs", "implementation"),
    os.path.join("docs", "research"),
    os.path.join(".claude"),
    os.path.join("outputs"),
    os.path.join(".git"),
    os.path.join(".local"),
)
HISTORICAL_FILES = (
    "CHANGELOG.md",
    os.path.join("docs", "FINALIZED.md"),
)

# Defs this package no longer ships. Naming one as something a player has or builds is a
# promise the package cannot keep.
RETIRED_DEFS = (
    "RR_MachineGate", "RR_GateConsole", "RR_EmergencyCutoff", "RR_UtilityGenerator",
    "RR_SiteFluorescent", "RR_SiteClimateUnit", "RR_FieldAnalysisBench",
    "RR_FadedInstitutionalCarpet", "RR_ReturnBeacon", "RR_MakeReturnBeacon",
)

# A phrase that will make a future agent skip a check.
CHECKER_COUNT = 6
CHECKER_PHRASES = (
    re.compile('\\b(all\\s+)?four checkers\\b', re.I),
    re.compile('\\b(all\\s+)?five checkers\\b', re.I),
)

VERSION_CLAIM = re.compile(r"(?:current\s+(?:development\s+)?version|development\s+build)\D{0,12}"
                           r"(\d+\.\d+\.\d+-dev)", re.I)

# Branch names that were genuinely the working branch once and are not now. Matching any
# "feature/..." string instead was tried first and was wrong: it flagged file paths like
# `feature/feature-review.md` and prose like "feature/adapter work". A checker that cries
# wolf is a checker people learn to scroll past, which is worse than not having it.
STALE_BRANCHES = ("feature/preproduction-handoff",)

# Vocabulary that marks a retired def as being DESCRIBED rather than promised. Naming one
# while explaining that it was retired is exactly what a ledger and a roadmap should do.
RETIREMENT_WORDS = re.compile(
    r"\b(retir|remov|delet|legacy|historical|no longer|former|obsolete|superseded|archiv|was\s+the)",
    re.I)

# Text that would tell a reader DEFERRED.md is somewhere to put open work.
DEFERRED_CLOSED_WORDS = re.compile(r"(closed|never add|nothing is deferred|zero open)", re.I)


def package_version():
    text = io.open(CSPROJ, encoding="utf-8-sig").read()
    match = re.search(r"<Version>([^<]+)</Version>", text)
    return match.group(1).strip() if match else None


def current_branch():
    try:
        out = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO)
        return out.decode("utf-8", "replace").strip()
    except Exception:
        return None


def is_historical(rel):
    if rel in HISTORICAL_FILES:
        return True
    for directory in HISTORICAL_DIRS:
        if rel == directory or rel.startswith(directory + os.sep):
            return True
    return False


def living_docs():
    found = []
    for path in glob.glob(os.path.join(REPO, "**", "*.md"), recursive=True):
        rel = os.path.relpath(path, REPO)
        if is_historical(rel):
            continue
        found.append((rel, path))
    return sorted(found)


def strip_code(text):
    """Fenced blocks are examples and transcripts, not claims the document is making."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def main():
    version = package_version()
    branch = current_branch()
    problems = []
    docs = living_docs()

    for rel, path in docs:
        raw = io.open(path, encoding="utf-8-sig").read()
        text = strip_code(raw)

        for match in VERSION_CLAIM.finditer(text):
            claimed = match.group(1)
            if version and claimed != version:
                problems.append("%s claims version %s; the build is %s" % (rel, claimed, version))

        for name in STALE_BRANCHES:
            if name in text and branch and name != branch:
                problems.append("%s names working branch %r; the branch is %r" % (rel, name, branch))

        # A retired def may be named while explaining that it is retired. It may not be named
        # on a line that reads as a promise, so the line itself has to carry the explanation.
        for number, line in enumerate(text.split("\n"), start=1):
            for definition in RETIRED_DEFS:
                if definition in line and not RETIREMENT_WORDS.search(line):
                    problems.append("%s:%d names retired def %s with nothing saying it is gone"
                                    % (rel, number, definition))

        for pattern in CHECKER_PHRASES:
            found = pattern.search(text)
            if found:
                problems.append("%s says %r; there are %d, and a reader following that will skip one"
                                % (rel, found.group(0), CHECKER_COUNT))
                break

        # Mentioning the file is fine; mentioning it without anywhere saying it is closed is
        # what leaves a reader thinking there is still somewhere to put work.
        if "DEFERRED.md" in text and not DEFERRED_CLOSED_WORDS.search(text):
            problems.append("%s mentions DEFERRED.md without saying anywhere that it is closed"
                            % rel)

    print("doc-conformance")
    print("  living documents checked : %d" % len(docs))
    print("  dated records skipped    : implementation records, FINALIZED, CHANGELOG, reviews")
    print("  build version            : %s" % version)
    print("  working branch           : %s" % branch)
    print("")

    if problems:
        print("FAIL: %d problem(s)" % len(problems))
        for problem in sorted(set(problems)):
            print("  - %s" % problem)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
