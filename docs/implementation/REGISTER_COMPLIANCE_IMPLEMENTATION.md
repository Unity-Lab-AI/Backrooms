# The register, by the column that matters — 0.12.20-dev, 2026-09-29

**Dated record.** Never rewritten.

---

## "Guided by the columns" named the column I had been skipping

> *"lets get it and rememebr we are trying to get shit done in droves and correctly and guided by
> the columns in the mod registar"*

The register has six columns — `load`, `mod`, `family`, `stance`, `firmness`, `trace` — and I had
been querying three of them. `family`, `stance`, `firmness`.

**`trace` is the one that answers the question the rule actually asks.** `family` says what the
*other mod* is about. `trace` says which part of **this** mod a row bears on — which is exactly
*"what applies to the thing I am about to build"*.

And it had **no query at all**. That is not a coincidence: a column nobody can ask about is a
column nobody consults. Sixteen codes are in use:

| | | | |
|---|---|---|---|
| RR-COMPAT 293 | RR-STA 149 | RR-FAC 126 | RR-EXP 74 |
| RR-THREAT 73 | **RR-OUT 65** | RR-ECO 58 | RR-DLC 40 |
| RR-EVD 31 | RR-MP 26 | RR-SPACEFLIGHT 25 | RR-UI 24 |
| RR-GATE 23 | RR-MSN 23 | RR-STYLE 16 | RR-SPACE 15 · RR-SCEN 3 |

`RR-OUT` alone is **65 rows**, and it is precisely *"a way out into the world"* — the next feature
in the queue. Querying it immediately surfaced the real neighbours of that work: Carryalls
intercontinental transport, Giddy-Up 2, Pack Mules Extended, Alpha Vehicles – Age of Sail. All
Settled, all about crossing the world map. Nothing in the `family` column would have grouped those
together.

**A truncated code was found while adding the query.** The first pattern capped codes at eight
characters and reported `RR-SPACEFLI`; the real code is `RR-SPACEFLIGHT`. A summary that silently
truncates its own keys is a summary that merges two categories into one.

---

## Guidance, not law

> *"remmebr its not law but guidance"*

That is a correction to how I had been treating it, and it changed what I built.
`check-register-compliance.py` does **not** veto work because a register row exists. It verifies
only the handful of dispositions that are **structural** — the ones that would regress silently and
that are about **this** package rather than a judgement about anybody else's:

| Check | Why it is structural |
|---|---|
| no hard mod dependency | the difference between *"works with the 294"* and *"requires some of them"* |
| every patched mod is a reviewed row | patching something nobody reviewed ships an unreviewed assumption |
| every patch sits inside `PatchOperationFindMod` | invariant 42 — optional by construction, or it is a dependency wearing a different hat |
| no `ResearchProjectDef` / `QuestScriptDef` / `StorytellerDef` | three separate reviews reached the same conclusion: use our own def types |
| no other mod's content shipped here | the owner's standing direction |

Everything advisory in the register stays advisory.

---

## What it found: nothing had regressed

```
note: no hard mod dependencies declared
note: loadAfter names Core only
note: patches 'Doors Expanded' -- row 77, Optional, Settled,
      trace RR-FAC;RR-THREAT;RR-STYLE;RR-COMPAT
note: authors no QuestScriptDef
note: authors no ResearchProjectDef
note: authors no StorytellerDef
note: every shipped file belongs to this package; no other mod's content is present
register rows parsed: 295
PASS
```

**This package patches exactly one mod, optionally, and depends on none.**

The interesting part is the third group. Three separate reviews — row 191 ResearchTree, row 279
Research Whatever, rows 148 and 132 on native quests — independently concluded that this mod should
use **its own def types** rather than the native systems those mods operate on. The build still
does, and that conclusion is now **checked every checkpoint instead of re-derived by reading**,
which is what stops it drifting the day somebody finds `ResearchProjectDef` more convenient.

The four remaining `ThingDef`s were confirmed as the known open ones — `RR_FieldRecorder`,
`RR_RouteRecording`, `RR_ReturnAnchor`, `RR_QuietPursuer` — all already tracked as the last
existing-content replacements. No new gameplay def has crept in.

---

## "We don't edit their files", asserted rather than remembered

> *"remmebr we dont change the mods we dont have rights to edit 274 or sum mods"*

A `PatchOperationFindMod` does **not** edit anybody's files — the owner confirmed that reading
explicitly on 2026-09-29. It patches the **loaded def database at runtime** and applies nothing when
the mod is absent.

So the thing that would actually breach the direction is this repository **containing** another
mod's content. That is what the checker asserts: every shipped file belongs to this package, and no
second `About.xml` has appeared anywhere under it.

---

## Fault-planted three ways

| Planted fault | Exit | Caught |
|---|---|---|
| a hard mod dependency declared in `About.xml` | 1 | ✓ |
| a `ResearchProjectDef` authored (rows 191 / 279) | 1 | ✓ |
| patching a mod that is not a reviewed register row | 1 | ✓ |
| *restored* | **0** | — |

---

## Receipts

| | |
|---|---|
| Version | 0.12.20-dev |
| Build | 173 C# files, 91 package files, **0 warnings, 0 errors** |
| C# changed | **none** |
| Checkers | **NINE**, up from eight |
| Register rows parsed by the checker | **295** |
| Mods this package depends on | **zero** |
| Mods this package patches | **one**, optionally |
| Trace codes now queryable | **16** |
| Planted faults caught | **3 of 3** |
| Game launched | **no**, and nothing in this mod has ever been played |
