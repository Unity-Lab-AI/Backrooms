# The documents use the mod's own words — 0.10.6-dev, 2026-09-29

**Dated record.** Describes the checkpoint as it was built. Never rewritten.

---

## The direction

> *"read now.md to continue the work completing the mod, and also real quick did we finish up
> that doc regress work and the later stuff i said about cleaning up text walls for everything
> making them a pleasure to read, lets make sure the docs and informations displays in game are
> proper to backrrooms universe and rimworld gameplay style of all displayed informations of
> varying types to include all."*

The in-game half shipped in 0.10.5-dev. This is the document half, and the answer to the two
questions.

---

## The two questions, answered with numbers

The owner asked whether two earlier pieces of work were finished. Both answers were **partly**,
and both were measured rather than asserted.

### *"did we finish up that doc regress work"*

`check-doc-conformance.py` shipped in 0.10.0-dev and closed **twenty-eight stale claims across
ten living documents**. It passes, and has passed every checkpoint since.

Its rule set was **five rules wide**: the version a document claims, the branch it names, a
retired def described as live, the checker count, and `DEFERRED.md` described as a live queue —
plus the LAW #0 rule that every archived owner direction reached the queue.

It did **not** check the vocabulary, and it did **not** check readability. A sweep on
2026-09-29 found the retired word in prose **262 times across 30 living documents**, with code
spans, file names, the branch name and owner quotations all excluded from the count.

So: the drift the checker covers is closed. The drift it did not cover was open, and is
now either fixed or counted.

### *"the later stuff i said about cleaning up text walls"*

`About.xml` was un-walled in 0.10.4-dev, and `check-info-cards.py` gained a 420-character wall
rule over **every string the game displays**, which passes. `tools/make-readable-html.py`
renders seven documents to standalone styled HTML.

What was never done is the documents themselves. **Twenty living documents carried prose lines
past 400 characters**, the worst being a single paragraph of 1,467. The game's text was clean;
the text a human sits down and reads was not.

---

## What shipped

Two new rules in `check-doc-conformance.py`, over a named **reader-facing set**:

| | |
|---|---|
| `README.md` | `docs/HOWTO.md` |
| `docs/COMPATIBILITY.md` | `docs/GAME_DESIGN.md` |
| `docs/SCENARIOS.md` | `docs/BUILDING.md` |
| `docs/RESEARCH.md` | `docs/CONTENT_REUSE_POLICY.md` |
| `docs/RIMROOMS_MOD_OVERVIEW.md` | `docs/TUTORIAL_SCRIPT.md` |
| `docs/CREDITS.md` | |

**Rule 7 — the vocabulary.** The same terms `check-info-cards.py` bans from anything the game
displays: *portal*, *doorway*, *the machine*, *gizmo*.

**Rule 8 — walls.** A rendered paragraph past **700 characters** with no break.

### Why the boundary is where it is

The set is not "documents I got around to". It is a real distinction:

* **These eleven describe the mod to a person.** A reader meets the mod here, so the mod's own
  words are the only ones that can be right.
* **An internal design or architecture document describes the code to whoever works on it
  next**, and the code's identifiers are `Portals/`, `PortalCrossingService`,
  `RR_PortalCrossing_*`. The standing invariant already exempts key names from the vocabulary.
  Rewriting the prose around those identifiers would make the documents **disagree with the
  source**, which is a worse failure than an old word in a design note.

The remainder is not deferred and not forgotten: it is **counted in `TODO.md`** — 262
occurrences — together with what the rule needs before it can run there, which is a
code-identifier exemption.

### Why 700

Grounded in this project's own accepted practice rather than picked. The documents rewritten
**deliberately for readability** — `PUBLIC_RELEASE_PLAN.md`, the implementation records — top
out at **393 and 542** characters per paragraph. 700 is real headroom above the shape already
agreed to read well, and still less than half the worst offender found.

### Paragraphs, not lines

Measuring source lines is wrong in both directions: a hard-wrapped document hides a long
paragraph behind short lines, and a document with one line per paragraph reports the paragraph.
The rule splits on blank lines and skips headings, lists, blockquotes and tables, because none
of those is prose.

### Words quoted from somewhere else are never rewritten

The first run flagged `docs/RESEARCH.md` and `docs/SCENARIOS.md` for the word *doorway* — in
both cases describing **the A24 synopsis**, which is the word A24 uses for what appears in the
basement of the furniture showroom.

Rewriting that would not have been tidying our vocabulary. It would have been **misquoting a
source**. The rule now excludes any double-quoted span, on the principle that a quoted phrase
belongs to whoever is being quoted — which already covered the owner's own words and now covers
everyone else's. The two sentences were marked as quotations, which is what they always were.

---

## What the sweep found beyond the two rules

Fixing the flagged text meant reading it, and two paragraphs turned out to be **superseded
rather than merely wordy**:

1. **`README.md`'s status paragraph** — 1,275 characters — still cited the **0.2.0 build
   record** and "original sprites", which were retired in 0.9.0-dev, and a profile row count
   that is now queried from the register rather than stated.

2. **The gate traversal rule at the head of both `GAME_DESIGN.md` and `SCENARIOS.md`** said two
   things that had stopped being true:
   * *"Gate, machine door and portal are one thing in the owner's vocabulary"* — 0.10.2-dev
     settled it as **three words for three different things**.
   * *"Nothing but this company's own pawns crosses a gate under its own will"* — 0.9.6-dev
     added **exactly one bounded exception**, and a founding rule with an undocumented
     exception is worse than either.

   Both corrected in place, with the exception named and bounded in the same paragraph, and
   with the part that is still absolutely true — a gate is never an objective, a lure or a
   spawn target, and nothing is ever drawn toward one — left standing.

**This is the argument for the rule and not just for the sweep.** Nobody was looking for either
of those. A readability rule made somebody read the paragraph, and reading it found the lie.

---

## Sanity-tested in both directions

| Planted | Result |
|---|---|
| The word *portal* in `docs/HOWTO.md` prose | **FAIL**, named the file and the word |
| A 779-character paragraph in `docs/HOWTO.md` | **FAIL**, named the file and the length |
| A quoted *"doorway"* attributed to A24 | **PASS**, as it must |
| Both plants reverted | **PASS** |

---

## Receipts

| | |
|---|---|
| Version | 0.10.6-dev |
| Documents brought into the vocabulary | 8 |
| Walls broken up | 11 |
| Superseded rules found and corrected | 2 |
| Rules added to `check-doc-conformance.py` | 2 (now 8) |
| Checkers | **seven**, all passing |
| Source changed | **none** — no C#, no def, no asset |
| Game launched | **no** |
