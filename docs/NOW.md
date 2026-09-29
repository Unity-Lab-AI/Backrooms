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

LAW #0 applies: owner words go in verbatim, everywhere. **This is now enforced** — see invariant #69.

---

## Active

**Nothing in flight. Tree clean, everything published, no half-finished task.** Written deliberately for the session after a compaction.

### State

| | |
|---|---|
| Branch | `feature/connected-colony-portals` |
| Published | **0.11.0-dev**. This handoff is the tip; `git log --oneline -1` is authoritative and the eight refs below match it. |
| Remotes | `forgejo` + `github`, all four refs each at that commit |
| Build | **160 C# files, 83 package files**, zero warnings, zero errors |
| Assembly | SHA-256 `21E6775A25CCADA65E49F5DD543AB7F04C9B815720399648A6F2FB83A45C9D45`, reproduced by two clean recompiles |
| Checkers | **eight**, all passing |
| Register | `python tools/register-query.py families\|family <x>\|find <x>\|row <n>` — **the HTML is the register**, never the xlsx |
| Readable HTML | `python tools/make-readable-html.py` → `outputs/readable/index.html` |
| Game launches | **none, ever** |

### The standing instruction

> *"you are NOT to stop untill i tell you to stop or you reach the completeion of the mod's build out"*

Chain checkpoints. Do not finish one and wait.

---

## What shipped this session, 0.7.1 → 0.11.0

| Version | What |
|---|---|
| 0.7.2–0.7.7 | **The economy** — odd origin, supply contracts, pressure, bonds, corporate trader, exchange |
| 0.7.8–0.8.1 | **The look and the ladder** — yellow rooms, archetypes, escalation, construction echo |
| 0.8.2–0.8.5 | **Inhabitants** — wanderers, survivors, anomalies, colonist echoes, fog-of-war holding |
| 0.8.6–0.8.8 | **Shape** — room echoes, hallways, coherence decay, the gate address book |
| 0.8.9 | **Bringing a gate up is work** — operator-driven spin-up with familiarity; gates are blue |
| 0.9.0 | **A gate is a door and nothing else** — 8 legacy defs retired, package 92 → 79 |
| 0.9.1 | **One kind of gate** — 68 dead branches collapsed, a vestigial power model gone, −112 lines |
| 0.9.2 | **A gate has a size** — 1×1 to 2×3; Core's own `OrnateDoor` gives 1×2 free |
| 0.9.3 | **Everything you can look at says what it is** — info cards calibrated to Core's practice |
| 0.9.4 | **What a gate's size lets through** — animals cross; width decides what fits |
| 0.9.5 | **They follow you** — at `Band.Hostile` an inhabitant hunts to the threshold |
| 0.9.6 | **It came through with them** — a bounded, named exception to the founding rule |
| 0.9.7 | **Some places are bigger than a room** — facilities as contiguous runs |
| 0.9.8 | **One tech tree, different starting points** — the tree is derived, not declared |
| 0.9.9 | **The beacon had nothing left to do** — first field-gear retirement |
| 0.10.0 | **The documents say what is true** — sixth checker, 28 stale claims in 10 living docs |
| 0.10.1 | **LAW #0, made checkable** — 10 owner directions found unrecorded |
| 0.10.2 | **One set of words** — gate / connection / threshold, enforced |
| 0.10.3 | **Something is not where you left it** — silent between-visit displacement |
| 0.10.4 | **The register checked backwards** — a LAW, a query tool, a real defect; plus a readable description |
| 0.10.5 | **Every surface the game speaks through** — a seventh checker measured against Core per display surface, and the alerts readout, which this mod used none of |
| 0.10.6 | **The documents use the mod's own words** — the vocabulary and the wall rule reach the reader-facing set; two superseded rules found while reading |
| 0.10.7 | **The survey tag becomes a glow pod** — marker types with colours, three caps removed, and an outcome that could never fire |
| 0.10.8 | **A gate's facility is the equipment linked into it** — shelves, analysers and cabinets link like furniture to a bed, but far, through walls and by hand |
| 0.10.9 | **What you have learned is what you can build** — projects require completed logs; the ladder had one rung and a declared top tier of four |
| 0.11.0 | **The only clock is the gate** — the campaign chart, two offer clocks retired, seven prep documents corrected, eighth checker |

