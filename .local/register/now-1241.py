# -*- coding: utf-8 -*-
"""NOW.md for 0.12.41-dev. The last two gameplay systems close; only housekeeping is left.

Measured, not carried:

    C# files       196
    package         89
    checkers        12
    proofs          38
    assembly       5670CA7C784A...70C69, read from the live build after the determinism run
    queue           50 open / 47 partial / 485 done
    items            5 numbered entries, of which 1 is a closed record -> 4 genuine
    versions       all four sites agree on 0.12.41-dev
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

STATE = [
    (u"| Published | **0.12.40-dev**.", u"| Published | **0.12.41-dev**."),
    (u"| Build | **192 C# files, 88 package files**",
     u"| Build | **196 C# files, 89 package files**"),
    (u"SHA-256 `7641035476D6D2A2A5FF326E258E1B5D24E32DD581FFD2A683994B55C2D230C4`",
     u"SHA-256 `5670CA7C784A5E11B2A50DBEC461B469D015727A8B453711FB35E938C7270C69`"),
    (u"| Proofs | **THIRTY-SEVEN** in `.local/register/proof-*.py`.",
     u"| Proofs | **THIRTY-EIGHT** in `.local/register/proof-*.py`."),
    (u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 54 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 48 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 480 done
```""",
     u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 50 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 47 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 485 done
