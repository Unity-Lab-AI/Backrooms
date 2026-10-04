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

NEWLINE = chr(10)
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
#
# **COUNTED OFF THE DIRECTORY, NEVER TYPED.** This read `CHECKER_COUNT = 8` with a phrase list
# that stopped at *"seven checkers"*, while nineteen checkers shipped. So the one number the rule
# exists to protect was eleven out of date, and every document saying *"all eight checkers"* --
# the first wrong phrase a reader would write at the time -- passed unexamined.
#
# It is the same defect this file already names in its own dependency rule: *"The count is read
# from About.xml, never typed here"*. A checker that hard-codes a number it is checking is a dated
# assertion wearing a check's clothes, and a dated assertion read as current is this project's most
# repeated documentation defect.
WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "twenty-one": 21, "twenty-two": 22, "twenty-three": 23, "twenty-four": 24,
}

# Any count of checkers, spelled or in digits. A correct count passes; a wrong one fails whatever
# the number is, which is what the fixed phrase list could not do.
#
# **`other` IS CAPTURED BECAUSE IT CHANGES THE ARITHMETIC, NOT TO BE LENIENT.** *"it runs in the
# standard sweep with the other twelve checkers"* is a sentence about thirteen checkers, and a rule
# that read it as twelve would be demanding the author write a number that is wrong in order to
# pass. This file's own branch rule states the cost of that: *"A checker that cries wolf is a
# checker people learn to scroll past, which is worse than not having it."*
CHECKER_CLAIM = re.compile(
    r"\b(?:all\s+)?(?:(other)\s+)?(\d{1,3}|" +
    "|".join(sorted(WORD_NUMBERS, key=len, reverse=True)) +
    r")\s+checkers\b", re.I)


def say(line):
    """Print a line that may hold characters the console cannot encode.

    **A CHECKER THAT CRASHES WHILE REPORTING CANNOT REPORT.** The Pages rule quotes the offending
    sentence, and one of those sentences contained an arrow; on a cp1252 console `print` raised
    `UnicodeEncodeError` and the run died **after** finding six real problems and before naming
    five of them. The findings were correct and invisible, which is the worst possible outcome for
    an instrument.

    Replaced rather than dropped, so the reader still sees where the character was.
    """
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"))


def checker_count():
    """How many checkers there are, read off `tools/`."""
    return len(glob.glob(os.path.join(REPO, "tools", "check-*.py")))


def check_checker_count(rel, text, count, problems):
    """Refuse a document that tells a reader to run the wrong number of checkers.

    **QUOTED SPANS ARE CUT FIRST, AND THIS RULE CAUGHT ITSELF DOING THE OPPOSITE.** The first
    version flagged the very sentence written to fix it: a document explaining that it used to say
    *"the other twelve checkers"* has to contain that phrase to explain it, and a rule that reads
    the quotation reads its own documentation. Good documentation names the thing it avoids, so an
    absence rule that scans quotations fails on the comment that justifies it -- the single most
    repeated defect in this battery, now three times in three batches.

    The doctrine is already written into `readable_prose` in this same file: *"Words we are quoting
    are never ours to change."* A count inside quotation marks is a report of what was said, not a
    claim about what is true.
    """
    text = OWNER_INLINE_QUOTE.sub(" ", text)
    text = QUOTED_SPAN.sub(" ", text)
    for match in CHECKER_CLAIM.finditer(text):
        raw = match.group(2).lower()
        claimed = WORD_NUMBERS.get(raw)
        if claimed is None:
            try:
                claimed = int(raw)
            except ValueError:
                continue
        # "the other twelve" counts everything except the one being described.
        total = claimed + 1 if match.group(1) else claimed
        if total != count:
            problems.append("%s says %r, which is %d checker(s); there are %d, and a reader "
                            "following that will skip one or hunt for one that is not there"
                            % (rel, match.group(0), total, count))
            return

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


# ------------------------------------------------- the expansions, which are all optional
#
# **Owner decision 19, binding: D1's option B text stays in force** -- *"do not announce
# compatibility until validation is complete"* -- and the queue row that this enforces says the
# consequence in its own words: the package *"must claim no profile row, no DLC interaction and
# no RWT co-op until that row has a recorded result"*, with **200 of the 294 dispositions still
# provisional**. The row also says what it needs to become: *"the main protection, not a
# formality"*.
#
# The RWT co-op half was already enforced by `FORBIDDEN_CLAIMS` above. The profile-row half is
# enforced by `check_broad_compatibility`. **This is the DLC half, and nothing covered it.**
#
# Every expansion is optional and `About.xml` declares none of them as a dependency, so a reader
# document stating that one is needed is wrong about what it takes to play -- which is a worse
# error than a stale version, because it turns somebody away at the door.
#
# **Narrow by construction, and negation-aware for the same reason the multiplayer rule is.**
# `docs/wiki/mods.md` exists to say the expansions are optional, so it must be able to name every
# one of them; only a sentence asserting a *requirement* is a finding. The phrase list pairs each
# expansion with requirement words rather than matching the name alone -- matching the name was
# tried first in the multiplayer rule's history and is recorded there as the way to fail the one
# document written to obey the rule.
EXPANSIONS = ("royalty", "ideology", "biotech", "anomaly", "odyssey")
REQUIREMENT_WORDS = ("requires", "required", "require", "needs", "needed", "must have",
                     "mandatory", "depends on", "dependency", "prerequisite")