---

## What is left, in order

Content set → gate model → generator → scenarios → docs. One direction, no backtracking.

1. **Finish the field gear (rest of M2).** All four replacements were decided at the fork; **none are built**:
   - **Survey tag → Core `GlowPod`.** Carried, deployed, and it lights the room it marks. **No cap** — *"a backrooms instance can have 100s of rooms"*. **Colour is semantic**: mod-defined marker types (route home, cleared, danger, supply cache, unexplored lead), each its own colour. `CompGlower.GlowColor` has a **public setter** backed by a saved per-instance `glowColorOverride`, and `CompProperties_Glower.colorPickerEnabled` turns on RimWorld's own picker — **so this needs no new UI**. Verified by decompiling.
   - **Evidence case → a designated HQ `Shelf` as the archive.** The book is carried; custody completes when it arrives. Same designation pattern as the gate console and the laboratory bench.
   - **Field recorder → the book is the recorder.** One Core `TextBook`: carried in blank, written in the field, carried home as the evidence.
   - Then `RR_QuietPursuer`, the five `RR_*Staff` PawnKinds and their recipes.
2. **The adjacent-door-run fallback** — 1×3 and 2×3 by binding one gate across a run of adjacent 1×1 Core doors, for players without Doors Expanded.
3. **New-game playability** — the world tile the branch does not hold, and **the other two starting sites** (`SCENARIOS.md`). **Blocked behind item 1**: the existing scenario still grants the field gear being retired.
4. **The player-facing how-to.** Written **once**, for both the repo and the site.
5. **Still unbuilt from the prep material** — *"contradictory accounts"* from a returning crew; staff **prior exposure**; the ladder's *"respond to openings in settlements"*.
6. **The unknown-def-field checker** — written, **proved broken, removed rather than shipped**. Start from the verified parts.
7. **The 1990s period and universe factions**; the four area types across a gate; M1 step 5; M3 breadth; M5 interface; M6a/M6b.
8. **Public release** — site, Workshop page, collection. Full plan: [`PUBLIC_RELEASE_PLAN.md`](PUBLIC_RELEASE_PLAN.md). **Correctly last**, and three decisions there are the owner's.
9. **Continue the register retro sweep.** Swept: animals, security, spatial construction, expedition logistics. Not yet: facilities, storage, furniture, commerce, contracts, power, medical, interface, world operations.
10. Reconcile 0.5.0–0.7.1 into the master backlog; fix the register's `disposition_stance()` negation bug.

---

## Invariants — do not break these

Each is a real defect or a pinned fact. Numbering is historical; gaps are deliberate.

### The gate and crossing

