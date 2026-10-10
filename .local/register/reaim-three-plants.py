# -*- coding: utf-8 -*-
"""Re-aim three plants at the wiki. They caught a real consequence of removing PLAYING.md.

`plant-playing-and-help.py` plants a shared-colony claim, a retired word and a wall of text into
`docs/PLAYING.md` and expects `check-doc-conformance.py` to refuse each. All three went **MISSED**
once `PLAYING.md` left `READER_FACING` -- which is exactly right: it is no longer held to the
vocabulary rule, the wall rule or the row 791 claim guard.

**The plants did their job.** They detected that a document stopped being supervised, which is the
one thing a reader-facing rule set can lose silently.

Re-aimed at `docs/wiki/troubleshooting.md`, where those rules now apply. Two of the three get
**stronger** in the move: the wall filler only had to clear 700 characters and now has to clear
**360**, and the page it lands in is one a confused player opens.
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUITE = os.path.join(REPO, ".local", "register", "plant-playing-and-help.py")

text = io.open(SUITE, encoding="utf-8").read()

# A target constant for the wiki page, beside the existing ones.
OLD_PATHS = u'''DOC = "docs/PLAYING.md"'''
NEW_PATHS = (u'''DOC = "docs/PLAYING.md"\n'''
             u'''# **The reader-facing rules live on the wiki now.** `PLAYING.md` is the long-form\n'''
             u'''# working version behind it and is no longer held to the vocabulary rule, the wall rule\n'''
             u'''# or the row 791 claim guard -- which three plants below detected by going MISSED.\n'''
             u'''WIKI_DOC = "docs/wiki/troubleshooting.md"''')
if text.count(OLD_PATHS) != 1:
    print("PATHS ANCHOR PROBLEM: %d" % text.count(OLD_PATHS))
    raise SystemExit(1)
text = text.replace(OLD_PATHS, NEW_PATHS, 1)

# ---------------------------------------------------------------- 1. the shared-colony claim
OLD_1 = (u'''    ("ROW 791: A REAL SHARED-COLONY CLAIM LANDS IN THE PLAY DOCUMENT", DOC,\n'''
         u'''     "\\n## The money", "\\n\\nTwo players run one shared colony together.\\n\\n## The money", CONF),''')
NEW_1 = (u'''    ("ROW 791: A REAL SHARED-COLONY CLAIM LANDS IN A WIKI PAGE", WIKI_DOC,\n'''
         u'''     "\\n## Reporting a problem",\n'''
         u'''     "\\n\\nTwo players run one shared colony together.\\n\\n## Reporting a problem", CONF),''')
if text.count(OLD_1) != 1:
    print("PLANT 1 ANCHOR PROBLEM: %d" % text.count(OLD_1))
    raise SystemExit(1)
text = text.replace(OLD_1, NEW_1, 1)

# ---------------------------------------------------------------- 2. the retired word
OLD_2 = (u'''    ("the retired vocabulary lands in the play document", DOC,\n'''
         u'''     "A **gate** is the built machine.", "A **portal** is the built machine.", CONF),''')
NEW_2 = (u'''    ("the retired vocabulary lands in a wiki page", WIKI_DOC,\n'''
         u'''     "A gate needs a registered coordinate to dial",\n'''
         u'''     "A portal needs a registered coordinate to dial", CONF),''')
if text.count(OLD_2) != 1:
    print("PLANT 2 ANCHOR PROBLEM: %d" % text.count(OLD_2))
    raise SystemExit(1)
text = text.replace(OLD_2, NEW_2, 1)

# ---------------------------------------------------------------- 3. the wall of text
# The old filler was sized for 700 characters. The wiki limit is 360, so the plant is now
# easier to trip and the claim behind it is stricter.
pattern = re.compile(
    r'    \("a wall of text lands in the play document", DOC,\n.*?CONF\),\n', re.S)
match = pattern.search(text)
if match is None:
    print("PLANT 3 NOT FOUND")
    raise SystemExit(1)
FILLER = (u"The company account is a ledger in dollars and it pays quoted company costs such as "
          u"staff wages and site fees and procurement orders and outstanding obligations, and it "
          u"is never spawned as physical silver for somebody to haul across a map on foot, which "
          u"is the whole distinction the two kinds of money exist to draw in the first place.")
NEW_3 = (u'    ("A WALL OF TEXT LANDS IN A WIKI PAGE", WIKI_DOC,\n'
         u'     "\\n## Reporting a problem",\n'
         u'     "\\n\\n" + "%s" + "\\n\\n## Reporting a problem", CONF),\n' % FILLER)
text = text[:match.start()] + NEW_3 + text[match.end():]

io.open(SUITE, "w", encoding="utf-8", newline="").write(text)

after = io.open(SUITE, encoding="utf-8").read()
failures = []
if u'WIKI_DOC = "docs/wiki/troubleshooting.md"' not in after:
    failures.append("the wiki target was not added")
for label in ("ROW 791: A REAL SHARED-COLONY CLAIM LANDS IN A WIKI PAGE",
              "the retired vocabulary lands in a wiki page",
              "A WALL OF TEXT LANDS IN A WIKI PAGE"):
    if label not in after:
        failures.append("missing plant %r" % label)
if u'lands in the play document' in after:
    failures.append("a plant still aims at the unsupervised document")
if len(FILLER) <= 360:
    failures.append("the wall filler is %d characters and must exceed 360" % len(FILLER))
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("three plants re-aimed at the wiki; the wall filler is %d characters against a 360 limit"
      % len(FILLER))