EXPANSION_CLAIM = re.compile(
    r"\b(?:(?:" + "|".join(REQUIREMENT_WORDS).replace(" ", r"\s+") + r")\s+(?:the\s+)?(" +
    "|".join(EXPANSIONS) + r")\b"
    r"|\b(" + "|".join(EXPANSIONS) + r")\s+(?:expansion\s+|dlc\s+)?(?:is|are)\s+(?:" +
    "|".join(REQUIREMENT_WORDS).replace(" ", r"\s+") + r"))", re.I)


def check_expansion_claims(rel, prose, problems):
    """Refuse a reader document saying an expansion is needed. None is."""
    for sentence in sentences(prose):
        match = EXPANSION_CLAIM.search(sentence)
        if not match:
            continue
        lowered = sentence.lower()
        if any(negator in lowered for negator in CLAIM_NEGATORS):
            continue
        named = match.group(1) or match.group(2)
        problems.append("%s tells a reader %s is required; every expansion is optional and "
                        "About.xml declares none as a dependency -- D1: do not announce "
                        "compatibility until validation is complete (%r)"
                        % (rel, named, sentence[:90]))


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
        check_expansion_claims(rel, prose, problems)

        check_reader_dependency_assertions(rel, prose, problems)
        check_only_one_pages_deploy(rel, prose, problems)

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


# ---------------------------------------------------------------- the rule, inverted
# **WITH NOTHING DECLARED, THE DANGEROUS SENTENCE REVERSES.** Until 0.12.86-dev `About.xml`
# declared 293 hard dependencies and the hazard was a document claiming the package needed none.
# The block is gone -- owner, 2026-10-03: *"rework mod to not need any depeancie mods"*, *"we hope
# to have the mod as a complete stand alone"* -- and now the hazard is a document implying that
# needing nothing means working with everything.
#
# D1's binding text has not moved: *"do not announce compatibility until validation is
# complete"*. `docs/ROADMAP.md` already lists *"Promising compatibility with every mod simply
# because the server has `AllowAllMods` enabled"* as a non-goal; this is the first thing that
# enforces it.
BROAD_COMPATIBILITY_CLAIMS = (
    "compatible with every mod",
    "compatible with all mods",
    "works with every mod",
    "works with all mods",
    "works with all 294",
    "compatible with the whole",
    "fully compatible with",
    "guaranteed compatible",
    "no compatibility issues",
    "universally compatible",
)


