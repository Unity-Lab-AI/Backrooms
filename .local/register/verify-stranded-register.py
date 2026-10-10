# -*- coding: utf-8 -*-
"""Add the lost-pawn register to `proof-stranded-crew.py`. The owner asked for a verification.

Owner, 2026-10-01: *"andf yes do those three things you listed as well"*, the third being to
verify the stranded-crew rows against `Company/LostPawnRegister.cs`. The row states the fear
itself: *"If a closing gate hands its crew to the world-pawn pool, or despawns them, or marks
them lost in any way that removes player control, that is a defect against this direction and the
most consequential kind."*

## The reading, and why it is better than it needed to be

`LostPawnRegister.cs` cannot remove player control **by construction**: it holds a
`List<string>`. No `Pawn` field, no `Thing` reference, no `PassToWorld`, no `Destroy`, no
`DeSpawn`. `NoteLostPawn` takes a name. It is a list of names used to make a stranger found in a
corridor somebody the player recognises -- *"finding random pawns of disappering"* -- and it has
no mechanism for touching a live colonist at all.

## But a reading is not a claim, which is the whole point of asking

`proof-stranded-crew.py` had **eleven claims and not one of them mentioned the register.** So the
guarantee rested on nobody ever adding a `Pawn` field to a file whose job sounds exactly like
somewhere a pawn would go. The three claims below make the structural property permanent: the day
somebody stores a pawn there, or despawns one, the proof fails and says why.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROOF = os.path.join(REPO, ".local", "register", "proof-stranded-crew.py")

ANCHOR = u'check("an alert reports a crew awaiting recovery",'

ADDITION = u'''# --------------------------------------------------------- the register of the lost
# **The owner asked for this verification by name**, 2026-10-01: check the stranded-crew rows
# against `Company/LostPawnRegister.cs`. The row names the fear: *"If a closing gate hands its
# crew to the world-pawn pool, or despawns them, or marks them lost in any way that removes
# player control, that is a defect against this direction and the most consequential kind."*
#
# **Eleven claims above and not one mentioned the register**, so the guarantee rested on nobody
# ever adding a `Pawn` field to a file whose name sounds exactly like somewhere a pawn would go.
register = no_comments(io.open(os.path.join(
    SRC, "Company", "LostPawnRegister.cs"), encoding="utf-8-sig").read())

check("THE LOST-PAWN REGISTER HOLDS NAMES, NOT PAWNS",
      "private List<string> lostPawnNames = new List<string>();" in register
      and "public void NoteLostPawn(string name)" in register
      and "public string TakeLostPawnName()" in register
      and "Pawn" not in register,
      "-- *\\"marks them lost in any way that removes player control\\"* is impossible here BY "
      "CONSTRUCTION: there is no pawn to mark. It is a list of names, so a stranger in a corridor "
      "can be somebody the player recognises")

check("and it cannot despawn, destroy or hand anybody to the world",
      not any(token in register for token in
              ("PassToWorld", "DeSpawn", "Destroy", "worldPawns", "Discard")),
      "-- the four verbs that would take a colonist away. **None of them is in the file**, and "
      "this claim is what keeps it that way")

check("and nothing it stores can outlive the save or point at a living colonist",
      "Scribe_Collections.Look(ref lostPawnNames" in register
      and "LookMode.Value" in register
      and "Scribe_References" not in register,
      "-- saved by VALUE. A `Scribe_References` list in this file would be a set of live pawn "
      "handles, which is the shape the row is afraid of")

'''

text = io.open(PROOF, encoding="utf-8").read()
if text.count(ANCHOR) != 1:
    print("ANCHOR PROBLEM: %d" % text.count(ANCHOR))
    raise SystemExit(1)
io.open(PROOF, "w", encoding="utf-8", newline="").write(
    text.replace(ANCHOR, ADDITION + ANCHOR, 1))

after = io.open(PROOF, encoding="utf-8").read()
failures = []
if u"THE LOST-PAWN REGISTER HOLDS NAMES, NOT PAWNS" not in after:
    failures.append("the claim was not added")
if u"no_comments" not in after.split(u"the register of the lost")[0]:
    failures.append("the proof has no no_comments helper, so the new claims cannot strip prose")
if u"SRC" not in after.split(u"the register of the lost")[0]:
    failures.append("the proof has no SRC path, so the new claims cannot find the file")
for failure in failures:
    print("VERIFY FAILED: %s" % failure)
if failures:
    raise SystemExit(1)
print("three claims added: the register holds names, cannot despawn, and saves by value")