1. **`PortalTraversalPolicy` is the only traversal chokepoint.** An inhabitant may never decide anything about a gate.
2. **Two halves of validation, never merged.** A candidate predicate runs against an explicit `Map`.
3. **Remote forbidden checks use the *faction* overload.**
4. **A bounded search that ran out of budget is *pending*, never "no route".**
5. **Every bounded scan is a rotating window, never a prefix.**
6. **Two work givers per family** — high-priority continue, low-priority plan.
7. **Never infer "no local work" from a priority number.**
8. **One commitment per worker**, across every record kind.
9. **Nothing is ever `playerForced`. No quantity is hardcoded.**
10. **No new gameplay ThingDef, PawnKindDef, art or audio.** Match by *capability*. A `FactionDef`, `ThoughtDef` or mechanics def is permitted.
11. **Zero throwing def lookups.** `GetNamedSilentFail` everywhere.
12. **Natural gates have no timer, operator, power, close command or address book, and may not dial.** Enforced by `IsDesignated`, not a second check.
13. **A Backrooms coordinate has no outside**; its roof is never removable; its interior is fully strippable.
14. **A candidate half must ask whether the *target* can take the work.**
15. **A def referencing DLC carries `MayRequire`.**
17. **A prisoner can never cross a gate; a *secure* slave can.**
18. **The topology is an unbounded alternation** of world maps and coordinates.
32. **There is exactly one way a laboratory gate opens** — through the spin-up. Every entry point routes into it.
40. **A gate's width and its footprint are different numbers.** Width decides what fits; footprint decides what it costs.
41. **Throughput is never capped.** A wide gate gets more doorway cells, never a quota. There is no counter, deliberately.
43. **Core ships `OrnateDoor` at 2×1** and `Building_MultiTileDoor` to drive it; Anomaly adds `SecurityDoor`.
47. **A connection has one width, in both directions.** Per-endpoint measuring traps an animal in the Backrooms.
48. **Company work and player orders are two different rules.** `TravellerFailureKey` is colonists-only; `OrderedCrossingFailureKey` admits player animals. **Both refuse a drafted pawn.**
53. **Incursion is the one named exception to the founding rule**, bounded on five axes: live opening, `Band.Hostile`, `PortalWindowTier >= 1`, it must fit, once per opening.
54. **`MayApproachThresholdForTraversal` must stay false for everything, forever.** Incursion works *because* nothing is drawn to a gate.
55. **A transfer that can lose a pawn is a corruption, not a threat.** Preflight fully, then move, and restore on failure.

### Generation and threats

16. **The register is generated output; the HTML one is the register.**
25. **Depth 1 is sacred.** The yellow rooms are fixed, sparse, never deranged. Higher number = deeper (owner-confirmed).
26. **Sort any candidate list ordinally before rolling.** A live trap three times.
27. **Anything saved that feeds the layout fingerprint must be snapshotted, not read live.**
28. **Every threat honours: readable warning, learnable rule, a countermeasure, no unavoidable instant failure.** The threshold room is excluded from every event and inhabitant.
29. **Undiscovered inhabitants are held.** Discovery starts their clock.
50. **`Band.Hostile` is the "deeper levels" threshold** — *"the space stops being forgiving"*. Do not invent a second number.
51. **Below `Band.Hostile` a hostile holds ground; at it, it hunts.**
52. **`LordJob_AssaultColony`'s first parameter is the ASSAULTER's faction.** Passing the player's compiles cleanly and no checker catches it.
57. **A facility is a contiguous run of 2–4 rooms sharing one archetype**, anchored at the lowest index and **stored nowhere**.
58. **Coherence is what wrongness needs.** Do not "fix" facilities by making deep coordinates tidier.
74. **A horror mechanic that fires every time is a mechanic, not horror.** Revisit displacement was weakened from 100% to 66.7% deliberately.
75. **Ownership is the test for "did the player make this".** Generation places with no faction.

### Method

