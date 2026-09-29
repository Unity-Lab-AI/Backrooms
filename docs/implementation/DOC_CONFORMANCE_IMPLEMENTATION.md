# The documents say what is true (0.10.0-dev)

**Baseline:** `578df5d` (0.9.9-dev, 158 C# files, 79 package files).

**This checkpoint — 0.10.0-dev:** **158 C# source files**, **79 approved package files**, **a sixth checker**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `1C54905192F5090A7C2F4F0D81321F1504919EB7E228CB9BB892A87265FADA73`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"we need to keep using the mod register and all the prep docs while updating old out of date docs, readmes, how tos and other docs making sure they conform to the wanted stake state"*

## What was actually wrong

`README.md` — the front page — opened with:

> **Current development version: 0.4.1-dev.**

The build was at **0.9.9-dev**. Twenty-five checkpoints stale, and the paragraph beneath it described a "pause to conserve usage" that ended long ago.

`PUBLISHING.md` — the procedure followed at every single checkpoint — named `feature/preproduction-handoff` as the working branch. The real branch has been `feature/connected-colony-portals` throughout. That one is not cosmetic: it is the document an agent follows to push, and it names the wrong ref.

In total, **28 genuine problems across 10 living documents**.

## Living documents and dated records are different things

This distinction is the whole design of the check, and getting it wrong would have been worse than having no check.

- A **living document** — a readme, a contributor guide, a publishing procedure, an architecture map — must describe the mod **as it is now**.
- A **dated record** — an implementation record, `FINALIZED.md`, `CHANGELOG.md`, a mod review — describes a moment that has passed. A record saying *"all four checkers pass"* **was telling the truth on the day it was written**. Rewriting it to say six would falsify the evidence trail this project's entire method rests on.

So dated records are never checked, and living documents are checked strictly. **48 living documents** are in scope.

## Precision mattered more than coverage

The first version of the branch rule matched any `feature/…` string and produced **26 false positives**: file paths like `feature/feature-review.md`, prose like *"feature/adapter work"*. The `DEFERRED.md` rule flagged `NOW.md` for the sentence that **forbids** deferring.

**A checker that cries wolf is one people learn to scroll past**, which is a worse outcome than not having it. So:

- Branch names come from an explicit list of names that were genuinely the working branch once.
- A retired def may be named freely **while explaining that it is retired** — the rule only fires when the line carries no retirement vocabulary at all.
- `DEFERRED.md` may be mentioned; it fails only if the document never says anywhere that it is closed.

54 raw hits became **28 real ones**, and every one was a genuine defect.

## Proved in both directions

`.local/register/prove-doccheck.py` plants each fault **separately**, so a rule that silently does nothing cannot hide behind a rule that works:

| Planted | Result |
|---|---|
| a stale version claim | CAUGHT |
| a retired working-branch name | CAUGHT |
| a retired def named as if it ships | CAUGHT |
| an out-of-date checker count | CAUGHT |
| **all four, planted in a dated record** | **correctly not flagged** |

The exemption is proved too. An exemption that leaked would quietly disable the whole check.

## It caught itself

Adding this checker made six, and the checker's own count said five — so it failed `NOW.md` on the checkpoint ritual. Its message also hardcoded the word "four" rather than quoting what it found, which it now does.

## Not done, and named in `TODO.md`

- **Unified terminology**, decided this checkpoint and not yet enforced: **gate** is the machine, **connection** is the live link it holds open, **threshold** is the doorway on the far side. Owner direction: *"ive used alot of differnt terms for the gates… we need a unified name throught the entire mode"*. It gets its own checkpoint and its own rule over player-facing text.
- The remaining field-gear replacements and the last two scenarios.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- **All six checkers pass.**
- Every rule proved by planting its fault; the dated-record exemption proved by planting four and confirming silence.
- Compliance: **no new def, asset, patch operation or work type.** One new tool, ten documents corrected.

## For the post-completion test phase

Nothing here reaches the game. The check runs without it, as all six do.
