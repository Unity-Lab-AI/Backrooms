# -*- coding: utf-8 -*-
"""Re-aim the dependency suite at the invariant that replaced its premise.

## The premise it was built on is the thing the owner reversed

The suite was written against owner direction, 2026-10-01: *"the mod DOES HAVE
HARD DEPENDANCIES SO GET IT RIGHT"*, and it planted faults into the 293-row
`modDependencies` block -- a missing `displayName`, a missing URL, a self
reference, Core declared as a dependency, a row required but never ordered.

Owner direction, 2026-10-03, reverses it: *"rework mod to not need any depeancie
mods"* and *"we hope to have the mod as a complete stand alone"*. The block is
gone, so five of the seven plants have nothing to edit and the two that do were
planting faults into rows that no longer exist.

## What is worth protecting NOW, and it is not nothing

Three properties replaced the old five, and each one is a real way this change
could have gone wrong or could silently rot:

  1. **`loadAfter` still carries every former dependency.** The deletion was only
     safe because all 293 were already there. A later pass that trimmed
     `loadAfter` would reintroduce the position-197 defect -- our mod sat at 197
     of 296 in the owner's live order with 99 mods loading after it -- with
     nothing left to notice.
  2. **The block does not come back.** A declaration re-added by habit or by a
     merge puts the requirement wall back in front of every player.
  3. **Nothing is promised in its place.** With no declaration, the new hazard is
     a document reading silence as a compatibility certificate, which is what
     `check_broad_compatibility` now refuses.

The old plants are **kept in the file, commented, with the direction that retired
them**, so nobody rebuilds them from scratch if the owner reverses again. The
suite's own header already records that this rule was once a prohibition, then an
assertion; this is the third position and the record of all three is the point.
"""
import io
import sys

NL = chr(10)
PATH = ".local/register/plant-dependencies.py"

