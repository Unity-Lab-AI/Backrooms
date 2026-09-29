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
| Published | 0.6.7-dev (`git log -1`; the cascade read-back is in `FINALIZED.md`) |
| Remotes | `forgejo` and `github`, both with `feature/connected-colony-portals`, `Prep`, `Develop`, `Main` at the same commit |
| Working tree | clean |
| Build | 119 C# source files, 76 approved package files, zero warnings, zero errors |
| Register | `outputs/.../Rimrooms_Async_Industries_294_Mod_Integration_Register.html` — **open this one**, not the `.xlsx`. Generated; rebuild after any CSV edit |
| Assembly | SHA-256 `9A73827B2E0F6C6AC33712BE447CEA5C7F8959C72820080AE7C2C00BA75A8EAE`, reproduced by two full recompiles after deleting `obj/` and `bin/` |
| Game launches | **none, ever.** Every runtime claim in this repo is pending the post-completion test phase |

### The standing instruction that matters most

**Owner direction, 2026-09-29:** *"you are NOT to stop untill i tell you to stop or you reach the completeion of the mod's build out"*

Do not finish a checkpoint and wait. Chain them. The owner got tired of asking for continuation, and rightly.

### What exists now, in order of arrival

- **0.4.2 → 0.4.3** — remembered gate addresses, the ordinary crossing job, laboratory sessions, emergency return; then the gate traversal rule at one chokepoint (`PortalTraversalPolicy`).
- **0.5.0 → 0.5.3** — the cross-map work engine (saved intents, planning leases, bounded route cursors, the adapter contract) and the first three carry families: storage hauling, casualties and remains, construction supply. Plus a deferment audit closing nine rows, and the audit proving the mod needs nothing but base Core.
- **0.5.4** — the laboratory duration ladder, natural-gate exemption confirmed, one tech tree for every scenario, a player-named company.
- **0.5.5** — **travel-to-work**: `ConnectedDeploymentIntent` as a *sibling* record, and construction finishing as the first provider.
- **0.5.6** — the `[!]` blocked status **deleted**, the post-completion test phase named, all cross-gate priorities made **live player settings**, and a verified RimWorld/Steam compliance position with automated checks.
- **0.5.7 → 0.6.1** — bills, research, tending plus medicine, food plus patient feeding, rest plus rescue-in-place. Also the **evidence-ritual fix**: the SDK was embedding the git commit in `AssemblyInformationalVersion`, so every recorded hash had been unreproducible after its own commit.
- **0.6.2** — eight families in one pass: cleaning, repair, firefighting, mining, hunting, plant cutting, growing zones, and refuel **with rearm as one family**.
- **0.6.3** — ways onward findable on ordinary world maps, never in a player-built door.
- **0.6.4** — **Backrooms containment** (no outside, roof never removable, interior fully strippable) and the last three work families: wardening, childcare, animal handling.
- **0.6.5** — **bill work**: five families, one per work type, so a bench on the far side finally gets worked. Plus a shipped defect closed — the carry family had been supplying autonomous and mech bills for five checkpoints contrary to its own record, because they derive from `Bill_Production`.
- **0.6.6** — **dark study**: a researcher crosses to a contained entity. Plus a second shipped defect closed — the childcare giver defs had referenced a Biotech-only work type with no `MayRequire` since 0.6.4, an unresolved cross-reference on a Core-only install. `tools/check-dlc-gating.py` now enforces it from the game's own data.
- **0.6.7** — **hauling upkeep, BasicWorker and Fishing**, closing the last work-type gaps. All thirty `Hauling` givers classified; three decided against as map-bound.
- **0.6.9** — **a way out**: `PortalConnectionKind.Emergence`, a player-marked door on an ordinary map as the place a way out comes up. Plus a duplicated keyed string fixed and `check-keyed-strings.py` added.
- **0.7.0** — **the gate kill switch**: an optional cutoff bound to a Core power switch, refused unless it genuinely carries the gate's power.
- **Register checkpoint, still 0.6.4** — the 294-mod register rebuilt with a generator and a checker, joy and rituals **decided no**, the three hauling rows closed, and the work-type list **enumerated instead of trusted**. No C# change; the assembly is byte-identical.

**Thirty-one cross-map work families, twenty-three of them travel-to-work deployments. Every work type in the game is covered or decided against.**

### What is left, in the order to do it

