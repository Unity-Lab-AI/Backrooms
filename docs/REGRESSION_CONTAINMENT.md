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

## Required task-record fields

`TODO/feature IDs · baseline build/commit · owned paths · affected callers and saved fields · deliberate changes · preserved behavior · source/build evidence · remaining regression cases · TODO updates`

Read this with [AGENTS.md](../AGENTS.md), [master TODO](PREPRODUCTION_AND_IMPLEMENTATION_TODO.md), [save policy](SAVE_MIGRATION_POLICY.md), [build instructions](BUILDING.md), and the [current company checkpoint](implementation/PHASE_3_BUILD_RECORD.md).
