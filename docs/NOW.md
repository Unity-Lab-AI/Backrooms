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
| Published | **0.10.0-dev** (this commit) |
| Remotes | `forgejo` + `github`, all four refs each at the same commit |
| Build | **158 C# files, 79 package files**, zero warnings, zero errors |
| Assembly | SHA-256 `1C54905192F5090A7C2F4F0D81321F1504919EB7E228CB9BB892A87265FADA73`, reproduced by two clean recompiles |
| Checkers | **six**, all passing |
| Register | `outputs/rimrooms-async-industries-register-2026-09-27/…Register.html` — **open the HTML**, not the xlsx |
| Game launches | **none, ever** |

### The standing instruction

> *"you are NOT to stop untill i tell you to stop or you reach the completeion of the mod's build out"*

Chain checkpoints. Do not finish one and wait.

---

## What shipped this session, 0.7.1 → 0.10.0

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
| 0.8.9 | **Bringing a gate up is work** — an operator-driven spin-up with familiarity, and gates that look like gates |
| 0.9.0 | **A gate is a door and nothing else** — eight legacy defs retired, package 92 → 79 files |
| 0.9.1 | **One kind of gate** — 68 dead branches collapsed, a vestigial power model removed, net −112 lines |
| 0.9.2 | **A gate has a size** — 1×1 to 2×3, Core's own `OrnateDoor` gives 1×2 free, cost scales with footprint |
| 0.9.3 | **Everything you can look at says what it is** — info cards calibrated to Core's own practice, fifth checker |
| 0.9.4 | **What a gate's size lets through** — animals may cross, and width decides which fit |
| 0.9.5 | **They follow you** — at `Band.Hostile` an inhabitant hunts to the threshold, on vanilla AI |
| 0.9.6 | **It came through with them** — a bounded, named exception to the founding rule |
| 0.9.7 | **Some places are bigger than a room** — facilities as contiguous runs of rooms |
| 0.9.8 | **One tech tree, different starting points** — the tree is derived, not declared per scenario |
| 0.9.9 | **The beacon had nothing left to do** — first field-gear retirement, four replacements decided |
| 0.10.0 | **The documents say what is true** — sixth checker, 28 stale claims across 10 living docs |

---

## What is left, in order

**The order is chosen and recorded**, by dependency direction rather than preference. Owner direction: *"we are doing it all so order needs to be logical and your intelkligent educated choise based on logical programming order of operations"*.

Content set → gate model → generator → scenarios → docs. One direction, no backtracking.

**Corrected immediately after 0.8.9-dev**: the multi-cell gate work was first listed ahead of M2. That was wrong. M2 deletes `RR_MachineGate`, which removes the gate comp’s second geometry model entirely, so doing it first means the multi-cell binding is written once rather than written and then rewritten.

