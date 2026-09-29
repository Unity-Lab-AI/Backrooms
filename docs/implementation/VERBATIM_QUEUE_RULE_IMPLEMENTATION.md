# LAW #0, made checkable (0.10.1-dev)

**Baseline:** `5740a94` (0.10.0-dev, 158 C# files, 79 package files).

**This checkpoint — 0.10.1-dev:** **158 C# source files**, **79 approved package files**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `B0878FAE21A2EC14A7DA9AD06E2B2280EB481F985935087EF0BD4E973EFFA094`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"it seems i could be wrong but it seems like sometimes i dont see you record the verbatiums and then build them into tasks of the todo prperly, documenting them alll, idk"*

## The owner was not wrong

The right response to that was to measure it, not to argue about it. An audit of seventeen directions from the current session found **fourteen recorded in `TODO.md` and three not**:

- *"dopnt flag shit!!! ask me then and there"* — in `NOW.md` and in persistent memory, never in the queue.
- *"…in vinilla any number of pawns can use a door at once so we dont want limitations"* — in `NOW.md` and `FINALIZED.md`, never in the queue.
- *"gate doors expansions can NOT be done on a working gate"* — in `FINALIZED.md` only.

All three were **implemented correctly**, so no work was lost. But the queue is supposed to be the record of what was asked for, and for those three it was not. That is exactly the failure the owner described.

Then the rule written to prevent a recurrence found **seven more** from earlier in the run, including *"we cant have backrooms npc pawns all dying off if a person is slow to explore"* and *"WE ARE NOT EDITING OTHER PEOPLES MODS!"*.

**Ten directions total, now recorded verbatim.**

## The rule

A direction quoted in `FINALIZED.md` is, by definition, something that shipped. If it never appeared in `TODO.md`, it **skipped the queue entirely**. That is now a build failure.

It is not a promise to do better. It is a check that runs at every checkpoint, and it caught seven things I had not noticed.

## Two things that would have made it useless

**Markup false positives.** The same direction is quoted in one ledger with escaped quotation marks and in another without. Comparing raw text reported those as missing directions. Comparison is now normalised — backslashes stripped, whitespace collapsed, case folded — so it fires on **words**, not on markup.

**Continuation prompts.** *"get to it all we are finishing everything"* is genuinely the owner's words, and a queue entry for it would say nothing anybody could act on. Six of those are listed **explicitly** rather than matched by a pattern, because an over-eager pattern would swallow a direction carrying real content alongside a *"get to it"* — which has happened repeatedly in this project, most recently with *"get to it hallways can have furniture and produiction benches too…"*, a genuine design direction that begins with exactly that phrase.

Explicit lists, reviewable one line at a time, are the same discipline the retired-def list and the stale-branch list use.

## Proved

`.local/register/prove-doccheck.py` now plants a direction into the archive that exists nowhere in the queue, and confirms the build fails. Alongside the four existing plants and the dated-record exemption, every rule in this checker has been shown to catch its own fault and only its own fault.

## Not done, and named in `TODO.md`

Unified terminology — **gate**, **connection**, **threshold** — decided and not yet enforced. The remaining field-gear replacements and the last two scenarios.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All six checkers pass.
- Every rule proved by planting its own fault; the exemption proved by planting faults it must ignore.
- Compliance: **no new def, asset, patch operation or work type.** One checker rule, ten directions recorded.

## For the post-completion test phase

Nothing here reaches the game.
