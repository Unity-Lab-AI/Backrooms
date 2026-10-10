import io

p = 'docs/NOW.md'
s = io.open(p, encoding='utf-8').read()

old = s[s.index(u'1. **Multi-cell gates**'):s.index(u'9. The four area types across a gate')]
new = u"""1. **M2 existing-content replacement.** **First, because it deletes defs** — anything built against content about to be removed gets built twice, and the save break is already declared so defs can go with no migration. It also **collapses the gate comp's whole non-native branch**: deleting `RR_MachineGate` removes the second geometry model, so the multi-cell work below is written once against one model instead of twice. Scope: legacy gate objects, field gear, fixtures and terrain, the `RR_QuietPursuer` presentation, five `RR_*Staff` PawnKinds, five recipes, and the fourteen historical PNGs off the allowlist.
2. **Multi-cell gates** — 1x2, 1x3 and 2x3, on the settled Core-door-only gate model. **Owner-answered: both paths.** Bind a gate across a **run of adjacent Core doors** (existing-content-only, always works), **and** accept **Doors Expanded** (register row 77) multi-cell doors as single-thing gates when that mod is installed. Width is the capability: how many cross abreast, whether cargo or a vehicle fits, what the opening draws. Core has only 1x1 `Door` and `Autodoor`, verified against installed game data.
3. **Pursuit and incursion.** Grouped here so **all the gate work happens once**. **Owner-answered: depth plus technology, while an opening is live.** An inhabitant chases a fleeing pawn to the threshold, and reaching it before the gate closes brings it through into the colony, where every native hostile behaviour applies with nothing bespoke written. **Closing the gate is the countermeasure**, which makes the emergency cutoff a tactical decision at the cost of stranding whoever is still inside. `PortalTraversalPolicy` gains the rule; the inhabitant still decides nothing.
4. **Facilities** — larger functional spaces, distinct from rooms and corridors. Generation must be finished before the scenarios that consume it.
5. **New-game playability** — the world tile the branch does not hold (world object plus generated map) and **the three starting sites** (`SCENARIOS.md`). Consumes the final content set, the finished gate model *and* the finished generator. **One tech tree for every start**, differing only in which projects begin complete — owner direction, and it belongs in the versioned start contract rather than bolted onto each scenario.
6. **The player-facing how-to.** Last, because documentation describes a finished thing and writing it earlier means rewriting it. Note `docs/HOWTO.md` is the **developer** guide; the player one does not exist yet.
7. **The unknown-def-field checker.** Written, **proved broken, removed rather than shipped.** See the warning below — start from the verified parts.
8. **The 1990s period and universe factions.**
"""
s = s.replace(old, new, 1)

marker = u'Content set → generator → scenarios → docs. One direction, no backtracking.'
assert marker in s
s = s.replace(marker,
    u'Content set → gate model → generator → scenarios → docs. One direction, no backtracking.\n\n'
    u'**Corrected immediately after 0.8.9-dev**: the multi-cell gate work was first listed ahead of M2. That was wrong. '
    u'M2 deletes `RR_MachineGate`, which removes the gate comp’s second geometry model entirely, so doing it first '
    u'means the multi-cell binding is written once rather than written and then rewritten.', 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('NOW.md order corrected')
