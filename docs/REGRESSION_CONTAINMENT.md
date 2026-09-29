# Regression containment and completion tracking

**Owner instruction, 2026-09-28:** keep the master TODO checked against actual completed work, and contain regressions while extending the mod. This rule applies to every implementation wave and delegated assignment.

## Before changing a working path

1. Identify the current compiled checkpoint and source record. Read the affected feature's canonical contract, callers, saved owners, Def/provider bindings and existing recovery paths.
2. Record a short impact list: files owned by this task; callers that may need changes; saved fields/enums/IDs; player actions; optional-provider behavior; and existing functionality that must continue working.
3. State deliberate behavior changes separately from preserved behavior. The owner's newer native-content or scenario direction can supersede an old implementation, but replacing its provider must preserve the promised gameplay function.
4. Give parallel agents exclusive file scopes. The lead owns shared integration and resolves conflicts before compiling or publishing. Preserve unrelated and uncommitted work.

## During implementation

- Keep one authoritative owner for money, pawns, inventory, coordinates and operation receipts. New components must not create a second balance, copy a pawn, remint lost evidence or regenerate an established site.
- Preserve stable saved identifiers and enum values. Append values rather than renumbering. Changes to saved meaning require an explicit migration or a documented development-save boundary, with old builds/saves retained.
- Review every caller when an interface or provider changes. Update creation, readiness, work jobs, UI, recovery, serialization and package references together. A new happy path must not disable recall, rescue, cancellation, partial delivery or retry of the original object.
- Keep existing native work, needs, equipment, power, doors and optional-mod behavior outside the scoped Rimrooms role. Provider absence produces a clear fallback/refusal rather than an exception or a silently substituted object.
- Bound active work and histories without deleting unresolved people, cargo or journals. Explain any intentional summary/archive boundary and preserve reconciliation totals and stable IDs.
- If a change exposes an earlier defect, record and fix it in the owning scope. Do not hide the error, weaken checks or remove a feature just to make the build pass.

## Before closing a source task

Compare the change against its impact list and inspect the neighboring paths. Compile the integrated source against the pinned references and save the actual output/package identity when publishing a build. A successful compile proves compiler/API consistency only. Preserve the previous installed package when staging and verify the copied package identity; do not launch the game or alter RimSort's profile.

Update the feature implementation record, canonical contracts when behavior changed, and the master TODO in the same wave. Each checked item must name its saved evidence and its completion scope: **source**, **build/package**, **document integrity**, or **observed runtime**. Do not leave completed source work represented only by an unchecked broad feature; add bounded checked subitems. Keep the broad item open when its remaining behaviors or required acceptance are unfinished. Reopen an item if later evidence contradicts its completion, with a reason and recovery task.

## Milestone publication

Publish both authorized remote cascades after a meaningful implementation milestone is integrated and its evidence is saved. Batch code, related contracts, TODO status and build/package records together. Do not push routine edits, every agent result or progress notes individually. Each publication includes all current project changes after active agent work is integrated. Read back the resulting remote refs in tool output; do not create a new local-only receipt after publishing. This cadence does not permit skipping a necessary correction to an already published defect.

## Runtime regression queue

Record the affected cases for the later owner-launched disposable session: old/new saves, repeat actions, interrupted transactions/transfers, provider present/absent, native controls, and any directly connected previously implemented loop. Include scenario → company → gate → expedition → return → analysis → payment → revisit when a change touches that chain. Add focused cases for staffing, shipments, UI and menu behavior when applicable.

These are future acceptance cases, not results or permission to start RimWorld. The owner alone launches through RimSort; attach RimBridgeServer only under the saved QA plan. Do not call compilation, source review, a passing document audit or another agent's message a runtime regression pass. Keep independent coding moving while those cases are deferred.

## Doc-rot sweep — every owner decision, checked against the live docs

**Owner direction, 2026-09-29, verbatim:** *"make sure no docs in docs have retoffeed or regressed with all ive said"*

