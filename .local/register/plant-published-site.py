# -*- coding: utf-8 -*-
"""Prove the published-site guard can fail, which is the whole reason the row exists.

The row's words were *"a comment is not a guard"*. A guard that has never been seen refusing is
not distinguishable from a comment, so each rule gets a planted fault that must make it refuse.

Four groups, because four distinct properties are being proved:

* **The ledger guard refuses.** Plants 1-4 take an entry out of the generated exclude list and
  require a refusal -- three ledger files and one ordinary document, because the undeclared-surface
  rule is what stops the next ledger arriving under a name nobody listed.
* **The guard cannot be blinded into a pass.** Plants 5-6 break the publish model. An empty
  published set satisfies every absence rule by construction, so both must still refuse. *"A
  checker that silently passes everything is worse than no checker: it manufactures confidence."*
* **The non-markdown coverage is real.** Plants 7-12 put a stale version, a stale branch, a retired
  def, banned vocabulary, a text wall and a wrong checker count into a layout, an include, a
  stylesheet and the front door -- the files the row says were uncovered.
* **The rules do not refuse everything.** Plants 13-16 cover the CNAME rule, including one
  **valid** CNAME that must PASS. A rule that refuses every input is not a rule, and this is the
  control that proves the other three are discriminating.

Plants 17-21 point at `tools/build-site.py --check`, which is the instrument that keeps the
exclude list from falling behind the directory in the first place.
"""
import io
import os
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)

CHECK = ["tools/check-doc-conformance.py"]
BUILD = ["tools/build-site.py", "--check"]

CONFIG = "docs/_config.yml"
CHECKER = "tools/check-doc-conformance.py"
LAYOUT = "docs/_layouts/default.html"
NAV = "docs/_includes/nav.html"
CSS = "docs/assets/css/rimrooms.css"
FRONT = "docs/index.html"
WIKI_INDEX = "docs/wiki/index.md"
CNAME = "docs/CNAME"
SCRATCH = "docs/PLANTED_SCRATCH_DOC.md"

# One sentinel per suite, named after the suite. `tools/check-plant-residue.py` refuses while it
# exists and prints what to restore -- which is the only thing that makes a destructive instrument
# safe against an interrupted sweep, as opposed to against an exception.
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


def remove_verified(path):
    for _ in range(6):
        try:
            if os.path.exists(path):
                os.remove(path)
            if not os.path.exists(path):
                return
        except OSError:
            pass
        time.sleep(0.4)
    sys.stderr.write("FATAL: could not remove %s -- CHECK BY HAND\n" % path)
    sys.exit(3)


# A paragraph past the wall rule's 360-character ceiling, which was lowered to that figure on the
# owner's direction that public documents *"ARE NOT to be text walls"*.
WALL = ("This sentence exists only to be too long for the wall rule to accept, and it keeps "
        "going well past the point where a reader would have given up on it, which is exactly "
        "the property the rule measures rather than the property a word count measures, and it "
        "carries on for a while yet so that the measurement is not close to the boundary, and "
        "then further still, because a plant that lands just under the ceiling it is aiming at "
        "proves only that the ceiling exists somewhere above it.")

# **THE FIRST VERSION OF THIS WAS 330 CHARACTERS AGAINST A 360 CEILING, SO IT PLANTED NO WALL.**
# The run reported MISSED and the rule was innocent: the plant was wrong, not the claim. That is
# the same defect this battery recorded last batch -- *"ONE PLANT WAS WRONG, NOT THE CLAIM"* --
# so the length is now asserted rather than assumed. A plant suite that cannot plant its own
# fault manufactures exactly the confidence it exists to deny.
if len(WALL) <= 360:
    sys.stderr.write("PLANT SETUP BROKEN: the wall paragraph is %d characters and the ceiling "
                     "is 360, so it would plant nothing%s" % (len(WALL), chr(10)))
    sys.exit(2)

