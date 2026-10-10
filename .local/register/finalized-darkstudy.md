
---

## 2026-09-29 — Study what you contain, through a gate, and a DLC gate that was never there (0.6.6-dev)

### Verbatim owner request

> *"okay get to it"*

Continuing the standing instruction: *"you are NOT to stop untill i tell you to stop or you reach the completeion of the mod's build out"*, and the goal restated as *"completing the AAA Mod Rimrooms - Async Industries"*.

### The family

- [x] **A researcher crosses a gate to study a contained entity on the other side.** Thematically the most apt family in the whole work layer — a company that reaches unstable spaces through a machine gate, holds what it finds and learns from it. A containment facility behind a portal is the premise of the mod and until now nobody would walk to one. **Twenty-eight families, twenty of them deployments.**
- [x] **Core hands the candidate half over directly, and this is the cleanest split so far.** `WorkGiver_StudyBase.PotentialWorkThingsGlobal` is `Find.StudyManager.GetStudiableThingsAndPlatforms(pawn.Map)` — it takes the map as an **argument** — and that method is a **pure read of a per-map cache** that returns an empty set for a map it does not know and mutates nothing. So asking about a map nobody stands on is fair, cheap and *exact*, with no reimplementation and no risk of touching Core's scan state from a remote probe.
- [x] **`EverStudiable()` and `CurrentlyStudiable()` are safe from here, verified in source.** Between them they read the studied thing, its parent holder, its own comps, the player-set prisoner interaction mode and the global tick. **Neither takes a pawn and neither reads any worker's map.** Left to arrival: `CanReserve` on **both** the platform and the held pawn, because Core reserves both, and the identity check that nobody is sent to study themselves.
- [x] **An empty platform is not work.** A holding platform is the work *target* but the entity held on it is the studiable thing — the same substitution Core makes in `HasJobOnThing`. Core then dereferences `TryGetComp<CompStudiable>()` **without a null check**, trusting its cache; this provider null-checks anyway, because a remote probe that threw would take down an unrelated work scan on the worker's own map.
- [x] **A rotating window over an unindexed collection.** The studiable set is a `HashSet<Thing>` with no stable index, so the scan skips to a per-worker offset, takes up to twelve, and re-enumerates once to pick up the wrap. Re-enumerating a `HashSet` allocates nothing. The arrival check stays unwindowed, as every deployment's does.
- [x] **Anomaly content that degrades rather than claiming support.** `WorkTypeDefOf` declares `DarkStudy` as `[MayRequireAnomaly]`, so `GetNamedSilentFail` returns null without it and the provider is unavailable. Core agrees: `WorkGiver_DarkStudyInteract.ShouldSkip` is exactly `return !ModsConfig.AnomalyActive;`.
- [x] **Register consulted first.** Row **8 Anomaly** is *"optional native anomaly touchpoints; Rimrooms supplies its own Core threat, evidence, and containment loops"* — so the campaign must stay whole without the expansion, which is what an unavailable provider gives. Rows **138 Move Your Monolith** (*"not a Rimrooms gate or navigation system"*), **140 Name Your Entities** (display naming only) and **39 Anomaly Research Asteroid** (optional expedition content, no adapter) were checked and none touches this route.
- [x] **Priority:** continue **112**, above Core's only `DarkStudy` giver (`StudyInteract`, 110); plan **2**, below everything local. Fifty-six cross-gate numbers, all player settings.

### A second shipped defect, the same shape as the last one

- [x] **The two childcare giver defs had referenced the Biotech-only `Childcare` work type with no `MayRequire`, since 0.6.4-dev.** On a Core-only install that is an **unresolved cross-reference at load** — a red error in a mod whose entire stated position is that it needs nothing but base Core. The C# side had always been right (`ChildcareProvider` uses `GetNamedSilentFail` and the 0.6.4 record describes that accurately); only the XML half was missing, and nothing checked it. **This is precisely the shape of the `Bill_Production` defect found in the previous checkpoint** — careful C# beside a def that quietly contradicts it. Both childcare defs are now gated Biotech; both new dark study defs Anomaly.
- [x] **The existing compliance check could never have caught it, and now something can.** That check looks for DLC **package ids** appearing ungated; a def reading `<workType>Childcare</workType>` never mentions Biotech at all. `tools/check-dlc-gating.py` indexes every `defName` under `RimWorld/Data/*/Defs/**`, treats anything not defined by `Core` as DLC-only, and fails on an ungated reference — **6,063 DLC-only defs indexed, 4 references in the package, all gated.** Reading the game's own data rather than a maintained list is the point: a list would rot exactly the way the thing it checks rotted. Prose is excluded by tag, because a keyed string whose English text collides with a defName is not a cross-reference; the live example is the word `Researcher` inside `<RR_Role_research>`. **Verified by deliberately removing a gate, confirming the failure was reported, and restoring it.**
- [x] **Written into the ritual and the invariants**, with the lesson stated plainly: handling a DLC def correctly in C# is **not sufficient**, and that mismatch has now produced two defects in two consecutive checkpoints.

### Anomaly work deliberately not given its own family

- [x] `ExtractBioferrite` and `DoctorTendToEntities` are `Doctor` givers; `ActivitySuppression`, `ExecuteEntity`, `ReleaseEntity` and `InterrogatePrisoner` are `Warden` givers. Both work types already have deployments, so a worker crossing for tending or wardening does this work locally on arrival. No separate family is needed and none is claimed. `TakeEntityToHoldingPlatform` and `TransferEntity` are `Hauling` givers and belong to the hauling upkeep gap.

### Documents updated in the same change

`implementation/CONNECTED_DARK_STUDY_IMPLEMENTATION.md` (new record), `TODO.md`, `DEFERRED.md`, `NOW.md` (two new invariants, a new ritual step), `CHANGELOG.md`, `REGRESSION_CONTAINMENT.md` (two rot checks and the gating section), `research/WORK_TYPE_COVERAGE_AUDIT.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `About.xml`, the csproj.

### Build evidence

0.6.6-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **115** C# source files (one new), **76** approved package files (unchanged; two giver defs and two keyed strings added to existing files). Assembly SHA-256 `238DA7119BECD99E080312C23FAC129E6996C805AD2A48A1E2405656CF86DEA0`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence folder `implementation/evidence/dark-study-2026-09-29/`. All 58 packaged XML files parse; every `RR_` key resolves with 0 missing; every Rimrooms `giverClass` resolves; all **28** priority pairs name real defs with keyed labels; `check-dlc-gating.py` passes; `audit-gate0.py` PASS with zero errors; reference manifest recomputed with no drift; no attribution strings. Published via the cascade in `PUBLISHING.md`; refs read back in session output. No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 1. Source files modified: 3. Package files modified: 3 (no new files). Tools created: 1. Docs updated: 9 (1 new).
Work families: **28, twenty of them deployments**. Gaps remaining: hauling upkeep and BasicWorker, with `Fishing` a generation question first.
Shipped defects found and fixed: 1, and it is the second of the same shape in two checkpoints — careful C# beside a def that contradicts it.
Blind spots closed in the checking tools: 1 (the compliance check cannot see DLC def *names*, only package ids).
Core facts verified rather than assumed: 3. Profile rows consulted: 4.
