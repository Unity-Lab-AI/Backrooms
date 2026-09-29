# The way out was already there — 0.12.2-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built, including the design it retired one
checkpoint after shipping it. Never rewritten.

---

## The direction, now satisfied

> *"and remember the solo/group start in a backroom needs to **100% have a exit to map natural
> portal** on their first backrroms level"*

0.12.0-dev shipped the opposite. 0.12.1-dev built the *"to an extent"* half — the depth cap — and
said plainly that the exit was still owed. **This is the exit.**

---

## The constraint that decided the architecture

The guaranteed exit needs a **registered** connection, and reading
`RimroomsPortalNetwork.Register` turned up a hard requirement nothing had written down:

```csharp
RimroomsDestinationMapParent site = secondAnchor.Map.Parent as RimroomsDestinationMapParent;
if (coordinate == null || coordinate.site != site || site == null || !site.LayoutReady ||
    site.CoordinateId != coordinateId) { return PortalNetworkResult.UnknownCoordinate; }
```

**The Backrooms side of every connection must be a real coordinate map.** And the *starting* map
can never be one: `Game.InitNewGame` generates it for a player `Settlement` world object and logs
an error without one, so the starting map's parent is always a `Settlement`.

So **0.12.0's design was the thing standing in the way.** Generating the starting map *as* a
coordinate was elegant, built clean, and passed its proof — and it made a registered exit
impossible. The alternative was to widen the validation **every existing gate depends on**, which
is the riskiest change available in this codebase.

Taken to the owner rather than decided quietly. The answer: ***"Two maps at start, coordinate is
real"***.

---

## What the opening does, and why the order is the safety

`SoloGroupOpening.Open`, from `PostGameStart`, after the branch exists and before the welcome
letter:

1. **Mint the coordinate** — `CreateDiscoveredCoordinate("opening", depth)`, a stable id so a
   reload or a retry resolves to the same space instead of a second one.
2. **Generate its map** — `DestinationService.EnsureSite`, the same path every gate destination
   uses. Nothing here is a special case of the generator.
3. **Mark the surface door** — `CompRimroomsEmergence.Mark()`, which re-checks that the door is on
   an ordinary branch map with a standable approach. The same validation the network will repeat.
4. **Register the connection** — an ordinary `Emergence` edge. Not a new kind, not a new code path.
5. **Move everybody inside** — last.

**Step 5 is last on purpose.** A failure anywhere above leaves the whole party standing safely on
the surface with no exit registered, which is recoverable. Moving them first would seal a group
inside a coordinate with **no registered way out** — the exact trap invariant 28 forbids. The proof
asserts the ordering rather than trusting the reading, and a plant that moves the party first fails
it immediately.

Step 3 before step 4 for the same reason: the network refuses an unmarked `Emergence` endpoint, so
marking afterwards would produce a coordinate, a map, and no connection.

### Why this is 100% and a survey is not

`NaturalFrontierService` finds a way out at roughly **one door in twelve**, and only when a way
home is already marked. **A draw cannot deliver a guarantee.** This registers the edge directly,
once, at the opening. The exit is not something the player might find; it is already there.

---

## What the surface map holds

**One small concrete shell, seven by seven, with one door in it. Nothing else.**

That door is where the Backrooms comes up, and it is where they will come out. No power, no
furniture, no stockpile — everything a facility needs, they build. The whole point of this start is
that nobody prepared anything for them.

The start def **names** which door is the way out, in `emergenceDoorCell`. Guessing would put the
exit somewhere different depending on scan order, and the player would have no way to know which
door mattered. `ConfigErrors` refuses a cell that is not in the start's own `doors` list, because
no door is generated at such a cell and there would be nothing to mark.

---

## What was retired, and archived

`GenStep_InsideStart` and the `RR_InsideStart` map generator are **gone**, archived verbatim at
`historical-content/0.12.0-dev/RETIRED_GENSTEP_INSIDESTART.md` with the reason. Invariant 37:
retired content is archived, never deleted.

**`BuildShell` stays.** It was extracted so that class could share it, and now has one caller
again — but it is not unused, it is the destination generator's own shell, and it is the single
implementation that carries invariant 13. Reverting a clean extraction to undo a dependency that
no longer exists would be churn.

`insideStart` changed meaning, and the field documents it: it used to say *the starting map is a
coordinate*; it now says *the starting people begin in a coordinate beside the surface map*.

---

## Two invented keys, caught

`check-keyed-strings.py` refused `RR_Portal_InvalidState` and
`RR_Portal_LocalThresholdUnavailable` — keys I made up while writing the refusal paths. The real
prefix is built by the service:

```csharp
private static CompanyActionResult Refuse(string suffix)
{ return CompanyActionResult.Refused("RR_PortalAddress_" + suffix); }
```

**A refusal key that does not exist shows the player the raw key**, and the only reason it was
caught before shipping is that a checker asks in both directions. Corrected to the real strings,
which already existed and already said the right thing.

---

## Fault-planted three ways

| Fault planted | Caught by |
|---|---|
| the party moved **before** the connection is registered | *"the way out is registered BEFORE anybody is moved inside — a failure would seal the group inside"* |
| the door marked **after** registration | *"the door is marked before the connection is registered"* |
| `emergenceDoorCell` moved off the start's own door | *"emergence door is one of its own doors — no door is generated there, so there is nothing to mark"* |

All restored, and the starts proof now holds over three starts, three layouts, the opening
sequence and the natural chain.

---

## Receipts

| | |
|---|---|
| Version | 0.12.2-dev |
| Build | 168 C# files, 86 package files, **0 warnings, 0 errors** |
| Retired | `GenStep_InsideStart`, `RR_InsideStart` — archived |
| New defs, art, audio or texture | **none** |
| Harmony | **none** |
| New keyed strings | **1** |
| Checkers | **eight**, all passing; keyed-strings caught two invented refusal keys |
| Proofs | **seven**, all holding; the starts proof gained six claims |
| Game launched | **no** |

**Recorded and queued, arriving mid-checkpoint:** *"natruals can not be destoryed or moved, so one
can technically build a roomm directly on the other side of the portal door and it shouldnt
interfere with the portal transition"*. A natural gate is a Core `Door` today, which has hit points
and a deconstruct designation — so it is very probably destructible, and a wall built on its
approach cell would very probably break a connection the design calls permanently open. Both are
checked first, not assumed.