def check_broad_compatibility(rel, raw, declared, problems):
    """Refuse a living document promising compatibility nobody has recorded a result for.

    Runs only while `About.xml` declares nothing, because that is when a reader has no
    declaration to calibrate against and silence reads as a guarantee. Same fence tracking and
    same same-clause retirement test as the rule it replaces -- a document may name the claim
    while saying it is not being made.
    """
    if declared > 0:
        return
    if rel in DEPENDENCY_LEDGER:
        return
    fenced = False
    for number, line in enumerate(raw.split("\n"), start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        lowered = line.lower()
        for phrase in BROAD_COMPATIBILITY_CLAIMS:
            if phrase not in lowered:
                continue
            if retirement_covers(line, phrase):
                continue
            problems.append("%s:%d says %r. Nothing is declared, and that is not a compatibility "
                            "certificate -- D1: do not announce compatibility until validation "
                            "is complete" % (rel, number, phrase))
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

# --------------------------------------------------------------------------- #
# The published site
# --------------------------------------------------------------------------- #
#
# Two queue rows, one piece of work, and the measurement that opened it was wrong in our favour.
#
# Row: *"`check-doc-conformance.py` must cover the published site"*. `living_docs()` already globs
# **every** `.md`, so the thirteen wiki pages were never uncovered. What was uncovered is the
# site's **non-markdown** published files -- a version claimed in a layout, a branch named in a
# stylesheet comment, a retired def named in the front door -- all of which would have shipped
# unexamined.
#
# Row: *"The generator stays internal, by the finding that opened this"*, noted as **stated in the
# config, not yet enforced**, because *"a comment is not a guard"*.
#
# **AND THE COMMENT WAS ALSO WRONG.** `_config.yml` said *"everything else under docs/ is project
# working material and is deliberately excluded"* while naming four directories, two of which do
# not exist. Jekyll publishes every entry in its source directory it is not told to exclude, and
# fifty-four documents sit at `docs/` root. Enabling Pages would have published `TODO.md`,
# `NOW.md`, `FINALIZED.md` and `DECOMPOSED.md` -- the whole ledger, as raw downloads, because none
# of them carries front matter.
#
# **This check does not read the exclude list and agree with it.** It works out what Jekyll would
# publish and fails on the answer, so a broken generator cannot produce a quiet pass.
SITE_SOURCE = os.path.join("docs")
SITE_CONFIG = os.path.join(REPO, SITE_SOURCE, "_config.yml")

# The work ledger, in both the form it is written and the form the internal renderer produces.
# The row names `TODO.html` and `NOW.html` specifically; the `.md` sources are the ones actually
# at risk, because they are what sits in the published directory.
LEDGER_NAMES = (
    "TODO.md", "TODO.html", "NOW.md", "NOW.html", "FINALIZED.md", "FINALIZED.html",
    "DECOMPOSED.md", "DECOMPOSED.html", "ROADMAP.md", "ROADMAP.html",
    "DEFERRED.md", "DEFERRED.html",
    "PREPRODUCTION_AND_IMPLEMENTATION_TODO.md", "PREPRODUCTION_AND_IMPLEMENTATION_TODO.html",
)

# What the published site is allowed to consist of. Anything else reaching the published set is a
# finding even when it is not a ledger: the ledger names are the hazard we know about, and a
# surface nobody declared is how the next one arrives.
SITE_SURFACE = ("wiki", "assets", "index.html", "CNAME")

# Files whose text is **not served as a file** but appears inside every published page. A layout
# is never fetched by a reader and its content is on every page a reader fetches, so a version
# claimed here ships exactly as widely as one claimed in prose. Checking the published set alone
# would have missed all three.
SITE_TEMPLATES = (
    os.path.join("docs", "_layouts", "default.html"),
    os.path.join("docs", "_includes", "nav.html"),
    os.path.join("docs", "_config.yml"),
)

HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
LIQUID_TAG = re.compile(r"\{%.*?%\}|\{\{.*?\}\}", re.S)
HTML_TAG = re.compile(r"<[^>]+>")
HTML_PARAGRAPH = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S | re.I)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
YAML_COMMENT = re.compile(r"^\s*#.*$", re.M)


def site_config_lists():
    """`include:` and `exclude:` as the config actually writes them.

    Hand-parsed rather than through a YAML library, because this project ships no third-party
    Python dependency and a checker that cannot run is a checker that does not exist. The parse
    is deliberately narrow: a block list of `- value` lines under a top-level key, which is the
    only shape either key has ever had here. Anything it cannot read is reported as unreadable
    rather than silently treated as empty -- an exclude list read as empty would publish
    everything, and this check would call that correct.
    """
    if not os.path.isfile(SITE_CONFIG):
        return None, None
    text = io.open(SITE_CONFIG, encoding="utf-8-sig").read()
    lists = {}
    key = None
    for line in text.split("\n"):
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", line):
            key = line.split(":", 1)[0]
            lists.setdefault(key, [])
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and key is not None:
            lists[key].append(stripped[2:].strip())
            continue
        if not line.startswith((" ", "\t")):
            key = None
    return lists.get("include"), lists.get("exclude")


def jekyll_publishes(rel, includes, excludes):
    """Conservative model of Jekyll's entry filter: would this path reach the built site?

    Jekyll keeps every entry unless it is *special* (a leading `_` or `.`), a backup, or matched
    by `exclude` -- and a match in `include` short-circuits all of that, which is the precedence
    that lets `include: [wiki]` keep a directory whose contents a pattern would otherwise drop.

    **Anything this cannot prove excluded is reported as PUBLISHED.** A ledger guard has exactly
    one failure mode it must never have, and that is calling a published file safe. Erring the
    other way produces a loud finding somebody fixes.
    """
    parts = rel.replace(os.sep, "/").split("/")
    for pattern in includes or ():
        clean = pattern.strip().strip("/")
        if not clean:
            continue
        if rel.replace(os.sep, "/") == clean or rel.replace(os.sep, "/").startswith(clean + "/"):
            return True
    if any(part.startswith("_") or part.startswith(".") for part in parts):
        return False
    for pattern in excludes or ():
        clean = pattern.strip().strip("/")
        if not clean:
            continue
        if rel.replace(os.sep, "/") == clean or rel.replace(os.sep, "/").startswith(clean + "/"):
            return False
    return True


