# Company-to-site logistics — 0.12.7-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including a latent bug it found and a
claim of its own that failed open. Never rewritten.

---

## What this is

**Arc 5's second piece.** The arc names *"company-to-site logistics"* and 0.12.6-dev gave a branch
sites to have — but procurement had the headquarters written into it, so **a registered site could
be billed for every day and never receive a shipment.** The paperwork without the point.

---

## The register, checked first

`Storage and recovered-material logistics` (15 rows) and `Staff jobs, policies, and social
systems` (8). Every row is *Optional* or *Settled*, and the storage family is stockpile and
container overhauls — none of them changes **who may be sent a shipment**, which is the only
question this touches. Nothing applied.

---

## The design had already anticipated it

`ProcurementOrderRecord` already had a `receivingMap` field, and **the delivery path already
honoured it**:

```csharp
if (!IsReceivingZoneValid(order.receivingMap, order.receivingZone, itemDef) ||
    order.receivingZone.ID != order.receivingZoneId)
```

Only the **selection** was pinned — seven `campaign.Headquarters` references at quote time, accept
time and redirect time. So this is a widening, not a rewrite, and the smallness of it is evidence
the original design expected the far side to move one day.

**The destination is now the zone's own map.** A stockpile already knows where it is, so nothing
has to be passed in and the two can never disagree — and the branch must be willing to receive
there: `CanReceiveDeliveryAt` is true for the headquarters and for any live registered site, and
nothing else.

A Backrooms coordinate is excluded **by construction**, because it can never be registered. Which
is right: a supplier does not drive into a hole in the world.

---

## The latent bug the widening would have exposed

The redirect path — rerouting an in-flight order — updated three fields:

```csharp
order.receivingZone = receivingZone;
order.receivingZoneId = receivingZone.ID;
order.receivingZoneLabel = receivingZone.label;
```

**It never updated `receivingMap`.**

That was completely harmless while every zone lived on the one allowed map. The moment a second
map became legal, redirecting a shipment across maps would leave the order pointing at the **old**
map — and the delivery check validates the zone *against* `order.receivingMap`. The order would be
refused on every attempt, for ever, awaiting a condition that could never come true. Paid for,
cargo held, and never arriving.

**A bug that only exists once you add the feature is the hardest kind to find**, because it is not
there while you are looking for it. It was found by reading every write to the record before
changing what the record could hold — the same method that found the frozen approach cell at
0.12.3, and the same method invariant 157 was written for.

The proof now asserts both that the map is updated and that it moves **alongside** the zone it
belongs to, because a mismatched pair is what the bug actually was.

---

## Reachable, not just permitted

`HeadquartersStockpiles` listed only the headquarters' stockpiles, so widening the service alone
would have left the feature permitted and unofferable. It is now `DeliveryStockpiles`, walking
every destination the branch may receive at.

And a stockpile **says where it is** — but only when the branch holds more than one place. A
colony with a headquarters and nothing else would otherwise read *"Stockpile at headquarters"* on
every row, which is noise teaching nothing.

Headquarters first, then sites in registration order, then by label, with an ordinal tiebreak on
the zone ID so the menu cannot follow scan order and shuffle between openings — invariant 26,
applied to a menu instead of a roll.

One string changed meaning rather than being reused wrongly: an unloaded destination used to
report *"The company HQ map is unavailable"*, which would be a lie about a site. A site's map can
be unloaded while the headquarters' cannot, so that case has its own line now.

---

## A claim of mine failed open, for the second time today

The on-the-books claim was written as:

```python
procurement.count('"RR_Proc_DestinationNotOnTheBooks"') >= 2
```

Fault-planting caught it. Replacing the guard `if (!campaign.CanReceiveDeliveryAt(destination))`
with `if (false)` **left the refusal string sitting there unused** — so the count still passed, the
guard was gone, and the proof said nothing. **The plant that mattered most was the one the proof
ignored.**

> **A claim must key off the thing that happens, not off a token near it.**

Rewritten as three claims: each guard asserted by its own expression, and the strings asserted
separately as *"a guard that refuses silently teaches nothing"*. Both guards re-planted, both now
fail correctly.

This is **invariant 152, written earlier today**, and it is evidently easy to write and easy to
forget while writing the next claim. Worth saying plainly: the rule is not "fix it when caught",
it is **check what your claim survives before believing it.**

---

## Fault-planted five ways

| Fault planted | Caught by |
|---|---|
| the redirect stops updating the map — **the latent bug, restored** | *"redirecting updates the receiving MAP"* **and** *"the map is set alongside the zone"* |
| the quote guard disabled | *"quoting guards the destination against the books"* (after the claim was fixed) |
| the redirect guard disabled | *"redirecting guards the destination against the books"* |
| the quote re-pinned to the headquarters | *"the quote no longer pins the destination to the headquarters"* |
| the menu reverted to headquarters-only | *"lists stockpiles at every destination"* **and** *"the headquarters-only listing is gone"* |

All restored, proof holding.

---

## Receipts

| | |
|---|---|
| Version | 0.12.7-dev |
| Build | 172 C# files, 86 package files, **0 warnings, 0 errors** |
| Latent bugs found and fixed | **1**, which only existed once the feature was added |
| Proof claims found failing open | **1**, by fault-planting |
| New defs, art, audio or texture | **none** |
| Harmony | **none** |
| New keyed strings | **4** |
| Checkers | **eight**, all passing |
| Proofs | **ten**, all holding; the sites proof fault-planted five ways |
| Game launched | **no**, and nothing here has been played |

**Still owed in arc 5:** staffing a site, and the exit plan. A gate may now anchor at a registered
site, so the second gate has stopped being theoretical — and the chart's relay stations, caches,
field shelters, guarded leases, resupply and evacuation missions are all unwritten.
