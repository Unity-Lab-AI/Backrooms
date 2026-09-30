# Letting a place go — 0.12.51-dev

## The question, verbatim

> *"yeah so if the player discovers and goes through a natural gate how do they turn them off to
> use the machine gates for more controll and aiming deeper?"*

> *"get 5 natural gates u cant use a machine gate"*

Asked how the player should do it, the owner chose an **Operations held-places list with a Release
button**, over a door gizmo alone, over both, and over an automatic timer.

## The correction this work forced, and it makes the trap worse

The previous checkpoint's record said discovering a gate was **free**, because no map was generated
until somebody crossed. **That is wrong.**

`NaturalFrontierService.Discover` calls `PortalAddressService.RegisterNaturalAddress`, which calls
`DestinationService.EnsureSite` **immediately** — because a natural edge is registered against the
far side's own `ReturnAnchor`, and that `Thing` does not exist until the map does.

**A discovery costs a slot the moment it is made.** Two things follow:

- the budget check in `Discover` is **load-bearing rather than over-eager**, as that record wrongly
  implied;
- the owner's trap is real **exactly as they described it** — five discoveries, not five crossings
  — and not a late-game edge case. That is why this shipped now instead of next checkpoint.

`WARREN_AND_DOORWAYS_IMPLEMENTATION.md` is **annotated rather than rewritten**, per invariant 135.

## Why a natural gate cannot simply be turned off

**Invariant 12: a natural gate is permanently open.** That is what makes it a natural gate rather
than a machine. So it is not closed, and — since the owner separately allowed destroying and
carrying — it is not closed *by* destroying either.

**What is released is the place behind it.** The door stays: still there, still marked, still
permanently open, and **remembering which place it led to.**

## The pairing has to be moved before the edge is removed

The edge is what records "this door goes to that coordinate", and every endpoint of it lives on the
map about to be torn down — so the edge must go. **It is therefore the only other record of the
pairing**, and if it is removed first the door becomes an ordinary marked door with the place behind
it unreachable for ever.

So the release writes the coordinate id onto the surface door's own `CompRimroomsEmergence`
(`shelvedCoordinateId`, saved) **while the edge still says so.**

### The order is the whole of the safety

```
1. tell every door on THIS side which place it led to
2. remove the edges into that coordinate
3. tear down the map and the world object
```

**The proof asserts this as an ordering**, by index, not as the presence of three calls. Reverse
either pair and a record points at something that no longer exists.

Nothing is remembered onto the far endpoint: it lives on the map being destroyed, so writing the
pairing there would be writing it onto nothing.

## `releasedByPlayer` exists to answer one question that cannot otherwise be answered

`EnsureSite` refuses to build a map for a coordinate that has **no site but whose rooms have been
surveyed**, because *"a broken reference must not create a competing owner or replace an already
explored graph."* That is exactly right for a fault.

**It is exactly wrong for a deliberate release, and from the outside the two are identical:** no
site, rooms surveyed. So a release writes it down, and the guard exempts **that and nothing else**:

- a **competing owner** or a **live map** still refuses even with the flag set, because those are
  real conflicts rather than an explored graph, and a release is required to have removed both;
- the flag is **cleared the moment the place is generated again**, because an exemption that
  outlives its reason is a hole — it would let a genuinely broken reference through on some later
  load.

## What a release costs, and the player is told the number

The coordinate **record and its rooms are kept**, so re-opening returns to **the same place** — the
same rooms in the same shape. **Its contents are not**, because the interior is generated from the
seed.

That is the honest price of not holding it open, and it is why this is a deliberate player action
with a red confirmation that counts the items first, rather than the eviction timer the owner
considered and rejected. A release that discarded the graph would hand the player a *different*
place back, which would be worse than either.

## What it refuses, and every refusal names itself

| Refusal | Why |
|---|---|
| `RR_Release_Headquarters` | the headquarters is not a place you let go of |
| `RR_Release_CrewInside` | a released map takes its contents with it, people included |
| `RR_Release_CrossingInFlight` | invariant 55: nobody may be part-way through |
| `RR_Release_NotHeldOpen` | a place with no live map has nothing to release |
| `RR_Release_Inactive` | the branch is not operating |

**A prisoner or an animal counts as somebody inside.** Colonists are not the only thing the player
would lose.

## Re-opening

A gizmo on the door that led there, because that is where a player is standing when they wonder why
the door no longer goes anywhere. It calls **`RegisterNaturalAddress`** — the same path that first
created the place, so there is no second implementation to drift — and:

- it is **disabled rather than hidden** when the budget is full, because a player at their limit
  needs to see what they are at the limit of;
- it **only forgets the shelved place on success.** Forgetting on failure would strand the place for
  ever over a transient refusal.

## Why a list rather than only a gizmo

The gates that fill a budget are **scattered across levels the player may not be standing on**. A
gizmo acts on the door in front of you; a player at their limit needs to see all of it at once and
choose. The door gizmo exists too, as the convenience.

The pane also lists **the colonies**, because they are the other half of the budget — a player
counting slots needs to see why three of five are gone before they blame the Backrooms. And neither
outcome of pressing Release is silent: the player pressed a button to free a slot, and a slot either
was or was not freed.

## The proof, and two more loose claims of mine

`proof-coordinate-layout.py` gained **26 claims**; `plant-coordinate-layout.py` gained **25 plants**
and the sweep is **88 of 88**.

**Two plants found claims of mine that were too loose, and both are the duplicate-string trap:**

- `DestinationService.EnsureSite(campaign, coordinate, out siteMap, out siteEntry)` appears
  **twice** in `PortalAddressService` — natural and machine registration each generate the site — so
  a presence test survived a plant that removed one of them. It is **counted** now.
- `connections.Remove(` did not match a planted `connections.RemoveAll(`. Widened to
  `connections.Remove`.

**That trap is now the single most recurrent failure mode in this project's proofs.** The rule it
keeps teaching: *a claim must remove the last thing that can satisfy it, so count what should exist
rather than testing that something does.*

## Build

**200 C# files, 91 package files**, zero warnings, zero errors. Assembly SHA-256
`378493F20F4B7CD8BB932608073434CC00315C00EE94567C50FE995CCADF1A79`, reproduced by two clean
recompiles. **Thirteen checkers pass, forty-one proofs hold.**

## What launch seven should settle

- **Operations → Places** lists the colony and any Backrooms levels, with the budget as `n/5`
- releasing a level with crew inside is **refused by name**, and releasing an empty one frees a slot
- the door that found it offers **Open this place again**, and the level comes back the same shape
- a machine gate can then be raised, which is the whole point of the question

## Still open

The **wild variation of materials** across items, equipment, walls, floors, lights, furniture and
benches, with the events, layouts and loot deeper in.
