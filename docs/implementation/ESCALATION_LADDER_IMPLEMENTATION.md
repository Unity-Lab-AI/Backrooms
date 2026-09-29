# The escalation ladder, paced against colony wealth (0.8.0-dev)

**Baseline:** `38a1abd` (0.7.9-dev, 140 C# files, 86 package files).

**This checkpoint — 0.8.0-dev:** **141 C# source files** (one new), **86 approved package files** (unchanged). Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `A9C6C6F7E12A756F9412688215B7F5DA535824A49AD77BD6D3899CF21E2FA553`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"when u add places and events to proper balance levels of colony wealth and the like so that a solo group has ability to build and get supplies on backrroms instances and find a way out before dying from metting monstrositeitys and insay psychopaths and the like in high teir hard seed ed levels of all variations"*

The ladder had been specified since 2026-09-28 with one question deliberately left open: **what does pressure scale against?** The owner has answered it — **colony wealth**.

That is the right answer for a RimWorld mod. Wealth is the input the game's own storyteller uses, so a coordinate paces against the same curve as everything else the player is facing, instead of running a private difficulty track alongside it.

## Wealth raises the ceiling. It never raises the floor.

| Term | Source | Saved? |
|---|---|---|
| Visits to this coordinate | the player went in | **yes** |
| Time worked inside it | the player stayed | **yes** |
| Depth | fixed at discovery | **yes** |
| Colony wealth | live, from player home maps only | no — it is a *cap* |

A colony that gets rich makes deep spaces **able** to become dangerous. It can never retroactively make a space the player already knows more dangerous than its own recorded history earned, because the history terms are saved and the wealth term only ever clamps them.

Backrooms maps are excluded from the wealth reading. A coordinate full of generated furniture is not something the player earned, and counting it would make a space escalate **simply because it was well stocked**.

## The three rules the owner named, as properties rather than intentions

`BandFor` reads **nothing but** fixed and saved terms. It does not read the clock, does not roll, and does not ask how many gates are open — those were the three failure modes named in the 2026-09-28 direction, and avoiding them is a property of the function rather than a discipline expected of its callers.

**A revisit resumes.** Both history terms are saved on the coordinate, so reopening a known space neither rerolls up to punish the revisit nor down to make it safe.

**Several open gates never sum.** Each coordinate carries its own history and is evaluated alone. There is no branch-wide number to add to.

## "So that a solo group has ability to ... find a way out before dying"

This is an **acceptance condition on the arithmetic**, not a hope, so three guarantees live in the file rather than in tuning:

1. **`MaxSimultaneousEncounters = 3`, absolute.** No combination of depth, wealth and history can exceed it. It is a constant rather than a curve precisely because it is the number that keeps the condition true.
2. **Half of every coordinate's rooms present nothing**, chosen by a *count* from the coordinate's seed rather than by chance — so an unlucky run of rolls can never produce a space with something in every room. *"Quiet stretches are required content."*
3. **A first visit is always quiet.** Whatever the colony is worth and however deep the space, **walking in is never the dangerous part.**

A shallow coordinate is also capped below the top band regardless of wealth. The shallow Backrooms is where a solo start has to be able to operate, and no amount of colony success is allowed to take that away.

## The ladder is load-bearing today, not a number waiting for callers

This repo has a documented failure mode — *public APIs with no callers; built, compiling, and reachable by nothing*. So the quiet-room guarantee was wired straight into generation in the same checkpoint: `RoomContentBuilder` asks `IsQuietRoom` before dressing, and half of every coordinate's rooms are now genuinely bare.

## How visits are counted, and why not from the gate

A visit is recorded on the **empty-to-occupied transition** on a Backrooms map, not on a gate opening. The owner's rule is that pressure rises from *operating history at that coordinate* — and a gate opened onto a space nobody walks into is not operating history. It also means the count cannot be inflated by cycling a gate from the safe side.

## Not done, and named in `TODO.md`

- **Inhabitant and monstrosity families.** The ladder says how many things may act and at what band; **nothing acts yet.** That is the next checkpoint and it is the one that makes the ladder visible.
- **Raising a cap as a recorded progression step**, which the 2026-09-28 direction requires.
- **A player-facing readout** of a coordinate's band.
- **Anomalous events**, as distinct from the anomalous rooms built in 0.7.9-dev.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All four checkers pass.
- Compliance: **no new def of any kind**, no asset, no patch operation, no new work type.

## For the post-completion test phase

Confirming a first visit to any coordinate at any wealth is quiet; confirming half the rooms are bare at every depth; confirming the same coordinate has the same bare rooms after a reload; confirming a revisit resumes its band rather than rerolling; confirming wealth changes a deep coordinate's ceiling but never a shallow one's past its cap; confirming several open gates do not sum; and confirming a gate cycled with nobody walking through records no visit.
