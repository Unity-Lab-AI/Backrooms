# One set of words (0.10.2-dev)

**Baseline:** `ad435ac` (0.10.1-dev, 158 C# files, 79 package files).

**This checkpoint — 0.10.2-dev:** **158 C# source files**, **79 approved package files**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `7F0ECE7490C23886E8862C1625812FEF27C2B9E31970FC55CD161E91B8157AB7`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"also ive used alot of differnt terms for the gates.. from portals, gates, doors , the machine, the gizmo, ect ect we need a unified name throught the entire mode in all the equipment information and cards of things items resources and buildings and all things that our mod touches"*

## One word would have been the wrong answer

The obvious reading is *pick a word and use it everywhere*. Asked at the fork, and the answer was **three words for three genuinely different things**:

| | |
|---|---|
| **gate** | the machine in your wall. Always a designated door. |
| **connection** | the live link a gate holds open to one coordinate. |
| **threshold** | the doorway you arrive at on the far side. |

*"The gate is fine, the connection dropped"* says something true, and it **could not be said at all** while both were called a portal. Collapsing them would have cost the game the ability to tell a player which part failed.

**Gate already won on the evidence**: 171 player-facing uses against 13 for "portal".

## What was actually wrong

The biggest source of drift was not "portal" at all — it was **"machine gate"**, the name of `RR_MachineGate`, a def **retired in 0.9.0-dev**. It was still in **25 player-facing strings**: *"calibrate machine gate"*, *"assembling the machine gate"*, *"No company machine was found"*, *"the machine's reserve"*.

The def was gone and its name was still what the game called itself.

**84 lines across 21 files** changed.

## Key names were deliberately left alone

A player never reads `RR_Portals_Heading`. Renaming keys would be churn with real DefInjected risk and no reader benefit, so only displayed text moved — keyed *values*, and def labels, descriptions, job strings, report strings, verbs and gerunds.

## A real bug, caught by a checker rather than by reading

A global word replacement renamed a **key**: `RR_Frontier_NotADoorway` became `RR_Frontier_NotADoor`, while the C# still asked for the old name. That is a refusal a player would have seen as a raw key.

`check-keyed-strings.py` caught it immediately. The new name actually matches the new vocabulary, so the **C# reference was updated rather than the rename reverted**.

The replacement script now asserts that no key or class name changes count, so this class of accident fails loudly next time.

## Enforced, not just done

`check-info-cards.py` gained a vocabulary rule over everything a player can read. Four banned terms, each with the reason attached:

- **portal** — the machine is a *gate*; the link is a *connection*
- **machine gate** — that def was retired; it is a *gate*
- **doorway** — a plain door is a *door*; the far-side arrival is a *threshold*
- **gizmo** — RimWorld's word for a button, never a name for our gate

## Proved in both directions

`.local/register/prove-vocab.py` plants each banned term separately and confirms a failure, then plants two things that **must stay allowed** and confirms silence:

| Planted | Result |
|---|---|
| a value saying "portal" | CAUGHT |
| a value saying "machine gate" | CAUGHT |
| a value saying "doorway" | CAUGHT |
| a value saying "gizmo" | CAUGHT |
| a **key name** containing "portal" | correctly allowed |
| gate, connection, threshold together | correctly allowed |

## Not done, and named in `TODO.md`

The remaining field-gear replacements — the survey tag as a `GlowPod` with marker types, custody at a designated archive shelf, the recorder merged into the book — then the last two scenarios.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All six checkers pass.
- Compliance: **no new def, asset, patch operation or work type.** Text and one checker rule.

## For the post-completion test phase

Confirming no screen, tooltip, job report, letter or info card says "portal", "machine gate", "doorway" or "gizmo"; that a refusal about a non-door still reads as a sentence; and that the operations pane reads **Gates and connections**.
