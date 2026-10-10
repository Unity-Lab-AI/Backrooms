# -*- coding: utf-8 -*-
"""Refresh the drifted sections of NOW.md for 0.12.98-dev.

The file is a one-record handoff and several batches of targeted edits had left three things
stale: the battery counts, the remotes row, and a *What changed* section still headed 0.12.94-dev.
"""
import io
import sys

NL = chr(10)
P = "docs/NOW.md"
t = io.open(P, encoding="utf-8").read()


def swap(old, new, label):
    global t
    if t.count(old) != 1:
        raise SystemExit("NOT UNIQUE (%d): %s" % (t.count(old), label))
    t = t.replace(old, new, 1)


swap("- **At publication, once:** 21 checkers → 58 proofs → 32 plant suites.",
     "- **At publication, once:** 21 checkers → 59 proofs → 34 plant suites → "
     "`check-plant-residue.py`. **Then stage, then `export-public-repo.py --push`, then commit, "
     "then the ten-ref cascade.**",
     "battery line")

swap("- **Batch size is 10–12 closed rows.** 0.12.93 closed nine and noted four; 0.12.94 closed "
     "**six**, every one of a single owner direction.",
     "- **Batch size is 10–12 closed rows.** 0.12.96 closed **ten** before the battery ran once, "
     "which is the cadence the owner asked for: *\"get a bunch done berfore battery and stage and "
     "cascade\"*.",
     "batch line")

swap("| Remotes | **all TEN refs level** — `forgejo` 5 of 5, `github` 5 of 5. Forgejo caught up "
     "2026-10-05 after four commits down |",
     "| Remotes | **TWELVE refs, all level** — this repository 10 (`forgejo` 5, `github` 5) plus "
     "the mod-only pair 2. Forgejo caught up 2026-10-05 after four commits down |",
     "remotes row")

START = t.index("## What 0.12.94-dev changed")
END = t.index("## THE NEXT THING")
CHANGED = NL.join([
"## What 0.12.95 through 0.12.98-dev changed",
"",
"**Four publications, and the pattern across all of them is the same:** almost nothing needed",
"building. What needed doing was **checking what was already built**, and every check that found",
"something found it in a place nobody had looked.",
"",
"1. **THE MOD TOLD EVERY PLAYER IT NEEDS 294 MODS, AND IT NEEDS NONE.** `About.xml` has declared zero dependencies since 0.12.86-dev while **five live documents** said the opposite — including `About.xml`'s **own description**, the install page, the mods page, the README and `PLAYING.md`. The install page listed all five expansions **and Harmony** as *Required*. Found by generating a readme from that text and reading it: it said *\"Needs no other mod and no expansion\"* two lines above a section demanding five expansions.",
"2. **ONE PAGES DEPLOY, AND IT IS THE PUBLIC MOD REPOSITORY.** Pages here is **404 and never was enabled** — the direction described the live state. What was wrong was three documents still telling a reader to switch it on, which is worse than stale: **somebody does it.** Now refused by a checker, with the 2026-10-01 answer recorded as superseded rather than quietly dropped.",
"3. **NOTHING REFERENCES THE BUILD REPOSITORIES**, and it did when the rule was given: the published wiki sent anyone wanting the source, or wanting to report a bug, **to the repository that holds the work ledger.**",
"4. **THE STAND-ALONE GUARANTEE'S MISSING HALF.** The checker proved the package only *names* safe things; it never proved the lookups **degrade**. Now: **152 silent-fail results, every one guarded.** The rule was wrong three times first — 65 findings of which 56 were innocent, then 9 more on correct code, then two safe through `??`.",
"5. **A MULTIPLAYER PAGE THAT NEVER NAMED THE MULTIPLAYER MOD.** It described the shape and withheld the thing that provides it. Rewritten from register row 196: **RimWorld Together**, what it does, that it needs Harmony and we do not, and that everyone needs the same mod list.",
"6. **TEN ROWS THAT WERE BUILT AND UNGUARDED**, including the whole stranded-crew guarantee — where the feared defect **never existed**: `LostPawnRegister` stores *names*, not pawns, and `DeinitAndRemoveMap` is called from exactly one place, a player action.",
"7. **A ROOM'S PILLARS WERE THE WRONG MATERIAL.** The wall ring used the room's material; the pillars inside it used the level band's. Stone walls, wooden columns. **Nothing asserted the material**, so it drifted.",
"8. **A PROOF WITH 34 CLAIMS AND NO PLANTS.** The recorder fold passed from the day it was written and nobody had watched it refuse. `RecorderGap` — the thing it turns on — was in **no proof at all**.",
"9. **AND STAGING IS TWELVE REFS, NOT TEN.** `PUBLISHING.md` — the cascade authority — said nothing about the mod-only repository, so the step lived in memory. Now in the procedure, in the handoff, and **receipted by the tool itself**.",
"",
])
t = t[:START] + CHANGED + t[END:]

io.open(P, "w", encoding="utf-8", newline=NL).write(t)
print("NOW.md refreshed: battery, batch, remotes and the what-changed section")
