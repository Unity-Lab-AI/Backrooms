# The register, checked backwards (0.10.4-dev)

**Baseline:** `8aad46e` (0.10.3-dev, 159 C# files, 79 package files).

**This checkpoint — 0.10.4-dev:** **159 C# source files**, **79 approved package files**, a **new query tool**, a **new LAW**, and **one real defect fixed**. Zero warnings, zero errors, `TreatWarningsAsErrors` on.

**No game was launched, no test was run, no RimSort mod list was changed.**

---

## The request

> *"add a memory and a law to always check the registry of mods before building something to see what if anything applies, and do this retro actively dfor regress too"*

Three things: a memory, a LAW, and a **backwards** pass over work already shipped.

## The LAW needed a tool or it would be skipped

A LAW that requires opening a browser, scrolling a 294-row table and eyeballing a column is a LAW that gets skipped precisely when it is inconvenient — which is when it matters.

`tools/register-query.py` makes the register answerable from the command line: list system families, filter by family, search every column, print one row whole.

**It found a parsing trap immediately.** The register HTML carries **two tables** over the same 294 mods with different layouts — the second puts a Steam workshop id where the system family belongs. A naive parse returned **589 rows** and would have made every family filter miss half its matches while looking like it worked. The parser keeps the row whose family reads as a family: **295 rows**.

## What the backwards pass found

### 1. A real defect — a drafted animal could cross a gate

**Register row 78, Draftable Animals - Releashed**, is in the owner's profile.

0.9.4-dev let player animals cross a gate, and its eligibility check returned early for animals **before** testing `Drafted`. A drafted *colonist* has never been allowed through — a pawn under direct combat control does not wander off mid-fight — but a drafted *animal* could.

Vanilla cannot draft an animal, so this read as dead code. **It is only reachable on somebody else's mod list**, which is exactly the class of defect the register exists to surface and exactly the class that no amount of re-reading my own diff would have found.

Fixed in both the crossing service and the traversal policy, so the chokepoint and the service agree.

### 2. The stance-classifier bug, confirmed on a concrete row

Row 78's `Stance` column reads **Required**. Its own review reads:

> *"Provisional disposition: optional animal expedition/combat control; no required staff or threat feature."*

That is the known `disposition_stance()` negation bug — recorded as open since an earlier session, where 14 of 17 rows said the opposite of their review. **Row 78 is now a named, reproducible example**, which the open task did not previously have.

**Consequence for this LAW**: the `Stance` column is not trustworthy on its own. The per-mod review under `docs/research/reviews/mods/` is, and the LAW requires reading it.

### 3. Pursuit is independent of Search and Destroy — verified, not assumed

**Row 200, Search and Destroy (Continued)** changes hostile AI to hunt colonists, overlapping 0.9.5-dev's pursuit change. Its review requires:

> *"optional combat automation; authored threat behavior/player control remain independent."*

0.9.5-dev swaps a defend lord for **vanilla `LordJob_AssaultColony`**, which is independent by construction: it works with that mod absent and does not depend on it when present. **No change needed**, and now that is checked rather than lucky.

### 4. Roof containment already survives a roof-removal mod

**Row 188, Removable Mt.Rock Roof Patch.** Its review warns:

> *"Do not assume a mountain roof preserves normal protection after removal."*

Invariant #13 says a coordinate's roof is never removable. `BackroomsContainment` already holds two independent guarantees, and the second is written to **not care how the roof went** — any cell that loses its roof is re-roofed with thick rock. Written defensively before this mod was ever considered.

**No change needed.** This is the kind of result the check should produce most of the time, and recording it is the point: silence is not evidence of having looked.

## The register check, as it will now appear in every record

```
[REGISTER CHECKED]
System family filtered: <family>
Rows examined: <count and ids>
Applies: <what, and how it changed the design> | NONE, and here is why
```

## Verification performed

- `tools/build.ps1`: zero warnings, zero errors.
- All six checkers pass.
- Compliance: **no new def, asset, patch operation or work type.** One tool, one LAW, one behavioural fix.

## For the post-completion test phase

Confirming a drafted animal is refused at a gate and an undrafted one is accepted; that pursuit behaves the same with Search and Destroy present and absent; and that a coordinate cannot be stripped of its roof with a roof-removal mod installed.