def published_files(includes, excludes):
    """Every file under `docs/` that Jekyll would copy or render into the built site."""
    root = os.path.join(REPO, SITE_SOURCE)
    found = []
    for base, dirs, names in os.walk(root):
        rel_base = os.path.relpath(base, root)
        rel_base = "" if rel_base == "." else rel_base
        # Prune a directory Jekyll would not descend into, so a tree of working material is not
        # walked only to be discarded a thousand files later.
        dirs[:] = [d for d in dirs
                   if jekyll_publishes(os.path.join(rel_base, d) if rel_base else d,
                                       includes, excludes)]
        for name in sorted(names):
            rel = os.path.join(rel_base, name) if rel_base else name
            if jekyll_publishes(rel, includes, excludes):
                found.append(rel.replace(os.sep, "/"))
    return sorted(found)


def check_ledger_never_published(published, problems):
    """The owner's rule, enforced instead of stated.

    Owner direction, 2026-10-02, verbatim: *"the now.md needs to be completedy deleted, then
    written current. The NOW .md is a temp read file not a history of all work ever done.. its a
    one time record only ever holding one record"*, and the queue row that this closes says the
    ledger *"stays an internal reading convenience and is never wired to the published tree"*.
    """
    for rel in published:
        name = rel.split("/")[-1]
        if name in LEDGER_NAMES:
            problems.append("docs/%s would be PUBLISHED by the site; the work ledger is never "
                            "published. Exclude it in docs/_config.yml (run "
                            "tools/build-site.py)" % rel)
        top = rel.split("/")[0]
        if top not in SITE_SURFACE and name not in SITE_SURFACE:
            problems.append("docs/%s would be PUBLISHED and is not part of the declared site "
                            "surface %s; a published file nobody declared is how a ledger "
                            "arrives next time" % (rel, "/".join(SITE_SURFACE)))


def template_prose(raw, rel):
    """The reader-visible text of a published non-markdown file.

    Comments go first and for a reason that bit this battery before: good documentation explains
    the thing it avoids **by naming it**, so a layout's own comment quoting *"NOT pop like a text
    wall"* would otherwise read as prose making a claim. The same cut removes Liquid tags, which
    are instructions rather than words anybody reads.
    """
    text = HTML_COMMENT.sub(" ", raw)
    if rel.endswith(".css"):
        text = CSS_COMMENT.sub(" ", text)
    if rel.endswith((".yml", ".yaml")):
        text = YAML_COMMENT.sub(" ", text)
    text = LIQUID_TAG.sub(" ", text)
    text = HTML_TAG.sub(" ", text)
    text = OWNER_INLINE_QUOTE.sub(" ", text)
    return QUOTED_SPAN.sub(" ", text)


def site_text_files(published):
    """Published non-markdown files plus the templates whose text rides inside every page."""
    found = []
    for rel in published:
        if rel.endswith(".md"):
            continue            # `living_docs()` already holds every markdown file.
        path = os.path.join(REPO, SITE_SOURCE, rel)
        if os.path.isfile(path):
            found.append((os.path.join("docs", rel).replace(os.sep, "/"), path))
    for rel in SITE_TEMPLATES:
        path = os.path.join(REPO, rel)
        if os.path.isfile(path):
            found.append((rel.replace(os.sep, "/"), path))
    return sorted(set(found))


def check_published_non_markdown(entries, version, branch, count, problems):
    """Hold the site's non-markdown published files to the claims rule.

    A version or a branch stated in a layout, an include, the config or the front door ships to
    every reader exactly like one stated in prose, and until 0.12.93-dev nothing looked at any of
    them. Binary files are never read; a stylesheet is text and a comment in it is a claim.
    """
    for rel, path in entries:
        raw = io.open(path, encoding="utf-8-sig").read()

        for match in VERSION_CLAIM.finditer(raw):
            if version and match.group(1) != version:
                problems.append("%s claims version %s; the build is %s"
                                % (rel, match.group(1), version))

        for name in STALE_BRANCHES:
            if name in raw and branch and name != branch:
                problems.append("%s names working branch %r; the branch is %r"
                                % (rel, name, branch))

        for number, line in enumerate(raw.split("\n"), start=1):
            for definition in RETIRED_DEFS:
                if definition in line and not RETIREMENT_WORDS.search(line):
                    problems.append("%s:%d names retired def %s with nothing saying it is gone"
                                    % (rel, number, definition))

        check_checker_count(rel, raw, count, problems)

        # Only files whose words a reader actually meets are held to the vocabulary and the wall
        # rule. A stylesheet's selectors are not prose, and flagging one would be the crying-wolf
        # failure this file warns about in its own branch rule.
        if not rel.endswith((".html", ".htm")):
            continue
        prose = template_prose(raw, rel)
        scanned = DOC_BANNED_EXEMPT.sub(" ", prose)
        for term, pattern in DOC_BANNED:
            match = pattern.search(scanned)
            if match:
                problems.append("%s says %r to a reader -- %s"
                                % (rel, match.group(0), DOC_BANNED_TERMS[term]))
        check_forbidden_claims(rel, prose, problems)

        # Paragraphs are `<p>` elements here, not blank-line blocks: an HTML file has no blank
        # line between paragraphs, so the markdown splitter would read a whole page as one and
        # report every front door as a wall.
        for block in HTML_PARAGRAPH.findall(HTML_COMMENT.sub(" ", raw)):
            paragraph = " ".join(HTML_TAG.sub(" ", LIQUID_TAG.sub(" ", block)).split())
            if len(paragraph) > DOC_WALL_CHARS:
                problems.append("%s has a %d-character paragraph with no break; a reader meets "
                                "it as a wall (%r)" % (rel, len(paragraph), paragraph[:60]))


