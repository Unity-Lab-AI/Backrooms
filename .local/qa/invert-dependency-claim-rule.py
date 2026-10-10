# -*- coding: utf-8 -*-
"""The claim rule inverts with the declaration, in the same change.

## The row that predicted this, verbatim from `docs/TODO.md`

*"A CHECKER CURRENTLY ENFORCES THE OPPOSITE, and it will block this work on the
first run."* ... *"The rule has to invert in the same change as the declaration,
or the build gate fails on correct documents -- and a checker that has to be
bypassed to ship correct work is how a gate stops being believed."*

**The prediction was half right, and the half it got wrong matters.**
`check_dependency_claims` begins `if declared <= 0: return`, so dropping the
block disables the old rule by itself and nothing fails. What the row got right
is the part that is not automatic: with nothing declared, the hazard **reverses
direction**. The dangerous sentence is no longer *"this needs nothing"* -- that
is now true -- it is *"this works with everything"*, which nobody has shown.

## D1 is the binding text and it has not moved

*"do not announce compatibility until validation is complete"*. A package that
declares no dependencies must not therefore imply it is compatible with all of
them. So the rule does not relax; it swaps which sentence it refuses, and the new
one is checked **only while nothing is declared**, which is exactly when a reader
would otherwise take silence for a guarantee.

The owner's own non-goal already says it in `docs/ROADMAP.md`: *"Promising
compatibility with every mod simply because the server has `AllowAllMods`
enabled."* That line had no enforcement behind it until now.
"""
import io
import sys

NL = chr(10)
CHECKER = "tools/check-doc-conformance.py"

BROAD_CLAIMS = '''
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
    for number, line in enumerate(raw.split("\\n"), start=1):
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

'''

EDITS = [
    # the new rule, defined beside the one it inverts
    ("def living_docs():", BROAD_CLAIMS.lstrip(NL) + NL + "def living_docs():"),

    # and called from the same place, on every living document
    ("        check_dependency_claims(rel, raw, declared_dependencies, problems)",
     "        check_dependency_claims(rel, raw, declared_dependencies, problems)" + NL
     + "        check_broad_compatibility(rel, raw, declared_dependencies, problems)"),

    # the printed label told a reader the rule only ever ran one way
    ('    print("  declared dependencies    : %d (no living document may say there are none)"',
     '    print("  declared dependencies    : %d (declared>0: no document may say there are '
     'none; declared==0: none may promise broad compatibility)"'),
]

text = io.open(CHECKER, encoding="utf-8").read()
problems = 0

if "BROAD_COMPATIBILITY_CLAIMS" in text:
    print("the inverted rule is already present")
    sys.exit(0)

for old, new in EDITS:
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d): %r" % (text.count(old), old.strip()[:84]))
        problems += 1
        continue
    text = text.replace(old, new)
    print("patched: %s" % old.strip()[:72])

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

io.open(CHECKER, "w", encoding="utf-8", newline=NL).write(text)
print("wrote %s" % CHECKER)
