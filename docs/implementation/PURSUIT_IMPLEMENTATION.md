# They follow you (0.9.5-dev)

**Baseline:** `6ededbe` (0.9.4-dev, 156 C# files, 79 package files).

**This checkpoint — 0.9.5-dev:** **156 C# source files**, **79 approved package files**. Zero warnings, zero errors, `TreatWarningsAsErrors` on. Assembly SHA-256 `C5160083A4903117221AF361E39C4709A6EF0B5E58755971513EE67640180E10`, reproduced by **two** full recompiles after deleting `obj/` and `bin/`.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"and at deeper levels i do want monstrosities and npcs to "Chase" pawns/ kill them all the way to the gate"*

## What was already there, and why it did the opposite

A hostile inhabitant was given a **`LordJob_DefendPoint`** with a twelve-cell radius, and the comment beside it said why:

> *"A defend-this-place lord rather than an assault lord: the warning-first rule requires that a player who backs off is not pursued across the whole space."*

That was a deliberate decision, and at shallow depth it is still the right one — it is what makes an early coordinate somewhere a lone survivor can retreat from. The owner's direction is not that it was wrong; it is that **it should stop being true as you go deeper**.

## The threshold already existed and did not need inventing

`Band.Hostile` is defined in the pressure ladder as:

> *"More than one thing acts, and the space stops being forgiving."*

That is the owner's *"deeper levels"* already written down, arrived at from depth, operating history, technology and colony wealth together. Inventing a second threshold beside it would have given the same idea two definitions that could drift apart.

So: **below `Hostile`, unchanged. At `Hostile`, it hunts.**

## No pursuit code was written

RimWorld's own assault lord already walks a hostile toward whoever it can reach. *"All the way to the gate"* needed nothing added, because **the threshold room is excluded from spawning, never from being walked into** — a hunter follows a fleeing crew right to the doorway on vanilla behaviour alone.

This is the fifth time this session a requirement has been met by an existing guarantee rather than new code, and it is worth stating rather than quietly relying on.

## What is switched off, and why

Kidnapping, stealing, fleeing and timing out are all disabled.

Every generated coordinate has map edges, because every generated map does. A kidnapper carrying somebody off one would be **a disappearance with no story attached to it** — the player loses a colonist to a hostile walking into the fog, with nothing to find and nothing to do about it. What the direction asks for is something that *follows you*, and the countermeasure stays exactly what it always was: leave.

## A bug caught by reading the diff

`LordJob_AssaultColony`'s first parameter is the **assaulter's** faction. The first version passed `Faction.OfPlayer`, which names the player as the attacker.

It compiled, and no checker would ever have caught it — the type is right and the value is a real faction. It was found by re-reading the change against the decompiled constructor, which is the only thing that would have found it short of launching the game.

## The frozen threat rules still hold

- **Readable warning** — a hostile is still announced when it is placed, exactly as before.
- **Learnable rule** — the band is visible in the coordinate's readout, and the change in behaviour is tied to it rather than to a hidden roll.
- **A countermeasure** — leave, or do not go that deep.
- **No unavoidable instant failure** — `MaxSimultaneousEncounters` is still an absolute 3, quiet rooms are still required content, and the threshold room still spawns nothing.

## Not done, and named in `TODO.md`

- **Coming through the gate into the colony.** The other half of the owner's sentence, and a larger piece: it inverts the mod's founding rule and needs its own diff, its own permission rule at `PortalTraversalPolicy`, and a technology condition that can actually fire.
- The legacy `RR_QuietPursuer` and its scripted first-slice chase, still pending retirement in M2. **This checkpoint deliberately did not touch it** — it is a separate, older system on a custom def.

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors. Determinism: recompiled **twice** from clean; identical SHA-256.
- All five checkers pass.
- Compliance: **no new def, asset, patch operation or work type.** One method added, one call changed.

## For the post-completion test phase

Confirming a hostile in a `Quiet`, `Unsettled` or `Active` coordinate still holds its ground and lets a player back away; that one in a `Hostile` coordinate pursues across rooms and into the threshold room; that it never leaves the map with a colonist; that the announcement still fires; and that a player who reaches the gate and leaves is not followed through it — which is the next checkpoint's job to change deliberately.
