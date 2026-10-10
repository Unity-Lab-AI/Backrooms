# -*- coding: utf-8 -*-
"""The two plant anchors a heredoc could not express.

**FOURTEENTH HEREDOC ESCAPE MANGLING IN THIS REPOSITORY.** Both needles below
contain the two characters backslash-n, because the plant file stores them as a
Python string literal that itself contains an escape. Passed through a heredoc,
`\\\\n` arrived as a real newline, the search matched nothing and the run
reported `NOT UNIQUE (0)` against a needle that is plainly there. `docs/NOW.md`
names this exact trap: *"USE THE WRITE TOOL FOR ANY SCRIPT WITH ESCAPES"*.

Both plants are re-aimed at the `detail:` argument that now carries their text,
which is the line that has to break for the player to stop seeing it.
"""
import io
import sys

NL = chr(10)

EDITS = [
    (".local/register/plant-integrations.py",
     '    ("the caveat becomes conditional", PANE,' + NL
     + '     \'            listing.Label("RR_Integration_Caveat".Translate());\\n\', "", PROOF),',

     '    # *"Loaded means present, not proven"* is the hover on the integration count now, so the'
     + NL
     + '    # way to take it away from the player is to empty the `detail:` argument.' + NL
     + '    ("the caveat becomes conditional", PANE,' + NL
     + '     \'                detail: "RR_Integration_Caveat".Translate());\',' + NL
     + '     \'                detail: TaggedString.Empty);\', PROOF),'),

    (".local/register/plant-planner-and-missions.py",
     '    ("the survey contract loses its own terms", TERMS,' + NL
     + '     \'                listing.Label("RR_UI_ContractTerms".Translate());\\n'
     + '                return;\\n\',' + NL
     + '     "                return;\\n", PROOF),',

     '    # The survey terms are the hover on the pane\'s own short heading now.' + NL
     + '    ("the survey contract loses its own terms", TERMS,' + NL
     + '     \'                    detail: "RR_UI_ContractTerms".Translate());\',' + NL
     + '     \'                    detail: TaggedString.Empty);\', PROOF),'),
]

problems = 0
touched = {}

for path, old, new in EDITS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if text.count(old) != 1:
        print("NEEDLE NOT UNIQUE (%d) in %s" % (text.count(old), path.split("/")[-1]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-36s re-aimed at the detail argument" % path.split("/")[-1])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path.split("/")[-1])
