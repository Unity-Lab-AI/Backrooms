
---

## 2026-09-29 — The M6 release gate, and the first change to a Gate 0 decision (docs only)

### Verbatim owner requests

> *"what is the m6 gate use askme question lets get past it"*

Then the three answers to the question set that produced:

> **M6 path:** *"Split M6a / M6b, build all of M6a"*

> **Fixtures:** *"option 2 and option 3"*

> **Release:** *"option 3 and remeber we dont have other peoples saves we just publish it all and update it as we go fixing bugs"*

### Why a question was the right move rather than building

- [x] **M6 is the only major that cannot be closed by building.** Six of its ten rows need the owner's launch; the exit condition was a distribution decision; and one row contained an instruction that contradicted a standing rule. None of that is resolvable by writing code, and guessing any of the three would have produced work that had to be torn out.
- [x] **Two of the three answers overrode standing policy**, which is why all three are recorded as numbered decisions rather than notes. **This is the first change to a D-numbered Gate 0 decision since they were recorded on 2026-09-27.**

### What was decided

- [x] **Decision 19 — M6 splits into M6a and M6b.** M6a is the four rows that close without a launch: package and def validation, the mod page and provenance, the tag-and-archive ritual, and the buildable part of the fresh-start checklist. M6b is the six that structurally cannot. **Bookkeeping only — no row dropped, reworded, renumbered or moved out of Phase 6.** It exists because one major reading 0% hid that nearly half of it was buildable today.
- [x] **Decision 20 — one scoped exception to the no-tests rule, and it is deferred.** The owner selected *both* the automated-fixtures option and the defer option. Read together: automated fixtures are **authorised**, replacing the manual-checklist-only reading, **and none is written until after the first launch**, so their content follows observed failures rather than guessed ones. The exception covers the five subjects in that one row and nothing else. `CONTRIBUTING.md`'s rule is unchanged everywhere else in the repo, and that is stated in `CONTRIBUTING.md` itself so a later session cannot read the exception as general permission.
- [x] **Decision 21 — D1 superseded. Public Steam Workshop is the first distribution target.** The owner's reason answers the exact objection put to them: the risk raised against this option was that first real-world validation would happen in public against other players' saves, and **there are no other players' saves.** Nothing has shipped, so there is no installed base to break.

### The two consequences that matter, both recorded rather than assumed

- [x] **The no-compatibility-claim rule is now the main protection, not a formality.** D1's option B text stays binding. The mod page may claim the Core-only solo path and must claim **no** profile row, **no** DLC interaction and **no** RWT co-op without a recorded result — and **200 of the 294 dispositions are still provisional.** Publishing early makes this rule stricter, not looser.
- [x] **Save migration becomes a standing obligation from the first published version.** It was a release-day checkbox on the assumption that publication came last. From publication onward there *are* other people's saves.

### Two defects surfaced while counting, both named rather than quietly fixed

- [ ] **The master backlog stopped at 0.4.2-dev.** It is granular for research — 81 rows on Phase 0 — and coarse for code: the entire cross-map work engine, 31 work families, 23 deployments, containment, emergence, the kill switch and gate servicing, **27 shipped versions**, all sit under one unchecked row. A raw count therefore reads ~12% on code while the source tree went from 78 files to 120. Recorded in `ROADMAP.md` beside the number so nobody reads it as truth.
- [ ] **`disposition_stance()` counts a negated "required" as Required.** 14 of the 17 rows in that bucket say the opposite — row 88 *"not required for materials/progression"*, row 101 *"never a required input"*, row 259 *"do not make it a required Rimrooms path"*. Only Harmony (1), Core (4) and Vanilla Expanded Framework (14) are genuinely required, so **82% of the bucket is wrong.** Same class of bug as the classifier-priority defect that silently moved 59 mods. Row 196 — RimWorld Together, the co-op backbone — additionally falls through to `Unclassified`.

### Documents updated in the same change

Thirteen, no code: `GATE_0_DECISIONS.md` (D1 superseded with its own anchored section; decisions 19–21; decision-log row rewritten), `ROADMAP.md` (M6 → M6a/M6b, decision log, critical-path diagram, **and the stale status table — it still read 0.4.2-dev, 78 C# files, 73 package files, 133/121**), `TODO.md` (M6 split, three owner answers verbatim, six consequence rows), `PREPRODUCTION_AND_IMPLEMENTATION_TODO.md` (Phase 6 note, the 2026-09-27 D1 row annotated rather than edited), `DEFERRED.md`, `CONTRIBUTING.md`, `AGENTS.md`, `HOWTO.md`, `ARCHITECTURE.md`, `SKILL_TREE.md`, `TECHNICAL_ARCHITECTURE.md`, `MOD_INTEGRATION_PLAN.md`, `research/PREPRODUCTION_ACCEPTANCE_STANDARD.md`.

### Verification performed

Docs-only: zero `.cs` and zero `.xml` files changed, so no build, no version bump and no `CHANGELOG.md` entry — nothing player-facing moved. `audit-gate0.py` **PASS with zero errors**: 482 markdown files, 3,048 local links and 202 fragments all resolving, including the new `#d1-superseded-…` anchor now referenced from five documents; 294 mod rows, 294 review records, 914 relationship records, 0 open Gate 0 boxes. Every D1 assertion in the repository was grepped and reconciled — four documents still stated the superseded content after the first pass and were fixed. No attribution strings added. No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files changed: 0. Package files changed: 0. Docs updated: 13.
Owner directions captured verbatim: 4 (the question, plus three answers).
**Gate 0 decisions changed: 1 — the first since 2026-09-27.** Standing rules given a scoped exception: 1, deliberately narrow and written into the rule's own file.
Defects surfaced and named: 2 (master-backlog granularity; the register's negated-"required" classifier, 82% of that bucket wrong).
Stale doc facts corrected: the roadmap status table, three versions and 42 source files out of date.
Still open and named: the player-facing how-to for the gameplay and systems, the M6a rows now unblocked, and the two defects above.
