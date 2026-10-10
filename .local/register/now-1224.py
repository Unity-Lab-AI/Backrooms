# -*- coding: utf-8 -*-
"""Bring NOW.md to 0.12.24-dev, and correct a queue count that was measured two ways.

The handoff carried *"90 open / 52 partial / 440 done"*. Measured at that same commit with one
consistent pattern the figures are **86 / 52 / 444**. Neither set was wrong about the file; the
two numbers came from two different greps. So the command goes in beside the number, which is
the only thing that has ever stopped a count in this repository from drifting.
"""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(REPO, 'docs', 'NOW.md')

s = io.open(PATH, encoding='utf-8').read()


def sub(old, new):
    global s
    assert old in s, 'anchor missing: %r' % old[:90]
    assert s.count(old) == 1, 'anchor not unique: %r' % old[:90]
    s = s.replace(old, new, 1)


# ------------------------------------------------------------------ state table
sub(u'| Published | **0.12.23-dev**.', u'| Published | **0.12.24-dev**.')
sub(u'| Build | **174 C# files, 87 package files**', u'| Build | **174 C# files, 86 package files**')
sub(u'| Assembly | SHA-256 `3CED6004E9AC406FAC52BB1FE20A5297E6C7390180C810B31DBFF30C7B389C44`, '
    u'reproduced by two clean recompiles.',
    u'| Assembly | SHA-256 `B382E45C0ADF918FFF8BBAAC643C88DAB1B7CF8F0E9CDA74D60ABB22617030BE`, '
    u'reproduced by **three** clean recompiles.')
sub(u'| Proofs | **TWENTY-ONE** in `.local/register/proof-*.py`.',
    u'| Proofs | **TWENTY-TWO** in `.local/register/proof-*.py`.')
sub(u'| Register | `python tools/register-query.py families\\|family <x>\\|find <x>\\|row <n>\\|traces\\|trace <code>`',
    u'| Register | `python tools/register-query.py families\\|family <x>\\|find <x>\\|row <n>\\|traces\\|trace <code>\\|card <x>\\|use <code>` '
    u'— **`use <trace>` is the query the LAW actually describes**: for every mod bearing on what you are building, '
    u'what the register says about how to use it. Added 0.12.24-dev, because until then the `card` column printed '
    u'the words *"open card"* and every real instruction was unreachable from the tool')

# ------------------------------------------------------------------ the next task replaces the last
sub(u"""## DO THIS FIRST — fold the field recorder into the record book

**Owner-answered 2026-09-29, in the turn it was found.** This is the only remaining breach of
invariant 10: `RR_FieldRecorder` is the one genuinely **buyable, carryable gameplay `ThingDef`** this
mod authors. Its art is already gone (0.12.22-dev); the def is what remains.""",
    u"""## DO THIS FIRST — contradictory accounts, and the interview that resolves them

Queue item 4. **From the prep material, and it is the oldest unbuilt content direction left**: a
returning crew whose accounts of the same coordinate **do not agree**, and a workflow that resolves
which account the company files.

Three things to establish before writing a line, in this order:

1. **`python tools/register-query.py use RR-EVD` and `use RR-STA`.** The prisoner, casework and
   interview families have real instructions in them — *"Keep custody, casework, and interview goals
   reachable through vanilla prisoner controls"* — and RR-STA is the largest trace at 149 rows.
2. **Read `docs/CAMPAIGN_CHART.md` before the prep documents.** The chart is the authority and beats
   any prep document; the prep names the feature, the chart says where it sits.
3. **Find the real read site first.** Invariant 136 deleted four tier 3 projects for being unlocks
   with nothing to unlock. `EvidenceObservationRecord` already saves `witness`, `witnessLoadId` and
   `witnessRoomIndex` per observation, and `EvidenceObservationKinds.RecorderGap` already exists and
   already requires a prior `RouteMismatch` on the same room and marker. **A contradiction may
   already be expressible in the saved schema** — check that before adding anything to it.

---

## Done, 0.12.24-dev — the field recorder is folded into the record book

**Owner-answered 2026-09-29, in the turn it was found**, and the answer had already been written
down at 0.9.9-dev. `RR_FieldRecorder` was the last genuinely **buyable, carryable gameplay
`ThingDef`** this mod authored. Its art went at 0.12.22-dev; **the def now stays deliberately** —
loadable so saves open, never granted or sold again. Full record:
[the recorder became the book](implementation/RECORD_BOOK_IMPLEMENTATION.md).""")

