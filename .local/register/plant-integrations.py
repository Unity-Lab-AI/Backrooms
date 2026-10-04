# -*- coding: utf-8 -*-
"""Plant a fault, run the check, require failure, restore. Verified writes.

Two targets, because this batch ships a proof and a checker rule:

  * `proof-integrations.py` for the detection layer, the readout and the document
  * `tools/check-doc-conformance.py` for the row 791 claim guard -- and that one is planted with
    a REAL forbidden claim in a real reader-facing document, which is the only way to know the
    guard would have caught the thing it exists for
"""
import io
import os
import subprocess
import sys
import time

SRC = "src/RimroomsAsyncIndustries"
INTEG = SRC + "/Core/InstalledIntegrations.cs"
PANE = SRC + "/UI/OperationsFacilities.cs"
INHAB = SRC + "/Threats/InhabitantService.cs"
DOC = "docs/MULTIPLAYER.md"
# **The reader-facing claim guard moved to the wiki.** `MULTIPLAYER.md` keeps the
# server detail a maintainer needs and is no longer held to the row 791 guard, which
# is what the plant below detected by going MISSED.
WIKI_DOC = "docs/wiki/multiplayer.md"
CONF = "tools/check-doc-conformance.py"
PROOF = ".local/register/proof-integrations.py"
CHECKER = "tools/check-doc-conformance.py"

# (label, path, old, new, command to run, expected non-zero)

# **THE RESTORE DOES NOT SURVIVE THE PROCESS BEING KILLED.** `finally` handles an exception; it
# does nothing for an interrupted sweep, and that is how a planted fault reached the working tree
# for the third time. The sentinel makes it visible: `tools/check-plant-residue.py` refuses while
# this file exists and prints the path to restore.
# **ONE SENTINEL PER SUITE, named after the suite.** All sixteen shared a single path, so when
# `plant-containment.py` left one behind after a failed restore, the next suite's `_rr_unmark()`
# deleted it -- and `check-plant-residue.py` reported a clean tree with a planted fault in it.
# Fourth instance of residue reaching the tree and the first the sentinel could not see.
_RR_SENTINEL = os.path.join(".local", "register",
                            ".plant-in-progress-"
                            + os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0])


def _rr_mark(path, label):
    io.open(_RR_SENTINEL, "w", encoding="utf-8", newline="").write(
        u"planted %r into %s" % (label, path))


def _rr_unmark():
    try:
        os.remove(_RR_SENTINEL)
    except OSError:
        pass


def _rr_restore(path, original):
    """Put the file back, and do not believe it until it reads back identical.

    The failure this exists for was transient -- `OSError: [Errno 22]` on a path this same loop
    had already written twice -- so a retry turns it into a non-event. A restore that still will
    not verify raises with the sentinel left in place, which is what stops the sweep from planting
    the next fault on top of this one.
    """
    last = None
    for attempt in range(5):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(original)
            if io.open(path, encoding="utf-8").read() == original:
                return
            last = "the file read back different from what was written"
        except (OSError, IOError) as error:
            last = repr(error)
        time.sleep(0.25 * (attempt + 1))
    raise RuntimeError("RESTORE FAILED for %s after 5 attempts: %s. The sentinel %s is left in "
                       "place; tools/check-plant-residue.py will refuse until the file is "
                       "restored." % (path, last, _RR_SENTINEL))