```"""),
    (u"### The package is staged, and FOURTEEN checkpoints behind",
     u"### The package is staged, and FIFTEEN checkpoints behind"),
    (u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is "
     u"**0.12.40-dev** —\n**fourteen checkpoints of work are not in the game folder.** "
     u"Re-stage before any launch:",
     u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is "
     u"**0.12.41-dev** —\n**fifteen checkpoints of work are not in the game folder.** "
     u"Re-stage before any launch:"),
    (u"## What shipped this session, 0.7.1 → 0.12.40",
     u"## What shipped this session, 0.7.1 → 0.12.41"),
]

TABLE_ANCHOR = (u"| 0.12.40 | **The words a player reads** — five rows in one batch. **Architect, "
                u"the first surface row 821 names, opened from nowhere in this package**, and the "
                u"handoff said it was already reachable. The company tab was second from the "
                u"right. `docs/PLAYING.md`, a help pane with the glossary, and Core's own "
                u"generator supplying the keyboard binding for one XML field")
TABLE_NEW = TABLE_ANCHOR + (
    u"\n| 0.12.41 | **The last two systems** — **every check row 728 asks for was already "
    u"enforced and not one was named**: five conditions across three people, all reported as "
    u"`RR_Exp_InvalidCrew`. And a mission is a contract **plus survey work at depth**, because "
    u"the odd mark carries no coordinate and stacks merge, so nothing can verify *where* a good "
    u"came from")

BATCH_START = u"## DO THIS FIRST — the two systems left"
BATCH_END = u"## What shipped this session"

BATCH_NEW = u"""## DO THIS FIRST — housekeeping is all that is left

**Every gameplay system in the queue is built.** What remains is four rows of bookkeeping, and
they are genuinely worth doing rather than filler: two of them are about the register and the
documents being *true*, which is the property this project leans on hardest.

| Row | What | Shape of the work |
|---|---|---|
| 1054 | reconcile 0.5.0–0.7.1 into the master backlog | reading and editing, no code |
| 206, 302 | the register retro sweep's last seven families | **medical, world operations, cargo, hospitality, materials, visitor economy, staff psychology** |
| 1268, 1269 | the campaign economy workbook has no generator, and the register preview PNGs depict a superseded layout | a generator, and regenerated images |
| 1286–1290 | the TOS and official-versions compliance pass | reading Ludeon's terms and the Steam agreements against the package |

Three things to settle:

1. **The retro sweep is the one with teeth.** `check-register-compliance.py` already refuses a
   shipped feature whose family was never consulted, so the seven unswept families are seven
   places the LAW has been satisfied on paper. **Query each one before reading anything else** —
   `python tools/register-query.py family <name>` — and expect at least one to change something,
   because every previous sweep did.
2. **1268 is a generator, so it is code, and it is the only code left.** The workbook is
   `docs/CAMPAIGN_ECONOMY_MODEL.md`'s numbers; a generator that derives them from the defs is
   what stops the document drifting from the build. Check whether `tools/` already has something
   close before writing a new one.
3. **1286–1290 cannot be answered by reading this repository.** It is Ludeon's modding terms and
   the Steam agreements against what the package actually does — and
   `docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md` already exists, so **read it first and establish
   what is stale rather than starting a new position.**

**After these four, the only rows left in the queue are the ~8 that cannot close before the game
runs once and the 9 the owner excluded.** That is the end of the build.

---

"""

COUNT_OLD = (u"**6 genuine build items**, counted at 0.12.40-dev, listed in full under **What is "
             u"left** below. **Five rows closed this batch** — 1193, 1220, 821, 822 and 833, all "
             u"one family. **Twenty-two rows across the last five batches.**\n\n"
             u"**The counting command overstates by one, and it is worth knowing why.** It counts "
             u"numbered entries under *What is left*, and **entry 1 is a closed record kept there "
             u"deliberately so nobody rebuilds row 761**. Seven entries, six of them open. Read "
             u"the list rather than the number.")
COUNT_NEW = (u"**4 genuine build items, and none of them is a gameplay system.** Counted at "
             u"0.12.41-dev, listed in full under **What is left** below. **Five rows closed this "
             u"batch** — 728, 1028, 1031, 1032 and 1033. **Twenty-seven rows across the last six "
             u"batches.**\n\n"
             u"**Every system the queue asked for is built.** What is left is a backlog "
             u"reconciliation, the register retro sweep's last seven families, an economy "
             u"workbook generator, and the compliance pass.\n\n"
             u"**The counting command overstates by one, and it is worth knowing why.** It counts "
             u"numbered entries under *What is left*, and **entry 1 is a closed record kept there "
             u"deliberately so nobody rebuilds row 761**. Five entries, four of them open. Read "
             u"the list rather than the number.")

COUNT2_OLD = (u"**7 numbered entries below, 6 of them genuine build items** — entry 1 is a closed "
              u"record. Counted rather than estimated:")
COUNT2_NEW = (u"**5 numbered entries below, 4 of them genuine build items** — entry 1 is a closed "
              u"record. Counted rather than estimated:")

WARN_OLD = (u"and across\n0.12.24 → 0.12.40 **the measurement was the defect at least fourteen "
            u"separate times while the code\nwas fine.** Five from 0.12.24 → 0.12.33 are "
            u"tabulated below; the nine since are:\n\n"
            u"| Measured wrong | The truth |\n|---|---|\n")
WARN_NEW = (u"and across\n0.12.24 → 0.12.41 **the measurement was the defect at least fifteen "
            u"separate times while the code\nwas fine.** Five from 0.12.24 → 0.12.33 are "
            u"tabulated below; the ten since are:\n\n"
            u"| Measured wrong | The truth |\n|---|---|\n"
            u"| a public `OpeningPowerDrawWatts` written for the cost preview | **one already "
            u"existed** in `GateFootprint.cs`, footprint-scaled and discounted by "
            u"`RR_Cap_EfficientAperture`. The compiler caught it, which is the cheapest way this "
            u"ever gets caught — and the existing one was *better*: the raw prop is not what any "
            u"gate above 1×1 draws |\n")

EDITS = list(STATE) + [
    (TABLE_ANCHOR, TABLE_NEW),
    (COUNT_OLD, COUNT_NEW),
    (COUNT2_OLD, COUNT2_NEW),
    (WARN_OLD, WARN_NEW),
]

text = original
problems = []
for old, _ in EDITS:
    count = text.count(old)
    if count != 1:
        problems.append("%d occurrence(s) of %r" % (count, old[:74]))
if text.count(BATCH_START) != 1:
    problems.append("batch start: %d" % text.count(BATCH_START))
if text.count(BATCH_END) != 1:
    problems.append("batch end: %d" % text.count(BATCH_END))
if problems:
    for problem in problems:
        print("ANCHOR PROBLEM: %s" % problem)
    raise SystemExit(1)

for old, new in EDITS:
    text = text.replace(old, new, 1)

start = text.index(BATCH_START)
end = text.index(BATCH_END)
text = text[:start] + BATCH_NEW + text[end:]

# --------------------------------------------------------------------------- drop closed items
CLOSED = (
    u"""2. **Crew composition and cargo planner** with skill, health, weight and window checks, ready and
   unready reasons, and a cost preview. Row 728. *"must not own connection existence"*.
""",
    u"""3. **Quests and missions for odd goods**, as distinct from contracts - contracts shipped 0.7.3-dev
   and the owner asked for *"quests and missions and contracts"*. Plus a player-facing surface for
   open odd demands: offers and settlements are recorded events and the Operations pane does not
   list them. Rows 1031, 1032, 1033.
""",
)

# The em-dash and quote characters in the file are not ASCII, so anchor on a stable prefix and
# take the whole numbered block rather than matching the body verbatim.
def drop_numbered(body, prefix):
    start = body.index(prefix)
    # Up to the next numbered entry or the next heading, whichever comes first.
    rest = body[start + len(prefix):]
    match = re.search(r"\n(?=\d+\. \*\*|### )", rest)
    end = start + len(prefix) + (match.start() + 1 if match else len(rest))
    return body[:start] + body[end:]


start = text.index(u"### Systems still unbuilt")
end = text.index(u"### Cannot close before the game runs once")
block = text[start:end]

for prefix in (u"2. **Crew composition and cargo planner**",
               u"3. **Quests and missions for odd goods**"):
    if block.count(prefix) != 1:
        print("CLOSED-ITEM ANCHOR PROBLEM: %d for %r" % (block.count(prefix), prefix))
        raise SystemExit(1)
for prefix in (u"2. **Crew composition and cargo planner**",
               u"3. **Quests and missions for odd goods**"):
    block = drop_numbered(block, prefix)

numbers = re.findall(r"^(\d+)\. ", block, re.M)
for new_index, old_index in enumerate(numbers, start=1):
    block = re.sub(r"^%s\. " % old_index, u"\x00%d. " % new_index, block, count=1, flags=re.M)
block = block.replace(u"\x00", u"")
text = text[:start] + block + text[end:]

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("NOW.md updated for 0.12.41-dev: %d numbered entries remain" % len(numbers))
