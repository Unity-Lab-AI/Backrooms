# -*- coding: utf-8 -*-
"""NOW.md for 0.12.40-dev.

Every anchor asserted before anything is written, one write at the end. Measured, not carried:

    tip            c1b8abb -> this commit, tree clean
    C# files       192   (git ls-files src --others --cached --exclude-standard | grep -c '\\.cs$')
    package         88
    checkers        12   (11 tools/check-*.py + tools/research/audit-gate0.py)
    proofs          37
    assembly       7641035476D6...30C4, read from the live build after the determinism run
    queue           54 open / 48 partial / 480 done
    items            7 numbered entries, of which 1 is a closed record -> 6 genuine
    versions       all four sites agree on 0.12.40-dev (About, csproj, README, doc-conformance)
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

# --------------------------------------------------------------------------- state
STATE = [
    (u"| Published | **0.12.39-dev**.", u"| Published | **0.12.40-dev**."),
    (u"| Build | **191 C# files, 87 package files**",
     u"| Build | **192 C# files, 88 package files**"),
    (u"SHA-256 `13031FCBAE5FB6238197D3EB36AD6B2AE0042B91E4B5F05E0AFF6252A736EFCD`",
     u"SHA-256 `7641035476D6D2A2A5FF326E258E1B5D24E32DD581FFD2A683994B55C2D230C4`"),
    (u"| Proofs | **THIRTY-SIX** in `.local/register/proof-*.py`.",
     u"| Proofs | **THIRTY-SEVEN** in `.local/register/proof-*.py`."),
    (u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 59 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 48 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 475 done
```""",
     u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 54 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 48 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 480 done
```"""),
    (u"### The package is staged, and THIRTEEN checkpoints behind",
     u"### The package is staged, and FOURTEEN checkpoints behind"),
    (u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is "
     u"**0.12.39-dev** —\n**thirteen checkpoints of work are not in the game folder.** "
     u"Re-stage before any launch:",
     u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is "
     u"**0.12.40-dev** —\n**fourteen checkpoints of work are not in the game folder.** "
     u"Re-stage before any launch:"),
    (u"## What shipped this session, 0.7.1 → 0.12.39",
     u"## What shipped this session, 0.7.1 → 0.12.40"),
]

# --------------------------------------------------------------------------- session table
TABLE_ANCHOR = (u"| 0.12.39 | **The register said don't patch, so the hook is a sentence** — "
                u"reading the integration approach first made the obvious build the wrong one. "
                u"Five rows, a read-only readout, and **row 791's absolute got a checker**")
TABLE_NEW = TABLE_ANCHOR + (
    u"\n| 0.12.40 | **The words a player reads** — five rows in one batch. **Architect, the "
    u"first surface row 821 names, opened from nowhere in this package**, and the handoff said "
    u"it was already reachable. The company tab was second from the right. `docs/PLAYING.md`, "
    u"a help pane with the glossary, and Core's own generator supplying the keyboard binding "
    u"for one XML field")

# --------------------------------------------------------------------------- the next batch
BATCH_START = u"## DO THIS FIRST — the player-facing words batch"
BATCH_END = u"## What shipped this session"

BATCH_NEW = u"""## DO THIS FIRST — the two systems left

**Rows 728 and 1031–1033.** Everything still unbuilt that is a *system* rather than housekeeping,
and the two are related enough to batch: one decides what a crew takes with them, the other decides
what the company wants brought back.

| Row | What |
|---|---|
| 728 | **crew composition and cargo planner** — skill, health, weight and window checks, ready and unready reasons, a cost preview |
| 1031–1033 | **quests and missions for odd goods**, as distinct from contracts, plus a player-facing surface for open odd demands |

Four things to settle before writing anything:

1. **Row 728 carries its own constraint, verbatim: *"must not own connection existence"*.** The
   planner may refuse a *crew*; it may never be the thing that decides whether a connection can
   exist. Six reasons already stop a gate and a seventh arrived at 0.12.38-dev — the planner is an
   eighth opinion about a crew, not about the machine.
2. **Most of the checks already exist somewhere.** `StaffDebrief` has nine refusals,
   `Dispatch` already gates on readiness, and the expedition pane already previews. **Read those
   first** — nine rows this session turned out already built, and twice a row's own *"confirmed
   absent by grep"* was itself the defect.
3. **The owner asked for *"quests and missions and contracts"*, and contracts shipped at
   0.7.3-dev.** So 1031–1033 is the other two thirds of one direction, not a new idea. Core's
   `QuestScriptDef` is the obvious surface and it is worth establishing what a Core-only,
   Harmony-free mod can actually reach through it before designing anything.
4. **The odd-demand surface is the small half and is nearly free.** Offers and settlements are
   already recorded events; the Operations pane simply does not list the open ones. Check that
   before building a system for it.

**Then the housekeeping batch**, which is all that is left after these: 1054, 206 and 302, 1268 and
1269, and 1286–1290.

---

"""

# --------------------------------------------------------------------------- the open count
COUNT_OLD = (u"**10 genuine build items**, counted at 0.12.39-dev, listed in full under **What is "
             u"left** below. **Five rows closed this batch** — 764, 765, 766, 784 and 791, all "
             u"one family. **Seventeen rows across the last four batches.**")
COUNT_NEW = (u"**6 genuine build items**, counted at 0.12.40-dev, listed in full under **What is "
             u"left** below. **Five rows closed this batch** — 1193, 1220, 821, 822 and 833, all "
             u"one family. **Twenty-two rows across the last five batches.**\n\n"
             u"**The counting command overstates by one, and it is worth knowing why.** It counts "
             u"numbered entries under *What is left*, and **entry 1 is a closed record kept there "
             u"deliberately so nobody rebuilds row 761**. Seven entries, six of them open. Read "
             u"the list rather than the number.")

COUNT2_OLD = u"**10 genuine build items**, counted rather than estimated:"
COUNT2_NEW = (u"**7 numbered entries below, 6 of them genuine build items** — entry 1 is a closed "
              u"record. Counted rather than estimated:")

# --------------------------------------------------------------------------- the standing warning
WARN_OLD = (u"and across\n0.12.24 → 0.12.39 **the measurement was the defect at least twelve "
            u"separate times while the code\nwas fine.** Five from 0.12.24 → 0.12.33 are "
            u"tabulated below; the seven since are:\n\n"
            u"| Measured wrong | The truth |\n|---|---|\n")
WARN_NEW = (u"and across\n0.12.24 → 0.12.40 **the measurement was the defect at least fourteen "
            u"separate times while the code\nwas fine.** Five from 0.12.24 → 0.12.33 are "
            u"tabulated below; the nine since are:\n\n"
            u"| Measured wrong | The truth |\n|---|---|\n"
            u"| **this file said `OpenNativeTab` already opens Architect** | it did not and never "
            u"had. `grep -rn \"Architect\" --include=*.cs src` returned **nothing at all**. The "
            u"stale measurement was in the handoff itself, which is the worst place for one |\n"
            u"| a colour guard that matched `new Color(` | `new UnityEngine.Color(...)` walked "
            u"past it — and the qualified spelling is the one a file without the `using` would "
            u"have to write |\n")

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

