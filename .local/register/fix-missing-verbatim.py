import io

p = 'docs/TODO.md'
s = io.open(p, encoding='utf-8').read()

block = u"""
## Owner directions recorded late

These three were **acted on correctly and recorded in `NOW.md` or `FINALIZED.md`, but never
written into this queue as tasks**. The owner noticed the gap on 2026-09-29 and was right.
They are recorded here verbatim now, and `check-doc-conformance.py` refuses from this point
on to let a direction reach `FINALIZED.md` without appearing here first.

**Verbatim owner direction (2026-09-29):** *"dopnt flag shit!!! ask me then and there"* and *"write that to mem,ory to not flag shit, it just becomes orphaned work"*

- [x] **HELD as a standing working rule.** No unresolved question is written down for later: it is asked immediately with `AskUserQuestion`. A flagged item becomes orphaned work - it lands in a doc nobody actions while the build carries an unresolved assumption forward. Recorded as a persistent memory and as invariant #44 in `NOW.md`.

**Verbatim owner direction (2026-09-29):** *"2 should really limit numbers through at once because in vinilla any number of pawns can use a door at once so we dont want limitations"*

- [x] **HELD 0.9.2-dev by adding nothing.** A wide gate gets **more doorway cells**, never a quota, and ordinary pathfinding spreads people across them exactly as at any wide vanilla door. `OrderCrossing` was checked first and only ever refused *the same pawn twice*, never a second pawn, so the existing behaviour was already vanilla-equivalent and the correct action was to leave it alone. There is no counter anywhere in `GateFootprint.cs`, deliberately.

**Verbatim owner direction (2026-09-29):** *"gate doors expansions can NOT be done on a working gate"*

- [x] **BUILT 0.9.2-dev.** Binding and unbinding already refused while a gate was open or had an unresolved trip. **A ramp is the gate working too**, so spinning up now blocks a rebind by the same rule. Resizing a gate means swapping the door, which means taking it out of service first.

"""

anchor = u'\n**Verbatim owner direction (2026-09-29):** *"we need to keep using the mod register'
assert anchor in s, 'anchor not found'
s = s.replace(anchor, block + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('three missing directions recorded verbatim in TODO.md')
