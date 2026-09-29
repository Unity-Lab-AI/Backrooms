# Something is not where you left it (0.10.3-dev)

**Baseline:** `fe743dd` (0.10.2-dev, 158 C# files, 79 package files).

**This checkpoint — 0.10.3-dev:** **159 C# source files** (one new), **79 approved package files**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `081A4DA33DD2D3CEF92D856E7B7926222B491EDDADCB73ECEB84742DABBC0D9F`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"remembner alot of things you should be reviewing the prep materials and registry for especially backroom themed items equip,memntn and questes and logic and game paly and factions and random events and backrooms make ups you should be doing deep dives into the univers's make up of backrroms to properly design all the sustems events and specialities involved with this mod"*

So this was found by reading the prep material rather than by inventing something.

## What the prep material said, and what had been skipped

`UNIVERSE_ADAPTATION.md` lists how ordinary interiors are made uncanny:

> *"Use intentional spatial changes such as a shifted doorway, impossible adjacency, repeated hall, changed room dimensions, or **a feature that has moved since the last visit**."*

Checked one by one against what is built:

| Change | Built |
|---|---|
| shifted doorway | yes — layout derangement, 0.8.6-dev |
| impossible adjacency | yes — hallway branching and derangement |
| repeated hall | yes — corridor loop and mismatch events |
| changed room dimensions | yes — `Derange()`, clamped 8–17 |
| **a feature that has moved since the last visit** | **no** |

Four of five. The missing one is the only one that **depends on the player's own memory** rather than on the geometry: the room is the room, the route is the route, and the workbench is four cells from where it was.

## Why it is not the rearrangement anomaly

`RR_Anomaly_Rearrangement` already exists and is a different idea: it moves **loose items during a session**, at depth four and above, and **announces itself with a letter**.

This moves **fixtures between visits**, **silently**, at any depth a coordinate has been opened twice.

They are opposites deliberately. An anomaly you are told about is a thing that happened *to you*. A chair that is somewhere else is a thing that happened **while you were not there**, which is the older and worse idea.

## The proof changed the design

The first version fired on **every single return** — 100% across 4,000 simulated visits. That is mechanical, not uncanny: a player would simply learn that coming back moves things, and the effect would become a mechanic to plan around.

**The unease depends on not being sure whether you misremembered.** So a once-per-visit roll now leaves roughly a third of returns exactly as they were:

| | |
|---|---|
| returns that change something | **66.7%** |
| nothing moved | 33.3% |
| one / two / three moved | 20% / 20% / 26.7% |
| a first visit changing anything | **never**, across 500 seeds |
| a sparse room, 3 fixtures | still fires on 267 of 400 returns |

This is the second time this session an offline proof has changed a design rather than merely confirming one.

## Nothing is told to the player

No letter, no message, no alert. A player who never notices has lost nothing; a player who does notice **found it themselves**. It is recorded in the company log, so the discovery is checkable after the fact rather than announced before it.

This does not breach the warning-first rule: that rule governs **threats**, and a bench in a different corner cannot hurt anybody.

## What it will never touch

- **Anything the player built or owns.** Ownership is the whole test — generation places things with no faction, the player's work belongs to the player. One check, no list of what they might have built.
- **The way back.** The return threshold is excluded, as from every other system here.
- **Doors, and anything on a room's edge.** Displacement happens strictly inside the room interior the dressing pass already treats as safe, so a moved fixture **can never seal a route**.
- **The layout fingerprint.** Only furnishings move; room geometry and the graph are untouched, so a revisited coordinate still re-plans byte-identically.

## Not done, and named in `TODO.md`

The remaining field-gear replacements, then the last two scenarios. Also still unbuilt from the same prep document: *"contradictory accounts"* from a returning crew, and staff **prior exposure** affecting an expedition.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All six checkers pass.
- `.local/register/proof-displacement.py`: 4,000 simulated returns; first visits never change, the count ladders 1–2–3 and caps, sparse rooms still fire, and a return replays identically.
- Compliance: **no new def, asset, patch operation or work type.** One source file, one keyed string.

## For the post-completion test phase

Confirming a first visit never changes anything; that returning sometimes does and sometimes does not; that what moved is always a generated fixture and never a player's own construction; that the return threshold never moves; that no moved fixture blocks a doorway or seals a route; and that reloading a save and re-entering finds the same fixtures in the same places.
