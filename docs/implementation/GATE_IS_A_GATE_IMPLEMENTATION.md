# A gate that looks like a gate and is walked through like one — 0.12.53-dev

## The report, verbatim

> *"its not blue!!! it doesnt have a light aura, and it in no way is a portal to the back rooms..
> wtf!!! im getting tired of this shit... you actually have to plug all the work we did on the
> gates into the game so they work and the pawns can walk from tmap to map like the stargate mod
> works but with normal does.. wtf!!! ive said stargate mod repeaditly is how the gates work but u
> keep fucking ignoring me and doing you own fucking thing instead of codeing the door into gates
> properly so that the doors work like startgates repurposed into the backrroms gate to travel to
> it"*

**Three separate things, and all three were real.** The log settles the first one immediately, and
it is the reason the other two were invisible.

## 1. The level never generated. Again. And the cause was new.

```
[Rimrooms][Generation] Site layout stopped: RR_Generation_ContentPlacementFailed
  at GenStep_BackroomsDestination.SpawnNativeConduit
  at GenStep_BackroomsDestination.SpawnNativePowerNetwork
```

`MarkLayoutReady` never ran → `SoloGroupOpening` stopped at step 2 again → the Store's back door
was **never marked**. **An unmarked door is an ordinary steel door.** Everything the owner is
looking at follows from that one throw: not blue, no aura, not a portal.

### The cause, measured

`SpawnNativePowerNetwork` carpeted every powered room with conduit:

```csharp
poweredRoomCoverage = rooms.Where(service_passage or utility_room)
                           .Select(room.Bounds.ContractedBy(1))
```

| | |
|---|---|
| at 12×12 rooms | ~100 cells — nobody noticed |
| at depth 1, a `service_passage` is **60×80** | `ContractedBy(1)` = **4,524 cells** |
| `MaxNativePowerConduits` | **512** |

**An eightfold blowout on the first powered room, every time.** No 300×300 coordinate could ever
have generated. **The carpet was a trick sized for small rooms and the 300×300 change invalidated
it** — my change, and I should have found this by sizing it rather than by shipping it.

### The fix, which is better than raising the cap

The carpet existed for one stated reason: `RoomContentBuilder` adds another lamp to each powered
room **after** the grid is laid, so the room was pre-wired to catch it. **Wiring four thousand
cells to catch one lamp is the wrong shape at any size.**

So: wire the generator and the known consumers, then **after content placement, wire whatever else
turned up.** `ConnectStrayConsumers` uses the **same map-wide `CompPowerTrader` sweep** that
`ValidateNativePowerNetwork` already uses to *detect* a stray consumer — so the thing that reports
one and the thing that fixes one agree by construction rather than by two people remembering the
same rule.

**And it can never cost the coordinate.** `TrySpawnNativeConduit` returns where the throwing form
would throw; a lamp that cannot be reached is a dark corner. The throwing form is kept only for the
generator's own footprint, where a failure really is a generator fault.

## 2. It did not look like a gate

`CompGlower` and `CompColorable` are **both Core** and both settable **per instance** —
`GlowColor` and `GlowRadius` have setters backed by per-instance overrides, and
`CompColorable.SetColor` is per thing. So a live gate is **blue and casts light** with **no new
texture and no new def.**

### The trap, and Core's own answer to it

Adding a glower to `Door` would give **every door in every colony** one — and every door every
other mod ships. That is exactly the *"do not change what the player already owns"* rule.

**Core solves it.** `CompGlower.ShouldBeLitNow` walks **every comp on the parent** and asks any
that implements `Verse.IThingGlower`; **one false keeps the glower dark and unregistered.** So
`CompRimroomsEmergence` implements it:

```csharp
public bool ShouldBeLitNow() { return IsLiveGate; }
```

Every ordinary door carries an inert glower **refused by Core's own rule**, not by hoping a radius
of zero is enough. The patch sets `glowRadius 0` as well, so even a Core change to that interface
leaves ordinary doors dark.

