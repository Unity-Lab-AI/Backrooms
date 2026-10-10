# -*- coding: utf-8 -*-
"""Restructure NOW.md so a post-compact session can act, not read.

The 0.12.23-dev handoff was accurate -- every state claim re-verified here -- but it was organised
as a narrative of what happened rather than an instruction for what to do. A fresh session after a
compaction has no memory and needs, in this order: the state, the next task fully specified, the
ritual, then history.

Two things also trimmed:
  * The Assembly row still carried a five-checkpoint-old warning about itself. The actionable half
    ("re-read it from the build") stays; the archaeology goes to the gotchas.
  * The next task was described in the middle of queue item 6. It is now the first thing after the
    state table, with its decision, files, read sites and constraints all named.
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


# ------------------------------------------------------------------ trim the assembly row
sub(u'| Assembly | SHA-256 `3CED6004E9AC406FAC52BB1FE20A5297E6C7390180C810B31DBFF30C7B389C44`, reproduced by two clean recompiles. **This line was stale for five checkpoints** — it still held 0.12.4’s hash. Re-read it from the build, never from memory |',
    u'| Assembly | SHA-256 `3CED6004E9AC406FAC52BB1FE20A5297E6C7390180C810B31DBFF30C7B389C44`, '
    u'reproduced by two clean recompiles. **Re-read this from the build after the determinism run, '
    u'never from memory or from this line** |')

# ------------------------------------------------------------------ lead with the work
sub(u"""### The standing instruction

> *"you are NOT to stop untill i tell you to stop or you reach the completeion of the mod's build out"*

Chain checkpoints. Do not finish one and wait.""",
    u"""### The standing instruction

> *"you are NOT to stop untill i tell you to stop or you reach the completeion of the mod's build out"*

Chain checkpoints. Do not finish one and wait. Two standing corrections that change how to read
everything below:

- **The mod register is GUIDANCE, not law.** *"remmebr its not law but guidance"*. Consult it, let
  it shape the design, say what it said — but a row never vetoes work.
- **Tests are not the concern yet.** *"test cases arnt being worried about right now we are trying
  to get the build complete so we can test"*. **Unverifiable-without-a-launch is never a reason to
  defer building something.** I parked the world exit for that reason and was overruled, correctly.

---

## DO THIS FIRST — fold the field recorder into the record book

**Owner-answered 2026-09-29, in the turn it was found.** This is the only remaining breach of
invariant 10: `RR_FieldRecorder` is the one genuinely **buyable, carryable gameplay `ThingDef`** this
mod authors. Its art is already gone (0.12.22-dev); the def is what remains.

**The decision, verbatim in effect:** *fold its job into the record book crews already carry.* A
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
  back. A check that cannot fail is the thing this project keeps catching.""")

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md restructured: state, then the next task fully specified, then the ritual')