def check_cname(problems):
    """A live `CNAME` is one bare hostname and nothing else.

    `CNAME.example` already says so -- *"GitHub Pages reads the whole file as one hostname, so a
    real CNAME contains exactly one line and no comments"* -- and nothing enforced it. Copying the
    example and forgetting to delete the explanation is the obvious way to get this wrong, and it
    fails the way the example warns about: quietly, by Pages serving nothing while DNS is blamed.
    """
    path = os.path.join(REPO, SITE_SOURCE, "CNAME")
    if not os.path.isfile(path):
        return
    raw = io.open(path, encoding="utf-8-sig").read()
    lines = [line for line in raw.split("\n") if line.strip()]
    if len(lines) != 1:
        problems.append("docs/CNAME holds %d non-empty lines; GitHub Pages reads the whole file "
                        "as one hostname, so it must hold exactly one" % len(lines))
        return
    host = lines[0].strip()
    if host.startswith("#") or "#" in host:
        problems.append("docs/CNAME contains a comment; Pages reads the whole file as the "
                        "hostname and will serve nothing")
    if not re.match(r"^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$", host) or "." not in host:
        problems.append("docs/CNAME holds %r, which is not a bare hostname" % host[:60])
    if "PUT-YOUR-HOSTNAME-HERE" in raw:
        problems.append("docs/CNAME still holds the placeholder from CNAME.example; a CNAME "
                        "naming a domain nobody owns stops Pages answering on github.io")


# --------------------------------------------------------------------------- #
# THE ONLY PAGES DEPLOY IS THE PUBLIC REPOSITORY
# --------------------------------------------------------------------------- #
#
# **Owner direction, 2026-10-05, verbatim:** *"the only page deploy will be on the new github mod
# and wiki and public docs ONLY!!! DO YOU UNDERSTAND!!!!?????"*
#
# It is already the live state -- Pages on this repository returns 404 and has never been enabled,
# and `G-Fourteen/Rimrooms-AsyncIndustries` is built and serving. **What was wrong was the
# documents**: `TODO.md`, `NOW.md` and `PUBLIC_RELEASE_PLAN.md` each still told a reader to switch
# Pages on for *this* repository, and one of them named a `unity-lab-ai.github.io/Backrooms/`
# address. A queue row instructing a forbidden action is worse than a stale one: somebody does it.
#
# **So the rule is enforced rather than written down**, which is the whole lesson of 0.12.93-dev --
# a configuration file described an exclusion policy it did not implement, and the ledger was one
# switch away from being public.
#
# Nothing is deleted to achieve this. The Jekyll configuration stays exactly where it is, and its
# exclude list stays with it, because that list is what would refuse the ledger **if this
# repository were ever deployed by accident**. A guard costs nothing to keep and is the only thing
# standing between a mis-click and the work ledger.
PAGES_INSTRUCTION = re.compile(
    r"(settings\s*(?:→|->|>)\s*pages"
    r"|enabl\w*\s+pages"
    r"|turn\w*\s+on\s+pages"
    r"|pages\s+(?:source|is\s+enabled))", re.I)

# A sentence naming the public repository or its address is about the right deploy and is fine.
PAGES_ALLOWED = re.compile(
    r"(Rimrooms-AsyncIndustries|g-fourteen\.github\.io|the public repository|"
    r"the new (?:github )?repo)", re.I)

# Denials. Wider than CLAIM_NEGATORS because the subject here is an instruction, and the natural
# way to write a denial of one is "never", "forbidden", "no longer" or "superseded".
PAGES_NEGATORS = ("never", " not ", "no longer", "forbidden", "refus", "must not", "cannot",
                  "superseded", "instead", "would have", "was never", "404", "is not")

# An address this repository does not serve and now never will.
FOREIGN_PAGES_ADDRESS = re.compile(r"unity-lab-ai\.github\.io", re.I)