**Only a gate with a real way through lights up.** `IsLiveGate` requires both the player's mark
*and* a live edge in the portal network — a door somebody marked but which nothing leads through
yet is a plan, not a gate, and lighting it blue would promise a way through that does not exist. A
gate that stops being live stops glowing and its colour is disabled.

## 3. It was not walked through the way a player expects

**This is the part of the complaint that was most fairly aimed at me.**

The travel already worked exactly as described: `PortalTravelService.OrderCrossing` makes a **real
job** that walks the pawn to the cell beside the door and crosses them to the other map. That is
the Stargate behaviour and it has been in the build for checkpoints.

**What was missing was the place a player looks for it.** The only way to ask was: select pawns,
select the door, click a gizmo, choose from a float menu. **That is a dispatch console, not a door
you walk through** — and the owner has said *"like the stargate mod"* repeatedly, which is exactly
this distinction and I kept hearing it as a statement about the destination rather than about the
interaction.

`ThingComp.CompFloatMenuOptions(Pawn selPawn)` is Core's own hook for *"right-click this with that
colonist selected"* — the same hook every piece of Core content uses for *go here and do this*. So:
**select a colonist, right-click the gate, "Enter the gate".** They walk over and go through.

**Nothing is decided there.** The order is still `OrderCrossing` and the rule is still
`PortalTraversalPolicy`, so invariant 1 holds — the menu is where the question is asked, not a
second opinion about the answer. A pawn who cannot cross is shown as a **disabled row with the
reason**, because a name missing from a menu tells the player nothing.

## The register, and the Stargate mod itself

Row **[218] Stargates!**, family *Additional portal content*, stance **No integration**. That
stance means *do not depend on it or adapt to it* — **it never meant ignore it as the interaction
model**, and treating those as the same thing is how three checkpoints went by with the order
buried in a gizmo.

## The proofs, and eight loose claims of mine

`proof-generation-batch.py` gained **7 claims** and `proof-gate-links.py` gained **10**. Sweeps are
**50 of 50** and **32 of 32**.

**Eight claims written this checkpoint were loose enough for a plant to walk through**, all one
family:

| What it read | Why the plant passed |
|---|---|
| `"poweredRoomCoverage" not in genstep` | named the **retired symbol**; a re-carpet under a new name walked past |
| `"throw" not in stray_body` | swapping `Try…` for the throwing form adds no `throw` **at the call site** |
| `"wiredCells.Count >= Max…" in stray_body` | appears **twice**; the harness replaces the first |
| `"CompProperties_Glower" in doorpatch` | **prefix** of `…GlowerUnused` |
| `"CompProperties_Colorable" in doorpatch` | same |
| `"colorable.SetColor(…)" in gatecomp` | survives being wrapped in `if (false)` |
| `"network.Connections" in live_body` | a later use survived an early `return true` |
| nothing asserted `if (!IsLiveGate) { yield break; }` | so the menu could be offered on any door |

**And the fix for the prefix trap fell into the prefix trap:** asserting
`"SpawnNativeConduit(map, …" not in stray_body` fails against *correct* code, because
`TrySpawnNativeConduit` **contains** `SpawnNativeConduit`. It strips the safe calls first now.
That is the most on-the-nose lesson this session has produced.

**The arithmetic that caused the outage is now a claim**, not just a fixed line: the proof computes
the 4,524-cell carpet from the planner's own constants and asserts it exceeds the cap — so any
future per-room area pass fails on the number that proves it.

## Build

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`3FD8054EB0EA1F3BFC9DA7D954F6E0796B3462A52D7B115E632D9905E7758A7C`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-one proofs hold.**

One checker earned its keep again: `check-package-integrity.py` refused the new patch because an
XML comment contained `--`, which is illegal inside an XML comment and would have been a silent
def-load failure.

## What the seventh launch should settle

1. **does a coordinate generate** — the conduit throw is gone, and this is the third attempt
2. **is the back-room door blue and glowing** once the level exists
3. **select a colonist, right-click the gate → "Enter the gate"** — they should walk over and appear
   on the other map
4. **every other door in the colony is unlit and unchanged** — the `IThingGlower` veto
