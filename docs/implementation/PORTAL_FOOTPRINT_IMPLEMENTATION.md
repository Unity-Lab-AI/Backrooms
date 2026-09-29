# A portal is its own door cell — 0.12.3-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## The direction

> *"and technically the way the gate works and make a portal when placing it on your map or having
> a natural one(natruals can not be destoryed or moved, so one can technically build a roomm
> directly on the other side of the portal door and it shouldnt interfere with the portal
> transition to the seeded backrooms"*

and the clarification that named the principle:

> *"if u get what i mean .. in the real world maps the portals dont extend into the real world
> environment so in the real world you can mine and build and explore directly behind the gates
> with out actually effecting the gate, unless there is connected need requipremd equipemnet
> directly required placemnets behind the pgate doors.. so yeah you get it"*

**A portal is its own door cell and reserves nothing.** No radius, no claimed cells, no protected
zone. The one exception is not the portal's doing at all: **linked equipment has a reach of its
own**, so a console or a bound battery has to be within range of the gate. That is the
equipment's constraint, and the distinction matters — a player told *"the gate needs space"*
builds very differently from one told *"this cabinet has to be within reach of that gate"*.

---

## The defect, which nothing could have shown from one file

`PortalEndpointRecord` snapshots the cell a traveller stands on, at registration:

```csharp
internal PortalEndpointRecord(Thing anchor, IntVec3 approach)
{ this.anchor = anchor; map = anchor.Map; anchorCell = anchor.Position; approachCell = approach; }
```

And `RimroomsPortalNetwork.Availability` validated that saved cell, forever after:

```csharp
return edge.First.ApproachCell.Standable(edge.First.Map) &&
    edge.Second.ApproachCell.Standable(edge.Second.Map)
    ? PortalNetworkResult.Success : PortalNetworkResult.Obstructed;
```

`ApproachCellFor` returns the **first** standable cardinal neighbour, so which cell got frozen
depended on what happened to be walkable the moment the address was registered.

**Build a wall on that one cell and the connection reports `Obstructed` for the life of the
save** — with up to three other perfectly walkable cells beside the same door. No error, no
message, no crash. A gate the design calls *permanently open* that had simply stopped working,
because the player built a room behind it. Which is exactly what the owner says must be allowed.

**Nobody could see this in either file alone.** The record looks correct — snapshotting is
deliberate and documented. The availability check looks correct — it asks whether the cell is
standable. The bug lives only in the relationship, and it is the same failure family as the
beacon that could never fire and the tier ladder that could never be climbed.

---

## The fix, and the half of it that matters more

`PortalEndpointRecord.TryRepairApproach()` re-derives the approach cell when the saved one has
been built over, through `PortalAddressService.ApproachCellFor` — the single derivation, whose own
comment says *"callers must not re-derive it"*.

**The anchor cell is deliberately not refreshed.** That snapshot is what stops a moved door
silently redirecting a saved route, and it is still exactly right. Only the cell a traveller
stands on moves, because that is a fact about the local geometry rather than about the connection.
Refreshing both would have traded one silent failure for a worse one, and the proof asserts the
asymmetry.

A door genuinely sealed on all four sides returns false and the connection reports `Obstructed`
— which is the honest answer. **Walling off your own door should cost exactly what walling off
any other RimWorld door costs, and no more.**

### Not repaired while a crossing is in flight

This is the part that needed care rather than cleverness.

A `PortalCrossingReceipt` records the approach cells it began with, and `ConnectionStillMatches`
refuses to continue if they changed. **That equality check is the guard that stops a transfer
losing a pawn** — invariant 55, *"a transfer that can lose a pawn is a corruption, not a
threat."*

Moving the cell out from under a live transfer would trip that guard and abort a legitimate
crossing. So `Availability` asks `CrossingInFlight(edge)` first, and a busy edge waits. The check
compares against the **connection id** specifically, because a broader match would freeze repairs
on unrelated connections.

The naive version of this fix — re-derive the approach live, everywhere — would have quietly
weakened the most safety-critical system in the mod. **Finding the read sites before changing the
value is the only reason that did not happen.**

---

## An eighth proof, and a rule it enforces going forward

`proof-portal-footprint.py` asserts the repair, the asymmetry, the ordering, the in-flight guard
— and one forward-looking rule:

> **No portal source may contain `ReserveCell`, `ClaimRadius`, `portalRadius`,
> `ProtectedRadius` or `ReservedCells`.**

If any of those ever appears, somebody has started projecting the gate onto the map, which is the
thing this direction forbids. It is cheap, it is a name check, and it will outlive the memory of
why.

### Fault-planted four ways

| Fault planted | Caught by |
|---|---|
| the repair also moves the anchor cell | *"the repair does not reassign the anchor cell — a moved door could then silently redirect a saved route"* |
| the repair moved **after** the standability test | *"availability repairs before it tests standability"* |
| the in-flight guard removed | *"the repair is skipped while a crossing is in flight"* |
| a reserved-cells name introduced | the banned-name claims |

All restored, proof holding.

---

## Still owed on this direction

**`"natruals can not be destoryed or moved"`** is not built, and it is not built because it needs
a decision rather than more typing.

A natural gate is a Core `Door`. Core decides destructibility and deconstructibility at the
**def** level — `def.destroyable`, `def.building.IsDeconstructible` — and this mod may not change
those, because that would make *every* door in every colony indestructible for every player and
every other mod. The content policy and the work-with-294-others rule both forbid it.

What is available without Harmony:

- **Damage** can be absorbed per-instance. `ThingComp.PostPreApplyDamage(ref DamageInfo, out bool
  absorbed)` is a vanilla comp hook, and these doors already carry this mod's comps.
- **Deconstruction** has no comp-level veto. The honest options are to let the designation happen
  and re-place the door, to refuse the crossing afterwards and explain, or to accept that a player
  who deliberately deconstructs their own natural gate has closed it.

Three defensible readings means asking, per invariant 134. Queued with that question attached
rather than guessed at.

---

## Receipts

| | |
|---|---|
| Version | 0.12.3-dev |
| Build | 168 C# files, 86 package files, **0 warnings, 0 errors** |
| Real defect fixed | **1**, invisible from any single file |
| New defs, art, audio or texture | **none** |
| Harmony | **none** |
| Checkers | **eight**, all passing |
| Proofs | **eight** — a new one, fault-planted four ways |
| Game launched | **no**, and nothing here has been played |
