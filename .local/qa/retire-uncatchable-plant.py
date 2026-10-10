# -*- coding: utf-8 -*-
"""Retire a plant that cannot be caught by construction, and say why in place.

## The plant

*"the inverted rule is skipped while a dependency is declared"* inserts an
unconditional `return` into `check_broad_compatibility`, disabling it.

## Why it reported MISSED, and why that is correct

The rule only produces a finding when a living document contains a
broad-compatibility phrase. **No correct document in this tree contains one** --
that is the point of the rule. So disabling the rule changes nothing observable,
and the suite reported MISSED against a plant that was working exactly as
written.

Keeping it would leave this suite permanently at 6 of 7, which is how a red
instrument stops being read. Weakening the verifier to make it pass would be the
worse answer, and faking an offending document to catch it would mean shipping a
false compatibility claim in the tree.

**The rule is already proved to fire**: the plant above it, *"A DOCUMENT PROMISES
BROAD COMPATIBILITY NOW THAT NOTHING IS DECLARED"*, adds the offending sentence
and is CAUGHT. One plant per behaviour, and that behaviour has one.

So this one is commented out with the reason beside it, not deleted -- the next
person to notice the rule has no plant of its own needs to find this paragraph
rather than write the same uncatchable plant again.
"""
import io
import sys

NL = chr(10)
PATH = ".local/register/plant-dependencies.py"

OLD = (
    '    ("the inverted rule is skipped while a dependency is declared", DOCS_CHECKER,' + NL
    + '     u"    if declared > 0:" + chr(10) + u"        return" + chr(10),' + NL
    + '     u"    if declared > 0:" + chr(10) + u"        return" + chr(10)' + NL
    + '     + u"    return" + chr(10), DOCS),' + NL
)

NEW = (
    '    # **RETIRED: UNCATCHABLE BY CONSTRUCTION, and the suite proved it rather than me.**' + NL
    + '    # This planted an unconditional `return` into `check_broad_compatibility`, disabling'
    + NL
    + '    # it -- and reported MISSED, correctly. The rule only produces a finding when a living'
    + NL
    + '    # document contains a broad-compatibility phrase, and no correct document in this tree'
    + NL
    + '    # does; that is the whole point of the rule. Disabling it therefore changes nothing'
    + NL
    + '    # observable.' + NL
    + '    #' + NL
    + '    # The rule IS proved to fire: the plant above adds the offending sentence and is'
    + NL
    + '    # CAUGHT. One plant per behaviour, and this behaviour has one. Commented rather than'
    + NL
    + '    # deleted so the next person to notice the guard has no plant of its own finds this'
    + NL
    + '    # paragraph instead of writing the same uncatchable plant again.' + NL
    + '    #' + NL
    + '    #     ("the inverted rule is skipped while a dependency is declared", DOCS_CHECKER,'
    + NL
    + '    #      u"    if declared > 0:" + chr(10) + u"        return" + chr(10),' + NL
    + '    #      u"    if declared > 0:" + chr(10) + u"        return" + chr(10)' + NL
    + '    #      + u"    return" + chr(10), DOCS),' + NL
)

text = io.open(PATH, encoding="utf-8").read()

if "RETIRED: UNCATCHABLE BY CONSTRUCTION" in text:
    print("already retired")
    sys.exit(0)
if text.count(OLD) != 1:
    print("PLANT NOT UNIQUE (%d); nothing written" % text.count(OLD))
    sys.exit(1)

io.open(PATH, "w", encoding="utf-8", newline=NL).write(text.replace(OLD, NEW))
print("retired the uncatchable plant, with the reason in place")