def check_only_one_pages_deploy(rel, raw, problems):
    """Refuse a living document that tells a reader to deploy Pages from this repository."""
    # **THE ADDRESS IS SCANNED ON RAW LINES, NOT ON PROSE, AND THAT IS NOT AN OVERSIGHT IN REVERSE.**
    # `readable_prose` strips code spans, which is right for claims -- a fenced example is not an
    # assertion. But `PUBLIC_RELEASE_PLAN.md` carried `unity-lab-ai.github.io/Backrooms/` **inside a
    # code span**, in a table saying that is what gets built, and the rule could not see it. A
    # hostname being advertised is a hostname being advertised whatever punctuation is around it.
    for number, line in enumerate(raw.split(NEWLINE), start=1):
        if not FOREIGN_PAGES_ADDRESS.search(line):
            continue
        lowered = line.lower()
        if any(negator in lowered for negator in PAGES_NEGATORS):
            continue
        problems.append("%s:%d names a Pages address this repository does not serve and never "
                        "will" % (rel, number))

    for sentence in sentences(readable_prose(raw)):
        lowered = sentence.lower()
        if PAGES_INSTRUCTION.search(sentence):
            if PAGES_ALLOWED.search(sentence):
                continue
            if any(negator in lowered for negator in PAGES_NEGATORS):
                continue
            problems.append("%s tells a reader to deploy Pages from THIS repository -- owner, "
                            "2026-10-05: the only Pages deploy is the public repository, and "
                            "Pages here is 404 by design (%r)" % (rel, sentence[:90]))
        if FOREIGN_PAGES_ADDRESS.search(sentence):
            if any(negator in lowered for negator in PAGES_NEGATORS):
                continue
            problems.append("%s names a Pages address this repository does not serve and never "
                            "will (%r)" % (rel, sentence[:90]))


# --------------------------------------------------------------------------- #
# About.xml's description: the most-read document this mod has
# --------------------------------------------------------------------------- #
#
# **It told every player the mod needs 294 other mods, and it needs none.**
#
# `About.xml` has declared **zero** `modDependencies` since 0.12.86-dev -- owner: *"rework mod to
# not need any depeancie mods"*, *"we hope to have the mod as a complete stand alone"*. Only
# `loadAfter` remained, which is sorting advice. The description never followed: it still said the
# build *"declares every member of it as a dependency"*, naming all five expansions and 288 mods.
#
# That text is what a player reads in the mod list before deciding whether they can run this at
# all, and **it was the one document nothing here checked**, because `living_docs()` globs `.md`.
# It survived six versions of a checker written specifically to catch stale claims.
#
# **The boundary with `check-info-cards.py` is deliberate.** That file owns *def cards* -- whether
# a thing a player can click has a label and a description at all. This owns *documents that make
# claims*, and `About.xml`'s description is a document the game displays.
#
# Found by generating the public repository's readme from this text and reading it: the readme said
# *"Needs no other mod and no expansion"* two lines above a section demanding five expansions. A
# contradiction that blatant survived because nothing had ever put the two sentences side by side.
ABOUT_XML = os.path.join(REPO, "Mod", "Rimrooms - Async Industries", "About", "About.xml")

# Asserting a dependency is the opposite error from `NO_DEPENDENCY_CLAIMS`, and which one is a
# finding depends on what `About.xml` declares. With nothing declared, these are the false ones.
DEPENDENCY_ASSERTION_CLAIMS = (
    "as a dependency",
    "declares every member",
    "is a requirement",
    "are required",
    "is required",
    "requires the following",
    "every dependency is declared",
    "hard dependency",
    "hard dependencies",
    # **ADDED AFTER A FALSE POSITIVE POINTED AT A REAL DEFECT.** A scoping bug flagged `README.md`
    # for the wrong reason, and the sentence it happened to print was genuinely false: *"RimWorld
    # 1.6, all five expansions, and the collection this build is authored against. Every requirement
    # is declared."* Fixing the bug made the finding vanish, so the phrasing is listed here -- a
    # defect that was real does not stop being real because the rule found it by accident.
    "requirement is declared",
    "requirements are declared",
    "every requirement",
    "declares every",
)


def about_description():
    """The description `About.xml` ships, or None."""
    if not os.path.isfile(ABOUT_XML):
        return None
    text = io.open(ABOUT_XML, encoding="utf-8-sig").read()
    match = re.search(r"<description>(.*?)</description>", text, re.S)
    if not match:
        return None
    # Entities matter here: the description is XML, and `&amp;` read as prose would be a word.
    body = match.group(1)
    return (body.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            .replace("&quot;", '"').replace("&apos;", "'"))


# A sentence can only be asserting a dependency if it is talking about one. These are the subjects.
DEPENDENCY_SUBJECTS = ("mod", "mods", "expansion", "expansions", "dlc", "collection",
                       "dependency", "dependencies", "royalty", "ideology", "biotech",
                       "anomaly", "odyssey", "profile")


