# -*- coding: utf-8 -*-
"""Bring NOW.md to 0.12.31-dev and set the next task."""
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


sub(u'| Published | **0.12.30-dev**.', u'| Published | **0.12.31-dev**.')
sub(u'| Build | **178 C# files, 87 package files**', u'| Build | **179 C# files, 87 package files**')
sub(u'| Assembly | SHA-256 `90E0885C229B6972E5209E3C30B4487F9BB3431AB5B5490A75B6B36188AA1923`, '
    u'reproduced by two clean recompiles.',
    u'| Assembly | SHA-256 `BA503ACA67B06719663B35D406E536C63DF266F55F926602B6958DE7CF76F757`, '
    u'reproduced by two clean recompiles.')
sub(u'| Proofs | **TWENTY-SEVEN** in `.local/register/proof-*.py`.',
    u'| Proofs | **TWENTY-EIGHT** in `.local/register/proof-*.py`.')
sub(u'| Genuine build items left | **~26** at 0.12.30-dev, some spanning several rows |',
    u'| Genuine build items left | **~25** at 0.12.31-dev, some spanning several rows |')

# ------------------------------------------------------------------ next task
sub(u"""## DO THIS FIRST — the adjacent-door-run fallback""",
    u"""## DO THIS FIRST — surgery across a gate, and the rest of the medical routes

Queue row 227, and the last named gap in the cross-map work families. The row states the hard part
itself:

> *"Surgery across a gate (`Bill_Medical` needs the patient present, and `uniqueRequiredIngredients`
> is a case no other family has); patient feeding, which belongs with the food family; prisoner and
> guest care including Hospitality."*

Five things to establish before writing a line:

1. **`Bill_Medical` needs the patient present, and that is not negotiable** — the patient is the
   bill's target. So the question is not *"how do we do surgery remotely"*, it is **who travels**.
   Every other family answers by sending the worker; this one may have to send the patient, and
   invariant 55 rules that absolutely: **a transfer that can lose a pawn is a corruption, not a
   threat.** Preflight fully, then move, and restore on failure.
2. **`uniqueRequiredIngredients` has no precedent here.** Decompile `Bill_Medical` and
   `Recipe_Surgery` before designing — a medicine reserved for one specific patient behaves unlike
   any quantity lease the adapter families already hold.
3. **Invariant 8: one commitment per worker**, across every record kind. A surgery that reserves a
   surgeon, a patient, a bed and a specific medicine is four reservations and must still be one
   commitment.
4. **`python tools/register-query.py use RR-EVD` and `family medical`** — the medical family is one
   of the **seven** still unswept by the register retro sweep, and its rows carry *"check pawn
   health/custody state, treatment choice, and transfer; preserve a vanilla fallback"*, which is
   almost a specification for this row.
5. **Hospitality is an optional mod**, so guest care is a `PatchOperationFindMod` case at most, and
   must do nothing at all when it is absent.

---

## Done, 0.12.31-dev — a wide gate out of plain doors

**Three rows were one feature**, and the answer was on record as **BOTH paths**. A run of adjacent
Core 1×1 doors binds into one gate. The change is small because **a straight line of N adjacent 1×1
doors is a 1×N `CellRect`**, which is exactly what every existing size derivation already works off
— so the width, the entry cells, the power draw and the spin-up work all came out right with nothing
written for them. Full record:
[a wide gate out of plain doors](implementation/GATE_DOOR_RUN_IMPLEMENTATION.md).

**Both defects in that checkpoint were mine and the checkers caught both** — a runtime-built keyed
string (fifth time) and the word *"doorway"* five times, a rule I had been corrected on hours
earlier.""")

# ------------------------------------------------------------------ shipped table
sub(u'| 0.12.30 | **You can call the company** — `EstablishCorporationContact` had no caller, so **two of three starts had no campaign at all**. Earned on a comms console, and it opens the line that already existed |',
    u'| 0.12.30 | **You can call the company** — `EstablishCorporationContact` had no caller, so **two of three starts had no campaign at all**. Earned on a comms console, and it opens the line that already existed |\n'
    u'| 0.12.31 | **A wide gate out of plain doors** — 1×3 and 2×3 with no mods, as one gate of one width. **Three rows were one feature**, and the union of a run is the `CellRect` everything already read |')
sub(u'## What shipped this session, 0.7.1 → 0.12.30', u'## What shipped this session, 0.7.1 → 0.12.31')

# ------------------------------------------------------------------ invariants
anchor = u"243. **An owner answer can delete work, not just direct it.**"
idx = s.index(anchor)
end = s.index(u'\n\n', idx)
s = s[:end] + u"""
244. **Find the ONE value everything already derives from, and change that.** A gate's width, entry
     cells, cell count, power draw and spin-up work all come off a single `CellRect`. A run of 1×1
     doors **is** a rect, so returning the union made every one of those correct with nothing
     written for it. **Look for the existing seam before adding a parallel path.**
245. **Validate the WHOLE, not the part, when legality is a property of the whole.** Whether a door
     may join a run cannot be answered about that door: it is answered about the run it would
     make. So propose, check, and put it back on failure — and have the candidate search ask the
     same way rather than keeping a second copy of the rule to drift out of step.
246. **A legal-looking bounding box is not a shape.** A ring of doors around a gap passes every
     size test and is not an opening. **Assert the area equals the parts.**
247. **The checkers do not care that you know the rule.** Both defects at 0.12.31-dev were mine: a
     runtime-built keyed string for the fifth time in this project, and the banned word *"doorway"*
     five times — **a rule I had personally been corrected on hours earlier in the same session.**
     That is the entire argument for having them.""" + s[end:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md brought to 0.12.31-dev, next task set to the medical routes')
