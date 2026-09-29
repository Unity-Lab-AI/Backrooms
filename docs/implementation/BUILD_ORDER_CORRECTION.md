# The queue was in the wrong order — 0.12.5-dev, 2026-09-29

**Dated record.** A correction checkpoint: no gameplay changed, and the reason that is the right
outcome is the whole point. Never rewritten.

---

## What happened

The next item in `docs/NOW.md` was **research tiers 3–4**, with arcs 5–8 after them. Work started
on tier 3 — *"Remote operations: support more than one site; work beyond headquarters"* — with the
method invariant 136 demands: **find the knobs and check each against its real read site before
writing anything.**

The sweep found that tier 3 **has almost no knobs**, and the ones it has are the wrong kind.

---

## What the sweep actually found

| Candidate | Verdict |
|---|---|
| ~30 `Maximum*` constants across `ConnectedWork/` | **Scan budgets, not unlocks.** `MaximumResourceCandidates`, `MaximumBedsExamined`, `MaximumPresenceCandidates` and the rest bound how many things a work pass *examines*. Raising one is a performance decision with no effect a player could name |
| `MaximumFrontiersPerCoordinate`, `FrontierRarity`, `EmergenceShare` | **Genuinely good, and all three belong to Spatial.** One branch cannot take three |
| `SurveyTicks` | Real, and Measurement's |
| `MaximumConnectedMapsPerPass` | On-theme, but a scan budget again, and only bites for a branch holding five or more maps |
| Facilities, Fieldcraft, Entities, Commerce at tier 3 | **Nothing.** No knob exists, because the systems a remote-operations unlock would modify are not built |

So seven tier-3 projects would have meant **four invented effects for systems that do not exist.**
That is precisely what three tier-2 unlocks were deleted for at 0.11.6-dev, and precisely what
invariant 136 exists to prevent.

---

## Then the chart settled it

`docs/CAMPAIGN_CHART.md` §7 is the authority on build order, and it had the answer already:

> 6. The remaining eight research branches, **tier 0 → 2 first.**
> 7. The clean-up team that means a facility never dies.
> 8. Arcs 5–8.

**"Tier 0 → 2 first."** The chart never authorised tiers 3–4 before the arcs, and the reason is
obvious once seen: **tier 3 is *remote operations*, and arc 5 is what builds remote sites.** A
research band cannot unlock capabilities for a system that has not been written.

Steps 6 and 7 are both done. **The next authorised step is 8.**

`NOW.md` had it backwards. The chart beats any other document by its own stated rule, so the queue
is corrected rather than the chart.

---

## And arc 5's obvious first piece is blocked too

The arc's principle is stated plainly in `CAMPAIGN_CONTENT_CATALOG.md`:

> *"A remote base is a costly responsibility rather than free map ownership."*

That suggests a clean, contained opening move: bill a daily surcharge per site held beyond the
headquarters, using the obligation machinery that already exists. It scales naturally with each
start's economy, needs no new tuning surface, and makes free map ownership impossible.

**It would currently always compute zero.** `OwnsMap` returns true for the headquarters and for
**open Backrooms coordinates** — which are transient destinations, not bases, and charging rent on
one would be wrong on its own terms. There is no way to acquire an ordinary remote world site yet.

**The acquisition is the missing system, and it is arc 5's actual first piece.** Shipping the
surcharge first would have been a feature that bills nothing, dressed as progress.

---

## Why this is a checkpoint and not a note

Nothing shipped here changes what the mod does. Two things changed that decide what gets built
next:

1. **The queue order now matches the chart**, so the next session does not open by building four
   invented research effects.
2. **The blockage is written down with its evidence** — which knobs exist, which are scan budgets,
   which branches have nothing, and why the surcharge computes zero — so nobody re-derives it and
   nobody talks themselves past it.

A correction that prevents a day of building the wrong thing is worth more than a day of building
the wrong thing, and **the cheapest possible outcome of a sweep is finding out there is nothing to
build yet.**

---

## Receipts

| | |
|---|---|
| Version | 0.12.5-dev |
| Build | 170 C# files, 86 package files, **0 warnings, 0 errors** |
| Gameplay changed | **none, deliberately** |
| Hollow unlocks not shipped | **4** |
| Checkers | **eight**, all passing |
| Proofs | **nine**, all holding |
| Game launched | **no**, and nothing here has been played |

**Next, per the chart: arc 5, and its first piece is a way to hold a remote site at all.** The
surcharge follows it, not the other way round.
