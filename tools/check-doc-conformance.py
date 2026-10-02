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
# The documents a player reads. **Nothing else belongs on this list.**
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

# **One exemption, and it is two words wide.** The Operations pane a player clicks is labelled
# exactly `Machine` -- `RR_OperationsExpeditions.xml` declares
# `<RR_UI_Machine>Machine</RR_UI_Machine>` -- so a page that cannot write *"the Machine pane"*
# cannot tell anybody where to click.
#
# Capital M, immediately followed by `pane`. **Nothing else.** The ban on calling a gate "the
# machine" is otherwise untouched, which matters: it caught two real violations in the wiki's own
# first draft, in the one document set whose whole job is to use the project's words.
DOC_BANNED_EXEMPT = re.compile(r"\bMachine\s+pane\b")

# A paragraph past this many characters with no break.
#
# **Lowered from 700 to 360 on 2026-10-01**, on the owner's direction: *"public facing documnets
# ARE NOT to be text walls get to each point in as short a way as possible"*.
#
# 700 was derived from the old documents' own paragraph shapes, and the owner has asked for
# shorter than those -- so the number comes down with the instruction rather than staying at a
# figure the instruction supersedes. The wiki as written tops out well below 360, which makes this
# **a floor under a standard already met**, not a target to grow into.
DOC_WALL_CHARS = 360

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

        # The pane's own name is removed BEFORE the ban scans, not excused after it. A page
        # that says both "the Machine pane" and "the machine" must still fail on the second,
        # and excusing matches one at a time would let the first hide the second.
        scanned = DOC_BANNED_EXEMPT.sub(" ", prose)
        for term, pattern in DOC_BANNED:
            match = pattern.search(scanned)
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


# Phrases that assert the package needs nothing but Core. Each was true until 2026-10-01 and
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

# A line may name the old claim while saying it is over. The retirement has to be in the SAME
# CLAUSE as the claim, not merely somewhere on the line.
#
# **Scoping this to the clause is a fix, and the defect it fixes was live.**
# `TECHNICAL_ARCHITECTURE.md` carried `Core-only solo path; optional support for all five DLC;
# other 294-profile mods optional` inside a 1,200-character paragraph that also said *"no
# compatibility announced until validation is complete"*. One incidental `until`, about an
# entirely different subject, exempted the whole paragraph -- so three false claims sat in a
# supervised document reading green.
#
# This is the inverse of the mention-versus-assertion defect this battery has caught four times.
# There, a checker FLAGGED a phrase that was only mentioned. Here, a checker EXCUSED a claim
# because a retirement word was mentioned. Same root cause: matching a line instead of the thing
# the line is doing.
DEPENDENCY_RETIREMENT = re.compile(
    r"\b(no longer|superseded|used to|previously|until|was true|retired|overruled|"
    r"changed on|changed \d{4}-\d{2}-\d{2}|historically|before)\b", re.I)

# Independent claims in these documents are separated by sentence stops and by semicolons, which
# is how the offending paragraph packed nine decisions onto one line.
CLAUSE_SPLIT = re.compile(r"[.;]")


def retirement_covers(line, phrase):
    """True when a retirement word sits in the same clause as the claim, not just on the line."""
    lowered = line.lower()
    start = 0
    while True:
        found = lowered.find(phrase, start)
        if found < 0:
            # Every occurrence on this line was covered by a retirement in its own clause.
            # Returning False here was the first draft's bug, and the planted cases caught it
            # immediately: a correctly-retired claim came back as a finding.
            return True
        # The clause is the span between the nearest delimiters either side of the match.
        left = 0
        right = len(line)
        for match in CLAUSE_SPLIT.finditer(line):
            if match.end() <= found:
                left = match.end()
            elif match.start() >= found + len(phrase):
                right = match.start()
                break
        if not DEPENDENCY_RETIREMENT.search(line[left:right]):
            # This occurrence is unretired, so the line is a finding regardless of the others.
            return False
        start = found + 1


def declared_dependency_count():
    """How many dependencies About.xml declares. Zero when it declares none."""
    about = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "About", "About.xml")
    if not os.path.isfile(about):
        return 0
    text = io.open(about, encoding="utf-8-sig").read()
    blocks = re.findall(r"<modDependencies>(.*?)</modDependencies>", text, re.S)
    return sum(block.count("<packageId>") for block in blocks)


