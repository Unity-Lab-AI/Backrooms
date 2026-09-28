# RimWorld Together post-build acceptance test plan

**Status:** post-build acceptance run sheet prepared; no multiplayer workflow result is claimed. Do not run these in-game cases before a Rimrooms build exists. The owner prepares and launches each profile through RimSort; RimBridgeServer attaches afterward.

## Purpose and boundary

Check the existing RWT workflows needed for the project's asynchronous, separate-facility design after a Rimrooms build exists and before advertising co-op support. Use a disposable server and saves. The pinned local game, DLC, Harmony, RWT client/server builds, hashes, and pre-Rimrooms 294-entry profile are recorded in [RWT_AND_GRAVSHIP_FEASIBILITY.md](RWT_AND_GRAVSHIP_FEASIBILITY.md). The first project test is the full 295-entry product target; then prepare a focused RWT profile containing Rimrooms, Core, Harmony, and RWT in RimSort. Record RimBridgeServer as a separate QA overlay and use the [RimSort package/launch plan](RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md) and [bridge plan](RIMBRIDGE_TEST_HARNESS.md) for owner-operated launch and evidence capture.

The owner selected Questionable Ethics Enhanced (profile row 182) and Medical Dissection (row 274) for the candidate RWT test despite their publishers' multiplayer warnings. Both remain optional. Their inclusion is test scope, not proof of compatibility or a co-op requirement.

