# NOW — handoff after compaction

**Single-focus tracker.** Distinct from the three-tier ledger:

| File | Grain |
|------|-------|
| `docs/ROADMAP.md` | MAJOR — phases and milestones |
| `docs/TODO.md` | MINOR — the working queue, **every owner direction verbatim** |
| `docs/DECOMPOSED.md` | smallest execution units |
| **`docs/NOW.md`** (this file) | **the handoff** |
| `docs/FINALIZED.md` | permanent archive |
| ~~`docs/DEFERRED.md`~~ | **CLOSED. Zero open rows. Never add one.** |

LAW #0 applies: owner words go in verbatim, everywhere.

---

## Active

**Nothing in flight. Tree clean, everything published.** Written deliberately for the session after a compaction.

### State

| | |
|---|---|
| Branch | `feature/connected-colony-portals` |
| Published | **0.8.8-dev**, commit read back below |
| Remotes | `forgejo` + `github`, all four refs each at the same commit |
| Build | **154 C# files, 92 package files**, zero warnings, zero errors |
| Assembly | SHA-256 `5CFCA1C8EEEF139655B91ED421942FC58B33F683B03F1590F0607810A75C643B`, reproduced by two clean recompiles |
| Checkers | four, all passing |
| Register | `outputs/rimrooms-async-industries-register-2026-09-27/…Register.html` — **open the HTML**, not the xlsx |
| Game launches | **none, ever** |

### The standing instruction

> *"you are NOT to stop untill i tell you to stop or you reach the completeion of the mod's build out"*

Chain checkpoints. Do not finish one and wait.

---

## What shipped this session, 0.7.1 → 0.8.7

| Version | What |
|---|---|
| 0.7.2 | **Odd origin** — anything out of a coordinate is marked, never stacks with ordinary |
| 0.7.3 | **Odd supply contracts** — buyers who want goods *by origin* |
| 0.7.4 | **Three-state origin** + the **Backrooms mood pressure** (−1 → −10 over a real hour, shelter scored from real surroundings) |
| 0.7.5 | **Company bonds** — 15 denominations, 10 → one quadrillion, greedy payout, credit beacon |
| 0.7.6 | **The corporate trader** — tiered catalogue behind research + contract + credit locks |
| 0.7.7 | **The exchange** — odd ×1.5, ordinary ×0.85; withdrawal as paper |
| 0.7.8 | **The yellow rooms**, and depth as an axis |
| 0.7.9 | **Fourteen room archetypes**, capability-driven |
| 0.8.0 | **The escalation ladder**, paced on colony wealth |
| 0.8.1 | **The construction echo** — the place copies what you build |
| 0.8.2 | **Inhabitants** — wanderers, missing, dead, psychotic, survivors |
| 0.8.3 | **Survivor recruitment** + the encounter cap as a recorded progression step |
| 0.8.4 | **Anomaly events** + the echo reaching items |
| 0.8.5 | **Colonist echoes** + **holding undiscovered inhabitants** (fog of war) |
| 0.8.6 | **Room shape echoes** and hallways |
| 0.8.7 | **Coherence decay** + tech scaling |
| 0.8.8 | **Gate connection history** — per-gate address book, editable and clearable |

---

## What is left, in order

1. **Dialling from the connection history.** 0.8.8-dev records and manages the address book; selecting an entry to *re-open* that coordinate is the natural next step, and is a separate interaction with its own permission checks.
2. **The unknown-def-field checker.** Written, **proved broken, removed rather than shipped.** See the warning below — start from the verified parts.
3. **Facilities** — larger functional spaces, distinct from rooms and corridors.
4. **A player-facing how-to.** Now **~12 interacting systems** with no written explanation of how they fit. Overdue.
5. **The four area types across a gate** (`Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear`, `Area_PollutionClear`).
6. **A world tile the branch does not hold** — needs a world object and generated map.
7. **The three starting sites** (`SCENARIOS.md` specifies all three).
8. **The 1990s period and universe factions.**
9. **M2 existing-content replacement** — the save break is declared, so Defs can now be deleted with no migration.
10. M1 step 5, M3 breadth, M5 interface, M6a/M6b.

---

## Invariants — do not break these

Each is a real defect or a pinned fact.

