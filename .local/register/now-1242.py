# -*- coding: utf-8 -*-
"""NOW.md for 0.12.42-dev. The build closes: every queue row that can close without a launch is
closed.

Measured, not carried:

    C# files       196
    package         89
    checkers        13   (12 tools/check-*.py + tools/research/audit-gate0.py)
    proofs          39
    assembly       CFAB1B96356D...44582
    queue           42 open / 45 partial / 495 done
    master          66 open / 190 done   (was 122 / 134)
    items            1 numbered entry, and it is a closed record -> 0 genuine
"""
import io
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, "docs", "NOW.md")

original = io.open(PATH, encoding="utf-8").read()

STATE = [
    (u"| Published | **0.12.41-dev**.", u"| Published | **0.12.42-dev**."),
    (u"| Build | **196 C# files, 89 package files**",
     u"| Build | **196 C# files, 89 package files** (unchanged this checkpoint: no C# was added)"),
    (u"SHA-256 `5670CA7C784A5E11B2A50DBEC461B469D015727A8B453711FB35E938C7270C69`",
     u"SHA-256 `CFAB1B96356D0F7BD7B40A19C22951E577E4597B2ADAFCD56A706F24A3244582`"),
    (u"| Proofs | **THIRTY-EIGHT** in `.local/register/proof-*.py`.",
     u"| Proofs | **THIRTY-NINE** in `.local/register/proof-*.py`."),
    (u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 50 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 47 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 485 done
```""",
     u"""```
grep -c '^\\s*- \\[ \\]' docs/TODO.md     # 42 open
grep -c '^\\s*- \\[~\\]' docs/TODO.md    # 45 partial
grep -c '^\\s*- \\[x\\]' docs/TODO.md    # 495 done
```

**And the master backlog, which row 1054 said understated the build by roughly thirty points.**
It was **56**. `docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md` went from **122 open / 134 done**
to **66 open / 190 done**, every flip naming the checkpoint that closed it, every original word
kept, and **not one runtime-acceptance row touched**."""),
    (u"### The package is staged, and FIFTEEN checkpoints behind",
     u"### The package is staged, and SIXTEEN checkpoints behind"),
    (u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is "
     u"**0.12.41-dev** —\n**fifteen checkpoints of work are not in the game folder.** "
     u"Re-stage before any launch:",
     u"The copy in the owner's Local Mods folder is **0.12.26-dev**; the build is "
     u"**0.12.42-dev** —\n**sixteen checkpoints of work are not in the game folder.** "
     u"**This is now the single most useful thing anybody can do with this repository.** "
     u"Re-stage before any launch:"),
    (u"## What shipped this session, 0.7.1 → 0.12.41",
     u"## What shipped this session, 0.7.1 → 0.12.42"),
    (u"| Checkers | **TWELVE**, all passing.",
     u"| Checkers | **THIRTEEN**, all passing. The thirteenth, `check-compliance.py`, is the "
     u"compliance table made executable: a dated table of mechanical checks is the same defect "
     u"as a dated count, and that one had been read as current for **thirty-six checkpoints** "
     u"with three of its rows no longer true. **Two of its own rules caught it before any plant "
     u"did** — the licence check flagged a comment that *denies* the GPL applies, and the "
     u"assembly check read the wrong manifest key and reported *\"0 assemblies, all from the "
     u"official install\"*."),
]

TABLE_ANCHOR = (u"| 0.12.41 | **The last two systems** — **every check row 728 asks for was "
                u"already enforced and not one was named**: five conditions across three people, "
                u"all reported as `RR_Exp_InvalidCrew`. And a mission is a contract **plus "
                u"survey work at depth**, because the odd mark carries no coordinate and stacks "
                u"merge, so nothing can verify *where* a good came from")
TABLE_NEW = TABLE_ANCHOR + (
    u"\n| 0.12.42 | **The housekeeping, which was not housekeeping** — the compliance table "
    u"had been *\"re-run rather than trusted\"* for **thirty-six checkpoints without being "
    u"re-run**, and three of its rows had stopped being true. The register's last five families "
    u"were all honoured, so **their rules became checks**. Row 1054 said the master backlog "
    u"understated the build by thirty points; **it was 56**")

BATCH_START = u"## DO THIS FIRST — housekeeping is all that is left"
BATCH_END = u"## What shipped this session"

BATCH_NEW = u"""## DO THIS FIRST — re-stage the package, then launch it

**The build is done.** Every queue row that can close without the game running is closed. There is
nothing left to build that does not first need somebody to press play.

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools/stage-mod.ps1 -UpdateExisting
```

The staged copy in Local Mods is **0.12.26-dev** against a build of **0.12.42-dev** — **sixteen
checkpoints**. Staging backs up the existing folder, hash-verifies every file against the build
manifest, and records `ProfileChanged = false; GameLaunched = false`. **It never touches the mod
list and never starts the game.**

**Only the owner launches, through RimSort.** That is a standing instruction and nothing below
changes it.

### What a first launch settles, in order of what it unblocks

| Rows | What only a launch can answer |
|---|---|
| 810 | duplicate def and patch collisions in the exact 294 profile — a conflict has to be reproducible to fix |
| 890, 891 | exchange-rate and catalogue balance — *"neither has any play behind it"* |
| 212, 742 | performance and profiling under a long save |
| 812 | the user-facing compatibility report — *"cannot honestly state a tested order before anything has been tested"* |
| 975 | whether the creepy-versus-normal balance lands — *"a play question"* |
| 835, 849 | the invalid-state matrix half, and the release tag |

**Read `docs/PLAYING.md` first.** It is the play document written at 0.12.40-dev, and its opening
caveat is the whole frame for a first session: every instruction in it is a structural claim about
the code, because nobody has played this. **Where it and the game disagree, the game is right.**

**The most likely first-launch failures, in the order they would appear**, each already carrying a
named refusal rather than silence: the company failing to register headquarters (the Overview pane
offers to retry), a coordinate failing to generate (the Atlas pane offers to re-address), and a
colony control unavailable in the world view. Nine gate refusals and ten crew-planner refusals all
name themselves. **If something fails silently, that is the bug worth reporting** — this package
was built so that it should not be possible.

---

"""

COUNT_OLD = (u"**4 genuine build items, and none of them is a gameplay system.** Counted at "
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
COUNT_NEW = (u"**ZERO build items left.** Counted at 0.12.42-dev. **Ten rows closed this "
             u"batch** — 206, 302, 1054, 1268, 1269 and 1286–1290. **Thirty-seven rows across "
             u"the last seven batches.**\n\n"
             u"**The one numbered entry under *What is left* is a closed record**, kept "
             u"deliberately so nobody rebuilds row 761. Everything else in that section is "
             u"either *cannot close before the game runs once* or *excluded by the owner*.\n\n"
             u"**So the answer to the heading has changed.** The build is done. What is not done "
             u"is **play**: about 8 rows need the game to run once, and the package in the game "
             u"folder is sixteen checkpoints stale. **Re-staging and a first launch is now the "
             u"only work that unblocks anything.**")

COUNT2_OLD = (u"**5 numbered entries below, 4 of them genuine build items** — entry 1 is a closed "
              u"record. Counted rather than estimated:")
COUNT2_NEW = (u"**1 numbered entry below, and it is a closed record.** Zero genuine build items. "
              u"Counted rather than estimated:")

HEADING_OLD = u"## Is it done? NO, and the shape of what is left"
HEADING_NEW = (u"## Is it done? THE BUILD IS. The play is not, and nothing else can start until "
               u"it does")

EDITS = list(STATE) + [
    (TABLE_ANCHOR, TABLE_NEW),
    (COUNT_OLD, COUNT_NEW),
    (COUNT2_OLD, COUNT2_NEW),
    (HEADING_OLD, HEADING_NEW),
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
start = text.index(u"### Housekeeping with teeth")
end = text.index(u"### Cannot close before the game runs once")
text = text[:start] + text[end:]

# Renumber whatever remains in the section, so the numbers and the count agree.
start = text.index(u"### Systems still unbuilt")
end = text.index(u"### Cannot close before the game runs once")
block = text[start:end]
numbers = re.findall(r"^(\d+)\. ", block, re.M)
for new_index, old_index in enumerate(numbers, start=1):
    block = re.sub(r"^%s\. " % old_index, u"\x00%d. " % new_index, block, count=1, flags=re.M)
block = block.replace(u"\x00", u"")
text = text[:start] + block + text[end:]

io.open(PATH, "w", encoding="utf-8", newline="").write(text)
print("NOW.md updated for 0.12.42-dev: %d numbered entries remain (closed records only)"
      % len(numbers))
