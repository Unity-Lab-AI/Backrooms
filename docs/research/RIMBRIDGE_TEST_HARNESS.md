# RimBridgeServer test harness plan

**Status:** selected for post-build RimWorld testing; not installed, configured, or run for this project. Do not start or interact with RimWorld for project testing until a Rimrooms build exists. The owner launches every test session through RimSort; this plan attaches RimBridgeServer after launch.

## Role in this project

[RimBridgeServer](https://github.com/pardeike/RimBridgeServer) is an auxiliary RimWorld-side test bridge. Its upstream README describes live state and UI inspection, screenshots, debug actions, mod/load-order and settings controls, and JSON/Lua automation. The upstream project recommends [GABS](https://github.com/pardeike/GABS) as a general start/attach layer. Rimrooms uses RimSort for profile management and launch, so the planned route is RimBridgeServer direct mode attached to the already-running, owner-started test game; GABS is optional only if an attach-only connection is verified.

RimBridgeServer and GABS are test/development tools, not Rimrooms dependencies, required player mods, or files to bundle. The upstream RimBridgeServer repository is MIT licensed as checked on 2026-09-28. Do not copy its source or binaries into Rimrooms; install the chosen test release separately and record its provenance.

## Isolation rules

RimBridgeServer can drive game actions and change enabled mods, load order, and mod settings. Every run therefore uses a disposable RimWorld test instance/profile, disposable saves, and a copied RWT server configuration where needed. Never attach the bridge to the owner's active game, live RWT server, or campaign saves. Before a run, verify the active game executable, mod root, `ModsConfig.xml`, save-data path, test-server directory, and loaded profile. Keep each RWT client attached to its own named profile/session; the dedicated RWT server is managed separately from the RimWorld clients.

Use RimBridgeServer direct mode for this project because RimSort owns process launch. Pin the exact RimBridgeServer release and record the local bridge port/token from the test log; keep the endpoint local to the test machine. Do not invoke GABS' start/stop workflow. Use GABS only if its attach-only connection to the already-running RimSort session has been verified and it leaves the selected profile untouched. Confirm both clients can be controlled at once for an RWT case before relying on automation.

## Test workflow

1. Build the current package in `Mod/Rimrooms - Async Industries/` and stage only that folder into the Local Mods path configured in RimSort. Follow the [RimSort package/launch plan](RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md): RimSort sorts the existing 294 entries plus Rimrooms into a 295-entry product target. For bridge-driven tests, enable RimBridgeServer as a separate QA overlay in the disposable RimSort profile; the game normally loads 296 entries (295 target plus bridge, plus any extra documented harness dependency). Do not replace any target mod to preserve the 295-target profile. The upstream debugging-stack guide uses Harmony; record all test-only entries separately from Rimrooms' player-facing dependency contract.
2. Capture exact game executable/Core hashes, runtime-reported build, DLC state, RimSort version, the 295 target IDs/order and the complete QA overlay IDs/order, Rimrooms commit/build, bridge version, server config hash, and save/profile identity.
3. After the owner starts the isolated profile through RimSort, connect to that already-running process in RimBridgeServer direct mode. Record its reported game/load state before changing the save. Discover the live tool surface rather than assuming tool names or schemas from an earlier release. Do not use a bridge action to launch the game, enable/disable mods, or reorder the saved profile.
4. Use the bridge for repeatable setup, state checks, bounded actions, UI verification, and screenshots. Use the relevant power, logistics, RWT, scenario, or feature acceptance plan for the case-specific assertions.
5. Save the bridge logs, game logs, screenshots, save identifiers, action/case results, and before/after item, pawn, ownership, ledger, and coordinate state needed by that plan. Restart/reload when the case requires it, then verify recovery and duplicate/loss behavior.
6. Record failures and bridge-side errors as findings. A successful bridge call or game load is not itself evidence that the tested gameplay behavior passed.

## Scope and limits

- RimBridgeServer can assist with local client automation and evidence capture; it does not itself establish RWT server behavior, offline visits, cross-client item delivery, or multiplayer synchronization.
- Test RWT workflows with two isolated client profiles and the disposable server; the owner starts each client through RimSort. Verify simultaneous bridge sessions and keep server logs/settings alongside client evidence.
- Keep every in-game test in the post-build acceptance stages in [`PREPRODUCTION_AND_IMPLEMENTATION_TODO.md`](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md). The existing [RWT run sheet](RWT_BASELINE_TEST_PLAN.md), [power acceptance cases](POWER_GATE_AND_TURRET_SOURCE_AUDIT.md), and [physical logistics plan](PHYSICAL_LOGISTICS_BASELINE_TEST_PLAN.md) remain prepared plans, not results.
- If a Rimrooms-specific bridge companion is ever proposed, document its exact need separately. The current plan does not add the RimBridgeServer SDK or a bridge companion to the mod.

## Upstream references

- [RimBridgeServer repository and README](https://github.com/pardeike/RimBridgeServer)
- [RimBridgeServer architecture notes](https://github.com/pardeike/RimBridgeServer/blob/main/docs/architecture.md)
- [Upstream RimWorld debugging-stack setup](https://github.com/pardeike/RimBridgeServer/blob/main/docs/rimworld-mod-debugging-stack.md)
- [RimBridgeServer license](https://github.com/pardeike/RimBridgeServer/blob/main/LICENSE)
- [GABS repository and setup guide](https://github.com/pardeike/GABS)
- [RimSort package staging and owner-operated launch plan](RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md)

The upstream tool surface and setup may change. Recheck the chosen release's README, supported RimWorld version, installation layout, launch profile, and license when configuring the first post-build test environment.
