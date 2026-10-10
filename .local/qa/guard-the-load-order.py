# -*- coding: utf-8 -*-
"""The load order is all that is left, so the load order gets a rule.

## A PLANT FOUND THIS, NOT A READING

`plant-dependencies.py` reported **MISSED: THE LOAD ORDER LOSES A FORMER
DEPENDENCY** — deleting `<li>brrainz.harmony</li>` from `loadAfter` produced no
finding from any of the eighteen checkers.

That gap was **created by the stand-alone change itself.**
`check-register-compliance.py` checked that every *declared dependency* also
appeared in `loadAfter`; with nothing declared, that rule has nothing to iterate
and `loadAfter` became unguarded. The deletion of 293 hard dependencies was only
safe *because* all 293 were already ordered — so the ordering is now the thing
carrying the whole weight, and it was the one thing nobody was checking.

The failure it protects against is measured, not hypothetical: our mod sat at
**position 197 of 296** in the owner's live load order with **99 mods loading
after it**. A mod that loads before the defs it reads does not announce itself; it
produces a null somewhere unrelated.

## The register is the authority, so the rule maintains itself

`docs/research/installed-mod-metadata-2026-09-27.csv` holds the profile's **294**
package ids, Core among them. `loadAfter` currently holds **294**, and the two
sets match exactly — measured before this rule was written, not asserted after.
Keying the rule to the register means adding a mod to the profile updates the
rule by updating the register, rather than by somebody remembering a number.
"""
import io
import sys

NL = chr(10)
CHECKER = "tools/check-register-compliance.py"

RULE = '''
# ------------------------------------------------- 1b. the load order carries the whole profile
# **A PLANT FOUND THIS GAP AND THE CHANGE ABOVE CREATED IT.** Owner, 2026-10-03: *"rework mod to
# not need any depeancie mods"*, *"we hope to have the mod as a complete stand alone"*. The 293
# hard dependencies came out of `About.xml` at 0.12.86-dev, and that was only safe because every
# one of them was already in `loadAfter`.
#
# So the rule above -- every declared dependency must also be ordered -- now has nothing to
# iterate, and `loadAfter` became the one thing carrying the whole weight and the one thing
# nobody checked. `plant-dependencies.py` reported MISSED when a former dependency was deleted
# from the order and not a single checker objected.
#
# **The cost is measured, not hypothetical.** Our mod sat at position 197 of 296 in the owner's
# live load order with 99 mods loading after it. A mod that loads before the defs it reads
# produces a null somewhere unrelated; it does not announce itself.
#
# Keyed to the register rather than to a literal count, so adding a mod to the profile updates
# this rule by updating the register.
profile = os.path.join(REPO, "docs", "research", "installed-mod-metadata-2026-09-27.csv")
if not os.path.isfile(profile):
    fail("the installed-mod metadata register is missing, so the load order cannot be checked "
         "against the profile it is meant to cover")
else:
    with io.open(profile, encoding="utf-8-sig") as handle:
        register_ids = set()
        for row in csv.DictReader(handle):
            value = (row.get("PackageID") or "").strip().lower()
            if value:
                register_ids.add(value)
    if not register_ids:
        fail("the installed-mod metadata register declares no PackageID column values")
    else:
        ordered = set(v.lower() for v in load_after)
        unordered = sorted(register_ids - ordered)
        strangers = sorted(ordered - register_ids)
        if unordered:
            fail("%d profile mod(s) are in the register and NOT in loadAfter, so this package "
                 "can load before them: %s" % (len(unordered), ", ".join(unordered[:8])))
        if strangers:
            fail("%d loadAfter entry/entries are not in the profile register, so nobody can say "
                 "what they are for: %s" % (len(strangers), ", ".join(strangers[:8])))
        if not unordered and not strangers:
            notes.append("loadAfter matches the %d-mod profile register exactly"
                         % len(register_ids))

'''

ANCHOR = "# ---------------------------------------------------------------- 2/3. patched mods"

text = io.open(CHECKER, encoding="utf-8").read()
problems = 0

if "1b. the load order carries the whole profile" in text:
    print("the rule is already present")
    sys.exit(0)

# `csv` is needed and the checker may not import it yet.
if NL + "import csv" + NL not in text:
    old = NL + "import os" + NL
    if text.count(old) != 1:
        print("COULD NOT FIND A SINGLE `import os` TO SIT BESIDE (%d)" % text.count(old))
        problems += 1
    else:
        text = text.replace(old, NL + "import csv" + NL + "import os" + NL, 1)
        print("added `import csv`")

if NL + "import io" + NL not in text:
    old = NL + "import os" + NL
    text = text.replace(old, NL + "import io" + NL + "import os" + NL, 1)
    print("added `import io`")

anchors = text.count(ANCHOR)
if anchors < 1:
    print("SECTION ANCHOR NOT FOUND")
    problems += 1
else:
    at = text.index(ANCHOR)
    text = text[:at] + RULE.lstrip(NL) + text[at:]
    print("inserted the load-order rule before section 2")

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

io.open(CHECKER, "w", encoding="utf-8", newline=NL).write(text)
print("wrote %s" % CHECKER)
