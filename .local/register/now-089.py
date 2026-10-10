import io

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()

# --- state table ---
pairs = [
 (u'| Published | **0.8.8-dev**, commit `0bfc000` |',
  u'| Published | **0.8.9-dev** (this commit) |'),
 (u'| Build | **154 C# files, 92 package files**, zero warnings, zero errors |',
  u'| Build | **155 C# files, 92 package files**, zero warnings, zero errors |'),
 (u'| Assembly | SHA-256 `5CFCA1C8EEEF139655B91ED421942FC58B33F683B03F1590F0607810A75C643B`, reproduced by two clean recompiles |',
  u'| Assembly | SHA-256 `9E0FA752A9DB00EB801A013FAFBC937D3723CC33D359A54B57A11E42083D8354`, reproduced by two clean recompiles |'),
 (u'## What shipped this session, 0.7.1 → 0.8.8',
  u'## What shipped this session, 0.7.1 → 0.8.9'),
 (u'| 0.8.8 | **Gate connection history** — per-gate address book, editable and clearable |',
  u'| 0.8.8 | **Gate connection history** — per-gate address book, editable and clearable |\n'
  u'| 0.8.9 | **Bringing a gate up is work** — an operator-driven spin-up with familiarity, and gates that look like gates |'),
]
for old, new in pairs:
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

# --- what is left ---
old_left = s[s.index(u'## What is left, in order'):s.index(u'## Invariants')]
new_left = u"""## What is left, in order

**The order is chosen and recorded**, by dependency direction rather than preference. Owner direction: *"we are doing it all so order needs to be logical and your intelkligent educated choise based on logical programming order of operations"*.

Content set → generator → scenarios → docs. One direction, no backtracking.

1. **Multi-cell gates** — 1x2, 1x3 and 2x3. **Owner-answered: both paths.** Bind a gate across a **run of adjacent Core doors** (existing-content-only, always works), **and** accept **Doors Expanded** (register row 77) multi-cell doors as single-thing gates when that mod is installed. Width is the capability: how many cross abreast, whether cargo or a vehicle fits, what the opening draws. Core has only 1x1 `Door` and `Autodoor`, verified against installed game data.
2. **Pursuit and incursion.** **Owner-answered: depth plus technology, while an opening is live.** An inhabitant chases a fleeing pawn to the threshold, and reaching it before the gate closes brings it through into the colony, where every native hostile behaviour applies with nothing bespoke written. **Closing the gate is the countermeasure**, which makes the emergency cutoff a tactical decision at the cost of stranding whoever is still inside. `PortalTraversalPolicy` gains the rule; the inhabitant still decides nothing.
3. **M2 existing-content replacement.** First of the four majors **because it deletes defs** — anything built against content about to be removed gets built twice. The save break is declared, so defs can go with no migration.
4. **Facilities** — larger functional spaces, distinct from rooms and corridors. Generation must be finished before the scenarios that consume it.
5. **New-game playability** — the world tile the branch does not hold (world object plus generated map) and **the three starting sites** (`SCENARIOS.md`). Consumes the final content set *and* the finished generator. **One tech tree for every start**, differing only in which projects begin complete — owner direction, and it belongs in the versioned start contract rather than bolted onto each scenario.
6. **The player-facing how-to.** Last, because documentation describes a finished thing and writing it earlier means rewriting it. Note `docs/HOWTO.md` is the **developer** guide; the player one does not exist yet.
7. **The unknown-def-field checker.** Written, **proved broken, removed rather than shipped.** See the warning below — start from the verified parts.
8. **The 1990s period and universe factions.**
9. The four area types across a gate, M1 step 5, M3 breadth, M5 interface, M6a/M6b.

"""
s = s.replace(old_left, new_left, 1)

# --- invariants ---
old_inv = u'31. **When an existing guarantee already covers a new requirement, say so and rely on it.**'
new_inv = (u'31. **When an existing guarantee already covers a new requirement, say so and rely on it.**')
assert old_inv in s
tail_marker = u'\n\n---\n\n## The warning that matters most right now'
assert tail_marker in s
additions = u"""
32. **There is exactly one way a laboratory gate opens** — through the spin-up. Every entry point routes into it. A second path would make the ramp optional, and a player who learned the other button would never see it.
33. **Never tie a penalty rate to a flat constant without proving it against the real stat range.** Spin-up decay was written as a flat 0.5 per tick with a comment claiming it was slower than progress; at low Intellectual it was **faster**, which would have made a slow operator's gate impossible rather than slow. Express such a rate as a **fraction of the observed rate** so the guarantee holds by construction.
34. **Ask at the fork; never flag it for later.** Owner direction: *"dopnt flag shit!!! ask me then and there"*. A flagged question becomes orphaned work — it lands in a doc nobody actions while the build carries a guess forward.
35. **`ThingComp.ForceColor()` is the tint hook**, consulted by `ThingWithComps.DrawColor` for every comp a thing carries, and a painted colour wins over it. `Notify_ColorChanged()` drops Core's cached coloured graphic and redraws the cell."""
s = s.replace(tail_marker, additions + tail_marker, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md updated')