19. **Never trust a remembered list against shipped game data. Enumerate.**
20. **Owner words have been mod names twice.** Search the register before reading a phrase as flavour.
21. **A D-numbered Gate 0 decision can change.** D1 changed 2026-09-29.
22. **The no-tests rule has exactly one exception** (decision 20), in `CONTRIBUTING.md`. Never widen it.
23. **Do not trust a progress percentage from a row count here.**
24. **Nothing is deferred.** Build it, queue it in `TODO.md`, or ask. **Never add a row to `DEFERRED.md`.**
31. **When an existing guarantee already covers a new requirement, say so and rely on it.**
33. **Never tie a penalty rate to a flat constant without proving it against the real stat range.** Express it as a fraction of the observed rate.
34. **Ask at the fork; never flag it for later.** *"dopnt flag shit!!! ask me then and there"*. A flagged question becomes orphaned work.
35. **`ThingComp.ForceColor()` is the tint hook**; a painted colour wins over it. `Notify_ColorChanged()` drops Core's cached graphic.
36. **A checker that reads only one kind of source has a blind side.** Ask both directions, of every source.
37. **Retired content is archived, never deleted** — `docs/implementation/historical-content/<version>/`.
38. **To remove a pervasive flag, delete it and let the compiler enumerate the sites.**
39. **A def field and the XML that sets it are removed in the same change, always.**
42. **A patch target inside `PatchOperationFindMod` is optional by construction**, and only there.
44. **"Like the game does" is measurable. Measure it.** Core describes 0 of 105 work givers and 80 of 80 recipes.
45. **A description nothing renders is text in a file.** Write it and show it in the same checkpoint.
46. **Escapes written through a shell can collapse one level too far and leave an invisible byte.**
49. **Before designing a rule, check it can fire.**
56. **When a founding comment stops describing the code, rewrite it in the same commit.**
59. **When a proof and the code disagree on a constant, change the proof.**
60. **A scenario declares what begins finished, never the tech tree.**
61. **A project that begins finished is also insight-committed.**
66. **Living documents and dated records are different things.** Dated records are **never** rewritten.
67. **A checker that cries wolf is worse than no checker.** Precision before coverage.
68. **The vocabulary is gate / connection / threshold.** Never "portal", "machine gate", "the machine", "doorway" or "gizmo" in player-facing text. **Key names are exempt.**
69. **Every owner direction quoted in `FINALIZED.md` must already exist in `TODO.md`.** A build failure. It found **ten**.
70. **When the owner suspects a process failure, measure it — do not argue.**
72. **A retired def's name outlives the def in player-facing text.** Retiring a def means retiring its vocabulary.
73. **Check a prep document against the build every checkpoint.**
76. **LAW: check the mod register before building.** Filter by system family, read the per-mod review, and **state in the record what was checked** — or that nothing applied. Retroactively too.
77. **The register's `Stance` column is not trustworthy alone.** Row 78 reads `Required`; its review reads `optional`. The review is the authority.
78. **The register HTML has TWO tables**; a naive parse yields 589 rows and silently halves every filter.
79. **Chromium blocks XSLT from `file://`** — a stylesheet on About.xml gives a **blank page**, not a styled one.
80. **RimWorld renders newlines, so a wall of text is a choice.** Fails past 420 chars with no break.
81. **Do not quote a banned string verbatim in a living document** — it trips the rule that bans it. Rephrase.
82. **RimWorld has a different convention per display surface, not one voice.** A float menu row ends with a full stop 7% of the time in Core; an explanatory tooltip does 93% of the time. Writing either in the other's register is the mistake.
83. **Measure a surface, never a file.** The first run of `check-display-style.py` reported seven faults that were not faults, every one from sampling `Letters.xml` or `GameplayCommands.xml` alone when the surface spans several files. The baselines were corrected, not the text.
84. **A census counts the zeroes.** *"to include all"* is only actionable if the report names the surfaces the mod uses **none** of. That is how the alerts readout was found unused. A zero is a question, not a failure.
85. **A count printed with no rule behind it says so.** The inspect pane is counted and not ruled on, because Core builds inspect lines from strings scattered across its keyed files and there is no clean population to measure. A stated limit is not a forgotten one.
86. **Cache an alert scan on the tick AND the game object.** Core calls `GetReport` on a rotating one-in-twenty-four schedule. Keying a cache on the tick alone hands a second save loaded at the same tick the first save's despawned components.
87. **Words quoted from somewhere else are never ours to rewrite.** The vocabulary rule excludes any double-quoted span. The A24 synopsis calls it a doorway; changing that would be misquoting a source, not tidying a vocabulary.
88. **A document that describes the CODE keeps the code's identifiers.** The vocabulary rule covers the eleven reader-facing documents only. Rewriting prose around `PortalCrossingService` would make the documents disagree with the source, which is worse than an old word.
89. **Measure paragraphs, not source lines.** A hard-wrapped document hides a wall behind short lines; a one-line-per-paragraph document reports the paragraph. Threshold 700, grounded in the documents already rewritten for readability, which top out at 542.
90. **A readability rule makes somebody read the paragraph, and reading it finds the lie.** Two superseded rules were found this way, neither of which anybody was looking for: gate and portal as one word, and nothing-ever-crosses-on-its-own after incursion was added.
91. **Retiring a def means retiring every rule only it could satisfy.** A distortion counter tested for a beacon retired three checkpoints earlier, so the outcome was unreachable and no checker could see it.
92. **A Building is moved by despawning and respawning, never by writing `Position`.** Its cells are registered in the map's thing grid at spawn.
93. **Core's `ScenPart_StartingThing_Defined` minifies its own output**, and `MinifyUtility.TryMakeMinified` passes a non-minifiable thing through unchanged. An uncrated building in a cargo hold is a thing nobody can pick up.
94. **`CompLifespan.age` is a public field.** A Core glow pod dies after 1,200,000 ticks; holding a designated one at zero leaves every other glow pod in the game alone.
95. **Count the caps, not the cap.** *"lets not limit the amount"* named one limit and there were three: per room, per crew at dispatch, and per recipe batch.
96. **Core keeps facility-link geometry on the FACILITY side.** `CompProperties_Facility` is `maxDistance = 8f`, `requiresLOS = true`; the consumer comp carries one field and no control over either. Long-range, wall-transparent links must be our own record, or vanilla research linking changes for everyone.
97. **A def name that reads correctly can still be wrong, and nothing will tell you.** `Multianalyzer` is a ResearchProjectDef; the building is `MultiAnalyzer`. RimWorld's XML loader validates neither, so the wrong one loads clean and matches nothing. **Enumerate the installed data.**
98. **A rule and its exemption must both be provably non-empty.** The same-power-net rule applies only to things with a power comp. If every candidate were powered the exemption would be dead code; if none were, the rule would be. Assert both halves.
99. **State what already works before building it again.** Six of the nine items in this direction were already satisfied by rules written for the original three providers.
100. **A ladder must be at least as long as the tier it declares.** `portalWindowTierProjects` held one rung while `portalIndefiniteTier` was 4, so the top of the gate's own capability ladder was unreachable for the whole life of the mod. **Every individual value was valid**; the fault existed only in the relationship between two settings in different files. Covered by `proof-tier-ladder.py`, which reads the ladder from the source and the rungs from the defs.
101. **Fungible currency cannot express what a branch has learned.** Insight bought the same thing whatever produced it. Completed logs are the qualification and insight is only the price; a spent currency is gone and a completed log is not.
102. **Check a qualification before charging for it.** `ProjectQualificationFailureKey` runs ahead of the insight deduction, so a branch short of logs is told which kind.
103. **Custody is a place, not a receipt.** The retired check asked whether an evidence case existed somewhere at headquarters and never asked where the book was. A rule that can be satisfied without the thing it is about being anywhere in particular is not a rule.
104. **A prerequisite chain needs a cycle check, transitively.** A cycle is unreachable content in which every individual def looks completely normal.
105. **ARCHIVE BEFORE REMOVING. Always.** A removal was made by deleting a tuned def field, a const and a keyed string outright, with no `historical-content/` archive. The owner stopped it: *"how tf do you know we didnt need that shit coded up correctly and wasnt unfinished work"*. **The conclusion was right and the method was wrong**, which is the worse failure because it looks like progress.
106. **ASK AT A FORK EVEN WHEN THE READING SEEMS OBVIOUS.** Whether *"offeres and trades"* covered a hiring applicant and a purchase quote was a real fork with two readings. It was guessed, not asked, and finished code was deleted on the strength of the guess.
107. **The only clock is the gate.** No mission, quest, offer, contract or trade ever expires. A delay, a cooldown and a timestamp are all fine; a deadline is not. Enforced by `check-campaign-absolutes.py`.
108. **Every offer carries two or more routes to success**, of at least two different kinds. Enforced before the content exists, so the first offer ever written has to satisfy it.
109. **A clock that bounds nothing is pure pressure.** Both retired offer clocks sat beside a count cap that already bounded the pool. Check what actually bounds a list before believing a timer is load-bearing.
110. **Never widen a rule so that existing text passes.** `banned` and `superseded` were briefly added to the deadline-negation list and taken straight back out; they would have masked a real promise sitting near either word.

