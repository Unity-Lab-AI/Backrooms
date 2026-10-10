# -*- coding: utf-8 -*-
"""The decision records say what the package now declares. Same commit as the code.

`.claude/CONSTRAINTS.md §DOCS BEFORE PUSH`. Three living documents stated the
opposite of what `About.xml` says after this change, and `docs/TODO.md` named all
three in advance: *"It supersedes owner decision D3/D4 as amended 2026-10-01 ...
recorded in GATE_0_DECISIONS.md, ROADMAP.md §Decision log and ARCHITECTURE.md
§B1. Those three say the opposite of this direction and all three are rewritten
in the same commit as the work."*

**LAW #0: nothing superseded is deleted.** Every earlier owner quote stays
exactly as written and is marked superseded in place, with the new direction
quoted beside it. A decision log that erases the decision it replaced cannot be
audited, and the owner has already had one reading of theirs struck rather than
removed this week for the same reason.
"""
import io
import sys

NL = chr(10)

D3_OLD = (
    "| D3 | **CHANGED by the owner 2026-10-01: every mod in the collection is a hard "
    "dependency.**"
)
D4_OLD = (
    "| D4 | **CHANGED by the owner 2026-10-01: all five expansions are hard dependencies.**"
)

SUPERSEDE_D3 = (
    "| D3 | **SUPERSEDED BY THE OWNER 2026-10-03: the package declares no hard dependencies at "
    "all.** *\"and something i dont like that is going to take major major work and should be "
    "added to the todo : rework mod to not need any depeancie mods\"*, and the same day *\"and im "
    "reiterating the fact that we need to fix the depancy list so that its accurate to what is "
    "required and we hope to have the mod as a complete stand alone\"*. `About.xml`'s "
    "`modDependencies` block is gone as of 0.12.86-dev; **all 293 entries were already in "
    "`loadAfter`**, so the load order is unchanged and only the requirement wall went. "
    "**The earlier reading is kept below rather than deleted.** ~~CHANGED by the owner "
    "2026-10-01: every mod in the collection is a hard dependency.~~"
)

SUPERSEDE_D4 = (
    "| D4 | **SUPERSEDED BY THE OWNER 2026-10-03, by the same direction as D3: the five "
    "expansions are not declared requirements either.** They came out of `modDependencies` with "
    "the other 288 and remain in `loadAfter`. This returns the five to the position D4 held when "
    "it was first recorded on 2026-09-27 — *\"Core-only campaign; all five DLC optional detected "
    "content\"* — which the 2026-10-01 amendment had reversed. **The graceful guards still "
    "stay**, and the conditional-layer work in Major M4 is what makes declaring nothing honest "
    "rather than merely quiet. **The earlier reading is kept below rather than deleted.** "
    "~~CHANGED by the owner 2026-10-01: all five expansions are hard dependencies.~~"
)

EDITS = [
    # ------------------------------------------------------------- GATE_0_DECISIONS.md
    ("docs/GATE_0_DECISIONS.md", D3_OLD, SUPERSEDE_D3),
    ("docs/GATE_0_DECISIONS.md", D4_OLD, SUPERSEDE_D4),

    # --------------------------------------------------------------------- ROADMAP.md
    ("docs/ROADMAP.md",
     "| D3 | 2026-09-27 | All 294 profile rows are the research/test target; only Core + "
     "Harmony/RWT required for co-op; everything else optional;",
     "| D3 | 2026-09-27, **amended 2026-10-01, SUPERSEDED 2026-10-03** | "
     "**The package declares no hard dependencies.** Owner, 2026-10-03: *\"rework mod to not "
     "need any depeancie mods\"* and *\"we hope to have the mod as a complete stand alone\"*. "
     "The 2026-10-01 amendment that made every collection member a declared requirement is "
     "struck; the 293 entries are `loadAfter` only, which is what they already were. "
     "Original row, kept: All 294 profile rows are the research/test target; only Core + "
     "Harmony/RWT required for co-op; everything else optional;"),

    ("docs/ROADMAP.md",
     "| D4 | 2026-09-27 | Core-only campaign; all five DLC optional detected content; "
     "validate the all-five profile |",
     "| D4 | 2026-09-27, **amended 2026-10-01, SUPERSEDED BACK 2026-10-03** | "
     "Core-only campaign; all five DLC optional detected content; validate the all-five "
     "profile. **This is the live reading again**: the 2026-10-01 amendment declaring the five "
     "expansions as hard dependencies is struck by the stand-alone direction, and the five came "
     "out of `modDependencies` with everything else at 0.12.86-dev. |"),

    # ----------------------------------------------------------------- ARCHITECTURE.md
    ("docs/ARCHITECTURE.md",
     "- **DLC:** isolated `LoadFolders.xml` + package-guarded patches per expansion. All five "
     "are **declared requirements**; the guards exist so an absent one degrades instead of "
     "throwing, not to advertise that absence is supported.",
     "- **DLC:** isolated `LoadFolders.xml` + package-guarded patches per expansion. All five "
     "are **optional detected content** as of 0.12.86-dev — owner, 2026-10-03: *\"rework mod to "
     "not need any depeancie mods\"*, *\"we hope to have the mod as a complete stand alone\"*. "
     "~~All five are declared requirements~~. The guards exist so an absent one degrades instead "
     "of throwing; **that is still not a claim that absence is supported** — the Core-only path "
     "has to be proved row by row, which is the open half of the stand-alone work and is not "
     "closed by removing a declaration."),

    # -------------------------------------------------- COMPLIANCE_AND_OFFICIAL_VERSIONS.md
    # True again, and its evidence line was wrong in the other direction: `loadAfter` is 294
    # entries, not Core alone. A compliance row whose evidence does not match the file is the
    # kind of row that gets believed once and then found out.
    ("docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md",
     "| No required third-party mod | **Pass** — zero `modDependencies`, `loadAfter` is "
     "`Ludeon.RimWorld` only | grep of `About.xml`: 0 matches for `modDependencies` / "
     "`incompatibleWith` |",
     "| No required third-party mod | **Pass** — zero `modDependencies` as of 0.12.86-dev. "
     "`loadAfter` carries **294** entries, which is an ordering preference and not a "
     "requirement: a mod manager sorts by it and never demands it | `About.xml`: 0 matches for "
     "`modDependencies` / `incompatibleWith`; 294 `loadAfter` entries, of which 293 were hard "
     "dependencies until the stand-alone direction |"),
]

problems = 0
touched = {}

for path, old, new in EDITS:
    if path not in touched:
        touched[path] = io.open(path, encoding="utf-8").read()
    text = touched[path]
    if new[:60] in text and old not in text:
        print("already applied in %s" % path.split("/")[-1])
        continue
    if text.count(old) != 1:
        print("TARGET NOT UNIQUE (%d) in %s: %r"
              % (text.count(old), path.split("/")[-1], old[:76]))
        problems += 1
        continue
    touched[path] = text.replace(old, new)
    print("%-38s amended %s" % (path.split("/")[-1], old[:44]))

if problems:
    print("%d problem(s); nothing written" % problems)
    sys.exit(1)

for path in touched:
    io.open(path, "w", encoding="utf-8", newline=NL).write(touched[path])
    print("wrote %s" % path)