# **The verbatim ledger is exempt, and the reason is a LAW.** These four carry the owner's own
# recorded words, and LAW #0 forbids altering them. They are records of what was said, not claims
# about what is true, and twenty-nine of the seventy-two matches live in them.
DEPENDENCY_LEDGER = {
    os.path.join("docs", "TODO.md"),
    os.path.join("docs", "NOW.md"),
    os.path.join("docs", "ROADMAP.md"),
    os.path.join("docs", "PREPRODUCTION_AND_IMPLEMENTATION_TODO.md"),
}

# A document may carry one supersession banner instead of rewriting forty-three sentences that
# were each true when written. It has to be near the top, because a supersession a reader meets
# after the prose it supersedes has not superseded anything.
DEPENDENCY_SUPERSEDED = re.compile(r"Superseded 2026-10-01 .{0,4} dependencies", re.I)


def check_dependency_claims(rel, raw, declared, problems):
    """Refuse a living document saying the package needs nothing, when it declares 294.

    **Walks the RAW text and tracks fence state itself.** The first version was handed
    `strip_code(raw)` and enumerated that while reporting numbers as if they came from the file,
    so every number after a document's first code fence was wrong. A finding with the wrong
    address is worse than no finding: somebody reads the named line, sees nothing, and concludes
    the checker is noise.
    """
    if declared <= 0:
        return
    if rel in DEPENDENCY_LEDGER:
        return
    head = u"\n".join(raw.split(u"\n")[:18])
    if DEPENDENCY_SUPERSEDED.search(head):
        return
    fenced = False
    for number, line in enumerate(raw.split("\n"), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        lowered = line.lower()
        for phrase in NO_DEPENDENCY_CLAIMS:
            if phrase not in lowered:
                continue
            if retirement_covers(line, phrase):
                continue
            problems.append("%s:%d says %r, and About.xml declares %d dependencies"
                            % (rel, number, phrase, declared))
            break


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


# Written only by the queue mover, and only around rows lifted verbatim out of a
# queue file. Explicit begin/end markers rather than "everything after a heading",
# because later session entries append below and must not fall inside a region.
ARCHIVED_QUEUE = re.compile(
    r"<!--\s*archived-queue:begin\s*-->(.*?)<!--\s*archived-queue:end\s*-->",
    re.S,
)


def archived_queue_regions(text):
    """The delimited regions holding rows moved out of a queue file."""
    return [match.group(1) for match in ARCHIVED_QUEUE.finditer(text)]


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

    SCOPED 2026-10-02, and the scoping is what keeps the rule true rather than what weakens it.

    Owner direction, verbatim: *"we need to move all finished items to finalized.md from the
    todo, the todods sahll never hold completed items, they are always to be moved to finalized
    first then deleted from the todods once confirmed virbatium transfer"*. A direction whose
    every row has closed now leaves `TODO.md` **with its rows**, archived into a delimited
    `archived-queue` region of `FINALIZED.md`. Read literally, the old rule would fail the build
    for every one of those -- it would be demanding the queue keep exactly what the owner just
    said it must not keep.

    So absence from the queue is excused by **one** thing: the direction appearing inside an
    `archived-queue` region, which is written only by the mover and only together with the
    queue rows that closed it. A direction that was acted on and never queued still appears
    only in a session write-up, outside every region, and still fails. The rule's teeth are
    where they were; what changed is that it now recognises the queue's own archive as the
    queue's history rather than as a missing entry.
    """
    archive = os.path.join(REPO, "docs", "FINALIZED.md")
    queue = os.path.join(REPO, "docs", "TODO.md")
    if not (os.path.isfile(archive) and os.path.isfile(queue)):
        return
    archive_text = io.open(archive, encoding="utf-8-sig").read()
    archived = owner_quotes(archive_text)
    queue_text = normalise(io.open(queue, encoding="utf-8-sig").read())
    moved_out = normalise("\n".join(archived_queue_regions(archive_text)))
    for quote in archived:
        if normalise(quote) in CONTINUATION_QUOTES:
            continue
        if normalise(quote) in queue_text:
            continue
        if normalise(quote) in moved_out:
            continue
        problems.append("docs/FINALIZED.md quotes an owner direction that never reached "
                        "docs/TODO.md: %r" % (quote[:90] + ("..." if len(quote) > 90 else "")))

def main():
    version = package_version()
    branch = current_branch()
    problems = []
    docs = living_docs()
    declared_dependencies = declared_dependency_count()

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

        check_dependency_claims(rel, raw, declared_dependencies, problems)

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
    print("  declared dependencies    : %d (no living document may say there are none)"
          % declared_dependencies)
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