---

## The warning that matters most right now

**A checker that silently passes everything is worse than no checker — it manufactures confidence.**

Proved twice more this session. A placeholder rule contained a **literal backspace byte** where a word boundary was meant, matched nothing, and looked perfect in every listing. A vocabulary sweep **renamed a keyed string** and only `check-keyed-strings.py` noticed.

- **Sanity-test every checker by breaking something and confirming it fails.** Both directions: plant the fault, **and** plant what must be ignored.
- **When a proof only confirms, suspect it.** Two designs changed this session *because* a proof disagreed — the spin-up decay rate, and revisit displacement firing 100% of the time.

---

## Standing method

- **Check the register first** (LAW). `python tools/register-query.py family <x>`, then the per-mod review under `docs/research/reviews/mods/`. Say what you checked.
- **Read the prep work.** `UNIVERSE_ADAPTATION.md` had an unbuilt item nobody had noticed for the whole project.
- **A TODO item carries all its related work.**
- **At a fork: ask immediately**, multiple choice with a write-in. Never flag.
- **State what already works before building it again.**
- **Name what is not done, in `TODO.md`, in the same checkpoint.**

## Read these first

1. `docs/NOW.md` — this file.
2. `docs/TODO.md` — every owner direction verbatim.
3. `.claude/CONSTRAINTS.md` — the LAWs, including the register LAW.
4. `docs/GATE_0_DECISIONS.md` — D1–D9 **and** decisions 13–25. D1 changed.
5. `docs/implementation/CONNECTED_WORK_CORE_API.md` — pinned Core facts.
6. `docs/PUBLISHING.md` — the cascade. Follow it literally.

