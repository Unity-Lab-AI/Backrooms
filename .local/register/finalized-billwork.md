
---

## 2026-09-29 — Somebody finally runs the bill on the far side (0.6.5-dev)

### Verbatim owner requests

> *"cool lets get to it remeber the goal: completing the AAA Mod Rimrooms - Async Industries"*

> *"make sure u are using the prep docs and the mod spreadsheet and still thinking critical at how we impliment our mods needs across the mods"*

> *"rememrb we are making a mod that works with the other 274, WE ARE NOT EDITING OTHER PEOPLES MODS!"*

### The gap closed

- [x] **Ingredients had been crossing a gate to a bill since 0.5.7-dev and nobody was ever sent to work the bench.** A coordinate with a stove, a live bill and delivered ingredients produced nothing unless a colonist happened to be standing there. `CONNECTED_BILLS_IMPLEMENTATION.md` settled the supply half completely and never decided this one.
- [x] **The deployment shape is correct here by construction, not as a workaround.** `ClosestUnfinishedThingForBill` validates `Creator == pawn` and `Bill_ProductionWithUft` binds `BoundUft` to a `BoundWorker`, so a half-made thing belongs to one colonist — which is exactly why the *carry* family must never touch one, and exactly why a **deployed** worker running Core's own `WorkGiver_DoBill` on the bill's own map is right. The same Core fact forbids one family and enables the other.
- [x] **Five families, one per work type, because Core draws that line itself.** `StartOrResumeBillJob` compares `bill.recipe.requiredGiverWorkType` against `def.workType`, and a bench belongs to a work type only through `WorkGiverDef.fixedBillGiverDefs`. One provider would have had to declare one work type and would have pulled a cook across a gate for smithing. **Twenty-seven families now, nineteen of them deployments.**
- [x] **The bench set is read from the loaded defs, never from a list of names** — the union of `fixedBillGiverDefs` across every `WorkGiverDef` of that work type whose giver class is `WorkGiver_DoBill` or a subclass. A mod adding a bench to an existing work type is covered with no code and no mention of its name. Match-by-capability applied one level deeper than usual.

### A shipped defect found by checking the hierarchy instead of trusting the names

- [x] **`ConnectedBillAdapter` had been supplying autonomous and mech bills for five checkpoints while its own record said it did not.** Its filter was `if (!(bill is Bill_Production)) return false;` — but `Bill_Autonomous : Bill_Production` and `Bill_Mech : Bill_Autonomous`, so both *are* `Bill_Production` and passed straight through the test written to exclude them. Both families now share one type test in `ConnectedBillScan.OrdinaryProductionBill`, which excludes `Bill_Autonomous` explicitly. `Bill_ProductionWithUft` stays included; `Bill_Medical` is excluded by deriving from `Bill` directly.
- [x] **Shared rather than duplicated.** Both bill families ask about the same bills from opposite senses — *is it short of something* versus *does it have what it needs* — so `ConnectedBillScan` owns the primitives and the adapter delegates. The hierarchy defect above is what a second copy of a rule looks like in practice.

### Core rules split by what each one reads, verified not assumed

- [x] **`PawnAllowedToStartAnew` is safe to ask remotely** — it reads the bill's pawn restriction, its slaves-only/mechs-only flags and the pawn's skill against `allowedSkillRange`, and **none of it reads the pawn's map**. That is the check that stops a bill restricted to one named colonist, or to a skill band, from dragging the wrong worker through a gate, and it costs nothing at planning time.
- [x] **`nextTickToSearchForIngredients` is read and never written.** Core's own throttle; writing Core's scan state from a remote probe is forbidden. Reading it means a bill that just failed for somebody does not immediately pull somebody else across.
- [x] **Left to arrival deliberately:** `TryFindBestBillIngredients`, every reservation, the interaction cell, the pawn form of the forbidden check, and the whole unfinished-thing resolution.
- [x] **One deliberately approximate test, documented as such.** `EveryIngredientPresent` is **necessary, not sufficient**. It exists because a coordinate with a bench, a live bill and no materials would otherwise look like work forever — Core's throttle cannot help, since `nextTickToSearchForIngredients` only moves when a pawn tries and fails, and **on a map nobody stands on nobody ever tries**. A false positive costs one walk; a false negative costs one planning delay. Written down so a later session does not "improve" it into a reimplementation of Core's allocator.

### The register was used, and updated forward

- [x] **Five profile rows read before writing, and their answers recorded back into the register.** 260 While You Are Nearby (reorders scanning givers; these are `NonScanJob` with one candidate, nothing to reorder); 67 Compact Work Tab (ten more givers, fifty-seven total; added givers inside existing types is weaker than added types); 53 Big Little Mod Patch (anything it links is covered, nothing named); 246 VFE Factory (covered if its work types are among the five — a modded *work type* is a named limit, not a claim); 96 Fueled Crematoriums (Core hands out a refuel job instead of the bill, so `UsableForBillsAfterFueling()` is required and fuel is pulled rather than a worker).
- [x] **Nothing of anyone else's was edited, copied, patched, replaced or bundled**, per the owner's direction. These are our notes about our own behaviour alongside theirs, and the compliance check confirms zero destructive patch operations again.

### One priority interaction named rather than papered over

- [x] **Rimrooms' own `RR_DoGateAssembly` sits at 100 in Crafting, so the Crafting continue giver at 102 outranks it.** That follows the rule every family follows — a committed traveller is never turned around — and it is tunable live. Recorded because it is the one new number landing above existing *Rimrooms* work rather than only above Core's. Fifty-four cross-gate numbers now, all player settings.

### Documents updated in the same change

`implementation/CONNECTED_BILL_WORK_IMPLEMENTATION.md` (new record), `TODO.md`, `DEFERRED.md`, `NOW.md`, `CHANGELOG.md`, `research/WORK_TYPE_COVERAGE_AUDIT.md`, `ARCHITECTURE.md`, the register CSV and both register outputs, `About.xml`, the csproj.

### Build evidence

0.6.5-dev, SDK 9.0.308, Release/net472, zero warnings and zero errors with `TreatWarningsAsErrors` enabled. **114** C# source files (two new), **76** approved package files (unchanged; ten giver defs and ten keyed strings added to existing files). Assembly SHA-256 `51D2DB71724A7559FCE6092406040C6660EDCF15817732511D74C3A018D7E8EC`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`. Evidence folder `implementation/evidence/bill-work-2026-09-29/`. All 58 packaged XML files parse; every `RR_` label and settings key resolves with 0 missing; all 57 Rimrooms `giverClass` references resolve; all 27 priority pairs name real defs with keyed labels; reference manifest recomputed with no drift; `audit-gate0.py` PASS with zero errors; no attribution strings. Published via the cascade in `PUBLISHING.md`; refs read back in session output. No game launched, no test run, no RimSort profile touched.

### SESSION SUMMARY

Source files created: 2. Source files modified: 4. Package files modified: 3 (no new files). Docs updated: 7 (1 new).
Owner directions captured verbatim: 3. Work families: **27, nineteen of them deployments**.
Shipped defects found and fixed: 1 (five checkpoints of autonomous and mech bills being supplied contrary to the record).
Core facts verified rather than assumed: 4. Profile rows consulted and updated: 5.
Still open of the four gaps: DarkStudy, hauling upkeep, BasicWorker (with Fishing a generation question first).