The local server snapshot has `Aid.json` and `Trade.json` enabled, each with cooldown 250. It has no local Visit/Activity action file or `EnableActivities` setting, so offline-visit availability must be checked on a disposable server. `ScenarioConfig.json` enforces `Crashlanded`; use a separate disposable configuration variant when testing mixed starts. The live server configuration is not part of these experiments. The official [trading guide](https://rimworldtogether.wiki.gg/wiki/Trading) says direct trades and gifts require both players online; its drop-pod instructions do not specify whether an offline recipient receives cargo, so RWT-10 checks that separately. The audit records the exact setting-file hashes.

Run the custom Rimrooms starts, dossier transfer, and any shared-research case only after those features exist. Keep shared research disabled unless a supported RWT extension and its synchronization tests are established. A full ordered 294-profile compatibility run is a separate release-stage check.

## Candidate profiles

Keep the same RimWorld build, DLC state, Harmony/RWT versions, server settings, and test steps across these disposable runs. Preserve each profile's exact client and server mod list/order with the result.

| Profile | Contents | Why it is tested |
| --- | --- | --- |
| RWT-BASE | Core + Rimrooms + Harmony + RimWorld Together | Check the Rimrooms co-op route without other optional mods. |
| RWT-QEE | RWT-BASE + Questionable Ethics Enhanced (row 182) | Test the owner's selected warning-mod candidate on its own. |
| RWT-MD | RWT-BASE + Medical Dissection (row 274) | Test the owner's selected warning-mod candidate on its own. |
| RWT-QEE-MD | RWT-BASE + both rows 182 and 274 | Check the selected pair together after the isolated runs. |

Use a fresh disposable world per profile. If a mod needs DLC or another dependency, record and match that requirement on both clients and the server. Do not remove Medical Dissection from a save after performing a dissection; its publisher warns that removal may be unsafe.

## Disposable setup and recovery

1. Copy the local RWT server directory/configuration and selected client mod profile to a disposable test location. The owner stages/sorts each client profile in RimSort and starts both clients there; never edit or launch the live server configuration for these cases.
2. Record hashes for both client profiles and the disposable server config. Match RimWorld executable/Core hashes, runtime build, DLC, Harmony, RWT version, ordered package IDs, and settings on both clients; use one fresh world per profile.
3. Start only the disposable server, connect the two clients, and make named branch/save copies before each case. Record the case ID, profile, save identity, and relevant settings in the evidence note.
4. After each case, save both branches, disconnect/reconnect, and restart the disposable server where the case calls for recovery. Compare item/pawn state and owner records with the before-state.
5. Preserve logs and the untouched source server/configuration; archive the disposable saves and evidence note together.

Mixed-start cases require a separate disposable copy of the scenario setting. Restore the original value after the experiment and document the result; do not change the live server.

## Test cases

| Case | Action | Record as passed only when |
| --- | --- | --- |
| RWT-01 Join and start | Start a disposable copy of the current server, connect two separate clients, and create/join two separate branches under the enforced Crashlanded setting. | Both players join without an error and each branch has a distinct owner/save. Record the enforced scenario and whether different seeds/branches coexist. |
| RWT-02 Visit | First establish whether offline visits are enabled in the disposable server. With one branch offline, use the documented visit flow from the other branch, then leave and resume play. Record whether the route loads a remote settlement view. Check the failure mode described in [closed issue #273](https://github.com/RimWorld-Together/Rimworld-Together/issues/273): duplicate IDs, unresolved references, renderer errors, and cleanup. | The feature is available and works as configured, its limits are understood, and neither branch gains unintended control or loses saved state. If unavailable, record the missing setting/limitation instead of treating this case as passed. A historical issue is a test lead, not proof of a current defect. |
| RWT-03 Item exchange | With both players online, transfer one ordinary vanilla material stack using direct trade; separately test gifting in the disposable world. Record quantities and resulting sender/recipient state before and after each action. | The intended recipient gets exactly one transfer, the sender's result is understood, and reconnect/save recovery does not duplicate or lose the stack. Do not count direct trade/gifting as an offline shipment. |
| RWT-04 Aid | Send one disposable test pawn through the enabled RWT aid route. Record identity/biography, faction/ideology, health, equipment, destination, and online state before and after; save, reconnect, and recheck. | The intended recipient receives one pawn with expected state and both branches remain loadable. Check the known [upstream aid-state report](https://github.com/RimWorld-Together/Rimworld-Together/issues/296); a run is evidence for this build, not a general fix. |
| RWT-05 Reconnect and recovery | Disconnect each client in turn, reconnect, then restart the disposable server and load both branches. | Both branches recover to their recorded state; no tested pawn or item is duplicated, silently lost, or assigned to the wrong owner. |
| RWT-06 QEE warning | Run RWT-01 through RWT-05 and RWT-10 on RWT-QEE. Exercise a representative QEE vat/bill if safe in the disposable world. | Record each workflow result and any desync, error, slowdown, or save problem; a completed run is not automatically a pass. |
| RWT-07 Medical Dissection warning | Run RWT-01 through RWT-05 and RWT-10 on RWT-MD. Exercise one dissection only in a disposable save, then save/reconnect/reload. | Record each workflow result and any desync, error, or save problem; a completed run is not automatically a pass. |
| RWT-08 Selected pair | Repeat the relevant RWT-01 through RWT-05 and RWT-10 workflows on RWT-QEE-MD after the isolated warning-mod runs. | Record whether combining the selected optional mods changes either result; do not infer success from the isolated runs. |
| RWT-09 Mixed starts | On a separate disposable server configuration with scenario enforcement adjusted only for this test, have clients attempt the chosen different vanilla start scenarios. | Record if RWT supports separate start scenarios, whether initial worlds/ownership remain distinct, and any join/save problems. The actual server installation remains unmodified. |
| RWT-10 Offline drop-pod cargo | With the recipient branch offline, launch one ordinary vanilla material stack by drop pod to its settlement. Have the recipient log in later and inspect the transfer spot, inventory, message/log, and sender save. | The route works with the recipient offline, delivers exactly once, and preserves sender/recipient saves through reconnect. If it requires the target to be online or fails, record the condition and do not advertise asynchronous shipping. |

Record the exact RWT settings used for visits, trade, and aid. The current local server configuration does not enforce the 294-entry client profile, so independently compare both test clients and the disposable server before each run. Direct trade/gifting requires both players online per the RWT guide; record any alternate route separately.

## Evidence record

For every case, save:

- date, tester, server/client device labels, RimWorld/DLC and RimSort state;
- RWT client/server build and file hashes, Harmony version, ordered target profile IDs, separate RimBridgeServer QA overlay IDs, and the profile label above;
- relevant server settings and whether they were changed for this run;
- branch/save names or hashes, action steps, before/after pawn and item counts, and observed result;
- client and server log paths, errors/desyncs, reconnect/restart steps, and a short conclusion.

| Profile | RWT-01 Join/start | RWT-02 Visit | RWT-03 Item | RWT-04 Aid | RWT-05 Recovery | RWT-09 Mixed starts | RWT-10 Drop pod | Warn-specific case | Evidence path / result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RWT-BASE | Not run | Not run | Not run | Not run | Not run | Not run | Not run | N/A |  |
| RWT-QEE | Not run | Not run | Not run | Not run | Not run | N/A | Not run | RWT-06: Not run |  |
| RWT-MD | Not run | Not run | Not run | Not run | Not run | N/A | Not run | RWT-07: Not run |  |
| RWT-QEE-MD | Not run | Not run | Not run | Not run | Not run | N/A | Not run | RWT-08: Not run |  |

Create a separate dated evidence note for each completed profile row so each case can record its own observed result, logs, and save identity.

A failed optional-mod case must be reported as a known limit for that tested profile; do not silently remove the mod from the owner's requested candidate or describe the run as compatible. A failed base workflow blocks any co-op support claim for that workflow until it is resolved. Custom-item transfer, Rimrooms scenario support, and shared-ledger synchronization remain post-code acceptance tests.
