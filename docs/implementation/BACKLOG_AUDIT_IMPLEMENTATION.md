# The queue could not answer the question — 0.12.14-dev, 2026-09-29

**Dated record.** Never rewritten. No gameplay changed; what changed is that the project can now
say how much is left without guessing.

---

## The question, and why it could not be answered

> *"okay is that todo list getting there are we getting close to having all work complete on the
> mod build to completion and thourough totality?"*

`docs/TODO.md` held **254 open rows**, and the honest answer was that **the queue could not tell
you**, because 178 of them sat in the historical master-backlog section and **their status had
never been re-measured against the code.**

A large fraction had shipped between 0.7.2-dev and 0.12.13-dev and nobody flipped a checkbox.
"Create the Async Industries new-game scenario" — shipped. "Implement Furniture & Knickknack Store
after Gate 2" — shipped 0.11.9-dev. "Implement Lone Survivor after Gate 2" — shipped 0.12.0-dev.
Some rows went stale **during this session**: arc 5's *"still owed"* list, the *"thirteen remaining
generated families"*, *"generation after the hinge"*.

**This is the same defect as the stale assembly hash and the C# file count**, and the third time
it has appeared: a plausible number that nobody re-measures. The difference is that this one was
being used to answer a question about whether the project was nearly finished.

---

## What the audit did, and the rule it obeyed

**LAW: never delete TODO information. Status changes only.** Every original word of every row is
kept, and **evidence is appended** so a future reader can re-check a flip rather than trust it — a
named file, symbol, def, version or invariant.

Four verdicts were used:

| | Meaning |
|---|---|
| `[x]` built | with a named read site, version or def |
| `[x]` superseded | with the decision that superseded it |
| `[~]` partial | **what exists and what does not, both named** |
| `[ ]` open | left alone; a note added only where the row was misleading |

Nothing was flipped on a guess. Where a claim could not be verified it stayed open.

---

## The result

| | Before | After |
|---|---|---|
| open | **254** | **107** |
| partial | 13 | **56** |
| done | 278 | **408** |
| runtime-acceptance, gates nothing | 34 | 42 |

**114 rows re-measured as built or superseded. 41 rewritten as partial with the gap named.**

---

## Four things the audit found that reading could not

### 1. No `FactionDef` exists anywhere in the package

The whole *"period and factions"* owner direction from 2026-09-28 — the 1990s framing and **seven
named universe factions** (US government, rival corporations after proprietary tech, disgruntled
ex-employees, high-tech thieves, corporate spies and saboteurs, concerned citizens) — is
**completely unbuilt.** Thirteen rows, none of them started.

It is also **explicitly authorised**: the owner answered that these are new `FactionDef`s reusing
existing pawn kinds and existing icon paths, because a `FactionDef` is world configuration rather
than a physical gameplay Def. All seven begin neutral and earn hostility from what the branch
actually does.

**This is the largest completely unbuilt owner direction remaining, and it is next.**

### 2. A comment claimed something the code does not do

`Generation/BackroomsContainment.cs` opens with *"every solid area is mineable in a variety of
materials"*. **There is no mineable-rock placement anywhere in `Generation/`.** The roofing half is
real — every unroofed cell gets `RoofDefOf.RoofRockThick`, which is what makes *"no outside"*
survive another mod's roof removal — but mineability is a sentence, not an implementation.

**Invariant 130 again**, and the reason the audit greps rather than reads. Three owner directions
turn out to be one coherent unbuilt piece: **mineable materials, reusable floor terrain, and
floors that return something when lifted.** Vanilla returns no materials for a removed floor, so
the owner's *"capte ands tile can all be uninstalled, moved, resued"* needs real work.

### 3. One row's own complaint had gone stale

*"The remaining rungs of the laboratory duration ladder … `portalWindowTierProjects` currently
names the single …"* — it names **three** gate projects and has since 0.10.9-dev. The row was
describing a state of the world that no longer existed.

### 4. Two documents described the same work from two directions

Already recorded at 0.12.13-dev and worth repeating, because the audit is how it surfaced: arc 5's
*"still unwritten"* list — relay stations, caches, guarded leases, resupply, evacuation — had had
**research projects since 0.11.6-dev**. The chart's arc names and the research tree's branch names
were the same nouns.

---

## Rows that will never close without the owner, and are marked so

Being honest about this is part of the answer to *"are we close"*:

- **performance measurement on a long-running save** — bounding is done; measuring needs a launch;
- **duplicate def and patch collisions in the exact 294 profile** — needs the profile loaded;
- **a user-facing compatibility report** — cannot state a tested order before anything is tested;
- **balance, the invalid-state matrix, the release report** — nothing here has ever been played;
- **the RWT multiplayer surface** — needs that mod present to detect anything.

These are not excuses and they are not deferrals. They are the shape of a project where **only the
owner launches the game.**

---

## One row challenged rather than closed

*"Remap RimWorld's menus, tabs, and campaign views into the finished company-first Company Command
layout."*

Left open, with the note that **it should be argued about before it is built**: remapping Core's
own menus is invasive, it would fight every interface mod in the register, and no owner direction
has asked for it since. The twelve-pane Operations tab already is the company-first surface. A row
that would be wrong to satisfy silently is worth saying so about.

---

## Receipts

| | |
|---|---|
| Version | 0.12.14-dev |
| Build | 173 C# files, 86 package files, **0 warnings, 0 errors** |
| C# changed | **none** |
| Rows re-measured | **155** |
| Re-measured as built or superseded | **114** |
| Rewritten as partial, gap named | **41** |
| Open rows | **254 → 107** |
| Checkers | **eight**, all passing |
| Proofs | **seventeen**, all exiting zero |
| Game launched | **no**, and nothing in this mod has ever been played |
