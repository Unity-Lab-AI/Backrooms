# NOW — Current Focus Snapshot

**Single-focus tracker.** One thing in flight at a time. The "what is Unity actively working on right this moment" file. Distinct from the three-tier task ledger:

| File | Grain | Scope |
|------|-------|-------|
| `docs/ROADMAP.md` | MAJOR | High-level phases / milestones (multi-session, multi-PR) — layered onto the project's Stage 0–6 development roadmap |
| `docs/TODO.md` | MINOR | Day-to-day work queue (everything pending + in-progress) — the working slice of the master backlog in `docs/PREPRODUCTION_AND_IMPLEMENTATION_TODO.md` |
| `docs/DECOMPOSED.md` | DECOMPOSED | Smallest meaningful execution unit (one file edit, one command) |
| **`docs/NOW.md`** (this file) | **CURRENT** | **The ONE task currently in motion — the active context** |
| `docs/FINALIZED.md` | ARCHIVE | Permanent record of every completed task |

LAW #0 applies: every snapshot of the active task preserves the user's verbatim words from the request.

---

## Active

**Nothing in flight.** The tree is clean and everything is published. This section is a handoff written deliberately for the session that picks up after a compaction.

### State at handoff

| | |
|---|---|
| Branch | `feature/connected-colony-portals` |
| Published | 0.7.1-dev (`git log -1`; the cascade read-back is in `FINALIZED.md`) |
| Remotes | `forgejo` and `github`, both with `feature/connected-colony-portals`, `Prep`, `Develop`, `Main` at the same commit |
| Working tree | clean |
| Build | 120 C# source files, 76 approved package files, zero warnings, zero errors |
| Assembly | SHA-256 `751C315B18A79A9EC9B965759261B987B69EF5B43319D5FA59B1D9C7B8B62C5A`, reproduced by two full recompiles after deleting `obj/` and `bin/` |
| Register | `outputs/rimrooms-async-industries-register-2026-09-27/Rimrooms_Async_Industries_294_Mod_Integration_Register.html` — **open this one**, not the `.xlsx`. Generated; rebuild after any CSV edit |
| Game launches | **none, ever.** Every runtime claim in this repo is pending the post-completion test phase |

### The standing instruction that matters most

**Owner direction, 2026-09-29:** *"you are NOT to stop untill i tell you to stop or you reach the completeion of the mod's build out"*

Do not finish a checkpoint and wait. Chain them. The owner got tired of asking for continuation, and rightly.

### What exists now, in order of arrival

- **0.4.2 → 0.4.3** — remembered gate addresses, the ordinary crossing job, laboratory sessions, emergency return; then the gate traversal rule at one chokepoint (`PortalTraversalPolicy`).
- **0.5.0 → 0.5.3** — the cross-map work engine (saved intents, planning leases, bounded route cursors, the adapter contract) and the first three carry families. Plus a deferment audit closing nine rows, and the audit proving the mod needs nothing but base Core.
- **0.5.4** — the laboratory duration ladder, natural-gate exemption confirmed, one tech tree for every scenario, a player-named company.
- **0.5.5 → 0.6.1** — travel-to-work as a *sibling* record; bills, research, tending, food, rest. Also the **evidence-ritual fix**: the SDK was embedding the git commit in `AssemblyInformationalVersion`, so every recorded hash had been unreproducible.
- **0.6.2 → 0.6.4** — eight families in one pass; ways onward findable on ordinary maps; **Backrooms containment** and the care families.
- **Register checkpoint (still 0.6.4)** — the 294-mod register rebuilt with a generator, a checker and an **HTML output**, because there is no spreadsheet application on this machine. Joy and rituals decided **no**.
- **0.6.5 → 0.6.7** — bill work as five families; dark study; hauling upkeep, BasicWorker and Fishing. **Every work type in Core and all five expansions is now covered or decided against.**
- **0.6.8** — the zone audit, and a growing-zone defect that **held a worker in the Backrooms indefinitely**.
- **0.6.9** — **a way out**: `PortalConnectionKind.Emergence`, a player-marked door as the place a way out comes up.
- **0.7.0** — the **gate kill switch**, refused unless the switch genuinely carries the gate's power.
- **0.7.1** — **gate servicing**, modelled on *Questionable Ethics Enhanced*'s vats: a condition that decays, modulated by room cleanliness, ×8 without power.

**Thirty-one cross-map work families, twenty-three of them travel-to-work deployments.**

### What is left, in the order to do it