# **THE NEGATOR MUST BE IN THE SAME CLAUSE AS THE CLAIM, AND A COMMA ENDS A CLAUSE HERE.**
#
# This file already records the identical defect in `retirement_covers`: *"One incidental `until`,
# about an entirely different subject, exempted the whole paragraph."* It happened again, in the
# other direction and on the page that matters most. `docs/wiki/install.md` said:
#
#     This build **declares every one of its requirements**, so your mod manager will tell you
#     what is missing before the game loads rather than failing later.
#
# A sentence-wide negator test saw *"rather than"* -- about failing later, nothing to do with
# dependencies -- and excused a false claim on the install page. **A false negative here is worse
# than a false positive**: the finding is simply never made.
#
# Commas are included in the split precisely because that is where the excuse was hiding. It cuts
# the other way too, and correctly: *"Nothing special is required, and nothing special is
# provided"* keeps its negator in the clause that carries the claim.
CLAUSE_SPLIT_PROSE = re.compile(r"[.;,]")


def phrase_found(lowered):
    """The first assertion phrase present, so the clause test knows what to scope around."""
    for phrase in DEPENDENCY_ASSERTION_CLAIMS:
        if phrase in lowered:
            return phrase
    return None


def negated_in_clause(sentence, phrase):
    """True when a negator sits in the same clause as the claim, not merely in the sentence."""
    if not phrase:
        return False
    lowered = sentence.lower()
    found = lowered.find(phrase)
    if found < 0:
        return False
    left, right = 0, len(sentence)
    for match in CLAUSE_SPLIT_PROSE.finditer(sentence):
        if match.end() <= found:
            left = match.end()
        elif match.start() >= found + len(phrase):
            right = match.start()
            break
    clause = lowered[left:right]
    return any(negator in clause for negator in CLAIM_NEGATORS)


def check_reader_dependency_assertions(rel, prose, problems):
    """Refuse a reader document asserting this mod needs something, when it declares nothing.

    **NARROWED AFTER SCORING ONE OUT OF FOUR.** The first version reused the phrase list written for
    `About.xml`, where every sentence is about dependencies. Turned loose on reader prose it flagged
    *"Nothing special is required"* -- a denial -- plus a table label and a heading, and caught one
    real claim. That is three false findings for one true one, and this file's own branch rule
    states the cost: *"A checker that cries wolf is a checker people learn to scroll past, which is
    worse than not having it."*

    So a finding now needs three things in **one sentence**: an assertion phrase, a subject that is
    actually a mod or an expansion, and no negator. The real claim --
    *"This build is authored against a specific collection and declares every member of it"* -- has
    all three. The three false ones each lack the subject or carry the negator.
    """
    if declared_dependency_count() > 0:
        return
    # **PARAGRAPHS, NOT RAW SENTENCES.** `sentences()` turned a table row --
    # `| Mods and expansions | What is required, what is optional |` -- into a sentence with a
    # subject and an assertion phrase in it, and flagged a column label. `paragraphs()` already
    # excludes tables, headings, lists and blockquotes, because **an assertion lives in prose and a
    # table cell is a label.** That distinction is the same one the wall rule relies on.
    for paragraph in paragraphs(prose):
        for sentence in sentences(paragraph):
            lowered = sentence.lower()
            if not any(phrase in lowered for phrase in DEPENDENCY_ASSERTION_CLAIMS):
                continue
            if not any(re.search(r"\b" + subject + r"\b", lowered)
                       for subject in DEPENDENCY_SUBJECTS):
                continue
            if negated_in_clause(sentence, phrase_found(lowered)):
                continue
            problems.append("%s tells a reader this mod needs something, and it declares NO "
                            "dependencies -- not one mod and not one expansion (%r)"
                            % (rel, sentence[:90]))