1. ~~**M2 existing-content replacement**, first pass.~~ **DONE 0.9.0-dev** for the eight defs whose replacements were already live. **Still open in M2:** the field gear (`RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon`, `RR_SealedEvidenceCase`, `RR_RouteRecording`), which carry real mechanics the owner has explicitly refused to drop, so each needs a capability replacement built before its def can go; `RR_QuietPursuer`; the five staff PawnKinds and their recipes; The sixty-eight now-unreachable `IsNativeProvider` branches were collapsed in 0.9.1-dev. Original entry: **first, because it deletes defs** — anything built against content about to be removed gets built twice, and the save break is already declared so defs can go with no migration. It also **collapses the gate comp's whole non-native branch**: deleting `RR_MachineGate` removes the second geometry model, so the multi-cell work below is written once against one model instead of twice. Scope: legacy gate objects, field gear, fixtures and terrain, the `RR_QuietPursuer` presentation, five `RR_*Staff` PawnKinds, five recipes, and the fourteen historical PNGs off the allowlist.
2. ~~**What a gate's size lets through.**~~ **BUILT 0.9.4-dev.** Original entry: ~~Multi-cell gates~~ **BUILT 0.9.2-dev** for the sizes themselves: Core's `OrnateDoor` is 2x1 so **1×2 needs no mods**, Anomaly's `SecurityDoor` matches it, and Doors Expanded supplies 1×3 and 2×3 behind a `PatchOperationFindMod`. **Still open:** body-size limits at `PortalTraversalPolicy` so bigger creatures and vehicles need a wider gate, and the adjacent-door-run fallback for 1×3 and 2×3 without that mod. Original entry: multi-cell gates **Owner-answered: both paths.** Bind a gate across a **run of adjacent Core doors** (existing-content-only, always works), **and** accept **Doors Expanded** (register row 77) multi-cell doors as single-thing gates when that mod is installed. Width is the capability: how many cross abreast, whether cargo or a vehicle fits, what the opening draws. Core has only 1x1 `Door` and `Autodoor`, verified against installed game data.
3. ~~**Incursion.**~~ **BOTH HALVES BUILT — pursuit 0.9.5-dev, incursion 0.9.6-dev.** Original entry: ~~Pursuit~~ **BUILT 0.9.5-dev** with no pursuit code: at `Band.Hostile` a hostile gets an assault lord and vanilla AI walks it to the threshold. **Still open: coming *through*.** Original entry: **Owner-answered: depth plus technology, while an opening is live.** An inhabitant chases a fleeing pawn to the threshold, and reaching it before the gate closes brings it through into the colony, where every native hostile behaviour applies with nothing bespoke written. **Closing the gate is the countermeasure**, which makes the emergency cutoff a tactical decision at the cost of stranding whoever is still inside. `PortalTraversalPolicy` gains the rule; the inhabitant still decides nothing.
4. ~~**Facilities**~~ **BUILT 0.9.7-dev** as contiguous runs of 2-4 rooms sharing one archetype, proved across 2,800 simulated coordinates.
5. **New-game playability.** The **starting-research contract is BUILT (0.9.8-dev)** — a start declares only what begins finished and the tree is derived from the def database. **Still open:** the world tile the branch does not hold (world object plus generated map) and **the other two starting sites** (`SCENARIOS.md`), which are **blocked behind the field-gear replacement** — the existing scenario grants `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon` and `RR_SealedEvidenceCase`, and writing two more against retiring content is what the ordering exists to prevent. Consumes the final content set, the finished gate model *and* the finished generator. **One tech tree for every start**, differing only in which projects begin complete — owner direction, and it belongs in the versioned start contract rather than bolted onto each scenario.
6. **The player-facing how-to.** Last, because documentation describes a finished thing and writing it earlier means rewriting it. Note `docs/HOWTO.md` is the **developer** guide; the player one does not exist yet.
7. **The unknown-def-field checker.** Written, **proved broken, removed rather than shipped.** See the warning below — start from the verified parts.
8. **The 1990s period and universe factions.**
9. The four area types across a gate, M1 step 5, M3 breadth, M5 interface, M6a/M6b.

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
32. **There is exactly one way a laboratory gate opens** — through the spin-up. Every entry point routes into it. A second path would make the ramp optional, and a player who learned the other button would never see it.
33. **Never tie a penalty rate to a flat constant without proving it against the real stat range.** Spin-up decay was written as a flat 0.5 per tick with a comment claiming it was slower than progress; at low Intellectual it was **faster**, which would have made a slow operator's gate impossible rather than slow. Express such a rate as a **fraction of the observed rate** so the guarantee holds by construction.
34. **Ask at the fork; never flag it for later.** Owner direction: *"dopnt flag shit!!! ask me then and there"*. A flagged question becomes orphaned work — it lands in a doc nobody actions while the build carries a guess forward.
35. **`ThingComp.ForceColor()` is the tint hook**, consulted by `ThingWithComps.DrawColor` for every comp a thing carries, and a painted colour wins over it. `Notify_ColorChanged()` drops Core's cached coloured graphic and redraws the cell.
36. **A checker that reads only one kind of source is a checker with a blind side.** The texture check read XML and never C#, so three live references to deleted textures passed clean. It also only ever asked the weaker question — *does every shipped file have a reference?* — when the serious one is *does every reference have a file?* Ask both directions, of every source.
37. **Retired content is archived, never deleted.** `docs/implementation/historical-content/<version>/` mirrors the package layout. `audit-gate0.py` will catch the doc links that pointed at the old location.
38. **To remove a pervasive flag, delete it and let the compiler enumerate the sites.** Pinning `IsNativeProvider` to true, transforming all 68 sites, then deleting the property turned "did I miss one?" into a build error. One had been missed.
39. **A def field and the XML that sets it are removed in the same change, always.** A field removed alone leaves an element no class declares, and RimWorld ignores it in silence. This cost two checkpoints once already.
40. **A gate's width and its footprint are different numbers.** A 2×3 blast door is three wide and six cells of machine. Width decides what fits through; footprint decides what it costs to run.
41. **Throughput is never capped.** Owner direction: *"in vinilla any number of pawns can use a door at once so we dont want limitations"*. A wide gate gets more doorway cells, never a quota. There is no counter, deliberately.
42. **A patch target inside `PatchOperationFindMod` is optional by construction**, and only there. The integrity checker exempts exactly those and still reports them. The exemption was proved narrow by planting a bogus target outside it.
43. **Core ships `OrnateDoor` at 2×1 and `Building_MultiTileDoor` to drive it.** Anomaly adds `SecurityDoor`. This was found by enumerating installed data after the opposite was assumed.
44. **"Like the game does" is measurable. Measure it.** Core describes 0 of 105 work givers and 80 of 80 recipes. Counting that cut a 94-item list to 17 and stopped 67 lines of text no player would ever see.
45. **A description nothing renders is text in a file.** Write it and show it in the same checkpoint, or do neither.
46. **Escapes written through a shell can collapse one level too far and leave an invisible byte.** A word-boundary escape became a literal backspace; the pattern matched nothing and looked perfect in every listing. Prefer a form that survives quoting, and always prove a checker by planting the fault it is meant to catch.
47. **A connection has one width, in both directions.** Measuring each endpoint separately traps an animal in the Backrooms, because a generated return threshold is always a one-cell door.
48. **Company work and player orders are two different traversal rules.** `TravellerFailureKey` governs work and stays colonists only; `OrderedCrossingFailureKey` governs a player order and admits player animals. Widening the first would schedule animals into bills.
49. **Before designing a rule, check it can fire.** Body size could never have mattered while no non-colonist could cross.
50. **`Band.Hostile` is the "deeper levels" threshold.** Its own definition is *"the space stops being forgiving"*. Anything gated on depth-plus-history should use it rather than inventing a second number that can drift from it.
51. **A hostile below `Band.Hostile` holds ground; at it, it hunts.** The warning-first retreat rule is what makes a shallow coordinate survivable for one person, and it must stay true there.
52. **`LordJob_AssaultColony`'s first parameter is the ASSAULTER's faction.** Passing the player's names the player as the attacker, compiles cleanly, and no checker can catch it.
53. **Incursion is the one named exception to the founding rule**, and it is bounded on five axes: a live opening, `Band.Hostile`, `PortalWindowTier >= 1`, it must fit the opening, and once per opening. Widening any of them without the owner's word rewrites the mod's premise.
54. **`MayApproachThresholdForTraversal` must stay false for everything, forever.** Incursion works *because* nothing is drawn to a gate: a hostile walks to the doorway to reach the people standing there, and the gate notices what is already on its doorstep.
55. **A transfer that can lose a pawn is a corruption, not a threat.** Preflight fully, then move, and put it back where it stood if the move fails — a vanished pawn looks exactly like the feature working.
56. **When a founding comment stops describing the code, rewrite it in the same commit.** A doc that lies at the top of the chokepoint is worse than no doc.
57. **A facility is a contiguous run of 2–4 rooms sharing one archetype**, resolved through the lowest-index anchor and **stored nowhere** — recomputed identically from the saved graph and seed. Never a quiet room, never the threshold, never depth 1.
58. **Coherence is what wrongness needs.** A recognisable institution that is wrong beats a jumble, because a jumble has nothing to violate. Do not "fix" facilities by making deep coordinates tidier.
59. **When a proof and the code disagree on a constant, change the proof.** A proof testing different numbers than what ships is worthless. `EligibleShare` stayed 0.45; the proof moved to match.
60. **A scenario declares what begins finished, never the tech tree.** The tree is every `RimroomsProjectDef` loaded, sorted ordinally. That is what makes "same tech tree" a fact rather than a convention three lists have to honour.
61. **A project that begins finished is also insight-committed**, or the UI offers a "start" button on work already done.
62. **The remaining two scenarios are blocked behind the field-gear replacement**, not behind effort. They would grant `RR_FieldRecorder`, `RR_SurveyTag`, `RR_ReturnBeacon` and `RR_SealedEvidenceCase` — content M2 is retiring.
63. **The field-kit replacements are decided.** Survey tag → Core `GlowPod`; return beacon → **dropped**, its job taken over by the gate's address book; evidence case → a **designated headquarters `Shelf`** as the archive; recorder → **the book is the recorder**. Asked at the fork, grounded in enumerated Core content.
64. **`CompGlower.GlowColor` has a public setter**, backed by a saved per-instance `glowColorOverride`, and `colorPickerEnabled` on the props turns on RimWorld's own colour picker. Settable glow colour needs no new UI.
65. **Glow pods are never capped.** Owner direction: a 300×300 instance can have hundreds of rooms. Colour is **semantic** — mod-defined marker types, not decoration.
66. **Living documents and dated records are different things.** A readme must describe the mod now; an implementation record describes a moment that has passed and **must never be rewritten** — one stating the checker count of its day was true when written. `check-doc-conformance.py` exempts dated records by path, and that exemption is proved by planting faults it must ignore.
67. **A checker that cries wolf is worse than no checker.** The first branch rule produced 26 false positives on file paths and prose. Precision before coverage, every time.
68. **The unified vocabulary is gate / connection / threshold.** The **gate** is the machine in your wall; the **connection** is the live link it holds open; the **threshold** is the doorway on the far side. Never "portal", "the machine" or "the gizmo" in player-facing text.

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
6. **All six checkers**: `check-package-integrity.py`, `check-keyed-strings.py`, `check-dlc-gating.py`, `check-info-cards.py`, `check-doc-conformance.py`, `research/audit-gate0.py`.
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
