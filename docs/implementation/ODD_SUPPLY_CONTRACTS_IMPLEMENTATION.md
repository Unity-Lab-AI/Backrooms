# Odd supply contracts — somebody who actually wants the goods (0.7.3-dev)

**Baseline:** `a4c3703` (0.7.2-dev, 122 C# files, 77 package files).

**This checkpoint — 0.7.3-dev:** **123 C# source files** (one new), **78 approved package files** (one new keyed file), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `D2D3C6E6F906B4AB698ED1D6C01C45BB616D67E0581D99FDA7E70FF8B8F64569`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"have quests and missions and contracts and stuff for like 1000 (odd) cotton or like 10 uninstalled electic stoves(odd) and the such for all things materials and resources ect ect that can give reason for the players to have to advance and excplore and haul and use the spaces iin the backrooms"*

0.7.2-dev built the marker. **Without a buyer, "(odd)" is a label nobody reads.** This is the half that makes it an economy.

## The decision that shaped everything else

The tempting implementation is to pick any thing definition in the game and demand a pile of it. **That produces contracts a player cannot possibly fill.** A thousand odd cotton is unanswerable if no space the branch has ever opened contained cotton, and the player would spend hours hunting something that was never down there — then conclude the feature is broken, correctly.

So **every coordinate records the distinct definitions it really produced**, once, at generation, and a demand is only ever drawn from the union of those records. `CoordinateRecord.oddGoodsDefNames`, filled by the same pass that applies the marker.

That also gives the loop its shape, and it is a better shape than the naive one: **open a space, see what it holds, and buyers appear who want it.** Exploration drives demand instead of demand arriving from nowhere.

## Bounded, deterministic, saved

| Property | Value, and why |
|---|---|
| Open at once | **3.** A long campaign cannot accumulate an unbounded backlog of contracts nobody will ever fill. |
| Offer interval | **60,000 ticks** — about a day, so demand arrives at a readable pace rather than flooding. |
| Choice of goods | `Gen.HashCombineInt(campaignSeed, supplyOfferIndex)` — **never `Rand`**, so reloading a save cannot reroll a hard demand into an easy one. |
| Quantity | Scaled by the thing's own `stackLimit` — a few stacks of a stackable resource, **2–10 of an unstackable**, which is the owner's *"10 uninstalled electic stoves"*. |
| Payment | The thing's own `BaseMarketValue` × count × **6**, clamped. Built from the game's economy so it tracks any mod that changes a value, rather than from a table this mod would have to maintain against 294 other mods. |

The ×6 is because the buyer **cannot source these anywhere else**, and because the player paid in gate time, power and risk rather than in silver.

## Settlement

Payment goes through the same idempotent `PostTransaction` every other contract uses, keyed by operation id. **Payment happens before the goods are consumed, deliberately:** it is the idempotent step, so a save reloaded mid-delivery reports "already applied" rather than paying twice, and the goods are consumed exactly once either way.

Matching reads through `OddOriginService.IsOdd`, which resolves a `MinifiedThing` to its `InnerThing` — **the owner's own stove example, and the case that would silently never settle** if the wrapper were asked directly. Burning things are excluded for the same reason any Core delivery excludes them.

## One integrity rule had to change, and it is worth stating

`RimroomsCampaignComponent` validated that **every** contract names a coordinate that exists. An odd-supply contract is **branch-wide**: it buys goods by origin, and any coordinate that produced them satisfies it. So it legitimately carries no coordinate id, and leaving the old rule in place would have faulted a perfectly valid save. The check now asks the right question of each kind rather than the same question of both.

## Save compatibility

A coordinate saved before 0.7.2-dev has no recorded odd goods. **An empty list is the honest answer** — that coordinate simply offers no supply contracts of its own — rather than inventing contents for a space generated before any of this existed. `supplyOfferIndex` and `lastSupplyOfferTick` default such that an existing branch begins offering from its first interval after load.

## Not done, and named in `TODO.md` rather than deferred

- **Missions and quests**, as distinct from contracts. The owner asked for *"quests and missions and contracts"*; this is the contract third. The other two want the 13 mission families under M3.
- **A player-facing surface.** Offers and settlements are recorded events today; the Operations pane does not yet list open odd demands. Owned by M5.
- **Materials recovered by deconstructing a marked building** — still uncovered, still named. Uninstall preserves the mark; deconstruct destroys the thing and `GenLeaving` exposes no public hook.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and recompiled **twice**; identical assembly SHA-256 both times.
- `tools/check-package-integrity.py`: PASS.
- `tools/check-keyed-strings.py`: 1,142 keys, 0 duplicates, 1,111 literal references all resolving, 0 argument mismatches.
- `tools/check-dlc-gating.py`: passes. `tools/research/audit-gate0.py`: PASS, zero errors.
- Compliance: no patch operation added, no asset, no new work type, no new gameplay ThingDef.

## For the post-completion test phase

Confirming no demand is ever offered before a coordinate has been generated; confirming a demand names something a coordinate actually held; filling one with odd goods and confirming payment lands once and the goods are consumed; attempting to fill one with ordinary goods of the same def and confirming it does not settle; delivering with an **uninstalled building** and confirming the minified wrapper is read correctly; reloading mid-settlement and confirming no double payment; confirming no more than three stand open; and loading a 0.7.2-dev save to confirm existing coordinates offer nothing rather than faulting.
