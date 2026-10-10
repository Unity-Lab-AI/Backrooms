# -*- coding: utf-8 -*-
"""Re-scope the bare-statement claim, written to a FILE because a heredoc mangled it.

Eleventh time a bash heredoc has turned an escaped newline into a real one in this project, and
the rule is written at the top of `docs/NOW.md`: **use the Write tool for anything with escapes,
apostrophes or a regex.** Writing it down has not been enough; reaching for the tool first is the
only thing that has worked.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-generation-batch.py")

BROKEN_START = u'''check("and no family fixture other than a landmark still throws",'''
GOOD_END = u'''# -------------------------------------------------- two transmitters on one cell'''

REPLACEMENT = u'''check("and no family fixture other than a landmark still throws",
      content.count("landmark = Place(map, room, coordinate,") == 7
      and BARE_FIXTURE not in content
      and "{ Place(map, room, coordinate," not in content,
      "-- scoped to a BARE statement, because the absence of "
      "`Place(map, room, coordinate, \\"Shelf\\"...)` is NOT the claim: that string is a substring "
      "of `service_passage`'s own landmark, and the first draft of this claim refused correct "
      "code because of it. Thirty-seventh instance of the scoping trap. What has to be gone is a "
      "family fixture whose result nobody keeps -- those are the twelve that could throw and had "
      "no reason to")

'''

text = io.open(PROOF, encoding="utf-8").read()
start = text.index(BROKEN_START)
end = text.index(GOOD_END)
io.open(PROOF, "w", encoding="utf-8", newline="").write(
    text[:start] + REPLACEMENT + text[end:])

# The literal the claim needs, defined once beside the other file bindings so the escape lives
# in exactly one place and never has to survive a shell again.
text = io.open(PROOF, encoding="utf-8").read()
ANCHOR = u'''content = strip_cs_comments(read(os.path.join(SRC, "Generation", "RoomContentBuilder.cs")))'''
BINDING = ANCHOR + u'''

# A family fixture written as a bare statement, at the indent the switch arms use. Its ABSENCE is
# the claim that every decoration became a `Decorate` call; see that claim for why the obvious
# shorter string was wrong.
BARE_FIXTURE = chr(10) + " " * 28 + "Place(map, room, coordinate,"'''
if text.count(ANCHOR) != 1:
    print("BINDING ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(text.replace(ANCHOR, BINDING, 1))
print("claim re-scoped and the literal bound once")