1. **A player-facing how-to for the gameplay and systems.** Owner-requested and **now the most pressing item**: power, cutoff and condition are three interacting systems on one gate with no written explanation of how they fit together. `docs/HOWTO.md` documents **the build**, not play. Verbatim in `TODO.md`.
2. **The four area types across a gate** — `Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear`, `Area_PollutionClear`. Correctly uncovered until 0.6.9; **now genuinely live**, because an ordinary map is reachable through a gate and a colony map gets snow and wants roofs built. See `research/ZONES_AND_AREAS_ACROSS_A_GATE.md`.
3. **A world tile the branch does not hold** — the larger half of the topology direction, needing a new world object and a generated map. Its own checkpoint.
4. **The three starting sites.** `SCENARIOS.md` specifies all three in full, so this is implementation, not design. Two begin with a way out of the Backrooms.
5. **Floors returning materials when lifted** — vanilla returns none, so *"uninstalled, moved, resued, sold"* for carpet and tile needs a `CONTENT_REUSE_POLICY.md` decision.
6. **The 1990s period and the universe factions.** New `FactionDef`s reusing existing pawn kinds, all starting neutral.
7. **The eleven DLC container hauling givers** (each needs a custody review) and the **four painting givers** in `Art`.
8. **M6a — now unblocked and buildable today.** Split out on 2026-09-29 by owner decision 19 because M6 was the only major that cannot be closed by building, and one major reading 0% hid that four of its ten rows needed no launch at all: package and def validation, the mod page and provenance, the tag-and-archive ritual, and the buildable part of the fresh-start checklist. M6b keeps the six rows that structurally require the owner's launch.
9. **Two defects surfaced 2026-09-29 while counting, named and open.** (a) **The master backlog stopped at 0.4.2-dev** — 81 rows on Phase 0 research, one unchecked row covering the entire cross-map work engine and 27 shipped versions, so a raw count reads ~12% on code while the source tree went 78 → 120 files; reconciling 0.5.0–0.7.1 back into it is its own item. (b) **`disposition_stance()` counts a negated "required" as Required** — 14 of 17 rows in that bucket say the opposite, so 82% of it is wrong, and row 196 (RimWorld Together) falls through to `Unclassified`.
10. Then M1 step 5, M2 existing-content replacement, M3 breadth, M5 interface, M6b release.

### Invariants — do not break these

Each one is a real defect or a pinned source fact.

