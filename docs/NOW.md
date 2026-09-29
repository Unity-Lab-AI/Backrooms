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

**Nothing in flight.** The last checkpoint is published and the tree is clean. This section is a handoff, written deliberately for the session that picks up next.

### State at handoff

| | |
|---|---|
| Branch | `feature/connected-colony-portals` |
| Published commit | 0.6.2-dev (see `git log -1`; the cascade read-back is in `FINALIZED.md`) |
| Remotes | `forgejo` and `github`, both with `feature/connected-colony-portals`, `Prep`, `Develop`, `Main` at the same commit |
| Working tree | clean |
| Build | 110 C# source files, 76 approved package files, zero warnings, zero errors |
| Assembly | SHA-256 `F575107A652079035111984660BADBD60235F80E3651FD9B025E8533AAE2A08C`, reproduced by two full recompiles after deleting `obj/` and `bin/` |
| Game launches | **none, ever.** Every runtime claim in this repo is pending the owner's first RimSort launch |

### What exists now, in order of arrival

- **0.4.2-dev** — remembered gate addresses, legacy threshold repair, the ordinary crossing job, laboratory session controls, emergency return, unresolved-crossing reconcile surface.
- **0.4.3-dev** — the owner's gate traversal rule at one chokepoint (`PortalTraversalPolicy`): inhabitants and monstrosities never cross on their own; anything else rides only in a carrier's hands.
- **0.5.0-dev** — the cross-map work engine: saved work intents, planning leases, bounded route cursors, the adapter contract, and the first family (**storage hauling**, both directions).
- **0.5.1-dev** — a deferment audit that closed **nine** rows. Natural-gate discovery by survey, container delivery destinations, observed remote allowed areas, a bound on the crossing-receipt archive.
- **0.5.2-dev** — **casualties and remains**: our own downed people carried home to a bed, our dead to a grave or storage.
- **0.5.3-dev** — **construction supply** (material carried into a real frame or blueprint), the audit proving the mod requires nothing but base Core, and the capability-matching method that dissolved the M2 content blockers.
- **0.5.4-dev** — four owner decisions: the laboratory duration ladder, natural-gate exemption confirmed, one tech tree for every scenario, a player-named company.
- **0.5.6-dev** — nothing is blocked on the owner: the `[!]` status deleted, the post-completion test phase named, all cross-gate work priorities made **live player settings**, and a verified RimWorld/Steam compliance position with automated checks.
- **0.6.2-dev** — **eight more families in one pass**: cleaning, repair and firefighting (scoped for free by Core's Home-area rule), mining, hunting, plant cutting and growing zones (driven entirely by what the player designated), and refuel **with rearm as one family**, because Core's own rearm giver is a refuel giver. Nineteen families now.
- **0.6.1-dev** — **rest and beds**: the tired-pawn question closed by *Core's own rule* rather than our caution, and the one real gap built — bedding a casualty where they lie instead of hauling them home.
- **0.6.0-dev** — **food across a gate**, as three parts, one of which was *decided against* rather than deferred: a hungry pawn does not walk through a gate to eat. Plus patient feeding as the fourth deployment provider.
- **0.5.9-dev** — **tending across a gate, both halves in one item**: the doctor travels to a patient who stays put (third deployment provider), and medicine travels as the first cargo consumed by the work. Surgery, patient feeding and prisoner care remain separately reviewed routes.
- **0.5.8-dev** — **research across a gate**, the *second* travel-to-work provider and one new file: no new record, driver or JobDef. Its real finding is that the deployment shape is inherently mod-tolerant, because a deployment never issues the work.
- **0.5.7-dev** — **bill ingredients**: goods cross a gate because a named bill is short of them, landing inside that bill's own search radius. Unfinished things deliberately out of scope.
- **0.5.5-dev** — **travel-to-work**: a fourth work family and the first that is not fetch → carry → deliver. `ConnectedDeploymentIntent` (a *sibling* record), `ConnectedDeploymentProvider`, `ConstructionFinishingProvider`, and `ConnectedCrossing` as the single shared gate step. Also: the 1990s period and the universe factions captured verbatim and decided, queued after the work families.

### The next task — continuous portal topology, then the scenario starts

**Two owner directions arrived on 2026-09-29 and they belong together.** Verbatim text is in `TODO.md` under the universe-direction headings; this is the plan.

**1. Continuous topology.** Every start shares one topology. A Backrooms coordinate may hold a portal to an ordinary world map, or deeper into the Backrooms, or to *another instance seed*, or emerge anywhere on a world tile — and **the link kind that brought you somewhere never restricts where you can go next**. Portals within portals, without a nesting limit. Portals also exist to be found on ordinary world maps, not only inside the Backrooms.

Before writing anything, establish honestly what already supports this:

- `RimroomsPortalNetwork` already stores a **graph** of connections, and `PortalRouteSearch` already does multi-hop, so chains and nesting may already work. Verify it rather than assuming either way.
- `NaturalFrontierService` already discovers natural gates *inside* Backrooms maps by survey and records them as permanently open ways onward. Check whether a frontier can create a **new coordinate with a new seed** or only link existing ones — that is the likely real gap.
- `CampaignServices.CreateDiscoveredCoordinate` exists specifically so no caller can invent coordinate ids or seeds. Any new link kind must go through it.
- The gap most likely to need real work is **emerging on a world tile**: a Backrooms exit that lands somewhere on the world map rather than on a map the branch already owns.

**2. The scenario starts, and the good news.** The owner offered a fallback — ship equipment and supplies and let the player build everything — because they were unsure authored facilities were feasible. **They are not needed as a design exercise.** `SCENARIOS.md` already specifies all three starting sites in full detail: the Async 60x60 headquarters down to the gate chamber assembled to three-quarters, the 50x50 store down to the basement threshold that is not a working machine gate, and the lone-survivor 6-8 room coordinate with its route clues. So this is implementation against an existing specification.

Take the fallback only if a specified element turns out to be unbuildable under the existing-content-only policy, and say which element and why.

**Order to work in:** verify what the portal graph already does → close the real topology gaps → then the three starts, which consume the topology. The faction and period layer follows, under `COMPLIANCE_AND_OFFICIAL_VERSIONS.md`.

**Still open on the work families**, and smaller than what is above: prisoner and guest care, wardening, childcare, animals and mechs, joy and rituals (expect the needs-are-not-work answer for the last two), and the three hauling providers — Pick Up And Haul (164), Haul To Stack (107), Prison Labor (288).

### Invariants — do not break these

Hard-won, each one the result of a real defect or a pinned source fact. Recorded in `implementation/CONNECTED_WORK_IMPLEMENTATION.md`, `implementation/CONNECTED_TRAVEL_TO_WORK_IMPLEMENTATION.md` and `implementation/DEPENDENCIES_AND_CAPABILITY_MATCHING.md`.

1. **`PortalTraversalPolicy` is the only chokepoint.** A colonist may decide to cross to do a job. An inhabitant may never decide anything about a gate. Nothing may reintroduce autonomous non-player traversal.
2. **Two halves of validation, never merged.** A candidate predicate runs against an explicit `Map` and may never call a native pawn-specific reachability, reservation, `HasJob`/`JobOn` or allowed-area query for a map the worker is not standing on. The definitive half runs only on arrival. When splitting a Core method, split it by **what each rule reads**, and write the table down — `CONNECTED_TRAVEL_TO_WORK_IMPLEMENTATION.md` has the worked example for `GenConstruct.CanConstruct`.
3. **Remote forbidden checks use the *faction* overload.** `IsForbidden(Pawn)` consults the pawn's allowed area *in its current map* — the wrong map. Use `IsForbidden(Faction.OfPlayer)` remotely and `IsForbidden(pawn)` only on arrival.
4. **A bounded search that ran out of budget is *pending*, never "no route".**
5. **Every bounded scan is a rotating window, never a prefix.** A prefix starves the fifth connected map forever and looks identical to correct code until a fifth gate opens. The rules live once, in `ConnectedWorkScan`. **The one exception is deliberate and documented:** a deployment's *arrival* check is unwindowed, because a window that missed the work would release the deployment and send the worker straight back across the gate.
6. **Two work givers per family** — a high-priority one that only finishes committed trips, a low-priority one that only starts them. One giver cannot be both.
7. **Never infer "there is no local work" from a priority number.** `JobGiver_Work` runs every giver's `NonScanJob` inside one priority-ordered loop. Ask the question outright, as `WorkGiver_ConnectedDeployment.Plan` does. This one nearly shipped as a bug that review would have passed.
8. **One commitment per worker, across every record kind.** `HasLiveCommitment` is the chokepoint; `ValidateSavedState` enforces it across both saved lists so no save can load with a worker owing two.
9. **Nothing is ever `playerForced`.** Automatic work must not bypass a policy the player set.
10. **No quantity is ever hardcoded.** Every count goes through `MaxStackSpaceEver` / `GetCountCanAccept` / the constructible's own requirement, which is why stack-size mods work for free.
11. **No new gameplay ThingDef, art or audio.** Behaviour is patched onto Core objects and designated at runtime. Match by *capability*, never by name. A `FactionDef` is world configuration and is permitted; a new `PawnKindDef` is not, because M2 is deleting the five that exist.
12. **Zero throwing def lookups.** `GetNamedSilentFail` everywhere; a missing def is an unavailable action, never an exception.
13. **Natural gates have no timer, operator, power or close command.** Ever. Non-corporation starts depend on it.
14. **Nothing in the work layer walks a pawn home.** A pawn that crossed legitimately stays where it is when its errand ends, with its own needs and local work.
15. **Never force-push. Never launch the game. Never alter the RimSort list. No AI attribution anywhere.**
16. **Add definitions; never redistribute assets.** Reference Ludeon's icons and pawn kinds by path and defName. No `PatchOperationReplace`/`Remove` on a Core def. Gate DLC-conditional content with `MayRequire`. Official versions only. Verified and mechanically checked — `COMPLIANCE_AND_OFFICIAL_VERSIONS.md`.
17. **Prefer a setting or a def over a constant** for anything tunable, because the only test session fixes things live without a mod reload.
18. **Needs are not work, and this layer does not reach into them.** Eating and sleeping come from Core's think tree, not from a `WorkGiver`. Do not patch Core's think tree to send a hungry or tired pawn through a gate: a closing gate strands them, and the failure mode is a dead colonist rather than a wasted walk. Solve needs logistically — take the thing to the people. Decided for food in 0.6.0-dev; see `implementation/CONNECTED_FOOD_IMPLEMENTATION.md`.
19. **A resource family must never move the shortage it is solving.** Food will not take the last meal off a map that still has hungry people. Any future family that moves a consumable owes the same guard, because every individual trip looks correct while the net effect is harm.
20. **A bed is only ever a bed on its own map.** `RestUtility.CanUseBedNow` returns false when `building_Bed.Map != sleeper.MapHeld`. Nothing may reserve, assign or own a bed across a gate; Core will refuse it on arrival. Verified at source in 0.6.1-dev.
21. **Before writing a family, check whether an existing one already covers it.** Beds on the far side turned out to need no rest family at all, because cross-gate construction already supplies and finishes them. Writing a redundant family for symmetry is worse than writing none.
22. **A provider answers one *question*, not one Core work giver.** Sowing and harvesting are two givers and one question, so they share a provider; Core's own givers pick whichever applies on arrival. Read Core before splitting a family — refuel and rearm were listed as two and are one, because Core's `RearmTurrets` giver *is* a refuel giver.
23. **Never touch Core's static scan state from a remote probe.** `WorkGiver_Grower.wantedPlantDef` is written by Core during its own scan; reading it is meaningless and writing it could corrupt a scan in progress on another map. Ask about the zone and the things in it instead.

### Binding owner decisions

Full text in `GATE_0_DECISIONS.md` under the two 2026-09-28 headings.

- **Laboratory duration is a ladder**: 108,000 ticks first (~30 real minutes), ×3 per earned tier, no countdown at the indefinite tier — where it still requires power, operator and a successful energy debit every tick. Tier counts **completed projects**, never spendable insight.
- **Natural gates stay permanently open.** Confirmed in source; nothing changed.
- **One research tree for every scenario.** No research, capability or duration rule may be gated on scenario identity.
- **Every company is named by its player**, on every start, renameable any time.
- **Inside start**: configurable party; the **player chooses the first exit destination** — a change from the old fixed-reveal assumption.
- **The campaign opens in the 1990s**, and the factions are the universe's own (US government, rival corporations, disgruntled ex-employees, high-tech thieves, corporate espionage and sabotage, concerned citizens, and more in the same vein). Authored as **new `FactionDef`s reusing existing pawn kinds** — no new pawn kind, texture or item. **All start neutral**, earning hostility from saved observable causes. The period **also constrains starting grants** but never research. Default-set per scenario, tailored per scenario, through the existing start contract and never by a scenario-identity branch in code.
- **Deferments are audited, not appended to.** The four audit questions are in the header of `DEFERRED.md`; ask them every time that file is touched.
- **Validation**: keep building, launch later. No QA pass scheduled.

### Read these first, in this order

**Before implementing any work family, read the relevant profile rows first.** Owner rule, 2026-09-28: *"remembre there are research mods you should always be checking mods too"* and *"thats what the prep work was for"*. The 294 per-mod reviews under `research/reviews/mods/` already carry verified source facts and a recorded disposition for every entry. Re-deriving them wastes the preparation, and the reviews have caught real constraints twice now.

1. `docs/NOW.md` (this file) — where things stand.
2. `docs/DEFERRED.md` — every open row with its named owner, and the four audit questions in its header.
3. `docs/implementation/CONNECTED_WORK_CORE_API.md` — the pinned Core job, reservation, carry, area and spawn facts every adapter depends on, **including its appendix on Core's own map-portal system and why it cannot serve this design**.
4. `docs/implementation/CONNECTED_WORK_IMPLEMENTATION.md` — the engine and the carry families.
5. `docs/implementation/CONNECTED_TRAVEL_TO_WORK_IMPLEMENTATION.md` — the deployment shape, and the Core-method split table.
6. `docs/implementation/DEPENDENCIES_AND_CAPABILITY_MATCHING.md` — the audited zero-dependency position and the capability-matching method.
7. `docs/CONNECTED_COLONY_PORTALS.md` — the governing contract, including the traversal rule and the duration model.
8. `docs/PUBLISHING.md` — the exact push procedure. Follow it literally.

### The checkpoint ritual

1. Read every file in full before editing it.
2. `powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1` — must be zero warnings and zero errors. It refuses to build if the csproj and `About.xml` versions disagree, so bump both.
3. Add a `CHANGELOG.md` entry in plain language, and update the `About.xml` description.
4. Write the implementation record and an evidence folder under `docs/implementation/evidence/<name>-<date>/` with compiler output plus source, package and **recomputed** reference manifests.
5. Update the ledger: `DEFERRED.md`, `TODO.md`, `NOW.md`, `FINALIZED.md` (verbatim owner words), `ROADMAP.md`, `ARCHITECTURE.md`, `SKILL_TREE.md`.
6. Verify: XML parses, every referenced `RR_` key resolves, every `giverClass` resolves to a real class, no attribution strings, and — **after deleting `obj/` and `bin/`** — the rebuilt assembly hash matches the recorded evidence. An incremental rebuild proves nothing about determinism. **Note for any pre-0.5.7 evidence folder:** its hash is *not* reproducible today. The SDK used to embed the git commit in `AssemblyInformationalVersion`, so those hashes were a function of source and commit both; `IncludeSourceRevisionInInformationalVersion=false` fixed that in 0.5.7-dev and the hash is now a pure function of the source. Do not conclude the build is broken — see `implementation/CONNECTED_BILLS_IMPLEMENTATION.md`.
7. Commit once, atomically, then push the feature branch and cascade by refspec to `Prep`, `Develop`, `Main` on **both** remotes, then read back all eight refs. Do not edit anything after the push.

### Practical gotchas learned the hard way

- **Long bash heredocs fail** on apostrophes and quotes — `1990's` killed one this session. Write the text with the Write tool to a `.local/*.md` file, `cat` it on, then delete it.
- **`cd` inside a Bash call persists** and moves the working directory. Use absolute paths.
- Python cannot open `/c/Program Files (x86)/...`; use the `C:\...` form.
- Package manifests are UTF-8 **with BOM** — read with `encoding="utf-8-sig"`.
- Decompile with `.local/tools/ilspycmd.exe -t <FullTypeName>`; pipe through `head` **only after** writing the file, or the output truncates mid-statement. Decompiled Core types already collected live in `.local/inspection-*/`.
- Assembly string literals are UTF-16 in the DLL; a UTF-8 byte search gives false negatives.
- C# 7.3: no target-typed conditionals. `AcceptanceReport` and `bool` will not unify in a ternary.
- `ForbidUtility`, `HaulAIUtility` and `GenConstruct` are all in the `RimWorld` namespace, not `Verse`.

### Blocked on the owner: nothing

**There is no blocked-on-owner status in this project, by owner direction 2026-09-28.** It was removed from `TODO.md` (28 rows) and `DEFERRED.md` (2 rows) in 0.5.6-dev and must not be reintroduced. Nothing here has ever waited on the owner.

Rows that cannot be *closed* without the game running are `[T]` and belong to **one phase, after completion**: the mod is confirmed complete at 100% including its behaviour with Core, the DLC and the mods → the owner sets up the environment → the rim api mod is added → the owner plays and reports, and fixes land **live, without a mod restart and reload**.

Two rules follow from that and bind work now:

- **Prefer settings and data over constants.** Anything hardcoded is something that live session cannot fix. The eight work-giver priorities became live settings in 0.5.6-dev for exactly this reason; hold every future tuning value to the same test.
- **Never ask the owner to launch in order to continue building.**

Compliance is also a standing release requirement with a verified position and mechanical checks — see `COMPLIANCE_AND_OFFICIAL_VERSIONS.md`. It binds the faction layer before a line of it is authored.

---

## Next up (from the cascade)

**Immediate:** bills and unfinished work, per the design notes above. Then research (as a travel-to-work provider), tending across a gate, food, rest, and the remaining work families — one at a time, each with source evidence per route.

**Then** the 1990s period and the universe faction layer, per the recorded decisions.

**Then** M1 step 5 (the saved bounded escalation ladder before any inhabitant generation ships, procedural inhabitants, optional provider adapters) and step 6 (connected-site scheduling and streaming).

**Then** M2 existing-content replacement, unblocked on content grounds by capability matching — remaining work is implementation plus the save-migration decision, shared with the legacy threshold repair already built. Then M3 breadth, M5 interface, M6 release.

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
