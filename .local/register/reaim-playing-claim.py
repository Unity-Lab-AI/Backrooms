# -*- coding: utf-8 -*-
"""Re-aim the play-document claim at the wiki. The role moved; the claim should not weaken.

`proof-playing-and-help.py` asserted *"the play document is held to the reader-facing rules"* and
read `PLAYING.md`'s presence in `READER_FACING` to prove it. `plant-playing-and-help.py` planted
its removal. Both were right about the thing that matters: **the document a player reads must be
held to the vocabulary rule, the wall rule and the claim guard.**

The owner's direction on 2026-10-01 moved that role: *"laying out the full wiki of the dame how to
play how to set it all up rimsort all of it"*. `docs/wiki/` is the play documentation now, and
`PLAYING.md` is the long-form working version behind it.

**The claim is pointed at the new document, not softened.** It gets stronger in two ways:

* it asserts **all twelve** wiki pages are in the set, not one document, so adding a page without
  supervising it fails,
* those pages are held to a **360-character** wall where `PLAYING.md` was held to 700.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-playing-and-help.py")
SUITE = os.path.join(REPO, ".local", "register", "plant-playing-and-help.py")

# ---------------------------------------------------------------- the proof
OLD_CLAIM = u'''check("it is held to the reader-facing rules",
      'os.path.join("docs", "PLAYING.md")' in conformance,
      "-- the vocabulary rule, the wall rule and the row 791 claim guard all hang off that set")'''

NEW_CLAIM = u'''# **The play document is the wiki now.** Owner, 2026-10-01: *"laying out the full wiki of the
# dame how to play how to set it all up rimsort all of it"*. `PLAYING.md` is the long-form
# working version behind it, and this claim follows the role rather than the filename.
#
# **Stronger than it was**, in two ways: every page is required rather than one document, so
# adding a page without supervising it fails; and these are held to a 360-character wall where
# `PLAYING.md` was held to 700.
WIKI_PAGES = ("index", "install", "first-hour", "scenarios", "gates", "backrooms", "company",
              "interface", "mods", "multiplayer", "troubleshooting", "links", "credits")
missing_pages = [name for name in WIKI_PAGES
                 if not os.path.isfile(os.path.join(REPO, "docs", "wiki", name + ".md"))]
unsupervised = [name for name in WIKI_PAGES
                if ('os.path.join(WIKI, "%s.md")' % name) not in conformance]

check("THE PLAY DOCUMENTATION IS A WIKI, AND EVERY PAGE OF IT EXISTS",
      not missing_pages,
      "-- missing: %s" % ", ".join(missing_pages))

check("and every page of it is held to the reader-facing rules",
      not unsupervised,
      "-- unsupervised: %s. The vocabulary rule, the wall rule and the row 791 claim guard all "
      "hang off that set, so a page outside it is a page nothing reads"
      % ", ".join(unsupervised))

check("and the wall limit is tighter than the old document was held to",
      "DOC_WALL_CHARS = 360" in conformance,
      "-- owner: *\\"public facing documnets ARE NOT to be text walls get to each point in as "
      "short a way as possible\\"*. It was 700")

check("and the long-form version points at it rather than competing with it",
      "wiki/index.md" in playing,
      "-- one canonical place, not two drifting copies")'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(OLD_CLAIM) != 1:
    print("PROOF ANCHOR PROBLEM: %d" % text.count(OLD_CLAIM))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(OLD_CLAIM, NEW_CLAIM, 1))

# ---------------------------------------------------------------- the plant
OLD_PLANT = u'''    ("THE PLAY DOCUMENT LEAVES THE READER-FACING SET", CONF,
     '    os.path.join("docs", "PLAYING.md"),\\n', "", PROOF),'''

NEW_PLANT = u'''    ("A WIKI PAGE LEAVES THE READER-FACING SET", CONF,
     '    os.path.join(WIKI, "troubleshooting.md"),\\n', "", PROOF),

    ("the wall limit goes back to the one the owner superseded", CONF,
     "DOC_WALL_CHARS = 360", "DOC_WALL_CHARS = 700", PROOF),

    ("a wiki page is deleted and nothing notices", CONF,
     '    os.path.join(WIKI, "install.md"),\\n', "", PROOF),'''

text = io.open(SUITE, encoding="utf-8").read()
if text.count(OLD_PLANT) != 1:
    print("SUITE ANCHOR PROBLEM: %d" % text.count(OLD_PLANT))
    raise SystemExit(1)
io.open(SUITE, "w", encoding="utf-8", newline="").write(text.replace(OLD_PLANT, NEW_PLANT, 1))

after_proof = io.open(PROOF, encoding="utf-8").read()
after_suite = io.open(SUITE, encoding="utf-8").read()
failures = []
if u'os.path.join("docs", "PLAYING.md")\' in conformance' in after_proof:
    failures.append("the proof still reads the old filename")
if u"THE PLAY DOCUMENTATION IS A WIKI" not in after_proof:
    failures.append("the re-aimed claim was not written")
if u'A WIKI PAGE LEAVES THE READER-FACING SET' not in after_suite:
    failures.append("the plant was not re-aimed")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("claim and plant re-aimed at the wiki; three plants where there was one")
