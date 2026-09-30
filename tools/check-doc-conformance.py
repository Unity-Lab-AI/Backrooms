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
6. **Every owner direction quoted in `FINALIZED.md` also appears in `TODO.md`.** LAW #0 says
   the owner's exact words go into the queue. An audit on 2026-09-29 found three of seventeen
   directions that had been acted on and archived without ever being written into the queue as
   tasks. Each was implemented correctly, so nothing was lost -- but the queue was not the
   record of what had been asked for, which is the one job it has. A direction in the
   permanent archive is by definition something that shipped; if it never appeared in the
   queue, it skipped the queue.

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
CHECKER_COUNT = 8
CHECKER_PHRASES = (
    re.compile('\\b(all\\s+)?four checkers\\b', re.I),
    re.compile('\\b(all\\s+)?five checkers\\b', re.I),
    re.compile('\\b(all\\s+)?six checkers\\b', re.I),
    re.compile('\\b(all\\s+)?seven checkers\\b', re.I),
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


# --------------------------------------------------------------------------- #
# The reader-facing set
# --------------------------------------------------------------------------- #
#
# Owner direction, 2026-09-29, verbatim: *"lets make sure the docs and informations displays
# in game are proper to backrrooms universe and rimworld gameplay style"*, and earlier
# *"cleaning up text walls for everything making them a pleasure to read"*.
#
# 0.10.2-dev unified the vocabulary in everything the **game** displays, and 0.10.4-dev added
# the wall rule over the same text. Neither reached the documents, and a sweep found the
# retired word in prose **262 times across 30 living documents**.
#
# Only these are held to the two rules below, and the boundary is a real distinction rather
# than a convenience:
#
# * These describe **the mod to a person**. A reader meets the mod here, so the mod's own
#   words are the only ones that can be right.
# * An internal design or architecture document describes **the code to whoever works on it
#   next**, and the code's own identifiers are `Portals/`, `PortalCrossingService`,
#   `RR_PortalCrossing_*`. Invariant: key names are exempt from the vocabulary. Rewriting the
#   prose around those identifiers would make the documents disagree with the source, which is
#   a worse failure than an old word.
#
# The remainder is counted in `TODO.md` with its number rather than left to be rediscovered.
READER_FACING = (
    "README.md",
    os.path.join("docs", "HOWTO.md"),
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
)

# The same words `check-info-cards.py` bans from anything the game displays, for the same
# reason: one set of words, or the mod cannot say which part failed.
DOC_BANNED_TERMS = {
    "portal": "the machine is a 'gate'; the link it holds open is a 'connection'",
    "doorway": "a plain door is a 'door'; the far-side arrival point is a 'threshold'",
    "the machine": "the gate is a 'gate'",
    "gizmo": "'gizmo' is RimWorld's word for a button, never a name for our gate",
}
DOC_BANNED = [(term, re.compile(r"\b" + term.replace(" ", r"\s+") + r"s?\b", re.I))
              for term in DOC_BANNED_TERMS]

# A paragraph past this many characters with no break. Grounded in this project's own
# accepted practice rather than picked: the documents rewritten deliberately for readability
# top out at 393 and 542 characters per paragraph, so 700 is real headroom above the shape
# already agreed to be readable, and still less than half the worst offender found (1,467).
DOC_WALL_CHARS = 700

FENCED = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`]*`")
MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
OWNER_INLINE_QUOTE = re.compile(r'\*"[^"]*"\*')
# Any double-quoted span, not only the owner's. A quoted phrase belongs to whoever is being
# quoted, and this project cites external sources -- the A24 synopsis calls what appears in
# the basement a "doorway". Rewriting that word would not be tidying our vocabulary, it would
# be misquoting a source. Words we are quoting are never ours to change.
QUOTED_SPAN = re.compile(r'"[^"\n]{0,200}"')
LIST_OR_TABLE = re.compile(r"^\s*(?:[|#>*+-]|\d+\.)")


def readable_prose(raw):
    """A document's prose, with everything that is not prose removed.

    Code spans, fenced blocks, link targets and verbatim owner quotations are all excluded.
    The owner's words are never rewritten -- LAW #0 -- so flagging a word inside one would be
    reporting a fault that must not be fixed, which is the definition of crying wolf. Link
    text is kept and the target dropped, because a reader reads the text and a file called
    `CONNECTED_COLONY_PORTALS.md` is a filename rather than a sentence.
    """
    text = FENCED.sub(" ", raw)
    text = MARKDOWN_LINK.sub(r"\1", text)
    text = INLINE_CODE.sub(" ", text)
    text = OWNER_INLINE_QUOTE.sub(" ", text)
    return QUOTED_SPAN.sub(" ", text)


def paragraphs(text):
    """Rendered paragraphs, not source lines.

    Measuring source lines is wrong in both directions: a hard-wrapped document hides a long
    paragraph behind short lines, and a document with one line per paragraph reports the
    paragraph. Headings, list items, blockquotes and tables are not prose and are skipped.
    """
    found = []
    for block in re.split(r"\n\s*\n", text):
        lines = [line for line in block.split("\n") if line.strip()]
        if not lines or any(LIST_OR_TABLE.match(line) for line in lines):
            continue
        found.append(" ".join(" ".join(lines).split()))
    return found


# Row 791, verbatim: "No statement may describe live shared-colony control or synchronized
# research unless implemented and demonstrated." Nothing has been demonstrated, because no game
# has ever been launched from this repository, so no reader-facing document may assert any of
# these.
#
# The rule is about **asserting**, not mentioning. `docs/MULTIPLAYER.md` exists to deny every
# one of these in so many words, and a naive substring ban would fail the one document written to
# obey it -- the same trap `disposition_stance()` fell into by testing `"required" in text` and
# calling "not required" a requirement. So each occurrence is checked for a negator in its own
# sentence, and only an un-negated one is a claim.
FORBIDDEN_CLAIMS = (
    "shared colony",
    "shared map",
    "shared research",
    "synchronised research",
    "synchronized research",
    "shared colony control",
    "same colony together",
)

# Maintained, not complete, and the comment says so on purpose. The first version of this list
# held only the obvious negators and immediately flagged a real denial in `docs/SCENARIOS.md`:
# *"shared research ... stay **unpromised** until the exact RWT profile passes the
# disposable-server test"*. That is exactly the sentence this rule wants documents to contain.
#
# A phrase list cannot anticipate every way English denies something -- the same limitation that
# made `disposition_stance()` wrong -- so the failure mode was chosen deliberately: a missing
# negator produces a **false positive that blocks a build**, which is loud and gets fixed, rather
# than a false negative that lets a claim ship, which is silent. Add to this list when a genuine
# denial is flagged; never widen a forbidden phrase to make a failure go away.
CLAIM_NEGATORS = ("no ", "not ", "never ", "without ", "cannot ", "neither ", "nor ",
                  "there is no", "does not", "do not", "is not", "are not", "none",
                  "unpromised", "unproven", "untested", "unverified", "unsupported",
                  "instead of", "rather than")


def sentences(prose):
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n", prose) if part.strip()]


def check_forbidden_claims(rel, prose, problems):
    """Refuse an un-negated claim of live shared-colony control or synchronised research."""
    for sentence in sentences(prose):
        lowered = sentence.lower()
        for phrase in FORBIDDEN_CLAIMS:
            if phrase not in lowered:
                continue
            if any(negator in lowered for negator in CLAIM_NEGATORS):
                continue
            problems.append("%s claims %r without denying it -- row 791: no statement may "
                            "describe live shared-colony control or synchronised research "
                            "unless implemented and demonstrated, and nothing has been "
                            "demonstrated (%r)" % (rel, phrase, sentence[:90]))


def check_reader_facing(problems):
    for rel in READER_FACING:
        path = os.path.join(REPO, rel)
        if not os.path.isfile(path):
            problems.append("%s is named as reader-facing and does not exist" % rel)
            continue
        prose = readable_prose(io.open(path, encoding="utf-8-sig").read())

        for term, pattern in DOC_BANNED:
            match = pattern.search(prose)
            if match:
                problems.append("%s says %r to a reader -- %s"
                                % (rel, match.group(0), DOC_BANNED_TERMS[term]))

        check_forbidden_claims(rel, prose, problems)

        for paragraph in paragraphs(prose):
            if len(paragraph) > DOC_WALL_CHARS:
                problems.append("%s has a %d-character paragraph with no break; a reader meets "
                                "it as a wall (%r)" % (rel, len(paragraph), paragraph[:60]))


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




# Owner instructions that mean "keep working" and name nothing to build. They are real words
# and they are archived, but a queue entry for them would say nothing a reader could act on.
# Listed explicitly rather than matched by pattern: an over-eager pattern would swallow a
# direction that carries real content alongside a "get to it", which has happened repeatedly.
CONTINUATION_QUOTES = {
    "continue towards getting to the goal: a 100",
    "cool lets get to it remeber the goal: completing the aaa mod rimrooms - async industries",
    "get to it all we are finishing everything",
    "get to the work we are doing everything to get this mod 100% and outstanding awesomeness",
    "lets get to them all so we can finish everything without shortcuts and no loose ends",
    "i said questionable ethics, its a mod",
}

# An owner direction as the ledgers quote one: a blockquote holding an italicised quotation.
OWNER_QUOTE = re.compile('^>\\s*\\*"(.+?)"\\*\\s*$', re.M)

# Quotations short enough to be a fragment of a longer one, or a stock phrase, are skipped:
# matching them proves nothing either way.
MIN_QUOTE_CHARS = 25


def normalise(text):
    """Compare on words, not on markup.

    A direction can be quoted in one ledger with escaped quotation marks and in another
    without, or wrapped differently. Those are the same words and must not read as a missing
    direction -- a check that fires on markup is a check people stop believing.
    """
    lowered = text.replace("\\", "").replace("\u201c", '"').replace("\u201d", '"')
    return " ".join(lowered.split()).lower()


def owner_quotes(text):
    """Every verbatim owner direction a document quotes."""
    found = []
    for match in OWNER_QUOTE.finditer(text):
        quote = " ".join(match.group(1).split())
        if len(quote) >= MIN_QUOTE_CHARS:
            found.append(quote)
    return found


def check_directions_reached_the_queue(problems):
    """LAW #0, made checkable.

    Owner direction, 2026-09-29, verbatim: *"it seems like sometimes i dont see you record
    the verbatiums and then build them into tasks of the todo prperly"*.

    The owner was right. An audit found **three of seventeen** directions that had been acted
    on and archived in `FINALIZED.md` without ever being written into `TODO.md` as tasks. Each
    was implemented correctly, so nothing was lost -- but the queue was not the record of what
    had been asked for, which is the one job it has.

    A direction quoted in the permanent archive is by definition something that shipped. If it
    never appeared in the working queue, it skipped the queue entirely. That is now a failure.
    """
    archive = os.path.join(REPO, "docs", "FINALIZED.md")
    queue = os.path.join(REPO, "docs", "TODO.md")
    if not (os.path.isfile(archive) and os.path.isfile(queue)):
        return
    archived = owner_quotes(io.open(archive, encoding="utf-8-sig").read())
    queue_text = normalise(io.open(queue, encoding="utf-8-sig").read())
    for quote in archived:
        if normalise(quote) in CONTINUATION_QUOTES:
            continue
        if normalise(quote) not in queue_text:
            problems.append("docs/FINALIZED.md quotes an owner direction that never reached "
                            "docs/TODO.md: %r" % (quote[:90] + ("..." if len(quote) > 90 else "")))

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

    check_directions_reached_the_queue(problems)
    check_reader_facing(problems)

    print("doc-conformance")
    print("  living documents checked : %d" % len(docs))
    print("  reader-facing documents  : %d, held to the vocabulary and the wall rule"
          % len(READER_FACING))
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