1. ~~**The four work-type gaps**~~ — **ALL CLOSED.** Bill work 0.6.5-dev, dark study 0.6.6-dev, hauling upkeep / BasicWorker / Fishing 0.6.7-dev. **Every work type in Core and all five expansions is now covered or decided against with its reason recorded**; joy, rituals, `Patient` and `PatientBedRest` are decided no. Do not reopen any of it — read `research/WORK_TYPE_COVERAGE_AUDIT.md`. What remains here is narrower and named in `DEFERRED.md`: the **eleven DLC container hauling givers** (each needs a custody review before a worker crosses for it) and the **four painting givers** in `Art`.
2. ~~**A portal whose far side is an ordinary map**~~ — **BUILT 0.6.9-dev.** Still open: **a world tile the branch does not hold**, which needs a new world object and a generated map.
   **Now live because of it:** `Area_BuildRoof`, `Area_NoRoof`, `Area_SnowOrSandClear` and `Area_PollutionClear` have no cross-gate route, and an ordinary map reachable through a gate genuinely gets snow, wants roofs built and may be polluted. See `research/ZONES_AND_AREAS_ACROSS_A_GATE.md`.
   **Also queued:** ~~the kill switch~~ (BUILT 0.7.0-dev), and two things newly asked for and **not** built — **equipment maintenance on the gate** (genuinely new; no upkeep concept exists, and the owner's ceiling is explicitly not *"crazy amounts"*) and a **player-facing how-to for the gameplay and systems** (`docs/HOWTO.md` covers the build, not play). Both verbatim in `TODO.md`.
   **Confirmed rather than changed** by that same direction, checked against shipped values: power loss already closes an open gate every tick; the first opening is already **exactly 30 real minutes** (`portalBaseWindowTicks = 108000` ÷ 60 ticks per second = 1,800 seconds); it already only increases from there (×3 per tier); and tiers already come from completed research.
3. **The three starting sites.** `SCENARIOS.md` specifies all three in full, so this is implementation, not design. Two of them begin with a way out of the Backrooms.
4. **Floors returning materials when lifted** — vanilla returns none, so the owner's "uninstalled, moved, resued, sold" for carpet and tile is a content feature needing a `CONTENT_REUSE_POLICY.md` decision.
5. **The 1990s period and the universe factions**, under `COMPLIANCE_AND_OFFICIAL_VERSIONS.md`. New `FactionDef`s reusing existing pawn kinds, all starting neutral.
6. Then M1 step 5 (the saved escalation ladder before any inhabitant generation), M2 existing-content replacement, M3 breadth, M5 interface, M6 release.

### Invariants — do not break these

Each one is a real defect or a pinned source fact.

1. **`PortalTraversalPolicy` is the only chokepoint.** A colonist may decide to cross to work; an inhabitant may never decide anything about a gate.
2. **Two halves of validation, never merged.** A candidate predicate runs against an explicit `Map` and may never ask a native pawn-specific reachability, reservation, `HasJob`/`JobOn` or allowed-area question about a map the worker is not on. Split a Core method by **what each rule reads**, and write the table down.
3. **Remote forbidden checks use the *faction* overload.** `IsForbidden(Pawn)` consults the pawn's allowed area in its *current* map.
4. **A bounded search that ran out of budget is *pending*, never "no route".**
5. **Every bounded scan is a rotating window, never a prefix.** One documented exception: a deployment's *arrival* check is unwindowed, because a miss there would loop the worker back across the gate.
6. **Two work givers per family** — high-priority continue, low-priority plan. One giver cannot be both.
7. **Never infer "there is no local work" from a priority number.** `JobGiver_Work` runs every giver's `NonScanJob` in one priority-ordered loop. Ask outright.
8. **One commitment per worker, across every record kind.** `HasLiveCommitment` is the chokepoint; `ValidateSavedState` enforces it across both saved lists.
9. **Nothing is ever `playerForced`.**
10. **No quantity is ever hardcoded.** Core's own count, always.
11. **No new gameplay ThingDef, art or audio.** Match by *capability*, never by name. A `FactionDef` is world configuration and is permitted; a new `PawnKindDef` is not.
12. **Zero throwing def lookups.** `GetNamedSilentFail` everywhere. Also watch for Core methods that *throw* rather than return false — `MedicalCareUtility.AllowsMedicine` does, on an undefined category.
13. **Natural gates have no timer, operator, power or close command.** Ever.
14. **Nothing in the work layer walks a pawn home.**
15. **Needs are not work and this layer does not reach into them.** Eating and sleeping come from Core's think tree. Do not patch it: a closing gate strands a hungry or tired pawn, and the failure is a dead colonist. Solve needs logistically.
16. **A resource family must never move the shortage it is solving.** Food will not take the last meal off a map that still has hungry people.
17. **A bed is only ever a bed on its own map.** `CanUseBedNow` returns false when the bed's map differs from the sleeper's `MapHeld`.
18. **A provider answers one *question*, not one Core work giver.**
19. **Never touch Core's static scan state from a remote probe.** `WorkGiver_Grower.wantedPlantDef` is written by Core mid-scan.
20. **Before writing a family, check whether an existing one already covers it.** Beds needed no rest family; construction already supplies and finishes them.
21. **A Backrooms coordinate has no outside, and its roof is never removable** — but its interior is fully strippable and mining is unrestricted, because thick rock roof never vanishes on collapse. **Ordinary world maps keep every vanilla roof and mountain tool**; the containment component returns immediately unless the map is a ready Backrooms site.
22. **Prefer a setting or a def over a constant** for anything tunable. The only test session fixes things live without a mod reload.
23. **Add definitions; never redistribute assets.** No `PatchOperationReplace`/`Remove` on a Core def. Gate DLC content with `MayRequire`. Official versions only.
24. **Never force-push. Never launch the game. Never alter the RimSort list. No AI attribution anywhere.**
25. **A candidate half must ask whether the *target* can take the work, not only whether its *zone or owner* wants it.** A growing zone on a coordinate's concrete floor (fertility 0) reported work forever, and because `HasWorkHere` asks the same question the deployment was **held open** with the worker idle — worse than a wasted trip. See `research/ZONES_AND_AREAS_ACROSS_A_GATE.md`.
26. **A def referencing DLC content carries `MayRequire`; the C# guard is not enough.** `GetNamedSilentFail` makes the *code* degrade and does nothing for an unresolved cross-reference in the *def*. `tools/check-dlc-gating.py` indexes the game's own data and must pass. The compliance check does **not** cover this — it looks for package ids, and a def naming `Childcare` never mentions Biotech.
27. **The register is generated output; the HTML one is the register.** There is **no spreadsheet application on this machine and no `.xlsx` association at all**, so `Rimrooms_Async_Industries_294_Mod_Integration_Register.html` is the file anybody reads. Both are built by `tools/research/build-mod-register.py` from the CSVs under `docs/research/`. **Hand-editing either output loses the edit on the next build.** Family, stance and firmness tallies are counted from the rows every build and are never stored.
28. **A prisoner can never cross a gate; a *secure* slave can.** `Pawn.IsColonist` requires `Faction.IsPlayer && (!IsSlave || guest.SlaveIsSecure) && !IsSubhuman`, and `PortalTraversalPolicy` delegates the whole judgement to it. Prisoners keep their own faction. Do not add a second check — Core's containment judgement is the one that decides.
29. **The portal topology is an unbounded alternation of world maps and Backrooms coordinates, in any order, built gates and found frontiers mixed freely.** Not "nesting" plus "an exit" — one rule. `map > backrooms > backrooms` already works; everything else resolves to the single open ordinary-map endpoint.
30. **Never trust a remembered list of anything against the shipped game data.** The families list omitted `DarkStudy` and `Fishing`, and closing the row on it would have closed it wrongly. Enumerate.

### Standing method

- **Read the prep work first.** The 294 per-mod reviews under `research/reviews/mods/` carry verified facts and a recorded disposition for every entry. Re-deriving them wastes it, and they have caught real constraints four times now — including that Meals On Wheels is not meal delivery, and that Gastronomy has unresolved rights.
- **A TODO item carries all its related work.** Rarely add rows; do the item and everything it needs.
- **Run the doc-rot sweep** whenever an owner decision lands. Rules and the live-versus-archive list are in `REGRESSION_CONTAINMENT.md` §Doc-rot sweep. This has bitten three times.
- **At a fork: ask immediately with multiple choice and a write-in, and keep building around it.** The listed options are never the whole space.
- **Nothing is blocked on the owner.** Runtime rows are `[T]` and belong to the post-completion test phase, which begins only once the mod is complete; then the owner sets up the environment, the rim api mod is added, and fixes land live without a mod reload.

### Read these first, in this order

1. `docs/NOW.md` — this file.
2. `docs/TODO.md` — every owner direction captured verbatim, newest first.
3. `docs/DEFERRED.md` — every open row with its owner, and the four audit questions in its header.
4. `docs/implementation/CONNECTED_WORK_CORE_API.md` — pinned Core facts, including why Core's own map-portal system cannot serve this design.
5. `docs/implementation/CONNECTED_TRAVEL_TO_WORK_IMPLEMENTATION.md` — the deployment shape and the Core-method split table.
6. `docs/implementation/CONTAINMENT_AND_CARE_IMPLEMENTATION.md` — the containment rule and its Core evidence.
7. `docs/research/WORK_TYPE_COVERAGE_AUDIT.md` — all 23 work types, what is covered, what is decided against, and the four gaps. **Read this before writing any work family.**
8. `docs/research/ZONES_AND_AREAS_ACROSS_A_GATE.md` — every zone and area type across a gate, what works, and the three that wait on the ordinary-map endpoint.
9. `docs/implementation/MOD_REGISTER_REBUILD.md` — how the 294-mod register works now, and why the HTML one is the one to open.
10. `docs/COMPLIANCE_AND_OFFICIAL_VERSIONS.md` — the verified TOS position and the rules binding every new def.
11. `docs/PUBLISHING.md` — the push procedure. Follow it literally.

### The checkpoint ritual

1. Read every file in full before editing it.
2. `powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1` — zero warnings, zero errors. It refuses to build if the csproj and `About.xml` versions disagree, so bump both.
3. `CHANGELOG.md` entry in plain player-facing language; update the `About.xml` description.
4. Write the implementation record and an evidence folder under `docs/implementation/evidence/<name>-<date>/` with compiler output plus source, package and **recomputed** reference manifests. **Write `build-output.txt` separately — the manifest script does not produce it.**
5. Update the ledger: `DEFERRED.md`, `TODO.md`, `NOW.md`, `FINALIZED.md` (verbatim owner words), `ROADMAP.md`, `ARCHITECTURE.md`, `SKILL_TREE.md`.
5a. **Run the doc-rot sweep** if an owner decision landed. `REGRESSION_CONTAINMENT.md` §Doc-rot sweep.
5b. **If any keyed string or `RR_` literal changed**, run `python tools/check-keyed-strings.py`. It must exit zero. It catches duplicate keys (there was a real one, used for two different messages), unresolved references, and format arguments that do not line up.
5c. **If any def was added or edited**, run `python tools/check-dlc-gating.py`. It must exit zero. Handling a DLC def correctly in C# with `GetNamedSilentFail` does **not** cover an ungated `MayRequire` in the def itself; that mismatch has produced two defects in two consecutive checkpoints.
5d. **If any register CSV changed**, rebuild in the same commit: `python tools/research/build-mod-register.py`, then `check-mod-register.py`, then `audit-gate0.py`. All three must exit zero. The outputs rebuild byte-identically from an unchanged source, so a diff on them always means the sources really changed.
6. Verify: XML parses, every `RR_` key resolves, every `giverClass` resolves, no attribution strings, and — **after deleting `obj/` and `bin/`** — the rebuilt hash matches the evidence. An incremental rebuild proves nothing. Pre-0.5.7 evidence hashes are **not** reproducible today; the SDK used to embed the git commit.
7. Commit once, atomically, push the feature branch, cascade by refspec to `Prep`, `Develop`, `Main` on **both** remotes, read back all eight refs. Do not edit after the push.

### Practical gotchas learned the hard way

- **Bash heredocs fail on apostrophes**, and **two heredocs in one compound command** fail even when quoted. Write the text to a `.local/*.py` or `.local/*.md` with the Write tool, run or `cat` it, delete it. This has cost time repeatedly.
- **`cd` inside a Bash call persists.** Absolute paths.
- Python cannot open `/c/Program Files (x86)/...`; use the `C:\...` form.
- Package manifests are UTF-8 **with BOM** — `encoding="utf-8-sig"`.
- Decompile with `.local/tools/ilspycmd.exe -t <FullTypeName>`. An **empty output file means the type name was wrong**, not that the type is empty. Already-collected Core types live in `.local/inspection-*/`.
- C# 7.3: no target-typed conditionals.
- `ForbidUtility`, `HaulAIUtility`, `GenConstruct` are in `RimWorld`; `ReservationUtility` is in `Verse.AI`.
- **A property can shadow a type in the same namespace.** `CampaignSeed` as a property broke four unrelated call sites of the static `CampaignSeed` helper. Renamed to `BranchSeed`.
- Some Core work givers are `internal` (`WorkGiver_FightFires`). Reproduce the rule from public pieces and say why.
- **`audit-gate0.py`'s link scanner strips fenced code blocks but not inline code spans.** Quoting a broken markdown link inline in a doc *recreates* it and fails the audit. Fence it.
- **No spreadsheet application is installed and `.xlsx` has no association.** Do not tell the owner to open a workbook; point at the HTML. Do not change file associations or install software — that is the owner's call.
- **Read the distribution after changing any classifier.** Testing "no integration" above "optional" silently moved 59 mods into the wrong bucket; a count jumping 13→72 was the only tell.

### Genuinely blocked on the owner

**Nothing.** That status does not exist here. Runtime confirmation is `[T]`, belongs to the post-completion test phase, and gates no work.

---

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
