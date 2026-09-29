# The handoff, audited again — 0.12.23-dev, 2026-09-29

**Dated record.** Never rewritten. The second time this procedure has been run properly, and the
second time it has found defects that reading would not have.

---

## The owner caught me parking a question in a document

I had written `RR_FieldRecorder` into the handoff as:

> **STILL OPEN, and it needs an owner decision.**

That is exactly the flagging invariant 34 forbids — *"dopnt flag shit!!! ask me then and there"* —
and I did it inside the very document whose purpose is to leave nothing hanging. The owner:

> *"ask me the question remebr i said sooner than later with those"*
> *"that means asap"*

Asked, answered in one exchange. **A handoff that contains an open question is a handoff that
deferred work.**

### The answer

**Fold `RR_FieldRecorder`'s job into the record book crews already carry.**

A crew already takes Core's `TextBook` into a coordinate — that is the native evidence carrier,
patched with our comp. The same book now logs visited rooms, route mismatches and entity sightings.

- **One item, two jobs.** No new def.
- **No save break.** The recorder def stays loadable so old saves open, and is never granted or sold
  again.
- It reads better: *the thing you write in is the thing that remembers.*

Four live read sites move onto the book. **That is the next thing to build.**

---

## Six defects, none of them visible by reading

### 1. The proof output split was stale by six, and understated its own case

The line said *"four of them print `PASS:` and eleven print `PROOF HELD`"* — **fifteen**, against
**twenty-one** proofs.

Measured:

| Ending | Count |
|---|---|
| `PROOF HELD` | **17** |
| `PASS:` | **2** |
| **a wrapped continuation line** | **2** |

`proof-displacement` and `proof-facilities` end mid-sentence on a wrapped line, so their final line
is **not a status token at all**. Every phrasing-based runner misses those two — not just the wrong
phrasing, *every* phrasing.

**That strengthens the exit-status rule rather than weakening it**, which is the opposite of what a
stale count usually does.

### 2. Research tier 3 was still listed as pending

Queue item 2 read *"Research tiers 3–4, AFTER the arcs. Deliberately moved behind them,
0.12.5-dev."* **Tier 3 shipped at 0.12.18-dev, all seven branches.** Only tier 4 remains, and the
note now says to **re-run the knob sweep rather than carry the old verdict** — because that is
exactly what made tier 3 writeable.

### 3. `RR_QuietPursuer` was still called "the last existing-content replacement"

It shipped at 0.12.22-dev.

### 4. The top warning was two sessions stale

It described 0.12.10-dev's four unfalsifiable claims. Replaced with **this** session's sharper
lesson:

> **A search that finds nothing is not evidence, and this session I twice took one as proof.**

- `Named<TerrainDef>("Carpet")` returned null **silently** for months, and a `??` fallback made wood
  plank flooring look deliberate. The depth-1 yellow rooms — invariant 25 calls them **sacred** —
  were never carpeted.
- I marked working code *"confirmed unbuilt by grep"* and accused a **correct** comment of lying.
  Condemning working code on a failed search is worse than trusting a wrong comment, because it
  invites somebody to "fix" what works.
- A check I wrote to catch one specific thing **passed that exact planted fault.**

### 5. "Done since the last handoff" named none of this session's twelve checkpoints

It described work up to 0.12.9. Rewritten to say what actually shipped — including the finding that
**the campaign did not exist in the game** until 0.12.11-dev, and that the queue went from 254 open
rows to 90 once it was re-measured.

### 6. "Open owner questions — THERE ARE NONE" was wrong when it was written

The recorder decision was outstanding at that moment. It is true again now — and true **by having
asked**, not by having omitted.

---

## One place my measurement was wrong and the document was right

An invariant-numbering check reported **222 entries with duplicates 1–9**. The regex had caught
ordinary numbered lists elsewhere in the file.

Corrected: **209 invariants, 1 to 215, no duplicates, 6 deliberate gaps.** The two apparent
out-of-order entries are subsection restarts, by design.

**When your measurement and the document disagree, suspect the measurement first.** I have spent
this session finding stale documents; that is not a licence to assume the document is the problem.

---

## Receipts

| | |
|---|---|
| Version | 0.12.23-dev |
| Build | 174 C# files, 87 package files, **0 warnings, 0 errors** |
| Gameplay changed | **none, deliberately** |
| Defects found in the handoff | **6** |
| Owner questions parked instead of asked | **1**, and the owner caught it |
| Open owner questions now | **zero** |
| Checkers | **nine**, all passing |
| Proofs | **twenty-one**, all exiting zero |
| Game launched | **no**, and nothing in this mod has ever been played |
