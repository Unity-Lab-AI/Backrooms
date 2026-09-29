# The free doors run out — 0.12.1-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including the claim of its own it
found failing open. Never rewritten.

---

## The direction, and what it corrects

> *"and remember the solo/group start in a backroom needs to 100% have a exit to map natural
> portal on their first backrroms level with **natural portals deeper to an extent till they would
> need to buidl theri own gate**"*

And the constraint that arrived with it:

> *"but remmebr this is all open eneded they can play how they choose"*

**This corrects 0.12.0-dev, which shipped an hour earlier.** That record states, in as many words,
*"There is no way home and finding one is the whole opening."* That is wrong: the first level must
hold a **guaranteed** way out. The 0.12.0 record is **annotated, not rewritten** — a dated record
is what shipped on the day, and the evidence trail is worth more than a tidy history.

**This checkpoint builds the second half of the direction.** The owner's answer at the fork was
**through depth 3**, and that is what shipped. The guaranteed exit is its own piece and is queued
with its full design, because its destination is a world tile that does not exist yet.

---

## The register, checked first

`Facilities and spatial construction` — 23 rows — and the mining and roof families that the
coordinate shell already answers.

**Nothing in the family applies**, and the reason is that this change adds no building, no
terrain and no roof behaviour. It only decides how deep a **found** door may lead, inside a
system that has been in the build since 0.6.x. The one adjacent concern — mods that remove
mountain roof — was closed in 0.6.4-dev by `BackroomsContainmentMapComponent` and is untouched
here.

---

## What shipped

`NaturalFrontierService.MaximumNaturalDepth = 3`.

The Backrooms hands a branch **three bands for free** — the shallow yellow rooms where a
frontier on an ordinary map mints depth 1, and two steps inward — and then stops handing out
doors. Past that, deeper is a machine's job.

That is the convergence this start needed. *"Till they would need to build their own gate"* is a
design statement about **when the company game becomes necessary**, and putting the wall at depth
3 puts it early enough that building a gate reads as the obvious next goal rather than an
afterthought.

### It caps going deeper, never coming out

The cap is applied **after** the way-out attempt, and that ordering is the whole safety of it:

```csharp
if (source != null)
{
    CompanyActionResult wayOut = TryRecordWayOut(door, origin, campaign);
    if (wayOut != null) { return wayOut; }
}

int depth = source == null ? 1 : source.Depth + 1;
if (depth > MaximumNaturalDepth)
{ return CompanyActionResult.Refused("RR_Frontier_BeyondNaturalReach"); }
```

**Capping both directions would make depth 3 a trap** — a crew standing at the deepest natural
band with no door home and no way to find one. Invariant 28 forbids an unavoidable failure, and
this is precisely the shape one would take. It is now asserted rather than trusted to the reading.

### It refuses rather than quietly minting something shallower

A door that led somewhere other than where it should would be a **quieter and worse lie** than
being told plainly that nothing natural goes further. The refusal carries a real string:

> *"The door goes on, and nothing anybody can walk through goes with it. Whatever is past this is
> only reachable through a gate of your own."*

Which teaches the rule at the exact moment it bites.

### It restrains the doors, not the player

*"This is all open eneded they can play how they choose."* The cap is a property of **found
doors**. It stops nobody doing anything: a built gate reaches any depth it has earned, exactly as
before, and a player who never wants to go deeper never meets the wall at all.

---

## The vocabulary checker earned its keep

The first version of that string said *"The **doorway** goes on"*. `check-info-cards.py` refused
it:

> *a plain door is a 'door'; the far-side arrival point is a 'threshold'*

**The string was wrong and the rule was right.** The mod has an enforced vocabulary — gate,
connection, threshold, door — settled in 0.10.2-dev precisely so that a player reads one set of
words for one set of things. Fixed the string, not the rule.

---

## A claim of my own that was failing open

The ordering claim above was first written as a string-index comparison over the literal text
`"depth > MaximumNaturalDepth"`.

Fault-planting it exposed the problem: a plant that reordered the cap **using a differently named
variable** made the search return −1, so the proof failed — but it failed on *"the expression is
missing"*, not on *"the order is wrong"*. The same claim would have **reported a pass** for a
genuinely reordered cap that happened to keep the original variable name in some other place.

> **A claim that can fail for the wrong reason can also pass for the wrong reason.**

Rewritten to key off the **refusal itself** — `Refused("RR_Frontier_BeyondNaturalReach")` — which
is the thing that actually happens and cannot be renamed without the keyed string moving with it.
Now it splits into two claims that mean what they say:

| Claim | Catches |
|---|---|
| the depth cap refusal exists | nothing stops the natural chain, so free doors go on forever |
| the way-out attempt runs before the depth cap | the deepest band is a trap |

And re-planted: a genuinely reordered cap now reports **`the depth cap refusal exists` OK** and
**`the way-out attempt runs before the depth cap` FAIL**, which is exactly right.

This is the fourth time this session an assertion needed correcting, and it is a **new** failure
mode. The first three were assertions that were simply wrong. This one was *right about the
property and wrong about how it looked for it* — invariant 145 said an assertion should be written
from what the code throws on rather than what it looks like, and a string-index search over a
variable name is the second kind wearing the first kind's clothes.

---

## Fault-planted three ways

| Fault planted | Caught by |
|---|---|
| `MaximumNaturalDepth = 5` | *"the natural depth limit is 3"* |
| the cap moved **before** the way-out attempt | *"the way-out attempt runs before the depth cap"* |
| the keyed string deleted | *"has a keyed string — the player would be shown the raw key"* |

All restored, proof holding.

---

## Receipts

| | |
|---|---|
| Version | 0.12.1-dev |
| Build | 168 C# files, 86 package files, **0 warnings, 0 errors** |
| New defs, art, audio or texture | **none** |
| Harmony | **none** |
| New keyed strings | **1** |
| Checkers | **eight**, all passing; info-cards caught a vocabulary breach |
| Proofs | **seven**, all holding; the starts proof gained four claims and one was rewritten |
| Game launched | **no** |

**Still owed on this direction, and queued with its design:** the *guaranteed* exit on level 1.
It emerges on a **fresh world tile chosen by the seed** (owner's answer at the fork), which is a
world map that does not exist at new-game — so it needs a tile derived from the branch seed, a
player settlement created on it, its map generated on first use, and a two-way route registered
between a Settlement-parented Backrooms map and that new map. The existing emergence path cannot
serve it: it requires a `CompRimroomsEmergence` anchor, which is **a door the player marked on a
map they already hold**, and a solo/group start holds none.

After that: the solo/group tutorial line — *"the tutorial like quest chains should lay it all
out"* — which needs per-start scoping on the request shape, and which **guides without railing**.
