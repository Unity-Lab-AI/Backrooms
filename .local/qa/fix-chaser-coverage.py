# -*- coding: utf-8 -*-
"""Two gaps the chaser plant suite found in its own proof.

Both MISSED results were **the claims being wrong, not the code**, which is the
outcome a plant suite exists to produce on the day a proof is written.

1. *"THE WITHDRAWAL VANISHES THE PAWN AGAIN"* -- the claim matched the old code's
   exact three-line layout with a regex, so reinstating the destroy on a
   different line passed it. Scoped to the `WithdrawPursuer` body and made
   shape-free. **Scoped matters:** `StartPursuer` legitimately destroys a pawn
   whose spawn failed, so a file-wide absence claim would be false against
   correct code -- the other way this claim could have been wrong.

2. *"THE RETIRED THING CLASS COMES BACK"* -- the plant appended
   `// Thing_QuietPursuer` as a comment and reported MISSED, correctly: the proof
   strips comments before reading, and a comment naming a retired class is
   harmless. The plant was testing nothing. Re-aimed at a fault that is real and
   silent -- dropping the chaser's save reference -- with a claim to match.

**SIXTEENTH HEREDOC ESCAPE MANGLING.** The first attempt at this patch went
through a shell heredoc and the regex in the needle arrived with its backslashes
collapsed, so the search matched nothing and reported `AssertionError: 0`.
`docs/NOW.md` names this trap; this file is the Write-tool version of it.
"""
import io
import sys

NL = chr(10)

PROOF = ".local/register/proof-chaser.py"
PLANTS = ".local/register/plant-chaser.py"

OLD_CLAIM = (
    'check("THE ENCOUNTER ENDING NO LONGER VANISHES THE PAWN",' + NL
    + '      "pursuerWithdrawn = true;" in chaser' + NL
    + '      and not re.search(r"pursuer\\.Destroy\\(DestroyMode\\.Vanish\\);\\s*\\n\\s*pursuer = null;\\s*\\n\\s*if \\(report",'
    + NL
    + '                        chaser),' + NL
    + '      "-- a dead raider leaves a corpse to strip and a live one may be met again. Vanishing the "'
    + NL
    + '      "thing a crew just fought reads as a bug")'
)

NEW_CLAIM = (
    "# **SCOPED TO THE METHOD, AND SHAPE-FREE.** The first draft matched the old code's exact"
    + NL
    + "# three-line layout with a regex, so a plant that reinstated the destroy on a different line"
    + NL
    + "# sailed past it and the suite reported MISSED. Scoped because `StartPursuer` legitimately"
    + NL
    + "# destroys a pawn whose spawn failed -- a file-wide absence claim would be false against"
    + NL
    + "# correct code, which is the other way this claim could have been wrong." + NL
    + '_withdraw = chaser[chaser.index("private void WithdrawPursuer("):]' + NL
    + '_withdraw = _withdraw[:_withdraw.index("private Dictionary<int, int> DistancesFrom(")]' + NL
    + 'check("THE ENCOUNTER ENDING NO LONGER VANISHES THE PAWN",' + NL
    + '      "pursuerWithdrawn = true;" in _withdraw' + NL
    + '      and "Destroy(" not in _withdraw,' + NL
    + '      "-- a dead raider leaves a corpse to strip and a live one may be met again. Vanishing the "'
    + NL
    + '      "thing a crew just fought reads as a bug")' + NL
    + NL
    + "# **A CHASER THAT IS NOT SAVED DISAPPEARS ON RELOAD, SILENTLY.** The encounter flags are"
    + NL
    + "# saved, so losing only the reference leaves the site certain something is hunting the crew"
    + NL
    + "# and unable to say what -- and the readout keeps reporting a room number for a pawn that is"
    + NL
    + "# gone." + NL
    + 'check("AND THE CHASER IS SAVED WITH THE SITE",' + NL
    + "      'Scribe_References.Look(ref pursuer, \"rr_pursuer\");' in site," + NL
    + '      "-- the encounter flags persist, so losing only the reference leaves the site certain "'
    + NL
    + '      "something is hunting the crew and unable to say what")'
)

OLD_PLANT = (
    "    # ------------------------------------------------- the retirement itself" + NL
    + '    ("THE RETIRED THING CLASS COMES BACK", SITE,' + NL
    + '     "        private Pawn pursuer;",' + NL
    + '     "        private Pawn pursuer; // Thing_QuietPursuer", PROOF),'
)

NEW_PLANT = (
    "    # ------------------------------------------------- the chaser survives a reload" + NL
    + "    # **THE FIRST VERSION OF THIS PLANT TESTED A COMMENT.** It appended" + NL
    + "    # `// Thing_QuietPursuer` to the field and reported MISSED -- correctly, because the"
    + NL
    + "    # proof strips comments before reading, and a comment naming a retired class is"
    + NL
    + "    # harmless. Re-aimed at a fault that is real and silent: the encounter flags are saved,"
    + NL
    + "    # so dropping only the reference leaves the site certain something is hunting the crew"
    + NL
    + "    # and unable to say what." + NL
    + '    ("THE CHASER STOPS BEING SAVED, so it vanishes on reload", SITE,' + NL
    + "     '            Scribe_References.Look(ref pursuer, \"rr_pursuer\");' + CHR_NL," + NL
    + '     "", PROOF),'
)

EDITS = [(PROOF, OLD_CLAIM, NEW_CLAIM), (PLANTS, OLD_PLANT, NEW_PLANT)]

problems = 0
touched = {}

for path, old, new in EDITS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d) in %s" % (text.count(old), path.split("/")[-1]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-28s patched" % path.split("/")[-1])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path.split("/")[-1])
