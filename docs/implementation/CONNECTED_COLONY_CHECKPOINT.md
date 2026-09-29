# Connected-colony foundation checkpoint — 0.4.1-dev

**Owner-directed stopping point:** wrap the current work, publish all current source/docs/evidence through both remote cascades, and pause further work to conserve weekly usage. The full mod is unfinished. Resume from this file and [the task](CONNECTED_COLONY_IMPLEMENTATION_TASK.md), not from the historical dispatch-only design.

## Included source

- Independent saved portal graph, immutable endpoint references and permanent-natural lifetime; [network record](CONNECTED_NETWORK_IMPLEMENTATION.md).
- Resumable bidirectional topology search with retained cursors, loop detection, explicit pending/invalidation states and live availability checks. Route discovery is not native pawn pathfinding or job scheduling.
- Separate laboratory connection/session IDs, physical power/timer ownership, recovery charge receipts and saved owner validation; historical expedition fields remain readable and separate.
- Content version 4 uses an existing Core steel door as the generated return threshold. Existing saved sites are preserved.
- Physical crossing API and receipt/custody work in [the crossing record](CONNECTED_CROSSING_IMPLEMENTATION.md). It remains unconnected to ordinary job scheduling/player travel and must not be represented as completed unified work.
- Pinned [Core API review](CONNECTED_WORK_CORE_API.md), [migration review](CONNECTED_PORTAL_STATE_MIGRATION.md), and [profile boundaries](CONNECTED_WORK_PROFILE_BOUNDARIES.md).

## Resume in this order

1. Review the crossing service's documented permission, recovery and state boundaries before connecting callers. Finish unresolved constraints rather than weakening checks. Preserve original pawns/cargo and no-wipe landings.
2. Add explicit address registration and discovery using the existing campaign coordinate/site owner. Preserve seeds and visited maps; provide an explicit legacy saved-endpoint repair path. No auto-conversion of active legacy missions.
3. Implement ordinary local threshold approach/crossing jobs and player controls without crew/manifests. Wire laboratory open/close/recovery and permanent natural links. Define the remaining emergency-return route without duplicate debits or teleporting stranded workers home.
4. Implement saved work intents, quantity leases and native destination job revalidation; then physical hauling, construction, bills, research, medical/food/bed and other work/needs families. Preserve priorities, schedules, areas, locks, custody and actual inventory. A generic graph does not implement these adapters.
5. Integrate exact optional work/storage providers and scenario openings, then procedural inhabitants, rare monstrosities, saved events and tech-driven complexity. Keep every wider master TODO feature in scope.
6. Continue source/build milestones. Runtime acceptance remains deferred until the owner launches through RimSort; no agent game launch or profile change.

## Evidence and publication

Final compiler output, source hashes and package/reference manifests are saved in [the checkpoint evidence folder](evidence/connected-colony-2026-09-28/). Compilation establishes API consistency only; no game/tests/runtime compatibility result is claimed. This checkpoint does not stage over the owner's existing installed 0.4.0 package; the updated copyable package is in the repository's `Mod/Rimrooms - Async Industries/` directory.

The integrated build uses SDK 9.0.308, Release/net472, **75 C# source files**, **71 approved package files**, and reports **zero warnings and errors**. The [package manifest](evidence/connected-colony-2026-09-28/package-manifest.json) owns the exact final DLL SHA-256; [source manifest](evidence/connected-colony-2026-09-28/source-manifest.json) identifies each compiled source input, and [compiler output](evidence/connected-colony-2026-09-28/build-output.txt) records the build result.

The authorized publication order is `feature/preproduction-handoff` → `Prep` → `Develop` → `Main`, separately on Forgejo and GitHub. Readback of all eight remote refs is the publication evidence in tool output. Do not create another local-only receipt after the push. Normal ignored build/dependency/reference files remain reproducible local artifacts; all current project source, documentation and saved evidence belong in the checkpoint commit.