NEW_PLANTS = '''PLANTS = [
    # ===================================================================================
    # **THE PREMISE OF THIS SUITE WAS REVERSED BY THE OWNER, 2026-10-03.** Verbatim: *"rework
    # mod to not need any depeancie mods"*, and the same day *"and im reiterating the fact that
    # we need to fix the depancy list so that its accurate to what is required and we hope to
    # have the mod as a complete stand alone"*.
    #
    # `About.xml` declared 293 hard `modDependencies`. They are gone at 0.12.86-dev, and the
    # deletion was only safe because **every one of them was already in `loadAfter`** -- so the
    # load order did not change and only the requirement wall went.
    #
    # The seven plants that edited rows inside that block are kept at the bottom of this list,
    # commented, with the direction that retired them. Five of them had nothing left to edit and
    # two were planting faults into rows that no longer exist; a suite whose anchors match
    # nothing reports that nothing broke. They are not deleted because the owner has reversed
    # this rule twice already -- prohibition, then assertion, now prohibition again -- and
    # rebuilding them from scratch on a third reversal is how coverage gets lost.
    # ===================================================================================

    # --------------------------------------- the position-197 defect, in its new shape
    # The ordering is all that is left, so the ordering is what has to be defended. Harmony is
    # first in the owner's live load order and was row one of the deleted block.
    ("THE LOAD ORDER LOSES A FORMER DEPENDENCY", ABOUT,
     u"    <li>brrainz.harmony</li>" + chr(10), u"", REGISTER),

    ("loadAfter stops naming Core at all", ABOUT,
     u"    <li>Ludeon.RimWorld</li>" + chr(10), u"", REGISTER),

    # --------------------------------------- the requirement wall comes back
    # A manager shows a player a missing-dependency wall for every row in this block. Re-adding
    # one by habit or by a merge is the regression the owner's direction exists to prevent, and
    # `check-register-compliance.py` is the rule that has to catch it.
    ("A HARD DEPENDENCY IS DECLARED AGAIN, WITH NO NAME FOR THE PLAYER", ABOUT,
     u"  <loadAfter>",
     u"  <modDependencies>" + chr(10)
     + u"    <li>" + chr(10)
     + u"      <packageId>brrainz.harmony</packageId>" + chr(10)
     + u"    </li>" + chr(10)
     + u"  </modDependencies>" + chr(10)
     + u"  <loadAfter>", REGISTER),

    ("Core is declared as a mod dependency again", ABOUT,
     u"  <loadAfter>",
     u"  <modDependencies>" + chr(10)
     + u"    <li>" + chr(10)
     + u"      <packageId>Ludeon.RimWorld</packageId>" + chr(10)
     + u"      <displayName>RimWorld</displayName>" + chr(10)
     + u"    </li>" + chr(10)
     + u"  </modDependencies>" + chr(10)
     + u"  <loadAfter>", REGISTER),

    ("the package is declared as its own dependency again", ABOUT,
     u"  <loadAfter>",
     u"  <modDependencies>" + chr(10)
     + u"    <li>" + chr(10)
     + u"      <packageId>Rimrooms.AsyncIndustries</packageId>" + chr(10)
     + u"      <displayName>Rimrooms - Async Industries</displayName>" + chr(10)
     + u"      <steamWorkshopUrl>steam://url/CommunityFilePage/1</steamWorkshopUrl>" + chr(10)
     + u"    </li>" + chr(10)
     + u"  </modDependencies>" + chr(10)
     + u"  <loadAfter>", REGISTER),

    # --------------------------------- and nothing is promised in the declaration's place
    # D1, unmoved: *"do not announce compatibility until validation is complete"*. With nothing
    # declared, a reader has no declaration to calibrate against and silence reads as a
    # guarantee, which is why `check_broad_compatibility` only runs while the count is zero.
    ("A DOCUMENT PROMISES BROAD COMPATIBILITY NOW THAT NOTHING IS DECLARED", ARCHITECTURE,
     u"## B8. Multiplayer, DLC and profile model",
     u"## B8. Multiplayer, DLC and profile model" + chr(10) + chr(10)
     + u"Rimrooms is fully compatible with every mod in the profile.", DOCS),

    ("the inverted rule is skipped while a dependency is declared", DOCS_CHECKER,
     u"    if declared > 0:" + chr(10) + u"        return" + chr(10),
     u"    if declared > 0:" + chr(10) + u"        return" + chr(10)
     + u"    return" + chr(10), DOCS),
]

# ===================================================================================
# RETIRED 2026-10-03 by the owner's stand-alone direction, kept rather than deleted.
#
#     ("A DEPENDENCY IS REQUIRED AND NEVER ORDERED", ABOUT,
#      u"    <li>brrainz.harmony</li>" + chr(10), u"", REGISTER),
#     ("A DEPENDENCY CARRIES NO NAME TO SHOW THE PLAYER", ABOUT,
#      u"      <displayName>Harmony</displayName>" + chr(10), u"", REGISTER),
#     ("a dependency gives the player no way to obtain it", ABOUT,
#      u"      <steamWorkshopUrl>steam://url/CommunityFilePage/2009463077</steamWorkshopUrl>"
#      + chr(10), u"", REGISTER),
#     ("the package is declared as its own dependency", ABOUT, FIRST, SELF_ROW + FIRST, REGISTER),
#     ("Core is declared as a mod dependency", ABOUT, FIRST, CORE_ROW + FIRST, REGISTER),
#     ("the same dependency is declared twice", ABOUT, FIRST, FIRST + chr(10) + FIRST, REGISTER),
#
# `FIRST`, `SELF_ROW` and `CORE_ROW` above are kept with them for the same reason.
# ===================================================================================
'''

NEW_CONSTS = (
    'ABOUT = "Mod/Rimrooms - Async Industries/About/About.xml"' + NL
    + 'REGISTER = "tools/check-register-compliance.py"' + NL
    + '# The stand-alone direction moved the risk from the declaration to what gets claimed in'
    + NL
    + "# its place, so this suite now reaches the doc checker as well as the register one." + NL
    + 'DOCS = "tools/check-doc-conformance.py"' + NL
    + 'DOCS_CHECKER = DOCS' + NL
    + 'ARCHITECTURE = "docs/ARCHITECTURE.md"'
)

text = io.open(PATH, encoding="utf-8").read()
problems = 0

if "THE LOAD ORDER LOSES A FORMER DEPENDENCY" in text:
    print("already re-aimed")
    sys.exit(0)

old_consts = ('ABOUT = "Mod/Rimrooms - Async Industries/About/About.xml"' + NL
              + 'REGISTER = "tools/check-register-compliance.py"')
if text.count(old_consts) != 1:
    print("CONSTANTS BLOCK NOT UNIQUE (%d)" % text.count(old_consts))
    problems += 1
else:
    text = text.replace(old_consts, NEW_CONSTS)
    print("added the DOCS and ARCHITECTURE targets")

start = text.find("PLANTS = [")
end = text.find("]" + NL, start)
if start < 0 or end < 0 or end <= start:
    print("COULD NOT BOUND THE PLANTS LIST")
    problems += 1
else:
    text = text[:start] + NEW_PLANTS + text[end + 2:]
    print("replaced the plant list: 7 retired, 7 new")

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

io.open(PATH, "w", encoding="utf-8", newline=NL).write(text)
print("wrote %s" % PATH)