## The checkpoint ritual

1. **Check the register** for the system family being touched, and record what it said.
2. Read every file in full before editing.
3. `powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1` — zero warnings. It refuses if csproj and `About.xml` disagree, so bump both.
4. `CHANGELOG.md` in plain player-facing language.
5. Implementation record under `docs/implementation/`.
6. Ledger: `TODO.md`, `NOW.md`, `FINALIZED.md` (verbatim owner words), `ROADMAP.md`.
7. **Every checker**: `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `check-info-cards.py`, `check-display-style.py`, `check-campaign-absolutes.py`, `check-doc-conformance.py`, `research/audit-gate0.py`. There are eight.
8. **Determinism**: delete `obj/` and `bin/`, rebuild **twice**, hashes must match.
9. Commit once atomically; cascade to `Prep`, `Develop`, `Main` on **both** remotes; **read back all eight refs**.

## Gotchas learned the hard way

- **XML comments cannot contain `--`.** Hit **four times**. The checker names the rule and the line.
- **Bash heredocs mangle `\n` and break on apostrophes.** Hit **six times**. Use Write, and a message file for commits.
- **A GitHub push can silently drop some refs.** Read back all eight, every time — it happened once this session.
- **A failed `assert` in a patch script means nothing was written** — the write comes last.
- `git` index lock goes stale; `rm -f .git/index.lock`.
- **`cd` inside a Bash call persists.** Absolute paths.
- Package manifests are UTF-8 **with BOM** — `encoding="utf-8-sig"`.
- Decompile with `.local/tools/ilspycmd.exe -t <FullTypeName> "<RimWorld>/RimWorldWin64_Data/Managed/Assembly-CSharp.dll"`. **Empty output means the type name was wrong.**
- C# 7.3: no target-typed conditionals.
- **A def field emitted in XML that no class declares is ignored silently at load.**
- Core's `StockGenerator_Category` has **all-private fields**. `GenRecipe.PostProcessProduct` is **private static**.
- `SetTerrain` **clears** the colour grid. `CompFlickable.SwitchIsOn` has a **public setter**.

## Blocked on the owner

**Nothing.** That status does not exist here. Runtime rows are `[T]` and gate no work.

Three decisions are *reserved* for the owner but block nothing now: the site's domain, the Pages publishing branch, and whether Playwright may drive Steam. All three are named in [`PUBLIC_RELEASE_PLAN.md`](PUBLIC_RELEASE_PLAN.md).