A decision that is recorded in one file and contradicted in another is worse than an unrecorded one, because the next session reads whichever it opens first. This has now bitten three times: `NOW.md` claimed three answered questions were still open; `TODO.md` did the same; and `SCENARIO_SETUP_AND_PORTAL_NETWORK.md` contradicted **itself**, describing the inside-start choices as pending in one paragraph and recording their answers in another.

So the sweep is a standing step, not a one-off. **Run it whenever an owner decision lands, and before any publication that records one.**

### What counts as a live doc

Only forward-looking docs can rot. These are **archives** and legitimately describe past state — never rewrite them to match the present:

- `FINALIZED.md`, `GATE_0_DECISIONS.md`, `DECOMPOSED.md`, `CHANGELOG.md`
- everything under `docs/implementation/` (per-checkpoint records) and `docs/research/` (source reviews)
- every `evidence/` folder

Everything else in `docs/` is live and must agree with the current decisions.

### The checks

Grep every live doc for each superseded claim, and treat a hit as rot **unless** the same line also supersedes, answers or withdraws it. Current list, with what the truth is:

| Stale claim to grep for | Current truth |
|---|---|
| `20 in-game minute` opening, or an access ladder of 2 hours / 1 day / 7 days / 30 days | 108,000 ticks first (~30 real minutes at normal speed), ×3 per earned tier, no countdown at the indefinite tier while power, operator and energy hold |
| `833` ticks as the portal window | Legacy expeditions only; portal sessions use the ladder |
| `fixed discovered` first-exit destination | **The player chooses** the destination settlement |
| `[!]` status marker, or `owner-blocked` / `blocked: owner` / `blocked on the owner` | No blocked status exists. `[T]` = post-completion test phase, which gates nothing |
| A hardcoded company identity | Every start names its own company; *Async Industries* is a suggested default only |
| Per-scenario or scenario-specific research or tech | **One** tech tree available to every scenario; no rule may be gated on scenario identity |
| Refuel and rearm as two families | One family — Core's own `RearmTurrets` giver *is* a refuel giver |
| A hungry or tired pawn crossing a gate for a need | Decided against: needs are not work, and a closing gate strands them. Take the thing to the people instead |
| A joy or recreation work family, or a ritual work family | Both decided against 2026-09-29. **Joy has no work type at all** — 23 exist across Core and all five DLC and `Joy` is not among them. **No `WorkGiverDef` anywhere is ritual-driven**; a `LordJob_Ritual` owns its participants' duties |
| Any family count other than the current one (twenty-two, twenty-seven, …), or the remembered families list treated as complete | **28 families, 20 of them deployments** as of 0.6.6-dev. Hauling upkeep and BasicWorker remain; `Fishing` is a generation question first. The remembered list was **not** complete — `DarkStudy` and `Fishing` were missing entirely. `research/WORK_TYPE_COVERAGE_AUDIT.md` is the enumeration and the only count worth quoting. **Update this row's number in the same change as any new family** rather than adding another row beside it |
| Bill work described as an open gap, or as one family | **BUILT 0.6.5-dev as five families**, one per work type, because Core compares a recipe's `requiredGiverWorkType` against the giver def's own `workType` |
| A def referencing DLC-only content without `MayRequire`, or the claim that the compliance check covers it | It does **not** — it looks for DLC *package ids*, and a def referencing `Childcare` never mentions Biotech. `tools/check-dlc-gating.py` indexes the game's own data and must pass |
| `is Bill_Production` used as a test that excludes autonomous or mech bills | It does **not**. `Bill_Autonomous : Bill_Production` and `Bill_Mech : Bill_Autonomous`. Use `ConnectedBillScan.OrdinaryProductionBill` |
| The register workbook as a hand-maintained file, or its Overview family tallies as stored numbers | Generated output. `tools/research/build-mod-register.py` builds it from the CSVs under `docs/research/`; tallies are **counted from the rows every build**, never stored. Hand-editing the workbook loses the edit on the next build |
| The register preview PNGs under `outputs/` as showing the current file | They depict the **superseded two-sheet layout**. Both registers now carry four views: Overview, Index, Full register, Mod cards |
| The `.xlsx` workbook as the register anybody reads, or telling the owner to open it | **There is no spreadsheet application on this machine and no `.xlsx` association at all.** The register that gets read is `Rimrooms_Async_Industries_294_Mod_Integration_Register.html` -- browser, no install, offline. The workbook is still built and verified, but it is the secondary output |

