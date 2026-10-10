# -*- coding: utf-8 -*-
"""NOW.md handoff protocol for 0.12.39-dev.

**Every anchor is asserted before anything is written, and the write happens once.** That is not
style, it is the failure this session hit twice: a patch script whose `sub()` throws part way
leaves the file untouched, so the edits *before* the throw are lost silently -- six state edits
vanished at 0.12.38-dev and eight at 0.12.39-dev, both found only by grepping afterwards.

Measured rather than carried, all of it:

    tip          303e722, tree clean
    C# files     191    (git ls-files src --others --cached --exclude-standard | grep -c '\\.cs$')
    package       87
    checkers      12    (11 tools/check-*.py + tools/research/audit-gate0.py)
    proofs        36
    assembly     13031FCB...EFCD, read from the live build
    queue         59 open / 48 partial / 475 done, one consistent pattern
    items         10    (counted out of the file's own list, not remembered)
    versions     all three sites agree on 0.12.39-dev

The three stale things this fixes, in order of how much they would cost a fresh session:

  1. **"Done since the last handoff" described 0.12.24 -> 0.12.33** -- six checkpoints stale, which
     under-reports what is done and over-reports what is left. That is the actively harmful one.
  2. **The session table stopped at 0.12.33**, so six checkpoints of work had no row.
  3. **"staged, and one checkpoint behind" said one. It is thirteen.**
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

# --------------------------------------------------------------------------- #
# 1. Six session table rows
# --------------------------------------------------------------------------- #
TABLE_ANCHOR = (u"| 0.12.33 | **Surgery cannot cross, and three things were invisible** — row 227 "
                u"closed **by proof**, plus the door crossing order, the coordinate band readout "
                u"and a sale confirmation |")

TABLE_NEW = TABLE_ANCHOR + u"""
| 0.12.34 | **Fifteen more reasons to walk through a gate** — the eleven DLC container givers and the four `Art` painting givers. **Core forbids all eleven from moving anything between maps**, so invariant 55 was never engaged; and a clamp was silently overwriting six shipped priorities |
| 0.12.35 | **Containment you can see from the other side of a gate** — **Core's four containment alerts all read `Find.CurrentMap`**, so the gap was never "no warning" but "no warning about the maps you are not looking at". Plus the security procedure and the alarm |
| 0.12.36 | **Roofs, snow, and reporting in** — **six rows in one batch.** The area rows closed themselves because somebody had written down *why* they were uncovered; quarantine turned out to be the debrief, because this package has no `HediffDefs` at all |
| 0.12.37 | **Every coordinate in the game was made of wood** — one hardcoded material for every stuffable fixture in every room. Plus the **twelfth checker**, which caught itself twice, and the stance classifier fixed to its own row's prediction |
| 0.12.38 | **A gate read no damage at all** — it could be shot to twelve per cent and still hold a connection. **Seven of row 725's nine subsystems were already built** under different names. Reliability is a record, not a dice roll |
| 0.12.39 | **The register said don't patch, so the hook is a sentence** — reading the integration approach first made the obvious build the wrong one. Five rows, a read-only readout, and **row 791's absolute got a checker**"""

# --------------------------------------------------------------------------- #
# 2. The staging note
# --------------------------------------------------------------------------- #
STAGE_OLD = u"### The package is staged, and one checkpoint behind"
STAGE_NEW = u"### The package is staged, and THIRTEEN checkpoints behind"

STAGE_BODY_OLD = (u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is "
                  u"**0.12.39-dev**. Re-stage\nbefore any launch:")
STAGE_BODY_NEW = (u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is "
                  u"**0.12.39-dev** —\n**thirteen checkpoints of work are not in the game folder.** "
                  u"Re-stage before any launch:")

# --------------------------------------------------------------------------- #
# 3. The "what is left" heading, which still carried its original date
# --------------------------------------------------------------------------- #
LEFT_OLD = u"## What is left, in order — rewritten 0.12.34-dev, measured not carried"
LEFT_NEW = (u"## What is left, in order — maintained through 0.12.39-dev, measured not carried\n\n"
            u"**Re-measure this list before trusting it.** It has been correct at every checkpoint "
            u"since 0.12.33-dev because each batch edited it, but the count at the top of the file "
            u"is a command for a reason: the item numbers are renumbered on every close and a "
            u"stale count is the most expensive thing this file can hold.")

# --------------------------------------------------------------------------- #
# 4. The already-built tally, which said four and is now nine
# --------------------------------------------------------------------------- #
ALREADY_OLD = (u"**The raw open count overstates.** Rows closed by work that shipped the same day "
               u"keep their `[ ]`\nuntil somebody flips them, and four separate rows this session "
               u"turned out to be **already built** —\n227 (medical routes), 308 (contradictory "
               u"accounts), 493 (the recorder fold) and 1266's neighbours.\n**Check a row against "
               u"the code before building for it.** That habit has saved more work this\nsession "
               u"than it cost.")
ALREADY_NEW = (u"**The raw open count overstates, and the reason is worth the paragraph.** Rows "
               u"closed by work\nthat shipped the same day keep their `[ ]` until somebody flips "
               u"them — and **NINE separate rows\nthis session turned out to be already built, "
               u"already true, or answered by Core**:\n\n"
               u"| Row | What it actually was |\n|---|---|\n"
               u"| 227 | surgery across a gate **cannot be built** — `Bill_Medical`'s patient *is* "
               u"the bill giver |\n"
               u"| 308 | the contradiction was already computed and thrown away |\n"
               u"| 493 | the recorder fold had been decided fourteen checkpoints earlier |\n"
               u"| 1266 | **Core forbids all eleven givers from moving anything between maps** |\n"
               u"| 98 | six reasons can stop a gate and **not one reads an adjacent cell** |\n"
               u"| 99 | the row's premise was wrong — a gate link has **no distance or LOS check** |\n"
               u"| 1011 | depth, band, wealth and seeding all already there |\n"
               u"| 1101 | a coordinate's floors were **ordinary layerable Core terrain** all along |\n"
               u"| 725 | **seven of its nine subsystems** existed under different names |\n\n"
               u"**CHECK A ROW AGAINST THE CODE BEFORE BUILDING FOR IT.** That habit is the single "
               u"highest-value\nthing in this file. It has saved more work this session than every "
               u"other practice combined, and\ntwice the row's own *"
               u"“confirmed absent by grep”* was the thing that was wrong.")

# --------------------------------------------------------------------------- #
# 5. The standing warning, brought to seven instances
# --------------------------------------------------------------------------- #
WARN_OLD = (u"**SUSPECT YOUR OWN MEASUREMENT FIRST.** A search that finds nothing is not evidence, "
            u"and across\n0.12.24 → 0.12.33 **the measurement was the defect five separate times "
            u"while the code was fine:**")
WARN_NEW = (u"**SUSPECT YOUR OWN MEASUREMENT FIRST.** A search that finds nothing is not evidence, "
            u"and across\n0.12.24 → 0.12.39 **the measurement was the defect at least twelve "
            u"separate times while the code\nwas fine.** Five from 0.12.24 → 0.12.33 are tabulated "
            u"below; the seven since are:\n\n"
            u"| Measured wrong | The truth |\n|---|---|\n"
            u"| the queue count, **twice** (90 vs 86, then an item count of 19 and 13 vs 20 and 12) "
            u"| the list is renumbered on every close, so the count must come from the file |\n"
            u"| **six** shipped work-giver priorities above the clamp | **seven** — the pattern was "
            u"`<WorkGiverDef>` and missed `<WorkGiverDef MayRequire=…>` |\n"
            u"| **five** ways a gate can stop working | **six** — I forgot the deliberate cutoff. "
            u"Then a seventh arrived and the proof kept passing, because it read one file of a "
            u"**partial class** |\n"
            u"| a replant of the historical `maxTechLevel` defect **passed** | 0.8.7-dev fixed it by "
            u"**adding the field to the class**, so the field is valid now. The plant was wrong, not "
            u"the checker |\n"
            u"| `CompHoldingPlatformTarget` flagged as an ungated expansion defName | it is a **comp "
            u"type** in the always-present base assembly |\n"
            u"| `MULTIPLAYER.md` reported as missing a sentence it contains | the document is "
            u"**hard-wrapped** and a literal phrase search cannot cross a newline |\n"
            u"| a fault-plant run reporting **17 of 17 caught** | **worthless** — a syntax error made "
            u"the proof fail unconditionally, so every plant registered as caught |\n\n"
            u"The five earlier ones:")

EDITS = [
    (TABLE_ANCHOR, TABLE_NEW),
    (STAGE_OLD, STAGE_NEW),
    (STAGE_BODY_OLD, STAGE_BODY_NEW),
    (LEFT_OLD, LEFT_NEW),
    (ALREADY_OLD, ALREADY_NEW),
    (WARN_OLD, WARN_NEW),
]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:72]))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("handoff: %d edits applied in one write" % len(EDITS))
