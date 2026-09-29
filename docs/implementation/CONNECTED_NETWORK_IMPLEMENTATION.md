# Persistent portal network implementation

Source increment for [the connected-colony task](CONNECTED_COLONY_IMPLEMENTATION_TASK.md). Read the [Core API review](CONNECTED_WORK_CORE_API.md), [state migration review](CONNECTED_PORTAL_STATE_MIGRATION.md) and [profile boundaries](CONNECTED_WORK_PROFILE_BOUNDARIES.md). No gameplay result is claimed.

## Implemented source

- [PortalConnectionRecord.cs](../../src/RimroomsAsyncIndustries/Portals/PortalConnectionRecord.cs) saves immutable public connection identity, branch, coordinate, kind and endpoint snapshots. Maps/doors use native saved references; cells retain their original location. Natural connections have no expiration or close operation.
- [RimroomsPortalNetwork.cs](../../src/RimroomsAsyncIndustries/Portals/RimroomsPortalNetwork.cs) saves schema 1 connections independently of expeditions. Registration checks actual doors, existing branch-owned coordinates/sites, distinct loaded maps, fixed approaches and provider roles. Idempotent registration refuses identity collisions. Missing/moved doors remain recorded and unavailable. Malformed identities disable the graph without deleting evidence.
- Graph queries traverse both directions and chains with loop detection, explicit map/connection scan budgets and distinct `SearchBudgetExceeded` versus `NoRoute` results. This is a map-topology query, **not pawn reachability or a path-cost calculation**. It never consumes materials, schedules jobs, transfers people, generates maps or unloads a connected site.
- [PortalRouteSearch.cs](../../src/RimroomsAsyncIndustries/Portals/PortalRouteSearch.cs) retains capture, search, reconstruction and validation cursors across calls. Automatic callers must retain this query and advance it; repeatedly restarting the old single-pass wrapper can starve long searches. Dynamic availability invalidates stale results, and each crossing rechecks its live edge. Per-call operation budgets are not measured wall-clock limits; concurrent-query and active-map scheduling remain later work.
- Several remembered laboratory addresses may share one source machine. Each has a distinct destination endpoint; its opening session can activate only the selected edge. A natural source threshold cannot be reassigned. Repeated addresses return their existing records.
- [PortalGateOpening.cs](../../src/RimroomsAsyncIndustries/Gate/PortalGateOpening.cs) adds separate saved portal connection/session IDs and a monotonic session sequence. The historical `rr_gateActiveExpeditionId` remains legacy-only. Active or unresolved legacy trips cannot be silently adopted or replaced. Machine power/timer/debit remains owned by `CompRimroomsGate`; the graph only observes the selected connection/session. Native debit IDs use the current owner session, preserving the historical expedition format for legacy runs.
- Portal recovery uses its own saved operation/session receipts and the same physical battery debit rules. A retry cannot restore time twice. An emergency session cannot clear its recovery cost through close/reopen. Conflicting or incomplete saved owner pairs stop gate operation and retain their original state for diagnosis.
- New generated site content version **4** uses an actual steel Core `Door` as its return threshold. Versions 0–3 retain the historical saved return anchor; validation distinguishes these providers by saved content version. No already visited map is rebuilt or retargeted. The generator and failed-site content preflight no longer require the custom return-anchor Def for new sites; its historical Def stays loadable.

## Save and failure boundaries

| Owner | Saved keys | Recovery behavior |
| --- | --- | --- |
| New GameComponent | `rr_portalNetworkSchema`, `rr_portalConnections` | Old saves load an empty network. Unsupported schema or malformed IDs refuse operations. Broken endpoint references retain the edge for diagnosis. |
| Each edge | `id`, `branchId`, `coordinateId`, `kind`, `first`, `second`, `openingId` | No site generation or automatic historical-run conversion. Natural kind never consults machine timers. |
| Each endpoint | `map`, `anchor`, `anchorCell`, `approachCell` | A moved/replaced door cannot redirect the saved edge. Obstruction is separate from permanent natural existence. |
| Existing gate, additive fields | `rr_gatePortalConnectionId`, `rr_gatePortalOpeningId`, `rr_gatePortalOpeningSequence`, `rr_gatePortalRecoveryReceipts` | Missing fields leave old runs unchanged. A matching active portal retry does not restore duration. Closing a normal opening clears its active ownership, leaves the address/edge saved, and does not move pawns. Emergency sessions require physical recovery first. |

The network validates branch/site identity again when querying availability. Laboratory outages/emergency states make normal edges unavailable; they do not remove maps, people, cargo or construction. A new portal opening runs the existing assembly, calibration, staffed station and physical energy readiness checks without a crew/cargo manifest. Failed graph observation before the first debit clears the attempted active session but retains consumed sequence numbers.

## Remaining integration

Player controls, natural portal discovery, ordinary crossing jobs, work intent/lease scheduling, all work/needs adapters, explicit endpoint repair/rebinding, emergency return behavior for portal sessions, streaming, procedural inhabitants/complexity and optional-provider integration remain incomplete. Existing saved sites retain their historical custom return anchor and need a separately reviewed endpoint migration/repair route; registration accepts actual doors only and does not silently replace that anchor. The graph is an API substrate, not a player-visible completion of the owner requirement.

The first local graph/gate compilation succeeded with zero warnings/errors against the pinned Core references. Final integrated build evidence belongs to the task's eventual checkpoint, after all assigned changes are reconciled. No test, game launch, runtime compatibility or release acceptance has occurred.
