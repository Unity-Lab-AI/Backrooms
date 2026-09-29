# The exit plan — 0.12.9-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## What this is

**Arc 5's last named piece, and the one that makes a second gate real.**

> *"Remote sites need people, supplies, signals, protection, and an exit plan."*

Sites went on the books at 0.12.6. Supplies reached them at 0.12.7. People at 0.12.8. **This is
the exit plan.**

---

## The register, checked first

The families this touches — power and industrial infrastructure, facilities and spatial
construction, transport and expedition logistics — were all swept earlier in this session for
0.12.6, and nothing in them applies for the same reason: this changes **where a gate may stand**,
which no row in the profile has an opinion about. No new sweep was needed and none was invented to
look thorough.

---

## One line was the whole blocker

```csharp
private bool SameNativeHeadquartersThing(Thing thing)
{
    ...
    parent.Map == campaign.Headquarters && ...
}
```

**Eleven call sites** route through that method — the console, the bound battery, the assembly
bench, the kill-switch, the equipment links, the console lookup. Every one of them inherited
`parent.Map == campaign.Headquarters`, so **a gate could only ever be designated at the
headquarters**, and arc 5's *"exit plan"* was unreachable no matter how many sites a branch held.

It now asks `campaign.OperatesAt(parent.Map)`: the headquarters, or a site on the books.

**The name is kept.** All eleven call sites read it as *"the branch's own infrastructure, here"*,
which is what it has always meant and still means. Only the set of valid *"here"*s grew, and
renaming it across eleven sites to say the same thing would be churn pretending to be clarity.

---

## The clause I did not touch, which is the good part

```csharp
thing.Map == parent.Map
```

A gate at a remote site therefore needs **its own console, its own bound battery and its own
assembly bench, at that site.**

You cannot run a gate at the far end of the world off the equipment in your headquarters. That is
not a restriction I added — it is the clause that was always there, and widening the *map* test
without touching it is what turns *"remote sites need people, supplies, signals, protection, and
an exit plan"* from a list into a build order. **A site with a gate is a real facility or it is
nothing.**

The proof asserts that clause explicitly, because deleting it would look like a simplification.

---

## A coordinate still cannot host a company gate

Not by a check that could be forgotten — **by construction.** A designated gate needs
`OperatesAt`, which is the headquarters or a **registered site**, and a Backrooms coordinate can
never be registered (refused in the service and in the pane, asserted since 0.12.6).

So invariant 12 holds without anybody remembering it: what is down there is a **natural** gate, with
no operator, no power and no address book, and it is not the company's doing.

The proof asserts the place-set never mentions `RimroomsDestinationMapParent` at all. Planting a
line that admits coordinates fails it.

---

## Two questions, one place-set

`OperatesAt` and `CanReceiveDeliveryAt` both delegate to a single private `IsBranchPlace`.

They are **named apart on purpose** even though they currently return the same answer, because
they are not the same question: a site could one day be too remote for a supplier and still
perfectly fine to build a gate on. Sharing the implementation means they cannot drift while they
agree; naming them apart means the day they should differ, there is somewhere for the difference
to go.

Two names for one predicate would be a smell. Two names for one *place-set*, with the questions
kept distinct, is the thing that stops a later change answering the wrong one.

---

## What came free

**A way out may already come up at a site.** `CompRimroomsEmergence.OrdinaryBranchMap` routes
through `OwnsMap` and excludes coordinates — so 0.12.6's third clause gave emergence anchors at
registered sites without a line written here.

That is the second time the single-predicate decision has paid: one clause at 0.12.6 delivered
work, deliveries, gates and now ways out. **It is also why the proof checks every one of those
consequences is still wanted** — a predicate that grants four things at once grants them to
whoever widens it next, too.

---

## Fault-planted four ways

| Fault planted | Caught by |
|---|---|
| back to headquarters-only | *"the gate no longer requires the headquarters map"* **and** *"asks where the branch operates"* |
| **a remote gate running off headquarters equipment** | *"gate infrastructure must stand on the gate's own map"* |
| coordinates admitted to the place-set | *"the place-set admits only the headquarters and registered sites"* |
| `OperatesAt` given its own separate definition | *"operating and receiving share one place-set"* |

All restored, proof holding. One plant failed to apply at first because my anchor text was wrong —
the script's assert fired before writing anything, so the proof correctly still held, and the
plant was redone properly rather than counted.

---

## Receipts

| | |
|---|---|
| Version | 0.12.9-dev |
| Build | 172 C# files, 86 package files, **0 warnings, 0 errors** |
| Call sites freed by one line | **11** |
| New defs, art, audio or texture | **none** |
| Harmony | **none** |
| Keyed strings corrected | **1**, which had begun to lie |
| Checkers | **eight**, all passing |
| Proofs | **eleven**, all holding; the sites proof fault-planted four more ways |
| Game launched | **no**, and nothing here has been played |

**Arc 5's named list is now complete**: people, supplies, signals, protection and an exit plan all
have a mechanism. **Still unwritten from the chart**: relay stations, caches, field shelters,
guarded leases, and resupply and evacuation missions.