def check_about_description(version, branch, count, declared, problems):
    """Hold the mod's own description to the same claims rules as every reader-facing document."""
    description = about_description()
    if description is None:
        problems.append("About.xml has no <description>, which is the mod's own card in the "
                        "mod list")
        return False
    rel = "Mod/Rimrooms - Async Industries/About/About.xml"

    for match in VERSION_CLAIM.finditer(description):
        if version and match.group(1) != version:
            problems.append("%s claims version %s; the build is %s"
                            % (rel, match.group(1), version))

    for name in STALE_BRANCHES:
        if name in description and branch and name != branch:
            problems.append("%s names working branch %r; the branch is %r" % (rel, name, branch))

    for definition in RETIRED_DEFS:
        if definition in description:
            problems.append("%s names retired def %s to a player" % (rel, definition))

    check_checker_count(rel, description, count, problems)

    # **WHICH DEPENDENCY RULE APPLIES IS READ OFF About.xml ITSELF**, never typed, which is the
    # same discipline the markdown rules use. If the owner ever declares dependencies again, the
    # assertion rule stops firing and the denial rule starts, with nothing here to edit.
    lowered = description.lower()
    if declared <= 0:
        for phrase in DEPENDENCY_ASSERTION_CLAIMS:
            if phrase in lowered:
                problems.append("%s says %r while About.xml declares NO dependencies; that is "
                                "the claim a player reads before deciding whether they can run "
                                "this at all" % (rel, phrase))
    else:
        for phrase in NO_DEPENDENCY_CLAIMS:
            if phrase in lowered:
                problems.append("%s says %r, and About.xml declares %d dependencies"
                                % (rel, phrase, declared))

    prose = readable_prose(description)
    scanned = DOC_BANNED_EXEMPT.sub(" ", prose)
    for term, pattern in DOC_BANNED:
        match = pattern.search(scanned)
        if match:
            problems.append("%s says %r to a player -- %s"
                            % (rel, match.group(0), DOC_BANNED_TERMS[term]))
    check_forbidden_claims(rel, prose, problems)
    check_expansion_claims(rel, prose, problems)
    check_broad_compatibility(rel, description, declared, problems)
    return True


def check_published_site(version, branch, count, problems):
    """Everything above, and the inventory the summary prints."""
    includes, excludes = site_config_lists()
    if includes is None and excludes is None:
        problems.append("docs/_config.yml is missing, so what the site publishes cannot be "
                        "determined and the ledger guard cannot run")
        return [], []
    published = published_files(includes, excludes)

    # **A GUARD THAT LOOKED AT NOTHING MUST NOT REPORT A PASS.** Every rule below is an absence
    # rule, and an absence rule over an empty set is satisfied by construction -- so a broken
    # model, a renamed directory or an exclude that swallowed the site would all read as green.
    # The site publishes thirteen wiki pages; if the model finds none, it is not modelling the
    # site, whatever else it says. This is the same property the def-field checker spends three
    # plants on: *"a checker that silently passes everything is worse than no checker: it
    # manufactures confidence."*
    if not any(rel.startswith("wiki/") for rel in published):
        problems.append("the published-site model finds no page under docs/wiki/, so it is not "
                        "modelling the site and every rule below it would pass on an empty set")

    check_ledger_never_published(published, problems)
    entries = site_text_files(published)
    check_published_non_markdown(entries, version, branch, count, problems)
    check_cname(problems)
    return published, entries


def main():
    version = package_version()
    branch = current_branch()
    problems = []
    docs = living_docs()
    declared_dependencies = declared_dependency_count()
    checkers = checker_count()

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

        check_only_one_pages_deploy(rel, raw, problems)
        check_dependency_claims(rel, raw, declared_dependencies, problems)
        check_broad_compatibility(rel, raw, declared_dependencies, problems)

        check_checker_count(rel, text, checkers, problems)

        # Mentioning the file is fine; mentioning it without anywhere saying it is closed is
        # what leaves a reader thinking there is still somewhere to put work.
        if "DEFERRED.md" in text and not DEFERRED_CLOSED_WORDS.search(text):
            problems.append("%s mentions DEFERRED.md without saying anywhere that it is closed"
                            % rel)

    check_directions_reached_the_queue(problems)
    check_reader_facing(problems)
    published, site_entries = check_published_site(version, branch, checkers, problems)
    about_checked = check_about_description(version, branch, checkers,
                                           declared_dependencies, problems)

    print("doc-conformance")
    print("  living documents checked : %d" % len(docs))
    print("  declared dependencies    : %d (declared>0: no document may say there are none; declared==0: none may promise broad compatibility)"
          % declared_dependencies)
    print("  reader-facing documents  : %d, held to the vocabulary and the wall rule"
          % len(READER_FACING))
    print("  checkers on disk         : %d, counted off tools/ and never typed" % checkers)
    print("  a Pages deploy here WOULD publish : %d files, modelled rather than trusted"
          % len(published))
    print("                             THIS REPOSITORY IS NEVER DEPLOYED (Pages 404 by"
          " design); the list is the guard against an accidental switch")
    print("  non-markdown site files  : %d, held to the version, branch and claims rules"
          % len(site_entries))
    print("  ledger names refused     : %d, in the published set" % len(LEDGER_NAMES))
    print("  About.xml description    : %s, held to the same claims rules as a reader document"
          % ("checked" if about_checked else "MISSING"))
    print("  dated records skipped    : implementation records, FINALIZED, CHANGELOG, reviews")
    print("  build version            : %s" % version)
    print("  working branch           : %s" % branch)
    print("")

    if problems:
        print("FAIL: %d problem(s)" % len(problems))
        for problem in sorted(set(problems)):
            say("  - %s" % problem)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
