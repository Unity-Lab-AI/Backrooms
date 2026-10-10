# -*- coding: utf-8 -*-
"""Ledger for 0.12.1-dev. Insertions re-include their anchors (invariant 144)."""
import io
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(rel):
    return io.open(os.path.join(REPO, rel), encoding='utf-8').read()


def write(rel, s):
    io.open(os.path.join(REPO, rel), 'w', encoding='utf-8', newline='').write(s)
    print('updated %s' % rel)


def insert_before(rel, anchor, block):
    s = read(rel)
    assert anchor in s, '%s: anchor not found' % rel
    write(rel, s.replace(anchor, block + anchor, 1))


insert_before('CHANGELOG.md', u'## 0.12.0-dev', u"""## 0.12.1-dev - 2026-09-29 - the free doors run out

- **Found doors stop leading deeper after the third level.** The Backrooms gives you the yellow rooms and two steps in, and then no more doors turn up. Past that, going deeper needs a gate you built.
- **Doors that lead OUT are never limited.** You can always find your way home from the deepest level the free doors reach. Being stuck down there with nothing to find would not be a challenge, it would be a bug.
- **A built gate is unaffected** and reaches anywhere it has earned, exactly as before. The limit is on the free doors, not on you.
- **When a door goes deeper than anything you can walk through, you are told so plainly** rather than quietly sent somewhere else.

Full record: [the free doors run out](docs/implementation/NATURAL_DEPTH_LIMIT_IMPLEMENTATION.md). No gameplay, balance, performance or compatibility result is claimed.

""")

insert_before('docs/FINALIZED.md', u'## Completed sessions', u"""## Session 2026-09-29 - the natural depth limit (0.12.1-dev)

**Verbatim user direction:** *"and remember the solo/group start in a backroom needs to 100% have a exit to map natural portal on their first backrroms level with natural portals deeper to an extent till they would need to buidl theri own gate"*

**And, mid-turn, verbatim:** *"but remmebr this is all open eneded they can play how they choose"*

**Owner answers at the fork, verbatim:** *"Emerges on a fresh tile chosen by the seed"* / *"option 1 and the tutorial like quest chains should lay it all out"*

### What shipped

`NaturalFrontierService.MaximumNaturalDepth = 3`. Found doors reach the shallow yellow rooms and two steps inward, then stop. Deeper requires a gate the player built.

### Files touched

`src/RimroomsAsyncIndustries/Portals/NaturalFrontierService.cs`, `1.6/Languages/English/Keyed/RR_Portals.xml`, `docs/implementation/NATURAL_DEPTH_LIMIT_IMPLEMENTATION.md`, `docs/implementation/SOLO_GROUP_START_IMPLEMENTATION.md` (annotated), `CHANGELOG.md`, `README.md`, `docs/TODO.md`, `docs/NOW.md`, `About.xml`, the csproj, and the starts proof.

### Closure notes

- **This corrects 0.12.0-dev, shipped an hour earlier**, whose record says *"There is no way home and finding one is the whole opening."* That is wrong. The 0.12.0 record is **annotated, not rewritten**, per invariant 135.
- **The cap is applied AFTER the way-out attempt**, and that ordering is the whole safety of it: capping both directions would make depth 3 a trap with no door home, which invariant 28 forbids. Asserted rather than trusted to the reading.
- **It restrains the doors, not the player.** *"This is all open eneded they can play how they choose"* - a built gate reaches any depth it has earned, and a player who never goes deeper never meets the wall.
- **`check-info-cards.py` refused the first version of the player-facing string** for saying *"doorway"*: the enforced vocabulary is door, gate, connection, threshold. The string was wrong and the rule was right.
- **A claim of mine was failing OPEN, which is a new failure mode this session.** The ordering claim was a string-index search over the literal `"depth > MaximumNaturalDepth"`, so a reordered cap using a different variable name failed it for the wrong reason - and the same claim could have **passed** for a genuinely reordered cap. Rewritten to key off `Refused("RR_Frontier_BeyondNaturalReach")`, which cannot be renamed without the keyed string moving with it, then re-planted and confirmed to fail for the right reason.
- **Still owed and queued with its design:** the guaranteed exit on level 1, emerging on a fresh world tile chosen by the seed. The existing emergence path cannot serve it - it needs a `CompRimroomsEmergence` anchor, which is a door the player marked on a map they already hold, and a solo/group start holds none. Then the solo/group tutorial line, which must guide without railing.
- Build 0.12.1-dev, 168 C# files, 86 package files, **0 warnings, 0 errors**. Eight checkers pass, seven proofs hold. Assembly reproduced by two clean recompiles. **No game was launched.**

---

""")

