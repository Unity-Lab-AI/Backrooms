# RimWorld Together pre-code baseline test plan

**Status:** prepared; no runtime cases have been run. This is a run sheet, not compatibility evidence.

## Purpose and boundary

Check the existing RWT workflows needed for the project's asynchronous, separate-facility design before Rimrooms code exists. Use a disposable server and saves. The pinned local game, DLC, Harmony, RWT client/server builds, hashes, and 294-entry profile are recorded in [RWT_AND_GRAVSHIP_FEASIBILITY.md](RWT_AND_GRAVSHIP_FEASIBILITY.md).

The owner selected Questionable Ethics Enhanced (profile row 182) and Medical Dissection (row 274) for the candidate RWT test despite their publishers' multiplayer warnings. Both remain optional. Their inclusion is test scope, not proof of compatibility or a co-op requirement.

Do not test custom Rimrooms starts, a Rimrooms dossier, or shared research before those features exist. Keep shared research disabled unless a supported RWT extension and its later synchronization tests are established. A full ordered 294-profile compatibility run is a separate release-stage check.

## Candidate profiles

Keep the same RimWorld build, DLC state, Harmony/RWT versions, server settings, and test steps across these disposable runs. Preserve each profile's exact client and server mod list/order with the result.

| Profile | Contents | Why it is tested |
| --- | --- | --- |
| RWT-BASE | Core + Harmony + RimWorld Together | Check the existing co-op workflow without optional mods. |
| RWT-QEE | RWT-BASE + Questionable Ethics Enhanced (row 182) | Test the owner's selected warning-mod candidate on its own. |
| RWT-MD | RWT-BASE + Medical Dissection (row 274) | Test the owner's selected warning-mod candidate on its own. |
| RWT-QEE-MD | RWT-BASE + both rows 182 and 274 | Check the selected pair together after the isolated runs. |

Use a fresh disposable world per profile. If a mod needs DLC or another dependency, record and match that requirement on both clients and the server. Do not remove Medical Dissection from a save after performing a dissection; its publisher warns that removal may be unsafe.

## Test cases

| Case | Action | Record as passed only when |
| --- | --- | --- |
| RWT-01 Join and start | Start the disposable server, connect two separate clients, and create/join two separate vanilla-started branches. | Both players join the same intended world without an error, and each branch has a distinct owner/save. Record whether different starts can coexist. |
| RWT-02 Visit | With one branch offline, use the documented visit flow from the other branch, then leave and resume play. | The visit works as configured, its limits are understood, and neither branch gains unintended control or loses saved state. |
| RWT-03 Item exchange | Transfer one ordinary vanilla material stack through an available RWT trade/delivery route. Record quantities before and after. | The intended recipient gets exactly one transfer, the sender's result is understood, and reconnect/save recovery does not duplicate or lose the stack. |
| RWT-04 Aid | Send one disposable test pawn through an available RWT aid route. Record faction, health, equipment, and destination before and after. | The intended recipient receives one pawn with expected state and both branches remain loadable. |
| RWT-05 Reconnect and recovery | Disconnect each client in turn, reconnect, then restart the disposable server and load both branches. | Both branches recover to their recorded state; no tested pawn or item is duplicated, silently lost, or assigned to the wrong owner. |
| RWT-06 QEE warning | Run RWT-01 through RWT-05 on RWT-QEE. Exercise a representative QEE vat/bill if safe in the disposable world. | Record each workflow result and any desync, error, slowdown, or save problem; a completed run is not automatically a pass. |
| RWT-07 Medical Dissection warning | Run RWT-01 through RWT-05 on RWT-MD. Exercise one dissection only in a disposable save, then save/reconnect/reload. | Record each workflow result and any desync, error, or save problem; a completed run is not automatically a pass. |
| RWT-08 Selected pair | Repeat the relevant workflows on RWT-QEE-MD after the isolated warning-mod runs. | Record whether combining the selected optional mods changes either result; do not infer success from the isolated runs. |

Use the exact RWT settings needed for visits, trade, and aid, and record their values. The current local server configuration does not enforce the 294-entry client profile, so independently compare both test clients and the disposable server before each run.

## Evidence record

For every case, save:

- date, tester, server/client device labels, RimWorld and DLC state;
- RWT client/server build and file hashes, Harmony version, ordered profile IDs, and the profile label above;
- relevant server settings and whether they were changed for this run;
- branch/save names or hashes, action steps, before/after pawn and item counts, and observed result;
- client and server log paths, errors/desyncs, reconnect/restart steps, and a short conclusion.

| Profile | RWT-01 Join/start | RWT-02 Visit | RWT-03 Item | RWT-04 Aid | RWT-05 Recovery | Warn-specific case | Evidence path / result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RWT-BASE | Not run | Not run | Not run | Not run | Not run | N/A |  |
| RWT-QEE | Not run | Not run | Not run | Not run | Not run | RWT-06: Not run |  |
| RWT-MD | Not run | Not run | Not run | Not run | Not run | RWT-07: Not run |  |
| RWT-QEE-MD | Not run | Not run | Not run | Not run | Not run | RWT-08: Not run |  |

Create a separate dated evidence note for each completed profile row so each case can record its own observed result, logs, and save identity.

A failed optional-mod case must be reported as a known limit for that tested profile; do not silently remove the mod from the owner's requested candidate or describe the run as compatible. A failed base workflow is a Gate 0 blocker for relying on that workflow in the co-op contract. Custom-item transfer, Rimrooms scenario support, and shared-ledger synchronization remain post-code acceptance tests.