# (label, kind, path, old-or-content, new, command, expected exit)
#   kind "replace" -- substitute `old` with `new` once
#   kind "create"  -- write `old` as the whole file, which must not already exist
PLANTS = [
    # ---- the ledger guard refuses -------------------------------------------------------
    ("the queue itself would be published", "replace", CONFIG,
     "\n  - TODO.md", "", CHECK, 1),
    ("the handoff would be published", "replace", CONFIG,
     "\n  - NOW.md", "", CHECK, 1),
    ("the permanent archive would be published", "replace", CONFIG,
     "\n  - FINALIZED.md", "", CHECK, 1),
    ("an ordinary design document reaches the published surface", "replace", CONFIG,
     "\n  - GAME_DESIGN.md", "", CHECK, 1),

    # ---- the guard cannot be blinded into a pass ----------------------------------------
    ("the config parse is blinded, so nothing is excluded and everything publishes",
     "replace", CHECKER,
     'return lists.get("include"), lists.get("exclude")', "return [], []", CHECK, 1),
    ("the publish model is blinded to publish nothing at all", "replace", CHECKER,
     "            if jekyll_publishes(rel, includes, excludes):",
     "            if False and jekyll_publishes(rel, includes, excludes):", CHECK, 1),

    # ---- the non-markdown coverage the row asked for -------------------------------------
    ("a stale version claimed in the layout that wraps every page", "replace", LAYOUT,
     "<body>", "<body>\n<!-- current development version: 0.1.1-dev -->", CHECK, 1),
    ("a stale version claimed in the published stylesheet", "replace", CSS,
     "/* Rimrooms", "/* current development version 0.1.1-dev */\n/* Rimrooms", CHECK, 1),
    ("a retired working branch named in the generated index", "replace", NAV,
     "<!-- GENERATED", "<!-- on feature/preproduction-handoff -->\n<!-- GENERATED", CHECK, 1),
    ("a retired def promised on the front door", "replace", FRONT,
     "<h1>", "<p>Build the RR_MachineGate first.</p>\n  <h1>", CHECK, 1),
    ("banned vocabulary on the front door", "replace", FRONT,
     "Open the wiki", "Open the portal", CHECK, 1),
    ("a text wall on the front door", "replace", FRONT,
     "<h1>", "<p>" + WALL + "</p>\n  <h1>", CHECK, 1),
    ("a wrong checker count on the front door", "replace", FRONT,
     "<h1>", "<p>Run all four checkers.</p>\n  <h1>", CHECK, 1),
    ("a wrong checker count in a wiki page", "replace", WIKI_INDEX,
     "---", "---\nRun all three checkers.", CHECK, 1),

    # ---- the expansions are all optional, with the control that must pass ---------------
    #
    # Owner decision 19 keeps D1's option B binding: *"do not announce compatibility until
    # validation is complete"*, and the queue row spells out the consequence -- no profile row,
    # no DLC interaction, no RWT co-op until there is a recorded result. **The control is the
    # important half here.** `docs/wiki/mods.md` exists to say the expansions are optional, so it
    # has to be able to name every one of them; a rule that fired on the name would fail the one
    # document written to obey it, which is recorded as exactly how the multiplayer rule went
    # wrong first time.
    ("a wiki page tells a reader an expansion is required", "replace", WIKI_INDEX,
     "---", "---" + chr(10) + "Rimrooms requires Biotech to play." + chr(10), CHECK, 1),
    ("the same claim phrased the other way round", "replace", WIKI_INDEX,
     "---", "---" + chr(10) + "Anomaly is required for the entities." + chr(10), CHECK, 1),
    ("AN EXPANSION NAMED AS OPTIONAL, WHICH MUST PASS -- the control", "replace", WIKI_INDEX,
     "---", "---" + chr(10) + "Biotech is not required; nothing here needs Anomaly." + chr(10),
     CHECK, 0),

    # ---- the CNAME rule, including the control that must pass ---------------------------
    ("a CNAME still holding the example's placeholder", "create", CNAME,
     "PUT-YOUR-HOSTNAME-HERE\n", None, CHECK, 1),
    ("a CNAME with the explanation left in it", "create", CNAME,
     "rimrooms.example\n\n# delete everything below this line\n", None, CHECK, 1),
    ("a CNAME that is not a hostname at all", "create", CNAME,
     "https://rimrooms.example/wiki\n", None, CHECK, 1),
    ("A VALID CNAME, WHICH MUST PASS -- the control", "create", CNAME,
     "rimrooms.example\n", None, CHECK, 0),

    # ---- the generator that keeps the list current --------------------------------------
    ("a new document at docs/ root that nothing excludes yet", "create", SCRATCH,
     "# Scratch\n\nPlanted by plant-published-site.py.\n", None, BUILD, 1),
    ("an exclude entry removed, so the list is behind the directory", "replace", CONFIG,
     "\n  - HOWTO.md", "", BUILD, 1),
    ("an exclude naming something that is not there, which reads as protection",
     "replace", CONFIG,
     "\n  - HOWTO.md", "\n  - HOWTO.md\n  - evidence", BUILD, 1),
    ("the generated markers removed, so there is nowhere to write the list", "replace", CONFIG,
     "  # END GENERATED EXCLUDE LIST", "  # nothing here", BUILD, 1),
    ("a wiki page retitled, so the generated index is stale", "replace", WIKI_INDEX,
     "---", "---\n# A Title The Index Does Not Have\n", BUILD, 1),
]


caught = 0
attempted = 0
for label, kind, path, old, new, command, want in PLANTS:
    attempted += 1
    existed = os.path.isfile(path)
    original = io.open(path, encoding="utf-8").read() if existed else None

    if kind == "create":
        if existed:
            print("PLANT SETUP BROKEN (%s already exists): %s" % (path, label))
            sys.exit(2)
        _rr_mark(path, label)
        write_verified(path, old)
    else:
        if not existed:
            print("PLANT SETUP BROKEN (%s missing): %s" % (path, label))
            sys.exit(2)
        if original.count(old) < 1:
            print("PLANT SETUP BROKEN (0 matches for %r): %s" % (old[:40], label))
            sys.exit(2)
        _rr_mark(path, label)
        write_verified(path, original.replace(old, new, 1))
    _rr_unmark()

    try:
        code = subprocess.call([sys.executable] + command,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    finally:
        # The one line that must always run. A leaked handle raising mid-run is how planted
        # source reached the working tree twice before.
        if kind == "create":
            remove_verified(path)
        else:
            write_verified(path, original)
        _rr_unmark()

    ok = code == want
    caught += 1 if ok else 0
    print("%s  %s (exit %d, wanted %d)"
          % ("CAUGHT " if ok else "MISSED!", label, code, want))

print("")
print("%d of %d planted faults caught" % (caught, attempted))
sys.exit(0 if caught == attempted else 1)