Add a row every time a decision supersedes something. A check that is not written down here is a check that will not be run.

### DLC-only defs must be gated, and the check is not optional

Any def that references content from an expansion must carry `MayRequire` naming that
expansion's package id. This is **not** covered by the compliance check, which looks for DLC
package ids rather than DLC def *names*: a `WorkGiverDef` reading `<workType>Childcare</workType>`
never mentions Biotech anywhere, and shipped ungated from 0.6.4-dev to 0.6.6-dev because of it.

```
python tools/check-dlc-gating.py
```

It indexes every `defName` under `RimWorld/Data/*/Defs/**`, treats anything not defined by
`Core` as DLC-only, and fails on an ungated reference. Reading the game's own data is the
point — a hand-written list of DLC def names would rot exactly the way the thing it checks
rotted. Run it whenever a def is added or edited.

**Handling a DLC def correctly in C# is not sufficient.** `GetNamedSilentFail` makes the
*code* degrade; it does nothing for an unresolved cross-reference in the *def*. Both halves
are required, and that mismatch has now produced two defects in two consecutive checkpoints.

### The register is generated, and must be rebuilt in the same change

Any edit to `docs/research/rimworld-server-mod-inventory.csv`, `mod-register-integration-fields-2026-09-29.csv` or `mod-register-overview-2026-09-29.csv` must be followed in the **same commit** by:

```
python tools/research/build-mod-register.py
python tools/research/check-mod-register.py
python tools/research/audit-gate0.py
```

All three must exit zero. `audit-gate0.py` compares 3,234 workbook cells against the inventory independently of the checker, so a register change that passes the checker but breaks the audit is a real disagreement to resolve, not a nuisance. The workbook rebuilds byte-identically from an unchanged source, so a diff on it in `git status` always means the sources actually changed.

Both outputs are produced by the one build command, so they can never disagree; `check-mod-register.py` round-trips the workbook cell by cell **and** validates the HTML (every mod carded and linked, every value present through the same escaper that wrote it, filters complete, tags balanced, zero external assets).

**A note learned the hard way:** the audit's link scanner strips fenced code blocks but **not** inline code spans, so quoting a broken markdown link inline in a doc recreates it and fails the audit. Fence it.

### What the 2026-09-29 sweep found and fixed

Eleven corrections across ten live docs, plus twelve in `ROADMAP.md`:

- `ARCHITECTURE.md` still listed all three answered owner questions as **open**, including the 833-tick window.
- `CAMPAIGN_ECONOMY_MODEL.md`, `CAMPAIGN_ROSTER_FREEZE.md`, `FIRST_PLAYABLE_CONTRACT.md`, `FIRST_SLICE_CONTENT_INVENTORY.md` and `SCENARIOS.md` all still asserted the 20 in-game-minute opening as current, two of them with the superseded 2-hour/1-day/7-day/30-day ladder.
- `ROADMAP.md` still defined `[!]` in its status legend and used it in eight places, still said the owner's launch "unblocks" things, and still posed the two inside-start questions as pending with the withdrawn fixed-reveal assumption.
- `SCENARIO_SETUP_AND_PORTAL_NETWORK.md` contradicted itself as described above.
- `DEFERRED.md` had two residual owner-blocked phrasings.

Superseded values were **kept and marked superseded** rather than deleted, per the never-delete-information rule, so the trail stays readable.

## Required task-record fields

`TODO/feature IDs · baseline build/commit · owned paths · affected callers and saved fields · deliberate changes · preserved behavior · source/build evidence · remaining regression cases · TODO updates`

Read this with [AGENTS.md](../AGENTS.md), [master TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md), [save policy](SAVE_MIGRATION_POLICY.md), [build instructions](BUILDING.md), and the [current company checkpoint](implementation/PHASE_3_BUILD_RECORD.md).
