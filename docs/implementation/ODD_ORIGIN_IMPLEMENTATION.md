# Odd origin — the reason a player goes back in (0.7.2-dev)

**Baseline:** `2e93747` (0.7.1-dev, 120 C# files, 76 package files).

**This checkpoint — 0.7.2-dev:** **122 C# source files** (two new), **77 approved package files** (one new keyed file), zero warnings and zero errors with `TreatWarningsAsErrors` enabled, SDK 9.0.308, Release/net472. Assembly SHA-256 `CC35332D69E4C9E4CF75A790B8C82641C2315A6CE113EDD6C927B5E1935A2A6D`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"ik think option one can work and we can add a flag to item from the back rooms like (odd) or something like that and have quests and missions and contracts and stuff for like 1000 (odd) cotton or like 10 uninstalled electic stoves(odd) and the such for all things materials and resources ect ect that can give reason for the players to have to advance and excplore and haul and use the spaces iin the backrooms"*

This arrived as the answer to a narrow question about floors returning materials, and went a long way past it. It is the owner's design, recorded as [decision 23](../GATE_0_DECISIONS.md).

## Why it is the right shape

Thirty-one cross-map work families have been moving real goods through a gate since 0.5.0. **Nothing in the game has ever asked for those goods by where they came from.** A contract that demands *odd* cotton cannot be satisfied from the colony's own fields at any price — only by going in, working the space, and hauling it out. That converts the existing work engine into an economy, and gives ordinary Core resources a second tier of value, **without inventing a single item, texture or resource**. It is therefore inside [`CONTENT_REUSE_POLICY.md`](../CONTENT_REUSE_POLICY.md) rather than an exception to it.

## The part that was easy to get wrong

**A marked stack must never merge with an unmarked one**, and the danger runs in both directions:

- odd absorbing ordinary would **manufacture** odd goods out of colony stock, defeating every contract at once;
- ordinary absorbing odd would **destroy** goods the player crossed a gate to fetch.

Core has the exact hook, verified in source rather than assumed: `ThingWithComps.CanStackWith` consults every comp's `AllowStackWith`, and `CanStackWith` gates `TryAbsorbStack`. Three further hooks complete the feature with **no Harmony and no patch to a Core method**:

| Hook | What it does here |
|---|---|
| `AllowStackWith(Thing)` | odd and ordinary never merge, either way round |
| `PostSplitOff(Thing)` | a piece split off an odd stack is odd — otherwise splitting launders |
| `TransformLabel(string)` | the owner's "(odd)", as a **keyed string** so the word is translatable |
| `PostExposeData()` | one saved boolean |

## Minified buildings — the owner's own example

*"10 uninstalled electic stoves(odd)"* is a **building**, not a resource. Uninstalling wraps it in a `MinifiedThing` whose `InnerThing` is the original, so the comp and its saved flag travel untouched. What this costs is that **every read must look through the wrapper** — asking a `MinifiedThing` directly reports every uninstalled stove as ordinary. `OddOriginService.IsOdd` and `.Mark` both resolve through `InnerThing` for exactly that reason.

## The marker is attached in code, and why

The direction is deliberately open-ended — *"for all things materials and resources ect ect"* — so the marker has to reach every carryable thing in the loaded game, **including things from the other 274 mods**. A `PatchOperationAdd` can only append to a `comps` node that already exists, and most item defs have none, so an XML patch would apply to an arbitrary subset and **fail silently on the rest**.

Appending to `ThingDef.comps` at startup reaches all of them and stays purely additive: no def replaced, nothing removed, no other mod's files touched. Two filters keep it honest:

- **the def must actually instantiate comps** — a `thingClass` that is not a `ThingWithComps` never builds its comp list, so adding one there is dead weight that looks like it works;
- **the thing must be carryable out** — it has `thingCategories` (an item) or a `minifiedDef` (an uninstallable building).

## One place applies a mark, and that is the whole security model

`OddOriginService.MarkGeneratedContents(map)` runs **once**, at the end of generation, before the map can be reached.

The obvious alternative — mark anything that spawns on a Backrooms map — is an **open laundering route**: haul a thousand ordinary cotton in, drop it, pick it up, walk out with a thousand odd cotton. Marking only at generation means the mark can only ever be earned by taking what was already there. Pawns are skipped: a generated inhabitant is not a good to be sold by origin, and the traversal rule already governs what may leave.

## What it costs

One boolean per marked thing, one comp per carryable def. No tick, no scan, no job, no work type, no new item.

## Not done, and named in `TODO.md` rather than deferred

- **Contracts that demand odd goods.** The marker is the substrate; the quests, missions and contracts that ask for *"1000 (odd) cotton"* land on [`CAMPAIGN_ECONOMY_MODEL.md`](../CAMPAIGN_ECONOMY_MODEL.md) and the 13 mission families under M3.
- **Materials recovered by deconstructing a marked building.** Uninstalling preserves the mark because the building survives; deconstructing destroys it and spawns fresh resources through `GenLeaving`, which has no public hook. Named as its own row rather than quietly assumed to work.
- **The acceptance test for the whole feature**, in the owner's own terms: if an odd contract can be satisfied without entering a coordinate, it has failed.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors, `TreatWarningsAsErrors` on.
- Determinism: `obj/` and `bin/` deleted and recompiled **twice**; identical assembly SHA-256 both times.
- `tools/check-package-integrity.py`: PASS.
- `tools/check-keyed-strings.py`: 1,138 keys, 0 duplicates, 1,107 literal references all resolving, 0 argument mismatches.
- `tools/check-dlc-gating.py`: passes.
- `tools/research/audit-gate0.py`: PASS, zero errors.
- Compliance: no patch operation added, no asset, no new work type, no new gameplay ThingDef. Nothing of another mod copied or referenced.

## For the post-completion test phase

Confirming a generated coordinate's contents read as odd and the colony's own goods do not; carrying odd cotton home and confirming it will not merge into an ordinary stack in the same stockpile, in either direction; splitting an odd stack and confirming both halves stay odd; uninstalling a generated stove, hauling it out, and confirming the minified thing still reads odd; hauling ordinary goods **in**, dropping them, and confirming they come back out ordinary; and loading a 0.7.1-dev save to confirm existing things read as ordinary rather than odd.
