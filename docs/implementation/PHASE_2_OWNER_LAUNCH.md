# Development 0.2.0: first owner-launched session

This is the first-expedition development package, with gameplay acceptance still pending. It is not the complete campaign release. The [build record](PHASE_2_BUILD_RECORD.md) lists implemented systems and the remaining work; the [master backlog](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md) preserves the full mod scope.

## Installed packages

Use the exact [Rimrooms staging receipt](evidence/phase2-first-expedition-2026-09-28/staging-receipt.json) and [QA bridge receipt](evidence/phase2-first-expedition-2026-09-28/rimbridge-staging-receipt.json) to identify installed files. Both packages occupy separate folders under the Local Mods directory read from the current RimSort instance. The bridge is optional QA tooling and is not part of the Rimrooms package.

## Owner's launch steps

1. In RimSort, preserve the existing profile and choose a disposable test profile. Refresh Local Mods so **Rimrooms - Async Industries 0.2.0** and **RimBridgeServer 2.1.1** are discoverable.
2. Keep the complete original 294-entry target and add Rimrooms: **295 product entries**. Enable the separate bridge overlay for this session: normally **296 loaded entries**. Keep Harmony once; it is already in the target. Review dependencies and sort/save using RimSort.
3. Launch RimWorld through RimSort and stop at the main menu. Report that this owner-launched session is ready. Leave the bridge token private; the local client can read it from that session's log.
4. After the initial read-only capture, use a fresh disposable **Async Industries** scenario for the first-loop acceptance. Do not use an existing colony save or connect the production RWT server for this local baseline. A loaded RWT client is not evidence of co-op behavior.

Agents do not launch or stop the game, select/reorder the profile, or use GABS launch controls. The [bridge setup review](PHASE_2_BRIDGE_SETUP_REVIEW.md) specifies direct attach and the read-only first capture. Later simulation-changing cases must use the disposable save and their named acceptance procedures.

## First-loop acceptance route

The [first-playable contract](../FIRST_PLAYABLE_CONTRACT.md) and [tutorial](../TUTORIAL_SCRIPT.md) own the expected experience: initial facility/staff and one-time funding → physical assembly/calibration/power and operator → crew/kit → bounded opening → fogged AI-01 survey and evidence → extraction/recovery → physical analysis → once-only settlement → telemetry or resurvey → save/reload/revisit.

Record actual results, logs, seed, coordinate, loaded order and build identity. A successful menu load is only a startup observation. The field cue controls are in native Mod Settings; written warnings remain available when cues are muted. Development diagnostics in Operations can write build/order/coordinate identity and opt-in timing samples; those buttons do not start tests automatically.

**Timing decision still pending:** the accepted initial opening is currently 833 ticks, approximately 14 real seconds at normal speed. The owner was asked whether the intended window is instead 20 real minutes, two in-game hours, or the original 20 in-game minutes. No change is inferred from silence. This is a known usability issue to resolve before accepting expedition balance.

No runtime result is recorded in this launch sheet. Gate 2 remains open until the actual loop, failure/recovery, save/reload, presentation and performance evidence exists.
