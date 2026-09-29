# A remote base is a costly responsibility — 0.12.6-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## What this is

**Arc 5's first piece**, and the first work in arcs 5–8 — which is what
`docs/CAMPAIGN_CHART.md` §7 step 8 authorises now that steps 6 and 7 are done.

The arc, from `CAMPAIGN_CONTENT_CATALOG.md`:

> *"A radio point or shelter can make a return possible where the facility alone cannot reach.
> Remote sites need people, supplies, signals, protection, and an exit plan... **A remote base is a
> costly responsibility rather than free map ownership.**"*

That last sentence is the whole design, and it decided the shape: **registration is the act, and
the bill is the consequence.**

---

## The register, checked first

`Facility construction and material access` (6 rows), `Power and industrial infrastructure` (10),
`World operations, contracts, and commerce` (12), `Transport and expedition logistics` (14).

**And a search for outposts returned nothing: there is no multi-colony or outpost-management mod
anywhere in the 295 rows.** So there is nothing to conflict with — and nothing to lean on either.
Every row in those families is *Optional* or *Configuration only*, and none of them touches how a
branch accounts for a place it holds.

---

## Acquisition is the game's; recognition is ours

The temptation was to build a way to *get* a remote site: a world object, a tile derived from
something, a map generated on demand.

**RimWorld already does this.** A colony can settle a second tile with a caravan, and this mod's
own topology already lets a crew come out of the Backrooms somewhere else in the world
(`map > backrooms > map`, owner direction). A mod that invented its own settling would be fighting
Core for no reason and would be first to break on a Core update.

So nothing here acquires anything. A map the player already holds is **not a branch site until
somebody puts it on the books**, and that act is the feature. The proof asserts the restraint:
`WorldObjectMaker.MakeWorldObject`, `GetOrGenerateMap`, `SettleInEmptyTileUtility` and
`MapGenerator.GenerateMap` are all banned from this source.

---

## The cost is a ratio, not a number

Each live site adds **a quarter of the branch's own base overhead** to the daily bill.

**That had to be a ratio.** Async Industries runs on $25,000 a day of overhead; the Store runs on
$1,500. One absolute surcharge would be a rounding error for the first and ruinous for the
second — and every start tunes this for free by tuning the number it already had.

It is billed as **its own obligation**, `RR_Ledger_RemoteSites`, rather than folded into
overhead — so a player can see on the ledger what the places are costing and decide whether to
keep them. A cost you cannot find is not a decision.

**It counts only live sites.** A record whose place has been lost stops being billed, and the pane
says so on its row rather than hiding it: a player needs to know why a site stopped costing money,
and silently dropping a row teaches somebody not to trust the screen.

---

## A coordinate is never a site

This is the distinction that made the naive version of this feature worthless, and it is worth
being explicit about because the naive version was mine, one checkpoint ago.

The obvious opening move was the surcharge on its own — bill per map held beyond the headquarters,
using machinery that already existed. **It would have computed zero forever.** `OwnsMap` returns
true for the headquarters and for **open Backrooms coordinates**, which are transient destinations
reached through a gate. Counting those would have been wrong on its own terms *and* would have
produced a feature that bills nothing while looking like progress.

So a coordinate is refused, in the service and again in the pane before the click, with a line that
says why: *"A Backrooms coordinate is somewhere you go, not somewhere you keep."*

---

## One predicate, five features

`OwnsMap` gained a third clause, and that single line is what *"people, supplies, signals,
protection, and an exit plan"* actually means in this codebase:

- **connected work** reaches a registered site, so people and supplies move there
- **the portal network** will anchor a gate there, so it can have an exit
- **an emergence anchor** may be marked there, so a way out can come up on it
- the solo/group hints count it as an ordinary map

Thirty call sites across sixteen files consult `OwnsMap`. Extending one predicate rather than
threading a second one through all of them is the difference between a concept and a bolt-on —
and every one of those consequences is a thing the arc asks for, which is why it was safe.

The clause is placed **after** the coordinate check and the proof asserts the order, because a
coordinate must never fall through to the site test.

---

## Releasing is free, and that is a rule rather than generosity

No fee, no notice period, and the bill stops on the next operating day.

**Nothing in this mod has a deadline but the gate** (`docs/CAMPAIGN_CHART.md` §1.1), and a release
fee is a deadline's cousin: a cost for changing your mind. The proof asserts that the release path
contains no `PostTransaction` and no `AddObligation`.

The map itself is untouched. Releasing a site says the branch no longer runs it — not that the
colony there stops existing, which is the player's business and RimWorld's.

---

## Fault-planted four ways

| Fault planted | Caught by |
|---|---|
| the surcharge stops being billed — **free map ownership restored silently** | *"the surcharge is billed as its own daily obligation"* |
| coordinates become registrable | *"registration refuses a Backrooms coordinate"* |
| releasing charges a fee | *"releasing a site charges nothing — a fee for changing your mind is a deadline wearing a different hat"* |
| the surcharge becomes an absolute number | *"the surcharge is a ratio of the branch's own overhead"* |

All restored, proof holding. The first is the one that mattered: **it is the whole arc, and it
would have broken with no compiler error, no checker failure and no visible symptom.**

---

## Receipts

| | |
|---|---|
| Version | 0.12.6-dev |
| Build | 172 C# files, 86 package files, **0 warnings, 0 errors** |
| New defs, art, audio or texture | **none** |
| Harmony | **none** |
| New keyed strings | **24** |
| New Operations pane | **1** — Sites |
| Checkers | **eight**, all passing |
| Proofs | **ten** — a new one, fault-planted four ways |
| Game launched | **no**, and nothing here has been played |

**Next in arc 5:** what a site needs to *be* one — staffing it, supplying it, and the exit plan.
The predicate now makes all three reachable; none of them is written.
