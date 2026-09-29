# Connected colony implementation task

Baseline: `dff9125732142928f4e48cd265b787d5676393bc`, native-provider 0.4.0-dev. Features RR-GATE, RR-EXP, RR-SPACE, RR-FAC and RR-COMPAT. Follow [the owner contract](../CONNECTED_COLONY_PORTALS.md), [regression containment](../REGRESSION_CONTAINMENT.md) and [master TODO](../PREPRODUCTION_AND_IMPLEMENTATION_TODO.md).

The lead owns canonical integration and the additive `Gate/PortalGateOpening.cs` adapter. Initial source reviews own the Core work API, profile boundary and state migration records respectively. Follow-on exclusive scopes are: routing agent — `Portals/RimroomsPortalNetwork.cs`, `PortalRouteSearch.cs` and Core API appendix; crossing agent — `Portals/PortalCrossingRecords.cs`, `PortalCrossingService.cs` and crossing implementation record. The lead retains `PortalConnectionRecord.cs`. Existing expedition records, receipts, paid machine assembly, saved coordinates and native provider bindings remain readable. Do not silently migrate active missions or replay charges.

The new GameComponent owns persistent branch-local connections independently of missions. Endpoint references and fixed approach cells identify real maps/doors. Natural connections have no close timer. Laboratory connectivity observes its actual machine window and explicit opening identity. Map graph reachability is only a routing substrate: pawn path, permissions, work scheduling, reservations and physical transfer require their own adapters.

Player route: choose a supported door/address, open the machine, then ordinary eligible workers cross for jobs and physical supplies. Closing a machine suspends cross-map continuations and leaves original people/items on their actual maps. Natural connections persist even while a doorway is physically obstructed. Reopening reuses saved site state.

## Work and evidence

- [x] Source: persistent connection records, validation and resumable bidirectional graph query; see [implementation](CONNECTED_NETWORK_IMPLEMENTATION.md).
- [x] Source: separate laboratory connection/session owner, preserving the physical gate's single timer/energy owner and historical expedition state.
- [ ] Machine ownership adapter, natural discovery registration and player controls.
- [ ] Same-pawn crossing, carried-object custody and interrupted-transfer recovery.
  - [x] Source: isolated crossing/recovery API, original-object custody and saved receipts; [scope and remaining limits](CONNECTED_CROSSING_IMPLEMENTATION.md). Player/job integration and runtime acceptance remain open.
- [ ] Saved work intents, quantity leases and native destination job revalidation.
- [ ] Work-specific hauling, construction, bill, research, medical and needs adapters.
- [ ] Optional profile interfaces and native priority/schedule/restriction coverage.
- [x] Integrated 0.4.1 compilation and saved source/package evidence; see [checkpoint](CONNECTED_COLONY_CHECKPOINT.md). This closes only source/compiler consistency, not gameplay acceptance.
- [ ] Owner-launched acceptance: both directions; chains/loops; closed/blocked endpoints; permanent natural links; save/reload; cargo identity; interrupted jobs; all supported native/provider routes.

No game launch or runtime testing in this task. New source alone does not close the full connected-colony contract. Missing endpoints must remain diagnosable; never delete a saved edge or regenerate a visited site to repair it. Core-only remains supported, with no required optional-mod library introduced by the routing substrate.