# The batch section is replaced wholesale rather than patched.
if text.count(BATCH_START) != 1:
    problems.append("batch start anchor: %d" % text.count(BATCH_START))
if text.count(BATCH_END) != 1:
    problems.append("batch end anchor: %d" % text.count(BATCH_END))

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
    u"""4. **The player-facing how-to for gameplay and systems.** Rows 1193, 1220. `docs/HOWTO.md`
    documents the **build**, not play. Written **once**, for both the repo and the site.
""",
    u"""5. **The native menu remap** into the company-first layout. Row 821. Twelve panes and reason codes
    ship; this is the Architect/Work/Assign/Research integration.
""",
    u"""6. **Tutorial, glossary, keyboard paths, contrast and scale.** Rows 822, 833. Localization
    completeness is already measurable: `check-keyed-strings.py` reports every declared key
    resolving.
""",
)
for block in CLOSED:
    if text.count(block) != 1:
        print("CLOSED-ITEM ANCHOR PROBLEM: %d occurrence(s) of %r" % (text.count(block),
                                                                      block[:60]))
        raise SystemExit(1)
for block in CLOSED:
    text = text.replace(block, u"", 1)

# The whole "Surfaces and words" heading goes with them -- all three of its entries closed.
HEADING = u"### Surfaces and words\n\n"
if text.count(HEADING) != 1:
    print("HEADING ANCHOR PROBLEM: %d" % text.count(HEADING))
    raise SystemExit(1)
text = text.replace(HEADING, u"", 1)

# Renumber what is left, in place, so the numbers and the count agree.
start = text.index(u"### Systems still unbuilt")
end = text.index(u"### Cannot close before the game runs once")
block = text[start:end]
numbers = re.findall(r"^(\d+)\. ", block, re.M)
for new_index, old_index in enumerate(numbers, start=1):
    block = re.sub(r"^%s\. " % old_index, u"\x00%d. " % new_index, block, count=1, flags=re.M)
block = block.replace(u"\x00", u"")
text = text[:start] + block + text[end:]

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("NOW.md updated for 0.12.40-dev: %d numbered entries remain" % len(numbers))