1. **`PortalTraversalPolicy` is the only chokepoint.** A colonist may decide to cross to work; an inhabitant may never decide anything about a gate.
2. **Two halves of validation, never merged.** A candidate predicate runs against an explicit `Map` and may never ask a native pawn-specific reachability, reservation, `HasJob`/`JobOn` or allowed-area question about a map the worker is not on. Split a Core method by **what each rule reads**, and write the table down.
3. **Remote forbidden checks use the *faction* overload.** `IsForbidden(Pawn)` consults the pawn's allowed area in its *current* map.
4. **A bounded search that ran out of budget is *pending*, never "no route".**
5. **Every bounded scan is a rotating window, never a prefix.** One documented exception: a deployment's *arrival* check is unwindowed.
6. **Two work givers per family** — high-priority continue, low-priority plan. One giver cannot be both.
7. **Never infer "there is no local work" from a priority number.** Ask outright.
8. **One commitment per worker, across every record kind.** `HasLiveCommitment` is the chokepoint.
9. **Nothing is ever `playerForced`.**
10. **No quantity is ever hardcoded.** Core's own count, always.
11. **No new gameplay ThingDef, art or audio.** Match by *capability*, never by name. A `FactionDef` is world configuration and is permitted.
12. **Zero throwing def lookups.** `GetNamedSilentFail` everywhere.
13. **Natural gates have no timer, operator, power or close command.** Ever.
14. **Nothing in the work layer walks a pawn home.**
15. **Needs are not work and this layer does not reach into them.** Solve needs logistically.
16. **A resource family must never move the shortage it is solving.**
17. **A bed is only ever a bed on its own map.**
18. **A provider answers one *question*, not one Core work giver.**
19. **Never touch Core's static scan state from a remote probe.** `WorkGiver_Grower.wantedPlantDef` is written by Core mid-scan.
20. **Before writing a family, check whether an existing one already covers it.**
21. **A Backrooms coordinate has no outside, and its roof is never removable** — but its interior is fully strippable and mining is unrestricted, because thick rock roof never vanishes on collapse. **Ordinary world maps keep every vanilla roof and mountain tool.**
22. **Prefer a setting or a def over a constant** for anything tunable.
23. **Add definitions; never redistribute assets.** No `PatchOperationReplace`/`Remove` on a Core def. Gate DLC content with `MayRequire`. Official versions only.
24. **Never force-push. Never launch the game. Never alter the RimSort list. No AI attribution anywhere.**
25. **A candidate half must ask whether the *target* can take the work, not only whether its *zone or owner* wants it.** A growing zone on a coordinate's concrete floor (fertility 0) reported work forever, and because `HasWorkHere` asks the same question the deployment was **held open** with the worker idle — worse than a wasted trip.
26. **A def referencing DLC content carries `MayRequire`; the C# guard is not enough.** `GetNamedSilentFail` makes the *code* degrade and does nothing for an unresolved cross-reference in the *def*. `tools/check-dlc-gating.py` must pass.
27. **The register is generated output; the HTML one is the register.** There is **no spreadsheet application on this machine and no `.xlsx` association**. Hand-editing either output loses the edit on the next build. Tallies are counted from the rows every build and never stored.
28. **A prisoner can never cross a gate; a *secure* slave can.** `Pawn.IsColonist` requires `Faction.IsPlayer && (!IsSlave || guest.SlaveIsSecure) && !IsSubhuman`. Do not add a second check.
29. **The portal topology is an unbounded alternation of world maps and Backrooms coordinates**, in any order, built gates and found frontiers mixed freely.
30. **Never trust a remembered list of anything against the shipped game data.** The families list omitted `DarkStudy` and `Fishing`. Enumerate.
31. **Two owner words have turned out to be mod names, not descriptions.** *"Questionable Ethics"* is profile row 182. **Search the register before interpreting an unfamiliar phrase as flavour.**
32. **A D-numbered Gate 0 decision can change, so read the sheet rather than a remembered answer.** D1 changed on 2026-09-29 — public Steam Workshop is now the first distribution target, not a private RWT prototype. Several documents assert a decision's *content* rather than linking it, so a change means grepping the assertion, not just the ID: four documents still stated the old D1 after the first propagation pass. `AGENTS.md` already required this — *"when a new owner decision changes scope, record it and propagate it across the TODO, design, technical, traceability, and test documents before relying on it"* — and it is a real sweep, not a formality.
33. **The no-tests rule has exactly one exception and it is written into `CONTRIBUTING.md` itself.** Owner decision 20 authorises automated fixtures for a single Phase 6 row and defers all of it until after the first launch. **Never widen it.** It is recorded in the rule's own file precisely so a later session cannot read it as general permission.
34. **Do not trust a progress percentage from a row count in this repo.** The master backlog is granular for research and coarse for code — one checkbox covers 27 shipped versions. Estimate per major, and say which basis a number came from.

### Standing method

- **Read the prep work first.** The 294 per-mod reviews under `research/reviews/mods/` carry verified facts and a recorded disposition for every entry. They have caught real constraints repeatedly, and **the register recovered a misread owner reference in one query**.
- **A TODO item carries all its related work.** Rarely add rows; do the item and everything it needs.
- **Run the doc-rot sweep** whenever an owner decision lands. `REGRESSION_CONTAINMENT.md` §Doc-rot sweep.
- **At a fork: ask immediately with multiple choice and a write-in, and keep building around it.** But **search the register first** — twice now an apparent design question was a factual one.
- **Nothing is blocked on the owner.** Runtime rows are `[T]` and belong to the post-completion test phase.
- **State what already works before building.** Four owner requirements this session were already shipped exactly as asked, including the 30-minute first opening. Saying so is worth more than rebuilding them.

### Read these first, in this order

1. `docs/NOW.md` — this file.
2. `docs/TODO.md` — every owner direction captured verbatim, newest first.
3. `docs/DEFERRED.md` — every open row with its owner.
4. `docs/implementation/CONNECTED_WORK_CORE_API.md` — pinned Core facts, including who may cross a gate.
5. `docs/implementation/CONNECTED_TRAVEL_TO_WORK_IMPLEMENTATION.md` — the deployment shape and the Core-method split table.
6. `docs/research/WORK_TYPE_COVERAGE_AUDIT.md` — all 23 work types. **Read before writing any work family.**
7. `docs/research/ZONES_AND_AREAS_ACROSS_A_GATE.md` — every zone and area type across a gate.
8. `docs/implementation/MOD_REGISTER_REBUILD.md` — how the register works, and why the HTML one is the one to open.
9. `docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md` — the verified TOS position.
10. `docs/PUBLISHING.md` — the push procedure. Follow it literally.