s = read('docs/NOW.md')
pairs = [
    (u'| Published | **0.12.0-dev**.', u'| Published | **0.12.1-dev**.'),
    (u'`C6810C8DD2E0B422B4B5F3BBF1CA05E178B8AC0F9D60FAF16D84598E7CB46AEB`',
     u'`62935DFB887DED243394A1A6C5440ED3DE39F364AF055AAB17E5CF8491FCFA57`'),
    (u'## What shipped this session, 0.7.1 → 0.12.0',
     u'## What shipped this session, 0.7.1 → 0.12.1'),
    (u'| 0.12.0 | **You are already in** — the solo/group start; the map itself is a coordinate. **All three starts ship.** |',
     u'| 0.12.0 | **You are already in** — the solo/group start; the map itself is a coordinate. **All three starts ship.** |\n'
     u'| 0.12.1 | **The free doors run out** — found doors stop at depth 3; deeper needs a built gate. Corrects 0.12.0 |'),
]
for old, new in pairs:
    assert old in s, old[:70]
    s = s.replace(old, new, 1)

start = s.index(u'1. **Research tiers 3–4**')
s = s[:start] + u"""1. **The guaranteed exit on the solo/group start's first level.** Owner direction, verbatim:
   *"needs to 100% have a exit to map natural portal on their first backrroms level"*. **0.12.0-dev
   shipped the opposite and its record is annotated as corrected.** Owner's answer at the fork:
   *"Emerges on a fresh tile chosen by the seed"*.
   - The existing emergence path **cannot serve it**: `RegisterEmergenceAddress` needs a
     `CompRimroomsEmergence` anchor, which is **a door the player marked on a map they already
     hold**, and a solo/group start holds none. `RegisterEmergenceAddress` also requires the
     Backrooms side to be a `RimroomsDestinationMapParent`, and the solo start's map is
     `Settlement`-parented because Core requires a player settlement for the starting map.
   - So it needs: a world tile derived from the branch seed, a player settlement created on it,
     its map generated on first use, and a two-way route registered between the two.
   - **100% means at generation, not by survey.** `NaturalFrontierService` finds frontiers at
     roughly one door in twelve; a draw cannot deliver a guarantee.
2. **The solo/group tutorial line.** *"the tutorial like quest chains should lay it all out"* —
   and *"this is all open eneded they can play how they choose"*, so it **guides without railing**.
   Requests have no per-start scoping yet: the six tutorial requests and the hinge are Async's
   unconditionally, so the request shape needs to know which start a line belongs to.
""" + s[start:]

marker = u'151. **A `workerClass` or `genStep Class` that does not resolve fails as ORDINARY '
idx = s.index(marker)
line_end = s.index(u'\n', idx)
s = (s[:line_end + 1] +
     u'152. **A claim that can fail for the wrong reason can also pass for the wrong reason.** The '
     u'natural-depth ordering claim was a string-index search over a variable name; renaming the '
     u'variable made it fail open. **Key an assertion off the thing that actually happens** — a '
     u'refusal, a keyed string, a def name — never off an expression’s spelling. Fourth assertion '
     u'corrected this session and the first of this kind (see 130, 142, 145).\n'
     u'153. **Cap the free doors, never the way home.** `MaximumNaturalDepth` is checked after the '
     u'way-out attempt. Capping both directions makes the deepest natural band a trap, which '
     u'invariant 28 forbids.\n'
     u'154. **Open-ended is a constraint on the content, not a mood.** Owner, verbatim: *"this is '
     u'all open eneded they can play how they choose"*. A tutorial line offers and describes; it '
     u'never requires an order, and a step already done by a player who got there first must read '
     u'as done rather than skipped.\n' +
     s[line_end + 1:])
write('docs/NOW.md', s)