1. **`PortalTraversalPolicy` is the only traversal chokepoint.** An inhabitant may never decide anything about a gate. Survivor recruitment works *because* joining makes them a colonist — it does not special-case a gate.
2. **Two halves of validation, never merged.** A candidate predicate runs against an explicit `Map`; never a pawn-specific native probe about a map the worker is not on.
3. **Remote forbidden checks use the *faction* overload.**
4. **A bounded search that ran out of budget is *pending*, never "no route".**
5. **Every bounded scan is a rotating window, never a prefix.**
6. **Two work givers per family** — high-priority continue, low-priority plan.
7. **Never infer "no local work" from a priority number.**
8. **One commitment per worker**, across every record kind.
9. **Nothing is ever `playerForced`.** **No quantity is hardcoded.**
10. **No new gameplay ThingDef, PawnKindDef, art or audio.** Match by *capability*. A `FactionDef`, `ThoughtDef` or mechanics def is permitted.
11. **Zero throwing def lookups.** `GetNamedSilentFail` everywhere.
12. **Natural gates have no timer, operator, power or close command — and no address book.**
13. **A Backrooms coordinate has no outside**; its roof is never removable; its interior is fully strippable.
14. **A candidate half must ask whether the *target* can take the work.**
15. **A def referencing DLC carries `MayRequire`.** The C# guard is not enough.
16. **The register is generated output; the HTML one is the register.**
17. **A prisoner can never cross a gate; a *secure* slave can.**
18. **The topology is an unbounded alternation** of world maps and coordinates.
19. **Never trust a remembered list against shipped game data. Enumerate.**
20. **Owner words have been mod names twice.** Search the register before reading a phrase as flavour.
21. **A D-numbered Gate 0 decision can change.** Read the sheet. D1 changed 2026-09-29.
22. **The no-tests rule has exactly one exception** (decision 20), written into `CONTRIBUTING.md` itself. Never widen it.
23. **Do not trust a progress percentage from a row count here.** The master backlog is granular for research and coarse for code.
24. **Nothing is deferred.** Build it, queue it in `TODO.md` (`[T]` if it needs a launch), or ask. **Never add a row to `DEFERRED.md`.**
25. **Depth 1 is sacred.** The yellow rooms are fixed, sparse and never deranged. The wrongness is travelled toward.
26. **Sort any candidate list ordinally before rolling.** Def load order varies with the mod list; unsorted, the same seed produces different output on another machine. This has been a live trap three times.
27. **Anything saved that feeds the layout fingerprint must be snapshotted, not read live.** Layout is re-planned to verify a saved graph; reading current colony state there makes a coordinate fail its own check.
28. **Every threat honours: readable warning, learnable rule, a countermeasure, no unavoidable instant failure.** The threshold room is excluded from every event and every inhabitant.
29. **Undiscovered inhabitants are held.** Needs topped up, rot held, while fogged. Discovery starts their clock.
30. **A natural gate has no address book and may not dial.** Enforced by `IsDesignated` on the gate gizmos, not by a second check — adding one would imply the first is unreliable.
31. **When an existing guarantee already covers a new requirement, say so and rely on it.** Twice this session a requirement needed no new code: the natural-gate rule, and survivor recruitment obeying the traversal chokepoint rather than special-casing it.

---

## The warning that matters most right now

**A checker that silently passes everything is worse than no checker — it manufactures confidence.**

The unknown-def-field check was written this session, every part verified correct in isolation, and **the assembled function still reported nothing against a deliberately planted bad field.** It was removed rather than shipped.

Two things follow:

- **Sanity-test every checker by breaking something and confirming it fails.** Three checker gaps were found this session; each was proved by breaking it first.
- The same rule caught a real risk in the layout derangement: if the clamp were wrong, every candidate would be rejected, the planner would fall back to plain, and **the feature would look like it worked while doing nothing.** That was proved offline across all 100 size combinations rather than trusted.

---

## Standing method

- **Read the prep work first.** The 294 per-mod reviews under `research/reviews/mods/` carry verified facts. The register has recovered misread owner references in one query.
- **A TODO item carries all its related work.** Do the item and everything it needs.
- **At a fork: ask immediately with multiple choice and a write-in**, and keep building around it. But **search the register first**.
- **State what already works before building it again.**
- **Name what is not done, in `TODO.md`, in the same checkpoint.** Every "not done" in this session's records was named before the owner asked.

## Read these first

1. `docs/NOW.md` — this file.
2. `docs/TODO.md` — every owner direction verbatim.
3. `docs/GATE_0_DECISIONS.md` — D1–D9 **and** decisions 13–25. D1 changed.
4. `docs/implementation/CONNECTED_WORK_CORE_API.md` — pinned Core facts.
5. `docs/research/WORK_TYPE_COVERAGE_AUDIT.md` — all 23 work types.
6. `docs/PUBLISHING.md` — the cascade. Follow it literally.

## The checkpoint ritual

1. Read every file in full before editing.
2. `powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1` — zero warnings. It refuses if csproj and `About.xml` versions disagree, so bump both.
3. `CHANGELOG.md` in plain player-facing language.
4. Implementation record under `docs/implementation/`.
5. Ledger: `TODO.md`, `NOW.md`, `FINALIZED.md` (verbatim owner words), `ROADMAP.md`.
6. **All four checkers**: `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `research/audit-gate0.py`.
7. **Determinism**: delete `obj/` and `bin/`, rebuild **twice**, hashes must match. An incremental rebuild proves nothing.
8. Commit once atomically; cascade to `Prep`, `Develop`, `Main` on **both** remotes; **read back all eight refs**.

## Gotchas learned the hard way

- **XML comments cannot contain `--`.** Hit **twice**. `check-package-integrity.py` now names the rule and the line.
- **Bash heredocs mangle `\n` and break on apostrophes**, silently aborting a patch script. Hit **five times**. Use Write/Edit.
- **A failed `assert` in a patch script means nothing was written** — the write comes last.
- `git` index lock goes stale; `rm -f .git/index.lock` and retry.
- **`cd` inside a Bash call persists.** Absolute paths.
- Package manifests are UTF-8 **with BOM** — `encoding="utf-8-sig"`.
- Decompile with `.local/tools/ilspycmd.exe -t <FullTypeName>`. **Empty output means the type name was wrong.**
- C# 7.3: no target-typed conditionals.
- **A def field emitted in XML that no class declares is ignored silently at load.** Cost two checkpoints once.
- Core's `StockGenerator_Category` has **all-private fields** — it cannot be usefully subclassed.
- `GenRecipe.PostProcessProduct` is **private static** — a bench bill cannot stamp a per-instance value. Mint in the recipe worker instead.
- `SetTerrain` **clears** the colour grid. Apply colour after, then dirty the mesh.
- `CompFlickable.SwitchIsOn` has a **public setter** — use vanilla's own switch for light failure.

## Blocked on the owner

**Nothing.** That status does not exist here. Runtime rows are `[T]` and gate no work.