# The rest of that section is now history, so the specification it carried is replaced by the
# outcome. Kept short: the implementation record holds the detail.
sub(u"""**The decision, verbatim in effect:** *fold its job into the record book crews already carry.* A
crew already takes Core's **`TextBook`** into a coordinate — that is the native evidence carrier,
resolved by `CompRouteEvidence.NativeCarrierDef` and patched with our comp in
`1.6/Patches/RR_ExistingEvidenceBook.xml`. The same book logs visited rooms, route mismatches and
entity sightings. **One item, two jobs.**

**NO SAVE BREAK.** The recorder def stays loadable so existing saves open; it is simply never
granted or sold again. That is the whole of the migration.

### The four live read sites, already located

| File | What it does there |
|---|---|
| `Expedition/ExpeditionCargo.cs:29` | `KitDefs = { "RR_FieldRecorder" }` — the kit a crew must carry |
| `Threats/FirstSliceSiteComponent.cs:117` | `HasItem(p, "RR_FieldRecorder")` — whether anyone present is recording |
| `Company/EvidenceObservations.cs:329` | resolves the def to attribute an observation to a recorder |
| `Generation/FailedSiteRecovery.cs:289` | recovery tolerance list; **leave this one naming the def**, because old saves still contain instances |

### Where it is granted or sold, and must stop being

- `1.6/Defs/RecipeDefs/RR_FieldEquipmentRecipes.xml:20` — the crafting recipe's product
- `1.6/Defs/ScenarioDefs/RR_Scenarios.xml:43` and `:130` — two starts grant one
- `1.6/Languages/English/Keyed/RR_Expedition.xml:3` — `RR_Exp_Missing_RR_FieldRecorder`, the refusal
  a crew gets without one. **Reword rather than delete**: the book can be missing too.

### Before writing a line

- **Check the register by trace**, not by family: `python tools/register-query.py trace RR-EVD` and
  `trace RR-STA`. It is guidance.
- **`GetNamedSilentFail` returns null silently.** If the book cannot be resolved, the recording job
  must refuse visibly rather than fall through — that is exactly how
  `Named<TerrainDef>("Carpet")` left the yellow rooms in wood plank flooring for months.
- **Write the proof to assert the def is never granted**, and fault-plant it by adding the recipe
  back. A check that cannot fail is the thing this project keeps catching.""",
    u"""**One item, two jobs.** The kit is resolved through `CompRouteEvidence.NativeCarrierDef` rather
than named, both callers refuse visibly on its null, and **two gates that had never agreed now ask
one question**: surveying needed the recorder *carried* while the observation needed the book merely
*somewhere on the map*. Both now want the book in a crew member's hands.

**A dead end was found and closed on the way.** Core gives books `Flammability 1` and sells
`TextBook` only as random outlander stock, so a branch whose only book burned would have failed every
future dispatch for ever. `RR_Procurement_RecordBooks` fixes it. **That was not in the row, the plan,
or the owner's answer** — it came out of reading what Core actually does with the object.

**And the register's own guidance had been unreachable from its own tool.** `row 4` printed
`card : open card`, a hyperlink label, while every real instruction sat in the register's `#cards`
section and 294 review records on disk. `card` and `use` now read them.""")

# ------------------------------------------------------------------ shipped table
sub(u'| 0.12.23 | **The handoff, audited again** — six defects in it. A question I had parked in a document, asked and answered instead |',
    u'| 0.12.23 | **The handoff, audited again** — six defects in it. A question I had parked in a document, asked and answered instead |\n'
    u'| 0.12.24 | **The recorder became the book** — the last authored gameplay item retired without a save break, a dead end closed, and the register made readable |')
sub(u'## What shipped this session, 0.7.1 → 0.12.23', u'## What shipped this session, 0.7.1 → 0.12.24')

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md brought to 0.12.24-dev')