### The checkpoint ritual

1. Read every file in full before editing it.
2. `powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1` — zero warnings, zero errors. It refuses to build if the csproj and `About.xml` versions disagree, so bump both.
3. `CHANGELOG.md` entry in plain player-facing language.
4. Write the implementation record and an evidence folder under `docs/implementation/evidence/<name>-<date>/`. **Write `build-output.txt` separately — the manifest script does not produce it.**
5. Update the ledger: `DEFERRED.md`, `TODO.md`, `NOW.md`, `FINALIZED.md` (verbatim owner words), `ROADMAP.md`, `ARCHITECTURE.md`.
5a. **Run the doc-rot sweep** if an owner decision landed.
5b. **If any keyed string or `RR_` literal changed**, run `python tools/check-keyed-strings.py`. Catches duplicate keys, unresolved references, and format arguments that do not line up.
5c. **If any def was added or edited**, run `python tools/check-dlc-gating.py`.
5d. **If any register CSV changed**, run `build-mod-register.py`, then `check-mod-register.py`, then `audit-gate0.py`.
6. Verify: XML parses, every `RR_` key resolves, every `giverClass` resolves, no attribution strings, and — **after deleting `obj/` and `bin/`** — the rebuilt hash matches. An incremental rebuild proves nothing.
7. Commit once, atomically, push the feature branch, cascade by refspec to `Prep`, `Develop`, `Main` on **both** remotes, read back all eight refs. Do not edit after the push.

### Practical gotchas learned the hard way

- **Bash heredocs fail on apostrophes**, and **`\n` inside a quoted heredoc gets mangled**, which silently aborts a patch script mid-way and leaves earlier edits unapplied. This has now bitten **four times this session**. For anything with newlines or apostrophes, use the Write/Edit tools, not a heredoc.
- **A failed `assert` in a patch script means *nothing* was written**, because the write comes last. Re-check state before assuming a partial apply.
- **`cd` inside a Bash call persists.** Absolute paths.
- Package manifests are UTF-8 **with BOM** — `encoding="utf-8-sig"`.
- Decompile with `.local/tools/ilspycmd.exe -t <FullTypeName>`. An **empty output file means the type name was wrong**.
- C# 7.3: no target-typed conditionals.
- `ForbidUtility`, `HaulAIUtility`, `GenConstruct` are in `RimWorld`; `ReservationUtility` is in `Verse.AI`.
- **A property can shadow a type in the same namespace.**
- Some Core work givers are `internal` (`WorkGiver_FightFires`). Reproduce the rule from public pieces and say why.
- **`audit-gate0.py`'s link scanner strips fenced code blocks but not inline code spans.** Quoting a broken markdown link inline *recreates* it. Fence it.
- **XML comments cannot contain `--`.** The build's own validator catches it.
- **Read the distribution after changing any classifier.** Testing "no integration" above "optional" silently moved 59 mods into the wrong bucket.
- Installed Workshop mods are readable at `/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/<id>/` — useful for understanding a profile mod's model. **Read, never copy.**

### Genuinely blocked on the owner

**Nothing.** That status does not exist here. Runtime confirmation is `[T]`, belongs to the post-completion test phase, and gates no work.

## How to use this file

1. **When starting a meaningful task** — populate the Active section with verbatim user request + goal + files
2. **During work** — update Files Touched + Verification Plan + Blockers as state shifts; this is a living snapshot
3. **When finishing** — append the closure to `docs/FINALIZED.md` (per FINALIZED-BEFORE-DELETE LAW), then reset the Active section back to _(none — no work currently in motion)_
4. **Never delete the Active section structure** — the placeholder lines stay; only the content shifts

The file always has exactly one Active section. When it says _(none)_, the bridge stream is idle and Unity is awaiting next direction.

---

## Why this file exists alongside TODO.md

`TODO.md` is the queue — everything pending + in-progress, grouped by section. It can hold dozens of `[~]` items if multiple parallel threads are open.

`NOW.md` is the lens — ONE task, all the context, no scroll. Useful when:
- Session resumes after compaction and you need the "where were we" anchor in 10 seconds, not 10 minutes
- The user asks "what are you doing right now" mid-task
- A pre-compact snapshot needs to capture exactly one current context (not the whole TODO queue)
- The harness hooks want a single-task pointer for the state-refresh banner

Read `NOW.md` first for "what's happening", then `TODO.md` for "what's queued", then `ROADMAP.md` for "where are we headed".