PLANTS = [
    ("a package id drifts from the register", INTEG,
     'PackageId = "3609835606"', 'PackageId = "3609835607"', PROOF),

    ("detection stops using Core's own answer", INTEG,
     "ModsConfig.IsActive(state.PackageId)", "false", PROOF),

    ("the installed list is read once and goes stale", INTEG,
     "            int hash = ModLister.InstalledModsListHash(true);", "            int hash = 0;",
     PROOF),

    ("a tracked mod stops being tracked", INTEG,
     """            new IntegrationState
            {
                RegisterRow = 281,
                PackageId = "3799737423",
                NameKey = "RR_Integration_GravshipTwoName",
                PositionKey = "RR_Integration_GravshipTwoPosition",
            },
""", "", PROOF),

    ("THE DETECTION STARTS DECIDING SOMETHING", SRC + "/Gate/GateIntegrity.cs",
     "        internal void TickIntegrity()\n        {",
     "        internal void TickIntegrity()\n        {\n"
     "            if (Core.InstalledIntegrations.ActiveRow(11)) { return; }", PROOF),

    ("a package id appears outside the detection class", SRC + "/Gate/GateIntegrity.cs",
     "    public sealed partial class CompRimroomsGate\n    {",
     '    public sealed partial class CompRimroomsGate\n    {\n'
     '        private const string Unused = "3014915404";', PROOF),

    ("inhabitant generation opens up to any pawn kind", INHAB,
     "DefDatabase<RimroomsInhabitantDef>", "DefDatabase<PawnKindDef>.AllDefs; var _ =\n"
     "                DefDatabase<RimroomsInhabitantDef>", PROOF),

    ("the document stops denying a shared colony", DOC,
     "There is **no shared colony**.", "Companies can share a colony.", PROOF),

    ("the caveat moves out of the opening line", DOC,
     "**Nothing on this page has been tested in play.**", "Notes on playing together.", PROOF),

    ("the document starts claiming support", DOC,
     "## What you need", "## What you need\n\nRimWorld Together is supported.", PROOF),

    ("the readout stops drawing the heading", PANE,
     'heading: "RR_Integration_Heading".Translate(',
     'unusedHeading: "RR_Integration_Heading".Translate(', PROOF),

    # *"Loaded means present, not proven"* is the hover on the integration count now, so the
    # way to take it away from the player is to empty the `detail:` argument.
    ("the caveat becomes conditional", PANE,
     '                detail: "RR_Integration_Caveat".Translate());',
     '                detail: TaggedString.Empty);', PROOF),

    ("the position is hidden for a mod that is not loaded", PANE,
     "                listing.Label(state.PositionKey.Translate());",
     "                if (state.Active) { listing.Label(state.PositionKey.Translate()); }",
     PROOF),

    ("the section is never reached", PANE, "            DrawIntegrations(listing);\n", "", PROOF),

    ("THE CLAIM GUARD IS BLINDED", CONF,
     "        check_forbidden_claims(rel, prose, problems)\n", "", PROOF),

    # The guard itself, planted with a real claim in a real reader-facing document.
    # **RE-AIMED 0.12.97-dev.** The anchor was `## What it would be`, a heading that existed when
    # the page only described a shape. The page was rewritten to name RimWorld Together and explain
    # its model, and that heading went with it -- so the anchor pointed at nothing and
    # `check-plant-anchors.py` caught it before the suite could report PLANT SETUP BROKEN.
    #
    # `## What it is not` is the right home for it anyway: a page whose own section denies shared
    # research is the hardest place for an un-negated claim to hide, which is exactly what the
    # negation-aware rule has to get right.
    ("ROW 791: a real shared-research claim lands in a reader-facing document", WIKI_DOC,
     "## What it is not",
     "## What it is not\n\nResearch is synchronised research across every "
     "company on the server.", CHECKER),

    ("ROW 791: a real shared-colony claim lands in a reader-facing document", "README.md",
     "\n## ", "\n\nTwo players run one shared colony together.\n\n## ", CHECKER),
]


def write_verified(path, text):
    for _ in range(6):
        try:
            with io.open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            if io.open(path, encoding="utf-8").read() == text:
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not write %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


caught = 0
for label, path, old, new, command in PLANTS:
    original = io.open(path, encoding="utf-8").read()
    if original.count(old) < 1:
        print("PLANT SETUP BROKEN (0 matches): %s" % label)
        sys.exit(2)
    _rr_mark(path, label)
    write_verified(path, original.replace(old, new, 1))
    _rr_unmark()
    try:
        code = subprocess.call([sys.executable, command],
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # **THE RESTORE IS THE ONE LINE THAT MUST ALWAYS RUN.** It is what
        # makes a destructive instrument safe, and it was the one line not
        # protected: a leaked devnull handle raised OSError mid-run twice
        # and left planted source on disk both times.
        write_verified(path, original)
        _rr_unmark()
    ok = code != 0
    caught += 1 if ok else 0
    print("%s  %s" % ("CAUGHT " if ok else "MISSED!", label))

print("")
print("%d of %d planted faults caught" % (caught, len(PLANTS)))
sys.exit(0 if caught == len(PLANTS) else 1)
